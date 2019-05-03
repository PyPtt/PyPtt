
import sys
import time
import telnetlib
import re
import traceback
from uao import register_uao
register_uao()

try:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import Exceptions
    from . import Log
except:
    import DataType
    import Config
    import Util
    import i18n
    import Exceptions
    import Log


def _showScreen(ScreenQueue, FunctionName=None):
    if Config.LogLevel != Log.Level.DEBUG:
        return
    
    if isinstance(ScreenQueue, list):
        for Screen in ScreenQueue:
            print('-' * 50)
            try:
                print(Screen.encode(
                    sys.stdin.encoding, "replace").decode(
                        sys.stdin.encoding))
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

    # \x1b\x4fA (上, 下右左 BCD)
    Up = '\x1b\x4fA'
    Down = '\x1b\x4fB'
    Right = '\x1b\x4fC'
    Left = '\x1b\x4fD'
    GoMainMenu = Left * 5


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
        Screens = ('-' * 50 + '\n').join(self.ScreenQueue)
        return Screens + '\n' + i18n.ScreenNoMatchTarget


class TargetUnit(object):
    def __init__(self,
                 DisplayMsg,
                 DetectTarget: str,
                 Response=' ',
                 BreakDetect=False):

        self._DisplayMsg = DisplayMsg
        self._DetectTarget = DetectTarget
        self._Response = Response
        self._BreakDetect = BreakDetect

    def isMatch(self, Screen: str):
        if self._DetectTarget in Screen:
            return True
        return False

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

    def getErrorCode(self):
        return self._ErrCode

    def getLogLevel(self):
        return self._LogLevel


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

            if self._ConnectMode == ConnectMode.Telnet:
                try:
                    self._Connect = telnetlib.Telnet(Config.Host, Config.Port)
                    ConnectSuccess = True
                except:
                    Log.showValue(Log.Level.INFO, [
                        i18n.Connect,
                        i18n.PTT,
                        ],
                        i18n.Fail
                    )
                    _wait()
                    continue
                break
            elif self._ConnectMode == DataType.ConnectionMode.WebSocket:
                # Do something

                break
        
        if not ConnectSuccess:
            raise ConnectError()

    def send(self, Msg: str, TargetList: list):

        if not Msg.endswith(Command.Refresh):
            Msg = Msg + Command.Refresh

        if not all(isinstance(T, TargetUnit) for T in TargetList):
            raise Exceptions.ParameterError(
                'Item of TargetList must be TargetUnit')

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
                Msg)

            if self._ConnectMode == ConnectMode.Telnet:
                self._Connect.read_very_eager()
                self._Connect.write(Msg)
                # raise ConnectError()
            else:
                pass
            Msg = ' '
            CycleTime = 0
            CycleWait = 0.1
            ReceiveData = []

            while CycleTime * CycleWait < Config.ScreenTimeOut:
                time.sleep(CycleWait)
                CycleTime += 1

                ReceiveDataTemp = self._Connect.read_very_eager()
                ReceiveDataTemp = ReceiveDataTemp.decode(
                    'utf-8', errors='ignore')
                ReceiveDataTemp = self._cleanScreen(ReceiveDataTemp)
                
                ReceiveData.append(ReceiveDataTemp)
                Screen = ''.join(ReceiveData)

                if len(Screen) > 0:
                    self._ReceiveDataQueue.append(Screen)

                FindTarget = False
                for i in range(len(TargetList)):
                    Target = TargetList[i]

                    if Target.getDetectTarget() in Screen:
                        FindTarget = True

                        Log.showValue(Log.Level.INFO, [
                            i18n.PTT,
                            i18n.Msg
                        ],
                            Target.getDisplayMsg()
                        )

                        if Target.isBreak():
                            return i

                        Msg = Target.getResponse(Screen)
                        break

                if FindTarget:
                    break
            if not FindTarget:
                raise NoMatchTargetError(self._ReceiveDataQueue)
        raise NoMatchTargetError(self._ReceiveDataQueue)

    def _cleanScreen(self, screen, NoColor=True):
        if not screen:
            return screen
        # http://asf.atmel.com/docs/latest/uc3l/html/group__group__avr32__utils__print__funcs.html#ga024c3e2852fe509450ebc363df52ae73
        
        PreNewLineMark = -1
        PTTLibraryNewLineMark = '==PTTLibraryNewLineMark=='
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
