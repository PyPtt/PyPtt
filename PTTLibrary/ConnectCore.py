
import time
import asyncio
import websockets
import re
import traceback
from uao import register_uao
register_uao()

try:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import Log
    from . import Screens
    from . import Command
    from . import Exceptions
except ModuleNotFoundError:
    import DataType
    import Config
    import Util
    import i18n
    import Log
    import Screens
    import Command
    import Exceptions


class ConnectMode(object):

    Telnet = 1
    WebSocket = 2

    MinValue = WebSocket
    MaxValue = WebSocket


class TargetUnit(object):
    def __init__(
        self,
        DisplayMsg,
        DetectTarget,
        LogLevel: int = 0,
        Response: str = '',
        BreakDetect=False,
        BreakDetectAfterSend=False,
        Exceptions=None,
        Refresh=True,
        Secret=False,
        Handler=None
    ):

        self._DisplayMsg = DisplayMsg
        self._DetectTarget = DetectTarget
        if LogLevel == 0:
            self._LogLevel = Log.Level.INFO
        else:
            self._LogLevel = LogLevel
        self._Response = Response
        self._BreakDetect = BreakDetect
        self._Exception = Exceptions
        self._Refresh = Refresh
        self._BreakAfterSend = BreakDetectAfterSend
        self._Secret = Secret
        self._Handler = Handler

    def isMatch(self, Screen: str):
        if isinstance(self._DetectTarget, str):
            if self._DetectTarget in Screen:
                return True
            return False
        elif isinstance(self._DetectTarget, list):
            for Target in self._DetectTarget:
                if Target not in Screen:
                    return False
            return True

    def getDisplayMsg(self):
        if callable(self._DisplayMsg):
            return self._DisplayMsg()
        return self._DisplayMsg

    def getDetectTarget(self):
        return self._DetectTarget

    def getLogLevel(self):
        return self._LogLevel

    def getResponse(self, Screen: str):
        if callable(self._Response):
            return self._Response(Screen)
        return self._Response

    def isBreak(self):
        return self._BreakDetect

    def raiseException(self):
        if self._Exception is not None:
            raise self._Exception

    def isRefresh(self):
        return self._Refresh

    def isBreakAfterSend(self):
        return self._BreakAfterSend

    def isSecret(self):
        return self._Secret


_WSRecvData = None


async def WebsocketRecvFunc(Core):
    global _WSRecvData
    _WSRecvData = await Core.recv()


async def WebsocketReceiver(Core, ScreenTimeOut):
    # Wait for at most 1 second
    await asyncio.wait_for(
        WebsocketRecvFunc(Core),
        timeout=ScreenTimeOut
    )


class ReceiveDataQueue(object):
    def __init__(self):
        self._ReceiveDataQueue = []

    def add(self, Screen):
        self._ReceiveDataQueue.append(Screen)
        self._ReceiveDataQueue = self._ReceiveDataQueue[-10:]

    def get(self, Last=1):
        return self._ReceiveDataQueue[-Last:]


class API(object):
    def __init__(self, Host: int):

        self._Host = Host
        self._RDQ = ReceiveDataQueue()
        self._UseTooManyResources = TargetUnit(
            [
                i18n.UseTooManyResources,
            ],
            Screens.Target.UseTooManyResources,
            Exceptions=Exceptions.UseTooManyResources
        )

        Log.showValue(Log.Level.INFO, [
            i18n.ConnectCore,
        ],
            i18n.Init
        )

    def connect(self):
        def _wait():
            for i in range(Config.RetryWaitTime):
                Log.showValue(Log.Level.INFO, [
                    i18n.Prepare,
                    i18n.Again,
                    i18n.Connect,
                    i18n.PTT,
                ],
                    str(Config.RetryWaitTime - i)
                )
                time.sleep(1)

        Log.showValue(Log.Level.INFO, [
            i18n.ConnectCore,
        ],
            i18n.Active
        )

        ConnectSuccess = False

        for _ in range(2):

            try:
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

                ConnectSuccess = True
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)
                if self._Host == DataType.Host.PTT1:
                    Log.showValue(Log.Level.INFO, [
                        i18n.Connect,
                        i18n.PTT,
                    ],
                        i18n.Fail
                    )
                else:
                    Log.showValue(Log.Level.INFO, [
                        i18n.Connect,
                        i18n.PTT2,
                    ],
                        i18n.Fail
                    )
                _wait()
                continue

            break

        if not ConnectSuccess:
            raise Exceptions.ConnectError()

    def send(
        self,
        Msg: str,
        TargetList: list,
        ScreenTimeout: int = 0,
        Refresh: bool = True,
        Secret: bool = False
    ) -> int:

        if not all(isinstance(T, TargetUnit) for T in TargetList):
            raise ValueError('Item of TargetList must be TargetUnit')

        if self._UseTooManyResources not in TargetList:
            TargetList.append(self._UseTooManyResources)

        if ScreenTimeout == 0:
            CurrentScreenTimeout = Config.ScreenTimeOut
        else:
            CurrentScreenTimeout = ScreenTimeout

        BreakDetectAfterSend = False
        BreakIndex = -1
        isSecret = Secret

        UseTooManyRes = False
        while True:

            if Refresh and not Msg.endswith(Command.Refresh):
                Msg = Msg + Command.Refresh
            try:
                Msg = Msg.encode('big5-uao', 'replace')

            except AttributeError:
                pass
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)
                Msg = Msg.encode('big5', 'replace')

            if isSecret:
                Log.showValue(
                    Log.Level.DEBUG, [
                        i18n.SendMsg
                    ],
                    i18n.HideSensitiveInfor
                )
            else:
                Log.showValue(
                    Log.Level.DEBUG, [
                        i18n.SendMsg
                    ],
                    Msg
                )

            try:
                asyncio.get_event_loop().run_until_complete(
                    self._Core.send(Msg)
                )
            except websockets.exceptions.ConnectionClosedError:
                raise Exceptions.ConnectionClosed()
            except RuntimeError:
                raise Exceptions.ConnectionClosed()
            except websockets.exceptions.ConnectionClosedOK:
                raise Exceptions.ConnectionClosed()

            if BreakDetectAfterSend:
                return BreakIndex

            Msg = ''
            ReceiveDataBuffer = bytes()

            # print(f'0 {UseTooManyRes}')
            StartTime = time.time()
            MidTime = time.time()
            while MidTime - StartTime < CurrentScreenTimeout:
                try:
                    asyncio.get_event_loop().run_until_complete(
                        WebsocketReceiver(self._Core, CurrentScreenTimeout)
                    )
                    ReceiveDataTemp = _WSRecvData

                except websockets.exceptions.ConnectionClosed:
                    # print(f'0.1 {UseTooManyRes}')
                    if UseTooManyRes:
                        # print(f'0.2 {UseTooManyRes}')
                        raise Exceptions.UseTooManyResources()
                    # print(f'0.3 {UseTooManyRes}')
                    raise Exceptions.ConnectionClosed()
                except websockets.exceptions.ConnectionClosedOK:
                    raise Exceptions.ConnectionClosed()
                except asyncio.TimeoutError:
                    return -1

                ReceiveDataBuffer += ReceiveDataTemp
                ReceiveDataTemp = ReceiveDataBuffer.decode(
                    'big5-uao', errors='replace'
                )
                Screen = self._cleanScreen(ReceiveDataTemp)

                FindTarget = False
                for Target in TargetList:

                    Condition = Target.isMatch(Screen)
                    if Condition:
                        if Target._Handler is not None:
                            Target._Handler()
                        if len(Screen) > 0:
                            Screens.show(Screen)
                            self._RDQ.add(Screen)
                            # self._ReceiveDataQueue.append(Screen)
                            if Target == self._UseTooManyResources:
                                # print('!!!!!!!!!!!!!!!')
                                UseTooManyRes = True
                                # print(f'1 {UseTooManyRes}')
                                break
                            Target.raiseException()

                        FindTarget = True

                        Log.showValue(Target.getLogLevel(), [
                            i18n.PTT,
                            i18n.Msg
                        ],
                            Target.getDisplayMsg()
                        )

                        EndTime = time.time()
                        Log.showValue(Log.Level.DEBUG, [
                            i18n.SpendTime,
                        ],
                            round(EndTime - StartTime, 2)
                        )

                        if Target.isBreak():
                            return TargetList.index(Target)

                        Msg = Target.getResponse(Screen)

                        AddRefresh = False
                        if Target.isRefresh():
                            AddRefresh = True
                        elif Refresh:
                            AddRefresh = True

                        if AddRefresh:
                            if not Msg.endswith(Command.Refresh):
                                Msg = Msg + Command.Refresh

                        isSecret = Target.isSecret()

                        if Target.isBreakAfterSend():
                            BreakIndex = TargetList.index(Target)
                            BreakDetectAfterSend = True
                        break
                
                # print(f'2 {UseTooManyRes}')
                if UseTooManyRes:
                    # print(f'3 {UseTooManyRes}')
                    continue
                # print(f'4 {UseTooManyRes}')

                if FindTarget:
                    break
                if len(Screen) > 0:
                    Screens.show(Screen)
                    self._RDQ.add(Screen)
                    # self._ReceiveDataQueue.append(Screen)

                MidTime = time.time()

            if not FindTarget:
                raise Exceptions.NoMatchTargetError(self._RDQ)
        raise Exceptions.NoMatchTargetError(self._RDQ)

    def close(self):
        asyncio.get_event_loop().run_until_complete(self._Core.close())

    def _cleanScreen(self, screen: str, NoColor: bool = True) -> str:

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

        screen = Screens.VT100(screen)

        return screen

    def getScreenQueue(self) -> list:
        return self._RDQ.get(1)
