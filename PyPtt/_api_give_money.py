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
        api,
        ptt_id: str,
        money: int,
        title: str,
        content: str) -> None:

    cmd_list = list()
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('P')
    cmd_list.append(command.Enter)
    cmd_list.append('P')
    cmd_list.append(command.Enter)
    cmd_list.append('O')
    cmd_list.append(command.Enter)

    cmd = ''.join(cmd_list)

    edit_red_bag_cmd_list = list()

    edit_red_bag_target = connect_core.TargetUnit(
        i18n.ConstantRedBagNoEdition,
        '要修改紅包袋嗎',
        response='n' + command.Enter
    )
    if (title != '' or content != ''):
        edit_red_bag_cmd_list.append('y')
        edit_red_bag_cmd_list.append(command.Enter)
        if title != '':
            edit_red_bag_cmd_list.append(command.Down)
            edit_red_bag_cmd_list.append(command.Ctrl_Y) # remove the title
            edit_red_bag_cmd_list.append(command.Enter)
            edit_red_bag_cmd_list.append(command.Up)
            edit_red_bag_cmd_list.append(f'標題: {title}')
            # reset cursor to original position
            edit_red_bag_cmd_list.append(command.Up * 2)
        if content != '':
            edit_red_bag_cmd_list.append(command.Down * 4)
            edit_red_bag_cmd_list.append(command.Ctrl_Y * 8) # remove original content
            edit_red_bag_cmd_list.append(content)
        edit_red_bag_cmd_list.append(command.Ctrl_X)

        edit_red_bag_cmd = ''.join(edit_red_bag_cmd_list)
        edit_red_bag_target = connect_core.TargetUnit(
            i18n.ConstantEditRedBag,
            '要修改紅包袋嗎',
            response=edit_red_bag_cmd
        )

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
        edit_red_bag_target,
        connect_core.TargetUnit(
            i18n.SaveFile,
            '確定要儲存檔案嗎',
            response='s' + command.Enter,
        ),
        connect_core.TargetUnit(
            i18n.VerifyID,
            '完成交易前要重新確認您的身份',
            response=api._Password + command.Enter
        ),
        connect_core.TargetUnit(
            i18n.AnonymousTransaction,
            '他是你的小主人，是否匿名？',
            response='n' + command.Enter
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