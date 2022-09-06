import re

try:
    from . import data_type
    from . import i18n
    from . import connect_core
    from . import log
    from . import screens
    from . import exceptions
    from . import command
    from . import check_value
    from . import _api_util
except ModuleNotFoundError:
    import data_type
    import i18n
    import connect_core
    import log
    import screens
    import exceptions
    import command
    import check_value
    import _api_util


def _get_newest_index(api) -> int:
    last_screen = api.connect_core.get_screen_queue()[-1]
    # print(last_screen)
    last_screen_list = last_screen.split('\n')
    last_screen_list = last_screen_list[3:]
    last_screen_list = '\n'.join([x[:9] for x in last_screen_list])
    # print(last_screen_list)
    all_index = re.findall(r'\d+', last_screen_list)

    if len(all_index) == 0:
        # print(last_screen)
        # raise exceptions.UnknownError(i18n.UnknownError)
        return 0

    all_index = list(map(int, all_index))
    all_index.sort(reverse=True)
    # print(all_index)

    max_check_range = 6
    newest_index = 0
    for IndexTemp in all_index:
        need_continue = True
        if IndexTemp > max_check_range:
            check_range = max_check_range
        else:
            check_range = IndexTemp
        for i in range(1, check_range):
            if str(IndexTemp - i) not in last_screen:
                need_continue = False
                break
        if need_continue:
            log.show_value(
                api.config,
                log.level.DEBUG,
                i18n.FindNewestIndex,
                IndexTemp)
            newest_index = IndexTemp
            break

    if newest_index == 0:
        last_screen = api.connect_core.get_screen_queue()[-1]
        print(last_screen)
        raise exceptions.UnknownError(i18n.UnknownError)

    return newest_index


def get_newest_index(
        api,
        index_type: int,
        search_type: int = 0,
        search_condition: str = None,
        search_list: list = None,
        # BBS
        board: str = None) -> int:
    if index_type == data_type.index_type.BBS:

        check_value.check(api.config, str, 'Board', board)

        api._check_board(board)
        api._goto_board(board)

        cmd_list, normal_newest_index = _api_util.get_search_condition_cmd(
            api,
            index_type,
            search_type,
            search_condition,
            search_list,
            board)

        cmd_list.append('1')
        cmd_list.append(command.Enter)
        cmd_list.append('$')

        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit(
                i18n.NoPost,
                '沒有文章...',
                break_detect=True,
                log_level=log.level.DEBUG),
            connect_core.TargetUnit(
                i18n.Success,
                screens.Target.InBoard,
                break_detect=True,
                log_level=log.level.DEBUG),
            connect_core.TargetUnit(
                i18n.Success,
                screens.Target.InBoardWithCursor,
                break_detect=True,
                log_level=log.level.DEBUG),
            connect_core.TargetUnit(
                i18n.NoSuchBoard,
                screens.Target.MainMenu_Exiting,
                exceptions_=exceptions.NoSuchBoard(api.config, board)),
        ]
        index = api.connect_core.send(cmd, target_list)
        if index < 0:
            # OriScreen = api.connect_core.getScreenQueue()[-1]
            # print(OriScreen)
            raise exceptions.NoSuchBoard(api.config, board)

        if index == 0:
            return 0

        newest_index = _get_newest_index(api)

        if normal_newest_index == newest_index:
            raise exceptions.NoSearchResult()

    elif index_type == data_type.index_type.MAIL:

        cmd_list = list()
        cmd_list.append(command.GoMainMenu)
        cmd_list.append(command.Ctrl_Z)
        cmd_list.append('m')

        _cmd_list, normal_newest_index = _api_util.get_search_condition_cmd(
            api,
            index_type,
            search_type,
            search_condition,
            search_list,
            board)
        # print('normal_newest_index', normal_newest_index)

        cmd_list.extend(_cmd_list)
        cmd_list.append(command.Ctrl_F * 50)

        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit(
                i18n.MailBox,
                screens.Target.InMailBox,
                break_detect=True),
            connect_core.TargetUnit(
                i18n.NoMail,
                screens.Target.CursorToGoodbye,
                break_detect=True,
                log_level=log.level.DEBUG),
        ]

        def get_index(api):
            current_capacity, _ = _api_util.get_mailbox_capacity(api)
            last_screen = api.connect_core.get_screen_queue()[-1]
            cursor_line = [x for x in last_screen.split('\n') if x.strip().startswith(api.cursor)][0]
            # print('---->', cursor_line)
            list_index = int(re.compile('(\d+)').search(cursor_line).group(0))

            # print('----> list_index', list_index)
            # print('----> current_capacity', current_capacity)
            if search_type == 0 and search_list is None:
                if list_index > current_capacity:
                    newest_index = list_index
                else:
                    newest_index = current_capacity
            else:
                newest_index = list_index

            return newest_index

        for i in range(3):
            index = api.connect_core.send(
                cmd,
                target_list)
            # print('index', index)
            # last_screen = api.connect_core.get_screen_queue()[-1]
            # print(last_screen)

            if index == 0:
                newest_index = get_index(api)
                if normal_newest_index == newest_index:
                    if i == 2:
                        raise exceptions.NoSearchResult()
                    else:
                        continue
                break
            newest_index = 0

    return newest_index
