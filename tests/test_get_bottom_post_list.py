def test_get_bottom_post_list(ptt_bots):
    """Tests getting the bottom post list from a board."""
    for ptt_bot in ptt_bots:
        bottom_posts = ptt_bot.get_bottom_post_list('Test')

        assert bottom_posts is not None, f'get_bottom_post_list returned None for host {ptt_bot.host}'
        assert isinstance(bottom_posts, list), f'bottom_posts is not a list for host {ptt_bot.host}'

        if len(bottom_posts) > 0:
            post = bottom_posts[0]
            assert isinstance(post, dict)
            assert 'board' in post
            assert 'aid' in post
            assert 'title' in post