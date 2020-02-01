try:
    from . import data_type
    from . import i18n
    from . import ConnectCore
    from . import log
    from . import screens
    from . import exceptions
    from . import Command
except ModuleNotFoundError:
    import data_type
    import i18n
    import ConnectCore
    import log
    import screens
    import exceptions
    import Command


def push(
        api,
        board: str,
        push_type: int,
        push_content: str,
        post_aid: str,
        post_index: int) -> None:

    cmd_list = []
    cmd_list.append(Command.GoMainMenu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(Command.Enter)
    cmd_list.append(Command.Ctrl_C * 2)
    cmd_list.append(Command.Space)

    if post_aid is not None:
        cmd_list.append('#' + post_aid)
    elif post_index != 0:
        cmd_list.append(str(post_index))
    cmd_list.append(Command.Enter)
    cmd_list.append(Command.Push)

    cmd = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            i18n.HasPushPermission,
            '您覺得這篇',
            log_level=log.Level.DEBUG,
            break_detect=True
        ),
        ConnectCore.TargetUnit(
            i18n.OnlyArrow,
            '加註方式',
            log_level=log.Level.DEBUG,
            break_detect=True
        ),
        ConnectCore.TargetUnit(
            i18n.NoFastPush,
            '禁止快速連續推文',
            log_level=log.Level.INFO,
            break_detect=True,
            exceptions=exceptions.NoFastPush()
        ),
        ConnectCore.TargetUnit(
            i18n.NoFastPush,
            '禁止短時間內大量推文',
            log_level=log.Level.INFO,
            break_detect=True,
            exceptions=exceptions.NoFastPush()
        ),
        ConnectCore.TargetUnit(
            i18n.NoPermission,
            '使用者不可發言',
            log_level=log.Level.INFO,
            break_detect=True,
            exceptions=exceptions.NoPermission(i18n.NoPermission)
        ),
        ConnectCore.TargetUnit(
            i18n.NoPush,
            '◆ 抱歉, 禁止推薦',
            log_level=log.Level.INFO,
            break_detect=True,
            exceptions=exceptions.NoPush()
        ),
    ]

    index = api.connect_core.send(
        cmd,
        target_list
    )

    if index == -1:
        if post_aid is not None:
            raise exceptions.NoSuchPost(board, post_aid)
        else:
            raise exceptions.NoSuchPost(board, post_index)

    cmd_list = []

    if index == 0:
        push_option_line = api.connect_core.get_screen_queue()[-1]
        push_option_line = push_option_line.split('\n')[-1]
        log.show_value(api.config, log.Level.DEBUG,
                      'Push option line', push_option_line)

        enable_push = '值得推薦' in push_option_line
        enable_boo = '給它噓聲' in push_option_line
        enable_arrow = '只加→註解' in push_option_line

        log.show_value(api.config, log.Level.DEBUG, 'Push', enable_push)
        log.show_value(api.config, log.Level.DEBUG, 'Boo', enable_boo)
        log.show_value(api.config, log.Level.DEBUG, 'Arrow', enable_arrow)

        if push_type == data_type.PushType.Push and not enable_push:
            push_type = data_type.PushType.Arrow
        elif push_type == data_type.PushType.Boo and not enable_boo:
            push_type = data_type.PushType.Arrow
        elif push_type == data_type.PushType.Arrow and not enable_arrow:
            push_type = data_type.PushType.Push

        cmd_list.append(str(push_type))
    # elif index == 1:
    #     push_type = data_type.PushType.Arrow

    cmd_list.append(push_content)
    cmd_list.append(Command.Enter)
    cmd_list.append('y')
    cmd_list.append(Command.Enter)

    cmd = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            [
                i18n.Push,
                i18n.Success,
            ],
            screens.Target.InBoard,
            break_detect=True,
            log_level=log.Level.DEBUG
        ),
    ]

    api.connect_core.send(
        cmd,
        target_list
    )
