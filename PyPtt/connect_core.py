from __future__ import annotations

import asyncio
import ssl
import telnetlib
import threading
import time
import traceback
import warnings
from typing import Any

import websockets
import websockets.exceptions
import websockets.http
from SingleLog import LogLevel, DefaultLogger

import PyPtt
from . import command
from . import data_type
from . import exceptions
from . import i18n
from . import screens

websockets.http.USER_AGENT += f' PyPtt/{PyPtt.__version__}'

ssl_context = ssl.create_default_context()


class TargetUnit:
    def __init__(self, detect_target, log_level: LogLevel = None, response: [Any | str] = '', break_detect=False,
                 break_detect_after_send=False, exceptions_=None, refresh=True, secret=False, handler=None,
                 max_match: int = 0):

        self._DetectTarget = detect_target
        if log_level is None:
            self._log_level = LogLevel.INFO
        else:
            self._log_level = log_level
        self._Response = response
        self._BreakDetect = break_detect
        self._Exception = exceptions_
        self._Refresh = refresh
        self._BreakAfterSend = break_detect_after_send
        self._Secret = secret
        self._Handler = handler
        self._max_match = max_match
        self._current_match = 0

    def is_match(self, screen: str) -> bool:
        if self._current_match >= self._max_match > 0:
            return False
        if isinstance(self._DetectTarget, str):
            if self._DetectTarget in screen:
                self._current_match += 1
                return True
            return False
        elif isinstance(self._DetectTarget, list):
            for Target in self._DetectTarget:
                if Target not in screen:
                    return False
            self._current_match += 1
            return True

    def get_detect_target(self):
        return self._DetectTarget

    def get_log_level(self) -> int:
        return self._log_level

    def get_response(self, screen: str) -> str:
        if callable(self._Response):
            return self._Response(screen)
        return self._Response

    def is_break(self) -> bool:
        return self._BreakDetect

    def raise_exception(self):
        if isinstance(self._Exception, Exception):
            raise self._Exception

    def is_refresh(self) -> bool:
        return self._Refresh

    def is_break_after_send(self) -> bool:
        return self._BreakAfterSend

    def is_secret(self) -> bool:
        return self._Secret


class RecvData:
    def __init__(self):
        self.data = None


async def websocket_recv_func(core, recv_data_obj):
    recv_data_obj.data = await core.recv()


async def websocket_receiver(core, screen_timeout, recv_data_obj):
    # Wait for at most 1 second
    await asyncio.wait_for(
        websocket_recv_func(core, recv_data_obj),
        timeout=screen_timeout)


class ReceiveDataQueue(object):
    def __init__(self):
        self._ReceiveDataQueue = []

    def add(self, screen):
        self._ReceiveDataQueue.append(screen)
        self._ReceiveDataQueue = self._ReceiveDataQueue[-10:]

    def get(self, last=1):
        return self._ReceiveDataQueue[-last:]


class API(object):
    def __init__(self, config):

        self.current_encoding = 'big5uao'
        self.config = config
        self._RDQ = ReceiveDataQueue()
        self._UseTooManyResources = TargetUnit(screens.Target.use_too_many_resources,
                                               exceptions_=exceptions.UseTooManyResources())

        self.logger = DefaultLogger('connect', self.config.log_level)
        self.ptt_logger = DefaultLogger(i18n.PTT if self.config.host == data_type.HOST.PTT1 else i18n.PTT2,
                                     self.config.log_level)

    def connect(self) -> None:
        def _wait():
            for i in range(self.config.retry_wait_time):

                if self.config.host == data_type.HOST.PTT1:
                    self.logger.info(i18n.prepare_connect_again, i18n.PTT, str(self.config.retry_wait_time - i))
                elif self.config.host == data_type.HOST.PTT2:
                    self.logger.info(i18n.prepare_connect_again, i18n.PTT2, str(self.config.retry_wait_time - i))
                elif self.config.host == data_type.HOST.LOCALHOST:
                    self.logger.info(i18n.prepare_connect_again, i18n.localhost, str(self.config.retry_wait_time - i))
                else:
                    self.logger.info(i18n.prepare_connect_again, self.config.host, str(self.config.retry_wait_time - i))

                time.sleep(1)

        warnings.filterwarnings("ignore", category=DeprecationWarning)

        self.current_encoding = 'big5uao'
        # self.log.py.info(i18n.connect_core, i18n.active)

        if self.config.host == data_type.HOST.PTT1:
            telnet_host = 'ptt.cc'
            websocket_host = 'wss://ws.ptt.cc/bbs/'
            websocket_origin = 'https://term.ptt.cc'
        elif self.config.host == data_type.HOST.PTT2:
            telnet_host = 'ptt2.cc'
            websocket_host = 'wss://ws.ptt2.cc/bbs/'
            websocket_origin = 'https://term.ptt2.cc'
        elif self.config.host == data_type.HOST.LOCALHOST:
            telnet_host = 'localhost'
            websocket_host = 'wss://localhost'
            websocket_origin = 'https://term.ptt.cc'
        else:
            telnet_host = self.config.host
            websocket_host = f'wss://{self.config.host}'
            websocket_origin = 'https://term.ptt.cc'

        connect_success = False

        for _ in range(2):

            try:
                if self.config.connect_mode == data_type.ConnectMode.TELNET:
                    self._core = telnetlib.Telnet(telnet_host, self.config.port)
                else:
                    if not threading.current_thread() is threading.main_thread():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    self.logger.debug('USER_AGENT', websockets.http.USER_AGENT)
                    self._core = asyncio.get_event_loop().run_until_complete(
                        websockets.connect(
                            websocket_host,
                            origin=websocket_origin,
                            ssl=ssl_context))

                connect_success = True
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)

                if self.config.host == data_type.HOST.PTT1:
                    self.logger.info(i18n.connect, i18n.PTT, i18n.fail)
                elif self.config.host == data_type.HOST.PTT2:
                    self.logger.info(i18n.connect, i18n.PTT2, i18n.fail)
                elif self.config.host == data_type.HOST.LOCALHOST:
                    self.logger.info(i18n.connect, i18n.localhost, i18n.fail)
                else:
                    self.logger.info(i18n.connect, self.config.host, i18n.fail)

                _wait()
                continue

            break

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
            condition = target.is_match(screen)
            if condition:
                if target._Handler is not None:
                    target._Handler(screen)
                if len(screen) > 0:
                    screens.show(self.config, screen)
                    self._RDQ.add(screen)
                    if target == self._UseTooManyResources:
                        use_too_many_res = True
                        # print(f'1 {use_too_many_res}')
                        break
                    target.raise_exception()

                find_target = True

                # self.ptt_logger.info(target.get_display_msg())

                # if target.get_display_msg() == '登入成功':
                #     print(type(receive_data_buffer), receive_data_buffer)
                #     print(receive_data_buffer == temp)

                end_time = time.time()
                self.logger.debug(i18n.spend_time, round(end_time - start_time, 3))

                if target.is_break():
                    target_index = target_list.index(target)
                    break

                msg = target.get_response(screen)

                add_refresh = False
                if target.is_refresh():
                    add_refresh = True
                elif refresh:
                    add_refresh = True

                if add_refresh:
                    if not msg.endswith(command.refresh):
                        msg = msg + command.refresh

                is_secret = target.is_secret()

                if target.is_break_after_send():
                    # break_index = target_list.index(target)
                    break_detect_after_send = True
                break
        return screen, find_target, is_secret, break_detect_after_send, use_too_many_res, msg, target_index

    def send(self, msg: str, target_list: list, screen_timeout: int = 0, refresh: bool = True,
             secret: bool = False) -> int:

        if not all(isinstance(T, TargetUnit) for T in target_list):
            raise ValueError('Item of TargetList must be TargetUnit')

        if self._UseTooManyResources not in target_list:
            target_list.append(self._UseTooManyResources)

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
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)
                msg = msg.encode('utf-8', 'replace')

            if is_secret:
                self.logger.debug(i18n.send_msg, i18n.hide_sensitive_info)
            else:
                self.logger.debug(i18n.send_msg, str(msg))

            if self.config.connect_mode == data_type.ConnectMode.TELNET:
                try:
                    self._core.read_very_eager()
                    self._core.write(msg)
                except EOFError:
                    raise exceptions.ConnectionClosed()
            else:
                try:
                    asyncio.get_event_loop().run_until_complete(
                        self._core.send(msg))
                except websockets.exceptions.ConnectionClosedError:
                    raise exceptions.ConnectionClosed()
                except RuntimeError:
                    raise exceptions.ConnectionClosed()
                except websockets.exceptions.ConnectionClosedOK:
                    raise exceptions.ConnectionClosed()

                if break_detect_after_send:
                    return -1

            msg = ''
            receive_data_buffer = bytes()

            start_time = time.time()
            mid_time = time.time()
            while mid_time - start_time < current_screen_timeout:

                # print(1)
                recv_data_obj = RecvData()

                if self.config.connect_mode == data_type.ConnectMode.TELNET:
                    try:
                        recv_data_obj.data = self._core.read_very_eager()
                    except EOFError:
                        return -1

                else:
                    try:

                        asyncio.get_event_loop().run_until_complete(
                            websocket_receiver(
                                self._core, current_screen_timeout, recv_data_obj))

                    except websockets.exceptions.ConnectionClosed:
                        if use_too_many_res:
                            raise exceptions.UseTooManyResources()
                        raise exceptions.ConnectionClosed()
                    except websockets.exceptions.ConnectionClosedOK:
                        raise exceptions.ConnectionClosed()
                    except asyncio.TimeoutError:
                        return -1
                    except RuntimeError:
                        raise exceptions.ConnectionClosed()

                receive_data_buffer += recv_data_obj.data

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

                # print(4)
                if target_index != -1:
                    return target_index

                if use_too_many_res:
                    continue

                if find_target:
                    break
                if len(screen) > 0:
                    screens.show(self.config, screen)
                    self._RDQ.add(screen)

                # print(6)

                mid_time = time.time()

            if not find_target:
                return -1
        return -2

    def close(self):
        if self.config.connect_mode == data_type.ConnectMode.WEBSOCKETS:
            asyncio.get_event_loop().run_until_complete(self._core.close())
        else:
            self._core.close()

    def get_screen_queue(self) -> list:
        return self._RDQ.get(1)
