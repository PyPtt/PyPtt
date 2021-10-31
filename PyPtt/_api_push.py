from SingleLog.log import Logger

from . import data_type
from . import i18n
from . import connect_core
from . import screens
from . import exceptions
from . import command


def push(
        api,
        board: str,
        push_type: int,
        push_content: str,
        post_aid: str,
        post_index: int) -> None:
    api._goto_board(board)

    logger = Logger('push', Logger.INFO)

    cmd_list = list()

    if post_aid is not None:
        cmd_list.append('#' + post_aid)
    elif post_index != 0:
        cmd_list.append(str(post_index))
    cmd_list.append(command.enter)
    cmd_list.append(command.comment)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.has_push_permission,
            '您覺得這篇',
            log_level=Logger.DEBUG,
            break_detect=True
        ),
        connect_core.TargetUnit(
            i18n.only_arrow,
            '加註方式',
            log_level=Logger.DEBUG,
            break_detect=True
        ),
        connect_core.TargetUnit(
            i18n.no_fast_comment,
            '禁止快速連續推文',
            log_level=Logger.INFO,
            break_detect=True,
            exceptions_=exceptions.NoFastComment()
        ),
        connect_core.TargetUnit(
            i18n.no_fast_comment,
            '禁止短時間內大量推文',
            log_level=Logger.INFO,
            break_detect=True,
            exceptions_=exceptions.NoFastComment()
        ),
        connect_core.TargetUnit(
            i18n.no_permission,
            '使用者不可發言',
            log_level=Logger.INFO,
            break_detect=True,
            exceptions_=exceptions.NoPermission(i18n.no_permission)
        ),
        connect_core.TargetUnit(
            i18n.no_comment,
            '◆ 抱歉, 禁止推薦',
            log_level=Logger.INFO,
            break_detect=True,
            exceptions_=exceptions.NoPush()
        ),
    ]

    index = api.connect_core.send(
        cmd,
        target_list)

    if index == -1:
        if post_aid is not None:
            raise exceptions.NoSuchPost(board, post_aid)
        else:
            raise exceptions.NoSuchPost(board, post_index)

    cmd_list = list()

    if index == 0:
        push_option_line = api.connect_core.get_screen_queue()[-1]
        push_option_line = push_option_line.split('\n')[-1]
        
        logger.debug('comment option line', push_option_line)

        enable_push = '值得推薦' in push_option_line
        enable_boo = '給它噓聲' in push_option_line
        enable_arrow = '只加→註解' in push_option_line

        logger.debug('comment', enable_push)
        logger.debug('Boo', enable_boo)
        logger.debug('Arrow', enable_arrow)

        if push_type == data_type.push_type.PUSH and not enable_push:
            push_type = data_type.push_type.ARROW
        elif push_type == data_type.push_type.BOO and not enable_boo:
            push_type = data_type.push_type.ARROW
        elif push_type == data_type.push_type.ARROW and not enable_arrow:
            push_type = data_type.push_type.PUSH

        cmd_list.append(str(push_type))
    # elif index == 1:
    #     push_type = data_type.push_type.ARROW

    cmd_list.append(push_content)
    cmd_list.append(command.enter)
    cmd_list.append('y')
    cmd_list.append(command.enter)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            [
                i18n.comment,
                i18n.success,
            ],
            screens.Target.InBoard,
            break_detect=True,
            log_level=Logger.DEBUG
        ),
    ]

    api.connect_core.send(
        cmd,
        target_list)
