from SingleLog.log import Logger

import PyPtt
from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import lib_util
from . import screens


def mark_post(api: PyPtt.API, mark_type: int, board: str, post_aid: str, post_index: int, search_type: int,
              search_condition: str) -> None:

    _api_util.one_thread(api)

    if not api._login_status:
        raise exceptions.Requirelogin(i18n.require_login)

    if api.unregistered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(int, 'MarkType', mark_type,
                           value_class=data_type.MarkType)
    check_value.check_type(str, 'board', board)
    if post_aid is not None:
        check_value.check_type(str, 'PostAID', post_aid)
    check_value.check_type(int, 'PostIndex', post_index)
    check_value.check_type(int, 'SearchType', search_type,
                           value_class=data_type.SearchType)
    if search_condition is not None:
        check_value.check_type(str, 'SearchCondition', search_condition)

    if len(board) == 0:
        raise ValueError(f'board error parameter: {board}')

    if mark_type != data_type.MarkType.DeleteD:
        if post_index != 0 and isinstance(post_aid, str):
            raise ValueError('wrong parameter post_index and post_aid can\'t both input')

        if post_index == 0 and post_aid is None:
            raise ValueError('wrong parameter post_index or post_aid must input')

    if search_condition is not None and search_type == 0:
        raise ValueError('wrong parameter post_index or post_aid must input')

    if search_type == data_type.SearchType.PUSH:
        try:
            S = int(search_condition)
        except ValueError:
            raise ValueError(f'wrong parameter search_condition: {search_condition}')

        check_value.check_range('search_condition', S, -100, 100)

    if post_aid is not None and search_condition is not None:
        raise ValueError('wrong parameter post_aid and search_condition can\'t both input')

    if post_index != 0:
        newest_index = api.get_newest_index(
            data_type.NewIndex.BBS,
            board=board,
            search_type=search_type,
            search_condition=search_condition)
        check_value.check_index(
            'post_index',
            post_index,
            max_value=newest_index)

    if mark_type == data_type.MarkType.UNCONFIRMED:
        # 批踢踢兔沒有待證文章功能 QQ
        if api.config.host == data_type.HOST.PTT2:
            raise exceptions.HostNotSupport(lib_util.get_current_func_name())

    _api_util._check_board(
        board,
        check_moderator=True)

    _api_util.goto_board(api, board)

    cmd_list = []
    if post_aid is not None:
        cmd_list.append('#' + post_aid)

        cmd_list.append(command.enter)

    elif post_index != 0:
        if search_condition is not None:
            if search_type == data_type.SearchType.KEYWORD:
                cmd_list.append('/')
            elif search_type == data_type.SearchType.AUTHOR:
                cmd_list.append('a')
            elif search_type == data_type.SearchType.PUSH:
                cmd_list.append('Z')
            elif search_type == data_type.SearchType.MARK:
                cmd_list.append('G')
            elif search_type == data_type.SearchType.MONEY:
                cmd_list.append('A')

            cmd_list.append(search_condition)
            cmd_list.append(command.enter)

        cmd_list.append(str(post_index))

        cmd_list.append(command.enter)

    if mark_type == data_type.MarkType.S:
        cmd_list.append('L')
    elif mark_type == data_type.MarkType.D:
        cmd_list.append('t')
    elif mark_type == data_type.MarkType.DeleteD:
        cmd_list.append(command.ctrl_d)
    elif mark_type == data_type.MarkType.M:
        cmd_list.append('m')
    elif mark_type == data_type.MarkType.UNCONFIRMED:
        cmd_list.append(command.ctrl_e + 'S')

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            [i18n.del_all_mark_post],
            '刪除所有標記',
            response='y' + command.enter,
            log_level=Logger.INFO),
        connect_core.TargetUnit(
            [i18n.mark_success],
            screens.Target.InBoard,
            break_detect=True,
            log_level=Logger.INFO),
    ]

    api.connect_core.send(cmd, target_list)
