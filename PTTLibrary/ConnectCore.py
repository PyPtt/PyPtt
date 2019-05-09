
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
    Ctrl_C = '\x03'
    QueryPost = 'Q'
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

    QueryPost = [
        '請按任意鍵繼續',
        '這一篇文章值',
    ]

    InBoard = [
        '文章選讀',
        '進板畫面',
        '【板主'
    ]

    InPost = [
        '瀏覽 第',
        '目前顯示: 第',
        '離開'
    ]

    PostEnd = [
        '瀏覽 第',
        '(100%)  目前顯示: 第',
        '離開'
    ]

    IP = [
        '發信站: 批踢踢實業坊(ptt.cc), 來自:'
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
        Screens = ('\n' + '-' * 50 + '\n').join(self.ScreenQueue[-3:])
        return Screens + '\n' + i18n.ScreenNoMatchTarget


class TargetUnit(object):
    def __init__(self,
                 DisplayMsg,
                 DetectTarget,
                 Response='',
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

        if not all(isinstance(T, TargetUnit) for T in TargetList):
            raise ValueError('Item of TargetList must be TargetUnit')

        self._ReceiveDataQueue = []

        while True:

            if not Msg.endswith(Command.Refresh):
                Msg = Msg + Command.Refresh
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
            Msg = ''
            CycleTime = 0
            CycleWait = 0
            ReceiveData = []

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

                ReceiveDataTemp = ReceiveDataTemp.decode(
                    'big5-uao', errors='ignore'
                )

                ReceiveDataTemp = self._cleanScreen(ReceiveDataTemp)
                ReceiveData.append(ReceiveDataTemp)
                Screen = ''.join(ReceiveData)

                _showScreen(Screen)

                FindTarget = False
                for Target in TargetList:

                    Condition = Target.isMatch(Screen)
                    if Condition:
                        if len(Screen) > 0:
                            self._ReceiveDataQueue.append(Screen)

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

                        Msg = Target.getResponse(Screen)
                        break

                if FindTarget:
                    break
                if len(Screen) > 0:
                    self._ReceiveDataQueue.append(Screen)

                MidTime = time.time()

            if not FindTarget:
                raise NoMatchTargetError(self._ReceiveDataQueue)
        raise NoMatchTargetError(self._ReceiveDataQueue)

    def close(self):
        self._Core.close()

    def _cleanScreen(self, screen: str, NoColor=True) ->str:
        if not screen:
            return screen
        
        # Log.log(Log.Level.INFO, screen)
        # http://asf.atmel.com/docs/latest/uc3l/html/group__group__avr32__utils__print__funcs.html#ga024c3e2852fe509450ebc363df52ae73

        if NoColor:
            # print(screen)
            screen = re.sub('\[[\d+;]*[mH]', '', screen)
            screen = re.sub('\[[\d+;]*[mH]', '', screen)

            # pattern = re.compile('\[[\d]+;[\d]+m')
            # PatternResult = pattern.search(screen)
            # if PatternResult is not None:
            #     print(f'QQQQ {PatternResult.group(0)}')
            #     screen = screen.replace('[' + PatternResult.group(0), '')

        screen = re.sub(r'[\r]', '', screen)
        screen = re.sub(r'[\x00-\x08]', '', screen)
        screen = re.sub(r'[\x0b\x0c]', '', screen)
        screen = re.sub(r'[\x0e-\x1f]', '', screen)
        screen = re.sub(r'[\x7f-\xff]', '', screen)
        screen = screen.replace('[K\n', '')
        screen = screen.replace('[K', '')
        screen = screen.replace('[2J\n', '')
        screen = screen.replace('[2J', '')

        return screen

    def getScreenQueue(self) ->list:
        return self._ReceiveDataQueue
