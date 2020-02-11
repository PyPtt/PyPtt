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


def logout(api) -> None:

    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('g')
    cmd_list.append(command.Enter)
    cmd_list.append('y')
    cmd_list.append(command.Enter)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            [
                i18n.logout,
                i18n.Success,
            ],
            '任意鍵',
            break_detect=True,
        ),
    ]

    log.log(
        api.config,
        log.Level.INFO,
        [
            i18n.Start,
            i18n.logout
        ]
    )

    try:
        api.connect_core.send(cmd, target_list)
        api.connect_core.close()
    except exceptions.ConnectionClosed:
        pass
    except RuntimeError:
        pass

    api._login_status = False

    log.show_value(
        api.config,
        log.Level.INFO,
        i18n.logout,
        i18n.Done
    )


def login(
        api,
        ptt_id,
        password,
        kick_other_login):

    if api._login_status:
        api.logout()

    api.config.kick_other_login = kick_other_login

    def kick_other_loginDisplayMsg():
        if api.config.kick_other_login:
            return i18n.kick_other_login
        return i18n.Notkick_other_login

    def kick_other_loginResponse(Screen):
        if api.config.kick_other_login:
            return 'y' + command.Enter
        return 'n' + command.Enter

    if len(password) > 8:
        password = password[:8]

    ptt_id = ptt_id.strip()
    password = password.strip()

    api._ID = ptt_id
    api._Password = password

    api.config.kick_other_login = kick_other_login

    api.connect_core.connect()

    log.show_value(
        api.config,
        log.Level.INFO,
        [
            i18n.login,
            i18n.ID
        ],
        ptt_id
    )

    target_list = [
        connect_core.TargetUnit(
            i18n.loginSuccess,
            screens.Target.MainMenu,
            break_detect=True
        ),
        connect_core.TargetUnit(
            i18n.HasNewMailGotoMainMenu,
            '你有新信件',
            # 加個進去 A 選單再出來的動作，讓畫面更新最底下一行
            response=command.GoMainMenu + 'A' + command.Right + command.Left,
        ),
        connect_core.TargetUnit(
            i18n.GoMainMenu,
            '【看板列表】',
            response=command.GoMainMenu,
        ),
        connect_core.TargetUnit(
            i18n.ErrorIDPW,
            '密碼不對',
            break_detect=True,
            exceptions_=exceptions.WrongIDorPassword()
        ),
        connect_core.TargetUnit(
            i18n.LoginTooOften,
            '登入太頻繁',
            break_detect=True,
            exceptions_=exceptions.LoginTooOften()
        ),
        connect_core.TargetUnit(
            i18n.SystemBusyTryLater,
            '系統過載',
            break_detect=True,
        ),
        connect_core.TargetUnit(
            i18n.DelWrongPWRecord,
            '您要刪除以上錯誤嘗試的記錄嗎',
            response='y' + command.Enter,
        ),
        connect_core.TargetUnit(
            i18n.MailBoxFull,
            '您保存信件數目',
            response=command.GoMainMenu,
        ),
        connect_core.TargetUnit(
            i18n.PostNotFinish,
            '請選擇暫存檔 (0-9)[0]',
            response=command.Enter,
        ),
        connect_core.TargetUnit(
            i18n.PostNotFinish,
            '有一篇文章尚未完成',
            response='Q' + command.Enter,
        ),
        connect_core.TargetUnit(
            i18n.SigningUnPleaseWait,
            '登入中，請稍候',
        ),
        connect_core.TargetUnit(
            kick_other_loginDisplayMsg,
            '您想刪除其他重複登入的連線嗎',
            response=kick_other_loginResponse,
        ),
        connect_core.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵',
            response=command.Enter
        ),
        connect_core.TargetUnit(
            i18n.SigningUpdate,
            '正在更新與同步線上使用者及好友名單',
        ),
    ]

    cmd_list = []
    cmd_list.append(ptt_id)
    cmd_list.append(command.Enter)
    cmd_list.append(password)
    cmd_list.append(command.Enter)

    cmd = ''.join(cmd_list)

    index = api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout,
        refresh=False,
        secret=True
    )

    if target_list[index].get_display_msg() != i18n.loginSuccess:
        ori_screen = api.connect_core.get_screen_queue()[-1]
        print(ori_screen)
        raise exceptions.LoginError()

    ori_screen = api.connect_core.get_screen_queue()[-1]
    if '> (' in ori_screen:
        api.cursor = data_type.Cursor.NEW
        log.log(
            api.config,
            log.Level.DEBUG,
            i18n.NewCursor
        )
    else:
        api.cursor = data_type.Cursor.OLD
        log.log(
            api.config,
            log.Level.DEBUG,
            i18n.OldCursor
        )

    if api.cursor not in screens.Target.InBoardWithCursor:
        screens.Target.InBoardWithCursor.append('\n' + api.cursor)

    api._unregistered_user = True
    if '(T)alk' in ori_screen:
        api._unregistered_user = False
    if '(P)lay' in ori_screen:
        api._unregistered_user = False
    if '(N)amelist' in ori_screen:
        api._unregistered_user = False

    if api._unregistered_user:
        # print(ori_screen)
        log.log(
            api.config,
            log.Level.INFO,
            i18n.UnregisteredUserCantUseAllAPI
        )

    api._login_status = True
