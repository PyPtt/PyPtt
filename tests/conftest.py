import os

import pytest
import PyPtt

try:
    from tests import util
    is_run_in_github_actions = False
except KeyError:
    is_run_in_github_actions = True

# ponytail: PTT_HOST=LOCALHOST points both bots at a local imageptt docker
# container instead of the real PTT1/PTT2 hosts; unset keeps the status quo.
_use_localhost = os.environ.get('PTT_HOST') == 'LOCALHOST'


@pytest.fixture(scope="session", autouse=True)
def ptt_bots(request):
    """
    Session-scoped fixture. Creates one PyPtt.API instance per host for the
    entire test session. Handles final teardown.
    """

    ptt1_host = PyPtt.HOST.LOCALHOST if _use_localhost else PyPtt.HOST.PTT1
    ptt2_host = PyPtt.HOST.LOCALHOST if _use_localhost else PyPtt.HOST.PTT2

    ptt1_bot = PyPtt.API(host=ptt1_host)
    if not is_run_in_github_actions: util.login(ptt1_bot, kick=True, account=1)

    ptt2_bot = PyPtt.API(host=ptt2_host)
    if not is_run_in_github_actions: util.login(ptt2_bot, kick=True, account=2)

    yield ptt1_bot, ptt2_bot
    # Final teardown at the end of the session

    if not is_run_in_github_actions:
        try:
            util.del_all_post(ptt1_bot)
            ptt1_bot.logout()
        except Exception:
            pass

        try:
            util.del_all_post(ptt2_bot)
            ptt2_bot.logout()
        except Exception:
            pass
