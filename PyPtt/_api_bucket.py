from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import lib_util
from . import screens

from .data_type import UserField

import re

def _bucket_operation_reset(api, board: str, ptt_id: str):
    """
    1. Confirm api login and the user is a moderator of the board.
    2. Confirm the existence of ptt_id
    3. goto the board
    """
    check_value.check_type(board, str, 'board')
    check_value.check_type(ptt_id, str, 'ptt_id')

    # Confirm single thread
    _api_util.one_thread(api)

    # Confirm login status
    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    # Confirm the user is registered
    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    # Confirm the existence of the target user_id
    api.get_user(ptt_id)

    # Confirm moderator status
    _api_util.check_board(api, board, check_moderator=True)

    # Move cursor to the board
    _api_util.goto_board(api, board)

def bucket(api, board: str, bucket_days: int, reason: str, ptt_id: str) -> None:
    _bucket_operation_reset(api, board, ptt_id)

    check_value.check_type(bucket_days, int, 'bucket_days')
    check_value.check_type(reason, str, 'reason')

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

def lift_bucket(api, board: str, ptt_id: str, reason: str) -> None:
    """提前解除水桶

    Args:
        api (_type_): _description_
        board (str): 板名
        ptt_id (str): ptt_id
        reason: 解除水桶裡由
    """
    _bucket_operation_reset(api, board, ptt_id)

    check_value.check_type(reason, str, 'reason')

    cmd_list = []
    cmd_list.append('i')
    cmd_list.append(command.ctrl_p)
    cmd_list.append('w')
    cmd_list.append(command.enter)
    cmd_list.append('d')
    cmd_list.append(command.enter)
    cmd_list.append(ptt_id)
    cmd_list.append(command.enter)
    cmd_lift_bucket = ''.join(cmd_list)

    cmd_list = []
    cmd_list.append(reason)
    cmd_list.append(command.enter)
    cmd_list.append('y')
    cmd_list.append(command.enter)
    cmd_lift_bucket_reason = ''.join(cmd_list)

    target_lift_bucket = [
        connect_core.TargetUnit('請輸入理由(空白可取消解除)', response=cmd_lift_bucket_reason),
        connect_core.TargetUnit('其它鍵結束', response=command.enter),
        connect_core.TargetUnit('權限設定系統', response=command.enter),
        connect_core.TargetUnit('任意鍵', response=command.space),
        connect_core.TargetUnit(screens.Target.InBoard, break_detect=True)
    ]

    api.connect_core.send(
        cmd_lift_bucket,
        target_lift_bucket)


def get_bucket_status(api, board: str, ptt_id: str) -> None:
    _bucket_operation_reset(api, board, ptt_id)

    cmd_list = []
    cmd_list.append('i')
    cmd_list.append(command.ctrl_p)
    cmd_list.append('w')
    cmd_list.append(command.enter)
    cmd_list.append('s')
    cmd_list.append(command.enter)
    cmd_list.append(ptt_id)
    cmd_list.append(command.enter)
    cmd_check_bucket_status = ''.join(cmd_list)

    target_list_check_status = [
        connect_core.TargetUnit('任意鍵', break_detect=True),
    ]

    api.connect_core.send(
        cmd_check_bucket_status,
        target_list_check_status)

    result = { UserField.is_suspended   : False,
               UserField.remaining_days : -1}

    # ori_screen should contain either of the following cases
    # Case 1: 暫停使用者 ANava 發言，解除時間尚有 35 天: 04/10/2025 08:46:34
    # Case 2: 使用者 arrenwu 目前不在禁言名單中。
    ori_screen = api.connect_core.get_screen_queue()[-1]

    REMAINING_DAYS_PATTERN = re.compile(r"解除時間尚有 *(?P<days>\d+) *天")
    if '目前不在禁言名單中' in ori_screen:
        result[UserField.remaining_days] = 0
    else:
        result[UserField.is_suspended] = True
        match_result = REMAINING_DAYS_PATTERN.search(ori_screen)
        result[UserField.remaining_days] = int(match_result['days'])

    # Go back to the board view.
    cmd_list = []
    cmd_list.append(command.space)
    cmd_part_back_to_board = ''.join(cmd_list)

    target_list = [
        # connect_core.TargetUnit('◆ 使用者之前已被禁言', exceptions_=exceptions.UserHasPreviouslyBeenBanned()),
        connect_core.TargetUnit('(A)增加 (D)提前清除 (S)取得目前狀態 (L)列出設定歷史', response=command.enter),
        connect_core.TargetUnit('其它鍵結束', response=command.enter),
        connect_core.TargetUnit('任意鍵', response=command.space),
        connect_core.TargetUnit(screens.Target.InBoard, break_detect=True),
    ]
    api.connect_core.send(
            cmd_part_back_to_board,
            target_list)

    return result
