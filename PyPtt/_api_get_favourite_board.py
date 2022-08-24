import PyPtt
from . import command, exceptions, _api_util
from . import connect_core
from . import data_type
from . import i18n


def get_favourite_board(api: PyPtt.API, ) -> list:
    _api_util._one_thread(api)

    if not api._login_status:
        raise exceptions.Requirelogin(i18n.require_login)

    cmd_list = list()
    cmd_list.append(command.go_main_menu)
    cmd_list.append('F')
    cmd_list.append(command.enter)
    cmd_list.append('0')
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.favourite_board_list,
            '選擇看板',
            break_detect=True
        )
    ]

    board_list = list()
    favourite_board_list = list()
    while True:

        api.connect_core.send(
            cmd,
            target_list
        )

        ori_screen = api.connect_core.get_screen_queue()[-1]
        # print(OriScreen)
        screen_buf = ori_screen
        screen_buf = [x for x in screen_buf.split('\n')][3:][:-1]
        screen_buf[0] = '  ' + screen_buf[0][1:]
        screen_buf = [x for x in screen_buf]

        min_len = 47

        # for line in ScreenBuf:
        #     print(line[:MinLen - len(line)])
        #     print(len(line))
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
            # 16 = line.find('◎')
            linebuff = line[:16].strip()

            board_type = linebuff[-2:]
            board = linebuff[:-2].strip()
            if board.startswith('ˇ'):
                board = board[1:]

            board_title = line[17:].strip()
            # print(line)
            # print('\t' + Type)
            # print('\t' + board)
            # print('\t' + BoardTitle)

            if board in board_list:
                return favourite_board_list
            board_list.append(board)
            #
            # print('board', board)
            # print('board_type', board_type)
            # print('board_title', board_title)

            f_board = data_type.FavouriteBoard(
                board,
                board_type,
                board_title
            )
            favourite_board_list.append(f_board)

        # print(len(favourite_board_list))
        # print(len(screen_buf))
        if len(screen_buf) < 20:
            break

        cmd = command.ctrl_f

    # ScreenBuf = '\n'.join(ScreenBuf)
    # print(ScreenBuf)
    # print(len(favourite_board_list))
    return favourite_board_list
