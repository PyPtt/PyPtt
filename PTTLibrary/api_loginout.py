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


def logout(api):

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('g')
    CmdList.append(Command.Enter)
    CmdList.append('y')
    CmdList.append(Command.Enter)

    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            [
                i18n.Logout,
                i18n.Success,
            ],
            '任意鍵',
            BreakDetect=True,
        ),
    ]

    Log.log(
        api.Config,
        Log.Level.INFO,
        [
            i18n.Start,
            i18n.Logout
        ]
    )

    try:
        api._ConnectCore.send(Cmd, TargetList)
        api._ConnectCore.close()
    except Exceptions.ConnectionClosed:
        pass
    except RuntimeError:
        pass

    api._LoginStatus = False

    Log.showValue(
        api.Config,
        Log.Level.INFO,
        i18n.Logout,
        i18n.Done
    )


def login(
        api,
        ID,
        Password,
        KickOtherLogin):

    if api._LoginStatus:
        api.logout()

    api.Config.KickOtherLogin = KickOtherLogin

    def KickOtherLoginDisplayMsg():
        if api.Config.KickOtherLogin:
            return i18n.KickOtherLogin
        return i18n.NotKickOtherLogin

    def KickOtherLoginResponse(Screen):
        if api.Config.KickOtherLogin:
            return 'y' + Command.Enter
        return 'n' + Command.Enter

    if len(Password) > 8:
        Password = Password[:8]

    ID = ID.strip()
    Password = Password.strip()

    api._ID = ID
    api._Password = Password

    Log.showValue(
        api.Config,
        Log.Level.INFO,
        [
            i18n.Login,
            i18n.ID
        ],
        ID
    )

    api.Config.KickOtherLogin = KickOtherLogin

    api._ConnectCore.connect()

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.HasNewMailGotoMainMenu,
            '你有新信件',
            Response=Command.GoMainMenu,
        ),
        ConnectCore.TargetUnit(
            i18n.LoginSuccess,
            Screens.Target.MainMenu,
            BreakDetect=True
        ),
        ConnectCore.TargetUnit(
            i18n.GoMainMenu,
            '【看板列表】',
            Response=Command.GoMainMenu,
        ),
        ConnectCore.TargetUnit(
            i18n.ErrorIDPW,
            '密碼不對或無此帳號',
            BreakDetect=True,
            Exceptions=Exceptions.WrongIDorPassword()
        ),
        ConnectCore.TargetUnit(
            i18n.LoginTooOften,
            '登入太頻繁',
            BreakDetect=True,
            Exceptions=Exceptions.LoginTooOften()
        ),
        ConnectCore.TargetUnit(
            i18n.SystemBusyTryLater,
            '系統過載',
            BreakDetect=True,
        ),
        ConnectCore.TargetUnit(
            i18n.DelWrongPWRecord,
            '您要刪除以上錯誤嘗試的記錄嗎',
            Response='y' + Command.Enter,
        ),
        ConnectCore.TargetUnit(
            i18n.MailBoxFull,
            '您保存信件數目',
            Response=Command.GoMainMenu,
        ),
        ConnectCore.TargetUnit(
            i18n.PostNotFinish,
            '請選擇暫存檔 (0-9)[0]',
            Response=Command.Enter,
        ),
        ConnectCore.TargetUnit(
            i18n.PostNotFinish,
            '有一篇文章尚未完成',
            Response='Q' + Command.Enter,
        ),
        ConnectCore.TargetUnit(
            i18n.SigningUnPleaseWait,
            '登入中，請稍候',
        ),
        ConnectCore.TargetUnit(
            KickOtherLoginDisplayMsg,
            '您想刪除其他重複登入的連線嗎',
            Response=KickOtherLoginResponse,
        ),
        ConnectCore.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵',
            Response=Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.SigningUpdate,
            '正在更新與同步線上使用者及好友名單',
        ),
    ]

    CmdList = []
    CmdList.append(ID)
    CmdList.append(Command.Enter)
    CmdList.append(Password)
    CmdList.append(Command.Enter)

    Cmd = ''.join(CmdList)

    index = api._ConnectCore.send(
        Cmd,
        TargetList,
        ScreenTimeout=api.Config.ScreenLongTimeOut,
        Refresh=False,
        Secret=True
    )

    if TargetList[index].getDisplayMsg() != i18n.LoginSuccess:
        # OriScreen = api._ConnectCore.getScreenQueue()[-1]
        # print(OriScreen)
        raise Exceptions.LoginError()

    OriScreen = api._ConnectCore.getScreenQueue()[-1]
    if '> (' in OriScreen:
        api._Cursor = DataType.Cursor.New
        Log.log(
            api.Config,
            Log.Level.DEBUG,
            i18n.NewCursor
        )
    else:
        api._Cursor = DataType.Cursor.Old
        Log.log(
            api.Config,
            Log.Level.DEBUG,
            i18n.OldCursor
        )

    if api._Cursor not in Screens.Target.InBoardWithCursor:
        Screens.Target.InBoardWithCursor.append('\n' + api._Cursor)

    api._UnregisteredUser = False
    if '(T)alk' not in OriScreen:
        api._UnregisteredUser = True
    if '(P)lay' not in OriScreen:
        api._UnregisteredUser = True
    if '(N)amelist' not in OriScreen:
        api._UnregisteredUser = True

    if api._UnregisteredUser:
        print(OriScreen)
        Log.log(
            api.Config,
            Log.Level.INFO,
            i18n.UnregisteredUserCantUseAllAPI
        )

    api._LoginStatus = True
