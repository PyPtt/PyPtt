import re
import time
try:
    from . import DataType
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Screens
    from . import Exceptions
    from . import Command
except ModuleNotFoundError:
    import DataType
    import i18n
    import ConnectCore
    import Log
    import Screens
    import Exceptions
    import Command


def get_waterball(api, operate_type:int) ->list:

    if operate_type == DataType.WaterBallOperateType.DoNothing:
        water_ball_operate_type = 'R'
    elif operate_type == DataType.WaterBallOperateType.Clear:
        water_ball_operate_type = 'C' + Command.Enter + 'Y'
    elif operate_type == DataType.WaterBallOperateType.Mail:
        water_ball_operate_type = 'M'

    target_list = [
        ConnectCore.TargetUnit(
            i18n.NoWaterball,
            '◆ 暫無訊息記錄',
            break_detect=True,
            log_level=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                i18n.BrowseWaterball,
                i18n.Done,
            ],
            Screens.Target.WaterBallListEnd,
            response=Command.Left + water_ball_operate_type +
                     Command.Enter + Command.GoMainMenu,
            break_detect_after_send=True,
            log_level=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                i18n.BrowseWaterball,
            ],
            Screens.Target.InWaterBallList,
            break_detect=True,
            log_level=Log.Level.DEBUG
        ),
    ]

    cmd_list = [Command.GoMainMenu, 'T', Command.Enter, 'D', Command.Enter]

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
            screen_timeout=1
        )
        Log.show_value(
            api.config,
            Log.Level.DEBUG,
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
        Log.show_value(
            api.config,
            Log.Level.DEBUG,
            'OriScreen',
            ori_screen
        )

        Log.show_value(
            api.config,
            Log.Level.DEBUG,
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
        last_read_line_list = pattern_result.group(0).split('~')
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
            Log.show_value(
                api.config,
                Log.Level.DEBUG,
                'NewContentPart',
                new_content_part
            )

        if index == 1:
            break

        last_read_line_a = last_read_line_a_temp
        last_read_line_b = last_read_line_b_temp

        cmd = Command.Down

    all_waterball = '\n'.join(all_waterball)

    if api.config.Host == DataType.Host.PTT1:
        all_waterball = all_waterball.replace(
            ']\n', ']==PTTWaterBallNewLine==')
        all_waterball = all_waterball.replace('\n', '')
        all_waterball = all_waterball.replace(
            ']==PTTWaterBallNewLine==', ']\n')
    else:
        all_waterball = all_waterball.replace('\\\n', '')
    Log.show_value(
        api.config,
        Log.Level.DEBUG,
        'AllWaterball',
        all_waterball
    )
    # print('=' * 20)
    # print(AllWaterball)
    # print('=' * 20)

    water_ball_list = []
    for line in all_waterball.split('\n'):

        if (not line.startswith('To')) and (not line.startswith('★')):
            Log.show_value(
                api.config,
                Log.Level.DEBUG,
                'Discard waterball',
                line
            )
            continue
        Log.show_value(
            api.config,
            Log.Level.DEBUG,
            'Ready to parse waterball',
            line
        )

        if line.startswith('To'):
            Log.show_value(
                api.config,
                Log.Level.DEBUG,
                'Waterball Type',
                'Send'
            )
            waterball_type = DataType.WaterBallType.Send

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
            Log.show_value(
                api.config,
                Log.Level.DEBUG,
                'Waterball Type',
                'Catch'
            )
            waterball_type = DataType.WaterBallType.Catch

            pattern_result = from_water_ball_target_pattern.search(line)
            target = pattern_result.group(0)[1:-1]

            pattern_result = water_ball_date_pattern.search(line)
            date = pattern_result.group(0)[1:-1]

            content = line
            content = content[content.find(
                target + ' ') + len(target + ' '):]
            content = content[:content.rfind(date) - 1]
            content = content.strip()

        Log.show_value(
            api.config,
            Log.Level.DEBUG,
            'Waterball target',
            target
        )
        Log.show_value(
            api.config,
            Log.Level.DEBUG,
            'Waterball content',
            content
        )
        Log.show_value(
            api.config,
            Log.Level.DEBUG,
            'Waterball date',
            date
        )

        current_waterball = DataType.WaterBallInfo(
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

        Log.show_value(
            api.config,
            Log.Level.INFO,
            i18n.WaterBall,
            waterball
        )

        target_list = [
            ConnectCore.TargetUnit(
                i18n.SetCallStatus,
                '您的呼叫器目前設定為關閉',
                response='y' + Command.Enter,
            ),
            # 對方已落跑了
            ConnectCore.TargetUnit(
                i18n.SetCallStatus,
                '◆ 糟糕! 對方已落跑了',
                exceptions=Exceptions.UserOffline(target_id)
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.Throw,
                    target_id,
                    i18n.WaterBall
                ],
                '丟 ' + target_id + ' 水球:',
                response=waterball + Command.Enter * 2 +
                         Command.GoMainMenu,
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.Throw,
                    i18n.WaterBall,
                    i18n.Success
                ],
                Screens.Target.MainMenu,
                break_detect=True
            )
        ]

        cmd_list = []
        cmd_list.append(Command.GoMainMenu)
        cmd_list.append('T')
        cmd_list.append(Command.Enter)
        cmd_list.append('U')
        cmd_list.append(Command.Enter)
        if '【好友列表】' in api.connect_core.get_screen_queue()[-1]:
            cmd_list.append('f')
        cmd_list.append('s')
        cmd_list.append(target_id)
        cmd_list.append(Command.Enter)
        cmd_list.append('w')

        cmd = ''.join(cmd_list)

        api.connect_core.send(
            cmd,
            target_list,
            screen_timeout=api.config.ScreenLongTimeOut
        )
        api._LastThrowWaterBallTime = time.time()
