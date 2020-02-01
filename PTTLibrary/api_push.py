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
            log_level=Log.Level.DEBUG,
            break_detect=True
        ),
        ConnectCore.TargetUnit(
            i18n.OnlyArrow,
            '加註方式',
            log_level=Log.Level.DEBUG,
            break_detect=True
        ),
        ConnectCore.TargetUnit(
            i18n.NoFastPush,
            '禁止快速連續推文',
            log_level=Log.Level.INFO,
            break_detect=True,
            exceptions=Exceptions.NoFastPush()
        ),
        ConnectCore.TargetUnit(
            i18n.NoFastPush,
            '禁止短時間內大量推文',
            log_level=Log.Level.INFO,
            break_detect=True,
            exceptions=Exceptions.NoFastPush()
        ),
        ConnectCore.TargetUnit(
            i18n.NoPermission,
            '使用者不可發言',
            log_level=Log.Level.INFO,
            break_detect=True,
            exceptions=Exceptions.NoPermission(i18n.NoPermission)
        ),
        ConnectCore.TargetUnit(
            i18n.NoPush,
            '◆ 抱歉, 禁止推薦',
            log_level=Log.Level.INFO,
            break_detect=True,
            exceptions=Exceptions.NoPush()
        ),
    ]

    index = api.connect_core.send(
        cmd,
        target_list
    )

    if index == -1:
        if post_aid is not None:
            raise Exceptions.NoSuchPost(board, post_aid)
        else:
            raise Exceptions.NoSuchPost(board, post_index)

    cmd_list = []

    if index == 0:
        push_option_line = api.connect_core.get_screen_queue()[-1]
        push_option_line = push_option_line.split('\n')[-1]
        Log.show_value(api.config, Log.Level.DEBUG,
                      'Push option line', push_option_line)

        enable_push = '值得推薦' in push_option_line
        enable_boo = '給它噓聲' in push_option_line
        enable_arrow = '只加→註解' in push_option_line

        Log.show_value(api.config, Log.Level.DEBUG, 'Push', enable_push)
        Log.show_value(api.config, Log.Level.DEBUG, 'Boo', enable_boo)
        Log.show_value(api.config, Log.Level.DEBUG, 'Arrow', enable_arrow)

        if push_type == DataType.PushType.Push and not enable_push:
            push_type = DataType.PushType.Arrow
        elif push_type == DataType.PushType.Boo and not enable_boo:
            push_type = DataType.PushType.Arrow
        elif push_type == DataType.PushType.Arrow and not enable_arrow:
            push_type = DataType.PushType.Push

        cmd_list.append(str(push_type))
    # elif index == 1:
    #     push_type = DataType.PushType.Arrow

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
            Screens.Target.InBoard,
            break_detect=True,
            log_level=Log.Level.DEBUG
        ),
    ]

    api.connect_core.send(
        cmd,
        target_list
    )
