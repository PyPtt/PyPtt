try:
    from . import DataType
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Screens
    from . import Command
    from . import CheckValue
except ModuleNotFoundError:
    import DataType
    import i18n
    import ConnectCore
    import Log
    import Screens
    import Command
    import CheckValue


def markPost(
        api,
        inputMarkType: int,
        Board: str,
        PostAID: str,
        PostIndex: int,
        SearchType: int,
        SearchCondition: str):

    Log.showValue(
        api.Config,
        Log.Level.INFO,
        [
            i18n.PTT,
            i18n.Msg
        ],
        i18n.MarkPost
    )

    CheckValue.check(api.Config, int, 'MarkType', inputMarkType,
                     Class=DataType.MarkType)
    CheckValue.check(api.Config, str, 'Board', Board)
    if PostAID is not None:
        CheckValue.check(api.Config, str, 'PostAID', PostAID)
    CheckValue.check(api.Config, int, 'PostIndex', PostIndex)
    CheckValue.check(api.Config, int, 'SearchType', SearchType,
                     Class=DataType.PostSearchType)
    if SearchCondition is not None:
        CheckValue.check(api.Config, str,
                         'SearchCondition', SearchCondition)

    if len(Board) == 0:
        raise ValueError(Log.merge([
            i18n.Board,
            i18n.ErrorParameter,
            Board
        ]))

    if PostIndex != 0 and isinstance(PostAID, str):
        raise ValueError(Log.merge([
            'PostIndex',
            'PostAID',
            i18n.ErrorParameter,
            i18n.BothInput
        ]))

    if PostIndex == 0 and PostAID is None:
        raise ValueError(Log.merge([
            'PostIndex',
            'PostAID',
            i18n.ErrorParameter
        ]))

    if SearchCondition is not None and SearchType == 0:
        raise ValueError(Log.merge([
            'SearchType',
            i18n.ErrorParameter,
        ]))

    if SearchType == DataType.PostSearchType.Push:
        try:
            S = int(SearchCondition)
        except ValueError:
            raise ValueError(Log.merge([
                'SearchCondition',
                i18n.ErrorParameter,
            ]))

        if not (-100 <= S <= 110):
            raise ValueError(Log.merge([
                'SearchCondition',
                i18n.ErrorParameter,
            ]))

    if PostAID is not None and SearchCondition is not None:
        raise ValueError(Log.merge([
            'PostAID',
            'SearchCondition',
            i18n.ErrorParameter,
            i18n.BothInput,
        ]))

    if PostIndex != 0:
        NewestIndex = api._get_newest_index(
            DataType.IndexType.BBS,
            board=Board,
            search_type=SearchType,
            search_condition=SearchCondition
        )
        CheckValue.checkIndex(api.Config, 'PostIndex',
                              PostIndex, MaxValue=NewestIndex)

    if inputMarkType == DataType.MarkType.Unconfirmed:
        # 批踢踢兔沒有待證文章功能 QQ
        if api.Config.Host == DataType.Host.PTT2:
            raise Exceptions.HostNotSupport(Util.getCurrentFuncName())

    api._check_board(
        Board,
        check_moderator=True
    )

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('qs')
    CmdList.append(Board)
    CmdList.append(Command.Enter)

    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵',
            Response=' ',
        ),
        ConnectCore.TargetUnit(
            [
                '動畫播放中',
            ],
            '互動式動畫播放中',
            Response=Command.Ctrl_C,
            LogLevel=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                '進板成功',
            ],
            Screens.Target.InBoard,
            BreakDetect=True,
            LogLevel=Log.Level.DEBUG
        ),
    ]

    index = api._ConnectCore.send(Cmd, TargetList)

    CmdList = []
    if PostAID is not None:
        CmdList.append('#' + PostAID)

    elif PostIndex != 0:
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

        CmdList.append(str(PostIndex))

    CmdList.append(Command.Enter)

    if inputMarkType == DataType.MarkType.S:
        CmdList.append('L')
    elif inputMarkType == DataType.MarkType.D:
        CmdList.append('t')
    elif inputMarkType == DataType.MarkType.DeleteD:
        CmdList.append(Command.Ctrl_D)
    elif inputMarkType == DataType.MarkType.M:
        CmdList.append('m')
    elif inputMarkType == DataType.MarkType.Unconfirmed:
        CmdList.append(Command.Ctrl_E + 'S')

    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            [i18n.DelAllMarkPost],
            '刪除所有標記',
            Response='y' + Command.Enter,
            LogLevel=Log.Level.INFO
        ),
        ConnectCore.TargetUnit(
            [
                i18n.Mark,
                i18n.Success,
            ],
            Screens.Target.InBoard,
            BreakDetect=True,
            LogLevel=Log.Level.INFO
        ),
    ]

    index = api._ConnectCore.send(Cmd, TargetList)
