import re
try:
    from . import DataType
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Exceptions
    from . import Command
except ModuleNotFoundError:
    import DataType
    import i18n
    import ConnectCore
    import Log
    import Exceptions
    import Command


def getBoardInfo(api, board):

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('qs')
    CmdList.append(board)
    CmdList.append(Command.Enter)
    CmdList.append(Command.Ctrl_C * 2)
    CmdList.append(Command.Space)
    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.LoginSuccess,
            [
                '文章選讀',
                '進板畫面'
            ],
            BreakDetect=True
        ),
    ]

    api._ConnectCore.send(
        Cmd,
        TargetList
    )

    OriScreen = api._ConnectCore.getScreenQueue()[-1]
    # print(OriScreen)
    Nuser = OriScreen.split('\n')[2]
    # print(Nuser)
    if '[靜]' in Nuser:
        OnlineUser = 0
    else:
        if '編號' not in Nuser or '人氣' not in Nuser:
            raise Exceptions.NoSuchBoard(api.Config, board)
        pattern = re.compile('[\d]+')
        r = pattern.search(Nuser)
        if r is None:
            raise Exceptions.NoSuchBoard(api.Config, board)
        OnlineUser = r.group(0)
        Log.showValue(
            api.Config,
            Log.Level.DEBUG,
            '人氣',
            OnlineUser
        )

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵繼續',
            BreakDetect=True,
            LogLevel=Log.Level.DEBUG
        ),
    ]

    index = api._ConnectCore.send(
        'i',
        TargetList
    )

    OriScreen = api._ConnectCore.getScreenQueue()[-1]
    # print(OriScreen)

    p = re.compile('《(.+)》看板設定')
    r = p.search(OriScreen)
    if r is not None:
        boardname = r.group(0)[1:-5].strip()
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '看板名稱',
        boardname
    )

    if boardname != board:
        raise Exceptions.NoSuchBoard(api.Config, board)

    p = re.compile('中文敘述: (.+)')
    r = p.search(OriScreen)
    if r is not None:
        ChineseDes = r.group(0)[5:].strip()
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '中文敘述',
        ChineseDes
    )

    p = re.compile('板主名單: (.+)')
    r = p.search(OriScreen)
    if r is not None:
        ModeratorLine = r.group(0)[5:].strip()
        Moderators = ModeratorLine.split('/')
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '板主名單',
        Moderators
    )

    OpenState = ('公開狀態(是否隱形): 公開' in OriScreen)
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '公開狀態',
        OpenState
    )

    IntoTopTenWhenHide = (
        '隱板時 可以 進入十大排行榜' in OriScreen
    )
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '隱板時可以進入十大排行榜',
        IntoTopTenWhenHide
    )

    NonBoardMembersPost = ('開放 非看板會員發文' in OriScreen)
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '非看板會員發文',
        NonBoardMembersPost
    )

    ReplyPost = ('開放 回應文章' in OriScreen)
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '回應文章',
        ReplyPost
    )

    SelfDelPost = ('開放 自刪文章' in OriScreen)
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '自刪文章',
        SelfDelPost
    )

    PushPost = ('開放 推薦文章' in OriScreen)
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '推薦文章',
        PushPost
    )

    BooPost = ('開放 噓文' in OriScreen)
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '噓文',
        BooPost
    )

    # 限制 快速連推文章, 最低間隔時間: 5 秒
    # 開放 快速連推文章

    FastPush = ('開放 快速連推文章' in OriScreen)
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '快速連推文章',
        FastPush
    )

    if not FastPush:
        p = re.compile('最低間隔時間: [\d]+')
        r = p.search(OriScreen)
        if r is not None:
            MinInterval = r.group(0)[7:].strip()
            MinInterval = int(MinInterval)
        else:
            MinInterval = 0
        Log.showValue(
            api.Config,
            Log.Level.DEBUG,
            '最低間隔時間',
            MinInterval
        )
    else:
        MinInterval = 0

    # 推文時 自動 記錄來源 IP
    # 推文時 不會 記錄來源 IP
    PushRecordIP = ('推文時 自動 記錄來源 IP' in OriScreen)
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '記錄來源 IP',
        PushRecordIP
    )

    # 推文時 對齊 開頭
    # 推文時 不用對齊 開頭
    PushAligned = ('推文時 對齊 開頭' in OriScreen)
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '對齊開頭',
        PushAligned
    )

    # 板主 可 刪除部份違規文字
    ModeratorCanDelIllegalContent = (
        '板主 可 刪除部份違規文字' in OriScreen
    )
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '板主可刪除部份違規文字',
        ModeratorCanDelIllegalContent
    )

    # 轉錄文章 會 自動記錄，且 需要 發文權限
    TranPostAutoRecordedAndRequirePostPermissions = (
        '轉錄文章 會 自動記錄，且 需要 發文權限' in OriScreen
    )
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '轉錄文章 會 自動記錄，且 需要 發文權限',
        TranPostAutoRecordedAndRequirePostPermissions
    )

    CoolMode = (
        '未 設為冷靜模式' not in OriScreen
    )
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '冷靜模式',
        CoolMode
    )

    Require18 = (
        '禁止 未滿十八歲進入' in OriScreen
    )

    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '禁止未滿十八歲進入',
        Require18
    )

    p = re.compile('登入次數 [\d]+ 次以上')
    r = p.search(OriScreen)
    if r is not None:
        RequireLoginTime = r.group(0).split(' ')[1]
        RequireLoginTime = int(RequireLoginTime)
    else:
        RequireLoginTime = 0
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '發文限制登入次數',
        RequireLoginTime
    )

    p = re.compile('退文篇數 [\d]+ 篇以下')
    r = p.search(OriScreen)
    if r is not None:
        RequireIllegalPost = r.group(0).split(' ')[1]
        RequireIllegalPost = int(RequireIllegalPost)
    else:
        RequireIllegalPost = 0
    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        '發文限制退文篇數',
        RequireIllegalPost
    )

    BoardInfo = DataType.BoardInfo(
        boardname,
        OnlineUser,
        ChineseDes,
        Moderators,
        OpenState,
        IntoTopTenWhenHide,
        NonBoardMembersPost,
        ReplyPost,
        SelfDelPost,
        PushPost,
        BooPost,
        FastPush,
        MinInterval,
        PushRecordIP,
        PushAligned,
        ModeratorCanDelIllegalContent,
        TranPostAutoRecordedAndRequirePostPermissions,
        CoolMode,
        Require18,
        RequireLoginTime,
        RequireIllegalPost,
    )
    return BoardInfo
