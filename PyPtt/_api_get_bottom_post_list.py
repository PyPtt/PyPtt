from SingleLog import DefaultLogger
from SingleLog import LogLevel

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import screens


def get_bottom_post_list(api, board):
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    check_value.check_type(board, str, 'board')
    _api_util.check_board(api, board)

    _api_util.goto_board(api, board, end=True)

    logger = DefaultLogger('get_bottom_post_list')

    last_screen = api.connect_core.get_screen_queue()[-1]

    bottom_screen = [line for line in last_screen.split('\n') if '★' in line[:8]]
    bottom_length = len(bottom_screen)

    if bottom_length == 0:
        logger.info(i18n.catch_bottom_post_success)
        return list()

    cmd_list = []
    cmd_list.append(command.query_post)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(screens.Target.QueryPost, log_level=LogLevel.DEBUG, break_detect=True, refresh=False),
        connect_core.TargetUnit(screens.Target.InBoard, log_level=LogLevel.DEBUG, break_detect=True),
        connect_core.TargetUnit(screens.Target.MainMenu_Exiting, exceptions_=exceptions.NoSuchBoard(api.config, board)),
    ]

    aid_list = []

    result = []
    for _ in range(bottom_length):
        api.connect_core.send(cmd, target_list)
        last_screen = api.connect_core.get_screen_queue()[-1]

        lock_post, post_author, post_title, post_aid, post_web, post_money, list_date, push_number, post_index = \
            _api_util.parse_query_post(
                api,
                last_screen)

        aid_list.append(post_aid)

        cmd_list = []
        cmd_list.append(command.enter)
        cmd_list.append(command.up)
        cmd_list.append(command.query_post)
        cmd = ''.join(cmd_list)

    aid_list.reverse()

    for post_aid in aid_list:
        current_post = api.get_post(board=board, aid=post_aid, query=True)
        result.append(current_post)

    logger.info(i18n.catch_bottom_post_success)

    return list(reversed(result))
