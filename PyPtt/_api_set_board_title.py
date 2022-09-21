from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import lib_util


def set_board_title(api, board: str, new_title: str) -> None:
    # 第一支板主專用 api
    _api_util.one_thread(api)

    _api_util.goto_board(api, board)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(board, str, 'board')
    check_value.check_type(new_title, str, 'new_title')

    _api_util.check_board(
        api,
        board,
        check_moderator=True)

    cmd_list = []
    cmd_list.append('I')
    cmd_list.append(command.ctrl_p)
    cmd_list.append('b')
    cmd_list.append(command.enter)
    cmd_list.append(command.backspace * 31)
    cmd_list.append(new_title)
    cmd_list.append(command.enter * 2)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('◆ 已儲存新設定', break_detect=True),
        connect_core.TargetUnit('◆ 未改變任何設定', break_detect=True),
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout)
