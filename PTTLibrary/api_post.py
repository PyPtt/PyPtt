try:
    from . import i18n
    from . import ConnectCore
    from . import Screens
    from . import Exceptions
    from . import Command
except ModuleNotFoundError:
    import i18n
    import ConnectCore
    import Screens
    import Exceptions
    import Command


def post(
        api: object,
        board: str,
        title: str,
        content: str,
        post_type: int,
        sign_file) -> None:

    cmd_list = []
    cmd_list.append(Command.GoMainMenu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(Command.Enter)
    cmd_list.append(Command.Ctrl_C * 2)
    cmd_list.append(Command.Space)
    cmd_list.append(Command.Ctrl_P)

    cmd = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            i18n.HasPostPermission,
            '發表文章於【',
            break_detect=True,
        ),
        ConnectCore.TargetUnit(
            i18n.NoPermission,
            '使用者不可發言',
            break_detect=True,
        )
    ]
    index = api._ConnectCore.send(cmd, target_list)
    if index < 0:
        Screens.show(api.Config, api._ConnectCore.get_screen_queue())
        raise Exceptions.UnknownError(i18n.UnknownError)
    if index == 1:
        raise Exceptions.NoPermission(i18n.NoPermission)

    Screens.show(api.Config, api._ConnectCore.get_screen_queue())

    cmd_list = []
    cmd_list.append(str(post_type))
    cmd_list.append(Command.Enter)
    cmd_list.append(str(title))
    cmd_list.append(Command.Enter)
    cmd_list.append(Command.Ctrl_Y * 30)
    cmd_list.append(str(content))
    cmd_list.append(Command.Ctrl_X)
    cmd = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵繼續',
            break_detect=True,
        ),
        ConnectCore.TargetUnit(
            i18n.SaveFile,
            '確定要儲存檔案嗎',
            response='s' + Command.Enter,
        ),
        ConnectCore.TargetUnit(
            i18n.SelectSignature,
            'x=隨機',
            response=str(sign_file) + Command.Enter,
        ),
    ]
    index = api._ConnectCore.send(
        cmd,
        target_list,
        screen_timeout=api.Config.ScreenPostTimeOut
    )
