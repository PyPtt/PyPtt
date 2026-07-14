import json

import PyPtt
from PyPtt import exceptions
import pytest

# Boards to test on PTT1
test_boards_ptt1 = [
    'Gossiping',
    'Stock',
    'Baseball',
    'Python',
]

# Boards to test on PTT2
test_boards_ptt2 = [
    'Ptt2Law',
    'SYSOP',
]

# A local imageptt container has neither PTT1/PTT2's boards nor their post
# volume. Only 'Python' is used here (not also 'Test', which
# scripts/bootstrap_local_pttbbs.py also seeds): every test file's session
# teardown deletes each bot's own recent posts on 'Test'
# (tests/util.py::del_all_post), so across a full-suite run -- or even a
# second run of just this file against the same container -- 'Test' can be
# left with 0 posts, which get_post_list rejects outright (limit must be
# >=1 and <= the newest index). 'Python' is never pruned this way, so its
# post count only ever grows.
test_boards_localhost = [
    'Python',
]


def test_get_post_list_positive(ptt_bots):
    """Shared logic for testing get_post_list's positive path (a board with
    posts returns a well-formed, duplicate-free, ascending-index list)."""

    verified = False
    for ptt_bot in ptt_bots:
        if ptt_bot.host == PyPtt.HOST.PTT1:
            boards = test_boards_ptt1
        elif ptt_bot.host == PyPtt.HOST.PTT2:
            boards = test_boards_ptt2
        else:
            boards = test_boards_localhost

        limit = 20

        for board in boards:
            if ptt_bot.host == PyPtt.HOST.LOCALHOST:
                # A fresh imageptt container only has the couple of seed
                # posts bootstrap plants -- get_post_list requires
                # limit <= the board's newest index.
                max_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, board=board)
                limit = min(20, max_index)

            try:
                post_list = ptt_bot.get_post_list(board=board, limit=limit)
            except exceptions.NoSearchResult:
                continue
            except exceptions.NoPermission:
                continue

            if not post_list:
                continue

            assert len(post_list) <= limit

            print(json.dumps(post_list, indent=2, ensure_ascii=False))

            index_set = set()
            last_index = -1
            for post in post_list:
                index = post.get(PyPtt.PostField.index)
                assert index is not None, f"Post is missing index field: {post}"
                assert isinstance(index, int)
                assert index > 0

                # Check for duplicates
                assert index not in index_set, f'Duplicate index found: {index}'
                index_set.add(index)

                # get_post_list walks the board forward from start_index (see
                # _api_get_post_list.py), so posts come back oldest-first --
                # ascending order.
                if last_index != -1:
                    assert index > last_index, "Posts are not in ascending order of index."
                last_index = index

            verified = True

    if not verified:
        pytest.skip("No board in this run returned a usable post list.")


def test_get_post_list_non_existent_board(ptt_bots):
    """Tests that get_post_list raises NoSuchBoard for a non-existent board."""
    for ptt_bot in ptt_bots:
        with pytest.raises(exceptions.NoSuchBoard):
            ptt_bot.get_post_list(board='xxxxx')