from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import lib_util
from . import screens


def bucket(api, board: str, bucket_days: int, reason: str, ptt_id: str) -> None:
    _api_util.one_thread(api)

    # log.py = DefaultLogger('api', api.config.log_level)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(board, str, 'board')
    check_value.check_type(bucket_days, int, 'bucket_days')
    check_value.check_type(reason, str, 'reason')
    check_value.check_type(ptt_id, str, 'ptt_id')

    api.get_user(ptt_id)

    _api_util.check_board(api, board, check_moderator=True)

    _api_util.goto_board(api, board)

    cmd_list = []
    cmd_list.append('i')
    cmd_list.append(command.ctrl_p)
    cmd_list.append('w')
    cmd_list.append(command.enter)
    cmd_list.append('a')
    cmd_list.append(command.enter)
    cmd_list.append(ptt_id)
    cmd_list.append(command.enter)
    cmd = ''.join(cmd_list)

    cmd_list = []
    cmd_list.append(str(bucket_days))
    cmd_list.append(command.enter)
    cmd_list.append(reason)
    cmd_list.append(command.enter)
    cmd_list.append('y')
    cmd_list.append(command.enter)
    cmd_part2 = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('◆ 使用者之前已被禁言', exceptions_=exceptions.UserHasPreviouslyBeenBanned()),
        connect_core.TargetUnit('請以數字跟單位(預設為天)輸入期限', response=cmd_part2),
        connect_core.TargetUnit('其它鍵結束', response=command.enter),
        connect_core.TargetUnit('權限設定系統', response=command.enter),
        connect_core.TargetUnit('任意鍵', response=command.space),
        connect_core.TargetUnit(screens.Target.InBoard, break_detect=True),
    ]

    api.connect_core.send(
        cmd,
        target_list)

    # OriScreen = api.connect_core.getScreenQueue()[-1]
