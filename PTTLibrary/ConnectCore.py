
import sys
import time
import telnetlib
import asyncio
import websockets
import ssl
import re
import traceback
from uao import register_uao
register_uao()

try:
    import DataType
    import Config
    import Util
    import i18n
    import Log
    import Screens
    import Command
except ModuleNotFoundError:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import Log
    from . import Screens
    from . import Command


class ConnectMode(object):

    Telnet = 1
    WebSocket = 2

    MinValue = Telnet
    MaxValue = WebSocket


class ConnectError(Exception):
    def __init__(self):
        self.message = [i18n.Connect, i18n.Fail]

    def __str__(self):

        if Config.Language == i18n.Language.Chinese:
            return ''.join(self.message)
        return ' '.join(self.message)


class NoMatchTargetError(Exception):
    def __init__(self, ScreenQueue: list):
        self.ScreenQueue = ScreenQueue

    def __str__(self):
        Screens = ('\n' + '-' * 50 + '\n').join(self.ScreenQueue[-3:])
        return Screens + '\n' + i18n.ScreenNoMatchTarget


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
        Refresh=True
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


class API(object):
    def __init__(self, ConnectMode: int):

        self._ConnectMode = ConnectMode

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

        if self._ConnectMode == ConnectMode.Telnet:
            Log.showValue(Log.Level.INFO, [
                i18n.Connect,
                i18n.PTT,
            ],
                i18n.ConnectMode_Telnet
            )
        else:
            Log.showValue(Log.Level.INFO, [
                i18n.Connect,
                i18n.PTT,
            ],
                i18n.ConnectMode_WebSocket
            )

        for _ in range(2):

            try:

                if self._ConnectMode == ConnectMode.Telnet:
                    self._Core = telnetlib.Telnet(Config.Host, Config.Port)
                else:
                    self._Core = asyncio.get_event_loop().run_until_complete(
                        websockets.connect(
                            'wss://ws.ptt.cc/bbs/',
                            origin='https://www.ptt.cc'
                        ))

                ConnectSuccess = True
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)
            # except:
                Log.showValue(Log.Level.INFO, [
                    i18n.Connect,
                    i18n.PTT,
                ],
                    i18n.Fail
                )
                _wait()
                continue

            break

        if not ConnectSuccess:
            raise ConnectError()

    def send(
        self,
        Msg: str,
        TargetList: list,
        ScreenTimeout: int = 0,
        Refresh: bool = True
    ) -> int:

        if not all(isinstance(T, TargetUnit) for T in TargetList):
            raise ValueError('Item of TargetList must be TargetUnit')

        if ScreenTimeout == 0:
            CurrentScreenTimeout = Config.ScreenTimeOut
        else:
            CurrentScreenTimeout = ScreenTimeout

        self._ReceiveDataQueue = []
        BreakDetectAfterSend = False
        BreakIndex = -1
        while True:

            if Refresh and not Msg.endswith(Command.Refresh):
                Msg = Msg + Command.Refresh
            try:
                Msg = Msg.encode('big5-uao', 'ignore')

            except AttributeError:
                pass
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)
                Msg = Msg.encode('big5', 'ignore')

            Log.showValue(Log.Level.DEBUG, [
                i18n.SendMsg
            ],
                Msg
            )

            if self._ConnectMode == ConnectMode.Telnet:
                self._Core.read_very_eager()
                self._Core.write(Msg)
            else:
                asyncio.get_event_loop().run_until_complete(
                    self._Core.send(Msg)
                )

            if BreakDetectAfterSend:
                return BreakIndex

            Msg = ''
            CycleTime = 0
            CycleWait = 0
            ReceiveData = []

            StartTime = time.time()
            MidTime = time.time()
            while MidTime - StartTime < CurrentScreenTimeout:
                if self._ConnectMode == ConnectMode.Telnet:
                    try:
                        ReceiveDataTemp = self._Core.read_very_eager()
                    except EOFError:
                        return -1
                else:
                    try:
                        asyncio.get_event_loop().run_until_complete(
                            WebsocketReceiver(self._Core, CurrentScreenTimeout)
                        )
                        ReceiveDataTemp = _WSRecvData

                    except websockets.exceptions.ConnectionClosed:
                        return -1
                    except asyncio.TimeoutError:
                        return -1

                ReceiveDataTemp = ReceiveDataTemp.decode(
                    'big5-uao', errors='ignore'
                )

                # ReceiveDataTemp = self._cleanScreen(ReceiveDataTemp)
                ReceiveData.append(ReceiveDataTemp)
                Screen = ''.join(ReceiveData)
                Screen = self._cleanScreen(Screen)

                FindTarget = False
                for Target in TargetList:

                    Condition = Target.isMatch(Screen)
                    if Condition:
                        if len(Screen) > 0:
                            Screens.show(Screen)
                            self._ReceiveDataQueue.append(Screen)
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
                        if Target.isRefresh() and \
                           not Msg.endswith(Command.Refresh):
                            Msg = Msg + Command.Refresh

                        if Target.isBreakAfterSend():
                            BreakIndex = TargetList.index(Target)
                            BreakDetectAfterSend = True
                        break

                if FindTarget:
                    break
                if len(Screen) > 0:
                    Screens.show(Screen)
                    self._ReceiveDataQueue.append(Screen)

                MidTime = time.time()

            if not FindTarget:
                raise NoMatchTargetError(self._ReceiveDataQueue)
        raise NoMatchTargetError(self._ReceiveDataQueue)

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
        return self._ReceiveDataQueue
