from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import lib_util
from . import log


def reply_post(api, reply_to: data_type.ReplyTo, board: str, content: str, sign_file, post_aid: str,
               post_index: int) -> None:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if not isinstance(reply_to, data_type.ReplyTo):
        raise TypeError(f'ReplyTo must be data_type.ReplyTo')

    check_value.check_type(board, str, 'board')
    check_value.check_type(content, str, 'content')
    if post_aid is not None:
        check_value.check_type(post_aid, str, 'PostAID')

    if post_index != 0:
        newest_index = api.get_newest_index(
            data_type.NewIndex.BOARD,
            board=board)
        check_value.check_index(
            'index',
            post_index,
            max_value=newest_index)

    sign_file_list = ['x']
    sign_file_list.extend([str(x) for x in range(0, 10)])

    if str(sign_file).lower() not in sign_file_list:
        raise ValueError(f'wrong parameter sign_file: {sign_file}')

    if post_aid is not None and post_index != 0:
        raise ValueError('wrong parameter aid and index can\'t both input')

    _api_util.check_board(api, board)

    _api_util.goto_board(api, board)

    cmd_list = []

    if post_aid is not None:
        cmd_list.append(lib_util.check_aid(post_aid))
    elif post_index != 0:
        cmd_list.append(str(post_index))
    else:
        raise ValueError('post_aid and post_index cannot be None at the same time')

    cmd_list.append(command.enter * 2)
    cmd_list.append('r')

    reply_msg = ''
    if reply_to == data_type.ReplyTo.BOARD:
        reply_msg = i18n.reply_board
        reply_target_unit = connect_core.TargetUnit('▲ 回應至', log_level=log.INFO, response='F' + command.enter)
    elif reply_to == data_type.ReplyTo.MAIL:
        reply_msg = i18n.reply_mail
        reply_target_unit = connect_core.TargetUnit('▲ 回應至', log_level=log.INFO, response='M' + command.enter)
    elif reply_to == data_type.ReplyTo.BOARD_MAIL:
        reply_msg = i18n.reply_board_mail
        reply_target_unit = connect_core.TargetUnit('▲ 回應至', log_level=log.INFO, response='B' + command.enter)
    log.logger.info(reply_msg)

    cmd = ''.join(cmd_list)
    target_list = [
        connect_core.TargetUnit('任意鍵繼續', break_detect=True),
        connect_core.TargetUnit('◆ 很抱歉, 此文章已結案並標記, 不得回應', log_level=log.INFO,
                                exceptions_=exceptions.CantResponse()),
        connect_core.TargetUnit('(E)繼續編輯 (W)強制寫入', log_level=log.INFO, response='W' + command.enter),
        connect_core.TargetUnit('請選擇簽名檔', response=str(sign_file) + command.enter),
        connect_core.TargetUnit('確定要儲存檔案嗎', response='s' + command.enter),
        connect_core.TargetUnit('編輯文章', log_level=log.INFO,
                                response=str(content) + command.enter + command.ctrl_x),
        connect_core.TargetUnit('請問要引用原文嗎', log_level=log.DEBUG, response='Y' + command.enter),
        connect_core.TargetUnit('採用原標題[Y/n]?', log_level=log.DEBUG, response='Y' + command.enter),
        reply_target_unit,
        connect_core.TargetUnit('已順利寄出，是否自存底稿', log_level=log.DEBUG, response='Y' + command.enter),
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout)

    log.logger.info(reply_msg, '...', i18n.success)
