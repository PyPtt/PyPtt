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


def VT100(OriScreen: str, NoColor: bool=True):

    result = OriScreen

    if NoColor:
        result = re.sub('\x1B\[[\d+;]*m', '', result)

    result = re.sub(r'[\x1B]', '=PTT=', result)

    # result = '\n'.join(
    #     [x.rstrip() for x in result.split('\n')]
    # )
    if '=PTT=[H' in result:
        result = result[result.find('=PTT=[H') + len('=PTT=[H'):]
    if '=PTT=[2J' in result:
        result = result[result.find('=PTT=[2J') + len('=PTT=[2J'):]
    #
    ResultList = re.findall(f'=PTT=\[(\d+);(\d+)H', result)
    for (Line, Space) in ResultList:
        print(Line, Space)
        CurrentLine = result[:result.find(f'[{Line};{Space}H')].count('\n') + 1
        print(CurrentLine)
    print(result)
    print('=' * 50)
    return result
