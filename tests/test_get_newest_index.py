import pytest

import PyPtt
from PyPtt import exceptions


PTT1_BOARD_CASES = [
    ('Python', None, None),
    ('Gossiping', None, None),
    ('Python', PyPtt.SearchType.KEYWORD, '[公告]'),
    ('ALLPOST', PyPtt.SearchType.KEYWORD, '(Wanted)'),
    ('Wanted', PyPtt.SearchType.KEYWORD, '(本文已被刪除)'),
    ('ALLPOST', PyPtt.SearchType.KEYWORD, '(Gossiping)'),
    ('Gossiping', PyPtt.SearchType.KEYWORD, '普悠瑪'),
    ('book', PyPtt.SearchType.KEYWORD, 'AWS'),
]

PTT2_BOARD_CASES = [
    ('PttSuggest', None, None),
    ('PttSuggest', PyPtt.SearchType.KEYWORD, '[問題]'),
]

def test_get_mail_index(logged_in_bot: PyPtt.API):
    """Tests getting the newest mail index."""
    index = logged_in_bot.get_newest_index(PyPtt.NewIndex.MAIL)
    assert isinstance(index, int) and index > 0


@pytest.mark.parametrize("board, search_type, search_condition", PTT1_BOARD_CASES)
def test_get_board_index_ptt1(logged_in_bot: PyPtt.API, board, search_type, search_condition):
    """Tests getting the newest board index on PTT1 with various search parameters."""
    if logged_in_bot.config.host != PyPtt.HOST.PTT1:
        pytest.skip("This test is for PTT1 only.")

    index = logged_in_bot.get_newest_index(
        index_type=PyPtt.NewIndex.BOARD,
        board=board,
        search_type=search_type,
        search_condition=search_condition
    )
    assert isinstance(index, int) and index > 0


@pytest.mark.parametrize("board, search_type, search_condition", PTT2_BOARD_CASES)
def test_get_board_index_ptt2(logged_in_bot: PyPtt.API, board, search_type, search_condition):
    """Tests getting the newest board index on PTT2 with various search parameters."""
    if logged_in_bot.config.host != PyPtt.HOST.PTT2:
        pytest.skip("This test is for PTT2 only.")

    index = logged_in_bot.get_newest_index(
        index_type=PyPtt.NewIndex.BOARD,
        board=board,
        search_type=search_type,
        search_condition=search_condition
    )
    assert isinstance(index, int) and index > 0


def test_get_index_of_non_existent_board(logged_in_bot: PyPtt.API):
    """Tests that getting the index of a non-existent board raises NoSuchBoard exception."""
    with pytest.raises(exceptions.NoSuchBoard):
        logged_in_bot.get_newest_index(
            PyPtt.NewIndex.BOARD,
            board='board_not_exist_xyz123')
