"""Tests PyPtt issue #84 (匿名發文): post()'s anonymous/display_id params
against a board that actually carries pttbbs' BRD_ANONYMOUS/BRD_DEFAULTANONYMOUS
flags. Only pttbbs boards flagged this way ever show the anonymous prompt --
PyPtt cannot force anonymity on a normal board (see PyPtt/_api_post.py). Only
scripts/bootstrap_local_pttbbs.py's local container provisions such a board
(AnonTest), so this file is LOCALHOST-only.
"""
import os
import time
import uuid

import pytest

import PyPtt
from PyPtt import PostField, NewIndex

if os.environ.get('PTT_HOST') != 'LOCALHOST':
    pytest.skip(
        'test_post_anonymous.py needs the AnonTest board, which only '
        'scripts/bootstrap_local_pttbbs.py provisions. Set PTT_HOST=LOCALHOST to run.',
        allow_module_level=True)

ANON_BOARD = 'AnonTest'


def _find_own_post(ptt_bot, title_marker):
    """Scan back from the newest post on ANON_BOARD for the one whose title
    contains title_marker, and return its parsed post dict."""
    newest_index = ptt_bot.get_newest_index(index_type=NewIndex.BOARD, board=ANON_BOARD)
    for i in range(10):
        index = newest_index - i
        if index <= 0:
            break
        post = ptt_bot.get_post(board=ANON_BOARD, index=index)
        if title_marker in post[PostField.title]:
            return post
    raise AssertionError(f'could not find a post titled with marker {title_marker!r}')


def test_post_anonymous(ptt_bots):
    """anonymous=True, display_id=None -> pttbbs masks the author as
    'Anonymous.' (AnonTest is bootstrapped BRD_DEFAULTANONYMOUS, so an empty
    response to the anon prompt means 'Anonymous', not the real id; pttbbs
    appends a trailing '.' the same way it does for a custom display_id)."""
    ptt_bot = ptt_bots[0]
    marker = uuid.uuid4().hex[:12]
    title = f'PyPtt anon test {marker}'

    ptt_bot.post(board=ANON_BOARD, title_index=1, title=title,
                 content='PyPtt anonymous post test content.\n', sign_file=0,
                 anonymous=True)

    time.sleep(1)
    post = _find_own_post(ptt_bot, marker)

    author = post[PostField.author]
    assert author.split(' ')[0] == 'Anonymous.', f'expected masked author "Anonymous.", got {author!r}'
    assert ptt_bot.ptt_id not in author, f'real ptt_id leaked into author field: {author!r}'


def test_post_anonymous_with_display_id(ptt_bots):
    """anonymous=True, display_id='PyPttFox' -> pttbbs masks the author as
    the custom name plus a trailing '.' (pttbbs behavior, not adjustable)."""
    ptt_bot = ptt_bots[0]
    marker = uuid.uuid4().hex[:12]
    title = f'PyPtt anon custom id test {marker}'
    display_id = 'PyPttFox'

    ptt_bot.post(board=ANON_BOARD, title_index=1, title=title,
                 content='PyPtt anonymous post (custom display id) test content.\n', sign_file=0,
                 anonymous=True, display_id=display_id)

    time.sleep(1)
    post = _find_own_post(ptt_bot, marker)

    author = post[PostField.author]
    assert author.split(' ')[0] == f'{display_id}.', f'expected masked author "{display_id}.", got {author!r}'
    assert ptt_bot.ptt_id not in author, f'real ptt_id leaked into author field: {author!r}'


def test_post_not_anonymous_shows_real_id(ptt_bots):
    """anonymous=False (default) -> even on an anonymous-capable board, the
    real ptt_id is used (safe default, backward compatible with pre-#84
    callers of post())."""
    ptt_bot = ptt_bots[0]
    marker = uuid.uuid4().hex[:12]
    title = f'PyPtt non-anon test {marker}'

    ptt_bot.post(board=ANON_BOARD, title_index=1, title=title,
                 content='PyPtt non-anonymous post test content.\n', sign_file=0)

    time.sleep(1)
    post = _find_own_post(ptt_bot, marker)

    author = post[PostField.author]
    assert author.split(' ')[0] == ptt_bot.ptt_id, f'expected real author {ptt_bot.ptt_id!r}, got {author!r}'
