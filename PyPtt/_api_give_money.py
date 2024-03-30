from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import lib_util
from . import log


def give_money(api, ptt_id: str, money: int, red_bag_title: str, red_bag_content: str) -> None:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(ptt_id, str, 'ptt_id')
    check_value.check_type(money, int, 'money')

    if red_bag_title is not None:
        check_value.check_type(red_bag_title, str, 'red_bag_title')
    else:
        red_bag_title = ''

    if red_bag_content is not None:
        check_value.check_type(red_bag_content, str, 'red_bag_content')
    else:
        red_bag_content = ''

    log.logger.info(
        i18n.replace(i18n.give_money_to, ptt_id, money))

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

    edit_red_bag_target = connect_core.TargetUnit('要修改紅包袋嗎', response='n' + command.enter)
    if red_bag_title != '' or red_bag_content != '':
        edit_red_bag_cmd_list.append('y')
        edit_red_bag_cmd_list.append(command.enter)
        if red_bag_title != '':
            edit_red_bag_cmd_list.append(command.down)
            edit_red_bag_cmd_list.append(command.ctrl_y)  # remove the red_bag_title
            edit_red_bag_cmd_list.append(command.enter)
            edit_red_bag_cmd_list.append(command.up)
            edit_red_bag_cmd_list.append(f'標題: {red_bag_title}')
            # reset cursor to original position
            edit_red_bag_cmd_list.append(command.up * 2)
        if red_bag_content != '':
            edit_red_bag_cmd_list.append(command.down * 4)
            edit_red_bag_cmd_list.append(command.ctrl_y * 8)  # remove original red_bag_content
            edit_red_bag_cmd_list.append(red_bag_content)
        edit_red_bag_cmd_list.append(command.ctrl_x)

        edit_red_bag_cmd = ''.join(edit_red_bag_cmd_list)
        edit_red_bag_target = connect_core.TargetUnit('要修改紅包袋嗎', response=edit_red_bag_cmd)

    target_list = [
        connect_core.TargetUnit('你沒有那麼多Ptt幣喔!', break_detect=True, exceptions_=exceptions.NoMoney()),
        connect_core.TargetUnit('金額過少，交易取消!', break_detect=True, exceptions_=exceptions.NoMoney()),
        connect_core.TargetUnit('交易取消!', break_detect=True,
                                exceptions_=exceptions.UnknownError(i18n.transaction_cancelled)),
        connect_core.TargetUnit('確定進行交易嗎？', response='y' + command.enter),
        connect_core.TargetUnit('按任意鍵繼續', break_detect=True),
        edit_red_bag_target,
        connect_core.TargetUnit('要修改紅包袋嗎', response=command.enter),
        connect_core.TargetUnit('完成交易前要重新確認您的身份', response=api._ptt_pw + command.enter),
        connect_core.TargetUnit('他是你的小主人，是否匿名？', response='n' + command.enter),
        connect_core.TargetUnit('要給他多少Ptt幣呢?', response=command.tab + str(money) + command.enter),
        connect_core.TargetUnit('這位幸運兒的id', response=ptt_id + command.enter),
        connect_core.TargetUnit('認證尚未過期', response='y' + command.enter),
        connect_core.TargetUnit('交易正在進行中', response=command.space)
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout
    )

    log.logger.info(
        i18n.replace(i18n.give_money_to, ptt_id, money),
        '...', i18n.success)
