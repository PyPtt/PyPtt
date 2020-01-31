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


def give_money(
        api, pttid: str, money: int) -> None:

    # Log.showValue(
    #     api.Config,
    #     Log.Level.INFO,
    #     [
    #         i18n.PTT,
    #         i18n.Msg
    #     ],
    #     i18n.MarkPost
    # )

    cmd_list = []
    cmd_list.append(Command.GoMainMenu)
    cmd_list.append('P')
    cmd_list.append(Command.Enter)
    cmd_list.append('P')
    cmd_list.append(Command.Enter)
    cmd_list.append('O')
    cmd_list.append(Command.Enter)

    cmd = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            i18n.NoMoney,
            '你沒有那麼多Ptt幣喔!',
            break_detect=True,
            exceptions=Exceptions.NoMoney
        ),
        ConnectCore.TargetUnit(
            i18n.NoMoney,
            '金額過少，交易取消!',
            break_detect=True,
            exceptions=Exceptions.MoneyTooFew
        ),
        ConnectCore.TargetUnit(
            i18n.NoMoney,
            '交易取消!',
            break_detect=True,
            exceptions=Exceptions.UnknownError
        ),
        ConnectCore.TargetUnit(
            [
                i18n.Transaction,
                i18n.Success
            ],
            '按任意鍵繼續',
            break_detect=True
        ),
        ConnectCore.TargetUnit(
            i18n.ConstantRedBag,
            '要修改紅包袋嗎',
            response=Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.VerifyID,
            '完成交易前要重新確認您的身份',
            response=api._Password + Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.InputMoney,
            '要給他多少Ptt幣呢?',
            response=Command.Tab + str(money) + Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.InputID,
            '這位幸運兒的id',
            response=pttid + Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.AuthenticationHasNotExpired,
            '認證尚未過期',
            response='y' + Command.Enter
        ),
        ConnectCore.TargetUnit(
            i18n.TradingInProgress,
            '交易正在進行中',
            response=Command.Space
        )
    ]

    api._ConnectCore.send(
        cmd,
        target_list,
        screen_timeout=api.Config.ScreenLongTimeOut
    )