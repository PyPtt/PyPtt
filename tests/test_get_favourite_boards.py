def test_get_favourite_boards(ptt_bots):
    """Tests getting the user's favourite boards."""
    for ptt_bot in ptt_bots:
        fav_boards = ptt_bot.get_favourite_boards()

        assert fav_boards is not None, f'get_favourite_boards returned None for host {ptt_bot.host}'
        assert isinstance(fav_boards, list), f'fav_boards is not a list for host {ptt_bot.host}'

        if len(fav_boards) > 0:
            board = fav_boards[0]
            assert isinstance(board, dict)
            assert 'board' in board
            assert 'type' in board
            assert 'title' in board