try:
    from . import data_type
    from . import i18n
    from . import connect_core
    from . import log
    from . import screens
    from . import exceptions
    from . import command
except ModuleNotFoundError:
    import data_type
    import i18n
    import connect_core
    import log
    import screens
    import exceptions
    import command


def get_call_status(api) -> None:

    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('A')
    cmd_list.append(command.Right)
    cmd_list.append(command.Left)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]打開',
            break_detect=True,
            log_level=log.level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]拔掉',
            break_detect=True,
            log_level=log.level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]防水',
            break_detect=True,
            log_level=log.level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]好友',
            break_detect=True,
            log_level=log.level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                i18n.GetCallStatus,
                i18n.Success,
            ],
            '[呼叫器]關閉',
            break_detect=True,
            log_level=log.level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                i18n.GetCallStatus,
            ],
            '★',
            response=cmd,
            log_level=log.level.DEBUG
        ),
    ]

    for i in range(2):
        index = api.connect_core.send(cmd, target_list)
        if index < 0:
            if i == 0:
                continue
            ori_screen = api.connect_core.get_screen_queue()[-1]
            raise exceptions.UnknownError(ori_screen)

    if index == 0:
        return data_type.call_status.ON
    if index == 1:
        return data_type.call_status.UNPLUG
    if index == 2:
        return data_type.call_status.WATERPROOF
    if index == 3:
        return data_type.call_status.FRIEND
    if index == 4:
        return data_type.call_status.OFF

    ori_screen = api.connect_core.get_screen_queue()[-1]
    raise exceptions.UnknownError(ori_screen)


def set_call_status(api, call_status) -> None:
    # 打開 -> 拔掉 -> 防水 -> 好友 -> 關閉

    current_call_status = api._get_call_status()

    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append(command.Ctrl_U)
    cmd_list.append('p')

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            [
                i18n.SetCallStatus,
                i18n.Success
            ],
            screens.Target.InUserList,
            break_detect=True
        )
    ]

    while current_call_status != call_status:
        api.connect_core.send(
            cmd,
            target_list,
            screen_timeout=api.config.screen_long_timeout
        )

        current_call_status = api._get_call_status()
