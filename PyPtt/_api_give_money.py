import PyPtt
from . import command, lib_util, check_value
from . import connect_core
from . import exceptions
from . import i18n


def give_money(api: PyPtt.API, ptt_id: str, money: int) -> None:
    api._one_thread()

    if not api._login_status:
        raise exceptions.Requirelogin(i18n.require_login)

    if api.unregistered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(str, 'ptt_id', ptt_id)
    check_value.check_type(int, 'money', money)
    # Check user
    api.get_user(ptt_id)

    cmd_list = list()
    cmd_list.append(command.go_main_menu)
    cmd_list.append('P')
    cmd_list.append(command.enter)
    cmd_list.append('P')
    cmd_list.append(command.enter)
    cmd_list.append('O')
    cmd_list.append(command.enter)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.no_money,
            '你沒有那麼多Ptt幣喔!',
            break_detect=True,
            exceptions_=exceptions.NoMoney()
        ),
        connect_core.TargetUnit(
            i18n.no_money,
            '金額過少，交易取消!',
            break_detect=True,
            exceptions_=exceptions.MoneyTooFew()
        ),
        connect_core.TargetUnit(
            i18n.transaction_cancelled,
            '交易取消!',
            break_detect=True,
            exceptions_=exceptions.UnknownError(i18n.transaction_cancelled)
        ),
        connect_core.TargetUnit(
            i18n.transaction,
            '確定進行交易嗎？',
            response='y' + command.enter
        ),
        connect_core.TargetUnit(
            i18n.transaction_success,
            '按任意鍵繼續',
            break_detect=True
        ),
        connect_core.TargetUnit(
            i18n.constant_red_bag,
            '要修改紅包袋嗎',
            response=command.enter
        ),
        connect_core.TargetUnit(
            i18n.verify_id,
            '完成交易前要重新確認您的身份',
            response=api._Password + command.enter
        ),
        connect_core.TargetUnit(
            i18n.anonymous_transaction,
            '他是你的小主人，是否匿名？',
            response='n' + command.enter
        ),
        connect_core.TargetUnit(
            i18n.input_money,
            '要給他多少Ptt幣呢?',
            response=command.tab + str(money) + command.enter
        ),
        connect_core.TargetUnit(
            i18n.input_id,
            '這位幸運兒的id',
            response=ptt_id + command.enter
        ),
        connect_core.TargetUnit(
            i18n.authentication_has_not_expired,
            '認證尚未過期',
            response='y' + command.enter
        ),
        connect_core.TargetUnit(
            i18n.trading_in_progress,
            '交易正在進行中',
            response=command.space
        )
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout
    )
