from __future__ import annotations

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import lib_util
from . import log


def fast_post_step0(api, board: str, title: str, content: str, post_type: int) -> None:
    _api_util.goto_board(api, board)

    cmd_list = []
    cmd_list.append(command.ctrl_p)
    cmd_list.append(str(post_type))
    cmd_list.append(command.enter)
    cmd_list.append(str(title))
    cmd_list.append(command.enter)
    cmd_list.append(str(content))
    cmd_list.append(command.ctrl_x)
    cmd_list.append('s')
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('發表文章於【', break_detect=True),
        connect_core.TargetUnit('使用者不可發言', break_detect=True),
        connect_core.TargetUnit('無法發文: 未達看板要求權限', break_detect=True),
        connect_core.TargetUnit('任意鍵繼續', break_detect=True),
        connect_core.TargetUnit('確定要儲存檔案嗎', break_detect=True)
    ]
    index = api.connect_core.fast_send(cmd, target_list)
    if index < 0:
        raise exceptions.UnknownError('UnknownError')
    if index == 1 or index == 2:
        raise exceptions.NoPermission(i18n.no_permission)


def fast_post_step1(api: object, sign_file) -> None:
    cmd = '\r'

    target_list = [
        connect_core.TargetUnit('發表文章於【', break_detect=True),
        connect_core.TargetUnit('使用者不可發言', break_detect=True),
        connect_core.TargetUnit('無法發文: 未達看板要求權限', break_detect=True),
        connect_core.TargetUnit('任意鍵繼續', break_detect=True),
        connect_core.TargetUnit('確定要儲存檔案嗎', break_detect=True),
        connect_core.TargetUnit('x=隨機', response=str(sign_file) + '\r'),
    ]
    index = api.connect_core.fast_send(cmd, target_list)
    if index < 0:
        raise exceptions.UnknownError('UnknownError')


def fast_post(
        api: object,
        board: str,
        title: str,
        content: str,
        post_type: int,
        sign_file) -> None:
    _api_util.goto_board(api, board)

    cmd_list = []
    cmd_list.append(command.ctrl_p)
    cmd_list.append(str(post_type))
    cmd_list.append(command.enter)
    cmd_list.append(str(title))
    cmd_list.append(command.enter)
    cmd_list.append(str(content))
    cmd_list.append(command.ctrl_x)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('發表文章於【', break_detect=True),
        connect_core.TargetUnit('使用者不可發言', break_detect=True),
        connect_core.TargetUnit('無法發文: 未達看板要求權限', break_detect=True),
        connect_core.TargetUnit('任意鍵繼續', break_detect=True),
        connect_core.TargetUnit('確定要儲存檔案嗎', response='s' + command.enter),
        connect_core.TargetUnit('x=隨機', response=str(sign_file) + command.enter),
    ]
    index = api.connect_core.fast_send(cmd, target_list)
    if index < 0:
        raise exceptions.UnknownError('UnknownError')
    if index == 1 or index == 2:
        raise exceptions.NoPermission(i18n.no_permission)


sign_file_list = [str(x) for x in range(0, 10)]
sign_file_list.append('x')


# --- post()'s `anonymous` / `display_id` params (issue #84) ---
#
# pttbbs only shows the "請輸入你想用的ID" / "確定[y/N]?" prompt pair when the
# *board itself* carries BRD_ANONYMOUS server-side (mbbsd/edit.c write_header,
# `if (currbrdattr & BRD_ANONYMOUS)`). On a normal board the two TargetUnits
# below simply never match anything on screen -- there is no way for PyPtt to
# force anonymity on a board that isn't flagged anonymous. See
# scripts/mkboard.py / scripts/bootstrap_local_pttbbs.py's AnonTest board for
# how to provision one locally.
#
# Response mapping, matching pttbbs' own rules for that prompt:
#   anonymous=False              -> 'r' (real userid; safe default, and a
#                                    no-op on non-anonymous boards)
#   anonymous=True,  no display_id -> '' (Enter; "Anonymous." -- pttbbs
#                                    appends the same trailing '.' as the
#                                    display_id case below -- on a
#                                    default-anonymous board, real userid
#                                    otherwise -- pttbbs' own behavior)
#   anonymous=True,  display_id  -> that string; pttbbs appends a trailing
#                                    '.' to it (e.g. display_id='Fox' shows
#                                    up as author 'Fox.') -- fixed pttbbs
#                                    behavior, not adjustable by PyPtt.
def _anonymous_response(anonymous: bool, display_id: [str | None]) -> str:
    if display_id is not None:
        check_value.check_type(display_id, str, 'display_id')
        if not anonymous:
            raise exceptions.ParameterError('display_id requires anonymous=True')
        # pttbbs (mbbsd/edit.c) treats a leading '-' as "this is a deleted
        # name" and re-shows the same prompt instead of accepting it, which
        # would make PyPtt's TargetUnit answer it the same way forever.
        if display_id.startswith('-'):
            raise exceptions.ParameterError("display_id must not start with '-'")
        for c in display_id:
            if ord(c) < 0x20 or ord(c) == 0x7f:
                raise exceptions.ParameterError(
                    f'display_id must not contain control characters (found {c!r})')
        return display_id

    return '' if anonymous else 'r'


def post(api, board: str, title: str, content: str, title_index: int, sign_file: [str | int],
         anonymous: bool = False, display_id: [str | None] = None) -> None:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(board, str, 'board')
    check_value.check_type(title_index, int, 'title_index')
    check_value.check_type(title, str, 'title')
    check_value.check_type(content, str, 'content')
    check_value.check_type(anonymous, bool, 'anonymous')

    if str(sign_file).lower() not in sign_file_list:
        raise exceptions.ParameterError(f'wrong parameter sign_file: {sign_file}')

    anonymous_response = _anonymous_response(anonymous, display_id)

    _api_util.check_board(api, board)
    _api_util.goto_board(api, board)

    log.logger.info(i18n.post)

    cmd_list = []
    cmd_list.append(command.ctrl_p)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('發表文章於【', break_detect=True),
        connect_core.TargetUnit('使用者不可發言', break_detect=True),
        connect_core.TargetUnit('無法發文: 未達看板要求權限', break_detect=True),
    ]
    index = api.connect_core.send(cmd, target_list)
    if index < 0:
        raise exceptions.UnknownError('UnknownError')
    if index == 1 or index == 2:
        log.logger.info(i18n.post, '...', i18n.fail)
        raise exceptions.NoPermission(i18n.no_permission)

    log.logger.debug(i18n.has_post_permission)

    content = lib_util.uniform_new_line(content)

    cmd_list = []
    cmd_list.append(str(title_index))
    cmd_list.append(command.enter)
    cmd_list.append(str(title))
    cmd_list.append(command.enter)
    cmd_list.append(command.ctrl_y * 40)
    cmd_list.append(str(content))
    cmd_list.append(command.ctrl_x)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('任意鍵繼續', break_detect=True),
        # max_match=1: pttbbs' "檔案處理" screen keeps every answered prompt's
        # echoed text on screen as the flow proceeds through the next ones
        # (confirmed live -- "確定要儲存檔案嗎？ s" stays visible through the
        # anonymous-post prompts below). Without max_match=1 this target
        # re-matches on every later screen in the same flow and re-sends
        # 's' + Enter into whatever field currently has focus (e.g. the
        # anonymous-ID or confirm prompt), corrupting the answer.
        connect_core.TargetUnit('確定要儲存檔案嗎', response='s' + command.enter, max_match=1),
        # Only shown on a BRD_ANONYMOUS board -- no-op on a normal board.
        connect_core.TargetUnit('請輸入你想用的ID', response=anonymous_response + command.enter, max_match=1),
        connect_core.TargetUnit('確定[y/N]', response='y' + command.enter, max_match=1),
        connect_core.TargetUnit('x=隨機', response=str(sign_file) + command.enter),
    ]
    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_post_timeout)

    log.logger.info(i18n.post, '...', i18n.success)
