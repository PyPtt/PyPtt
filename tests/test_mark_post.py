"""Integration tests for mark_post.

`mark_post` requires board-moderator credentials (see
`_api_mark_post.py:_api_util.check_board(..., check_moderator=True)`).
The success-path test runs on a board the bot moderates (`config.MOD_BOARD`,
skipped if unset). The permission-rejection test uses the public `Test`
board where the account is not a moderator.
"""
import time

import pytest

import PyPtt
from PyPtt import PostField, NewIndex
from tests import config
from tests import util


def _post_and_get_aid(ptt_bot, board: str) -> str:
    """Post a fresh article on `board` and return its AID."""
    ptt_bot.post(
        board=board,
        title_index=1,
        title=f'PyPtt mark_post test {int(time.time())}',
        content='mark test content',
        sign_file=0,
    )
    time.sleep(1)
    newest = ptt_bot.get_newest_index(index_type=NewIndex.BOARD, board=board)
    for i in range(10):
        post = ptt_bot.get_post(board=board, index=newest - i)
        if post[PostField.author].split(' ')[0] == ptt_bot.ptt_id:
            return post[PostField.aid]
    raise AssertionError('posted article not found')


def test_mark_post_on_moderated_board(ptt_bots):
    """Successful path: post on a board the bot moderates, apply marks,
    then clean up the article."""
    if not config.MOD_BOARD:
        pytest.skip('MOD_BOARD env var not set')
    for ptt_bot in ptt_bots:
        if not util.is_primary_host(ptt_bot, ptt_bots):
            continue  # MOD_BOARD is moderated by the primary bot
        aid = _post_and_get_aid(ptt_bot, board=config.MOD_BOARD)
        try:
            ptt_bot.mark_post(
                mark_type=PyPtt.MarkType.S,
                board=config.MOD_BOARD,
                aid=aid,
                search_type=PyPtt.SearchType.NOPE,
            )
            ptt_bot.mark_post(
                mark_type=PyPtt.MarkType.M,
                board=config.MOD_BOARD,
                aid=aid,
                search_type=PyPtt.SearchType.NOPE,
            )
        finally:
            try:
                ptt_bot.del_post(board=config.MOD_BOARD, aid=aid)
            except Exception:
                pass


def test_mark_post_without_moderator_perm_raises(ptt_bots):
    """Pinning current behaviour: mark_post unconditionally requires
    moderator perms. On the `Test` board the bot is not a moderator."""
    for ptt_bot in ptt_bots:
        aid = _post_and_get_aid(ptt_bot, board='Test')
        with pytest.raises(PyPtt.NeedModeratorPermission):
            ptt_bot.mark_post(
                mark_type=PyPtt.MarkType.S,
                board='Test',
                aid=aid,
                search_type=PyPtt.SearchType.NOPE,
            )
