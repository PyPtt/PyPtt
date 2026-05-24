"""Integration tests for bucket (water-bucket / mute, moderator-only).

The success-path test mutes `config.TEST_USER` for 1 day on a board the
bot moderates (`config.MOD_BOARD`, skipped if unset). PTT's
`UserHasPreviouslyBeenBanned` guard is treated as an acceptable outcome
on re-runs (the previous run created the ban record and PTT hasn't
released it yet) — that still proves the API drove the full command
sequence and reached PTT's own duplicate-detection.

A no-moderator-permission test for `bucket` is intentionally omitted:
when called with a real user ID, the function's `check_user_exist` step
is sensitive to PyPtt's session state and returns `NoSuchUser` instead
of reaching the permission check on this branch. That's a pre-existing
quirk, not something this test file should pin down.
"""
import pytest

import PyPtt
from tests import config


def test_bucket_nonexistent_user_raises(ptt_bots):
    """`_api_util.check_user_exist` runs early, so any board works for
    this assertion. Uses a clearly-invalid ID — not a real account."""
    for ptt_bot in ptt_bots:
        with pytest.raises(PyPtt.NoSuchUser):
            ptt_bot.bucket(
                board='Test',
                bucket_days=1,
                reason='will-not-apply',
                ptt_id='zz_no_such_user_xx',
            )


def test_bucket_on_moderated_board(ptt_bots):
    """Bucket config.TEST_USER on config.MOD_BOARD. Tolerates 'already
    banned' on re-runs."""
    if not config.MOD_BOARD:
        pytest.skip('MOD_BOARD env var not set')
    for ptt_bot in ptt_bots:
        if ptt_bot.host != PyPtt.HOST.PTT1:
            continue
        try:
            ptt_bot.bucket(
                board=config.MOD_BOARD,
                bucket_days=1,
                reason='PyPtt automated bucket test',
                ptt_id=config.TEST_USER,
            )
        except PyPtt.UserHasPreviouslyBeenBanned:
            # Re-run hit PTT's duplicate guard — also a success signal.
            pass
