import re

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

# Fetch the line of cursor
def get_cursor_line_from_screen(api, ori_screen):
    ori_screen = api.connect_core.get_screen_queue()[-1]
    cursor_line = [line for line in ori_screen.split(
        '\n') if line.startswith(api.cursor)]

    if len(cursor_line) != 1:
        raise exceptions.UnknownError(ori_screen)

    cursor_line = cursor_line[0]
    log.logger.debug('CursorLine', cursor_line)

    return cursor_line

def go_to_the_specified_article(api, post_aid: str = None, post_index: int = 0):
    """ Need to make sure we're already in the correct board.
    """
    assert (post_aid is not None and post_index == 0) or (post_aid is None and post_index > 0)
    cmd_list = []

    if post_aid is not None:
        # Use aid to find article
        cmd_list.append(lib_util.check_aid(post_aid))
    elif post_index != 0:
        # Use index to find article
        cmd_list.append(str(max(1, post_index - 100)))
        cmd_list.append(command.enter)
        cmd_list.append(str(post_index))
    else:
        raise ValueError('post_aid and post_index cannot be None at the same time')

    cmd_list.append(command.enter)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(screens.Target.InBoard, log_level=log.DEBUG, break_detect=True),
    ]

    index = api.connect_core.send(cmd, target_list)

def copy_toggled_article_to_selected_zone(api, board:str , route: str, confirm_board=True):
    """
        Pre-requisite:
        1. There is already an toggled article, either in a board or the mailbox

        Note that this method doesn't require the current position to be at the board.

    Args:
        board (str): target board
        route (str): location of the selected zone in the target board
    """

    if confirm_board:
        # Need to confirm we are in the target board.
        _api_util.goto_board(api, board)

    # Go to the destination in Selected Zone
    cmd_list = []

    cmd_list.append('z')
    cmd_list.append(route)
    cmd_list.append(command.enter)
    cmd_list.append(command.enter)
    cmd_list.append(command.end)
    cmd = ''.join(cmd_list)

    target_list=[]
    target_list = [
        connect_core.TargetUnit('【板  主】  (n)新增文章 (g)新增目錄 (e)編輯檔案', break_detect=True),
    ]

    api.connect_core.send(
        cmd,
        target_list)

    ori_screen = api.connect_core.get_screen_queue()[-1]
    cursor_line = get_cursor_line_from_screen(api, ori_screen)
    #● 615. ◇ [萌夯] 哇操 國民黨水母                      arrenwu      [03/07/25]
    LATEST_INDEX_PATTERN = re.compile(r'{} *(?P<latest_index>\d+)\. ◇'.format(api.cursor))

    latest_index_match_result = LATEST_INDEX_PATTERN.search(cursor_line)

    next_index = int(latest_index_match_result['latest_index']) + 1

    cmd_list.append(command.ctrl_p)
    cmd = ''.join(cmd_list)

    target_list=[]
    target_list = [
        connect_core.TargetUnit('【板  主】  (n)新增文章 (g)新增目錄 (e)編輯檔案', response='q'),
        connect_core.TargetUnit(screens.Target.InBoard, break_detect=True),
    ]

    api.connect_core.send(
        cmd,
        target_list)

    return next_index

def go_to_and_toggle_the_specified_article(api, post_aid: str = None, post_index: int = 0):
    """
        Toggle the article of the specified aid or index.
        ! Note that this method requires the current position to be inside the board.
    """

    assert (post_aid is not None and post_index == 0) or (post_aid is None and post_index > 0)
    cmd_list = []

    # Go to the article
    if post_aid is not None:
        # Use aid to find article
        # the returned result from lib_util.check_aid is with '#'
        cmd_list.append(lib_util.check_aid(post_aid))
    elif post_index != 0:
        # Use index to find article
        cmd_list.append(str(max(1, post_index - 100)))
        cmd_list.append(command.enter)
        cmd_list.append(str(post_index))
    else:
        raise ValueError('post_aid and post_index cannot be None at the same time')
    cmd_list.append(command.enter)

    # toggle the article
    cmd_list.append('t')

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(screens.Target.InBoard, log_level=log.DEBUG, break_detect=True),
    ]

    index = api.connect_core.send(cmd, target_list)
    assert index >= 0, "index= {}. TargetUnit was not found".format(index)

def copy_article_to_selected_zone(api, board:str , route: str, aid: str, index: int):
    """
    Copy an article of a board to its selected zone.

    Return the new index in the selected zone.
    """
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    # Require moderator identity
    _api_util.check_board(
        api,
        board,
        check_moderator=True)

    _api_util.goto_board(api, board)

    # Go to the target article
    go_to_and_toggle_the_specified_article(api, aid, index)

    next_index = copy_toggled_article_to_selected_zone(api, board , route, confirm_board=False)

    return next_index

def copy_latest_recycled_in_mailbox_to_selected_zone(api, board:str , route: str) -> int:
    # This will lead us to the position of the latest mail from the recycle bin.
    search_list = [(data_type.SearchType.AUTHOR, '資源回收筒')]
    newest_index = api.get_newest_index(data_type.NewIndex.MAIL, search_list=search_list)

    # Toggle the current mail
    cmd = 't'

    target_list=[]
    target_list = [
        connect_core.TargetUnit(screens.Target.InMailBox, break_detect=True),
    ]
    api.connect_core.send(
        cmd,
        target_list)

    # Copy the marked article to the selected zone
    next_index_in_selected_zone = copy_toggled_article_to_selected_zone(api, board, route)

    return next_index_in_selected_zone
