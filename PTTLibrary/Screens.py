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
        '───────┘',
    ]

    InBoard = [
        '看板資訊/設定',
        '文章選讀',
        '相關主題'
    ]

    InBoardWithCursor = [
        '【',
        '看板資訊/設定',
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

    InWaterBallList = [
        '瀏覽',
        '頁',
        '說明',
    ]

    WaterBallListEnd = [
        '瀏覽',
        '頁 (100%)',
        '說明'
    ]

    PostIP_New = [
        '※ 發信站: 批踢踢實業坊(ptt.cc), 來自:'
    ]

    PostIP_Old = [
        '◆ From:'
    ]

    Edit = [
        '※ 編輯'
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

    AnyKey = '任意鍵'

    InTalk = [
        '【聊天說話】',
        '線上使用者列表',
        '查詢網友',
        '顯示上幾次熱訊'
    ]

    InUserList = [
        '休閒聊天',
        '聊天/寫信',
        '說明',
    ]

    InMailBox = [
        '【郵件選單】',
        '鴻雁往返'
    ]

    PostNoContent = [
        '◆ 此文章無內容',
        AnyKey
    ]

    InBoardList = [
        '【看板列表】',
        '選擇看板',
        '已讀/未讀',
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


def VT100(OriScreen: str, NoColor: bool = True):

    result = OriScreen

    if NoColor:
        result = re.sub('\x1B\[[\d+;]*m', '', result)

    result = re.sub(r'[\x1B]', '=PTT=', result)

    # result = '\n'.join(
    #     [x.rstrip() for x in result.split('\n')]
    # )

    while '=PTT=[H' in result:
        result = result[result.find('=PTT=[H') + len('=PTT=[H'):]
    while '=PTT=[2J' in result:
        result = result[result.find('=PTT=[2J') + len('=PTT=[2J'):]

    PatternResult = re.compile('=PTT=\[(\d+);(\d+)H$').search(result)
    LastPosition = None
    if PatternResult is not None:
        # print(f'Before [{PatternResult.group(0)}]')
        LastPosition = PatternResult.group(0)

    # 進入 PTT 時，有時候會連分類看版一起傳過來然後再用主功能表畫面直接繪製畫面
    # 沒有[H 或者 [2J 導致後面的繪製行數錯誤

    if '=PTT=[1;3H主功能表' in result:
        result = result[result.find('=PTT=[1;3H主功能表') + len('=PTT=[1;3H主功能表'):]

    # if '=PTT=[1;' in result:
    #     if LastPosition is None:
    #         result = result[result.rfind('=PTT=[1;'):]
    #     elif not LastPosition.startswith('=PTT=[1;'):
    #         result = result[result.rfind('=PTT=[1;'):]

    # print('-'*50)
    # print(result)
    ResultList = re.findall('=PTT=\[(\d+);(\d+)H', result)
    for (Line, Space) in ResultList:
        # print(f'>{Line}={Space}<')
        Line = int(Line)
        Space = int(Space)
        CurrentLine = result[
            :result.find(
                f'[{Line};{Space}H'
            )
        ].count('\n') + 1
        CurrentSpace = result[
            :result.find(
                f'=PTT=[{Line};{Space}H'
            )
        ]
        CurrentSpace = CurrentSpace[
            CurrentSpace.rfind('\n') + 1:
        ]

        CurrentSpace = len(CurrentSpace)
        if CurrentLine > Line:
            pass
            # if LastPosition is None:
            #     pass
            # elif LastPosition != f'=PTT=[{Line};{Space}H':
            #     print(f'CurrentLine [{CurrentLine}]')
            #     print(f'Line [{Line}]')
            #     print('Clear !!!')
            # print(f'=PTT=[{Line};{Space}H')
        elif CurrentLine == Line:
            if CurrentSpace > Space:
                result = result.replace(
                    f'=PTT=[{Line};{Space}H',
                    (Line - CurrentLine) * '\n' + Space * ' '
                )
            else:
                result = result.replace(
                    f'=PTT=[{Line};{Space}H',
                    (Line - CurrentLine) * '\n' + (Space - CurrentSpace) * ' '
                )
        else:
            result = result.replace(
                f'=PTT=[{Line};{Space}H',
                (Line - CurrentLine) * '\n' + Space * ' '
            )

    while '=PTT=[K' in result:
        Target = result[result.find('=PTT=[K'):]
        index1 = Target.find('\n')
        index2 = Target.find('=PTT=')
        if index2 == 0:
            index = index1
        else:
            index = min(index1, index2)
        Target = Target[:index]
        result = result.replace(Target, '')

    if LastPosition is not None:
        result = result.replace(LastPosition, '')

    return result
