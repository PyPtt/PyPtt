from SingleLog import LogLevel
from SingleLog import Logger

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n


def reply_post(api, ReplyTo: int, board: str, content: str, sign_file, post_aid: str,
               post_index: int) -> None:
    logger = Logger('reply_post')

    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.Requirelogin(i18n.require_login)

    if not isinstance(ReplyTo, data_type.ReplyTo):
        raise TypeError(f'ReplyTo must be data_type.ReplyTo')

    check_value.check_type(board, str, 'board')
    check_value.check_type(content, str, 'content')
    if post_aid is not None:
        check_value.check_type(post_aid, str, 'PostAID')

    if post_index != 0:
        newest_index = api.get_newest_index(
            data_type.NewIndex.BBS,
            board=board)
        check_value.check_index(
            'post_index',
            post_index,
            max_value=newest_index)

    sign_file_list = [str(x) for x in range(0, 10)].append('x')
    if str(sign_file).lower() not in sign_file_list:
        raise ValueError(f'wrong parameter sign_file: {sign_file}')

    if post_aid is not None and post_index != 0:
        raise ValueError('wrong parameter post_aid and post_index can\'t both input')

    _api_util.check_board(api, board)

    _api_util.goto_board(api, board)

    cmd_list = []

    if post_aid is not None:
        cmd_list.append('#' + post_aid)
    elif post_index != 0:
        cmd_list.append(str(post_index))
    cmd_list.append(command.enter * 2)
    cmd_list.append('r')

    if ReplyTo == data_type.ReplyTo.BOARD:
        reply_target_unit = connect_core.TargetUnit(
            i18n.reply_board,
            '▲ 回應至',
            log_level=LogLevel.INFO,
            response='F' + command.enter
        )
    elif ReplyTo == data_type.ReplyTo.MAIL:
        reply_target_unit = connect_core.TargetUnit(
            i18n.reply_mail,
            '▲ 回應至',
            log_level=LogLevel.INFO,
            response='M' + command.enter
        )
    elif ReplyTo == data_type.ReplyTo.BOARD_MAIL:
        reply_target_unit = connect_core.TargetUnit(
            i18n.reply_board_mail,
            '▲ 回應至',
            log_level=LogLevel.INFO,
            response='B' + command.enter
        )

    cmd = ''.join(cmd_list)
    target_list = [
        connect_core.TargetUnit(
            i18n.any_key_continue,
            '任意鍵繼續',
            break_detect=True,
        ),
        connect_core.TargetUnit(
            i18n.no_response,
            '◆ 很抱歉, 此文章已結案並標記, 不得回應',
            log_level=LogLevel.INFO,
            exceptions_=exceptions.NoResponse()
        ),
        connect_core.TargetUnit(
            i18n.forced_write,
            '(E)繼續編輯 (W)強制寫入',
            log_level=LogLevel.INFO,
            response='W' + command.enter
        ),
        connect_core.TargetUnit(
            i18n.select_signature,
            '請選擇簽名檔',
            response=str(sign_file) + command.enter,
        ),
        connect_core.TargetUnit(
            i18n.save_file,
            '確定要儲存檔案嗎',
            response='s' + command.enter,
        ),
        connect_core.TargetUnit(
            i18n.edit_post,
            '編輯文章',
            log_level=LogLevel.INFO,
            response=str(content) + command.enter + command.ctrl_x
        ),
        connect_core.TargetUnit(
            i18n.quote_original,
            '請問要引用原文嗎',
            log_level=LogLevel.DEBUG,
            response='Y' + command.enter
        ),
        connect_core.TargetUnit(
            i18n.use_the_original_title,
            '採用原標題[Y/n]?',
            log_level=LogLevel.DEBUG,
            response='Y' + command.enter
        ),
        reply_target_unit,
        connect_core.TargetUnit(
            i18n.api_save_draft,
            '已順利寄出，是否自存底稿',
            log_level=LogLevel.DEBUG,
            response='Y' + command.enter
        ),
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout)

    logger.info(i18n.respond_success)
