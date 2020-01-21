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


def setBoardTitle(
        api,
        Board: str,
        NewTitle: str):

    # Log.showValue(
    #     api.Config,
    #     Log.Level.INFO,
    #     [
    #         i18n.PTT,
    #         i18n.Msg
    #     ],
    #     i18n.MarkPost
    # )

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('qs')
    CmdList.append(Board)
    CmdList.append(Command.Enter)
    CmdList.append(Command.Ctrl_C * 2)
    CmdList.append(Command.Space)
    CmdList.append('I')
    CmdList.append(Command.Ctrl_P)
    CmdList.append('b')
    CmdList.append(Command.Enter)
    CmdList.append(Command.Backspace * 31)
    CmdList.append(NewTitle)
    CmdList.append(Command.Enter * 2)
    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.NewSettingsHaveBeenSaved,
            '◆ 已儲存新設定',
            BreakDetect=True,
        ),
        ConnectCore.TargetUnit(
            i18n.NoChanges,
            '◆ 未改變任何設定',
            BreakDetect=True,
        ),
    ]

    api._ConnectCore.send(
        Cmd,
        TargetList,
        ScreenTimeout=api.Config.ScreenLongTimeOut
    )
