import asyncio
import telnetlib
import threading
import time
import traceback
from enum import Enum, auto, unique

import websockets
import websockets.exceptions
import websockets.http
from SingleLog.log import Logger
from SingleLog.log import LoggerLevel
from uao import register_uao

from . import command
from . import data_type
from . import exceptions
from . import i18n
from . import screens
from . import version

register_uao()
websockets.http.USER_AGENT += f' PyPtt/{version.V}'


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


@unique
class ConnectMode(AutoName):
    TELNET = auto()
    WEBSOCKET = auto()


class TargetUnit:
    def __init__(self,
                 display_msg,
                 detect_target,
                 log_level: LoggerLevel = None,
                 response: str = '',
                 break_detect=False,
                 break_detect_after_send=False,
                 exceptions_=None,
                 refresh=True,
                 secret=False,
                 handler=None,
                 max_match: int = 0):

        self._DisplayMsg = display_msg
        self._DetectTarget = detect_target
        if log_level is None:
            self._log_level = Logger.INFO
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

    def get_display_msg(self) -> str:
        if callable(self._DisplayMsg):
            return self._DisplayMsg()
        return self._DisplayMsg

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
        self._ReceiveDataQueue = list()

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
        self._UseTooManyResources = TargetUnit(
            i18n.use_too_many_resources,
            screens.Target.use_too_many_resources,
            exceptions_=exceptions.use_too_many_resources())

        self.logger = Logger('connector', config.log_level)
        self.logger.info(i18n.connect_core, i18n.init)

        if self.config.connect_mode == ConnectMode.TELNET:
            self.logger.info(i18n.set_connect_mode, i18n.connect_mode_TELNET)
        elif self.config.connect_mode == ConnectMode.WEBSOCKET:
            self.logger.info(i18n.set_connect_mode, i18n.connect_mode_WEBSOCKET)

    def connect(self) -> None:
        def _wait():
            for i in range(self.config.retry_wait_time):

                if self.config.host == data_type.host_type.PTT1:
                    self.logger.info(i18n.prepare_connect_again, i18n.PTT, str(self.config.retry_wait_time - i))
                elif self.config.host == data_type.host_type.PTT2:
                    self.logger.info(i18n.prepare_connect_again, i18n.PTT2, str(self.config.retry_wait_time - i))
                elif self.config.host == data_type.host_type.LOCALHOST:
                    self.logger.info(i18n.prepare_connect_again, i18n.localhost, str(self.config.retry_wait_time - i))
                else:
                    self.logger.info(i18n.prepare_connect_again, self.config.host, str(self.config.retry_wait_time - i))

                time.sleep(1)

        self.current_encoding = 'big5uao'
        self.logger.info(i18n.connect_core, i18n.active)

        if self.config.host == data_type.host_type.PTT1:
            telnet_host = 'ptt.cc'
            websocket_host = 'wss://ws.ptt.cc/bbs/'
            websocket_origin = 'https://term.ptt.cc'
        elif self.config.host == data_type.host_type.PTT2:
            telnet_host = 'ptt2.cc'
            websocket_host = 'wss://ws.ptt2.cc/bbs/'
            websocket_origin = 'https://term.ptt2.cc'
        elif self.config.host == data_type.host_type.LOCALHOST:
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
                if self.config.connect_mode == ConnectMode.TELNET:
                    self._core = telnetlib.Telnet(telnet_host, self.config.port)
                else:
                    if not threading.current_thread() is threading.main_thread():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    self.logger.debug('USER_AGENT', websockets.http.USER_AGENT)
                    self._core = asyncio.get_event_loop().run_until_complete(
                        websockets.connect(
                            websocket_host,
                            origin=websocket_origin))

                connect_success = True
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)

                if self.config.host == data_type.host_type.PTT1:
                    self.logger.info(i18n.connect, i18n.PTT, i18n.fail)
                elif self.config.host == data_type.host_type.PTT2:
                    self.logger.info(i18n.connect, i18n.PTT2, i18n.fail)
                elif self.config.host == data_type.host_type.LOCALHOST:
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

                self.logger.debug(
                    i18n.ptt_msg,
                    target.get_display_msg())

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

    def send(
            self,
            msg: str,
            target_list: list,
            screen_timeout: int = 0,
            refresh: bool = True,
            secret: bool = False) -> int:

        def clean_screen(recv_screen: str, NoColor: bool = True) -> str:

            if not recv_screen:
                return recv_screen
            # http://asf.atmel.com/docs/latest/uc3l/html/group__group__avr32__lib_utils__print__funcs.html#ga024c3e2852fe509450ebc363df52ae73

            # screen = re.sub('\[[\d+;]*m', '', screen)

            # recv_screen = re.sub(r'[\r]', '', recv_screen)
            # recv_screen = re.sub(r'[\x00-\x07]', '', recv_screen)
            # recv_screen = re.sub(r'[\x0b\x0c]', '', recv_screen)
            # recv_screen = re.sub(r'[\x0e-\x1A]', '', recv_screen)
            # recv_screen = re.sub(r'[\x1C-\x1F]', '', recv_screen)
            # recv_screen = re.sub(r'[\x7f-\xff]', '', recv_screen)

            recv_screen = screens.vt100(recv_screen)

            return recv_screen

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
                msg = msg.encode('big5uao', 'replace')

            except AttributeError:
                pass
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)
                msg = msg.encode('big5', 'replace')

            if is_secret:
                self.logger.debug(i18n.send_msg, i18n.hide_sensitive_info)
            else:
                self.logger.debug(i18n.send_msg, msg)

            if self.config.connect_mode == ConnectMode.TELNET:
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

            # print(f'0 {use_too_many_res}')
            start_time = time.time()
            mid_time = time.time()
            while mid_time - start_time < current_screen_timeout:

                recv_data_obj = RecvData()

                if self.config.connect_mode == ConnectMode.TELNET:
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
                        # print(f'0.1 {use_too_many_res}')
                        if use_too_many_res:
                            # print(f'0.2 {use_too_many_res}')
                            raise exceptions.use_too_many_resources()
                        # print(f'0.3 {use_too_many_res}')
                        raise exceptions.ConnectionClosed()
                    except websockets.exceptions.ConnectionClosedOK:
                        raise exceptions.ConnectionClosed()
                    except asyncio.TimeoutError:
                        return -1
                    except RuntimeError:
                        raise exceptions.ConnectionClosed()

                receive_data_buffer += recv_data_obj.data
                # receive_data_temp = receive_data_buffer.decode(
                #     'utf-8', errors='replace')
                # screen = clean_screen(receive_data_temp)

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

                if target_index != -1:
                    return target_index

                if use_too_many_res:
                    continue

                if find_target:
                    break
                if len(screen) > 0:
                    screens.show(self.config, screen)
                    self._RDQ.add(screen)
                    # self._ReceiveDataQueue.append(screen)

                mid_time = time.time()

            if not find_target:
                # raise exceptions.NoMatchTargetError(self._RDQ)
                return -1
        # raise exceptions.NoMatchTargetError(self._RDQ)
        return -1

    def close(self):
        if self.config.connect_mode == ConnectMode.WEBSOCKET:
            asyncio.get_event_loop().run_until_complete(self._core.close())
        else:
            self._core.close()

    def get_screen_queue(self) -> list:
        return self._RDQ.get(1)
