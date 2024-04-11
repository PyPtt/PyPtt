import re
from typing import Dict

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import log
from . import screens
from .data_type import BoardField


def get_board_info(api, board: str, get_post_kind: bool, call_by_others: bool) -> Dict:
    logger = log.init(log.DEBUG if call_by_others else log.INFO)

    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    check_value.check_type(board, str, 'board')

    logger.info(
        i18n.replace(i18n.get_board_info, board))

    _api_util.goto_board(api, board, refresh=True)

    ori_screen = api.connect_core.get_screen_queue()[-1]
    # print(ori_screen)

    nuser = None
    for line in ori_screen.split('\n'):
        if '編號' not in line:
            continue
        if '日 期' not in line:
            continue
        if '人氣' not in line:
            continue

        nuser = line
        break

    if nuser is None:
        raise exceptions.NoSuchBoard(api.config, board)

    # print('------------------------')
    # print('nuser', nuser)
    # print('------------------------')
    if '[靜]' in nuser:
        online_user = 0
    else:
        if '編號' not in nuser or '人氣' not in nuser:
            raise exceptions.NoSuchBoard(api.config, board)
        pattern = re.compile(r'[\d]+')
        r = pattern.search(nuser)
        if r is None:
            raise exceptions.NoSuchBoard(api.config, board)
        # 減一是把自己本身拿掉
        online_user = int(r.group(0)) - 1

    logger.debug('人氣', online_user)

    target_list = [
        connect_core.TargetUnit('任意鍵繼續', log_level=log.DEBUG if call_by_others else log.INFO,
                                break_detect=True),
    ]

    api.connect_core.send(
        'i',
        target_list)

    ori_screen = api.connect_core.get_screen_queue()[-1]
    # print(ori_screen)

    p = re.compile(r'《(.+)》看板設定')
    r = p.search(ori_screen)
    if r is not None:
        boardname = r.group(0)[1:-5].strip()

    logger.debug('看板名稱', boardname, board)

    if boardname.lower() != board.lower():
        raise exceptions.NoSuchBoard(api.config, board)

    p = re.compile(r'中文敘述: (.+)')
    r = p.search(ori_screen)
    if r is not None:
        chinese_des = r.group(0)[5:].strip()
    logger.debug('中文敘述', chinese_des)

    p = re.compile(r'板主名單: (.+)')
    r = p.search(ori_screen)
    if r is not None:
        moderator_line = r.group(0)[5:].strip()
        if '(無)' in moderator_line:
            moderators = []
        else:
            moderators = moderator_line.split('/')
            for moderator in moderators.copy():
                if moderator == '徵求中':
                    moderators.remove(moderator)
    logger.debug('板主名單', moderators)

    open_status = ('公開狀態(是否隱形): 公開' in ori_screen)
    logger.debug('公開狀態', open_status)

    into_top_ten_when_hide = ('隱板時 可以 進入十大排行榜' in ori_screen)
    logger.debug('隱板時可以進入十大排行榜', into_top_ten_when_hide)

    non_board_members_post = ('開放 非看板會員發文' in ori_screen)
    logger.debug('非看板會員發文', non_board_members_post)

    reply_post = ('開放 回應文章' in ori_screen)
    logger.debug('回應文章', reply_post)

    self_del_post = ('開放 自刪文章' in ori_screen)
    logger.debug('自刪文章', self_del_post)

    push_post = ('開放 推薦文章' in ori_screen)
    logger.debug('推薦文章', push_post)

    boo_post = ('開放 噓文' in ori_screen)
    logger.debug('噓文', boo_post)

    # 限制 快速連推文章, 最低間隔時間: 5 秒
    # 開放 快速連推文章

    fast_push = ('開放 快速連推文章' in ori_screen)
    logger.debug('快速連推文章', fast_push)

    if not fast_push:
        p = re.compile(r'最低間隔時間: [\d]+')
        r = p.search(ori_screen)
        if r is not None:
            min_interval = r.group(0)[7:].strip()
            min_interval = int(min_interval)
        else:
            min_interval = 0
        logger.debug('最低間隔時間', min_interval)
    else:
        min_interval = 0

    # 推文時 自動 記錄來源 IP
    # 推文時 不會 記錄來源 IP
    push_record_ip = ('推文時 自動 記錄來源 IP' in ori_screen)
    logger.debug('記錄來源 IP', push_record_ip)

    # 推文時 對齊 開頭
    # 推文時 不用對齊 開頭
    push_aligned = ('推文時 對齊 開頭' in ori_screen)
    logger.debug('對齊開頭', push_aligned)

    # 板主 可 刪除部份違規文字
    moderator_can_del_illegal_content = ('板主 可 刪除部份違規文字' in ori_screen)
    logger.debug('板主可刪除部份違規文字', moderator_can_del_illegal_content)

    # 轉錄文章 會 自動記錄，且 需要 發文權限
    tran_post_auto_recorded_and_require_post_permissions = ('轉錄文章 會 自動記錄，且 需要 發文權限' in ori_screen)
    logger.debug('轉錄文章 會 自動記錄，且 需要 發文權限', tran_post_auto_recorded_and_require_post_permissions)

    cool_mode = ('未 設為冷靜模式' not in ori_screen)
    logger.debug('冷靜模式', cool_mode)

    require18 = ('禁止 未滿十八歲進入' in ori_screen)
    logger.debug('禁止未滿十八歲進入', require18)

    p = re.compile(r'登入次數 [\d]+ 次以上')
    r = p.search(ori_screen)
    if r is not None:
        require_login_time = r.group(0).split(' ')[1]
        require_login_time = int(require_login_time)
    else:
        require_login_time = 0
    logger.debug('發文限制登入次數', require_login_time)

    p = re.compile(r'退文篇數 [\d]+ 篇以下')
    r = p.search(ori_screen)
    if r is not None:
        require_illegal_post = r.group(0).split(' ')[1]
        require_illegal_post = int(require_illegal_post)
    else:
        require_illegal_post = 0
    logger.debug('發文限制退文篇數', require_illegal_post)

    kind_list = []
    if get_post_kind:

        _api_util.goto_board(api, board)

        # Go certain board, then post to get post type info
        cmd_list = []
        cmd_list.append(command.ctrl_p)
        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit('無法發文: 未達看板要求權限', break_detect=True),
            connect_core.TargetUnit('或不選)', break_detect=True)
        ]

        index = api.connect_core.send(
            cmd,
            target_list)

        if index == 0:
            raise exceptions.NoPermission(i18n.no_permission)
            # no post permission

        ori_screen = api.connect_core.get_screen_queue()[-1]
        screen_lines = ori_screen.split('\n')

        for i in screen_lines:
            if '種類：' in i:
                type_pattern = re.compile(r'\d\.([^\ ]*)')
                # 0 is not present any type that the key hold None object
                kind_list = type_pattern.findall(i)
                break

        # Clear post status
        cmd_list = []
        cmd_list.append(command.ctrl_c)
        cmd_list.append(command.ctrl_c)
        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit(screens.Target.InBoard, break_detect=True)
        ]
        api.connect_core.send(
            cmd,
            target_list)

    logger.info(
        i18n.replace(i18n.get_board_info, board),
        '...', i18n.success
    )

    return {
        BoardField.board: boardname,
        BoardField.online_user: online_user,
        BoardField.mandarin_des: chinese_des,
        BoardField.moderators: moderators,
        BoardField.open_status: open_status,
        BoardField.into_top_ten_when_hide: into_top_ten_when_hide,
        BoardField.can_non_board_members_post: non_board_members_post,
        BoardField.can_reply_post: reply_post,
        BoardField.self_del_post: self_del_post,
        BoardField.can_comment_post: push_post,
        BoardField.can_boo_post: boo_post,
        BoardField.can_fast_push: fast_push,
        BoardField.min_interval_between_comments: min_interval,
        BoardField.is_comment_record_ip: push_record_ip,
        BoardField.is_comment_aligned: push_aligned,
        BoardField.can_moderators_del_illegal_content: moderator_can_del_illegal_content,
        BoardField.does_tran_post_auto_recorded_and_require_post_permissions: tran_post_auto_recorded_and_require_post_permissions,
        BoardField.is_cool_mode: cool_mode,
        BoardField.is_require18: require18,
        BoardField.require_login_time: require_login_time,
        BoardField.require_illegal_post: require_illegal_post,
        BoardField.post_kind_list: kind_list
    }
