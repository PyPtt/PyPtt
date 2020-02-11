try:
    from . import i18n
    from . import connect_core
    from . import log
    from . import exceptions
    from . import command
except ModuleNotFoundError:
    import i18n
    import connect_core
    import log
    import exceptions
    import command


def mail(
        api,
        ptt_id: str,
        title: str,
        content: str,
        sign_file) -> None:

    # log.showValue(
    #     api.config,
    #     log.Level.INFO,
    #     [
    #         i18n.PTT,
    #         i18n.Msg
    #     ],
    #     i18n.MarkPost
    # )

    CmdList = []
    CmdList.append(command.GoMainMenu)
    CmdList.append('M')
    CmdList.append(command.Enter)
    CmdList.append('S')
    CmdList.append(command.Enter)
    CmdList.append(ptt_id)
    CmdList.append(command.Enter)

    Cmd = ''.join(CmdList)

    TargetList = [
        connect_core.TargetUnit(
            [
                i18n.Start,
                i18n.SendMail
            ],
            '主題：',
            break_detect=True
        ),
        connect_core.TargetUnit(
            i18n.NoSuchUser,
            '【電子郵件】',
            exceptions_=exceptions.NoSuchUser(ptt_id)
        ),
    ]

    api.connect_core.send(
        Cmd,
        TargetList,
        screen_timeout=api.config.screen_long_timeout
    )

    CmdList = []
    CmdList.append(title)
    CmdList.append(command.Enter)
    CmdList.append(content)
    CmdList.append(command.Ctrl_X)

    Cmd = ''.join(CmdList)

    if sign_file == 0:
        SingFileSelection = i18n.NoSignatureFile
    else:
        SingFileSelection = i18n.Select + ' ' + \
                            str(sign_file) + 'th ' + i18n.SignatureFile

    TargetList = [
        connect_core.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵',
            break_detect=True
        ),
        connect_core.TargetUnit(
            i18n.SaveFile,
            '確定要儲存檔案嗎',
            response='s' + command.Enter,
            # Refresh=False,
        ),
        connect_core.TargetUnit(
            i18n.SelfSaveDraft,
            '是否自存底稿',
            response='y' + command.Enter
        ),
        connect_core.TargetUnit(
            SingFileSelection,
            '選擇簽名檔',
            response=str(sign_file) + command.Enter
        ),
        connect_core.TargetUnit(
            SingFileSelection,
            'x=隨機',
            response=str(sign_file) + command.Enter
        ),
    ]

    api.connect_core.send(
        Cmd,
        TargetList,
        screen_timeout=api.config.screen_post_timeout
    )

    log.show_value(
        api.config,
        log.Level.INFO,
        i18n.SendMail,
        i18n.Success
    )
