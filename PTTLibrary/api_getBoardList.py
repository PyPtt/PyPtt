import progressbar
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


def getBoardList(api):

    # Log.showValue(
    #     api.Config,
    #     Log.Level.INFO,
    #     [
    #         i18n.PTT,
    #         i18n.Msg
    #     ],
    #     i18n.MarkPost
    # )

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('F')
    CmdList.append(Command.Enter)
    CmdList.append('y')
    CmdList.append('$')
    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.BoardList,
            Screens.Target.InBoardList,
            BreakDetect=True
        )
    ]

    api._ConnectCore.send(
        Cmd,
        TargetList,
        ScreenTimeout=api.Config.ScreenLongTimeOut
    )
    OriScreen = api._ConnectCore.getScreenQueue()[-1]

    MaxNo = 0

    for line in OriScreen.split('\n'):
        if '◎' not in line:
            continue

        if line.startswith(api._Cursor):
            line = line[len(api._Cursor):]

        # print(f'->{line}<')

        FrontPart = line[:line.find('◎')]
        FrontPartList = [x for x in FrontPart.split(' ')]
        FrontPartList = list(filter(None, FrontPartList))
        # print(f'FrontPartList =>{FrontPartList}<=')
        MaxNo = int(FrontPartList[0])

    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        'MaxNo',
        MaxNo
    )

    if api.Config.LogLevel == Log.Level.INFO:
        PB = progressbar.ProgressBar(
            max_value=MaxNo,
            redirect_stdout=True
        )

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('F')
    CmdList.append(Command.Enter)
    CmdList.append('y')
    CmdList.append('0')
    Cmd = ''.join(CmdList)

    BoardList = []
    while True:

        api._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=api.Config.ScreenLongTimeOut
        )

        OriScreen = api._ConnectCore.getScreenQueue()[-1]
        # print(OriScreen)
        for line in OriScreen.split('\n'):
            if '◎' not in line and '●' not in line:
                continue

            if line.startswith(api._Cursor):
                line = line[len(api._Cursor):]

            # print(f'->{line}<')

            if '◎' in line:
                FrontPart = line[:line.find('◎')]
            else:
                FrontPart = line[:line.find('●')]
            FrontPartList = [x for x in FrontPart.split(' ')]
            FrontPartList = list(filter(None, FrontPartList))
            # print(f'FrontPartList =>{FrontPartList}<=')
            No = int(FrontPartList[0])
            # print(f'No  =>{No}<=')
            # print(f'LastNo =>{LastNo}<=')

            Log.showValue(
                api.Config,
                Log.Level.DEBUG,
                'Board NO',
                No
            )

            BoardName = FrontPartList[1]
            if BoardName.startswith('ˇ'):
                BoardName = BoardName[1:]

            Log.showValue(
                api.Config,
                Log.Level.DEBUG,
                'Board Name',
                BoardName
            )

            BoardList.append(BoardName)

            if api.Config.LogLevel == Log.Level.INFO:
                PB.update(No)

        if No == MaxNo:
            break
        Cmd = Command.Ctrl_F

    if api.Config.LogLevel == Log.Level.INFO:
        PB.finish()

    return BoardList
