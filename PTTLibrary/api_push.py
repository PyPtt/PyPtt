try:
    from . import DataType
    from . import Util
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Screens
    from . import Exceptions
    from . import Command
except ModuleNotFoundError:
    import DataType
    import Util
    import i18n
    import ConnectCore
    import Log
    import Screens
    import Exceptions
    import Command


def push(
        api,
        Board: str,
        PushType: int,
        PushContent: str,
        PostAID: str,
        PostIndex: int):

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('qs')
    CmdList.append(Board)
    CmdList.append(Command.Enter)
    CmdList.append(Command.Ctrl_C * 2)
    CmdList.append(Command.Space)

    if PostAID is not None:
        CmdList.append('#' + PostAID)
    elif PostIndex != 0:
        CmdList.append(str(PostIndex))
    CmdList.append(Command.Enter)
    CmdList.append(Command.Push)

    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.HasPushPermission,
            '您覺得這篇',
            LogLevel=Log.Level.DEBUG,
            BreakDetect=True
        ),
        ConnectCore.TargetUnit(
            i18n.OnlyArrow,
            '加註方式',
            LogLevel=Log.Level.DEBUG,
            BreakDetect=True
        ),
        ConnectCore.TargetUnit(
            i18n.NoFastPush,
            '禁止快速連續推文',
            LogLevel=Log.Level.INFO,
            BreakDetect=True,
            Exceptions=Exceptions.NoFastPush()
        ),
        ConnectCore.TargetUnit(
            i18n.NoFastPush,
            '禁止短時間內大量推文',
            LogLevel=Log.Level.INFO,
            BreakDetect=True,
            Exceptions=Exceptions.NoFastPush()
        ),
        ConnectCore.TargetUnit(
            i18n.NoPermission,
            '使用者不可發言',
            LogLevel=Log.Level.INFO,
            BreakDetect=True,
            Exceptions=Exceptions.NoPermission(i18n.NoPermission)
        ),
        ConnectCore.TargetUnit(
            i18n.NoPush,
            '◆ 抱歉, 禁止推薦',
            LogLevel=Log.Level.INFO,
            BreakDetect=True,
            Exceptions=Exceptions.NoPush()
        ),
    ]

    index = api._ConnectCore.send(
        Cmd,
        TargetList
    )

    if index == -1:
        if PostAID is not None:
            raise Exceptions.NoSuchPost(Board, PostAID)
        else:
            raise Exceptions.NoSuchPost(Board, PostIndex)

    EnablePush = False
    EnableBoo = False
    EnableArrow = False

    CmdList = []

    if index == 0:
        PushOptionLine = api._ConnectCore.getScreenQueue()[-1]
        PushOptionLine = PushOptionLine.split('\n')[-1]
        Log.showValue(api.Config, Log.Level.DEBUG,
                      'Push option line', PushOptionLine)

        EnablePush = '值得推薦' in PushOptionLine
        EnableBoo = '給它噓聲' in PushOptionLine
        EnableArrow = '只加→註解' in PushOptionLine

        Log.showValue(api.Config, Log.Level.DEBUG, 'Push', EnablePush)
        Log.showValue(api.Config, Log.Level.DEBUG, 'Boo', EnableBoo)
        Log.showValue(api.Config, Log.Level.DEBUG, 'Arrow', EnableArrow)

        if PushType == DataType.PushType.Push and not EnablePush:
            PushType = DataType.PushType.Arrow
        elif PushType == DataType.PushType.Boo and not EnableBoo:
            PushType = DataType.PushType.Arrow
        elif PushType == DataType.PushType.Arrow and not EnableArrow:
            PushType = DataType.PushType.Push

        CmdList.append(str(PushType))
    elif index == 1:
        PushType = DataType.PushType.Arrow

    CmdList.append(PushContent)
    CmdList.append(Command.Enter)
    CmdList.append('y')
    CmdList.append(Command.Enter)

    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            [
                i18n.Push,
                i18n.Success,
            ],
            Screens.Target.InBoard,
            BreakDetect=True,
            LogLevel=Log.Level.DEBUG
        ),
    ]

    index = api._ConnectCore.send(
        Cmd,
        TargetList
    )
