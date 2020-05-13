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


def change_pw(
        api,
        new_password: str) -> None:
    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('U')
    cmd_list.append(command.Enter)
    cmd_list.append('I')
    cmd_list.append(command.Enter)
    cmd_list.append('2')
    cmd_list.append(command.Enter)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.ErrorPW,
            '您輸入的密碼不正確',
            exceptions_=exceptions.WrongPassword()
        ),
        connect_core.TargetUnit(
            i18n.confirm,
            '請您確定(Y/N)？',
            response='Y' + command.Enter
        ),
        connect_core.TargetUnit(
            i18n.CheckNewPassword,
            '檢查新密碼',
            response=new_password + command.Enter,
            max_match=1
        ),
        connect_core.TargetUnit(
            i18n.InputNewPassword,
            '設定新密碼',
            response=new_password + command.Enter,
            max_match=1
        ),
        connect_core.TargetUnit(
            i18n.InputOriginPassword,
            '輸入原密碼',
            response=api._Password + command.Enter,
            max_match=1
        ),
        connect_core.TargetUnit(
            i18n.Done,
            '設定個人資料與密碼',
            break_detect=True
        ),
    ]

    index = api.connect_core.send(
        cmd,
        target_list,
    )
    if index < 0:
        raise exceptions.Timeout

    api._Password = new_password

    # ori_screen = api.connect_core.get_screen_queue()[-1]
    # print(ori_screen)
