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
import contextlib
import re

import pytest

import PyPtt
from PyPtt import LotteryBetField, LotteryField, LotteryOptionField
from PyPtt import _api_lottery

LOTTERY_BOARD = 'PyPttLottery'
LOTTERY_PRICE = 10
LOTTERY_ITEMS = ('Alpha', 'Bravo', 'Charlie')
# PyPtt.API.bet_lottery's check_range() ceiling, i.e. the most that can be spent
# in a single bet.
MAX_AMOUNT = 9999

_money_pattern = re.compile(r'現有 Dtt幣: (\d+)')


def _wallet(bot):
    """The balance pttbbs prints on the ticket screen. There is no public
    accessor -- PyPtt.UserField.money is the textual rank ('小康'), not a
    number."""
    screen = _api_lottery._enter_ticket_screen(bot, LOTTERY_BOARD)
    _api_lottery._leave_ticket_screen(bot)
    return int(_money_pattern.search(screen).group(1))


@contextlib.contextmanager
def _record_sends(bot):
    """Record every (msg, return code) of connect_core.send() made inside the
    block. send() returns -1 when no TargetUnit ever matched, i.e. the screen
    the code was waiting for never arrived and it burned a whole
    screen_timeout; a healthy flow returns the matched target's index."""
    core = bot.connect_core
    original = core.send
    calls = []

    def spy(msg, target_list, *args, **kwargs):
        ret = original(msg, target_list, *args, **kwargs)
        calls.append((msg, ret))
        return ret

    core.send = spy
    try:
        yield calls
    finally:
        del core.send


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


def test_bet_lottery_never_blind_sends(ptt_bots):
    """Every send() inside bet_lottery must match one of its own targets.

    A -1 return means no TargetUnit ever matched, i.e. PyPtt sat there burning a
    full screen_timeout on a screen it did not recognise -- and, worse, whatever
    keys it had already queued as a `response` were replayed into a screen they
    were not written for."""
    ptt1_bot, ptt2_bot = ptt_bots
    if ptt1_bot.host != PyPtt.HOST.LOCALHOST:
        pytest.skip('PyPttLottery is only provisioned by the LOCALHOST bootstrap')

    with _record_sends(ptt2_bot) as calls:
        ptt2_bot.bet_lottery(board=LOTTERY_BOARD, item=1, amount=1)

    blind = [msg for msg, ret in calls if ret == -1]
    assert not blind, f'send() timed out on {blind!r} (all sends: {calls!r})'


def test_bet_lottery_buys_exactly_the_requested_amount(ptt_bots):
    """bet_lottery must buy `amount` tickets of `item` and nothing else.

    pttbbs' ticket() loop reads one key at a time, so any stray key PyPtt sends
    while it thinks it is still on the 要買多少份呢 prompt lands back on the
    種類 prompt and silently buys extra tickets. The per-option deltas (plus
    已下注總額, which counts every option) pin that down."""
    ptt1_bot, ptt2_bot = ptt_bots
    if ptt1_bot.host != PyPtt.HOST.LOCALHOST:
        pytest.skip('PyPttLottery is only provisioned by the LOCALHOST bootstrap')

    item = 1
    amount = 2

    before = ptt2_bot.get_lottery(board=LOTTERY_BOARD)
    ptt2_bot.bet_lottery(board=LOTTERY_BOARD, item=item, amount=amount)
    after = ptt2_bot.get_lottery(board=LOTTERY_BOARD)

    def sold(lottery):
        return [o[LotteryOptionField.sold] for o in lottery[LotteryField.options]]

    expected = list(sold(before))
    expected[item - 1] += amount

    assert sold(after) == expected
    assert after[LotteryField.total] == before[LotteryField.total] + LOTTERY_PRICE * amount


def test_bet_lottery_item_past_last_option_raises(ptt_bots):
    """item is in range but the round has fewer options. This one only becomes
    detectable after entering the ticket screen, so it also has to get back
    out of it."""
    ptt1_bot, ptt2_bot = ptt_bots
    if ptt1_bot.host != PyPtt.HOST.LOCALHOST:
        pytest.skip('PyPttLottery is only provisioned by the LOCALHOST bootstrap')

    with pytest.raises(PyPtt.exceptions.ParameterError):
        ptt2_bot.bet_lottery(board=LOTTERY_BOARD, item=len(LOTTERY_ITEMS) + 1, amount=1)

    assert ptt2_bot.get_time() is not None


def test_bet_lottery_no_money_leaves_ticket_screen(ptt_bots):
    """Running out of money must not cost us the session.

    buy_ticket_ui() reports 現金不夠 through vmsg(), which parks a bar at the
    bottom of the screen waiting for a keypress. _leave_ticket_screen's 'q' is
    swallowed by that bar as its "press any key", so it leaves us back on the
    種類 prompt, still inside pttbbs' ticket() loop -- and pttbbs paints nothing
    new on the way, so there is no screen to notice it by. Without the retry in
    _leave_ticket_screen the (session-scoped, shared) bot stays stuck there and
    every later call talks to the lottery menu instead of PTT."""
    ptt1_bot, ptt2_bot = ptt_bots
    if ptt1_bot.host != PyPtt.HOST.LOCALHOST:
        pytest.skip('PyPttLottery is only provisioned by the LOCALHOST bootstrap')

    # A single bet tops out at MAX_AMOUNT tickets, so on a wallet that rich it
    # cannot be made unaffordable -- spend it down first.
    if _wallet(ptt2_bot) > LOTTERY_PRICE * MAX_AMOUNT:
        ptt2_bot.bet_lottery(board=LOTTERY_BOARD, item=1, amount=MAX_AMOUNT)
    assert _wallet(ptt2_bot) < LOTTERY_PRICE * MAX_AMOUNT

    with pytest.raises(PyPtt.exceptions.NoMoney):
        ptt2_bot.bet_lottery(board=LOTTERY_BOARD, item=1, amount=MAX_AMOUNT)

    # get_time() returns None instead of raising when it cannot reach the main
    # menu, which is exactly what a session stuck inside ticket() looks like.
    assert ptt2_bot.get_time() is not None


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


# Deliberately last in the file: when bet_lottery does *not* clean up after
# itself, this test leaves the shared session inside pttbbs' ticket() loop and
# anything running after it fails too.
def test_bet_lottery_leaves_ticket_screen_on_failure(ptt_bots, monkeypatch):
    """A failure between entering and leaving the ticket screen must still leave
    the ticket screen. The bot is session-scoped and shared by every test
    (tests/conftest.py), so a bet_lottery that dies inside pttbbs' ticket() loop
    strands the session there and takes every later test down with it."""
    ptt1_bot, ptt2_bot = ptt_bots
    if ptt1_bot.host != PyPtt.HOST.LOCALHOST:
        pytest.skip('PyPttLottery is only provisioned by the LOCALHOST bootstrap')

    def explode(board, screen):
        raise RuntimeError('injected failure inside the ticket screen')

    monkeypatch.setattr(_api_lottery, '_parse_lottery_screen', explode)
    with pytest.raises(RuntimeError):
        ptt2_bot.bet_lottery(board=LOTTERY_BOARD, item=1, amount=1)
    monkeypatch.undo()

    # get_time() returns None instead of raising when it cannot reach the main
    # menu, which is exactly what a session stuck inside ticket() looks like.
    assert ptt2_bot.get_time() is not None
