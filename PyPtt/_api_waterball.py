import re
import time

from SingleLog.log import Logger

try:
    from . import data_type
    from . import i18n
    from . import connect_core
    from . import screens
    from . import exceptions
    from . import command
except ModuleNotFoundError:
    import data_type
    import i18n
    import connect_core
    import screens
    import exceptions
    import command


def get_waterball(api, operate_type: int) -> list:
    logger = Logger('get_waterball', Logger.INFO)

    if operate_type == data_type.waterball_operate_type.NOTHING:
        water_ball_operate_type = 'R'
    elif operate_type == data_type.waterball_operate_type.CLEAR:
        water_ball_operate_type = 'C' + command.enter + 'Y'
    elif operate_type == data_type.waterball_operate_type.MAIL:
        water_ball_operate_type = 'M'

    target_list = [
        connect_core.TargetUnit(
            i18n.no_waterball,
            '◆ 暫無訊息記錄',
            break_detect=True,
            log_level=Logger.DEBUG),
        connect_core.TargetUnit(
            i18n.browse_waterball_done,
            screens.Target.WaterBallListEnd,
            response=command.left + water_ball_operate_type +
                     command.enter + command.go_main_menu,
            break_detect_after_send=True,
            log_level=Logger.DEBUG),
        connect_core.TargetUnit(
            i18n.browse_waterball,
            screens.Target.InWaterBallList,
            break_detect=True,
            log_level=Logger.DEBUG),
    ]

    cmd_list = [command.go_main_menu, 'T', command.enter, 'D', command.enter]

    cmd = ''.join(cmd_list)

    line_from_pattern = re.compile('[\d]+~[\d]+')
    to_water_ball_target_pattern = re.compile('To [\w]+:')
    from_water_ball_target_pattern = re.compile('★[\w]+ ')
    water_ball_date_pattern = re.compile(
        '\[[\d]+/[\d]+/[\d]+ [\d]+:[\d]+:[\d]+\]')

    all_waterball = list()
    first_page = True
    while True:
        index = api.connect_core.send(
            cmd,
            target_list)
        log.show_value(
            api.config,
            Logger.DEBUG,
            'index',
            index)
        if index == 0:
            return list()

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

        logger.debug('ori_screen', ori_screen)
        logger.debug('last_line', last_line)

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
            # Error result
            # 'NoneType' object has no attribute 'group'
            # ori_screen 【聊天說話】                     批踢踢實業坊
            #                    )                  │   \  /  /▎  ‧  ▉  ▁__C \  \
            #               )    (.                 │   / ∕/◤  .   ．▉   ▔▔ ◣ ﹨|
            #              ( (      :.              │  7／ ◤▁▁▁▁▁▉▁▁▁▁  ◣＼
            #   ╰╮╮    ▁▂▃▄▃▂▁            │  〢∕▄▄▄▄▄▄█▄▄▄▄▄▄\〢
            #    ╰     ▊▃▄▅▆▅▄▃\▆◣       │  ==}             █            {==
            # last_line       ▄▆▉▇▅▃▃▃▅▇◤ ◥▍     │  〣\    ▅▆     █  █

            # import traceback
            # traceback.print_tb(e.__traceback__)
            # print(e)
            # print(f'ori_screen {ori_screen}')
            # print(f'last_line {last_line}')
            continue

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
            logger.debug('new_content_part', new_content_part)

        if index == 1:
            break

        last_read_line_a = last_read_line_a_temp
        last_read_line_b = last_read_line_b_temp

        cmd = command.down

    all_waterball = '\n'.join(all_waterball)

    if api.config.host == data_type.host_type.PTT1:
        all_waterball = all_waterball.replace(
            ']\n', ']==PTTWaterBallNewLine==')
        all_waterball = all_waterball.replace('\n', '')
        all_waterball = all_waterball.replace(
            ']==PTTWaterBallNewLine==', ']\n')
    else:
        all_waterball = all_waterball.replace('\\\n', '')
    logger.debug('logger.debug(', all_waterball)
    # print('=' * 20)
    # print(AllWaterball)
    # print('=' * 20)

    water_ball_list = list()
    for line in all_waterball.split('\n'):

        if (not line.startswith('To')) and (not line.startswith('★')):
            logger.debug('Discard waterball', line)
            continue
        logger.debug('Ready to parse waterball', line)

        if line.startswith('To'):
            logger.debug('Waterball Type', 'Send')
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
            logger.debug('Waterball Type', 'Catch')
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

        logger.debug('Waterball target', target)
        logger.debug('Waterball content', content)
        logger.debug('Waterball date', date)

        current_waterball = data_type.WaterballInfo(
            waterball_type,
            target,
            content,
            date)

        water_ball_list.append(current_waterball)

    return water_ball_list


def throw_waterball(api: object, target_id: str, content: str) -> None:
    logger = Logger('throw_waterball', Logger.INFO)

    max_length = 50

    water_ball_list = list()
    temp_start_index = 0
    temp_end_index = temp_start_index + 1

    while temp_end_index <= len(content):
        temp = ''
        last_temp = None
        while len(temp.encode('big5uao', 'ignore')) < max_length:
            temp = content[temp_start_index:temp_end_index]

            if not len(temp.encode('big5uao', 'ignore')) < max_length:
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

        logger.info(i18n.water_ball, waterball)

        target_list = [
            connect_core.TargetUnit(
                i18n.set_call_status,
                '您的呼叫器目前設定為關閉',
                response='y' + command.enter),
            # 對方已落跑了
            connect_core.TargetUnit(
                i18n.set_call_status,
                '◆ 糟糕! 對方已落跑了',
                exceptions_=exceptions.UserOffline(target_id)),
            connect_core.TargetUnit(
                i18n.replace(i18n.throw_waterball, target_id),
                f'丟 {target_id} 水球:',
                response=waterball + command.enter * 2 +
                         command.go_main_menu),
            connect_core.TargetUnit(
                i18n.throw_waterball_success,
                screens.Target.MainMenu,
                break_detect=True)
        ]

        cmd_list = list()
        cmd_list.append(command.go_main_menu)
        cmd_list.append('T')
        cmd_list.append(command.enter)
        cmd_list.append('U')
        cmd_list.append(command.enter)
        if '【好友列表】' in api.connect_core.get_screen_queue()[-1]:
            cmd_list.append('f')
        cmd_list.append('s')
        cmd_list.append(target_id)
        cmd_list.append(command.enter)
        cmd_list.append('w')

        cmd = ''.join(cmd_list)

        api.connect_core.send(
            cmd,
            target_list,
            screen_timeout=api.config.screen_long_timeout
        )
        api._LastThrowWaterBallTime = time.time()
