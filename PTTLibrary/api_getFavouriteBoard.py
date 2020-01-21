try:
    from . import DataType
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Command
except ModuleNotFoundError:
    import DataType
    import i18n
    import ConnectCore
    import Log
    import Command


def getFavouriteBoard(api):

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('F')
    CmdList.append(Command.Enter)
    CmdList.append('0')
    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.FavouriteBoardList,
            '選擇看板',
            BreakDetect=True
        )
    ]

    FavouriteBoardList = []
    while True:

        api._ConnectCore.send(
            Cmd,
            TargetList
        )

        OriScreen = api._ConnectCore.getScreenQueue()[-1]
        # print(OriScreen)
        ScreenBuf = OriScreen
        ScreenBuf = [x for x in ScreenBuf.split('\n')][3:][:-1]
        ScreenBuf[0] = '  ' + ScreenBuf[0][1:]
        ScreenBuf = [x for x in ScreenBuf]

        MinLen = 47

        # for line in ScreenBuf:
        #     print(line[:MinLen - len(line)])
        #     print(len(line))
        for i, line in enumerate(ScreenBuf):
            if len(ScreenBuf[i]) == 0:
                continue
            if len(ScreenBuf[i]) <= MinLen:
                # print(f'[{ScreenBuf[i]}]')
                ScreenBuf[i] = ScreenBuf[i] + \
                    (' ' * ((MinLen + 1) - len(ScreenBuf[i])))
        ScreenBuf = [x[10:MinLen - len(x)].strip() for x in ScreenBuf]
        ScreenBuf = list(filter(None, ScreenBuf))

        for i, line in enumerate(ScreenBuf):
            # print(i)
            # 16 = line.find('◎')
            linebuff = line[:16].strip()

            Type = linebuff[-2:]
            Board = linebuff[:-2].strip()

            BoardTitle = line[17:].strip()
            # print(line)
            # print('\t' + Type)
            # print('\t' + Board)
            # print('\t' + BoardTitle)

            FBoard = DataType.FavouriteBoard(
                Board,
                Type,
                BoardTitle
            )

            FavouriteBoardList.append(FBoard)

        # print(len(FavouriteBoardList))
        # print(len(ScreenBuf))
        if len(ScreenBuf) < 20:
            break

        Cmd = Command.Ctrl_F

    # ScreenBuf = '\n'.join(ScreenBuf)
    # print(ScreenBuf)
    # print(len(FavouriteBoardList))
    return FavouriteBoardList
