from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import lib_util


def give_money(api, ptt_id: str, money: int) -> None:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.Requirelogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(ptt_id, str, 'ptt_id')
    check_value.check_type(money, int, 'money')
    # Check data_type.user
    api.get_user(ptt_id)

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append('P')
    cmd_list.append(command.enter)
    cmd_list.append('P')
    cmd_list.append(command.enter)
    cmd_list.append('O')
    cmd_list.append(command.enter)

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
        edit_red_bag_target,
        connect_core.TargetUnit(
            i18n.constant_red_bag,
            '要修改紅包袋嗎',
            response=command.enter
        ),
        connect_core.TargetUnit(
            i18n.verify_id,
            '完成交易前要重新確認您的身份',
            response=api._ptt_pw + command.enter
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
