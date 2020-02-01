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


def search_user(
        api: object, pttid: str, min_page: int, max_page: int) -> list:
    cmd_list = []
    cmd_list.append(Command.GoMainMenu)
    cmd_list.append('T')
    cmd_list.append(Command.Enter)
    cmd_list.append('Q')
    cmd_list.append(Command.Enter)
    cmd_list.append(pttid)
    cmd = ''.join(cmd_list)

    if min_page is not None:
        template = min_page
    else:
        template = 1

    appendstr = ' ' * template
    cmdtemp = cmd + appendstr

    target_list = [
        ConnectCore.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵',
            break_detect=True,
        ),
    ]

    resultlist = []

    while True:

        api.connect_core.send(
            cmdtemp,
            target_list
        )
        ori_screen = api.connect_core.get_screen_queue()[-1]
        Log.log(
            api.config,
            Log.Level.INFO,
            i18n.Reading
        )
        # print(OriScreen)
        # print(len(OriScreen.split('\n')))

        if len(ori_screen.split('\n')) == 2:
            resultid = ori_screen.split('\n')[1]
            resultid = resultid[resultid.find(' ') + 1:].strip()
            # print(resultid)

            resultlist.append(resultid)
            break
        else:

            ori_screen = ori_screen.split('\n')[3:-1]
            ori_screen = '\n'.join(ori_screen)

            templist = ori_screen.replace('\n', ' ')

            while '  ' in templist:
                templist = templist.replace('  ', ' ')

            templist = templist.split(' ')
            resultlist.extend(templist)

            # print(templist)
            # print(len(templist))

            if len(templist) != 100 and len(templist) != 120:
                break

            template += 1
            if max_page is not None:
                if template > max_page:
                    break

            cmdtemp = ' '

    Log.log(
        api.config,
        Log.Level.INFO,
        i18n.ReadComplete
    )

    api.connect_core.send(
        Command.Enter,
        [
            # 《ＩＤ暱稱》
            ConnectCore.TargetUnit(
                i18n.QuitUserProfile,
                '《ＩＤ暱稱》',
                response=Command.Enter,
                # log_level=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                i18n.Done,
                '查詢網友',
                break_detect=True,
                # log_level=Log.Level.DEBUG
            )
        ]
    )

    return list(filter(None, resultlist))
