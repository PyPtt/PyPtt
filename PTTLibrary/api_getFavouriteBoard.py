try:
    from . import DataType
    from . import i18n
    from . import ConnectCore
    from . import Command
except ModuleNotFoundError:
    import DataType
    import i18n
    import ConnectCore
    import Command


def get_favourite_board(api):

    cmd_list = []
    cmd_list.append(Command.GoMainMenu)
    cmd_list.append('F')
    cmd_list.append(Command.Enter)
    cmd_list.append('0')
    cmd = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            i18n.FavouriteBoardList,
            '選擇看板',
            BreakDetect=True
        )
    ]

    favourite_board_list = []
    while True:

        api._ConnectCore.send(
            cmd,
            target_list
        )

        ori_screen = api._ConnectCore.getScreenQueue()[-1]
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
                screen_buf[i] = screen_buf[i] + \
                    (' ' * ((min_len + 1) - len(screen_buf[i])))
        screen_buf = [x[10:min_len - len(x)].strip() for x in screen_buf]
        screen_buf = list(filter(None, screen_buf))

        for i, line in enumerate(screen_buf):
            # print(i)
            # 16 = line.find('◎')
            linebuff = line[:16].strip()

            board_type = linebuff[-2:]
            board = linebuff[:-2].strip()

            board_title = line[17:].strip()
            # print(line)
            # print('\t' + Type)
            # print('\t' + Board)
            # print('\t' + BoardTitle)

            f_board = DataType.FavouriteBoard(
                board,
                board_type,
                board_title
            )

            favourite_board_list.append(f_board)

        # print(len(FavouriteBoardList))
        # print(len(ScreenBuf))
        if len(screen_buf) < 20:
            break

        cmd = Command.Ctrl_F

    # ScreenBuf = '\n'.join(ScreenBuf)
    # print(ScreenBuf)
    # print(len(FavouriteBoardList))
    return favourite_board_list
