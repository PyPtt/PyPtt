try:
    from . import i18n
    from . import ConnectCore
    from . import log
    from . import exceptions
    from . import Command
except ModuleNotFoundError:
    import i18n
    import ConnectCore
    import log
    import exceptions
    import Command


def mail(
        api,
        pttid: str,
        title: str,
        content: str,
        sign_file) -> object:

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
    CmdList.append(Command.GoMainMenu)
    CmdList.append('M')
    CmdList.append(Command.Enter)
    CmdList.append('S')
    CmdList.append(Command.Enter)
    CmdList.append(pttid)
    CmdList.append(Command.Enter)

    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            [
                i18n.Start,
                i18n.SendMail
            ],
            '主題：',
            break_detect=True
        ),
        ConnectCore.TargetUnit(
            i18n.NoSuchUser,
            '【電子郵件】',
            exceptions=exceptions.NoSuchUser(pttid)
        ),
    ]

    api.connect_core.send(
        Cmd,
        TargetList,
        screen_timeout=api.config.screen_long_timeout
    )

    CmdList = []
    CmdList.append(title)
    CmdList.append(Command.Enter)
    CmdList.append(content)
    CmdList.append(Command.Ctrl_X)

    Cmd = ''.join(CmdList)

    if sign_file == 0:
        SingFileSelection = i18n.NoSignatureFile
    else:
        SingFileSelection = i18n.Select + ' ' + \
                            str(sign_file) + 'th ' + i18n.SignatureFile

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵',
            break_detect=True
        ),
        ConnectCore.TargetUnit(
            i18n.SaveFile,
            '確定要儲存檔案嗎',
            response='s' + Command.Enter,
            # Refresh=False,
        ),
        ConnectCore.TargetUnit(
            i18n.SelfSaveDraft,
            '是否自存底稿',
            response='y' + Command.Enter
        ),
        ConnectCore.TargetUnit(
            SingFileSelection,
            '選擇簽名檔',
            response=str(sign_file) + Command.Enter
        ),
        ConnectCore.TargetUnit(
            SingFileSelection,
            'x=隨機',
            response=str(sign_file) + Command.Enter
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
