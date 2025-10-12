import time

import pytest

import PyPtt
from tests import util


@pytest.fixture(params=[PyPtt.HOST.PTT1, PyPtt.HOST.PTT2])
def ptt_bot(request):
    """
    Pytest fixture to create and tear down a PyPtt.API instance.
    It's parameterized to run tests for each host.
    """
    bot = PyPtt.API(host=request.param)

    # 'yield' passes the 'bot' object to the test function
    yield bot

    # --- Teardown code runs after the test is complete ---
    # Ensure the user is logged out and the connection is closed.
    # NOTE: Accessing the internal `_is_login` attribute is not ideal,
    # but necessary here for robust teardown.
    if bot._is_login:
        bot.logout()


def test_login_logout(ptt_bot: PyPtt.API):
    """
    Tests the login and logout functionality using the ptt_bot fixture.
    """
    # --- Test Logic ---
    # First login/logout cycle
    util.login(ptt_bot, kick=True)
    ptt_bot.logout()

    print('wait', end=' ')
    max_wait_time = 5
    for sec in range(max_wait_time):
        print(max_wait_time - sec, end=' ')
        time.sleep(1)
    print()

    # Second login/logout cycle
    util.login(ptt_bot, kick=False)
    ptt_bot.logout()

    print(f'login logout test for host {ptt_bot.config.host} ok')