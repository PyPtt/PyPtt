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


def get_callstatus(api) -> None:

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
            break_detect=True,
            log_level=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]拔掉',
            break_detect=True,
            log_level=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]防水',
            break_detect=True,
            log_level=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]好友',
            break_detect=True,
            log_level=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]關閉',
            break_detect=True,
            log_level=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                i18n.GetCallStatus,
            ],
            '★',
            response=cmd,
            log_level=Log.Level.DEBUG
        ),
    ]

    for i in range(2):
        index = api.connect_core.send(cmd, target_list)
        if index < 0:
            if i == 0:
                continue
            ori_screen = api.connect_core.get_screen_queue()[-1]
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

    ori_screen = api.connect_core.get_screen_queue()[-1]
    raise Exceptions.UnknownError(ori_screen)


def set_callstatus(api, callstatus) -> None:
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
            break_detect=True
        )
    ]

    while current_call_status != callstatus:
        api.connect_core.send(
            cmd,
            target_list,
            screen_timeout=api.config.ScreenLongTimeOut
        )

        current_call_status = api._get_callstatus()
