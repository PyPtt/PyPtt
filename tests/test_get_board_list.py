def test_get_all_boards(ptt_bots):
    """Tests getting all board list from PTT."""

    check_board_list = [
        'Test',
        'Announce',
        'SYSOP',
    ]

    for ptt_bot in ptt_bots:
        board_list = ptt_bot.get_all_boards()
        assert board_list is not None, f'get_all_boards returned None for host {ptt_bot.host}'
        assert isinstance(board_list, list), f'board_list is not a list for host {ptt_bot.host}'
        assert len(board_list) > 0, f'board_list is empty for host {ptt_bot.host}'

        for board in check_board_list:
            assert board in board_list, f'Board "{board}" not found in board_list for host {ptt_bot.host}'