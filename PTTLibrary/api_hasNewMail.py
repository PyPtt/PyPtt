import re
try:
    from . import DataType
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Screens
    from . import Exceptions
    from . import Command
    from . import CheckValue
except ModuleNotFoundError:
    import DataType
    import i18n
    import ConnectCore
    import Log
    import Screens
    import Exceptions
    import Command
    import CheckValue


def hasNewMail(api):

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
    CmdList.append('M')
    CmdList.append(Command.Enter)
    CmdList.append('R')
    CmdList.append(Command.Enter)
    CmdList.append('1')
    CmdList.append(Command.Enter)
    CmdList.append('$')
    Cmd = ''.join(CmdList)

    #
    TargetList = [
        ConnectCore.TargetUnit(
            i18n.MailBox,
            Screens.Target.InMailBox,
            BreakDetect=True,
            LogLevel=Log.Level.DEBUG
        )
    ]

    api._ConnectCore.send(
        Cmd,
        TargetList,
        ScreenTimeout=api.Config.ScreenLongTimeOut
    )

    OriScreen = api._ConnectCore.getScreenQueue()[-1]

    pattern = re.findall('[\s]+[\d]+ (\+)[\s]+', OriScreen)
    return len(pattern)
