"""Integration test for fast_post_step0 + fast_post_step1.

These two methods (and the bundled `fast_post`) all call
`api.connect_core.fast_send(...)`, but `connect_core.API` only defines
`send` — `fast_send` does not exist. So every invocation raises
`AttributeError: 'API' object has no attribute 'fast_send'`. This is
pre-existing broken code, not a regression from the parser overhaul.

The test below is marked xfail so it visibly tracks the bug. Once
`fast_send` is implemented (or the methods are rewired to `send`), the
test should switch from xfail to pass.
"""
import time

import pytest

import PyPtt
from PyPtt import PostField, PostStatus, NewIndex


@pytest.mark.xfail(
    reason='fast_post_step0/1 call api.connect_core.fast_send which is not '
           'defined — see _api_post.py:34, :52, :84',
    strict=True,
    raises=AttributeError,
)
def test_fast_post_round_trip(ptt_bots):
    """Drive the two-step API and confirm the article reaches Test board."""
    for ptt_bot in ptt_bots:
        marker = f'fast-post-marker-{int(time.time())}-{ptt_bot.host}'
        title = f'PyPtt fast_post test {marker}'
        content = (
            'PyPtt fast_post integration test\n'
            f'{marker}\n'
        )

        ptt_bot.fast_post_step0(
            board='Test',
            title=title,
            content=content,
            post_type=1,
        )
        ptt_bot.fast_post_step1(sign_file=0)
        time.sleep(1)

        newest = ptt_bot.get_newest_index(index_type=NewIndex.BOARD, board='Test')
        for i in range(10):
            post = ptt_bot.get_post(board='Test', index=newest - i)
            if post[PostField.post_status] != PostStatus.EXISTS:
                continue
            if post[PostField.author].split(' ')[0] != ptt_bot.ptt_id:
                continue
            if marker in (post[PostField.content] or ''):
                assert title in post[PostField.title]
                return
        pytest.fail(f'fast_post article {marker!r} not found on Test')
