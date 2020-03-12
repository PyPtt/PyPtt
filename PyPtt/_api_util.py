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


def get_content(api, post_mode: bool = True):
    api.Unconfirmed = False

    def is_unconfirmed_handler(screen):
        api.Unconfirmed = True

    if post_mode:
        cmd = command.Enter * 2
    else:
        cmd = command.Enter
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
            log_level=log.level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                i18n.BrowsePost,
            ],
            screens.Target.InPost,
            break_detect=True,
            log_level=log.level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                i18n.PostNoContent,
            ],
            screens.Target.PostNoContent,
            break_detect=True,
            log_level=log.level.DEBUG
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
                log.level.DEBUG,
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
        log.level.DEBUG,
        'OriginPost',
        origin_post
    )

    return origin_post, has_control_code


def get_mailbox_capacity(api):
    last_screen = api.connect_core.get_screen_queue()[-1]
    capacity_line = last_screen.split('\n')[2]
    log.show_value(
        api.config,
        log.level.DEBUG,
        'capacity_line',
        capacity_line
    )
    pattern_result = re.compile('(\d+)/(\d+)').search(capacity_line)
    if pattern_result is not None:
        # print(pattern_result.group(0))
        current_capacity = int(pattern_result.group(0).split('/')[0])
        max_capacity = int(pattern_result.group(0).split('/')[1])
        log.show_value(
            api.config,
            log.level.DEBUG,
            'current_capacity',
            current_capacity
        )
        log.show_value(
            api.config,
            log.level.DEBUG,
            'max_capacity',
            max_capacity
        )
        return current_capacity, max_capacity
    return 0, 0
