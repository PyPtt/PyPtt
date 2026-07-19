"""Integration tests for the per-board lottery (issue #95): get_lottery /
bet_lottery, driven against mbbsd/gamble.c's join_gamble()/ticket() flow (the
'f' key inside a board).

Round-driving tests need an actual open lottery round, which only the
LOCALHOST bootstrap provisions (board `PyPttLottery`, seeded directly via
`ticket.items` + a `ticket` marker file -- see
scripts/bootstrap_local_pttbbs.py, step_lottery()); they're skipped on the
real PTT hosts. item/amount range validation raises before any board
navigation, so those run everywhere.
"""
import pytest

import PyPtt
from PyPtt import LotteryBetField, LotteryField, LotteryOptionField

LOTTERY_BOARD = 'PyPttLottery'
LOTTERY_PRICE = 10
LOTTERY_ITEMS = ('Alpha', 'Bravo', 'Charlie')


def test_get_lottery_seeded_round(ptt_bots):
    """get_lottery reads back the seeded price + option names + sold counts."""
    ptt1_bot, ptt2_bot = ptt_bots
    if ptt1_bot.host != PyPtt.HOST.LOCALHOST:
        pytest.skip('PyPttLottery is only provisioned by the LOCALHOST bootstrap')

    lottery = ptt2_bot.get_lottery(board=LOTTERY_BOARD)

    assert lottery[LotteryField.board] == LOTTERY_BOARD
    assert lottery[LotteryField.price] == LOTTERY_PRICE

    options = lottery[LotteryField.options]
    assert len(options) == len(LOTTERY_ITEMS)
    assert [o[LotteryOptionField.name] for o in options] == list(LOTTERY_ITEMS)
    assert [o[LotteryOptionField.index] for o in options] == [1, 2, 3]
    for option in options:
        assert option[LotteryOptionField.sold] >= 0


def test_bet_lottery_increments_sold_count(ptt_bots):
    """Buying `amount` of an item bumps that item's sold count by exactly
    `amount`, verified via a follow-up get_lottery -- pttbbs gives no
    textual purchase receipt, so this is the ground truth."""
    ptt1_bot, ptt2_bot = ptt_bots
    if ptt1_bot.host != PyPtt.HOST.LOCALHOST:
        pytest.skip('PyPttLottery is only provisioned by the LOCALHOST bootstrap')

    item = 2
    amount = 3

    before = ptt2_bot.get_lottery(board=LOTTERY_BOARD)
    sold_before = before[LotteryField.options][item - 1][LotteryOptionField.sold]

    result = ptt2_bot.bet_lottery(board=LOTTERY_BOARD, item=item, amount=amount)
    assert result[LotteryBetField.board] == LOTTERY_BOARD
    assert result[LotteryBetField.item] == item
    assert result[LotteryBetField.name] == LOTTERY_ITEMS[item - 1]
    assert result[LotteryBetField.amount] == amount
    assert result[LotteryBetField.cost] == LOTTERY_PRICE * amount

    after = ptt2_bot.get_lottery(board=LOTTERY_BOARD)
    sold_after = after[LotteryField.options][item - 1][LotteryOptionField.sold]

    assert sold_after == sold_before + amount


def test_get_lottery_no_round_raises(ptt_bots):
    """A board that never had a lottery round raises NoSuchLottery."""
    ptt1_bot, ptt2_bot = ptt_bots
    if ptt1_bot.host != PyPtt.HOST.LOCALHOST:
        pytest.skip('needs a board known to never have hosted a lottery round')

    with pytest.raises(PyPtt.exceptions.NoSuchLottery):
        ptt2_bot.get_lottery(board='Test')


@pytest.mark.parametrize('item', [0, 9])
def test_bet_lottery_invalid_item_raises(ptt_bots, item):
    """item is 1..8; out-of-range raises before any board navigation."""
    ptt1_bot, ptt2_bot = ptt_bots
    with pytest.raises(PyPtt.exceptions.ParameterError):
        ptt2_bot.bet_lottery(board='Test', item=item, amount=1)


@pytest.mark.parametrize('amount', [0, 10000])
def test_bet_lottery_invalid_amount_raises(ptt_bots, amount):
    """amount is 1..9999 (pttbbs' getdata_str buffer is 4 digits); out-of-range
    raises before any board navigation."""
    ptt1_bot, ptt2_bot = ptt_bots
    with pytest.raises(PyPtt.exceptions.ParameterError):
        ptt2_bot.bet_lottery(board='Test', item=1, amount=amount)
