"""Integration test for fast_post_step0 + fast_post_step1."""
import time

import pytest

import PyPtt
from PyPtt import PostField, PostStatus, NewIndex


def test_fast_post_round_trip(ptt_bots):
    """Drive the two-step API and confirm the article reaches Test board."""
    for ptt_bot in ptt_bots:
        marker = f'fast-post-marker-{int(time.time())}-{ptt_bot.host}'
        title = marker
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
                # PTT prepends a board class tag (e.g. "[測試]") to the title,
                # so check that the unique marker appears in the stored title.
                assert marker in post[PostField.title]
                return
        pytest.fail(f'fast_post article {marker!r} not found on Test')
