try:
    from . import data_type
    from . import i18n
    from . import connect_core
    from . import log
    from . import exceptions
    from . import command
except ModuleNotFoundError:
    import data_type
    import i18n
    import connect_core
    import log
    import exceptions
    import command


def reply_post(
        api,
        reply_type: int,
        board: str,
        content: str,
        sign_file,
        post_aid: str,
        post_index: int) ->None:

    # log.showValue(
    #     api.config,
    #     log.level.INFO,
    #     [
    #         i18n.PTT,
    #         i18n.Msg
    #     ],
    #     i18n.MarkPost
    # )

    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(command.Enter)
    cmd_list.append(command.Ctrl_C * 2)
    cmd_list.append(command.Space)

    if post_aid is not None:
        cmd_list.append('#' + post_aid)
    elif post_index != 0:
        cmd_list.append(str(post_index))
    cmd_list.append(command.Enter * 2)
    cmd_list.append('r')

    if reply_type == data_type.reply_type.BOARD:
        reply_target_unit = connect_core.TargetUnit(
            i18n.ReplyBoard,
            '▲ 回應至',
            log_level=log.level.INFO,
            response='F' + command.Enter
        )
    elif reply_type == data_type.reply_type.MAIL:
        reply_target_unit = connect_core.TargetUnit(
            i18n.ReplyMail,
            '▲ 回應至',
            log_level=log.level.INFO,
            response='M' + command.Enter
        )
    elif reply_type == data_type.reply_type.BOARD_MAIL:
        reply_target_unit = connect_core.TargetUnit(
            i18n.ReplyBoard_Mail,
            '▲ 回應至',
            log_level=log.level.INFO,
            response='B' + command.Enter
        )

    cmd = ''.join(cmd_list)
    target_list = [
        connect_core.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵繼續',
            break_detect=True,
        ),
        connect_core.TargetUnit(
            i18n.NoResponse,
            '◆ 很抱歉, 此文章已結案並標記, 不得回應',
            log_level=log.level.INFO,
            exceptions_=exceptions.NoResponse()
        ),
        connect_core.TargetUnit(
            i18n.ForcedWrite,
            '(E)繼續編輯 (W)強制寫入',
            log_level=log.level.INFO,
            response='W' + command.Enter
        ),
        connect_core.TargetUnit(
            i18n.SelectSignature,
            '請選擇簽名檔',
            response=str(sign_file) + command.Enter,
        ),
        connect_core.TargetUnit(
            i18n.SaveFile,
            '確定要儲存檔案嗎',
            response='s' + command.Enter,
        ),
        connect_core.TargetUnit(
            i18n.EditPost,
            '編輯文章',
            log_level=log.level.INFO,
            response=str(content) + command.Enter + command.Ctrl_X
        ),
        connect_core.TargetUnit(
            i18n.QuoteOriginal,
            '請問要引用原文嗎',
            log_level=log.level.DEBUG,
            response='Y' + command.Enter
        ),
        connect_core.TargetUnit(
            i18n.UseTheOriginalTitle,
            '採用原標題[Y/n]?',
            log_level=log.level.DEBUG,
            response='Y' + command.Enter
        ),
        reply_target_unit,
        connect_core.TargetUnit(
            i18n.SelfSaveDraft,
            '已順利寄出，是否自存底稿',
            log_level=log.level.DEBUG,
            response='Y' + command.Enter
        ),
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout
    )

    log.log(
        api.config,
        log.level.INFO,
        i18n.RespondSuccess
    )
