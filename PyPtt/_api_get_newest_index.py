from __future__ import annotations

import re

from SingleLog import DefaultLogger
from SingleLog import LogLevel

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import data_type, lib_util
from . import exceptions
from . import i18n
from . import screens


def _get_newest_index(api) -> int:
    logger = DefaultLogger('api', api.config.log_level)

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
    for index_temp in all_index:
        need_continue = True
        if index_temp > max_check_range:
            check_range = max_check_range
        else:
            check_range = index_temp
        for i in range(1, check_range):
            if str(index_temp - i) not in last_screen:
                need_continue = False
                break
        if need_continue:
            logger.debug(i18n.find_newest_index, index_temp)
            newest_index = index_temp
            break

    if newest_index == 0:
        last_screen = api.connect_core.get_screen_queue()[-1]
        print(last_screen)
        raise exceptions.UnknownError('UnknownError')

    return newest_index


def get_newest_index(api, index_type: data_type.NewIndex, board: [str | None] = None,
                     search_type: data_type.SearchType = None, search_condition: [str | None] = None,
                     search_list: [list | None] = None) -> int:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if search_type is None:
        search_type = data_type.SearchType.NOPE

    check_value.check_type(index_type, data_type.NewIndex, 'index_type')
    check_value.check_type(search_type, data_type.SearchType, 'search_type')

    if index_type == data_type.NewIndex.MAIL:
        if not api.is_registered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        if board is not None:
            raise ValueError('board should not input at NewIndex.MAIL.')

    if search_condition is not None:
        check_value.check_type(search_condition, str, 'search_condition')

    if search_list is not None:
        check_value.check_type(search_list, list, 'search_list')

    if index_type == data_type.NewIndex.BOARD:

        check_value.check_type(board, str, 'board')

        _api_util.check_board(api, board)
        _api_util.goto_board(api, board)

        cmd_list, normal_newest_index = _api_util.get_search_condition_cmd(api, index_type, board, search_type,
                                                                           search_condition, search_list)

        cmd_list.append('1')
        cmd_list.append(command.enter)
        cmd_list.append('$')

        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit('沒有文章...', log_level=LogLevel.DEBUG, break_detect=True),
            connect_core.TargetUnit(screens.Target.InBoard, log_level=LogLevel.DEBUG, break_detect=True),
            connect_core.TargetUnit(screens.Target.InBoardWithCursor, log_level=LogLevel.DEBUG, break_detect=True),
            connect_core.TargetUnit(screens.Target.MainMenu_Exiting,
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

    elif index_type == data_type.NewIndex.MAIL:

        cmd_list = []
        cmd_list.append(command.go_main_menu)
        cmd_list.append(command.ctrl_z)
        cmd_list.append('m')

        _cmd_list, normal_newest_index = _api_util.get_search_condition_cmd(api, index_type, board, search_type,
                                                                            search_condition, search_list)
        # print('normal_newest_index', normal_newest_index)

        cmd_list.extend(_cmd_list)
        cmd_list.append(command.ctrl_f * 50)

        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit(screens.Target.InMailBox, break_detect=True),
            connect_core.TargetUnit(screens.Target.CursorToGoodbye, log_level=LogLevel.DEBUG, break_detect=True),
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
