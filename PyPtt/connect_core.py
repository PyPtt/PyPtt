from __future__ import annotations

import asyncio
import os.path
import ssl
import tempfile
import time
import traceback
import warnings
from typing import Any

import websockets
import websockets.exceptions

import PyPtt
from . import command
from . import data_type
from . import exceptions
from . import i18n
from . import log
from . import screens
from . import ssl_config

try:
    import websockets.http

    websockets.http.USER_AGENT += f' PyPtt/{PyPtt.__version__}'
    use_http11 = False
except AttributeError:
    import websockets.http11

    websockets.http11.USER_AGENT += f' PyPtt/{PyPtt.__version__}'
    use_http11 = True

ssl_context = None


def ssl_init():
    global ssl_context

    cert_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pem')
    cert_file.write(ssl_config.cert.encode('utf-8'))

    key_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pem')
    key_file.write(ssl_config.key.encode('utf-8'))

    cert_file.close()
    key_file.close()

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.load_cert_chain(certfile=cert_file.name, keyfile=key_file.name)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.verify_mode = ssl.CERT_NONE

    os.unlink(cert_file.name)
    os.unlink(key_file.name)


ssl_init()


class TargetUnit:
    def __init__(self, detect_target, log_level: log.LogLevel = None, response: [Any | str] = '', break_detect=False,
                 break_detect_after_send=False, exceptions_=None, refresh=True, secret=False, handler=None,
                 max_match: int = 0):

        self.detect_target = detect_target
        if log_level is None:
            self.log_level = log.INFO
        else:
            self.log_level = log_level
        self._response_func = response
        self._break_detect = break_detect
        self._exception = exceptions_
        self._refresh = refresh
        self._break_after_send = break_detect_after_send
        self._secret = secret
        self._Handler = handler
        self._max_match = max_match
        self._current_match = 0

    def is_match(self, screen: str, cursor) -> bool:
        if self._current_match >= self._max_match > 0:
            return False
        if isinstance(self.detect_target, str):
            if self.detect_target in screen:
                self._current_match += 1
                return True
            return False
        elif isinstance(self.detect_target, list):
            for target in self.detect_target:
                if target == cursor:
                    if not any(line.startswith(target) for line in screen.split('\n')):
                        return False
                elif isinstance(target, str):
                    if target not in screen:
                        return False
                elif isinstance(target, list):
                    if not any(t in screen for t in target):
                        return False

            self._current_match += 1
            return True

    def get_detect_target(self):
        return self.detect_target

    def get_log_level(self):
        return self.log_level

    def get_response(self, screen: str) -> str:
        if callable(self._response_func):
            return self._response_func(screen)
        return self._response_func

    def is_break(self) -> bool:
        return self._break_detect

    def raise_exception(self):
        if isinstance(self._exception, Exception):
            raise self._exception

    def is_refresh(self) -> bool:
        return self._refresh

    def is_break_after_send(self) -> bool:
        return self._break_after_send

    def is_secret(self) -> bool:
        return self._secret


class ReceiveDataQueue(object):
    def __init__(self):
        self._ReceiveDataQueue = []

    def add(self, screen):
        self._ReceiveDataQueue.append(screen)
        self._ReceiveDataQueue = self._ReceiveDataQueue[-10:]

    def get(self, last=1):
        return self._ReceiveDataQueue[-last:]


class API(object):
    def __init__(self, api):

        self.current_encoding = 'big5uao'
        self.api = api
        self.config = api.config
        self._RDQ = ReceiveDataQueue()
        self._UseTooManyResources = TargetUnit(screens.Target.use_too_many_resources,
                                               exceptions_=exceptions.UseTooManyResources())
        self._loop = None

    def _get_event_loop(self):
        if self._loop and not self._loop.is_closed():
            return self._loop

        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop

    def connect(self) -> None:
        def _wait():
            for i in range(self.config.retry_wait_time):

                if self.config.host == data_type.HOST.PTT1:
                    log.logger.info(i18n.prepare_connect_again, i18n.PTT, str(self.config.retry_wait_time - i))
                elif self.config.host == data_type.HOST.PTT2:
                    log.logger.info(i18n.prepare_connect_again, i18n.PTT2, str(self.config.retry_wait_time - i))
                elif self.config.host == data_type.HOST.LOCALHOST:
                    log.logger.info(i18n.prepare_connect_again, i18n.localhost, str(self.config.retry_wait_time - i))
                else:
                    log.logger.info(i18n.prepare_connect_again, self.config.host, str(self.config.retry_wait_time - i))

                time.sleep(1)

        warnings.filterwarnings("ignore", category=DeprecationWarning)

        self.current_encoding = 'big5uao'

        if self.config.host == data_type.HOST.PTT1:
            websocket_host = 'wss://ws.ptt.cc/bbs/'
            websocket_origin = 'https://term.ptt.cc'
        elif self.config.host == data_type.HOST.PTT2:
            websocket_host = 'wss://ws.ptt2.cc/bbs/'
            websocket_origin = 'https://term.ptt2.cc'
        elif self.config.host == data_type.HOST.LOCALHOST:
            websocket_host = 'wss://localhost'
            websocket_origin = 'https://term.ptt.cc'
        else:
            websocket_host = f'wss://{self.config.host}'
            websocket_origin = 'https://term.ptt.cc'

        connect_success = False
        loop = self._get_event_loop()

        for _ in range(2):
            try:
                log.logger.debug('USER_AGENT',
                                 websockets.http11.USER_AGENT if use_http11 else websockets.http.USER_AGENT)
                self._core = loop.run_until_complete(
                    websockets.connect(
                        websocket_host,
                        origin=websocket_origin,
                        ssl=ssl_context))
                connect_success = True
                break
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)

                if self.config.host == data_type.HOST.PTT1:
                    log.logger.info(i18n.connect, i18n.PTT, '...', i18n.fail)
                elif self.config.host == data_type.HOST.PTT2:
                    log.logger.info(i18n.connect, i18n.PTT2, '...', i18n.fail)
                elif self.config.host == data_type.HOST.LOCALHOST:
                    log.logger.info(i18n.connect, i18n.localhost, '...', i18n.fail)
                else:
                    log.logger.info(i18n.connect, self.config.host, '...', i18n.fail)

                _wait()
                continue

        if not connect_success:
            raise exceptions.ConnectError(self.config)

    def _decode_screen(self, receive_data_buffer, start_time, target_list, is_secret, refresh, msg):

        break_detect_after_send = False
        use_too_many_res = False

        vt100_p = screens.VT100Parser(receive_data_buffer, self.current_encoding)
        screen = vt100_p.screen

        find_target = False
        target_index = -1
        for target in target_list:
            if target.is_match(screen, self.api.cursor):
                if target._Handler is not None:
                    target._Handler(screen)
                if len(screen) > 0:
                    screens.show(self.config, screen)
                    self._RDQ.add(screen)
                    if target == self._UseTooManyResources:
                        use_too_many_res = True
                        break
                    target.raise_exception()

                find_target = True

                end_time = time.time()
                log.logger.debug(i18n.spend_time, round(end_time - start_time, 3))

                if target.is_break():
                    target_index = target_list.index(target)
                    break

                msg = target.get_response(screen)

                add_refresh = False
                if target.is_refresh():
                    add_refresh = True
                elif refresh:
                    add_refresh = True

                if add_refresh and not msg.endswith(command.refresh):
                    msg += command.refresh

                is_secret = target.is_secret()

                if target.is_break_after_send():
                    break_detect_after_send = True
                break
        return screen, find_target, is_secret, break_detect_after_send, use_too_many_res, msg, target_index

    async def _async_send(self, msg: str, target_list: list, screen_timeout: int, refresh: bool, secret: bool) -> int:
        current_screen_timeout = self.config.screen_timeout if screen_timeout == 0 else screen_timeout
        is_secret = secret
        break_detect_after_send = False
        use_too_many_res = False

        while True:
            if refresh and msg and not msg.endswith(command.refresh):
                msg += command.refresh

            try:
                encoded_msg = msg.encode('utf-8', 'replace')
            except AttributeError:
                encoded_msg = msg
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)
                encoded_msg = msg.encode('utf-8', 'replace')

            if is_secret:
                log.logger.debug(i18n.send_msg, i18n.hide_sensitive_info)
            else:
                log.logger.debug(i18n.send_msg, str(encoded_msg))

            try:
                await self._core.send(encoded_msg)
            except (websockets.exceptions.ConnectionClosed, websockets.exceptions.ConnectionClosedOK, RuntimeError):
                raise exceptions.ConnectionClosed()

            if break_detect_after_send:
                return -1

            msg = ''
            receive_data_buffer = bytes()
            start_time = time.time()
            find_target = False
            target_index = -1

            try:
                async with asyncio.timeout(current_screen_timeout):
                    while True:
                        try:
                            data_chunk = await self._core.recv()
                        except (websockets.exceptions.ConnectionClosed, websockets.exceptions.ConnectionClosedOK):
                            if use_too_many_res:
                                raise exceptions.UseTooManyResources()
                            raise exceptions.ConnectionClosed()

                        receive_data_buffer += data_chunk

                        screen, find_target, is_secret, break_detect_after_send, use_too_many_res, msg, target_index = \
                            self._decode_screen(receive_data_buffer, start_time, target_list, is_secret, refresh, msg)

                        if self.current_encoding == 'big5uao' and not find_target:
                            self.current_encoding = 'utf-8'
                            screen_, find_target, is_secret, break_detect_after_send, use_too_many_res, msg, target_index = \
                                self._decode_screen(receive_data_buffer, start_time, target_list, is_secret, refresh, msg)
                            if find_target:
                                screen = screen_
                            else:
                                self.current_encoding = 'big5uao'

                        if find_target:
                            break
            except TimeoutError:
                if len(receive_data_buffer) > 0:
                    vt100_p = screens.VT100Parser(receive_data_buffer, self.current_encoding)
                    screens.show(self.config, vt100_p.screen)
                    self._RDQ.add(vt100_p.screen)
                return -1

            if target_index != -1:
                return target_index

            if use_too_many_res:
                continue

            if not find_target:
                return -1

    def send(self, msg: str, target_list: list, screen_timeout: int = 0, refresh: bool = True,
             secret: bool = False) -> int:

        if not all(isinstance(T, TargetUnit) for T in target_list):
            raise exceptions.ParameterError('Item of TargetList must be TargetUnit')

        if self._UseTooManyResources not in target_list:
            target_list.append(self._UseTooManyResources)

        if self.config.connect_mode == data_type.ConnectMode.TELNET:
            # Original Telnet logic remains, as it doesn't use asyncio
            if screen_timeout == 0:
                current_screen_timeout = self.config.screen_timeout
            else:
                current_screen_timeout = screen_timeout
            break_detect_after_send = False
            is_secret = secret
            use_too_many_res = False
            while True:
                if refresh and not msg.endswith(command.refresh):
                    msg = msg + command.refresh
                try:
                    msg = msg.encode('utf-8', 'replace')
                except AttributeError:
                    pass
                if is_secret:
                    log.logger.debug(i18n.send_msg, i18n.hide_sensitive_info)
                else:
                    log.logger.debug(i18n.send_msg, str(msg))
                try:
                    self._core.read_very_eager()
                    self._core.write(msg)
                except EOFError:
                    raise exceptions.ConnectionClosed()
                if break_detect_after_send:
                    return -1
                msg = ''
                receive_data_buffer = bytes()
                start_time = time.time()
                mid_time = time.time()
                while mid_time - start_time < current_screen_timeout:
                    try:
                        data = self._core.read_very_eager()
                    except EOFError:
                        return -1
                    receive_data_buffer += data
                    screen, find_target, is_secret, break_detect_after_send, use_too_many_res, msg, target_index = \
                        self._decode_screen(receive_data_buffer, start_time, target_list, is_secret, refresh, msg)
                    if target_index != -1:
                        return target_index
                    if use_too_many_res:
                        continue
                    if find_target:
                        break
                    if len(screen) > 0:
                        screens.show(self.config, screen)
                        self._RDQ.add(screen)
                    mid_time = time.time()
                if not find_target:
                    return -1
            return -2
        else:
            loop = self._get_event_loop()
            return loop.run_until_complete(
                self._async_send(msg, target_list, screen_timeout, refresh, secret)
            )

    def close(self):
        if self.config.connect_mode == data_type.ConnectMode.WEBSOCKETS:
            if self._core and self._core.open:
                loop = self._get_event_loop()
                loop.run_until_complete(self._core.close())
        else:
            self._core.close()

    def get_screen_queue(self) -> list:
        return self._RDQ.get(1)