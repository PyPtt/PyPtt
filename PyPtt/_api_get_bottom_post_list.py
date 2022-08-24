from SingleLog.log import Logger

import PyPtt
from . import _api_util, check_value
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import screens


def get_bottom_post_list(api: PyPtt.API, board):
    _api_util._one_thread(api)

    if not api._login_status:
        raise exceptions.Requirelogin(i18n.require_login)

    check_value.check_type(str, 'board', board)
    api._check_board(board)

    api._goto_board(board, end=True)

    logger = Logger('get_bottom_post_list', Logger.INFO)

    last_screen = api.connect_core.get_screen_queue()[-1]

    bottom_screen = [line for line in last_screen.split('\n') if '★' in line[:8]]
    bottom_length = len(bottom_screen)
    # bottom_screen = '\n'.join(bottom_screen)
    # print(bottom_screen)

    if bottom_length == 0:
        logger.info(i18n.catch_bottom_post_success)
        return list()

    cmd_list = list()
    cmd_list.append(command.query_post)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.catch_post_success,
            screens.Target.QueryPost,
            break_detect=True,
            refresh=False,
            log_level=Logger.DEBUG),
        connect_core.TargetUnit(
            i18n.post_deleted,
            screens.Target.InBoard,
            break_detect=True,
            log_level=Logger.DEBUG),
        connect_core.TargetUnit(
            i18n.no_such_board,
            screens.Target.MainMenu_Exiting,
            exceptions_=exceptions.NoSuchBoard(api.config, board)
        ),
    ]

    result = list()
    for _ in range(0, bottom_length):
        api.connect_core.send(cmd, target_list)
        last_screen = api.connect_core.get_screen_queue()[-1]

        lock_post, post_author, post_title, post_aid, post_web, post_money, list_date, push_number, post_index = \
            _api_util.parse_query_post(
                api,
                last_screen)

        current_post = api.get_post(board, aid=post_aid, query=True)

        # print(current_post.aid)
        # print(current_post.title)
        # print('==========================')

        result.append(current_post)

        cmd_list = list()
        cmd_list.append(command.enter)
        cmd_list.append(command.up)
        cmd_list.append(command.query_post)
        cmd = ''.join(cmd_list)

    logger.info(i18n.catch_bottom_post_success)

    return list(reversed(result))
