import pytest
import PyPtt

try:
    from tests import util
    is_run_in_github_actions = False
except KeyError:
    is_run_in_github_actions = True



@pytest.fixture(scope="session", autouse=True)
def ptt_bots(request):
    """
    Session-scoped fixture. Creates one PyPtt.API instance per host for the
    entire test session. Handles final teardown.
    """

    ptt1_bot = PyPtt.API(host=PyPtt.HOST.PTT1)
    if not is_run_in_github_actions: util.login(ptt1_bot, kick=True)

    ptt2_bot = PyPtt.API(host=PyPtt.HOST.PTT2)
    if not is_run_in_github_actions: util.login(ptt2_bot, kick=True)

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
