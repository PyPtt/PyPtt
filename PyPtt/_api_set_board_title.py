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

    # mbbsd/board.c:641 vgetstr(genbuf, BTLEN-16, ...) with BTLEN=48 gives
    # len=32; vtuikit.c:1409-1415's vkey_purge() clears the input queue one
    # byte early, so the safe limit is 32-2=30 Big5 bytes, not 31.
    try:
        encoded_new_title = new_title.encode('big5uao')
    except UnicodeEncodeError as e:
        raise exceptions.ParameterError(
            f'new_title contains a character that cannot be encoded in Big5: {e}') from e
    if len(encoded_new_title) > 30:
        raise exceptions.ParameterError('new_title must not exceed 30 bytes')

    _api_util.check_board(
        api,
        board,
        check_moderator=True)

    # check_board() above calls get_board_info(get_post_kind=False) (to look
    # up the moderator list) whenever the board isn't already cached, and
    # that helper reads the board's "《board》看板設定" info screen but never
    # dismisses its trailing "[按任意鍵繼續]" prompt. Left alone, the 'I'
    # below lands on that prompt instead of the board's article-list screen:
    # it gets consumed as the "any key" dismissal, so the following ctrl_p
    # is read as the article-list's own "[Ctrl-P]發表文章" shortcut and the
    # whole command ends up composing a new post instead of opening board
    # settings. Verified live against a moderated board: without this
    # re-navigation the send always lands in the article editor; with it,
    # the confirmation targets below match every time (8/8 in local testing).
    _api_util.goto_board(api, board)

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

    index = api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout)
    if index < 0:
        ori_screen = api.connect_core.get_screen_queue()[-1]
        raise exceptions.UnknownError(ori_screen)
