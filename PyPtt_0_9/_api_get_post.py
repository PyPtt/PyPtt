import re

try:
    from . import data_type
    from . import i18n
    from . import connect_core
    from . import log
    from . import screens
    from . import exceptions
    from . import command
    from . import _api_util
except ModuleNotFoundError:
    import data_type
    import i18n
    import connect_core
    import log
    import screens
    import exceptions
    import command
    import _api_util


def get_post(
        api,
        board: str,
        post_aid: str = None,
        post_index: int = 0,
        search_type: int = 0,
        search_condition: str = None,
        search_list: list = None,
        query: bool = False) -> data_type.PostInfo:
    api._goto_board(board)

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
            cmd_list.append(command.Enter)

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
                cmd_list.append(command.Enter)

        cmd_list.append(str(max(1, post_index - 100)))
        cmd_list.append(command.Enter)
        cmd_list.append(str(post_index))

    cmd_list.append(command.Enter)
    cmd_list.append(command.QueryPost)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            [
                i18n.CatchPost,
                i18n.Success,
            ],
            screens.Target.QueryPost,
            break_detect=True,
            refresh=False,
            log_level=log.level.DEBUG),
        connect_core.TargetUnit(
            [
                i18n.PostDeleted,
                i18n.Success,
            ],
            screens.Target.InBoard,
            break_detect=True,
            log_level=log.level.DEBUG),
        connect_core.TargetUnit(
            i18n.NoSuchBoard,
            screens.Target.MainMenu_Exiting,
            exceptions_=exceptions.NoSuchBoard(api.config, board)),
    ]

    index = api.connect_core.send(cmd, target_list)
    ori_screen = api.connect_core.get_screen_queue()[-1]

    post_author = None
    post_title = None
    if index < 0 or index == 1:
        # 文章被刪除
        log.log(api.config, log.level.DEBUG, i18n.PostDeleted)

        log.show_value(
            api.config,
            log.level.DEBUG,
            'OriScreen',
            ori_screen)

        cursor_line = [line for line in ori_screen.split(
            '\n') if line.startswith(api.cursor)]

        if len(cursor_line) != 1:
            raise exceptions.UnknownError(ori_screen)

        cursor_line = cursor_line[0]
        log.show_value(
            api.config,
            log.level.DEBUG,
            'CursorLine',
            cursor_line)

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

        log.show_value(api.config, log.level.DEBUG, 'ListDate', list_date)
        log.show_value(api.config, log.level.DEBUG,
                       'PostAuthor', post_author)
        log.show_value(api.config, log.level.DEBUG,
                       'post_del_status', post_del_status)

        return data_type.PostInfo(
            board=board,
            author=post_author,
            list_date=list_date,
            delete_status=post_del_status,
            format_check=True)

    elif index == 0:

        lock_post, post_author, post_title, post_aid, post_web, post_money, list_date, push_number, post_index = \
            _api_util.parse_query_post(
                api,
                ori_screen)

        if lock_post:
            post = data_type.PostInfo(
                board=board,
                aid=post_aid,
                index=post_index,
                author=post_author,
                title=post_title,
                web_url=post_web,
                money=post_money,
                list_date=list_date,
                format_check=True,
                push_number=push_number,
                lock=True)

            return post

    if query:
        post = data_type.PostInfo(
            board=board,
            aid=post_aid,
            index=post_index,
            author=post_author,
            title=post_title,
            web_url=post_web,
            money=post_money,
            list_date=list_date,
            format_check=True,
            push_number=push_number)
        return post

    origin_post, has_control_code = _api_util.get_content(api)

    if origin_post is None:
        post = data_type.PostInfo(
            board=board,
            aid=post_aid,
            index=post_index,
            author=post_author,
            title=post_title,
            web_url=post_web,
            money=post_money,
            list_date=list_date,
            control_code=has_control_code,
            format_check=False,
            push_number=push_number,
            unconfirmed=api.Unconfirmed)
        return post

    # print('=' * 20)
    # print(origin_post)
    # print('=' * 20)

    content_start = '───────────────────────────────────────'
    content_end = list()
    content_end.append('--\n※ 發信站: 批踢踢實業坊')
    content_end.append('--\n※ 發信站: 批踢踢兔(ptt2.cc)')
    content_end.append('--\n※ 發信站: 新批踢踢(ptt2.twbbs.org.tw)')

    post_author_pattern_new = re.compile('作者  (.+) 看板')
    post_author_pattern_old = re.compile('作者  (.+)')
    board_pattern = re.compile('看板  (.+)')

    post_date = None
    post_content = list()
    ip = None
    location = None
    push_list = list()

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
                log.show_value(
                    api.config,
                    log.level.DEBUG,
                    i18n.Board,
                    board
                )
    pattern_result = post_author_pattern_new.search(author_line)
    if pattern_result is not None:
        post_author = pattern_result.group(0)
        post_author = post_author[:post_author.rfind(')') + 1]
    else:
        pattern_result = post_author_pattern_old.search(author_line)
        if pattern_result is None:
            log.show_value(
                api.config,
                log.level.DEBUG,
                i18n.SubstandardPost,
                i18n.Author
            )
            post = data_type.PostInfo(
                board=board,
                aid=post_aid,
                index=post_index,
                author=post_author,
                date=post_date,
                title=post_title,
                web_url=post_web,
                money=post_money,
                content=post_content,
                ip=ip,
                push_list=push_list,
                list_date=list_date,
                control_code=has_control_code,
                format_check=False,
                location=location,
                push_number=push_number,
                origin_post=origin_post,
                unconfirmed=api.Unconfirmed,
            )
            return post
        post_author = pattern_result.group(0)
        post_author = post_author[:post_author.rfind(')') + 1]
    post_author = post_author[4:].strip()

    log.show_value(
        api.config,
        log.level.DEBUG,
        i18n.Author,
        post_author)

    post_title_pattern = re.compile('標題  (.+)')

    title_line = origin_post_lines[1]
    pattern_result = post_title_pattern.search(title_line)
    if pattern_result is None:
        log.show_value(
            api.config,
            log.level.DEBUG,
            i18n.SubstandardPost,
            i18n.Title)

        post = data_type.PostInfo(
            board=board,
            aid=post_aid,
            index=post_index,
            author=post_author,
            date=post_date,
            title=post_title,
            web_url=post_web,
            money=post_money,
            content=post_content,
            ip=ip,
            push_list=push_list,
            list_date=list_date,
            control_code=has_control_code,
            format_check=False,
            location=location,
            push_number=push_number,
            origin_post=origin_post,
            unconfirmed=api.Unconfirmed)
        return post
    post_title = pattern_result.group(0)
    post_title = post_title[4:].strip()

    log.show_value(
        api.config,
        log.level.DEBUG,
        i18n.Title,
        post_title)

    post_date_pattern = re.compile('時間  .{24}')
    date_line = origin_post_lines[2]
    pattern_result = post_date_pattern.search(date_line)
    if pattern_result is None:
        log.show_value(
            api.config,
            log.level.DEBUG,
            i18n.SubstandardPost,
            i18n.Date
        )
        post = data_type.PostInfo(
            board=board,
            aid=post_aid,
            index=post_index,
            author=post_author,
            date=post_date,
            title=post_title,
            web_url=post_web,
            money=post_money,
            content=post_content,
            ip=ip,
            push_list=push_list,
            list_date=list_date,
            control_code=has_control_code,
            format_check=False,
            location=location,
            push_number=push_number,
            origin_post=origin_post,
            unconfirmed=api.Unconfirmed,
        )
        return post
    post_date = pattern_result.group(0)
    post_date = post_date[4:].strip()

    log.show_value(
        api.config,
        log.level.DEBUG,
        i18n.Date,
        post_date
    )

    content_fail = True
    if content_start not in origin_post:
        # print('Type 1')
        content_fail = True
    else:
        post_content = origin_post
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
                origin_post_lines = origin_post[origin_post.find(EC):]
                # post_content = post_content.strip()
                origin_post_lines = origin_post_lines.split('\n')
                break

    if content_fail:
        log.show_value(
            api.config,
            log.level.DEBUG,
            i18n.SubstandardPost,
            i18n.Content
        )
        post = data_type.PostInfo(
            board=board,
            aid=post_aid,
            index=post_index,
            author=post_author,
            date=post_date,
            title=post_title,
            web_url=post_web,
            money=post_money,
            content=post_content,
            ip=ip,
            push_list=push_list,
            list_date=list_date,
            control_code=has_control_code,
            format_check=False,
            location=location,
            push_number=push_number,
            origin_post=origin_post,
            unconfirmed=api.Unconfirmed,
        )
        return post

    log.show_value(
        api.config,
        log.level.DEBUG,
        i18n.Content,
        post_content
    )

    info_lines = [
        line for line in origin_post_lines if line.startswith('※') or
                                              line.startswith('◆')
    ]

    pattern = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')
    pattern_p2 = re.compile('[\d]+-[\d]+-[\d]+-[\d]+')
    for line in reversed(info_lines):
        log.show_value(
            api.config,
            log.level.DEBUG,
            'IP Line',
            line
        )

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
                log.show_value(api.config, log.level.DEBUG,
                               'Location', location)
            break

        pattern_result = pattern_p2.search(line)
        if pattern_result is not None:
            ip = pattern_result.group(0)
            ip = ip.replace('-', '.')
            # print(f'IP -> [{IP}]')
            break
    if api.config.host == data_type.host_type.PTT1:
        if ip is None:
            log.show_value(
                api.config,
                log.level.DEBUG,
                i18n.SubstandardPost,
                'IP'
            )
            post = data_type.PostInfo(
                board=board,
                aid=post_aid,
                index=post_index,
                author=post_author,
                date=post_date,
                title=post_title,
                web_url=post_web,
                money=post_money,
                content=post_content,
                ip=ip,
                push_list=push_list,
                list_date=list_date,
                control_code=has_control_code,
                format_check=False,
                location=location,
                push_number=push_number,
                origin_post=origin_post,
                unconfirmed=api.Unconfirmed,
            )
            return post
    log.show_value(api.config, log.level.DEBUG, 'IP', ip)

    push_author_pattern = re.compile('[推|噓|→] [\w| ]+:')
    push_date_pattern = re.compile('[\d]+/[\d]+ [\d]+:[\d]+')
    push_ip_pattern = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')

    push_list = list()

    for line in origin_post_lines:
        if line.startswith('推'):
            push_type = data_type.push_type.PUSH
        elif line.startswith('噓 '):
            push_type = data_type.push_type.BOO
        elif line.startswith('→ '):
            push_type = data_type.push_type.ARROW
        else:
            continue

        result = push_author_pattern.search(line)
        if result is None:
            # 不符合推文格式
            continue
        push_author = result.group(0)[2:-1].strip()
        log.show_value(api.config, log.level.DEBUG, [
            i18n.Push,
            i18n.ID,
        ],
                       push_author
                       )

        result = push_date_pattern.search(line)
        if result is None:
            continue
        push_date = result.group(0)
        log.show_value(api.config, log.level.DEBUG, [
            i18n.Push,
            i18n.Date,
        ],
                       push_date
                       )

        push_ip = None
        result = push_ip_pattern.search(line)
        if result is not None:
            push_ip = result.group(0)
            log.show_value(
                api.config,
                log.level.DEBUG,
                [
                    i18n.Push,
                    'IP',
                ],
                push_ip
            )

        push_content = line[
                       line.find(push_author) + len(push_author):
                       ]
        # PushContent = PushContent.replace(PushDate, '')

        if api.config.host == data_type.host_type.PTT1:
            push_content = push_content[
                           :push_content.rfind(push_date)
                           ]
        else:
            # → CodingMan:What is Ptt?                                       推 10/04 13:25
            push_content = push_content[
                           :push_content.rfind(push_date) - 2
                           ]
        if push_ip is not None:
            push_content = push_content.replace(push_ip, '')
        push_content = push_content[
                       push_content.find(':') + 1:
                       ].strip()
        log.show_value(
            api.config,
            log.level.DEBUG, [
                i18n.Push,
                i18n.Content,
            ],
            push_content
        )

        current_push = data_type.PushInfo(
            push_type,
            push_author,
            push_content,
            push_ip,
            push_date
        )
        push_list.append(current_push)

    post = data_type.PostInfo(
        board=board,
        aid=post_aid,
        index=post_index,
        author=post_author,
        date=post_date,
        title=post_title,
        web_url=post_web,
        money=post_money,
        content=post_content,
        ip=ip,
        push_list=push_list,
        list_date=list_date,
        control_code=has_control_code,
        format_check=True,
        location=location,
        push_number=push_number,
        origin_post=origin_post,
        unconfirmed=api.Unconfirmed,
    )
    return post
