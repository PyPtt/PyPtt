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
        'codingman',
        'CODINGMAN',
        'cOdInGmAn',
    ]

    for _ in range(3):
        for test_user in test_users:
            user_info = ptt_bots[0].get_user(test_user)
            _check_user_info(user_info, test_user)


def test_get_user_no_such_user(ptt_bots):
    """Tests that querying a non-existent user raises NoSuchUser."""
    import PyPtt
    import pytest

    no_such_users = [
        'zzznotexist999',
        'qqzzxxyy123',
    ]

    for user in no_such_users:
        with pytest.raises(PyPtt.exceptions.NoSuchUser):
            ptt_bots[0].get_user(user)
