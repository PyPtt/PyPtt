import PyPtt
import pytest

from tests import config

def test_give_money(ptt_bots):
    """Tests giving PTT money to a user."""
    recipient_id = config.TEST_USER
    amount = 1

    for ptt_bot in ptt_bots:
        # PTT2 test host does not support giving money.
        if ptt_bot.host == PyPtt.HOST.PTT2:
            continue
        # Can't give money to yourself — under LOCALHOST both bots share the
        # same .host value, so the PTT2 skip above doesn't disambiguate them,
        # and TEST_USER may legitimately be the PTT2 account's own ptt_id.
        if ptt_bot.ptt_id.lower() == recipient_id.lower():
            continue

        try:
            # This call should not raise an exception on success
            ptt_bot.give_money(recipient_id, amount)
        except Exception as e:
            pytest.fail(f"give_money() raised an exception on host {ptt_bot.host}: {e}")