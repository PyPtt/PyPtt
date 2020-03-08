import re
import time
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


def get_waterball(api, operate_type:int) -> list:

    if operate_type == data_type.waterball_operate_type.NOTHING:
        water_ball_operate_type = 'R'
    elif operate_type == data_type.waterball_operate_type.CLEAR:
        water_ball_operate_type = 'C' + command.Enter + 'Y'
    elif operate_type == data_type.waterball_operate_type.MAIL:
        water_ball_operate_type = 'M'

    target_list = [
        connect_core.TargetUnit(
            i18n.NoWaterball,
            '◆ 暫無訊息記錄',
            break_detect=True,
            log_level=log.level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                i18n.BrowseWaterball,
                i18n.Done,
            ],
            screens.Target.WaterBallListEnd,
            response=command.Left + water_ball_operate_type +
                     command.Enter + command.GoMainMenu,
            break_detect_after_send=True,
            log_level=log.level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                i18n.BrowseWaterball,
            ],
            screens.Target.InWaterBallList,
            break_detect=True,
            log_level=log.level.DEBUG
        ),
    ]

    cmd_list = [command.GoMainMenu, 'T', command.Enter, 'D', command.Enter]

    cmd = ''.join(cmd_list)

    line_from_pattern = re.compile('[\d]+~[\d]+')
    to_water_ball_target_pattern = re.compile('To [\w]+:')
    from_water_ball_target_pattern = re.compile('★[\w]+ ')
    water_ball_date_pattern = re.compile(
        '\[[\d]+/[\d]+/[\d]+ [\d]+:[\d]+:[\d]+\]')

    all_waterball = []
    first_page = True
    while True:
        index = api.connect_core.send(
            cmd,
            target_list,
            # screen_timeout=1
        )
        log.show_value(
            api.config,
            log.level.DEBUG,
            'index',
            index
        )
        if index == 0:
            return []

        ori_screen = api.connect_core.get_screen_queue()[-1]
        lines = ori_screen.split('\n')
        last_line = lines[-1]
        lines.pop()
        lines = list(filter(None, lines))
        ori_screen = '\n'.join(lines)

        # print('=' * 50)
        # print(OriScreen)
        # print('=' * 50)
        # ScreenTemp = OriScreen
        log.show_value(
            api.config,
            log.level.DEBUG,
            'OriScreen',
            ori_screen
        )

        log.show_value(
            api.config,
            log.level.DEBUG,
            'LastLine',
            last_line
        )
        if last_line.startswith('★'):
            continue

        # 整理水球換行格式
        # ScreenTemp = ScreenTemp.replace(
        #     ']\n', ']==PTTWaterBallNewLine==')
        # ScreenTemp = ScreenTemp.replace('\\\n', '')
        # ScreenTemp = ScreenTemp.replace('\n', '')
        # ScreenTemp = ScreenTemp.replace(
        #     ']==PTTWaterBallNewLine==', ']\n')

        # print('=' * 50)
        # print(LastLine)
        # print('=' * 50)

        pattern_result = line_from_pattern.search(last_line)
        try:
            last_read_line_list = pattern_result.group(0).split('~')
        except Exception as e:
            import traceback
            traceback.print_tb(e.__traceback__)
            print(e)
            print(f'ori_screen {ori_screen}')
            print(f'last_line {last_line}')
            raise e

        last_read_line_a_temp = int(last_read_line_list[0])
        last_read_line_b_temp = int(last_read_line_list[1])
        # last_read_line_a = last_read_line_a_temp - 1
        # last_read_line_b = last_read_line_b_temp - 1

        if first_page:
            first_page = False
            all_waterball.append(ori_screen)
            last_read_line_a = last_read_line_a_temp - 1
            last_read_line_b = last_read_line_b_temp - 1
        else:
            get_line_a = last_read_line_a_temp - last_read_line_a
            get_line_b = last_read_line_b_temp - last_read_line_b

            # print(f'last_read_line_a [{last_read_line_a}]')
            # print(f'last_read_line_b [{last_read_line_b}]')
            # print(f'last_read_line_a_temp [{last_read_line_a_temp}]')
            # print(f'last_read_line_b_temp [{last_read_line_b_temp}]')
            # print(f'get_line_a [{get_line_a}]')
            # print(f'get_line_b [{get_line_b}]')
            if get_line_b > 0:
                # print('Type 1')

                if not all_waterball[-1].endswith(']'):
                    get_line_b += 1

                new_content_part = '\n'.join(lines[-get_line_b:])
            else:
                # print('Type 2')
                if get_line_a > 0:
                    # print('Type 2 - 1')

                    if len(lines[-get_line_a]) == 0:
                        # print('!!!!!!!!!')
                        get_line_a += 1

                    new_content_part = '\n'.join(lines[-get_line_a:])
                else:
                    # print('Type 2 - 2')
                    new_content_part = '\n'.join(lines)

            all_waterball.append(new_content_part)
            log.show_value(
                api.config,
                log.level.DEBUG,
                'NewContentPart',
                new_content_part
            )

        if index == 1:
            break

        last_read_line_a = last_read_line_a_temp
        last_read_line_b = last_read_line_b_temp

        cmd = command.Down

    all_waterball = '\n'.join(all_waterball)

    if api.config.host == data_type.host_type.PTT1:
        all_waterball = all_waterball.replace(
            ']\n', ']==PTTWaterBallNewLine==')
        all_waterball = all_waterball.replace('\n', '')
        all_waterball = all_waterball.replace(
            ']==PTTWaterBallNewLine==', ']\n')
    else:
        all_waterball = all_waterball.replace('\\\n', '')
    log.show_value(
        api.config,
        log.level.DEBUG,
        'AllWaterball',
        all_waterball
    )
    # print('=' * 20)
    # print(AllWaterball)
    # print('=' * 20)

    water_ball_list = []
    for line in all_waterball.split('\n'):

        if (not line.startswith('To')) and (not line.startswith('★')):
            log.show_value(
                api.config,
                log.level.DEBUG,
                'Discard waterball',
                line
            )
            continue
        log.show_value(
            api.config,
            log.level.DEBUG,
            'Ready to parse waterball',
            line
        )

        if line.startswith('To'):
            log.show_value(
                api.config,
                log.level.DEBUG,
                'Waterball Type',
                'Send'
            )
            waterball_type = data_type.waterball_type.SEND

            pattern_result = to_water_ball_target_pattern.search(line)
            target = pattern_result.group(0)[3:-1]

            pattern_result = water_ball_date_pattern.search(line)
            date = pattern_result.group(0)[1:-1]

            content = line
            content = content[content.find(
                target + ':') + len(target + ':'):]
            content = content[:content.rfind(date) - 1]
            content = content.strip()

        elif line.startswith('★'):
            log.show_value(
                api.config,
                log.level.DEBUG,
                'Waterball Type',
                'Catch'
            )
            waterball_type = data_type.waterball_type.CATCH

            pattern_result = from_water_ball_target_pattern.search(line)
            target = pattern_result.group(0)[1:-1]

            pattern_result = water_ball_date_pattern.search(line)
            date = pattern_result.group(0)[1:-1]

            content = line
            content = content[content.find(
                target + ' ') + len(target + ' '):]
            content = content[:content.rfind(date) - 1]
            content = content.strip()

        log.show_value(
            api.config,
            log.level.DEBUG,
            'Waterball target',
            target
        )
        log.show_value(
            api.config,
            log.level.DEBUG,
            'Waterball content',
            content
        )
        log.show_value(
            api.config,
            log.level.DEBUG,
            'Waterball date',
            date
        )

        current_waterball = data_type.WaterballInfo(
            waterball_type,
            target,
            content,
            date
        )

        water_ball_list.append(current_waterball)

    return water_ball_list


def throw_waterball(api: object, target_id: str, content: str) -> None:
    max_length = 50

    water_ball_list = []
    temp_start_index = 0
    temp_end_index = temp_start_index + 1

    while temp_end_index <= len(content):
        temp = ''
        last_temp = None
        while len(temp.encode('big5-uao', 'ignore')) < max_length:
            temp = content[temp_start_index:temp_end_index]

            if not len(temp.encode('big5-uao', 'ignore')) < max_length:
                break
            elif content.endswith(temp) and temp_start_index != 0:
                break
            elif temp.endswith('\n'):
                break
            elif last_temp == temp:
                break

            temp_end_index += 1
            last_temp = temp

        water_ball_list.append(temp.strip())

        temp_start_index = temp_end_index
        temp_end_index = temp_start_index + 1
    water_ball_list = filter(None, water_ball_list)

    for waterball in water_ball_list:

        if api._LastThrowWaterBallTime != 0:
            current_time = time.time()
            while (current_time - api._LastThrowWaterBallTime) < 3.2:
                time.sleep(0.1)
                current_time = time.time()

        log.show_value(
            api.config,
            log.level.INFO,
            i18n.WaterBall,
            waterball
        )

        target_list = [
            connect_core.TargetUnit(
                i18n.SetCallStatus,
                '您的呼叫器目前設定為關閉',
                response='y' + command.Enter,
            ),
            # 對方已落跑了
            connect_core.TargetUnit(
                i18n.SetCallStatus,
                '◆ 糟糕! 對方已落跑了',
                exceptions_=exceptions.UserOffline(target_id)
            ),
            connect_core.TargetUnit(
                [
                    i18n.Throw,
                    target_id,
                    i18n.WaterBall
                ],
                '丟 ' + target_id + ' 水球:',
                response=waterball + command.Enter * 2 +
                command.GoMainMenu,
            ),
            connect_core.TargetUnit(
                [
                    i18n.Throw,
                    i18n.WaterBall,
                    i18n.Success
                ],
                screens.Target.MainMenu,
                break_detect=True
            )
        ]

        cmd_list = []
        cmd_list.append(command.GoMainMenu)
        cmd_list.append('T')
        cmd_list.append(command.Enter)
        cmd_list.append('U')
        cmd_list.append(command.Enter)
        if '【好友列表】' in api.connect_core.get_screen_queue()[-1]:
            cmd_list.append('f')
        cmd_list.append('s')
        cmd_list.append(target_id)
        cmd_list.append(command.Enter)
        cmd_list.append('w')

        cmd = ''.join(cmd_list)

        api.connect_core.send(
            cmd,
            target_list,
            screen_timeout=api.config.screen_long_timeout
        )
        api._LastThrowWaterBallTime = time.time()
