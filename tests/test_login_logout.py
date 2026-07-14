import os
import time

import pytest

import PyPtt
from tests import util

# Mirrors tests/conftest.py's own PTT_HOST=LOCALHOST switch: point both
# accounts at a local imageptt container instead of the real PTT1/PTT2 hosts.
_use_localhost = os.environ.get('PTT_HOST') == 'LOCALHOST'

# (host, account) pairs -- account picks PTT1_ID/PTT1_PW vs PTT2_ID/PTT2_PW
# in tests/util.py::login. Passing account explicitly (rather than letting
# login() infer it from ptt_bot.host) matters under LOCALHOST: both bots
# share HOST.LOCALHOST there, so host-based inference can't tell them apart.
if _use_localhost:
    _ptt_bot_params = [(PyPtt.HOST.LOCALHOST, 1), (PyPtt.HOST.LOCALHOST, 2)]
else:
    _ptt_bot_params = [(PyPtt.HOST.PTT1, 1), (PyPtt.HOST.PTT2, 2)]


@pytest.fixture(params=_ptt_bot_params, ids=['account1', 'account2'])
def ptt_bot(request):
    """This local, function-scoped fixture overrides the session-scoped one
    from conftest.py. It provides a clean, isolated API instance for this
    test file, which is necessary because these tests manipulate login/logout state.

    Note: conftest.py's session-scoped, autouse `ptt_bots` fixture has
    already logged both accounts into this same host by the time this test
    runs. Logging in again here with kick_other_session=True (below) will
    kick that session out from under it -- expected/intended (this is what
    kick_other_session is for), harmless as long as this file runs as its
    own pytest process (nothing else in the same session still needs
    conftest's bots afterwards), which is how the integration suite is run
    (see CLAUDE.md / .github/workflows/deploy.yml: one `pytest tests/$f`
    invocation per file).
    """
    host, account = request.param
    bot = PyPtt.API(host=host)
    yield bot, account
    # Teardown
    try:
        bot.logout()
    except Exception:
        pass


def test_login_logout(ptt_bot):
    """
    Tests the login and logout functionality using the ptt_bot fixture.
    """
    bot, account = ptt_bot

    # --- Test Logic ---
    # First login/logout cycle
    util.login(bot, kick=True, account=account)
    bot.logout()

    time.sleep(5)

    # Second login/logout cycle
    util.login(bot, kick=False, account=account)
    bot.logout()

    print(f'login logout test for host {bot.config.host} (account {account}) ok')