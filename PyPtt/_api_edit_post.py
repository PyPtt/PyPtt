from urllib.parse import scheme_chars

from build.lib.PyPtt.command import refresh
from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import lib_util
from . import log
from . import screens


def edit_post(api, board: str, post_aid: str, post_index: int, new_content: str, new_title: str) -> None:
    _api_util.one_thread(api)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    check_value.check_type(board, str, 'board')
    if post_aid is not None:
        check_value.check_type(post_aid, str, 'PostAID')
    check_value.check_type(post_index, int, 'PostIndex')

    if new_content is not None:
        check_value.check_type(new_content, str, 'NewContent')
    if new_title is not None:
        check_value.check_type(new_title, str, 'NewTitle')

    if len(board) == 0:
        raise exceptions.ParameterError(f'board error parameter: {board}')

    if post_index != 0 and isinstance(post_aid, str):
        raise exceptions.ParameterError('wrong parameter index and aid can\'t both input')

    if post_index == 0 and post_aid is None:
        raise exceptions.ParameterError('wrong parameter index or aid must input')

    if post_index != 0:
        newest_index = api.get_newest_index(
            data_type.NewIndex.BOARD,
            board=board)
        check_value.check_index(
            'PostIndex',
            post_index,
            newest_index)

    log.logger.info(i18n.edit_post)

    post_info = api.get_post(board, aid=post_aid, index=post_index)
    if not post_info[data_type.PostField.author].lower().startswith(api.ptt_id.lower()):
        log.logger.info(i18n.edit_post, '...', i18n.fail)
        raise exceptions.NoPermission(i18n.no_permission)

    cmd_list = []
    cmd_list.append(command.left)
    #
    # print(new_title, new_content)
    # print(len(new_title), len(new_content))

    if new_title is not None:

        last_screen = api.connect_core.get_screen_queue()[-1]
        print('!!!!! 1', last_screen)

        cmd_list.append('T')
        cmd_list.append(command.backspace * 63)
        cmd_list.append(new_title)
        cmd_list.append(command.enter)
        cmd_list.append('Y')
        cmd_list.append(command.enter)

        cmd = ''.join(cmd_list)
        cmd_list = []

        screens.Target.EditTitle = screens.Target.EditTitle[:screens.Target.EditTitleLen]
        screens.Target.EditTitle.append(api.cursor)

        target_list = [
            connect_core.TargetUnit(screens.Target.InBoardWithCursor, break_detect=True)
        ]

        index = api.connect_core.send(
            cmd,
            target_list
        )

    if new_content is not None:
        new_content = lib_util.uniform_new_line(new_content)

        cmd_list.append('E')
        cmd_list.append(command.ctrl_y * len(post_info[data_type.PostField.full_content].splitlines()))
        cmd_list.append(new_content)
        cmd_list.append(command.ctrl_x)

        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit('任意鍵繼續', break_detect=True),
            connect_core.TargetUnit('確定要儲存檔案嗎', response='s' + command.enter),
            connect_core.TargetUnit(screens.Target.InBoard, break_detect=True),
        ]
        api.connect_core.send(
            cmd,
            target_list,
            screen_timeout=api.config.screen_post_timeout)


    log.logger.info(i18n.edit_post, '...', i18n.success)
