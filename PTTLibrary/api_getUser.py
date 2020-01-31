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


def get_user(api, pttid) -> DataType.UserInfo:

    cmd_list = []
    cmd_list.append(Command.GoMainMenu)
    cmd_list.append('T')
    cmd_list.append(Command.Enter)
    cmd_list.append('Q')
    cmd_list.append(Command.Enter)
    cmd_list.append(pttid)
    cmd_list.append(Command.Enter)

    cmd = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            [
                i18n.GetUser,
                i18n.Success,
            ],
            Screens.Target.AnyKey,
            break_detect=True,
        ),
        ConnectCore.TargetUnit(
            [
                i18n.GetUser,
                i18n.Fail,
            ],
            Screens.Target.InTalk,
            break_detect=True,
        ),
    ]

    index = api._ConnectCore.send(
        cmd,
        target_list
    )
    ori_screen = api._ConnectCore.get_screen_queue()[-1]
    Log.show_value(
        api.Config,
        Log.Level.DEBUG,
        'OriScreen',
        ori_screen
    )
    if index == 1:
        raise Exceptions.NoSuchUser(pttid)
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

    data = Util.get_sub_string_list(ori_screen, '》', ['《', '\n'])
    if len(data) < 10:
        print('\n'.join(data))
        print(len(data))
        raise Exceptions.ParseError(ori_screen)

    pttid = data[0]
    money = data[1]
    login_time = data[2]
    login_time = login_time[:login_time.find(' ')]
    login_time = int(login_time)

    temp = re.findall(r'\d+', data[3])
    legal_post = int(temp[0])

    # PTT2 沒有退文
    if api.Config.Host == DataType.Host.PTT1:
        illegal_post = int(temp[1])
    else:
        illegal_post = -1

    state = data[4]
    mail = data[5]
    last_login = data[6]
    last_ip = data[7]
    five_chess = data[8]
    chess = data[9]

    signature_file = '\n'.join(ori_screen.split('\n')[6:-1]).strip()

    Log.show_value(api.Config, Log.Level.DEBUG, 'pttid', pttid)
    Log.show_value(api.Config, Log.Level.DEBUG, 'money', money)
    Log.show_value(api.Config, Log.Level.DEBUG, 'login_time', login_time)
    Log.show_value(api.Config, Log.Level.DEBUG, 'legal_post', legal_post)
    Log.show_value(api.Config, Log.Level.DEBUG, 'illegal_post', illegal_post)
    Log.show_value(api.Config, Log.Level.DEBUG, 'state', state)
    Log.show_value(api.Config, Log.Level.DEBUG, 'mail', mail)
    Log.show_value(api.Config, Log.Level.DEBUG, 'last_login', last_login)
    Log.show_value(api.Config, Log.Level.DEBUG, 'last_ip', last_ip)
    Log.show_value(api.Config, Log.Level.DEBUG, 'five_chess', five_chess)
    Log.show_value(api.Config, Log.Level.DEBUG, 'chess', chess)
    Log.show_value(api.Config, Log.Level.DEBUG,
                  'signature_file', signature_file)

    user = DataType.UserInfo(
        pttid,
        money,
        login_time,
        legal_post,
        illegal_post,
        state,
        mail,
        last_login,
        last_ip,
        five_chess,
        chess,
        signature_file
    )
    return user
