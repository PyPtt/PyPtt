from __future__ import annotations

import json
import re
import time
from typing import Dict, Optional

from AutoStrEnum import AutoJsonEncoder

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import lib_util
from . import log
from . import screens
from .data_type import PostField, CommentField


def get_post(api, board: str, aid: Optional[str] = None, index: Optional[int] = None,
             search_list: Optional[list] = None,
             search_type: Optional[data_type.SearchType] = None,
             search_condition: Optional[str] = None, query: bool = False) -> Dict:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    check_value.check_type(board, str, 'board')
    if aid is not None:
        check_value.check_type(aid, str, 'aid')
    if index is not None:
        check_value.check_type(index, int, 'index')

    if search_list is None:
        search_list = []
    else:
        check_value.check_type(search_list, list, 'search_list')

    if (search_type, search_condition) != (None, None):
        search_list.insert(0, (search_type, search_condition))

    for search_type, search_condition in search_list:
        check_value.check_type(search_type, data_type.SearchType, 'search_type')
        check_value.check_type(search_condition, str, 'search_condition')

    if len(board) == 0:
        raise ValueError(f'board error parameter: {board}')

    if index > 0 and aid is not None:
        raise ValueError('wrong parameter index and aid can\'t both input')

    if aid is not None:
        pass
    elif index > 0:
        pass
    else:
        raise ValueError('wrong parameter index or aid must input')

    search_cmd = None
    if search_list is not None and len(search_list) > 0:
        current_index = api.get_newest_index(data_type.NewIndex.BOARD, board=board, search_list=search_list)
        search_cmd = _api_util.get_search_condition_cmd(data_type.NewIndex.BOARD, search_list)
    else:
        current_index = api.get_newest_index(data_type.NewIndex.BOARD, board=board)

    if index is not None and index > 0:
        check_value.check_index('index', index, current_index)

    max_retry = 2
    post = {}
    for i in range(max_retry):
        try:
            post = _get_post(api, board, aid, index, query, search_cmd)
            if not post:
                pass
            elif not post[PostField.pass_format_check]:
                pass
            else:
                break
        except exceptions.UnknownError:
            if i == max_retry - 1:
                raise
        except exceptions.NoSuchBoard:
            if i == max_retry - 1:
                raise

        log.logger.debug('Wait for retry repost')
        time.sleep(0.1)

    post = json.dumps(post, cls=AutoJsonEncoder)
    return json.loads(post)


def _get_post(api, board: str, post_aid: Optional[str] = None, post_index: int = 0, query: bool = False,
              search_cmd_list: Optional[list[str]] = None) -> Dict:
    _api_util.check_board(api, board)
    _api_util.goto_board(api, board)

    cmd_list = []

    if post_aid is not None:
        cmd_list.append(lib_util.check_aid(post_aid))
    elif post_index != 0:

        if search_cmd_list is not None:
            cmd_list.extend(search_cmd_list)

        cmd_list.append(str(max(1, post_index - 100)))
        cmd_list.append(command.enter)
        cmd_list.append(str(post_index))
    else:
        raise ValueError('post_aid and post_index cannot be None at the same time')

    cmd_list.append(command.enter)
    cmd_list.append(command.query_post)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            screens.Target.PTT1_QueryPost if api.config.host == data_type.HOST.PTT1 else screens.Target.PTT2_QueryPost,
            log_level=log.DEBUG, break_detect=True, refresh=False),
        connect_core.TargetUnit(screens.Target.InBoard, log_level=log.DEBUG, break_detect=True),
        connect_core.TargetUnit(screens.Target.MainMenu_Exiting, exceptions_=exceptions.NoSuchBoard(api.config, board)),
    ]

    index = api.connect_core.send(cmd, target_list)
    ori_screen = api.connect_core.get_screen_queue()[-1]

    post = {
        PostField.board: None,
        PostField.aid: None,
        PostField.index: None,
        PostField.author: None,
        PostField.date: None,
        PostField.title: None,
        PostField.content: None,
        PostField.money: None,
        PostField.url: None,
        PostField.ip: None,
        PostField.comments: [],
        PostField.post_status: data_type.PostStatus.EXISTS,
        PostField.list_date: None,
        PostField.has_control_code: False,
        PostField.pass_format_check: False,
        PostField.location: None,
        PostField.push_number: None,
        PostField.is_lock: False,
        PostField.full_content: None,
        PostField.is_unconfirmed: False}

    post_author = None
    post_title = None
    if index < 0 or index == 1:
        # 文章被刪除
        log.logger.debug(i18n.post_deleted)
        log.logger.debug('OriScreen', ori_screen)

        cursor_line = [line for line in ori_screen.split(
            '\n') if line.startswith(api.cursor)]

        if len(cursor_line) != 1:
            raise exceptions.UnknownError(ori_screen)

        cursor_line = cursor_line[0]
        log.logger.debug('CursorLine', cursor_line)

        pattern = re.compile(r'[\d]+\/[\d]+')
        pattern_result = pattern.search(cursor_line)
        if pattern_result is None:
            list_date = None
        else:
            list_date = pattern_result.group(0)
            list_date = list_date[-5:]

        pattern = re.compile(r'\[[\w]+\]')
        pattern_result = pattern.search(cursor_line)
        if pattern_result is not None:
            post_del_status = data_type.PostStatus.DELETED_BY_AUTHOR
        else:
            pattern = re.compile(r'<[\w]+>')
            pattern_result = pattern.search(cursor_line)
            post_del_status = data_type.PostStatus.DELETED_BY_MODERATOR

        # > 79843     9/11 -             □ (本文已被吃掉)<
        # > 76060     8/28 -             □ (本文已被刪除) [weida7332]
        # print(f'O=>{CursorLine}<')
        if pattern_result is not None:
            post_author = pattern_result.group(0)[1:-1]
        else:
            post_author = None
            post_del_status = data_type.PostStatus.DELETED_BY_UNKNOWN

        log.logger.debug('ListDate', list_date)
        log.logger.debug('PostAuthor', post_author)
        log.logger.debug('post_del_status', post_del_status)

        post.update({
            PostField.board: board,
            PostField.author: post_author,
            PostField.list_date: list_date,
            PostField.post_status: post_del_status,
            PostField.pass_format_check: True
        })

        return post

    elif index == 0:

        lock_post, post_author, post_title, post_aid, post_web, post_money, list_date, push_number, post_index = \
            _api_util.parse_query_post(
                api,
                ori_screen)

        if lock_post:
            post.update({
                PostField.board: board,
                PostField.aid: post_aid,
                PostField.index: post_index,
                PostField.author: post_author,
                PostField.title: post_title,
                PostField.url: post_web,
                PostField.money: post_money,
                PostField.list_date: list_date,
                PostField.pass_format_check: True,
                PostField.push_number: push_number,
                PostField.is_lock: True})
            return post

    if query:
        post.update({
            PostField.board: board,
            PostField.aid: post_aid,
            PostField.index: post_index,
            PostField.author: post_author,
            PostField.title: post_title,
            PostField.url: post_web,
            PostField.money: post_money,
            PostField.list_date: list_date,
            PostField.pass_format_check: True,
            PostField.push_number: push_number})
        return post

    origin_post, has_control_code = _api_util.get_content(api)

    if origin_post is None:
        log.logger.info(i18n.post_deleted)

        post.update({
            PostField.board: board,
            PostField.aid: post_aid,
            PostField.index: post_index,
            PostField.author: post_author,
            PostField.title: post_title,
            PostField.url: post_web,
            PostField.money: post_money,
            PostField.list_date: list_date,
            PostField.has_control_code: has_control_code,
            PostField.pass_format_check: False,
            PostField.push_number: push_number,
            PostField.is_unconfirmed: api.Unconfirmed
        })
        return post

    post_author_pattern_new = re.compile(r'作者  (.+) 看板')
    post_author_pattern_old = re.compile(r'作者  (.+)')
    board_pattern = re.compile(r'看板  (.+)')

    post_date = None
    post_content = None
    ip = None
    location = None
    push_list = []

    # 格式確認，亂改的我也沒辦法Q_Q
    origin_post_lines = origin_post.split('\n')

    author_line = origin_post_lines[0]

    if board.lower() == 'allpost':
        board_line = author_line[author_line.find(')') + 1:]
        pattern_result = board_pattern.search(board_line)
        if pattern_result is not None:
            board_temp = post_author = pattern_result.group(0)
            board_temp = board_temp[2:].strip()
            if len(board_temp) > 0:
                board = board_temp
                log.logger.debug(i18n.board, board)

    pattern_result = post_author_pattern_new.search(author_line)
    if pattern_result is not None:
        post_author = pattern_result.group(0)
        post_author = post_author[:post_author.rfind(')') + 1]
    else:
        pattern_result = post_author_pattern_old.search(author_line)
        if pattern_result is None:
            log.logger.info(i18n.substandard_post, i18n.author)

            post.update({
                PostField.board: board,
                PostField.aid: post_aid,
                PostField.index: post_index,
                PostField.author: post_author,
                PostField.date: post_date,
                PostField.title: post_title,
                PostField.url: post_web,
                PostField.money: post_money,
                PostField.content: post_content,
                PostField.ip: ip,
                PostField.comments: push_list,
                PostField.list_date: list_date,
                PostField.has_control_code: has_control_code,
                PostField.pass_format_check: False,
                PostField.location: location,
                PostField.push_number: push_number,
                PostField.full_content: origin_post,
                PostField.is_unconfirmed: api.Unconfirmed, })

            return post
        post_author = pattern_result.group(0)
        post_author = post_author[:post_author.rfind(')') + 1]
    post_author = post_author[4:].strip()

    log.logger.debug(i18n.author, post_author)

    post_title_pattern = re.compile(r'標題  (.+)')

    title_line = origin_post_lines[1]
    pattern_result = post_title_pattern.search(title_line)
    if pattern_result is None:
        log.logger.info(i18n.substandard_post, i18n.title)

        post.update({
            PostField.board: board,
            PostField.aid: post_aid,
            PostField.index: post_index,
            PostField.author: post_author,
            PostField.date: post_date,
            PostField.title: post_title,
            PostField.url: post_web,
            PostField.money: post_money,
            PostField.content: post_content,
            PostField.ip: ip,
            PostField.comments: push_list,
            PostField.list_date: list_date,
            PostField.has_control_code: has_control_code,
            PostField.pass_format_check: False,
            PostField.location: location,
            PostField.push_number: push_number,
            PostField.full_content: origin_post,
            PostField.is_unconfirmed: api.Unconfirmed, })

        return post
    post_title = pattern_result.group(0)
    post_title = post_title[4:].strip()

    log.logger.debug(i18n.title, post_title)

    post_date_pattern = re.compile(r'時間  .{24}')
    date_line = origin_post_lines[2]
    pattern_result = post_date_pattern.search(date_line)
    if pattern_result is None:
        log.logger.info(i18n.substandard_post, i18n.date)

        post.update({
            PostField.board: board,
            PostField.aid: post_aid,
            PostField.index: post_index,
            PostField.author: post_author,
            PostField.date: post_date,
            PostField.title: post_title,
            PostField.url: post_web,
            PostField.money: post_money,
            PostField.content: post_content,
            PostField.ip: ip,
            PostField.comments: push_list,
            PostField.list_date: list_date,
            PostField.has_control_code: has_control_code,
            PostField.pass_format_check: False,
            PostField.location: location,
            PostField.push_number: push_number,
            PostField.full_content: origin_post,
            PostField.is_unconfirmed: api.Unconfirmed, })

        return post
    post_date = pattern_result.group(0)
    post_date = post_date[4:].strip()

    log.logger.debug(i18n.date, post_date)

    content_fail = True
    if screens.Target.content_start not in origin_post:
        # print('Type 1')
        content_fail = True
    else:
        post_content = origin_post
        post_content = post_content[
                       post_content.find(screens.Target.content_start) + len(screens.Target.content_start) + 1:]
        # print('Type 2')
        # print(f'PostContent [{PostContent}]')
        for content_end in screens.Target.content_end_list:
            # + 3 = 把 --\n 拿掉
            # print(f'EC [{EC}]')
            if content_end in post_content:
                content_fail = False

                post_content = post_content[:post_content.rfind(content_end) + 3]
                origin_post_lines = origin_post[origin_post.find(content_end):]
                # post_content = post_content.strip()
                origin_post_lines = origin_post_lines.split('\n')
                break

    if content_fail:
        log.logger.info(i18n.substandard_post, i18n.content)

        post.update({
            PostField.board: board,
            PostField.aid: post_aid,
            PostField.index: post_index,
            PostField.author: post_author,
            PostField.date: post_date,
            PostField.title: post_title,
            PostField.url: post_web,
            PostField.money: post_money,
            PostField.content: post_content,
            PostField.ip: ip,
            PostField.comments: push_list,
            PostField.list_date: list_date,
            PostField.has_control_code: has_control_code,
            PostField.pass_format_check: False,
            PostField.location: location,
            PostField.push_number: push_number,
            PostField.full_content: origin_post,
            PostField.is_unconfirmed: api.Unconfirmed, })

        return post

    log.logger.debug(i18n.content, post_content)

    info_lines = [line for line in origin_post_lines if line.startswith('※') or line.startswith('◆')]

    pattern = re.compile(r'[\d]+\.[\d]+\.[\d]+\.[\d]+')
    pattern_p2 = re.compile(r'[\d]+-[\d]+-[\d]+-[\d]+')
    for line in reversed(info_lines):

        log.logger.debug('IP Line', line)

        # type 1
        # ※ 編輯: CodingMan (111.243.146.98 臺灣)
        # ※ 發信站: 批踢踢實業坊(ptt.cc), 來自: 111.243.146.98 (臺灣)

        # type 2
        # ※ 發信站: 批踢踢實業坊(ptt.cc), 來自: 116.241.32.178
        # ※ 編輯: kill77845 (114.136.55.237), 12/08/2018 16:47:59

        # type 3
        # ※ 發信站: 批踢踢實業坊(ptt.cc)
        # ◆ From: 211.20.78.69
        # ※ 編輯: JCC             來自: 211.20.78.69         (06/20 10:22)
        # ※ 編輯: JCC (118.163.28.150), 12/03/2015 14:25:35

        pattern_result = pattern.search(line)
        if pattern_result is not None:
            ip = pattern_result.group(0)
            location_temp = line[line.find(ip) + len(ip):].strip()
            location_temp = location_temp.replace('(', '')
            location_temp = location_temp[:location_temp.rfind(')')]
            location_temp = location_temp.strip()
            # print(f'=>[{LocationTemp}]')
            if ' ' not in location_temp and len(location_temp) > 0:
                location = location_temp

                log.logger.debug('Location', location)
            break

        pattern_result = pattern_p2.search(line)
        if pattern_result is not None:
            ip = pattern_result.group(0)
            ip = ip.replace('-', '.')
            # print(f'IP -> [{IP}]')
            break
    if api.config.host == data_type.HOST.PTT1:
        if ip is None:
            log.logger.info(i18n.substandard_post, ip)

            post.update({
                PostField.board: board,
                PostField.aid: post_aid,
                PostField.index: post_index,
                PostField.author: post_author,
                PostField.date: post_date,
                PostField.title: post_title,
                PostField.url: post_web,
                PostField.money: post_money,
                PostField.content: post_content,
                PostField.ip: ip,
                PostField.comments: push_list,
                PostField.list_date: list_date,
                PostField.has_control_code: has_control_code,
                PostField.pass_format_check: False,
                PostField.location: location,
                PostField.push_number: push_number,
                PostField.full_content: origin_post,
                PostField.is_unconfirmed: api.Unconfirmed, })

            return post
    log.logger.debug('IP', ip)

    push_author_pattern = re.compile(r'[推|噓|→] [\w| ]+:')
    push_date_pattern = re.compile(r'[\d]+/[\d]+ [\d]+:[\d]+')
    push_ip_pattern = re.compile(r'[\d]+\.[\d]+\.[\d]+\.[\d]+')

    push_list = []

    for line in origin_post_lines:
        if line.startswith('推'):
            comment_type = data_type.CommentType.PUSH
        elif line.startswith('噓 '):
            comment_type = data_type.CommentType.BOO
        elif line.startswith('→ '):
            comment_type = data_type.CommentType.ARROW
        else:
            continue

        result = push_author_pattern.search(line)
        if result is None:
            # 不符合推文格式
            continue
        push_author = result.group(0)[2:-1].strip()

        log.logger.debug(i18n.comment_id, push_author)

        result = push_date_pattern.search(line)
        if result is None:
            continue
        push_date = result.group(0)
        log.logger.debug(i18n.comment_date, push_date)

        comment_ip = None
        result = push_ip_pattern.search(line)
        if result is not None:
            comment_ip = result.group(0)
            log.logger.debug(f'{i18n.comment} ip', comment_ip)

        push_content = line[line.find(push_author) + len(push_author):]
        # PushContent = PushContent.replace(PushDate, '')

        if api.config.host == data_type.HOST.PTT1:
            push_content = push_content[:push_content.rfind(push_date)]
        else:
            # → CodingMan:What is Ptt?                                       推 10/04 13:25
            push_content = push_content[:push_content.rfind(push_date) - 2]
        if comment_ip is not None:
            push_content = push_content.replace(comment_ip, '')
        push_content = push_content[push_content.find(':') + 1:].strip()

        log.logger.debug(i18n.comment_content, push_content)

        current_push = {
            CommentField.type: comment_type,
            CommentField.author: push_author,
            CommentField.content: push_content,
            CommentField.ip: comment_ip,
            CommentField.time: push_date}
        push_list.append(current_push)

    post.update({
        PostField.board: board,
        PostField.aid: post_aid,
        PostField.index: post_index,
        PostField.author: post_author,
        PostField.date: post_date,
        PostField.title: post_title,
        PostField.url: post_web,
        PostField.money: post_money,
        PostField.content: post_content,
        PostField.ip: ip,
        PostField.comments: push_list,
        PostField.list_date: list_date,
        PostField.has_control_code: has_control_code,
        PostField.pass_format_check: True,
        PostField.location: location,
        PostField.push_number: push_number,
        PostField.full_content: origin_post,
        PostField.is_unconfirmed: api.Unconfirmed})

    return post
