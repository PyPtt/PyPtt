import sys
import re
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


class Target(object):
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
        '瀏覽',
        '頁',
        '離開'
    ]

    PostEnd = [
        '瀏覽',
        '頁 (100%)',
        '離開'
    ]

    PostIP_New = [
        '※ 發信站: 批踢踢實業坊(ptt.cc), 來自:'
    ]

    PostIP_Old = [
        '◆ From:'
    ]

    Edit = [
        '※ 編輯',
        '來自:'
    ]

    Vote_Type1 = [
        '◆ 投票名稱',
        '◆ 投票中止於',
        '◆ 票選題目描述'
    ]

    Vote_Type2 = [
        '投票名稱',
        '◆ 預知投票紀事',
    ]


def show(ScreenQueue, FunctionName=None):
    if Config.LogLevel != Log.Level.TRACE:
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


def isMatch(Screen: str, Target):

    if isinstance(Target, str):
        return Target in Screen
    if isinstance(Target, list):
        for T in Target:
            if T not in Screen:
                return False
        return True


class Screen(object):
    # https://github.com/RobTillaart/Arduino/blob/master/libraries/VT100/VT100.h

    Control = '\x1B'
    CleanScreen = '\x1B[2J'
    HOME = '\x1B[H'

    XY = re.compile('\x1B\[(\d+);(\d+)H')

    def __init__(self, OriScreen):
        self._y = 0
        self._x = 0
        self._OriScreen = OriScreen
        self._screen = [[' '] * 80] * 24

    def _writeChar(self, char):
        print(f'({self._y}, {self._x})')
        self._screen[self._y][self._x] = str(char)
        self._x += 1
        if self._x >= 80:
            self._y += 1
            self._x = 0

    def _getScreen(self):
        Lines = []
        for LineList in self._screen:
            Line = ''.join(LineList)
            Lines.append(Line)
        return '\n'.join(Lines)

    def _show(self):
        print(self._getScreen())
        print('= ' * 50)

    def process(self):

        print(self._OriScreen)

        while len(self._OriScreen) > 1:
            if self._OriScreen.startswith(self.Control):
                result = self.XY.search(self._OriScreen)
                if result is not None:
                    XYResult = result.group(0)
                    print(XYResult)

                    # if self._OriScreen.startswith(XYResult):

                if self._OriScreen.startswith(self.CleanScreen):
                    self._screen = [[' '] * 80] * 24
                    self._y = 0
                    self._x = 0
                    self._OriScreen = self._OriScreen[len(self.CleanScreen):]
                elif self._OriScreen.startswith(self.HOME):
                    self._x = 0
                    self._OriScreen = self._OriScreen[len(self.HOME):]
                else:
                    pass
            else:
                char = self._OriScreen[0]
                self._OriScreen = self._OriScreen[1:]
                self._writeChar(char)
            
            print(len(self._OriScreen))
            print(self._OriScreen)
            # self._show()
        return self._getScreen()