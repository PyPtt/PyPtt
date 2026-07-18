import os
import time

import pytest

import PyPtt

# This file logs the same account in/out repeatedly, including
# kick_other_session=True -- which, against the session-scoped `ptt_bots`
# fixture's shared accounts (pypttbot1/pypttbot2), would kick those bots'
# sessions out from under every other test file sharing the same pytest
# process. There's no real-PTT account configured that's safe to kick this
# way (PTT1_ID/PTT2_ID *are* pypttbot1/pypttbot2), so this file only runs
# against a local imageptt container, which bootstrap_local_pttbbs.py also
# provisions two extra, otherwise-unused accounts for (CodingMan/CodingMan2).
# master doesn't collect this file at all, so skipping it on real PTT here is
# zero regression, not a coverage loss.
if os.environ.get('PTT_HOST') != 'LOCALHOST':
    pytest.skip(
        'test_login_logout.py needs an account that is safe to kick '
        '(kick_other_session=True) without disturbing the session-scoped '
        'ptt_bots fixture shared by every other test file; only the '
        'LOCALHOST bootstrap provisions one (CodingMan/CodingMan2). Set '
        'PTT_HOST=LOCALHOST to run this file.',
        allow_module_level=True)

# scripts/bootstrap_local_pttbbs.py provisions these two accounts with this
# fixed password, entirely separate from the session-scoped ptt_bots
# fixture's pypttbot1/pypttbot2 -- so kicking them here can't affect any
# other test file in the same pytest process.
_LOCALHOST_ACCOUNTS = [('CodingMan', 'coding123'), ('CodingMan2', 'coding123')]


@pytest.fixture(params=_LOCALHOST_ACCOUNTS, ids=['CodingMan', 'CodingMan2'])
def ptt_bot(request):
    """Function-scoped fixture: a clean, isolated API instance per account,
    logged in/out by the test itself (see module docstring for why these
    specific accounts)."""
    ptt_id, ptt_pw = request.param
    bot = PyPtt.API(host=PyPtt.HOST.LOCALHOST)
    yield bot, ptt_id, ptt_pw
    try:
        bot.logout()
    except Exception:
        pass


def test_login_logout(ptt_bot):
    """
    Tests the login and logout functionality using the ptt_bot fixture.
    """
    bot, ptt_id, ptt_pw = ptt_bot

    # --- Test Logic ---
    # First login/logout cycle
    bot.login(ptt_id=ptt_id, ptt_pw=ptt_pw, kick_other_session=True)
    bot.logout()

    time.sleep(5)

    # Second login/logout cycle
    bot.login(ptt_id=ptt_id, ptt_pw=ptt_pw, kick_other_session=False)
    bot.logout()

    print(f'login logout test for {ptt_id} on LOCALHOST ok')
