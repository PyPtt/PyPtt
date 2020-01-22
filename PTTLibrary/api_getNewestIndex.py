import re
import time
try:
    from . import DataType
    from . import Util
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Screens
    from . import Exceptions
    from . import Command
    from . import CheckValue
except ModuleNotFoundError:
    import DataType
    import Util
    import i18n
    import ConnectCore
    import Log
    import Screens
    import Exceptions
    import Command
    import CheckValue


def getNewestIndex(
        api,
        IndexType: int,
        Board: str = None,
        # BBS
        SearchType: int = 0,
        SearchCondition: str = None):

    if IndexType == DataType.IndexType.BBS:

        api._checkBoard(Board)

        CheckValue.check(
            api.Config, int, 'SearchType', SearchType,
            Class=DataType.PostSearchType)
        if SearchCondition is not None:
            CheckValue.check(
                api.Config, str,
                'SearchCondition', SearchCondition)
        CheckValue.check(api.Config, int, 'SearchType', SearchType)

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('qs')
        CmdList.append(Board)
        CmdList.append(Command.Enter)
        CmdList.append(Command.Ctrl_C * 2)
        CmdList.append(Command.Space)

        if SearchCondition is not None:
            if SearchType == DataType.PostSearchType.Keyword:
                CmdList.append('/')
            elif SearchType == DataType.PostSearchType.Author:
                CmdList.append('a')
            elif SearchType == DataType.PostSearchType.Push:
                CmdList.append('Z')
            elif SearchType == DataType.PostSearchType.Mark:
                CmdList.append('G')
            elif SearchType == DataType.PostSearchType.Money:
                CmdList.append('A')

            CmdList.append(SearchCondition)
            CmdList.append(Command.Enter)

        CmdList.append('1')
        CmdList.append(Command.Enter)
        CmdList.append('$')

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.NoPost,
                '沒有文章...',
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                i18n.Success,
                Screens.Target.InBoard,
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                i18n.Success,
                Screens.Target.InBoardWithCursor,
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                i18n.NoSuchBoard,
                Screens.Target.MainMenu_Exiting,
                Exceptions=Exceptions.NoSuchBoard(api.Config, Board)
            ),
        ]
        index = api._ConnectCore.send(Cmd, TargetList)
        if index < 0:
            # OriScreen = api._ConnectCore.getScreenQueue()[-1]
            # print(OriScreen)
            raise Exceptions.NoSuchBoard(api.Config, Board)

        if index == 0:
            return 0

        LastScreen = api._ConnectCore.getScreenQueue()[-1]
        AllIndex = re.findall(r'\d+ ', LastScreen)

        if len(AllIndex) == 0:
            print(LastScreen)
            raise Exceptions.UnknowError(i18n.UnknowError)

        AllIndex = list(map(int, AllIndex))
        AllIndex.sort(reverse=True)

        MaxCheckRange = 6
        NewestIndex = 0
        for IndexTemp in AllIndex:
            Continue = True
            if IndexTemp > MaxCheckRange:
                CheckRange = MaxCheckRange
            else:
                CheckRange = IndexTemp
            for i in range(1, CheckRange):
                if str(IndexTemp - i) not in LastScreen:
                    Continue = False
                    break
            if Continue:
                Log.showValue(
                    api.Config,
                    Log.Level.DEBUG,
                    i18n.FindNewestIndex,
                    IndexTemp
                )
                NewestIndex = IndexTemp
                break

        if NewestIndex == 0:
            Screens.show(api.Config, api._ConnectCore.getScreenQueue())
            raise Exceptions.UnknowError(i18n.UnknowError)

    elif DataType.IndexType.Web:
        # web
        _NewestIndex = None
        NewestIndex = 0
        _url = 'https://www.ptt.cc/bbs/'
        url = _url + Board
        r = requests.get(url, cookies={'over18': '1'})

        if r.status_code != requests.codes.ok:
            raise Exceptions.NoSuchBoard(api.Config, Board)
        soup = BeautifulSoup(r.text, 'html.parser')

        for index, data in enumerate(soup.select('div.btn-group.btn-group-paging a')):
            text = data.text
            herf = data.get('href')
            if '上頁' in text:
                _NewestIndex = herf.split('index')[1].split('.')[0]
                # print("_NewestIndex: " + _NewestIndex)
                _NewestIndex = int(_NewestIndex)

        if _NewestIndex is None:
            raise Exceptions.UnknowError('')
        NewestIndex = (_NewestIndex) + 1
    return NewestIndex
