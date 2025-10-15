def test_search_user(ptt_bots):
    """Tests searching for a user."""
    search_keyword = 'Coding'
    expected_user = 'CodingMan'

    for ptt_bot in ptt_bots:
        user_list = ptt_bot.search_user(search_keyword)

        assert isinstance(user_list, list), f"search_user should return a list on host {ptt_bot.host}"
        
        # Check if at least one known user is in the search results
        found = any(user.lower() == expected_user.lower() for user in user_list)
        assert found, f"Expected to find '{expected_user}' in search results for '{search_keyword}' on host {ptt_bot.host}"