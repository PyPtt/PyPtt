"""Integration tests for set_board_title (moderator-only).

The success-path test runs on a board the bot moderates
(`config.MOD_BOARD`, skipped if unset). It changes the board's mandarin
description to a marker, then restores the original.

We intentionally do NOT verify the change via `get_board_info` in the
same session: after `set_board_title` returns, the next `get_board_info`
call fails with `NoSuchBoard` (a pre-existing PyPtt session-state
quirk). Both `set_board_title` calls completing without raising is the
strongest in-session signal of success.
"""
import time

import pytest

import PyPtt
from tests import config


def test_a_set_board_title_without_moderator_perm_raises(ptt_bots):
    """Pinning current behaviour: set_board_title requires moderator perms.

    Test order matters — this MUST run before the moderated-board test
    because that test leaves the session in a state where subsequent
    `goto_board` calls intermittently fail. The `test_a_` / `test_b_`
    prefixes pin the order alphabetically.
    """
    for ptt_bot in ptt_bots:
        with pytest.raises(PyPtt.NeedModeratorPermission):
            ptt_bot.set_board_title(board='Test', new_title='will-not-apply')


def test_b_set_board_title_on_moderated_board(ptt_bots):
    """Change the description, then restore. Only runs on PTT1."""
    if not config.MOD_BOARD:
        pytest.skip('MOD_BOARD env var not set')
    for ptt_bot in ptt_bots:
        if ptt_bot.host != PyPtt.HOST.PTT1:
            continue
        info = ptt_bot.get_board_info(board=config.MOD_BOARD)
        original = info[PyPtt.BoardField.mandarin_des]

        marker = f'pyptt-{int(time.time())}'
        ptt_bot.set_board_title(board=config.MOD_BOARD, new_title=marker)
        time.sleep(1)
        # Restore — completing without raising means PTT accepted both
        # mutations against the same moderated board.
        ptt_bot.set_board_title(board=config.MOD_BOARD, new_title=original)
