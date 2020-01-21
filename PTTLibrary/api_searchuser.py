
try:
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Command
except ModuleNotFoundError:
    import i18n
    import ConnectCore
    import Log
    import Command


def searchuser(api, target, minpage, maxpage):

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('T')
    CmdList.append(Command.Enter)
    CmdList.append('Q')
    CmdList.append(Command.Enter)
    CmdList.append(target)
    Cmd = ''.join(CmdList)

    if minpage is not None:
        temppage = minpage
    else:
        temppage = 1

    appendstr = ' ' * temppage
    cmdtemp = Cmd + appendstr

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵',
            BreakDetect=True,
        ),
    ]

    resultlist = []

    while True:

        api._ConnectCore.send(
            cmdtemp,
            TargetList
        )
        OriScreen = api._ConnectCore.getScreenQueue()[-1]
        Log.log(
            api.Config,
            Log.Level.INFO,
            i18n.Reading
        )
        # print(OriScreen)
        # print(len(OriScreen.split('\n')))

        if len(OriScreen.split('\n')) == 2:
            resultid = OriScreen.split('\n')[1]
            resultid = resultid[resultid.find(' ') + 1:].strip()
            # print(resultid)

            resultlist.append(resultid)
            break
        else:

            OriScreen = OriScreen.split('\n')[3:-1]
            OriScreen = '\n'.join(OriScreen)

            templist = OriScreen.replace('\n', ' ')

            while '  ' in templist:
                templist = templist.replace('  ', ' ')

            templist = templist.split(' ')
            resultlist.extend(templist)

            # print(templist)
            # print(len(templist))

            if len(templist) != 100 and len(templist) != 120:
                break

            temppage += 1
            if maxpage is not None:
                if temppage > maxpage:
                    break

            cmdtemp = ' '

    Log.log(
        api.Config,
        Log.Level.INFO,
        i18n.ReadComplete
    )

    api._ConnectCore.send(
        Command.Enter,
        [
            # 《ＩＤ暱稱》
            ConnectCore.TargetUnit(
                i18n.QuitUserProfile,
                '《ＩＤ暱稱》',
                Response=Command.Enter,
                # LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                i18n.Done,
                '查詢網友',
                BreakDetect=True,
                # LogLevel=Log.Level.DEBUG
            )
        ]
    )

    resultlist = list(filter(None, resultlist))

    return resultlist
