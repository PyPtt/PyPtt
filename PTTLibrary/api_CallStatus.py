try:
    from . import DataType
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Screens
    from . import Exceptions
    from . import Command
except ModuleNotFoundError:
    import DataType
    import i18n
    import ConnectCore
    import Log
    import Screens
    import Exceptions
    import Command


def getCallStatus(api):

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('A')
    CmdList.append(Command.Right)
    CmdList.append(Command.Left)

    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]打開',
            BreakDetect=True,
            LogLevel=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]拔掉',
            BreakDetect=True,
            LogLevel=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]防水',
            BreakDetect=True,
            LogLevel=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]好友',
            BreakDetect=True,
            LogLevel=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]關閉',
            BreakDetect=True,
            LogLevel=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                i18n.GetCallStatus,
            ],
            '★',
            Response=Cmd,
            LogLevel=Log.Level.DEBUG
        ),
    ]

    for i in range(2):
        index = api._ConnectCore.send(Cmd, TargetList)
        if index < 0:
            if i == 0:
                continue
            OriScreen = api._ConnectCore.getScreenQueue()[-1]
            raise Exceptions.UnknownError(OriScreen)

    if index == 0:
        return DataType.CallStatus.On
    if index == 1:
        return DataType.CallStatus.Unplug
    if index == 2:
        return DataType.CallStatus.Waterproof
    if index == 3:
        return DataType.CallStatus.Friend
    if index == 4:
        return DataType.CallStatus.Off

    OriScreen = api._ConnectCore.getScreenQueue()[-1]
    raise Exceptions.UnknownError(OriScreen)


def setCallStatus(api, inputCallStatus):
    # 打開 -> 拔掉 -> 防水 -> 好友 -> 關閉

    CurrentCallStatus = api._getCallStatus()

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append(Command.Ctrl_U)
    CmdList.append('p')

    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            [
                i18n.SetCallStatus,
                i18n.Success
            ],
            Screens.Target.InUserList,
            BreakDetect=True
        )
    ]

    while CurrentCallStatus != inputCallStatus:
        api._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=api.Config.ScreenLongTimeOut
        )

        CurrentCallStatus = api._getCallStatus()
