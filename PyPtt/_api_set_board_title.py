import PyPtt
from . import command, exceptions, lib_util, check_value
from . import connect_core
from . import i18n


def set_board_title(api: PyPtt.api,
                    board: str,
                    new_title: str) -> None:
    # 第一支板主專用 api
    api._one_thread()

    api._goto_board(board)

    if not api._login_status:
        raise exceptions.Requirelogin(i18n.require_login)

    if api.unregistered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(str, 'board', board)
    check_value.check_type(str, 'new_title', new_title)

    api._check_board(
        board,
        check_moderator=True)

    cmd_list = list()
    cmd_list.append('I')
    cmd_list.append(command.ctrl_p)
    cmd_list.append('b')
    cmd_list.append(command.enter)
    cmd_list.append(command.backspace * 31)
    cmd_list.append(new_title)
    cmd_list.append(command.enter * 2)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.new_settings_have_been_saved,
            '◆ 已儲存新設定',
            break_detect=True,
        ),
        connect_core.TargetUnit(
            i18n.no_changes,
            '◆ 未改變任何設定',
            break_detect=True,
        ),
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout)
