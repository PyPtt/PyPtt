import re

from SingleLog.log import Logger

from . import _api_util
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import screens
from .data_type import Article, Comment


def get_article(
        api,
        board: str,
        post_aid: str = None,
        post_index: int = 0,
        search_type: int = 0,
        search_condition: str = None,
        search_list: list = None,
        query: bool = False) -> dict:
    api._goto_board(board)

    logger = Logger('get_article', Logger.INFO)

    cmd_list = list()

    if post_aid is not None:
        cmd_list.append('#' + post_aid)

    elif post_index != 0:
        if search_condition is not None:
            if search_type == data_type.post_search_type.KEYWORD:
                cmd_list.append('/')
            elif search_type == data_type.post_search_type.AUTHOR:
                cmd_list.append('a')
            elif search_type == data_type.post_search_type.PUSH:
                cmd_list.append('Z')
            elif search_type == data_type.post_search_type.MARK:
                cmd_list.append('G')
            elif search_type == data_type.post_search_type.MONEY:
                cmd_list.append('A')

            cmd_list.append(search_condition)
            cmd_list.append(command.enter)

        if search_list is not None:
            for search_type_, search_condition_ in search_list:

                if search_type_ == data_type.post_search_type.KEYWORD:
                    cmd_list.append('/')
                elif search_type_ == data_type.post_search_type.AUTHOR:
                    cmd_list.append('a')
                elif search_type_ == data_type.post_search_type.PUSH:
                    cmd_list.append('Z')
                elif search_type_ == data_type.post_search_type.MARK:
                    cmd_list.append('G')
                elif search_type_ == data_type.post_search_type.MONEY:
                    cmd_list.append('A')

                cmd_list.append(search_condition_)
                cmd_list.append(command.enter)

        cmd_list.append(str(max(1, post_index - 100)))
        cmd_list.append(command.enter)
        cmd_list.append(str(post_index))

    cmd_list.append(command.enter)
    cmd_list.append(command.query_post)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.query_post_success,
            screens.Target.QueryPost,
            break_detect=True,
            refresh=False,
            log_level=Logger.DEBUG),
        connect_core.TargetUnit(
            i18n.post_deleted,
            screens.Target.InBoard,
            break_detect=True,
            log_level=Logger.DEBUG),
        connect_core.TargetUnit(
            i18n.no_such_board,
            screens.Target.MainMenu_Exiting,
            exceptions_=exceptions.NoSuchBoard(api.config, board)),
    ]

    index = api.connect_core.send(cmd, target_list)
    ori_screen = api.connect_core.get_screen_queue()[-1]

    article = {
        Article.board: None,
        Article.aid: None,
        Article.index: None,
        Article.author: None,
        Article.date: None,
        Article.title: None,
        Article.content: None,
        Article.money: None,
        Article.web_url: None,
        Article.ip: None,
        Article.push_list: [],
        Article.delete_status: None,
        Article.list_date: None,
        Article.is_control_code: False,
        Article.pass_format_check: False,
        Article.location: None,
        Article.push_number: None,
        Article.is_lock: False,
        Article.origin_post: None,
        Article.is_unconfirmed: False}

    post_author = None
    post_title = None
    if index < 0 or index == 1:
        # 文章被刪除
        logger.debug(i18n.post_deleted)
        logger.debug('OriScreen', ori_screen)

        cursor_line = [line for line in ori_screen.split(
            '\n') if line.startswith(api.cursor)]

        if len(cursor_line) != 1:
            raise exceptions.UnknownError(ori_screen)

        cursor_line = cursor_line[0]
        logger.debug('CursorLine', cursor_line)

        pattern = re.compile('[\d]+\/[\d]+')
        pattern_result = pattern.search(cursor_line)
        if pattern_result is None:
            list_date = None
        else:
            list_date = pattern_result.group(0)
            list_date = list_date[-5:]

        pattern = re.compile('\[[\w]+\]')
        pattern_result = pattern.search(cursor_line)
        if pattern_result is not None:
            post_del_status = data_type.post_delete_status.AUTHOR
        else:
            pattern = re.compile('<[\w]+>')
            pattern_result = pattern.search(cursor_line)
            post_del_status = data_type.post_delete_status.MODERATOR

        # > 79843     9/11 -             □ (本文已被吃掉)<
        # > 76060     8/28 -             □ (本文已被刪除) [weida7332]
        # print(f'O=>{CursorLine}<')
        if pattern_result is not None:
            post_author = pattern_result.group(0)[1:-1]
        else:
            post_author = None
            post_del_status = data_type.post_delete_status.UNKNOWN

        logger.debug('ListDate', list_date)
        logger.debug('PostAuthor', post_author)
        logger.debug('post_del_status', post_del_status)

        article.update({
            Article.board: board,
            Article.author: post_author,
            Article.list_date: list_date,
            Article.delete_status: post_del_status,
            Article.pass_format_check: True
        })

        return article

    elif index == 0:

        lock_post, post_author, post_title, post_aid, post_web, post_money, list_date, push_number, post_index = \
            _api_util.parse_query_post(
                api,
                ori_screen)

        if lock_post:
            article.update({
                Article.board: board,
                Article.aid: post_aid,
                Article.index: post_index,
                Article.author: post_author,
                Article.title: post_title,
                Article.web_url: post_web,
                Article.money: post_money,
                Article.list_date: list_date,
                Article.pass_format_check: True,
                Article.push_number: push_number,
                Article.lock: True})
            return article

    if query:
        article.update({
            Article.board: board,
            Article.aid: post_aid,
            Article.index: post_index,
            Article.author: post_author,
            Article.title: post_title,
            Article.web_url: post_web,
            Article.money: post_money,
            Article.list_date: list_date,
            Article.pass_format_check: True,
            Article.push_number: push_number})
        return article

    origin_article, has_control_code = _api_util.get_content(api)

    if origin_article is None:
        article.update({
            Article.board: board,
            Article.aid: post_aid,
            Article.index: post_index,
            Article.author: post_author,
            Article.title: post_title,
            Article.web_url: post_web,
            Article.money: post_money,
            Article.list_date: list_date,
            Article.is_control_code: has_control_code,
            Article.pass_format_check: False,
            Article.push_number: push_number,
            Article.is_unconfirmed: api.Unconfirmed
        })
        return article

    # print('=' * 20)
    # print(origin_article)
    # print('=' * 20)

    content_start = '─── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──'
    content_end = list()
    content_end.append('--\n※ 發信站: 批踢踢實業坊')
    content_end.append('--\n※ 發信站: 批踢踢兔(ptt2.cc)')
    content_end.append('--\n※ 發信站: 新批踢踢(ptt2.twbbs.org.tw)')

    post_author_pattern_new = re.compile('作者  (.+) 看板')
    post_author_pattern_old = re.compile('作者  (.+)')
    board_pattern = re.compile('看板  (.+)')

    post_date = None
    post_content = None
    ip = None
    location = None
    push_list = list()

    # 格式確認，亂改的我也沒辦法Q_Q
    origin_post_lines = origin_article.split('\n')

    author_line = origin_post_lines[0]

    if board.lower() == 'allpost':
        board_line = author_line[author_line.find(')') + 1:]
        pattern_result = board_pattern.search(board_line)
        if pattern_result is not None:
            board_temp = post_author = pattern_result.group(0)
            board_temp = board_temp[2:].strip()
            if len(board_temp) > 0:
                board = board_temp
                logger.debug(i18n.board, board)

    pattern_result = post_author_pattern_new.search(author_line)
    if pattern_result is not None:
        post_author = pattern_result.group(0)
        post_author = post_author[:post_author.rfind(')') + 1]
    else:
        pattern_result = post_author_pattern_old.search(author_line)
        if pattern_result is None:
            logger.debug(i18n.substandard_post, i18n.author)

            article.update({
                board: board,
                Article.aid: post_aid,
                Article.index: post_index,
                Article.author: post_author,
                Article.date: post_date,
                Article.title: post_title,
                Article.web_url: post_web,
                Article.money: post_money,
                Article.content: post_content,
                Article.ip: ip,
                Article.push_list: push_list,
                Article.list_date: list_date,
                Article.is_control_code: has_control_code,
                Article.pass_format_check: False,
                Article.location: location,
                Article.push_number: push_number,
                Article.origin_post: origin_article,
                Article.is_unconfirmed: api.Unconfirmed, })

            return article
        post_author = pattern_result.group(0)
        post_author = post_author[:post_author.rfind(')') + 1]
    post_author = post_author[4:].strip()

    logger.debug(i18n.author, post_author)

    post_title_pattern = re.compile('標題  (.+)')

    title_line = origin_post_lines[1]
    pattern_result = post_title_pattern.search(title_line)
    if pattern_result is None:
        logger.debug(i18n.substandard_post, i18n.title)

        article.update({
            Article.board: board,
            Article.aid: post_aid,
            Article.index: post_index,
            Article.author: post_author,
            Article.date: post_date,
            Article.title: post_title,
            Article.web_url: post_web,
            Article.money: post_money,
            Article.content: post_content,
            Article.ip: ip,
            Article.push_list: push_list,
            Article.list_date: list_date,
            Article.is_control_code: has_control_code,
            Article.pass_format_check: False,
            Article.location: location,
            Article.push_number: push_number,
            Article.origin_post: origin_article,
            Article.is_unconfirmed: api.Unconfirmed, })

        return article
    post_title = pattern_result.group(0)
    post_title = post_title[4:].strip()

    logger.debug(i18n.title, post_title)

    post_date_pattern = re.compile('時間  .{24}')
    date_line = origin_post_lines[2]
    pattern_result = post_date_pattern.search(date_line)
    if pattern_result is None:
        logger.debug(i18n.substandard_post, i18n.date)

        article.update({
            Article.board: board,
            Article.aid: post_aid,
            Article.index: post_index,
            Article.author: post_author,
            Article.date: post_date,
            Article.title: post_title,
            Article.web_url: post_web,
            Article.money: post_money,
            Article.content: post_content,
            Article.ip: ip,
            Article.push_list: push_list,
            Article.list_date: list_date,
            Article.is_control_code: has_control_code,
            Article.pass_format_check: False,
            Article.location: location,
            Article.push_number: push_number,
            Article.origin_post: origin_article,
            Article.is_unconfirmed: api.Unconfirmed, })

        return article
    post_date = pattern_result.group(0)
    post_date = post_date[4:].strip()

    logger.debug(i18n.date, post_date)

    content_fail = True
    if content_start not in origin_article:
        # print('Type 1')
        content_fail = True
    else:
        post_content = origin_article
        post_content = post_content[
                       post_content.find(content_start) +
                       len(content_start) + 1:
                       ]
        # print('Type 2')
        # print(f'PostContent [{PostContent}]')
        for EC in content_end:
            # + 3 = 把 --\n 拿掉
            # print(f'EC [{EC}]')
            if EC in post_content:
                content_fail = False

                post_content = post_content[
                               :post_content.rfind(EC) + 3
                               ]
                origin_post_lines = origin_article[origin_article.find(EC):]
                # post_content = post_content.strip()
                origin_post_lines = origin_post_lines.split('\n')
                break

    if content_fail:
        logger.debug(i18n.substandard_post, i18n.content)

        article.update({
            Article.board: board,
            Article.aid: post_aid,
            Article.index: post_index,
            Article.author: post_author,
            Article.date: post_date,
            Article.title: post_title,
            Article.web_url: post_web,
            Article.money: post_money,
            Article.content: post_content,
            Article.ip: ip,
            Article.push_list: push_list,
            Article.list_date: list_date,
            Article.is_control_code: has_control_code,
            Article.pass_format_check: False,
            Article.location: location,
            Article.push_number: push_number,
            Article.origin_post: origin_article,
            Article.is_unconfirmed: api.Unconfirmed, })

        return article

    logger.debug(i18n.content, post_content)

    info_lines = [
        line for line in origin_post_lines if line.startswith('※') or
                                              line.startswith('◆')
    ]

    pattern = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')
    pattern_p2 = re.compile('[\d]+-[\d]+-[\d]+-[\d]+')
    for line in reversed(info_lines):

        logger.debug('IP Line', line)

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

                logger.debug('Location', location)
            break

        pattern_result = pattern_p2.search(line)
        if pattern_result is not None:
            ip = pattern_result.group(0)
            ip = ip.replace('-', '.')
            # print(f'IP -> [{IP}]')
            break
    if api.config.host == data_type.HOST.PTT1:
        if ip is None:
            logger.debug(i18n.substandard_post, ip)

            article.update({
                Article.board: board,
                Article.aid: post_aid,
                Article.index: post_index,
                Article.author: post_author,
                Article.date: post_date,
                Article.title: post_title,
                Article.web_url: post_web,
                Article.money: post_money,
                Article.content: post_content,
                Article.ip: ip,
                Article.push_list: push_list,
                Article.list_date: list_date,
                Article.is_control_code: has_control_code,
                Article.pass_format_check: False,
                Article.location: location,
                Article.push_number: push_number,
                Article.origin_post: origin_article,
                Article.is_unconfirmed: api.Unconfirmed, })

            return article
    logger.debug('IP', ip)

    push_author_pattern = re.compile('[推|噓|→] [\w| ]+:')
    push_date_pattern = re.compile('[\d]+/[\d]+ [\d]+:[\d]+')
    push_ip_pattern = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')

    push_list = list()

    for line in origin_post_lines:
        if line.startswith('推'):
            comment_type = data_type.push_type.PUSH
        elif line.startswith('噓 '):
            comment_type = data_type.push_type.BOO
        elif line.startswith('→ '):
            comment_type = data_type.push_type.ARROW
        else:
            continue

        result = push_author_pattern.search(line)
        if result is None:
            # 不符合推文格式
            continue
        push_author = result.group(0)[2:-1].strip()

        logger.debug(i18n.comment_id, push_author)

        result = push_date_pattern.search(line)
        if result is None:
            continue
        push_date = result.group(0)
        logger.debug(i18n.comment_date, push_date)

        comment_ip = None
        result = push_ip_pattern.search(line)
        if result is not None:
            comment_ip = result.group(0)
            logger.debug(f'{i18n.comment} ip', comment_ip)

        push_content = line[
                       line.find(push_author) + len(push_author):
                       ]
        # PushContent = PushContent.replace(PushDate, '')

        if api.config.host == data_type.HOST.PTT1:
            push_content = push_content[
                           :push_content.rfind(push_date)
                           ]
        else:
            # → CodingMan:What is Ptt?                                       推 10/04 13:25
            push_content = push_content[
                           :push_content.rfind(push_date) - 2
                           ]
        if comment_ip is not None:
            push_content = push_content.replace(comment_ip, '')
        push_content = push_content[
                       push_content.find(':') + 1:
                       ].strip()

        logger.debug(i18n.comment_content, push_content)

        current_push = {
            Comment.type: comment_type,
            Comment.author: push_author,
            Comment.content: push_content,
            Comment.ip: comment_ip,
            Comment.time: push_date}
        push_list.append(current_push)

    article.update({
        Article.board: board,
        Article.aid: post_aid,
        Article.index: post_index,
        Article.author: post_author,
        Article.date: post_date,
        Article.title: post_title,
        Article.web_url: post_web,
        Article.money: post_money,
        Article.content: post_content,
        Article.ip: ip,
        Article.push_list: push_list,
        Article.list_date: list_date,
        Article.is_control_code: has_control_code,
        Article.pass_format_check: True,
        Article.location: location,
        Article.push_number: push_number,
        Article.origin_post: origin_article,
        Article.is_unconfirmed: api.Unconfirmed})

    return article
