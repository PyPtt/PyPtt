import re
from typing import Dict

from SingleLog.log import Logger

import PyPtt
from . import command, check_value, _api_util
from . import connect_core
from . import exceptions
from . import i18n
from . import screens
from .data_type import Board


def get_board_info(
        api: PyPtt.API,
        board: str,
        get_post_kind: bool,
        call_by_others: bool) -> Dict:
    logger = Logger('get_board_info', Logger.DEBUG if call_by_others else Logger.INFO)

    _api_util._one_thread(api)

    if not api._login_status:
        raise exceptions.Requirelogin(i18n.require_login)

    check_value.check_type(str, 'board', board)

    api._goto_board(board, refresh=True)

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
        pattern = re.compile('[\d]+')
        r = pattern.search(nuser)
        if r is None:
            raise exceptions.NoSuchBoard(api.config, board)
        # 減一是把自己本身拿掉
        online_user = int(r.group(0)) - 1

    logger.debug('人氣', online_user)

    target_list = [
        connect_core.TargetUnit(
            i18n.reading_board_info,
            '任意鍵繼續',
            break_detect=True,
            log_level=log_level
        ),
    ]

    api.connect_core.send(
        'i',
        target_list)

    ori_screen = api.connect_core.get_screen_queue()[-1]
    # print(ori_screen)

    p = re.compile('《(.+)》看板設定')
    r = p.search(ori_screen)
    if r is not None:
        boardname = r.group(0)[1:-5].strip()

    logger.debug('看板名稱', boardname, board)

    if boardname.lower() != board.lower():
        raise exceptions.NoSuchBoard(api.config, board)

    p = re.compile('中文敘述: (.+)')
    r = p.search(ori_screen)
    if r is not None:
        chinese_des = r.group(0)[5:].strip()
    logger.debug('中文敘述', chinese_des)

    p = re.compile('板主名單: (.+)')
    r = p.search(ori_screen)
    if r is not None:
        moderator_line = r.group(0)[5:].strip()
        if '(無)' in moderator_line:
            moderators = list()
        else:
            moderators = moderator_line.split('/')
            for moderator in moderators.copy():
                check = True
                for c in moderator:
                    if len(c.encode('big5')) > 1:
                        check = False
                        break
                if not check:
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
        p = re.compile('最低間隔時間: [\d]+')
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

    p = re.compile('登入次數 [\d]+ 次以上')
    r = p.search(ori_screen)
    if r is not None:
        require_login_time = r.group(0).split(' ')[1]
        require_login_time = int(require_login_time)
    else:
        require_login_time = 0
    logger.debug('發文限制登入次數', require_login_time)

    p = re.compile('退文篇數 [\d]+ 篇以下')
    r = p.search(ori_screen)
    if r is not None:
        require_illegal_post = r.group(0).split(' ')[1]
        require_illegal_post = int(require_illegal_post)
    else:
        require_illegal_post = 0
    logger.debug('發文限制退文篇數', require_illegal_post)

    kind_list = None
    if get_post_kind:

        api._goto_board(board)

        # Go certain board, then post to get post type info
        cmd_list = list()
        cmd_list.append(command.ctrl_p)
        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit(
                i18n.no_permission,
                '無法發文: 未達看板要求權限',
                break_detect=True
            ),
            connect_core.TargetUnit(
                i18n.complete,
                '或不選)',
                break_detect=True
            )
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
                type_pattern = re.compile('\d\.([^\ ]*)')
                # 0 is not present any type that the key hold None object
                kind_list = type_pattern.findall(i)
                break

        # Clear post status
        cmd_list = list()
        cmd_list.append(command.ctrl_c)
        cmd_list.append(command.ctrl_c)
        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit(
                i18n.complete,
                screens.Target.InBoard,
                break_detect=True
            )
        ]
        api.connect_core.send(
            cmd,
            target_list)

    # board_info = data_type.BoardInfo(
    #     boardname,
    #     online_user,
    #     chinese_des,
    #     moderators,
    #     open_status,
    #     into_top_ten_when_hide,
    #     non_board_members_post,
    #     reply_post,
    #     self_del_post,
    #     push_post,
    #     boo_post,
    #     fast_push,
    #     min_interval,
    #     push_record_ip,
    #     push_aligned,
    #     moderator_can_del_illegal_content,
    #     tran_post_auto_recorded_and_require_post_permissions,
    #     cool_mode,
    #     require18,
    #     require_login_time,
    #     require_illegal_post,
    #     kind_list)
    return {
        Board.board: boardname,
        Board.online_user: online_user,
        Board.chinese_des: chinese_des,
        Board.moderators: moderators,
        Board.open_status: open_status,
        Board.into_top_ten_when_hide: into_top_ten_when_hide,
        Board.non_board_members_post: non_board_members_post,
        Board.reply_post: reply_post,
        Board.self_del_post: self_del_post,
        Board.push_post: push_post,
        Board.boo_post: boo_post,
        Board.fast_push: fast_push,
        Board.min_interval: min_interval,
        Board.push_record_ip: push_record_ip,
        Board.push_aligned: push_aligned,
        Board.moderator_can_del_illegal_content: moderator_can_del_illegal_content,
        Board.tran_post_auto_recorded_and_require_post_permissions: tran_post_auto_recorded_and_require_post_permissions,
        Board.cool_mode: cool_mode,
        Board.require18: require18,
        Board.require_login_time: require_login_time,
        Board.require_illegal_post: require_illegal_post,
        Board.kind_list: kind_list
    }
