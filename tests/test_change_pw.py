import pytest

def test_change_password(ptt_bots):
    """Tests changing the password to the same password."""
    for ptt_bot in ptt_bots:
        try:
            # Change password to the same one to test functionality
            ptt_bot.change_pw(ptt_bot._ptt_pw)
        except Exception as e:
            pytest.fail(f"change_pw failed for host {ptt_bot.host} with error: {e}")