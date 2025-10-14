import json

import pytest
import PyPtt

test_boards = ['SYSOP', 'Test']


@pytest.mark.parametrize('board_name', test_boards)
def test_get_board_info(ptt_bots, board_name):
    """Tests getting board information, with and without post types."""
    for ptt_bot in ptt_bots:
        # Test without post types
        board_info = ptt_bot.get_board_info(board_name, get_post_types=False)

        assert board_info is not None
        assert board_info[PyPtt.BoardField.board] == board_name
        assert isinstance(board_info[PyPtt.BoardField.online_user], int)
        assert isinstance(board_info[PyPtt.BoardField.moderators], list)

        assert isinstance(board_info[PyPtt.BoardField.post_kind_list], list)
        assert len(board_info[PyPtt.BoardField.post_kind_list]) == 0

        # Test with post types
        board_info_with_types = ptt_bot.get_board_info(board_name, get_post_types=True)

        assert board_info_with_types is not None
        assert board_info_with_types[PyPtt.BoardField.board] == board_name
        assert isinstance(board_info_with_types[PyPtt.BoardField.post_kind_list], list)
        assert len(board_info_with_types[PyPtt.BoardField.post_kind_list]) > 0


def test_get_board_info_non_existent(ptt_bots):
    """Tests getting info for a non-existent board."""
    for ptt_bot in ptt_bots:
        with pytest.raises(PyPtt.NoSuchBoard):
            ptt_bot.get_board_info('ThisBoardShouldNotExist12345')
