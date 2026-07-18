import re
from typing import Dict

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import lib_util
from . import log
from . import screens
from .data_type import LotteryBetField, LotteryField, LotteryOptionField

_price_pattern = re.compile(r'每張要花 (\d+)')
_total_pattern = re.compile(r'已下注總額: (\d+)')
_option_pattern = re.compile(r'(\d+)\.(.+?): *(\d+)')

# mbbsd/gamble.c: show_ticket_data()/join_gamble() vmsg() text for "no round
# open to bet on", either because none was ever held (show_ticket_data can't
# open ticket.items), or a running one's auto-close time already passed
# (join_gamble's stop_gamble() check, before ticket() is even entered).
_NO_LOTTERY_TEXTS = (
    '目前並沒有舉辦樂透',
    '目前未舉辦或樂透已開獎',
)


def _parse_lottery_screen(board: str, screen: str) -> Dict:
    price = 0
    r = _price_pattern.search(screen)
    if r is not None:
        price = int(r.group(1))

    total = 0
    r = _total_pattern.search(screen)
    if r is not None:
        total = int(r.group(1))

    # Options are only printed between these two headers (mbbsd/gamble.c:
    # show_ticket_data()); slicing avoids the 站規 rule text above it, which
    # can otherwise be mistaken for "N.name: number" (e.g. "2:00 11:00").
    options = []
    if '目前下注狀況' in screen and '已下注總額' in screen:
        start = screen.index('目前下注狀況')
        end = screen.index('已下注總額')
        for m in _option_pattern.finditer(screen[start:end]):
            options.append({
                LotteryOptionField.index: int(m.group(1)),
                LotteryOptionField.name: m.group(2).strip(),
                LotteryOptionField.sold: int(m.group(3)),
            })

    return {
        LotteryField.board: board,
        LotteryField.price: price,
        LotteryField.total: total,
        LotteryField.options: options,
    }


def _enter_ticket_screen(api, board: str) -> str:
    _api_util.goto_board(api, board)

    target_list = [
        connect_core.TargetUnit(
            _NO_LOTTERY_TEXTS[0], break_detect=True, exceptions_=exceptions.NoSuchLottery(board)),
        connect_core.TargetUnit(
            _NO_LOTTERY_TEXTS[1], break_detect=True, exceptions_=exceptions.NoSuchLottery(board)),
        connect_core.TargetUnit('請選擇要購買的種類', break_detect=True),
    ]
    api.connect_core.send('f', target_list)

    return api.connect_core.get_screen_queue()[-1]


def _leave_ticket_screen(api) -> None:
    target_list = [
        connect_core.TargetUnit(screens.Target.InBoard, break_detect=True),
    ]
    api.connect_core.send('q', target_list)


def get_lottery(api, board: str) -> Dict:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    check_value.check_type(board, str, 'board')

    log.logger.info(i18n.replace(i18n.get_lottery, board))

    ori_screen = _enter_ticket_screen(api, board)
    result = _parse_lottery_screen(board, ori_screen)

    _leave_ticket_screen(api)

    log.logger.info(i18n.replace(i18n.get_lottery, board), '...', i18n.success)

    return result


def bet_lottery(api, board: str, item: int = 1, amount: int = 1) -> Dict:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(board, str, 'board')
    check_value.check_type(item, int, 'item')
    check_value.check_range(item, 1, 8, 'item')
    check_value.check_type(amount, int, 'amount')
    check_value.check_range(amount, 1, 9999, 'amount')

    log.logger.info(i18n.replace(i18n.bet_lottery, board))

    ori_screen = _enter_ticket_screen(api, board)
    before = _parse_lottery_screen(board, ori_screen)

    options = before[LotteryField.options]
    if item > len(options):
        _leave_ticket_screen(api)
        raise exceptions.ParameterError(
            f'item {item} error, board {board} only has {len(options)} lottery options')

    name = options[item - 1][LotteryOptionField.name]
    price = before[LotteryField.price]

    target_list = [
        # buy_ticket_ui()'s getdata_str() pre-fills this field with "1" and
        # parks the cursor after it (mbbsd/vtuikit.c: vgetstring() copies
        # defstr into buf then sets icurr = iend = strlen(buf)); typing
        # digits without clearing first inserts after the "1" (e.g. "3"
        # becomes "13"), so Ctrl-Y (clear-to-start) must come first.
        connect_core.TargetUnit(
            '要買多少份呢', response=command.ctrl_y + str(amount) + command.enter),
        connect_core.TargetUnit('現金不夠', break_detect=True, exceptions_=exceptions.NoMoney()),
        connect_core.TargetUnit(
            '板主已經停止下注了', break_detect=True, exceptions_=exceptions.NoSuchLottery(board)),
        connect_core.TargetUnit('按任意鍵繼續', break_detect=True),
    ]
    api.connect_core.send(str(item), target_list)

    # dismiss the purchase-confirmation picture, back to the (refreshed) ticket screen
    target_list = [
        connect_core.TargetUnit('請選擇要購買的種類', break_detect=True),
    ]
    api.connect_core.send(command.space, target_list)

    _leave_ticket_screen(api)

    log.logger.info(i18n.replace(i18n.bet_lottery, board), '...', i18n.success)

    return {
        LotteryBetField.board: board,
        LotteryBetField.item: item,
        LotteryBetField.name: name,
        LotteryBetField.amount: amount,
        LotteryBetField.cost: price * amount,
    }
