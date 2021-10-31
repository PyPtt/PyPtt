from SingleLog.log import Logger

from . import data_type
from . import i18n
from . import connect_core
from . import screens
from . import command
from . import check_value
from . import exceptions
from . import lib_util


def mark_post(
        api,
        mark_type: int,
        board: str,
        post_aid: str,
        post_index: int,
        search_type: int,
        search_condition: str) -> None:
    logger = Logger('mark_post', Logger.INFO)

    check_value.check_type(int, 'mark_type', mark_type,
                           value_class=data_type.mark_type)
    check_value.check_type(str, 'board', board)
    if post_aid is not None:
        check_value.check_type(str, 'PostAID', post_aid)
    check_value.check_type(int, 'PostIndex', post_index)
    check_value.check_type(int, 'SearchType', search_type,
                           value_class=data_type.post_search_type)
    if search_condition is not None:
        check_value.check_type(str,
                          'SearchCondition', search_condition)

    if len(board) == 0:
        raise ValueError(f'board error parameter: {board}')

    if mark_type != data_type.mark_type.DeleteD:
        if post_index != 0 and isinstance(post_aid, str):
            raise ValueError('wrong parameter post_index and post_aid can\'t both input')

        if post_index == 0 and post_aid is None:
            raise ValueError('wrong parameter post_index or post_aid must input')

    if search_condition is not None and search_type == 0:
        raise ValueError('wrong parameter post_index or post_aid must input')

    if search_type == data_type.post_search_type.PUSH:
        try:
            S = int(search_condition)
        except ValueError:
            raise ValueError(f'wrong parameter search_condition: {search_condition}')

        check_value.check_range('search_condition', S, -100, 100)

    if post_aid is not None and search_condition is not None:
        raise ValueError('wrong parameter post_aid and search_condition can\'t both input')

    if post_index != 0:
        newest_index = api._get_newest_index(
            data_type.index_type.BBS,
            board=board,
            search_type=search_type,
            search_condition=search_condition)
        check_value.check_index(
            'post_index',
            post_index,
            max_value=newest_index)

    if mark_type == data_type.mark_type.UNCONFIRMED:
        # 批踢踢兔沒有待證文章功能 QQ
        if api.config.host == data_type.host_type.PTT2:
            raise exceptions.HostNotSupport(lib_util.get_current_func_name())

    api._check_board(
        board,
        check_moderator=True)

    api._goto_board(board)

    cmd_list = list()
    if post_aid is not None:
        cmd_list.append('#' + post_aid)

        cmd_list.append(command.enter)

    elif post_index != 0:
        if search_condition is not None:
            if search_type == data_type.post_search_type.KEYWORD:
                cmd_list.append('/')
            elif search_type == data_type.post_search_type.AUTHOR:
                cmd_list.append('a')
            elif search_type == data_type.post_search_type.PUSH:
                cmd_list.append('Z')
            elif search_type == data_type.post_search_type.MARK:
                cmd_list.append('G')
            elif search_type == data_type.post_search_type.MONEY:
                cmd_list.append('A')

            cmd_list.append(search_condition)
            cmd_list.append(command.enter)

        cmd_list.append(str(post_index))

        cmd_list.append(command.enter)

    if mark_type == data_type.mark_type.S:
        cmd_list.append('L')
    elif mark_type == data_type.mark_type.D:
        cmd_list.append('t')
    elif mark_type == data_type.mark_type.DeleteD:
        cmd_list.append(command.ctrl_d)
    elif mark_type == data_type.mark_type.M:
        cmd_list.append('m')
    elif mark_type == data_type.mark_type.UNCONFIRMED:
        cmd_list.append(command.ctrl_e + 'S')

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            [i18n.DelAllMarkPost],
            '刪除所有標記',
            response='y' + command.enter,
            log_level=Logger.INFO),
        connect_core.TargetUnit(
            [
                i18n.Mark,
                i18n.success,
            ],
            screens.Target.InBoard,
            break_detect=True,
            log_level=Logger.INFO),
    ]

    api.connect_core.send(cmd, target_list)
