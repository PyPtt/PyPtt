try:
    from . import i18n
    from . import connect_core
    from . import log
    from . import command
except ModuleNotFoundError:
    import i18n
    import connect_core
    import log
    import command


def search_user(
        api: object, ptt_id: str, min_page: int, max_page: int) -> list:
    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('T')
    cmd_list.append(command.Enter)
    cmd_list.append('Q')
    cmd_list.append(command.Enter)
    cmd_list.append(ptt_id)
    cmd = ''.join(cmd_list)

    if min_page is not None:
        template = min_page
    else:
        template = 1

    appendstr = ' ' * template
    cmdtemp = cmd + appendstr

    target_list = [
        connect_core.TargetUnit(
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
        log.log(
            api.config,
            log.level.INFO,
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

    log.log(
        api.config,
        log.level.INFO,
        i18n.ReadComplete
    )

    api.connect_core.send(
        command.Enter,
        [
            # 《ＩＤ暱稱》
            connect_core.TargetUnit(
                i18n.QuitUserProfile,
                '《ＩＤ暱稱》',
                response=command.Enter,
                # log_level=log.level.DEBUG
            ),
            connect_core.TargetUnit(
                i18n.Done,
                '查詢網友',
                break_detect=True,
                # log_level=log.level.DEBUG
            )
        ]
    )

    return list(filter(None, resultlist))
