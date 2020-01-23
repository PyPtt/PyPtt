try:
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Exceptions
    from . import Command
except ModuleNotFoundError:
    import i18n
    import ConnectCore
    import Log
    import Exceptions
    import Command


def mail(
        api,
        ID,
        Title,
        Content,
        SignFile):

    # Log.showValue(
    #     api.Config,
    #     Log.Level.INFO,
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
    CmdList.append(ID)
    CmdList.append(Command.Enter)

    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            [
                i18n.Start,
                i18n.SendMail
            ],
            '主題：',
            BreakDetect=True
        ),
        ConnectCore.TargetUnit(
            i18n.NoSuchUser,
            '【電子郵件】',
            Exceptions=Exceptions.NoSuchUser(ID)
        ),
    ]

    api._ConnectCore.send(
        Cmd,
        TargetList,
        ScreenTimeout=api.Config.ScreenLongTimeOut
    )

    CmdList = []
    CmdList.append(Title)
    CmdList.append(Command.Enter)
    CmdList.append(Content)
    CmdList.append(Command.Ctrl_X)

    Cmd = ''.join(CmdList)

    if SignFile == 0:
        SingFileSelection = i18n.NoSignatureFile
    else:
        SingFileSelection = i18n.Select + ' ' + \
            str(SignFile) + 'th ' + i18n.SignatureFile

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵',
            BreakDetect=True
        ),
        ConnectCore.TargetUnit(
            i18n.SaveFile,
            '確定要儲存檔案嗎',
            Response='s' + Command.Enter,
            # Refresh=False,
        ),
        ConnectCore.TargetUnit(
            i18n.SelfSaveDraft,
            '是否自存底稿',
            Response='y' + Command.Enter
        ),
        ConnectCore.TargetUnit(
            SingFileSelection,
            '選擇簽名檔',
            Response=str(SignFile) + Command.Enter
        ),
        ConnectCore.TargetUnit(
            SingFileSelection,
            'x=隨機',
            Response=str(SignFile) + Command.Enter
        ),
    ]

    api._ConnectCore.send(
        Cmd,
        TargetList,
        ScreenTimeout=api.Config.ScreenPostTimeOut
    )

    Log.showValue(
        api.Config,
        Log.Level.INFO,
        i18n.SendMail,
        i18n.Success
    )
