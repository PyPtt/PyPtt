import re

try:
    from . import data_type
    from . import i18n
    from . import connect_core
    from . import log
    from . import exceptions
    from . import command
except ModuleNotFoundError:
    import data_type
    import i18n
    import connect_core
    import log
    import exceptions
    import command


def get_board_info(
        api, board: str,
        call_by_others: bool) -> None:

    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(command.Enter)
    cmd_list.append(command.Ctrl_C * 2)
    cmd_list.append(command.Space)
    cmd = ''.join(cmd_list)

    if call_by_others:
        log_level = log.Level.DEBUG
    else:
        log_level = log.Level.INFO

    target_list = [
        connect_core.TargetUnit(
            i18n.IntoBoard,
            [
                '文章選讀',
                '進板畫面'
            ],
            break_detect=True,
            log_level=log_level
        ),
    ]

    api.connect_core.send(
        cmd,
        target_list
    )

    ori_screen = api.connect_core.get_screen_queue()[-1]
    # print(OriScreen)
    nuser = ori_screen.split('\n')[2]
    # print(Nuser)
    if '[靜]' in nuser:
        online_user = 0
    else:
        if '編號' not in nuser or '人氣' not in nuser:
            raise exceptions.NoSuchBoard(api.config, board)
        pattern = re.compile('[\d]+')
        r = pattern.search(nuser)
        if r is None:
            raise exceptions.NoSuchBoard(api.config, board)
        # 減一是把自己本身拿掉
        online_user = int(r.group(0)) - 1
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '人氣',
        online_user
    )

    target_list = [
        connect_core.TargetUnit(
            i18n.ReadingBoardInfo,
            '任意鍵繼續',
            break_detect=True,
            log_level=log_level
        ),
    ]

    api.connect_core.send(
        'i',
        target_list
    )

    ori_screen = api.connect_core.get_screen_queue()[-1]
    # print(OriScreen)

    p = re.compile('《(.+)》看板設定')
    r = p.search(ori_screen)
    if r is not None:
        boardname = r.group(0)[1:-5].strip()
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '看板名稱',
        boardname
    )

    if boardname != board:
        raise exceptions.NoSuchBoard(api.config, board)

    p = re.compile('中文敘述: (.+)')
    r = p.search(ori_screen)
    if r is not None:
        chinese_des = r.group(0)[5:].strip()
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '中文敘述',
        chinese_des
    )

    p = re.compile('板主名單: (.+)')
    r = p.search(ori_screen)
    if r is not None:
        moderator_line = r.group(0)[5:].strip()
        moderators = moderator_line.split('/')
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '板主名單',
        moderators
    )

    open_status = ('公開狀態(是否隱形): 公開' in ori_screen)
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '公開狀態',
        open_status
    )

    into_top_ten_when_hide = (
            '隱板時 可以 進入十大排行榜' in ori_screen
    )
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '隱板時可以進入十大排行榜',
        into_top_ten_when_hide
    )

    non_board_members_post = ('開放 非看板會員發文' in ori_screen)
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '非看板會員發文',
        non_board_members_post
    )

    reply_post = ('開放 回應文章' in ori_screen)
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '回應文章',
        reply_post
    )

    self_del_post = ('開放 自刪文章' in ori_screen)
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '自刪文章',
        self_del_post
    )

    push_post = ('開放 推薦文章' in ori_screen)
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '推薦文章',
        push_post
    )

    boo_post = ('開放 噓文' in ori_screen)
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '噓文',
        boo_post
    )

    # 限制 快速連推文章, 最低間隔時間: 5 秒
    # 開放 快速連推文章

    fast_push = ('開放 快速連推文章' in ori_screen)
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '快速連推文章',
        fast_push
    )

    if not fast_push:
        p = re.compile('最低間隔時間: [\d]+')
        r = p.search(ori_screen)
        if r is not None:
            min_interval = r.group(0)[7:].strip()
            min_interval = int(min_interval)
        else:
            min_interval = 0
        log.show_value(
            api.config,
            log.Level.DEBUG,
            '最低間隔時間',
            min_interval
        )
    else:
        min_interval = 0

    # 推文時 自動 記錄來源 IP
    # 推文時 不會 記錄來源 IP
    push_record_ip = ('推文時 自動 記錄來源 IP' in ori_screen)
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '記錄來源 IP',
        push_record_ip
    )

    # 推文時 對齊 開頭
    # 推文時 不用對齊 開頭
    push_aligned = ('推文時 對齊 開頭' in ori_screen)
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '對齊開頭',
        push_aligned
    )

    # 板主 可 刪除部份違規文字
    moderator_can_del_illegal_content = (
            '板主 可 刪除部份違規文字' in ori_screen
    )
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '板主可刪除部份違規文字',
        moderator_can_del_illegal_content
    )

    # 轉錄文章 會 自動記錄，且 需要 發文權限
    tran_post_auto_recorded_and_require_post_permissions = (
            '轉錄文章 會 自動記錄，且 需要 發文權限' in ori_screen
    )
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '轉錄文章 會 自動記錄，且 需要 發文權限',
        tran_post_auto_recorded_and_require_post_permissions
    )

    cool_mode = (
            '未 設為冷靜模式' not in ori_screen
    )
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '冷靜模式',
        cool_mode
    )

    require18 = (
            '禁止 未滿十八歲進入' in ori_screen
    )

    log.show_value(
        api.config,
        log.Level.DEBUG,
        '禁止未滿十八歲進入',
        require18
    )

    p = re.compile('登入次數 [\d]+ 次以上')
    r = p.search(ori_screen)
    if r is not None:
        require_login_time = r.group(0).split(' ')[1]
        require_login_time = int(require_login_time)
    else:
        require_login_time = 0
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '發文限制登入次數',
        require_login_time
    )

    p = re.compile('退文篇數 [\d]+ 篇以下')
    r = p.search(ori_screen)
    if r is not None:
        require_illegal_post = r.group(0).split(' ')[1]
        require_illegal_post = int(require_illegal_post)
    else:
        require_illegal_post = 0
    log.show_value(
        api.config,
        log.Level.DEBUG,
        '發文限制退文篇數',
        require_illegal_post
    )

    board_info = data_type.BoardInfo(
        boardname,
        online_user,
        chinese_des,
        moderators,
        open_status,
        into_top_ten_when_hide,
        non_board_members_post,
        reply_post,
        self_del_post,
        push_post,
        boo_post,
        fast_push,
        min_interval,
        push_record_ip,
        push_aligned,
        moderator_can_del_illegal_content,
        tran_post_auto_recorded_and_require_post_permissions,
        cool_mode,
        require18,
        require_login_time,
        require_illegal_post,
    )
    return board_info
