from SingleLog.log import Logger

import PyPtt
from . import command, check_value, NewIndex
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n


def reply_post(api: PyPtt.API,
               reply_type: int,
               board: str,
               content: str,
               sign_file,
               post_aid: str,
               post_index: int) -> None:
    logger = Logger('reply_post', Logger.INFO)

    _api_util._one_thread(api)

    if not api._login_status:
        raise exceptions.Requirelogin(i18n.require_login)

    check_value.check_type(int, 'reply_type', reply_type, value_class=reply_type)
    check_value.check_type(str, 'board', board)
    check_value.check_type(str, 'content', content)
    if post_aid is not None:
        check_value.check_type(str, 'PostAID', post_aid)

    if post_index != 0:
        newest_index = api.get_newest_index(
            NewIndex.BBS,
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

    api._check_board(board)

    api._goto_board(board)

    cmd_list = list()

    if post_aid is not None:
        cmd_list.append('#' + post_aid)
    elif post_index != 0:
        cmd_list.append(str(post_index))
    cmd_list.append(command.enter * 2)
    cmd_list.append('r')

    if reply_type == data_type.reply_type.BOARD:
        reply_target_unit = connect_core.TargetUnit(
            i18n.reply_board,
            '▲ 回應至',
            log_level=Logger.INFO,
            response='F' + command.enter
        )
    elif reply_type == data_type.reply_type.MAIL:
        reply_target_unit = connect_core.TargetUnit(
            i18n.reply_mail,
            '▲ 回應至',
            log_level=Logger.INFO,
            response='M' + command.enter
        )
    elif reply_type == data_type.reply_type.BOARD_MAIL:
        reply_target_unit = connect_core.TargetUnit(
            i18n.reply_board_mail,
            '▲ 回應至',
            log_level=Logger.INFO,
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
            log_level=Logger.INFO,
            exceptions_=exceptions.NoResponse()
        ),
        connect_core.TargetUnit(
            i18n.forced_write,
            '(E)繼續編輯 (W)強制寫入',
            log_level=Logger.INFO,
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
            log_level=Logger.INFO,
            response=str(content) + command.enter + command.ctrl_x
        ),
        connect_core.TargetUnit(
            i18n.quote_original,
            '請問要引用原文嗎',
            log_level=Logger.DEBUG,
            response='Y' + command.enter
        ),
        connect_core.TargetUnit(
            i18n.use_the_original_title,
            '採用原標題[Y/n]?',
            log_level=Logger.DEBUG,
            response='Y' + command.enter
        ),
        reply_target_unit,
        connect_core.TargetUnit(
            i18n.api_save_draft,
            '已順利寄出，是否自存底稿',
            log_level=Logger.DEBUG,
            response='Y' + command.enter
        ),
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout)

    logger.info(i18n.respond_success)
