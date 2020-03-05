import re

try:
    from . import i18n
    from . import connect_core
    from . import log
    from . import screens
    from . import command
except ModuleNotFoundError:
    import i18n
    import connect_core
    import log
    import screens
    import command


def has_new_mail(api) -> int:
    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append(command.Ctrl_Z)
    cmd_list.append('m')
    cmd_list.append('1')
    cmd_list.append(command.Enter)
    # cmd_list.append('$')
    cmd = ''.join(cmd_list)
    current_capacity = None
    plus_count = 0
    last_index = 0
    index_pattern = re.compile('(\d+)')
    checked_index_list = []
    break_detect = False

    while True:
        target_list = [
            connect_core.TargetUnit(
                i18n.MailBox,
                screens.Target.InMailBox,
                break_detect=True,
                log_level=log.level.DEBUG
            )
        ]

        api.connect_core.send(
            cmd,
            target_list,
        )
        last_screen = api.connect_core.get_screen_queue()[-1]

        if current_capacity is None:
            capacity_line = last_screen.split('\n')[2]
            log.show_value(
                api.config,
                log.level.DEBUG,
                'capacity_line',
                capacity_line
            )

            pattern_result = re.compile('(\d+)/(\d+)').search(capacity_line)
            if pattern_result is not None:
                current_capacity = pattern_result.group(0).split('/')[0]

        last_screen_list = last_screen.split('\n')
        last_screen_list = last_screen_list[3:-1]
        last_screen_list = [x[:10] for x in last_screen_list]

        current_plus_count = 0
        for line in last_screen_list:
            if str(current_capacity) in line:
                break_detect = True

            index_result = index_pattern.search(line)
            if index_result is None:
                continue
            current_index = index_result.group(0)
            if current_index in checked_index_list:
                continue
            checked_index_list.append(current_index)
            if '+' not in line:
                continue

            current_plus_count += 1

        plus_count += current_plus_count
        if break_detect:
            break
        cmd = command.Ctrl_F

    return plus_count
