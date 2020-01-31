
import time
import asyncio
import websockets
import re
import traceback
import threading
from uao import register_uao
register_uao()

try:
    from . import DataType
    from . import i18n
    from . import Log
    from . import Screens
    from . import Command
    from . import Exceptions
except ModuleNotFoundError:
    import DataType
    import i18n
    import Log
    import Screens
    import Command
    import Exceptions

new_event_loop = []


class ConnectMode(object):

    Telnet = 1
    WebSocket = 2

    MinValue = WebSocket
    MaxValue = WebSocket


class TargetUnit(object):
    def __init__(
        self,
        display_msg,
        detect_target,
        log_level: int = 0,
        response: str = '',
        break_detect=False,
        break_detect_after_send=False,
        exceptions=None,
        refresh=True,
        secret=False,
        handler=None):

        self._DisplayMsg = display_msg
        self._DetectTarget = detect_target
        if log_level == 0:
            self._LogLevel = Log.Level.INFO
        else:
            self._LogLevel = log_level
        self._Response = response
        self._BreakDetect = break_detect
        self._Exception = exceptions
        self._Refresh = refresh
        self._BreakAfterSend = break_detect_after_send
        self._Secret = secret
        self._Handler = handler

    def is_match(self, screen: str):
        if isinstance(self._DetectTarget, str):
            if self._DetectTarget in screen:
                return True
            return False
        elif isinstance(self._DetectTarget, list):
            for Target in self._DetectTarget:
                if Target not in screen:
                    return False
            return True

    def get_display_msg(self):
        if callable(self._DisplayMsg):
            return self._DisplayMsg()
        return self._DisplayMsg

    def get_detect_target(self):
        return self._DetectTarget

    def get_log_level(self):
        return self._LogLevel

    def get_response(self, Screen: str):
        if callable(self._Response):
            return self._Response(Screen)
        return self._Response

    def is_break(self):
        return self._BreakDetect

    def raise_exception(self):
        if isinstance(self._Exception, Exception):
            raise self._Exception

    def is_refresh(self):
        return self._Refresh

    def is_break_after_send(self):
        return self._BreakAfterSend

    def is_secret(self):
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
    def __init__(self, config, host: int):

        self.Config = config
        self._Host = host
        self._RDQ = ReceiveDataQueue()
        self._UseTooManyResources = TargetUnit(
            [
                i18n.UseTooManyResources,
            ],
            Screens.Target.UseTooManyResources,
            exceptions=Exceptions.UseTooManyResources
        )

        Log.show_value(self.Config, Log.Level.INFO, [
            i18n.ConnectCore,
        ],
                       i18n.Init
                       )

    def connect(self):
        def _wait():
            for i in range(self.Config.RetryWaitTime):
                Log.show_value(self.Config, Log.Level.INFO, [
                    i18n.Prepare,
                    i18n.Again,
                    i18n.Connect,
                    i18n.PTT,
                ],
                               str(self.Config.RetryWaitTime - i)
                               )
                time.sleep(1)

        Log.show_value(self.Config, Log.Level.INFO, [
            i18n.ConnectCore,
        ],
                       i18n.Active
                       )

        connect_success = False

        global new_event_loop
        threadid = threading.get_ident()

        for _ in range(2):

            try:

                if threadid not in new_event_loop:
                    new_event_loop.append(threadid)
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    except Exception as e:
                        pass

                if self._Host == DataType.Host.PTT1:
                    self._Core = asyncio.get_event_loop().run_until_complete(
                        websockets.connect(
                            'wss://ws.ptt.cc/bbs/',
                            origin='https://term.ptt.cc'
                        )
                    )
                else:
                    self._Core = asyncio.get_event_loop().run_until_complete(
                        websockets.connect(
                            'wss://ws.ptt2.cc/bbs',
                            origin='https://term.ptt2.cc'
                        )
                    )

                connect_success = True
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)
                if self._Host == DataType.Host.PTT1:
                    Log.show_value(self.Config, Log.Level.INFO, [
                        i18n.Connect,
                        i18n.PTT,
                    ],
                                   i18n.Fail
                                   )
                else:
                    Log.show_value(self.Config, Log.Level.INFO, [
                        i18n.Connect,
                        i18n.PTT2,
                    ],
                                   i18n.Fail
                                   )
                _wait()
                continue

            break

        if not connect_success:
            raise Exceptions.ConnectError(self.Config)

    def send(
        self,
        msg: str,
        target_list: list,
        screen_timeout: int = 0,
        refresh: bool = True,
        secret: bool = False
    ) -> int:

        def clean_screen(screen: str, NoColor: bool = True) -> str:

            if not screen:
                return screen
            # http://asf.atmel.com/docs/latest/uc3l/html/group__group__avr32__utils__print__funcs.html#ga024c3e2852fe509450ebc363df52ae73

                # screen = re.sub('\[[\d+;]*m', '', screen)

            screen = re.sub(r'[\r]', '', screen)
            screen = re.sub(r'[\x00-\x08]', '', screen)
            screen = re.sub(r'[\x0b\x0c]', '', screen)
            # screen = re.sub(r'[\x0e-\x1f]', '', screen)

            screen = re.sub(r'[\x0e-\x1A]', '', screen)

            screen = re.sub(r'[\x1C-\x1F]', '', screen)
            screen = re.sub(r'[\x7f-\xff]', '', screen)

            screen = Screens.vt100(screen)

            return screen

        if not all(isinstance(T, TargetUnit) for T in target_list):
            raise ValueError('Item of TargetList must be TargetUnit')

        if self._UseTooManyResources not in target_list:
            target_list.append(self._UseTooManyResources)

        if screen_timeout == 0:
            current_screen_timeout = self.Config.ScreenTimeOut
        else:
            current_screen_timeout = screen_timeout

        break_detect_after_send = False
        break_index = -1
        is_secret = secret

        use_too_many_res = False
        while True:

            if refresh and not msg.endswith(Command.Refresh):
                msg = msg + Command.Refresh
            try:
                msg = msg.encode('big5-uao', 'replace')

            except AttributeError:
                pass
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)
                msg = msg.encode('big5', 'replace')

            if is_secret:
                Log.show_value(
                    self.Config,
                    Log.Level.DEBUG, [
                        i18n.SendMsg
                    ],
                    i18n.HideSensitiveInfor
                )
            else:
                Log.show_value(
                    self.Config,
                    Log.Level.DEBUG, [
                        i18n.SendMsg
                    ],
                    msg
                )

            try:
                asyncio.get_event_loop().run_until_complete(
                    self._Core.send(msg)
                )
            except websockets.exceptions.ConnectionClosedError:
                raise Exceptions.ConnectionClosed()
            except RuntimeError:
                raise Exceptions.ConnectionClosed()
            except websockets.exceptions.ConnectionClosedOK:
                raise Exceptions.ConnectionClosed()

            if break_detect_after_send:
                return break_index

            msg = ''
            receive_data_buffer = bytes()

            # print(f'0 {use_too_many_res}')
            start_time = time.time()
            mid_time = time.time()
            while mid_time - start_time < current_screen_timeout:
                try:
                    recv_data_obj = RecvData()
                    asyncio.get_event_loop().run_until_complete(
                        websocket_receiver(
                            self._Core, current_screen_timeout, recv_data_obj)
                    )

                except websockets.exceptions.ConnectionClosed:
                    # print(f'0.1 {use_too_many_res}')
                    if use_too_many_res:
                        # print(f'0.2 {use_too_many_res}')
                        raise Exceptions.UseTooManyResources()
                    # print(f'0.3 {use_too_many_res}')
                    raise Exceptions.ConnectionClosed()
                except websockets.exceptions.ConnectionClosedOK:
                    raise Exceptions.ConnectionClosed()
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
                            Target._Handler()
                        if len(screen) > 0:
                            Screens.show(self.Config, screen)
                            self._RDQ.add(screen)
                            # self._ReceiveDataQueue.append(screen)
                            if Target == self._UseTooManyResources:
                                # print('!!!!!!!!!!!!!!!')
                                use_too_many_res = True
                                # print(f'1 {use_too_many_res}')
                                break
                            Target.raise_exception()

                        find_target = True

                        Log.show_value(
                            self.Config,
                            Target.get_log_level(), [
                                i18n.PTT,
                                i18n.Msg
                            ],
                            Target.get_display_msg()
                        )

                        end_time = time.time()
                        Log.show_value(
                            self.Config,
                            Log.Level.DEBUG, [
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
                            if not msg.endswith(Command.Refresh):
                                msg = msg + Command.Refresh

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
                    Screens.show(self.Config, screen)
                    self._RDQ.add(screen)
                    # self._ReceiveDataQueue.append(screen)

                mid_time = time.time()

            if not find_target:
                raise Exceptions.NoMatchTargetError(self._RDQ)
        raise Exceptions.NoMatchTargetError(self._RDQ)

    def close(self):
        asyncio.get_event_loop().run_until_complete(self._Core.close())

    def get_screen_queue(self) -> list:
        return self._RDQ.get(1)
