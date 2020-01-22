import re
try:
    from . import DataType
    from . import Util
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Screens
    from . import Exceptions
    from . import Command
except ModuleNotFoundError:
    import DataType
    import Util
    import i18n
    import ConnectCore
    import Log
    import Screens
    import Exceptions
    import Command


def getUser(api, UserID):

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('T')
    CmdList.append(Command.Enter)
    CmdList.append('Q')
    CmdList.append(Command.Enter)
    CmdList.append(UserID)
    CmdList.append(Command.Enter)

    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            [
                i18n.GetUser,
                i18n.Success,
            ],
            Screens.Target.AnyKey,
            BreakDetect=True,
        ),
        ConnectCore.TargetUnit(
            [
                i18n.GetUser,
                i18n.Fail,
            ],
            Screens.Target.InTalk,
            BreakDetect=True,
        ),
    ]

    index = api._ConnectCore.send(
        Cmd,
        TargetList
    )
    OriScreen = api._ConnectCore.getScreenQueue()[-1]
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        'OriScreen',
        OriScreen
    )
    if index == 1:
        raise Exceptions.NoSuchUser(UserID)
    # PTT1
    # 《ＩＤ暱稱》CodingMan (專業程式 BUG 製造機)《經濟狀況》小康 ($73866)
    # 《登入次數》1118 次 (同天內只計一次) 《有效文章》15 篇 (退:0)
    # 《目前動態》閱讀文章     《私人信箱》最近無新信件
    # 《上次上站》10/06/2019 17:29:49 Sun  《上次故鄉》111.251.231.184
    # 《 五子棋 》 0 勝  0 敗  0 和 《象棋戰績》 0 勝  0 敗  0 和

    # https://github.com/Truth0906/PTTLibrary

    # 強大的 PTT 函式庫
    # 提供您 快速 穩定 完整 的 PTT API

    # 提供專業的 PTT 機器人諮詢服務

    # PTT2
    # 《ＩＤ暱稱》CodingMan (專業程式 BUG 製造機)《經濟狀況》家徒四壁 ($0)
    # 《登入次數》8 次 (同天內只計一次)  《有效文章》0 篇
    # 《目前動態》看板列表     《私人信箱》最近無新信件
    # 《上次上站》10/06/2019 17:27:55 Sun  《上次故鄉》111.251.231.184
    # 《 五子棋 》 0 勝  0 敗  0 和 《象棋戰績》 0 勝  0 敗  0 和

    # 《個人名片》CodingMan 目前沒有名片

    Data = Util.getSubStringList(OriScreen, '》', ['《', '\n'])
    if len(Data) < 10:
        print('\n'.join(Data))
        print(len(Data))
        raise Exceptions.ParseError(OriScreen)

    ID = Data[0]
    Money = Data[1]
    LoginTime = Data[2]
    LoginTime = LoginTime[:LoginTime.find(' ')]
    LoginTime = int(LoginTime)

    Temp = re.findall(r'\d+', Data[3])
    LegalPost = int(Temp[0])

    # PTT2 沒有退文
    if api.Config.Host == DataType.Host.PTT1:
        IllegalPost = int(Temp[1])
    else:
        IllegalPost = -1

    State = Data[4]
    Mail = Data[5]
    LastLogin = Data[6]
    LastIP = Data[7]
    FiveChess = Data[8]
    Chess = Data[9]

    SignatureFile = '\n'.join(OriScreen.split('\n')[6:-1]).strip()

    Log.showValue(api.Config, Log.Level.DEBUG, 'ID', ID)
    Log.showValue(api.Config, Log.Level.DEBUG, 'Money', Money)
    Log.showValue(api.Config, Log.Level.DEBUG, 'LoginTime', LoginTime)
    Log.showValue(api.Config, Log.Level.DEBUG, 'LegalPost', LegalPost)
    Log.showValue(api.Config, Log.Level.DEBUG, 'IllegalPost', IllegalPost)
    Log.showValue(api.Config, Log.Level.DEBUG, 'State', State)
    Log.showValue(api.Config, Log.Level.DEBUG, 'Mail', Mail)
    Log.showValue(api.Config, Log.Level.DEBUG, 'LastLogin', LastLogin)
    Log.showValue(api.Config, Log.Level.DEBUG, 'LastIP', LastIP)
    Log.showValue(api.Config, Log.Level.DEBUG, 'FiveChess', FiveChess)
    Log.showValue(api.Config, Log.Level.DEBUG, 'Chess', Chess)
    Log.showValue(api.Config, Log.Level.DEBUG,
                  'SignatureFile', SignatureFile)

    User = DataType.UserInfo(
        ID,
        Money,
        LoginTime,
        LegalPost,
        IllegalPost,
        State,
        Mail,
        LastLogin,
        LastIP,
        FiveChess,
        Chess,
        SignatureFile
    )
    return User
