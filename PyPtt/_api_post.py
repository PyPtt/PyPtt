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


def post(api, board: str, title: str, content: str, title_index: int, sign_file: [str | int]) -> None:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(board, str, 'board')
    check_value.check_type(title_index, int, 'title_index')
    check_value.check_type(title, str, 'title')
    check_value.check_type(content, str, 'content')

    if str(sign_file).lower() not in sign_file_list:
        raise ValueError(f'wrong parameter sign_file: {sign_file}')

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
        connect_core.TargetUnit('確定要儲存檔案嗎', response='s' + command.enter),
        connect_core.TargetUnit('x=隨機', response=str(sign_file) + command.enter),
    ]
    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_post_timeout)

    log.logger.info(i18n.post, '...', i18n.success)
