import progressbar

from . import _api_util
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import log
from . import screens


def get_board_list(api) -> list:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    cmd_list = [
        command.go_main_menu,
        'F',
        command.enter,
        'y',
        '$']
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(screens.Target.InBoardList, break_detect=True)
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout)
    ori_screen = api.connect_core.get_screen_queue()[-1]

    max_no = 0
    for line in ori_screen.split('\n'):
        if '◎' not in line and '●' not in line:
            continue

        if line.startswith(api.cursor):
            line = line[len(api.cursor):]

        # print(f'->{line}<')
        if '◎' in line:
            front_part = line[:line.find('◎')]
        else:
            front_part = line[:line.find('●')]
        front_part_list = [x for x in front_part.split(' ')]
        front_part_list = list(filter(None, front_part_list))
        # print(f'FrontPartList =>{FrontPartList}<=')
        max_no = int(front_part_list[0].rstrip(')'))

    if api.config.log_level == log.INFO:
        pb = progressbar.ProgressBar(
            max_value=max_no,
            redirect_stdout=True)

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append('F')
    cmd_list.append(command.enter)
    cmd_list.append('y')
    cmd_list.append('0')
    cmd = ''.join(cmd_list)

    board_list = []
    while True:

        api.connect_core.send(
            cmd,
            target_list,
            screen_timeout=api.config.screen_long_timeout)

        ori_screen = api.connect_core.get_screen_queue()[-1]
        # print(OriScreen)
        for line in ori_screen.split('\n'):
            if '◎' not in line and '●' not in line:
                continue

            if line.startswith(api.cursor):
                line = line[len(api.cursor):]

            if '◎' in line:
                front_part = line[:line.find('◎')]
            else:
                front_part = line[:line.find('●')]
            front_part_list = [x for x in front_part.split(' ')]
            front_part_list = list(filter(None, front_part_list))

            number = front_part_list[0]
            if ')' in number:
                number = number[:number.rfind(')')]
            no = int(number)

            board_name = front_part_list[1]
            if board_name.startswith('ˇ'):
                board_name = board_name[1:]
                if len(board_name) == 0:
                    board_name = front_part_list[2]

            board_list.append(board_name)

            if api.config.log_level == log.INFO:
                pb.update(no)

        if no >= max_no:
            break
        cmd = command.ctrl_f

    if api.config.log_level == log.INFO:
        pb.finish()

    return board_list
