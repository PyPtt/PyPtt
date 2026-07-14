import PyPtt
import pytest


def _skip_or_fail_empty_mailbox(ptt_bot):
    """An empty mailbox used to be silently swallowed here (print + continue),
    so this test always passed whether or not it actually exercised get_mail.
    On LOCALHOST, scripts/bootstrap_local_pttbbs.py always sends each bot a
    self-mail, so an empty mailbox there means something is actually broken
    -- fail loudly. On real PTT1/PTT2 we can't guarantee the configured test
    account has any mail, so skip explicitly instead of asserting a fact
    about the world we don't control."""
    msg = f"No mail found for host {ptt_bot.host} (account {ptt_bot.ptt_id})."
    if ptt_bot.host == PyPtt.HOST.LOCALHOST:
        pytest.fail(f"{msg} bootstrap_local_pttbbs.py seeds a self-mail for every account, "
                    "so this indicates a real regression, not an environment quirk.")
    pytest.skip(f"{msg} Nothing to assert get_mail against.")


def test_get_newest_mail(ptt_bots):
    """Tests getting the newest mail from the mailbox."""
    for ptt_bot in ptt_bots:
        mail_index = ptt_bot.get_newest_index(PyPtt.NewIndex.MAIL)

        assert isinstance(mail_index, int)
        if mail_index == 0:
            _skip_or_fail_empty_mailbox(ptt_bot)

        mail_info = ptt_bot.get_mail(mail_index)

        assert mail_info is not None, f'get_mail returned None for host {ptt_bot.host}'
        assert isinstance(mail_info, dict), f'mail_info is not a dict for host {ptt_bot.host}'

        assert PyPtt.MailField.author in mail_info
        assert PyPtt.MailField.title in mail_info
        assert PyPtt.MailField.date in mail_info
        assert PyPtt.MailField.content in mail_info
        assert mail_info[PyPtt.MailField.author]
        assert mail_info[PyPtt.MailField.title]
        assert mail_info[PyPtt.MailField.content]


def test_get_recent_mails(ptt_bots):
    """Tests getting the 5 most recent mails."""
    for ptt_bot in ptt_bots:
        mail_index = ptt_bot.get_newest_index(PyPtt.NewIndex.MAIL)

        if mail_index == 0:
            _skip_or_fail_empty_mailbox(ptt_bot)

        # Test getting the last 5 mails
        for i in range(min(5, mail_index)):
            current_index = mail_index - i
            mail_info = ptt_bot.get_mail(current_index)

            assert mail_info is not None, f'get_mail returned None for index {current_index} on host {ptt_bot.host}'
            assert isinstance(mail_info, dict), f'mail_info is not a dict for index {current_index} on host {ptt_bot.host}'
            assert PyPtt.MailField.title in mail_info
            assert mail_info[PyPtt.MailField.title]