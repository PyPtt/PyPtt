try:
    from . import i18n
    from . import ConnectCore
    from . import Exceptions
    from . import Command
except ModuleNotFoundError:
    import i18n
    import ConnectCore
    import Exceptions
    import Command


def giveMoney(
        api, ID, Money):

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
    CmdList.append('P')
    CmdList.append(Command.Enter)
    CmdList.append('P')
    CmdList.append(Command.Enter)
    CmdList.append('O')
    CmdList.append(Command.Enter)

    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.NoMoney,
            '你沒有那麼多Ptt幣喔!',
            BreakDetect=True,
            Exceptions=Exceptions.NoMoney
        ),
        ConnectCore.TargetUnit(
            i18n.NoMoney,
            '金額過少，交易取消!',
            BreakDetect=True,
            Exceptions=Exceptions.MoneyTooFew
        ),
        ConnectCore.TargetUnit(
            i18n.NoMoney,
            '交易取消!',
            BreakDetect=True,
            Exceptions=Exceptions.UnknownError
        ),
        ConnectCore.TargetUnit(
            [
                i18n.Transaction,
                i18n.Success
            ],
            '按任意鍵繼續',
            BreakDetect=True
        ),
        ConnectCore.TargetUnit(
            i18n.ConstantRedBag,
            '要修改紅包袋嗎',
            Response=Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.VerifyID,
            '完成交易前要重新確認您的身份',
            Response=api._Password + Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.InputMoney,
            '要給他多少Ptt幣呢?',
            Response=Command.Tab + str(Money) + Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.InputID,
            '這位幸運兒的id',
            Response=ID + Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.AuthenticationHasNotExpired,
            '認證尚未過期',
            Response='y' + Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.TradingInProgress,
            '交易正在進行中',
            Response=Command.Space
        )
    ]

    api._ConnectCore.send(
        Cmd,
        TargetList,
        ScreenTimeout=api.Config.ScreenLongTimeOut
    )