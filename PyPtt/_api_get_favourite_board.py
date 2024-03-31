from . import _api_util
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import log
from .data_type import FavouriteBoardField


def get_favourite_board(api) -> list:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    cmd_list = [command.go_main_menu, 'F', command.enter, '0']
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('選擇看板', break_detect=True)
    ]

    log.logger.info(i18n.get_favourite_board_list)

    board_list = []
    favourite_board_list = []
    while True:

        api.connect_core.send(
            cmd,
            target_list)

        ori_screen = api.connect_core.get_screen_queue()[-1]
        # print(OriScreen)
        screen_buf = ori_screen
        screen_buf = [x for x in screen_buf.split('\n')][3:-1]

        # adjust for cursor
        screen_buf[0] = '  ' + screen_buf[0][1:]
        screen_buf = [x for x in screen_buf]

        min_len = 47

        for i, line in enumerate(screen_buf):
            if len(screen_buf[i]) == 0:
                continue
            if len(screen_buf[i]) <= min_len:
                # print(f'[{ScreenBuf[i]}]')
                screen_buf[i] = screen_buf[i] + (' ' * ((min_len + 1) - len(screen_buf[i])))
        screen_buf = [x[10:min_len - len(x)].strip() for x in screen_buf]
        screen_buf = list(filter(None, screen_buf))

        for i, line in enumerate(screen_buf):
            if '------------' in line:
                continue

            temp = line.strip().split(' ')
            no_space_temp = list(filter(None, temp))

            board = no_space_temp[0]
            if board.startswith('ˇ'):
                board = board[1:]

            board_type = no_space_temp[1]

            title_start_index = temp.index(board_type) + 1
            board_title = ' '.join(temp[title_start_index:])
            # remove ◎
            board_title = board_title[1:]

            if board in board_list:
                log.logger.info(i18n.get_favourite_board_list, '...', i18n.success)
                return favourite_board_list
            board_list.append(board)

            favourite_board_list.append({
                FavouriteBoardField.board: board,
                FavouriteBoardField.type: board_type,
                FavouriteBoardField.title: board_title})

        if len(screen_buf) < 20:
            break

        cmd = command.ctrl_f

    log.logger.info(i18n.get_favourite_board_list, '...', i18n.success)
    return favourite_board_list
