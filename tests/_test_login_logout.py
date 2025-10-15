import time

import pytest

import PyPtt
from tests import util


@pytest.fixture(params=[PyPtt.HOST.PTT1, PyPtt.HOST.PTT2])
def ptt_bot(request):
    """This local, function-scoped fixture overrides the session-scoped one
    from conftest.py. It provides a clean, isolated API instance for this
    test file, which is necessary because these tests manipulate login/logout state.
    """
    bot = PyPtt.API(host=request.param)
    yield bot
    # Teardown
    try:
        bot.logout()
    except Exception:
        pass


def test_login_logout(ptt_bot: PyPtt.API):
    """
    Tests the login and logout functionality using the ptt_bot fixture.
    """
    # --- Test Logic ---
    # First login/logout cycle
    util.login(ptt_bot, kick=True)
    ptt_bot.logout()

    time.sleep(5)

    # Second login/logout cycle
    util.login(ptt_bot, kick=False)
    ptt_bot.logout()

    print(f'login logout test for host {ptt_bot.config.host} ok')