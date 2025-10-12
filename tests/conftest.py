import pytest
import PyPtt
from tests import util


@pytest.fixture(scope="session", params=[PyPtt.HOST.PTT1, PyPtt.HOST.PTT2])
def ptt_bot(request):
    """
    Session-scoped fixture. Creates one PyPtt.API instance per host for the
    entire test session. Handles final teardown.
    """
    bot = PyPtt.API(host=request.param)
    print(f"\n--- Created API instance for {request.param} ---")
    yield bot
    # Final teardown at the end of the session
    if bot._is_login:
        print(f"\n--- Logging out from {request.param} at session end ---")
        bot.logout()


@pytest.fixture(scope="session")
def logged_in_bot(ptt_bot):
    """
    Session-scoped fixture. Ensures the bot is logged in for tests
    that require an authenticated session.
    """
    if not ptt_bot._is_login:
        print(f"--- Logging in to {ptt_bot.config.host} for session ---")
        util.login(ptt_bot)
    yield ptt_bot
