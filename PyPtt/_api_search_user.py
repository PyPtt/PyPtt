from SingleLog.log import Logger

try:
    from . import i18n
    from . import connect_core
    from . import command
except ModuleNotFoundError:
    import i18n
    import connect_core
    import command


def search_user(
        api: object, ptt_id: str, min_page: int, max_page: int) -> list:

    logger = Logger('search_user', Logger.INFO)

    cmd_list = list()
    cmd_list.append(command.go_main_menu)
    cmd_list.append('T')
    cmd_list.append(command.enter)
    cmd_list.append('Q')
    cmd_list.append(command.enter)
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
            i18n.any_key_continue,
            '任意鍵',
            break_detect=True,
        ),
    ]

    resultlist = list()

    while True:

        api.connect_core.send(
            cmdtemp,
            target_list)
        ori_screen = api.connect_core.get_screen_queue()[-1]
        logger.info(i18n.reading)
        # print(OriScreen)
        # print(len(OriScreen.split('\n')))

        if len(ori_screen.split('\n')) == 2:
            result_id = ori_screen.split('\n')[1]
            result_id = result_id[result_id.find(' ') + 1:].strip()
            # print(result_id)

            resultlist.append(result_id)
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

    logger.info(i18n.read_complete)

    api.connect_core.send(
        command.enter,
        [
            # 《ＩＤ暱稱》
            connect_core.TargetUnit(
                i18n.quit_user_profile,
                '《ＩＤ暱稱》',
                response=command.enter,
                # log_level=Logger.DEBUG
            ),
            connect_core.TargetUnit(
                i18n.done,
                '查詢網友',
                break_detect=True,
                # log_level=Logger.DEBUG
            )
        ]
    )

    return list(filter(None, resultlist))
