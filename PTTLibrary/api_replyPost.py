try:
    from . import data_type
    from . import i18n
    from . import ConnectCore
    from . import log
    from . import exceptions
    from . import Command
except ModuleNotFoundError:
    import data_type
    import i18n
    import ConnectCore
    import log
    import exceptions
    import Command


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
    #     log.Level.INFO,
    #     [
    #         i18n.PTT,
    #         i18n.Msg
    #     ],
    #     i18n.MarkPost
    # )

    cmd_list = []
    cmd_list.append(Command.GoMainMenu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(Command.Enter)
    cmd_list.append(Command.Ctrl_C * 2)
    cmd_list.append(Command.Space)

    if post_aid is not None:
        cmd_list.append('#' + post_aid)
    elif post_index != 0:
        cmd_list.append(str(post_index))
    cmd_list.append(Command.Enter * 2)
    cmd_list.append('r')

    if reply_type == data_type.ReplyType.Board:
        reply_target_unit = ConnectCore.TargetUnit(
            i18n.ReplyBoard,
            '▲ 回應至',
            log_level=log.Level.INFO,
            response='F' + Command.Enter
        )
    elif reply_type == data_type.ReplyType.Mail:
        reply_target_unit = ConnectCore.TargetUnit(
            i18n.ReplyMail,
            '▲ 回應至',
            log_level=log.Level.INFO,
            response='M' + Command.Enter
        )
    elif reply_type == data_type.ReplyType.Board_Mail:
        reply_target_unit = ConnectCore.TargetUnit(
            i18n.ReplyBoard_Mail,
            '▲ 回應至',
            log_level=log.Level.INFO,
            response='B' + Command.Enter
        )

    cmd = ''.join(cmd_list)
    target_list = [
        ConnectCore.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵繼續',
            break_detect=True,
        ),
        ConnectCore.TargetUnit(
            i18n.NoResponse,
            '◆ 很抱歉, 此文章已結案並標記, 不得回應',
            log_level=log.Level.INFO,
            exceptions=exceptions.NoResponse()
        ),
        ConnectCore.TargetUnit(
            i18n.ForcedWrite,
            '(E)繼續編輯 (W)強制寫入',
            log_level=log.Level.INFO,
            response='W' + Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.SelectSignature,
            '請選擇簽名檔',
            response=str(sign_file) + Command.Enter,
        ),
        ConnectCore.TargetUnit(
            i18n.SaveFile,
            '確定要儲存檔案嗎',
            response='s' + Command.Enter,
        ),
        ConnectCore.TargetUnit(
            i18n.EditPost,
            '編輯文章',
            log_level=log.Level.INFO,
            response=str(content) + Command.Enter + Command.Ctrl_X
        ),
        ConnectCore.TargetUnit(
            i18n.QuoteOriginal,
            '請問要引用原文嗎',
            log_level=log.Level.DEBUG,
            response='Y' + Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.UseTheOriginalTitle,
            '採用原標題[Y/n]?',
            log_level=log.Level.DEBUG,
            response='Y' + Command.Enter
        ),
        reply_target_unit,
        ConnectCore.TargetUnit(
            i18n.SelfSaveDraft,
            '已順利寄出，是否自存底稿',
            log_level=log.Level.DEBUG,
            response='Y' + Command.Enter
        ),
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout
    )

    log.log(
        api.config,
        log.Level.INFO,
        i18n.RespondSuccess
    )
