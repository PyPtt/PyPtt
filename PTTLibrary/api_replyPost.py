try:
    from . import DataType
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Screens
    from . import Exceptions
    from . import Command
    from . import CheckValue
except ModuleNotFoundError:
    import DataType
    import i18n
    import ConnectCore
    import Log
    import Screens
    import Exceptions
    import Command
    import CheckValue


def replyPost(
        api,
        inputReplyType: int,
        Board: str,
        Content: str,
        SignFile,
        PostAID: str,
        PostIndex: int):

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
    CmdList.append('qs')
    CmdList.append(Board)
    CmdList.append(Command.Enter)
    CmdList.append(Command.Ctrl_C * 2)
    CmdList.append(Command.Space)

    if PostAID is not None:
        CmdList.append('#' + PostAID)
    elif PostIndex != 0:
        CmdList.append(str(PostIndex))
    CmdList.append(Command.Enter * 2)
    CmdList.append('r')

    if inputReplyType == DataType.ReplyType.Board:
        ReplyTargetUnit = ConnectCore.TargetUnit(
            i18n.ReplyBoard,
            '▲ 回應至',
            LogLevel=Log.Level.INFO,
            Response='F' + Command.Enter
        )
    elif inputReplyType == DataType.ReplyType.Mail:
        ReplyTargetUnit = ConnectCore.TargetUnit(
            i18n.ReplyMail,
            '▲ 回應至',
            LogLevel=Log.Level.INFO,
            Response='M' + Command.Enter
        )
    elif inputReplyType == DataType.ReplyType.Board_Mail:
        ReplyTargetUnit = ConnectCore.TargetUnit(
            i18n.ReplyBoard_Mail,
            '▲ 回應至',
            LogLevel=Log.Level.INFO,
            Response='B' + Command.Enter
        )

    Cmd = ''.join(CmdList)
    TargetList = [
        ConnectCore.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵繼續',
            BreakDetect=True,
        ),
        ConnectCore.TargetUnit(
            i18n.NoResponse,
            '◆ 很抱歉, 此文章已結案並標記, 不得回應',
            LogLevel=Log.Level.INFO,
            Exceptions=Exceptions.NoResponse()
        ),
        ConnectCore.TargetUnit(
            i18n.ForcedWrite,
            '(E)繼續編輯 (W)強制寫入',
            LogLevel=Log.Level.INFO,
            Response='W' + Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.SelectSignature,
            '請選擇簽名檔',
            Response=str(SignFile) + Command.Enter,
        ),
        ConnectCore.TargetUnit(
            i18n.SaveFile,
            '確定要儲存檔案嗎',
            Response='s' + Command.Enter,
        ),
        ConnectCore.TargetUnit(
            i18n.EditPost,
            '編輯文章',
            LogLevel=Log.Level.INFO,
            Response=str(Content) + Command.Enter + Command.Ctrl_X
        ),
        ConnectCore.TargetUnit(
            i18n.QuoteOriginal,
            '請問要引用原文嗎',
            LogLevel=Log.Level.DEBUG,
            Response='Y' + Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.UseTheOriginalTitle,
            '採用原標題[Y/n]?',
            LogLevel=Log.Level.DEBUG,
            Response='Y' + Command.Enter
        ),
        ReplyTargetUnit,
        ConnectCore.TargetUnit(
            i18n.SelfSaveDraft,
            '已順利寄出，是否自存底稿',
            LogLevel=Log.Level.DEBUG,
            Response='Y' + Command.Enter
        ),
    ]

    api._ConnectCore.send(
        Cmd,
        TargetList,
        ScreenTimeout=api.Config.ScreenLongTimeOut
    )

    Log.log(
        api.Config,
        Log.Level.INFO,
        i18n.RespondSuccess
    )
