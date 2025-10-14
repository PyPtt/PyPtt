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

def test_get_mail_index(ptt_bots):
    """Tests getting the newest mail index."""
    for ptt_bot in ptt_bots:
        index = ptt_bot.get_newest_index(PyPtt.NewIndex.MAIL)
        assert isinstance(index, int) and index > 0


def test_get_board_index(ptt_bots):
    """Tests getting the newest board index on PTT2 with various search parameters."""
    for ptt_bot in ptt_bots:
        if ptt_bot.config.host == PyPtt.HOST.PTT1:
            test_params = PTT1_BOARD_CASES
        else:
            test_params = PTT2_BOARD_CASES

        for board, search_type, search_condition in test_params:

            index = ptt_bot.get_newest_index(
                index_type=PyPtt.NewIndex.BOARD,
                board=board,
                search_type=search_type,
                search_condition=search_condition
            )
            assert isinstance(index, int) and index > 0


def test_get_index_of_non_existent_board(ptt_bots):
    """Tests that getting the index of a non-existent board raises NoSuchBoard exception."""
    for logged_in_bot in ptt_bots:
        with pytest.raises(exceptions.NoSuchBoard):
            logged_in_bot.get_newest_index(
                PyPtt.NewIndex.BOARD,
                board='board_not_exist_xyz123')
