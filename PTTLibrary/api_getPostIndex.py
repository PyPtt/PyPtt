
try:
    from . import Util
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Screens
    from . import Exceptions
    from . import Command
    from . import CheckValue
except ModuleNotFoundError:
    import Util
    import i18n
    import ConnectCore
    import Log
    import Screens
    import Exceptions
    import Command
    import CheckValue


def getPostIndex(
        api,
        Board,
        AID):

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('qs')
    CmdList.append(Board)
    CmdList.append(Command.Enter)
    CmdList.append(Command.Ctrl_C * 2)
    CmdList.append(Command.Space)

    CmdList.append('#')
    CmdList.append(AID)
    CmdList.append(Command.Enter)

    Cmd = ''.join(CmdList)

    TargetList = []
    if AID is not None:
        NoSuchPost = i18n.NoSuchPost
        NoSuchPost = i18n.replace(NoSuchPost, Board, AID)
        TargetList.append(
            ConnectCore.TargetUnit(
                NoSuchPost,
                '找不到這個文章代碼',
                LogLevel=Log.Level.DEBUG,
                Exceptions=Exceptions.NoSuchPost(Board, AID)
            ),
        )
    else:
        NoSuchPost = i18n.NoSuchPost
        NoSuchPost = i18n.replace(NoSuchPost, Board, PostIndex)
        TargetList.append(
            ConnectCore.TargetUnit(
                NoSuchPost,
                '找不到這個文章代碼',
                LogLevel=Log.Level.DEBUG,
                Exceptions=Exceptions.NoSuchPost(Board, PostIndex)
            ),
        )

    TargetList.extend([
        # 此狀態下無法使用搜尋文章代碼(AID)功能
        ConnectCore.TargetUnit(
            i18n.CanNotUseSearchPostCodeF,
            '此狀態下無法使用搜尋文章代碼(AID)功能',
            Exceptions=Exceptions.CanNotUseSearchPostCode()
        ),
        ConnectCore.TargetUnit(
            i18n.NoPost,
            '沒有文章...',
            Exceptions=Exceptions.NoSuchPost(Board, AID)
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
            # BreakDetect=True,
        ),
    ])
    index = api._ConnectCore.send(
        Cmd,
        TargetList
    )
    OriScreen = api._ConnectCore.getScreenQueue()[-1]
    if index < 0:
        # print(OriScreen)
        raise Exceptions.NoSuchBoard(api.Config, Board)

    # if index == 5:
    #     print(OriScreen)
    #     raise Exceptions.NoSuchBoard(api.Config, Board)

    # print(index)
    # print(OriScreen)
    ScreenList = OriScreen.split('\n')

    line = [x for x in ScreenList if x.startswith(api._Cursor)]
    line = line[0]
    LastLine = ScreenList[ScreenList.index(line) - 1]
    # print(LastLine)
    # print(line)

    if '編號' in LastLine and '人氣:' in LastLine:
        Index = line[1:].strip()
        IndexFix = False
    else:
        Index = LastLine.strip()
        IndexFix = True
    while '  ' in Index:
        Index = Index.replace('  ', ' ')
    IndexList = Index.split(' ')
    Index = IndexList[0]
    if Index == '★':
        return 0
    Index = int(Index)
    if IndexFix:
        Index += 1
    # print(Index)
    return Index
