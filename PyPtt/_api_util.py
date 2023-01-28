from __future__ import annotations

import re
import threading
from typing import Dict

from SingleLog import DefaultLogger
from SingleLog import LogLevel

from . import _api_get_board_info
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import screens


def get_content(api, post_mode: bool = True):
    logger = DefaultLogger('get_content')
    api.Unconfirmed = False

    def is_unconfirmed_handler(screen):
        api.Unconfirmed = True

    if post_mode:
        cmd = command.enter * 2
    else:
        cmd = command.enter

    target_list = [
        # 待證實文章
        connect_core.TargetUnit('本篇文章內容經站方授權之板務管理人員判斷有尚待證實之處', response=' ',
                                handler=is_unconfirmed_handler),
        connect_core.TargetUnit(screens.Target.PostEnd, log_level=LogLevel.DEBUG, break_detect=True),
        connect_core.TargetUnit(screens.Target.InPost, log_level=LogLevel.DEBUG, break_detect=True),
        connect_core.TargetUnit(screens.Target.PostNoContent, log_level=LogLevel.DEBUG, break_detect=True),
        # 動畫文章
        connect_core.TargetUnit(screens.Target.Animation, response=command.go_main_menu_type_q,
                                break_detect_after_send=True),
    ]

    line_from_pattern = re.compile('[\d]+~[\d]+')

    content_start = '───────────────────────────────────────'
    content_end = []
    content_end.append('--\n※ 發信站: 批踢踢實業坊')
    content_end.append('--\n※ 發信站: 批踢踢兔(ptt2.cc)')
    content_end.append('--\n※ 發信站: 新批踢踢(ptt2.twbbs.org.tw)')

    has_control_code = False
    control_code_mode = False
    push_start = False
    content_start_exist = False
    content_start_jump = False
    content_start_jump_set = False

    first_page = True
    origin_post = []
    stop_dict = dict()

    while True:
        index = api.connect_core.send(cmd, target_list)
        if index == 3 or index == 4:
            return None, False

        last_screen = api.connect_core.get_screen_queue()[-1]
        lines = last_screen.split('\n')
        last_line = lines[-1]
        lines.pop()
        last_screen = '\n'.join(lines)

        if content_start in last_screen and not content_start_exist:
            content_start_exist = True

        if content_start_exist:
            if not content_start_jump_set:
                if content_start not in last_screen:
                    content_start_jump = True
                    content_start_jump_set = True
            else:
                content_start_jump = False

        pattern_result = line_from_pattern.search(last_line)
        if pattern_result is None:
            control_code_mode = True
            has_control_code = True
        else:
            last_read_line_list = pattern_result.group(0).split('~')
            last_read_line_a_temp = int(last_read_line_list[0])
            last_read_line_b_temp = int(last_read_line_list[1])
            if control_code_mode:
                last_read_line_a = last_read_line_a_temp - 1
                last_read_line_b = last_read_line_b_temp - 1
            control_code_mode = False

        if first_page:
            first_page = False
            origin_post.append(last_screen)
        else:
            # print(LastScreen)
            # print(f'last_read_line_a_temp [{last_read_line_a_temp}]')
            # print(f'last_read_line_b_temp [{last_read_line_b_temp}]')
            # print(f'last_read_line_a {last_read_line_a}')
            # print(f'last_read_line_b {last_read_line_b}')
            # print(f'GetLineB {last_read_line_a_temp - last_read_line_a}')
            # print(f'GetLineA {last_read_line_b_temp - last_read_line_b}')
            # print(f'show line {last_read_line_b_temp - last_read_line_a_temp + 1}')
            if not control_code_mode:

                if last_read_line_a_temp in stop_dict:
                    new_content_part = '\n'.join(
                        lines[-stop_dict[last_read_line_a_temp]:])
                    stop_dict = dict()
                else:
                    get_line_b = last_read_line_b_temp - last_read_line_b
                    if get_line_b > 0:
                        # print('Type 1')
                        # print(f'Type 1 line_dis [{line_dis}]')
                        # print(f'Type 1 get_line_b [{get_line_b}]')
                        # print('index', index)
                        new_content_part = '\n'.join(lines[-get_line_b:])
                        if index == 1 and len(new_content_part) == get_line_b - 1:
                            # print(1)
                            new_content_part = '\n'.join(lines[-(get_line_b * 2):])
                        elif origin_post:
                            # print(2)
                            last_line_temp = origin_post[-1].strip()
                            try_line = lines[-(get_line_b + 1)].strip()

                            if not last_line_temp.endswith(try_line):
                                # print(3)
                                # print('=====' * 20)
                                # print('== last line [', last_line_temp, ']')
                                # print('== try_line [', try_line, ']')
                                new_content_part = try_line + '\n' + new_content_part
                        stop_dict = dict()
                    else:
                        # 駐足現象，LastReadLineB跟上一次相比並沒有改變
                        if (last_read_line_b_temp + 1) not in stop_dict:
                            stop_dict[last_read_line_b_temp + 1] = 1
                        stop_dict[last_read_line_b_temp + 1] += 1

                        get_line_a = last_read_line_a_temp - last_read_line_a

                        if get_line_a > 0:
                            # print(f'Type 2 get_line_a [{get_line_a}]')
                            new_content_part = '\n'.join(lines[-get_line_a:])
                        else:
                            new_content_part = '\n'.join(lines)

            else:
                new_content_part = lines[-1]

            origin_post.append(new_content_part)

            logger.debug('NewContentPart', new_content_part)

        if index == 1:
            if content_start_jump and len(new_content_part) == 0:
                # print(f'!!!GetLineB {GetLineB}')
                get_line_b += 1
                new_content_part = '\n'.join(lines[-get_line_b:])
                # print(f'!!!NewContentPart {NewContentPart}')
                origin_post.pop()
                origin_post.append(new_content_part)
            break

        if not control_code_mode:
            last_read_line_a = last_read_line_a_temp
            last_read_line_b = last_read_line_b_temp

        for EC in content_end:
            if EC in last_screen:
                push_start = True
                break

        if not push_start:
            cmd = command.down
        else:
            cmd = command.right

    # print(api.Unconfirmed)
    origin_post = '\n'.join(origin_post)
    # OriginPost = [line.strip() for line in OriginPost.split('\n')]
    # OriginPost = '\n'.join(OriginPost)

    logger.debug('OriginPost', origin_post)

    return origin_post, has_control_code


def get_mailbox_capacity(api):
    last_screen = api.connect_core.get_screen_queue()[-1]
    capacity_line = last_screen.split('\n')[2]

    logger = DefaultLogger('get_mailbox_capacity')
    logger.debug('capacity_line', capacity_line)

    pattern_result = re.compile('(\d+)/(\d+)').search(capacity_line)
    if pattern_result is not None:
        # print(pattern_result.group(0))
        current_capacity = int(pattern_result.group(0).split('/')[0])
        max_capacity = int(pattern_result.group(0).split('/')[1])

        logger.debug('current_capacity', current_capacity)
        logger.debug('max_capacity', max_capacity)

        return current_capacity, max_capacity
    return 0, 0


# >     1   112/09 ericsk       □ [心得] 終於開板了
# ┌── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ─┐
# │ 文章代碼(AID): #13cPSYOX (Python) [ptt.cc] [心得] 終於開板了  │
# │ 文章網址: https://www.ptt.cc/bbs/Python/M.1134139170.A.621.html      │
# │ 這一篇文章值 2 Ptt幣                                              │
# └── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ─┘

def parse_query_post(api, ori_screen):
    logger = DefaultLogger('parse_query_post')
    lock_post = False
    try:
        cursor_line = [line for line in ori_screen.split(
            '\n') if line.strip().startswith(api.cursor)][0]
    except Exception as e:
        print(api.cursor)
        print(ori_screen)
        raise e

    post_author = cursor_line
    if '□' in post_author:
        post_author = post_author[:post_author.find('□')].strip()
    elif 'R:' in post_author:
        post_author = post_author[:post_author.find('R:')].strip()
    elif ' 轉 ' in post_author:
        post_author = post_author[:post_author.find('轉')].strip()
    elif ' 鎖 ' in post_author:
        post_author = post_author[:post_author.find('鎖')].strip()
        lock_post = True
    post_author = post_author[post_author.rfind(' '):].strip()

    post_title = cursor_line
    if ' □ ' in post_title:
        post_title = post_title[post_title.find('□') + 1:].strip()
    elif ' R:' in post_title:
        post_title = post_title[post_title.find('R:'):].strip()
    elif ' 轉 ' in post_title:
        # print(f'[{PostTitle}]=========>')
        post_title = post_title[post_title.find('轉') + 1:].strip()
        post_title = f'Fw: {post_title}'
        # print(f'=========>[{PostTitle}]')
    elif ' 鎖 ' in post_title:
        post_title = post_title[post_title.find('鎖') + 1:].strip()

    ori_screen_temp = ori_screen[ori_screen.find('┌──'):]
    ori_screen_temp = ori_screen_temp[:ori_screen_temp.find('└──')]

    aid_line = [line for line in ori_screen.split(
        '\n') if line.startswith('│ 文章代碼(AID)')]

    post_aid = None
    if len(aid_line) == 1:
        aid_line = aid_line[0]
        pattern = re.compile('#[\w|-]+')
        pattern_result = pattern.search(aid_line)
        post_aid = pattern_result.group(0)[1:]

    pattern = re.compile('文章網址: https:[\S]+html')
    pattern_result = pattern.search(ori_screen_temp)

    if pattern_result is None:
        post_web = None
    else:
        post_web = pattern_result.group(0)[6:]

    pattern = re.compile('這一篇文章值 [\d]+ Ptt幣')
    pattern_result = pattern.search(ori_screen_temp)
    if pattern_result is None:
        # 特殊文章無價格
        post_money = -1
    else:
        post_money = pattern_result.group(0)[7:]
        post_money = post_money[:post_money.find(' ')]
        post_money = int(post_money)

    pattern = re.compile('[\d]+\/[\d]+')
    pattern_result = pattern.search(cursor_line)
    if pattern_result is None:
        list_date = None
    else:
        list_date = pattern_result.group(0)
        list_date = list_date[-5:]
    # print(list_date)

    # >  7485   9 8/09 CodingMan    □ [閒聊] PTT Library 更新
    # > 79189 M 1 9/17 LittleCalf   □ [公告] 禁言退文公告
    # >781508 +爆 9/17 jodojeda     □ [新聞] 國人吃魚少 學者：應把吃魚當成輕鬆愉快
    # >781406 +X1 9/17 kingofage111 R: [申請] ReDmango 請辭Gossiping板主職務

    pattern = re.compile('[\d]+')
    pattern_result = pattern.search(cursor_line)
    if pattern_result is not None:
        post_index = int(pattern_result.group(0))

    push_number = cursor_line
    # print(f'2>{push_number}<')
    push_number = push_number[7:11]
    # print(push_number)
    push_number = push_number.split(' ')
    # print(PushNumber)
    push_number = list(filter(None, push_number))
    # print(push_number)

    if len(push_number) == 0:
        push_number = None
    else:
        push_number = push_number[-1]
        if push_number.startswith('爆') or push_number.startswith('~爆'):
            push_number = '爆'

        if push_number.startswith('+') or push_number.startswith('~'):
            push_number = push_number[1:]
            # print(PushNumber)
        if push_number.lower().startswith('m'):
            push_number = push_number[1:]
            # print(PushNumber)
        if push_number.lower().startswith('!'):
            push_number = push_number[1:]

        if push_number.lower().startswith('s'):
            push_number = push_number[1:]

        if push_number.lower().startswith('='):
            push_number = push_number[1:]

        if len(push_number) == 0:
            push_number = None

    # print(PushNumber)

    logger.debug('PostAuthor', post_author)
    logger.debug('PostTitle', post_title)
    logger.debug('PostAID', post_aid)
    logger.debug('PostWeb', post_web)
    logger.debug('PostMoney', post_money)
    logger.debug('ListDate', list_date)
    logger.debug('PushNumber', push_number)

    return lock_post, post_author, post_title, post_aid, post_web, post_money, list_date, push_number, post_index


def get_search_condition_cmd(api, index_type: data_type.NewIndex, board: [str | None] = None,
                             search_type: data_type.SearchType = data_type.SearchType.NOPE,
                             search_condition: [str | None] = None, search_list: [list | None] = None):
    # log.py = DefaultLogger('get_search_condition_cmd')
    cmd_list = []

    normal_newest_index = -1
    if search_condition is not None:

        if index_type == data_type.NewIndex.BOARD:
            normal_newest_index = api.get_newest_index(index_type, board=board)
        else:
            normal_newest_index = api.get_newest_index(index_type)

        if search_type == data_type.SearchType.KEYWORD:
            cmd_list.append('/')
        elif search_type == data_type.SearchType.AUTHOR:
            cmd_list.append('a')
        elif search_type == data_type.SearchType.MARK:
            cmd_list.append('G')

        if index_type == data_type.NewIndex.BOARD:
            if search_type == data_type.SearchType.COMMENT:
                cmd_list.append('Z')
            elif search_type == data_type.SearchType.MONEY:
                cmd_list.append('A')

        cmd_list.append(search_condition)
        cmd_list.append(command.enter)

    if search_list is not None:

        if normal_newest_index == -1:
            if index_type == data_type.NewIndex.BOARD:
                normal_newest_index = api.get_newest_index(index_type, board=board)
            else:
                normal_newest_index = api.get_newest_index(index_type)

        for search_type_, search_condition_ in search_list:

            # print('==>', search_type_, search_condition_)

            if search_type_ == data_type.SearchType.KEYWORD:
                cmd_list.append('/')
            elif search_type_ == data_type.SearchType.AUTHOR:
                cmd_list.append('a')
            elif search_type_ == data_type.SearchType.MARK:
                cmd_list.append('G')
            elif index_type == data_type.NewIndex.BOARD:
                if search_type_ == data_type.SearchType.COMMENT:
                    cmd_list.append('Z')
                elif search_type_ == data_type.SearchType.MONEY:
                    cmd_list.append('A')
                else:
                    continue
            else:
                continue

            cmd_list.append(search_condition_)
            cmd_list.append(command.enter)

    return cmd_list, normal_newest_index


def goto_board(api, board: str, refresh: bool = False, end: bool = False) -> None:
    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(command.enter)
    cmd_list.append(command.space)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('任意鍵', log_level=LogLevel.DEBUG, response=' '),
        connect_core.TargetUnit('互動式動畫播放中', log_level=LogLevel.DEBUG, response=command.ctrl_c),
        connect_core.TargetUnit(screens.Target.InBoard, log_level=LogLevel.DEBUG, break_detect=True),
    ]

    if refresh:
        current_refresh = True
    else:
        if board.lower() in api._goto_board_list:
            current_refresh = True
        else:
            current_refresh = False
    api._goto_board_list.append(board.lower())
    api.connect_core.send(cmd, target_list, refresh=current_refresh)

    if end:
        cmd_list = []
        cmd_list.append('1')
        cmd_list.append(command.enter)
        cmd_list.append('$')
        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit(screens.Target.InBoard, log_level=LogLevel.DEBUG, break_detect=True),
        ]

        api.connect_core.send(cmd, target_list)


def one_thread(api):
    current_thread_id = threading.get_ident()
    if current_thread_id == api._thread_id:
        return

    raise exceptions.MultiThreadOperated()


def check_board(api, board: str, check_moderator: bool = False) -> Dict:
    if board.lower() not in api._exist_board_list:
        board_info = _api_get_board_info.get_board_info(api, board, get_post_kind=False, call_by_others=False)
        api._exist_board_list.append(board.lower())
        api._board_info_list[board.lower()] = board_info

        moderators = board_info[data_type.BoardField.moderators]
        moderators = [x.lower() for x in moderators]
        api._ModeratorList[board.lower()] = moderators
        api._board_info_list[board.lower()] = board_info

    if check_moderator:
        if api.ptt_id.lower() not in api._ModeratorList[board.lower()]:
            raise exceptions.NeedModeratorPermission(board)

    return api._board_info_list[board.lower()]
