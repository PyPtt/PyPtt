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

def run_post_list_test(ptt_bots):
    """Shared logic for testing get_post_list."""

    for ptt_bot in ptt_bots:
        if ptt_bot.host == PyPtt.HOST.PTT1:
            boards = test_boards_ptt1
        elif ptt_bot.host == PyPtt.HOST.PTT2:
            boards = test_boards_ptt2

        limit = 20

        for board in boards:
            try:
                post_list = ptt_bot.get_post_list(board=board, limit=limit)
            except exceptions.NoSearchResult:
                pytest.skip(f"Board {board} has no posts to test.")
                return
            except exceptions.NoPermission:
                pytest.skip(f"No permission to enter board {board}.")
                return

            if not post_list:
                pytest.skip(f"Board {board} returned no posts.")

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

                # Check if posts are returned in descending order of index
                if last_index != -1:
                    assert index < last_index, "Posts are not in descending order of index."
                last_index = index


def test_get_post_list_non_existent_board(ptt_bots):
    """Tests that get_post_list raises NoSuchBoard for a non-existent board."""
    for ptt_bot in ptt_bots:
        with pytest.raises(exceptions.NoSuchBoard):
            ptt_bot.get_post_list(board='xxxxx')