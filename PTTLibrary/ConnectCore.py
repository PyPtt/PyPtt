
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
except ModuleNotFoundError:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import Log


def _showScreen(ScreenQueue, FunctionName=None):
    if Config.LogLevel != Log.Level.DEBUG:
        return

    if isinstance(ScreenQueue, list):
        for Screen in ScreenQueue:
            print('-' * 50)
            try:
                print(Screen.encode(
                    sys.stdin.encoding, "replace").decode(
                        sys.stdin.encoding
                    )
                )
            except Exception:
                print(Screen.encode('utf-8', "replace").decode('utf-8'))
    else:
        print('-' * 50)
        try:
            print(ScreenQueue.encode(
                sys.stdin.encoding, "replace").decode(
                    sys.stdin.encoding))
        except Exception:
            print(ScreenQueue.encode('utf-8', "replace").decode('utf-8'))

        print('len:' + str(len(ScreenQueue)))
    if FunctionName is not None:
        print('錯誤在 ' + FunctionName + ' 函式發生')
    print('-' * 50)


class Command(object):
    Enter = '\r'
    Refresh = '\x0C'
    Up = '\x1b\x4fA'
    Down = '\x1b\x4fB'
    Right = '\x1b\x4fC'
    Left = '\x1b\x4fD'
    GoMainMenu = Left * 5


class ScreenTarget(object):
    MainMenu = [
        '人, 我是',
        '[呼叫器]',
    ]


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


class LoginError(Exception):
    def __init__(self):
        self.message = [i18n.LoginFail]

    def __str__(self):

        if Config.Language == i18n.Language.Chinese:
            return ''.join(self.message)
        return ' '.join(self.message)


class NoMatchTargetError(Exception):
    def __init__(self, ScreenQueue: list):
        self.ScreenQueue = ScreenQueue

    def __str__(self):
        Screens = ('\n' + '-' * 50 + '\n').join(self.ScreenQueue)
        return Screens + '\n' + i18n.ScreenNoMatchTarget


class TargetUnit(object):
    def __init__(self,
                 DisplayMsg,
                 DetectTarget,
                 Response=' ',
                 BreakDetect=False):

        self._DisplayMsg = DisplayMsg
        self._DetectTarget = DetectTarget
        self._Response = Response
        self._BreakDetect = BreakDetect

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

    def getResponse(self, Screen: str):
        if callable(self._Response):
            return self._Response(Screen)
        return self._Response

    def isBreak(self):
        return self._BreakDetect


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

    def send(self, Msg: str, TargetList: list) ->int:

        if not Msg.endswith(Command.Refresh):
            Msg = Msg + Command.Refresh

        if not all(isinstance(T, TargetUnit) for T in TargetList):
            raise ValueError('Item of TargetList must be TargetUnit')

        self._ReceiveDataQueue = []

        for _ in range(len(TargetList) + 1):

            try:
                Msg = Msg.encode('big5-uao', 'replace')
            except AttributeError:
                pass
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                print(e)
                Msg = Msg.encode('big5', 'replace')

            Log.showValue(Log.Level.DEBUG, [
                    i18n.SendMsg
                ],
                Msg
            )

            if self._ConnectMode == ConnectMode.Telnet:
                self._Core.read_very_eager()
                self._Core.write(Msg)
                # raise ConnectError()
            else:
                asyncio.get_event_loop().run_until_complete(
                    self._Core.send(Msg)
                )
            Msg = b' '
            CycleTime = 0
            CycleWait = 0
            ReceiveDataUTF8 = []
            ReceiveDataBIG5UAO = []

            StartTime = time.time()
            MidTime = time.time()
            while MidTime - StartTime < Config.ScreenTimeOut:

                if self._ConnectMode == ConnectMode.Telnet:
                    try:
                        ReceiveDataTemp = self._Core.read_very_eager()
                    except EOFError:
                        return -1
                else:
                    try:
                        ReceiveDataTemp = (
                            asyncio.get_event_loop().run_until_complete(
                                self._Core.recv()
                            )
                        )
                    except websockets.exceptions.ConnectionClosed:
                        return -1

                MixingDetect = False
                MixingDetectEncoding = None
                try:
                    ReceiveDataTempUTF8 = ReceiveDataTemp.decode(
                        'utf-8'
                    )
                except UnicodeDecodeError:
                    # 可能有 UTF8 與 Big5UAO的資料出現
                    MixingDetect = True
                    ReceiveDataTempBIG5UAO = ReceiveDataTemp.decode(
                        'big5-uao', errors='ignore'
                    )
                    ReceiveDataTempBIG5UAO = self._cleanScreen(
                        ReceiveDataTempBIG5UAO
                    )
                    ReceiveDataBIG5UAO.append(ReceiveDataTempBIG5UAO)
                    ScreenBIG5UAO = ''.join(ReceiveDataBIG5UAO)

                    ReceiveDataTempUTF8 = ReceiveDataTemp.decode(
                        'utf-8', errors='ignore'
                    )

                ReceiveDataTempUTF8 = self._cleanScreen(ReceiveDataTempUTF8)
                ReceiveDataUTF8.append(ReceiveDataTempUTF8)
                ScreenUTF8 = ''.join(ReceiveDataUTF8)

                # _showScreen(ScreenUTF8)

                FindTarget = False
                for Target in TargetList:

                    Condition = Target.isMatch(ScreenUTF8)
                    if MixingDetect and (not Condition):
                        Condition = Target.isMatch(ScreenBIG5UAO)
                        MixingDetectEncoding = 'BIG5UAO'
                        if len(ScreenBIG5UAO) > 0:
                            self._ReceiveDataQueue.append(ScreenBIG5UAO)

                    else:
                        MixingDetectEncoding = 'UTF8'
                        if len(ScreenUTF8) > 0:
                            self._ReceiveDataQueue.append(ScreenUTF8)

                    if Condition:
                        FindTarget = True

                        Log.showValue(Log.Level.INFO, [
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

                        if MixingDetectEncoding == 'UTF8':
                            Msg = Target.getResponse(ScreenUTF8)
                        else:
                            Msg = Target.getResponse(ScreenBIG5UAO)
                        break

                if FindTarget:
                    break
                if len(ScreenUTF8) > 0:
                    self._ReceiveDataQueue.append(ScreenUTF8)
                
                MidTime = time.time()
                
            if not FindTarget:
                raise NoMatchTargetError(self._ReceiveDataQueue)
        raise NoMatchTargetError(self._ReceiveDataQueue)

    def close(self):
        self._Core.close()

    def _cleanScreen(self, screen: str, NoColor=True) ->str:
        if not screen:
            return screen
        # http://asf.atmel.com/docs/latest/uc3l/html/group__group__avr32__utils__print__funcs.html#ga024c3e2852fe509450ebc363df52ae73

        PreNewLineMark = -1
        PTTLibraryNewLineMark = '==PTTLibNewLineMark=='
        for NewLineMark in range(1, 25):
            for Type in range(1, 26):
                Target = '[' + str(NewLineMark) + ';' + str(Type) + 'H'
                if Target in screen:

                    if PreNewLineMark == -1:
                        NewLineCount = screen[:screen.find(Target)].count('\n')

                        NewLine = NewLineMark - NewLineCount - 1
                        # if ShowTarget in screen:
                        #     print('NewLineMark', NewLineMark)
                        #     print('NewLineCount', NewLineCount)
                        #     print('NewLine', NewLine)
                        if NewLine < 1:
                            NewLine = 1
                        screen = screen.replace(Target,
                                                PTTLibraryNewLineMark*NewLine)
                    else:
                        NewLineMarkCount = NewLineMark - PreNewLineMark
                        NewLineCount = screen[
                            screen.rfind(PTTLibraryNewLineMark):
                            screen.find(Target)].count('\n')

                        NewLine = NewLineMarkCount - NewLineCount
                        # if ShowTarget in screen:
                        #     print('NewLineMark', NewLineMark)
                        #     print('NewLineCount', NewLineCount)
                        #     print('NewLine', NewLine)

                        if NewLine < 1:
                            NewLine = 1

                        screen = screen.replace(Target,
                                                PTTLibraryNewLineMark*NewLine)

                    PreNewLineMark = NewLineMark

        screen = screen.replace(PTTLibraryNewLineMark, '\n')
        # if ShowTarget in screen:
        #     self.Log('----------------------')
        #     self.Log(str(screen))
        #     self.Log('----------------------')
        # screen = screen.replace('[2J    ', '')
        screen = screen.replace('[2J', '')

        if NoColor:
            screen = re.sub('\[[\d+;]*[mH]', '', screen)

        screen = re.sub(r'[\r]', '', screen)
        screen = re.sub(r'[\x00-\x08]', '', screen)
        screen = re.sub(r'[\x0b\x0c]', '', screen)
        screen = re.sub(r'[\x0e-\x1f]', '', screen)
        screen = re.sub(r'[\x7f-\xff]', '', screen)
        # self.Log('after: ' + str(screen))
        return screen

    def getScreenQueue(self) ->list:
        return self._ReceiveDataQueue
