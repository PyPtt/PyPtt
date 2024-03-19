from __future__ import annotations

from typing import Optional

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import lib_util
from . import screens


def del_post(api, board: str, post_aid: Optional[str] = None, post_index: int = 0) -> None:
    _api_util.one_thread(api)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    check_value.check_type(board, str, 'board')
    if post_aid is not None:
        check_value.check_type(post_aid, str, 'PostAID')
    check_value.check_type(post_index, int, 'PostIndex')

    if len(board) == 0:
        raise ValueError(f'board error parameter: {board}')

    if post_index != 0 and isinstance(post_aid, str):
        raise ValueError('wrong parameter index and aid can\'t both input')

    if post_index == 0 and post_aid is None:
        raise ValueError('wrong parameter index or aid must input')

    if post_index != 0:
        newest_index = api.get_newest_index(
            data_type.NewIndex.BOARD,
            board=board)
        check_value.check_index(
            'PostIndex',
            post_index,
            newest_index)

    board_info = _api_util.check_board(api, board)

    check_author = True
    for moderator in board_info[data_type.BoardField.moderators]:
        if api.ptt_id.lower() == moderator.lower():
            check_author = False
            break

    api.logger.info(i18n.delete_post)

    post_info = api.get_post(board, aid=post_aid, index=post_index, query=True)
    if post_info[data_type.PostField.post_status] != data_type.PostStatus.EXISTS:
        # delete success
        api.logger.info(i18n.success)
        return

    if check_author:
        if api.ptt_id.lower() != post_info[data_type.PostField.author].lower():
            raise exceptions.NoPermission(i18n.no_permission)

    _api_util.goto_board(api, board)

    cmd_list = []

    if post_aid is not None:
        cmd_list.append(lib_util.check_aid(post_aid))
    elif post_index != 0:
        cmd_list.append(str(post_index))
    else:
        raise ValueError('post_aid and post_index cannot be None at the same time')

    cmd_list.append(command.enter)
    cmd_list.append('d')

    cmd = ''.join(cmd_list)

    api.confirm = False

    def confirm_delete_handler(screen):
        api.confirm = True

    target_list = [
        connect_core.TargetUnit('請按任意鍵繼續', response=' '),
        connect_core.TargetUnit('請確定刪除(Y/N)?[N]', response='y' + command.enter, handler=confirm_delete_handler,
                                max_match=1),
        connect_core.TargetUnit(screens.Target.InBoard, break_detect=True),
    ]

    index = api.connect_core.send(
        cmd,
        target_list)

    # last_screen = api.connect_core.get_screen_queue()[-1]
    # print(api.confirm)
    # print(last_screen)
    # print(index)

    if index == 1:
        if not api.confirm:
            raise exceptions.NoPermission(i18n.no_permission)

    api.logger.info(i18n.success)
