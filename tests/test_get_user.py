import time


def _check_user_info(user_info, test_user):
    assert user_info is not None, f'get_user returned None for user {test_user}'
    assert 'ptt_id' in user_info
    assert user_info['ptt_id'].lower().startswith(test_user.lower())
    assert 'money' in user_info
    assert 'login_count' in user_info
    assert 'account_verified' in user_info
    assert 'legal_post' in user_info
    assert 'activity' in user_info
    assert 'last_login_date' in user_info


def test_get_user(ptt_bots):
    """Tests getting user information from PTT."""
    test_users = [
        'CodingMan',
    ]

    for _ in range(100):
        for test_user in test_users:
            user_info = ptt_bots[0].get_user(test_user)
            _check_user_info(user_info, test_user)

            time.sleep(1)

