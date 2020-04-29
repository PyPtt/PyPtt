try:
    from . import i18n
    from . import connect_core
    from . import exceptions
    from . import command
except ModuleNotFoundError:
    import i18n
    import connect_core
    import exceptions
    import command


def give_money(
        api, ptt_id: str, money: int) -> None:

    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('P')
    cmd_list.append(command.Enter)
    cmd_list.append('P')
    cmd_list.append(command.Enter)
    cmd_list.append('O')
    cmd_list.append(command.Enter)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.NoMoney,
            '你沒有那麼多Ptt幣喔!',
            break_detect=True,
            exceptions_=exceptions.NoMoney()
        ),
        connect_core.TargetUnit(
            i18n.NoMoney,
            '金額過少，交易取消!',
            break_detect=True,
            exceptions_=exceptions.MoneyTooFew()
        ),
        connect_core.TargetUnit(
            i18n.TransactionCancelled,
            '交易取消!',
            break_detect=True,
            exceptions_=exceptions.UnknownError(i18n.TransactionCancelled)
        ),
        connect_core.TargetUnit(
            i18n.Transaction,
            '確定進行交易嗎？',
            response='y' + command.Enter
        ),
        connect_core.TargetUnit(
            [
                i18n.Transaction,
                i18n.Success
            ],
            '按任意鍵繼續',
            break_detect=True
        ),
        connect_core.TargetUnit(
            i18n.ConstantRedBag,
            '要修改紅包袋嗎',
            response=command.Enter
        ),
        connect_core.TargetUnit(
            i18n.VerifyID,
            '完成交易前要重新確認您的身份',
            response=api._Password + command.Enter
        ),
        connect_core.TargetUnit(
            i18n.InputMoney,
            '要給他多少Ptt幣呢?',
            response=command.Tab + str(money) + command.Enter
        ),
        connect_core.TargetUnit(
            i18n.InputID,
            '這位幸運兒的id',
            response=ptt_id + command.Enter
        ),
        connect_core.TargetUnit(
            i18n.AuthenticationHasNotExpired,
            '認證尚未過期',
            response='y' + command.Enter
        ),
        connect_core.TargetUnit(
            i18n.TradingInProgress,
            '交易正在進行中',
            response=command.Space
        )
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout
    )