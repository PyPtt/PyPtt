import re

from . import _api_util
from . import command
from . import connect_core
from . import log
from . import screens


def has_new_mail(api) -> int:
    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append(command.ctrl_z)
    cmd_list.append('m')
    # cmd_list.append('1')
    # cmd_list.append(command.enter)
    cmd = ''.join(cmd_list)
    current_capacity = None
    plus_count = 0
    index_pattern = re.compile(r'(\d+)')
    checked_index_list = []
    break_detect = False

    target_list = [
        connect_core.TargetUnit(screens.Target.InMailBox, log_level=log.DEBUG, break_detect=True)
    ]

    api.connect_core.send(
        cmd,
        target_list,
    )
    current_capacity, _ = _api_util.get_mailbox_capacity(api)
    if current_capacity > 20:
        cmd_list = []
        cmd_list.append(command.go_main_menu)
        cmd_list.append(command.ctrl_z)
        cmd_list.append('m')
        cmd_list.append('1')
        cmd_list.append(command.enter)
        cmd = ''.join(cmd_list)

    while True:
        if current_capacity > 20:
            api.connect_core.send(
                cmd,
                target_list,
            )
        last_screen = api.connect_core.get_screen_queue()[-1]

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
        cmd = command.ctrl_f

    return plus_count
