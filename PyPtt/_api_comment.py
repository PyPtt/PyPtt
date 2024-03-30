import collections
import time

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

comment_option = [
    None,
    data_type.CommentType.PUSH,
    data_type.CommentType.BOO,
    data_type.CommentType.ARROW,
]


def _comment(api,
             board: str,
             push_type: data_type.CommentType,
             push_content: str,
             post_aid: str,
             post_index: int) -> None:
    _api_util.goto_board(api, board)

    cmd_list = []

    if post_aid is not None:
        cmd_list.append(lib_util.check_aid(post_aid))
    elif post_index != 0:
        cmd_list.append(str(post_index))
    else:
        raise ValueError('post_aid and post_index cannot be None at the same time')

    cmd_list.append(command.enter)
    cmd_list.append(command.comment)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('您覺得這篇', log_level=log.DEBUG, break_detect=True),
        connect_core.TargetUnit(f'→ {api.ptt_id}: ', log_level=log.DEBUG, break_detect=True),
        connect_core.TargetUnit('加註方式', log_level=log.DEBUG, break_detect=True),
        connect_core.TargetUnit('禁止快速連續推文', log_level=log.INFO, break_detect=True,
                                exceptions_=exceptions.NoFastComment()),
        connect_core.TargetUnit('禁止短時間內大量推文', log_level=log.INFO, break_detect=True,
                                exceptions_=exceptions.NoFastComment()),
        connect_core.TargetUnit('使用者不可發言', log_level=log.INFO, break_detect=True,
                                exceptions_=exceptions.NoPermission(i18n.no_permission)),
        connect_core.TargetUnit('◆ 抱歉, 禁止推薦', log_level=log.INFO, break_detect=True,
                                exceptions_=exceptions.CantComment()),
    ]

    index = api.connect_core.send(
        cmd,
        target_list)

    if index == -1:
        raise exceptions.UnknownError('unknown error in comment')

    log.logger.debug(i18n.has_comment_permission)

    cmd_list = []

    if index == 0 or index == 1:
        push_option_line = api.connect_core.get_screen_queue()[-1]
        push_option_line = push_option_line.split('\n')[-1]

        log.logger.debug('comment option line', push_option_line)

        available_push_type = collections.defaultdict(lambda: False)
        first_available_push_type = None

        if '值得推薦' in push_option_line:
            available_push_type[data_type.CommentType.PUSH] = True

            if first_available_push_type is None:
                first_available_push_type = data_type.CommentType.PUSH

        if '只加→註解' in push_option_line:
            available_push_type[data_type.CommentType.ARROW] = True

            if first_available_push_type is None:
                first_available_push_type = data_type.CommentType.ARROW

        if '給它噓聲' in push_option_line:
            available_push_type[data_type.CommentType.BOO] = True

            if first_available_push_type is None:
                first_available_push_type = data_type.CommentType.BOO

        log.logger.debug('available_push_type', available_push_type)

        if available_push_type[push_type] is False:
            if first_available_push_type:
                push_type = first_available_push_type

        if True in available_push_type.values():
            cmd_list.append(str(comment_option.index(push_type)))

    cmd_list.append(push_content)
    cmd_list.append(command.enter)
    cmd_list.append('y')
    cmd_list.append(command.enter)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(screens.Target.InBoard, log_level=log.DEBUG, break_detect=True),
    ]

    api.connect_core.send(
        cmd,
        target_list)


def comment(api, board: str, push_type: data_type.CommentType, push_content: str, post_aid: str,
            post_index: int) -> None:
    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    check_value.check_type(board, str, 'board')

    if not isinstance(push_type, data_type.CommentType):
        raise TypeError(f'CommentType must be data_type.CommentType')

    check_value.check_type(push_content, str, 'push_content')
    if post_aid is not None:
        check_value.check_type(post_aid, str, 'aid')
    check_value.check_type(post_index, int, 'index')

    if len(board) == 0:
        raise ValueError(f'wrong parameter board: {board}')

    if post_index != 0 and isinstance(post_aid, str):
        raise ValueError('wrong parameter index and aid can\'t both input')

    if post_index == 0 and post_aid is None:
        raise ValueError('wrong parameter index or aid must input')

    if post_index != 0:
        newest_index = api.get_newest_index(
            data_type.NewIndex.BOARD,
            board=board)
        check_value.check_index('index', post_index, newest_index)

    _api_util.check_board(api, board)

    board_info = api._board_info_list[board.lower()]

    if board_info[data_type.BoardField.is_comment_record_ip]:
        log.logger.debug(i18n.record_ip)
        if board_info[data_type.BoardField.is_comment_aligned]:
            log.logger.debug(i18n.push_aligned)
            max_push_length = 32
        else:
            log.logger.debug(i18n.not_push_aligned)
            max_push_length = 43 - len(api.ptt_id)
    else:
        log.logger.debug(i18n.not_record_ip)
        if board_info[data_type.BoardField.is_comment_aligned]:
            log.logger.debug(i18n.push_aligned)
            max_push_length = 46
        else:
            log.logger.debug(i18n.not_push_aligned)
            max_push_length = 58 - len(api.ptt_id)

    push_content = push_content.strip()

    push_list = []
    while push_content:
        index = 0
        jump = 0

        while len(push_content[:index].encode('big5uao', 'replace')) < max_push_length:

            if index == len(push_content):
                break
            if push_content[index] == '\n':
                jump = 1
                break

            index += 1

        push_list.append(push_content[:index])
        push_content = push_content[index + jump:]

    push_list = filter(None, push_list)

    for comment in push_list:

        log.logger.info(i18n.comment)

        for _ in range(2):
            try:
                _comment(api, board, push_type, comment, post_aid=post_aid, post_index=post_index)
                break
            except exceptions.NoFastComment:
                # screens.show(api.config, api.connect_core.getScreenQueue())
                log.logger.info(i18n.wait_for_no_fast_comment)
                time.sleep(5.2)

        log.logger.info(i18n.comment, '...', i18n.success)
