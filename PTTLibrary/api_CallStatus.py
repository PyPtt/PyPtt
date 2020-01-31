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

    cmd_list = []
    cmd_list.append(Command.GoMainMenu)
    cmd_list.append('A')
    cmd_list.append(Command.Right)
    cmd_list.append(Command.Left)

    cmd = ''.join(cmd_list)

    target_list = [
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
            Response=cmd,
            LogLevel=Log.Level.DEBUG
        ),
    ]

    for i in range(2):
        index = api._ConnectCore.send(cmd, target_list)
        if index < 0:
            if i == 0:
                continue
            ori_screen = api._ConnectCore.getScreenQueue()[-1]
            raise Exceptions.UnknownError(ori_screen)

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

    ori_screen = api._ConnectCore.getScreenQueue()[-1]
    raise Exceptions.UnknownError(ori_screen)


def set_callstatus(api, inputCallStatus):
    # 打開 -> 拔掉 -> 防水 -> 好友 -> 關閉

    current_call_status = api._get_callstatus()

    cmd_list = []
    cmd_list.append(Command.GoMainMenu)
    cmd_list.append(Command.Ctrl_U)
    cmd_list.append('p')

    cmd = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            [
                i18n.SetCallStatus,
                i18n.Success
            ],
            Screens.Target.InUserList,
            BreakDetect=True
        )
    ]

    while current_call_status != inputCallStatus:
        api._ConnectCore.send(
            cmd,
            target_list,
            ScreenTimeout=api.Config.ScreenLongTimeOut
        )

        current_call_status = api._get_callstatus()
