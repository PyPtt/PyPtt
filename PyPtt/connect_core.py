import time
import asyncio
import websockets
import telnetlib
import re
import traceback
import threading
from uao import register_uao

register_uao()

try:
    from . import data_type
    from . import i18n
    from . import log
    from . import screens
    from . import command
    from . import exceptions
except ModuleNotFoundError:
    import data_type
    import i18n
    import log
    import screens
    import command
    import exceptions

new_event_loop = []


class connect_mode(object):
    TELNET = 1
    WEBSOCKET = 2

    min_value = TELNET
    max_value = WEBSOCKET


class TargetUnit(object):
    def __init__(
            self,
            display_msg,
            detect_target,
            log_level: int = 0,
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
        if log_level == 0:
            self._log_level = log.level.INFO
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


async def websocket_receiver(core, screen_time_out, recv_data_obj):
    # Wait for at most 1 second
    await asyncio.wait_for(
        websocket_recv_func(core, recv_data_obj),
        timeout=screen_time_out
    )


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

        self.config = config
        self._RDQ = ReceiveDataQueue()
        self._UseTooManyResources = TargetUnit(
            [
                i18n.UseTooManyResources,
            ],
            screens.Target.UseTooManyResources,
            exceptions_=exceptions.UseTooManyResources()
        )

        log.show_value(
            self.config, log.level.INFO, [
                i18n.connect_core,
            ],
            i18n.Init
        )

    def connect(self) -> None:
        def _wait():
            for i in range(self.config.retry_wait_time):
                log.show_value(
                    self.config, log.level.INFO, [
                        i18n.Prepare,
                        i18n.Again,
                        i18n.Connect,
                        i18n.PTT,
                    ],
                    str(self.config.retry_wait_time - i)
                )
                time.sleep(1)

        log.show_value(
            self.config, log.level.INFO, [
                i18n.connect_core,
            ],
            i18n.Active
        )

        telnet_host, websocket_host, websocket_origin = '', '', ''
        if self.config.host == data_type.host_type.PTT1:
            telnet_host = 'ptt.cc'
            websocket_host = 'wss://ws.ptt.cc/bbs/'
            websocket_origin = 'https://term.ptt.cc'
        elif self.config.host == data_type.host_type.PTT2:
            telnet_host = 'ptt2.cc'
            websocket_host = 'wss://ws.ptt2.cc/bbs/'
            websocket_origin = 'https://term.ptt2.cc'
        else:
            telnet_host = 'localhost'
            websocket_host = 'wss://localhost'
            websocket_origin = 'https://term.ptt.cc'

        if self.config.connect_mode == connect_mode.TELNET:
            log.show_value(
                self.config,
                log.level.INFO,
                i18n.ConnectMode,
                i18n.ConnectMode_Telnet
            )
        elif self.config.connect_mode == connect_mode.WEBSOCKET:
            log.show_value(
                self.config,
                log.level.INFO,
                i18n.ConnectMode,
                i18n.ConnectMode_WebSocket
            )

        connect_success = False

        global new_event_loop
        thread_id = threading.get_ident()

        for _ in range(2):

            try:
                if self.config.connect_mode == connect_mode.TELNET:

                    self._core = telnetlib.Telnet(telnet_host, self.config.port)

                else:

                    if thread_id not in new_event_loop:
                        new_event_loop.append(thread_id)
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                        except Exception as e:
                            pass

                    self._core = asyncio.get_event_loop().run_until_complete(
                        websockets.connect(
                            websocket_host,
                            origin=websocket_origin
                        )
                    )

                connect_success = True
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)
                if self.config.host == data_type.host_type.PTT1:
                    log.show_value(
                        self.config, log.level.INFO, [
                            i18n.Connect,
                            i18n.PTT,
                        ],
                        i18n.Fail
                    )
                else:
                    log.show_value(
                        self.config, log.level.INFO, [
                            i18n.Connect,
                            i18n.PTT2,
                        ],
                        i18n.Fail
                    )
                _wait()
                continue

            break

        if not connect_success:
            raise exceptions.ConnectError(self.config)

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

            recv_screen = re.sub(r'[\r]', '', recv_screen)
            # recv_screen = re.sub(r'[\x00-\x08]', '', recv_screen)
            recv_screen = re.sub(r'[\x00-\x07]', '', recv_screen)
            # print(recv_screen)
            recv_screen = re.sub(r'[\x0b\x0c]', '', recv_screen)
            # screen = re.sub(r'[\x0e-\x1f]', '', screen)

            recv_screen = re.sub(r'[\x0e-\x1A]', '', recv_screen)
            recv_screen = re.sub(r'[\x1C-\x1F]', '', recv_screen)
            recv_screen = re.sub(r'[\x7f-\xff]', '', recv_screen)

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
        break_index = -1
        is_secret = secret

        use_too_many_res = False
        while True:

            if refresh and not msg.endswith(command.Refresh):
                msg = msg + command.Refresh
            try:
                msg = msg.encode('big5-uao', 'replace')

            except AttributeError:
                pass
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)
                msg = msg.encode('big5', 'replace')

            if is_secret:
                log.show_value(
                    self.config,
                    log.level.DEBUG, [
                        i18n.SendMsg
                    ],
                    i18n.HideSensitiveInfor
                )
            else:
                log.show_value(
                    self.config,
                    log.level.DEBUG, [
                        i18n.SendMsg
                    ],
                    msg
                )
            if self.config.connect_mode == connect_mode.TELNET:
                try:
                    self._core.read_very_eager()
                    self._core.write(msg)
                except EOFError:
                    raise exceptions.ConnectionClosed()
            else:
                try:
                    asyncio.get_event_loop().run_until_complete(
                        self._core.send(msg)
                    )
                except websockets.exceptions.ConnectionClosedError:
                    raise exceptions.ConnectionClosed()
                except RuntimeError:
                    raise exceptions.ConnectionClosed()
                except websockets.exceptions.ConnectionClosedOK:
                    raise exceptions.ConnectionClosed()

                if break_detect_after_send:
                    return break_index

            msg = ''
            receive_data_buffer = bytes()

            # print(f'0 {use_too_many_res}')
            start_time = time.time()
            mid_time = time.time()
            while mid_time - start_time < current_screen_timeout:

                recv_data_obj = RecvData()

                if self.config.connect_mode == connect_mode.TELNET:
                    try:
                        recv_data_obj.data = self._core.read_very_eager()
                    except EOFError:
                        return -1
                else:
                    try:

                        asyncio.get_event_loop().run_until_complete(
                            websocket_receiver(
                                self._core, current_screen_timeout, recv_data_obj)
                        )

                    except websockets.exceptions.ConnectionClosed:
                        # print(f'0.1 {use_too_many_res}')
                        if use_too_many_res:
                            # print(f'0.2 {use_too_many_res}')
                            raise exceptions.UseTooManyResources()
                        # print(f'0.3 {use_too_many_res}')
                        raise exceptions.ConnectionClosed()
                    except websockets.exceptions.ConnectionClosedOK:
                        raise exceptions.ConnectionClosed()
                    except asyncio.TimeoutError:
                        return -1

                receive_data_buffer += recv_data_obj.data
                receive_data_temp = receive_data_buffer.decode(
                    'big5-uao', errors='replace'
                )
                screen = clean_screen(receive_data_temp)

                find_target = False
                for Target in target_list:
                    condition = Target.is_match(screen)
                    if condition:
                        if Target._Handler is not None:
                            Target._Handler(screen)
                        if len(screen) > 0:
                            screens.show(self.config, screen)
                            self._RDQ.add(screen)
                            # self._ReceiveDataQueue.append(screen)
                            if Target == self._UseTooManyResources:
                                # print('!!!!!!!!!!!!!!!')
                                use_too_many_res = True
                                # print(f'1 {use_too_many_res}')
                                break
                            Target.raise_exception()

                        find_target = True

                        log.show_value(
                            self.config,
                            Target.get_log_level(),
                            [
                                i18n.PTT,
                                i18n.Msg
                            ],
                            Target.get_display_msg()
                        )

                        end_time = time.time()
                        log.show_value(
                            self.config,
                            log.level.DEBUG, [
                                i18n.SpendTime,
                            ],
                            round(end_time - start_time, 2)
                        )

                        if Target.is_break():
                            return target_list.index(Target)

                        msg = Target.get_response(screen)

                        add_refresh = False
                        if Target.is_refresh():
                            add_refresh = True
                        elif refresh:
                            add_refresh = True

                        if add_refresh:
                            if not msg.endswith(command.Refresh):
                                msg = msg + command.Refresh

                        is_secret = Target.is_secret()

                        if Target.is_break_after_send():
                            break_index = target_list.index(Target)
                            break_detect_after_send = True
                        break

                # print(f'2 {use_too_many_res}')
                if use_too_many_res:
                    # print(f'3 {use_too_many_res}')
                    continue
                # print(f'4 {use_too_many_res}')

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
        if self.config.connect_mode == connect_mode.WEBSOCKET:
            asyncio.get_event_loop().run_until_complete(self._core.close())
        else:
            self._core.close()

    def get_screen_queue(self) -> list:
        return self._RDQ.get(1)
