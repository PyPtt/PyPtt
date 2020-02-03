import re

try:
    from . import data_type
    from . import i18n
    from . import connect_core
    from . import log
    from . import screens
    from . import exceptions
    from . import command
except ModuleNotFoundError:
    import data_type
    import i18n
    import connect_core
    import log
    import screens
    import exceptions
    import command


def get_post(
        api,
        board: str,
        post_aid: str = None,
        post_index: int = 0,
        search_type: int = 0,
        search_condition: str = None,
        query: bool = False) -> data_type.PostInfo:
    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(command.Enter)
    cmd_list.append(command.Ctrl_C * 2)
    cmd_list.append(command.Space)

    if post_aid is not None:
        cmd_list.append('#' + post_aid)

    elif post_index != 0:
        if search_condition is not None:
            if search_type == data_type.PostSearchType.KEYWORD:
                cmd_list.append('/')
            elif search_type == data_type.PostSearchType.AUTHOR:
                cmd_list.append('a')
            elif search_type == data_type.PostSearchType.PUSH:
                cmd_list.append('Z')
            elif search_type == data_type.PostSearchType.MARK:
                cmd_list.append('G')
            elif search_type == data_type.PostSearchType.MONEY:
                cmd_list.append('A')

            cmd_list.append(search_condition)
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
            log_level=log.Level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                i18n.PostDeleted,
                i18n.Success,
            ],
            screens.Target.InBoard,
            break_detect=True,
            log_level=log.Level.DEBUG
        ),
        connect_core.TargetUnit(
            i18n.NoSuchBoard,
            screens.Target.MainMenu_Exiting,
            exceptions=exceptions.NoSuchBoard(api.config, board)
        ),
    ]

    index = api.connect_core.send(cmd, target_list)
    ori_screen = api.connect_core.get_screen_queue()[-1]

    post_author = None
    post_title = None
    if index < 0 or index == 1:
        # 文章被刪除
        log.log(api.config, log.Level.DEBUG, i18n.PostDeleted)

        log.show_value(
            api.config,
            log.Level.DEBUG,
            'OriScreen',
            ori_screen
        )

        cursor_line = [line for line in ori_screen.split(
            '\n') if line.startswith(api.cursor)]

        if len(cursor_line) != 1:
            raise exceptions.UnknownError(ori_screen)

        cursor_line = cursor_line[0]
        log.show_value(
            api.config,
            log.Level.DEBUG,
            'CursorLine',
            cursor_line
        )

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
            post_del_status = data_type.PostDeleteStatus.ByAuthor
        else:
            pattern = re.compile('<[\w]+>')
            pattern_result = pattern.search(cursor_line)
            post_del_status = data_type.PostDeleteStatus.ByModerator

        # > 79843     9/11 -             □ (本文已被吃掉)<
        # > 76060     8/28 -             □ (本文已被刪除) [weida7332]
        # print(f'O=>{CursorLine}<')
        if pattern_result is not None:
            post_author = pattern_result.group(0)[1:-1]
        else:
            post_author = None
            post_del_status = data_type.PostDeleteStatus.ByUnknown

        log.show_value(api.config, log.Level.DEBUG, 'ListDate', list_date)
        log.show_value(api.config, log.Level.DEBUG,
                      'PostAuthor', post_author)
        log.show_value(api.config, log.Level.DEBUG,
                      'post_del_status', post_del_status)

        return data_type.PostInfo(
            board=board,
            author=post_author,
            list_date=list_date,
            delete_status=post_del_status,
            format_check=True
        )

    elif index == 0:

        lock_post = False
        cursor_line = [line for line in ori_screen.split(
            '\n') if line.startswith(api.cursor)][0]
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

        ori_screen_temp = ori_screen[ori_screen.find('┌──────────'):]
        ori_screen_temp = ori_screen_temp[:ori_screen_temp.find(
            '└─────────────')
                          ]

        aid_line = [line for line in ori_screen.split(
            '\n') if line.startswith('│ 文章代碼(AID)')]

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

        push_number = cursor_line
        # print(f'2>{push_number}<')
        push_number = push_number[7:11]
        # print(PushNumber)
        push_number = push_number.split(' ')
        # print(PushNumber)
        push_number = list(filter(None, push_number))
        # print(PushNumber)

        if len(push_number) == 0:
            push_number = None
        else:
            push_number = push_number[-1]
            # print(PushNumber)

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
        log.show_value(api.config, log.Level.DEBUG,
                      'PostAuthor', post_author)
        log.show_value(api.config, log.Level.DEBUG, 'PostTitle', post_title)
        log.show_value(api.config, log.Level.DEBUG, 'PostAID', post_aid)
        log.show_value(api.config, log.Level.DEBUG, 'PostWeb', post_web)
        log.show_value(api.config, log.Level.DEBUG, 'PostMoney', post_money)
        log.show_value(api.config, log.Level.DEBUG, 'ListDate', list_date)
        log.show_value(api.config, log.Level.DEBUG,
                      'PushNumber', push_number)

        if lock_post:
            post = data_type.PostInfo(
                board=board,
                aid=post_aid,
                author=post_author,
                title=post_title,
                web_url=post_web,
                money=post_money,
                list_date=list_date,
                format_check=True,
                push_number=push_number,
                lock=True,
            )
            return post

    if query:
        post = data_type.PostInfo(
            board=board,
            aid=post_aid,
            author=post_author,
            title=post_title,
            web_url=post_web,
            money=post_money,
            list_date=list_date,
            format_check=True,
            push_number=push_number,
        )
        return post

    api.Unconfirmed = False

    def is_unconfirmed_handler():
        api.Unconfirmed = True

    cmd = command.Enter * 2
    target_list = [
        # 待證實文章
        connect_core.TargetUnit(
            i18n.UnconfirmedPost,
            '本篇文章內容經站方授權之板務管理人員判斷有尚待證實之處',
            response=' ',
            handler=is_unconfirmed_handler
        ),
        connect_core.TargetUnit(
            [
                i18n.BrowsePost,
                i18n.Done,
            ],
            screens.Target.PostEnd,
            break_detect=True,
            log_level=log.Level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                i18n.BrowsePost,
            ],
            screens.Target.InPost,
            break_detect=True,
            log_level=log.Level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                i18n.PostNoContent,
            ],
            screens.Target.PostNoContent,
            break_detect=True,
            log_level=log.Level.DEBUG
        ),
        # 動畫文章
        connect_core.TargetUnit(
            [
                i18n.AnimationPost,
            ],
            screens.Target.Animation,
            response=command.GoMainMenu_TypeQ,
            break_detect_after_send=True
        ),
    ]

    line_from_pattern = re.compile('[\d]+~[\d]+')

    content_start = '───────────────────────────────────────'
    content_end = []
    content_end.append('--\n※ 發信站: 批踢踢實業坊(ptt.cc)')
    content_end.append('--\n※ 發信站: 批踢踢兔(ptt2.cc)')
    content_end.append('--\n※ 發信站: 新批踢踢(ptt2.twbbs.org.tw)')

    # '※ 發信站: 批踢踢實業坊(ptt.cc)'

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
            post = data_type.PostInfo(
                board=board,
                aid=post_aid,
                author=post_author,
                # Date=PostDate,
                title=post_title,
                web_url=post_web,
                money=post_money,
                # Content=PostContent,
                # PushList=PushList,
                list_date=list_date,
                control_code=has_control_code,
                format_check=False,
                push_number=push_number,
                unconfirmed=api.Unconfirmed,
            )
            return post

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
            # print(f'LastReadLineATemp [{LastReadLineATemp}]')
            # print(f'LastReadLineBTemp [{LastReadLineBTemp}]')
            # print(f'Dis [{23 - (LastReadLineBTemp - LastReadLineATemp)}]')
            # print(f'ContentStartJump {ContentStartJump}')
            # print(f'GetLineB {LastReadLineBTemp - LastReadLineB}')
            # print(f'GetLineA {LastReadLineATemp - LastReadLineA}')
            if not control_code_mode:

                if last_read_line_a_temp in stop_dict:
                    new_content_part = '\n'.join(
                        lines[-stop_dict[last_read_line_a_temp]:])
                else:
                    get_line_b = last_read_line_b_temp - last_read_line_b
                    if get_line_b > 0:
                        # print('Type 1')
                        # print(f'GetLineB [{GetLineB}]')
                        new_content_part = '\n'.join(lines[-get_line_b:])
                    else:
                        # 駐足現象，LastReadLineB跟上一次相比並沒有改變
                        if (last_read_line_b_temp + 1) not in stop_dict:
                            stop_dict[last_read_line_b_temp + 1] = 1
                        stop_dict[last_read_line_b_temp + 1] += 1

                        get_line_a = last_read_line_a_temp - last_read_line_a

                        if get_line_a > 0:
                            new_content_part = '\n'.join(lines[-get_line_a:])
                        else:
                            new_content_part = '\n'.join(lines)

            else:
                new_content_part = lines[-1]

            origin_post.append(new_content_part)
            log.show_value(
                api.config,
                log.Level.DEBUG,
                'NewContentPart',
                new_content_part
            )

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
            cmd = command.Down
        else:
            cmd = command.Right

    # print(api.Unconfirmed)
    origin_post = '\n'.join(origin_post)
    # OriginPost = [line.strip() for line in OriginPost.split('\n')]
    # OriginPost = '\n'.join(OriginPost)

    log.show_value(
        api.config,
        log.Level.DEBUG,
        'OriginPost',
        origin_post
    )

    # print('=' * 20)
    # print()
    # print('=' * 20)

    post_author_pattern_new = re.compile('作者  (.+) 看板')
    post_author_pattern_old = re.compile('作者  (.+)')
    board_pattern = re.compile('看板  (.+)')

    post_date = None
    post_content = []
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
                log.show_value(
                    api.config,
                    log.Level.DEBUG,
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
                log.Level.DEBUG,
                i18n.SubstandardPost,
                i18n.Author
            )
            post = data_type.PostInfo(
                board=board,
                aid=post_aid,
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
        log.Level.DEBUG,
        i18n.Author,
        post_author
    )

    post_title_pattern = re.compile('標題  (.+)')

    title_line = origin_post_lines[1]
    pattern_result = post_title_pattern.search(title_line)
    if pattern_result is None:
        log.show_value(
            api.config,
            log.Level.DEBUG,
            i18n.SubstandardPost,
            i18n.Title
        )
        post = data_type.PostInfo(
            board=board,
            aid=post_aid,
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
    post_title = pattern_result.group(0)
    post_title = post_title[4:].strip()

    log.show_value(
        api.config,
        log.Level.DEBUG,
        i18n.Title,
        post_title
    )

    post_date_pattern = re.compile('時間  (.+)')
    date_line = origin_post_lines[2]
    pattern_result = post_date_pattern.search(date_line)
    if pattern_result is None:
        log.show_value(
            api.config,
            log.Level.DEBUG,
            i18n.SubstandardPost,
            i18n.Date
        )
        post = data_type.PostInfo(
            board=board,
            aid=post_aid,
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
        log.Level.DEBUG,
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
            log.Level.DEBUG,
            i18n.SubstandardPost,
            i18n.Content
        )
        post = data_type.PostInfo(
            board=board,
            aid=post_aid,
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
        log.Level.DEBUG,
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
            log.Level.DEBUG,
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
                log.show_value(api.config, log.Level.DEBUG,
                              'Location', location)
            break

        pattern_result = pattern_p2.search(line)
        if pattern_result is not None:
            ip = pattern_result.group(0)
            ip = ip.replace('-', '.')
            # print(f'IP -> [{IP}]')
            break
    if api.config.host == data_type.host.PTT1:
        if ip is None:
            log.show_value(
                api.config,
                log.Level.DEBUG,
                i18n.SubstandardPost,
                'IP'
            )
            post = data_type.PostInfo(
                board=board,
                aid=post_aid,
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
    log.show_value(api.config, log.Level.DEBUG, 'IP', ip)

    push_author_pattern = re.compile('[推|噓|→] [\w| ]+:')
    push_date_pattern = re.compile('[\d]+/[\d]+ [\d]+:[\d]+')
    push_ip_pattern = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')

    push_list = []

    for line in origin_post_lines:
        if line.startswith('推'):
            push_type = data_type.PushType.PUSH
        elif line.startswith('噓 '):
            push_type = data_type.PushType.BOO
        elif line.startswith('→ '):
            push_type = data_type.PushType.ARROW
        else:
            continue

        result = push_author_pattern.search(line)
        if result is None:
            # 不符合推文格式
            continue
        push_author = result.group(0)[2:-1].strip()
        log.show_value(api.config, log.Level.DEBUG, [
            i18n.Push,
            i18n.ID,
        ],
                       push_author
                       )

        result = push_date_pattern.search(line)
        if result is None:
            continue
        push_date = result.group(0)
        log.show_value(api.config, log.Level.DEBUG, [
            i18n.Push,
            i18n.Date,
        ],
                       push_date
                       )

        push_ip = None
        result = push_ip_pattern.search(line)
        if result is not None:
            push_ip = result.group(0)
            log.show_value(api.config, log.Level.DEBUG, [
                i18n.Push,
                'IP',
            ],
                           push_ip
                           )

        push_content = line[
                       line.find(push_author) + len(push_author):
                       ]
        # PushContent = PushContent.replace(PushDate, '')

        if api.config.host == data_type.host.PTT1:
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
            log.Level.DEBUG, [
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
