try:
    from . import i18n
    from . import connect_core
    from . import screens
    from . import exceptions
    from . import command
except ModuleNotFoundError:
    import i18n
    import connect_core
    import screens
    import exceptions
    import command


def post(
        api: object,
        board: str,
        title: str,
        content: str,
        post_type: int,
        sign_file) -> None:
    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(command.Enter)
    cmd_list.append(command.Ctrl_C * 2)
    cmd_list.append(command.Space)
    cmd_list.append(command.Ctrl_P)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.HasPostPermission,
            '發表文章於【',
            break_detect=True,
        ),
        connect_core.TargetUnit(
            i18n.NoPermission,
            '使用者不可發言',
            break_detect=True,
        ),
        connect_core.TargetUnit(
            i18n.NoPermission,
            '無法發文: 未達看板要求權限',
            break_detect=True
        ),
    ]
    index = api.connect_core.send(cmd, target_list)
    if index < 0:
        screens.show(api.config, api.connect_core.get_screen_queue())
        raise exceptions.UnknownError(i18n.UnknownError)
    if index == 1 or index == 2:
        raise exceptions.NoPermission(i18n.NoPermission)

    screens.show(api.config, api.connect_core.get_screen_queue())

    cmd_list = []
    cmd_list.append(str(post_type))
    cmd_list.append(command.Enter)
    cmd_list.append(str(title))
    cmd_list.append(command.Enter)
    cmd_list.append(command.Ctrl_Y * 40)
    cmd_list.append(str(content))
    cmd_list.append(command.Ctrl_X)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵繼續',
            break_detect=True,
        ),
        connect_core.TargetUnit(
            i18n.SaveFile,
            '確定要儲存檔案嗎',
            response='s' + command.Enter,
        ),
        connect_core.TargetUnit(
            i18n.SelectSignature,
            'x=隨機',
            response=str(sign_file) + command.Enter,
        ),
    ]
    index = api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_post_timeout
    )
