import PyPtt
import pytest

from PyPtt import _api_mail, _api_util, data_type


def _handle_empty_mailbox(ptt_bot):
    """On LOCALHOST, scripts/bootstrap_local_pttbbs.py always sends each bot a
    self-mail, so an empty mailbox there means something is actually broken
    -- fail loudly and immediately. On real PTT1/PTT2 we can't guarantee the
    configured test account has any mail, so just report it; the caller
    (per-bot, not the whole test) decides whether anything was verified."""
    if ptt_bot.host == PyPtt.HOST.LOCALHOST:
        pytest.fail(f"No mail found for host {ptt_bot.host} (account {ptt_bot.ptt_id}). "
                    "bootstrap_local_pttbbs.py seeds a self-mail for every account, "
                    "so this indicates a real regression, not an environment quirk.")


def test_get_mail_search_type_is_honored(monkeypatch):
    """Regression: get_mail must merge search_type/search_condition into the
    mail search command, the same way get_newest_index does. They were
    previously ignored, so `get_mail(index, search_type=AUTHOR, ...)` returned
    the unfiltered mail at that index instead of the author-filtered one.

    Offline unit test: captures the search_list handed to the command builder
    and stops before any PTT navigation. (log/i18n are initialised by the
    autouse ptt_bots fixture, which constructs PyPtt.API before this runs.)"""

    class _StopBeforeNetwork(Exception):
        pass

    captured = {}

    def fake_cmd(index_type, search_list):
        captured["search_list"] = search_list
        raise _StopBeforeNetwork

    monkeypatch.setattr(_api_util, "one_thread", lambda api: None)
    monkeypatch.setattr(_api_util, "get_search_condition_cmd", fake_cmd)

    class _FakeAPI:
        _is_login = True
        is_registered_user = True

        def get_newest_index(self, *a, **k):
            return 999

    # search_type/search_condition alone (no search_list) must reach the builder.
    # Both the enum and its string name are accepted (SearchType._MagicMeta lets
    # isinstance('AUTHOR', SearchType) pass), matching get_post's validation loop.
    for st in ("AUTHOR", data_type.SearchType.AUTHOR):
        captured.clear()
        with pytest.raises(_StopBeforeNetwork):
            _api_mail.get_mail(_FakeAPI(), index=3, search_type=st,
                               search_condition="someone")
        assert captured["search_list"] == [(st, "someone")]

    # no search -> no filter (unchanged behaviour)
    captured.clear()
    with pytest.raises(_StopBeforeNetwork):
        _api_mail.get_mail(_FakeAPI(), index=1)
    assert captured["search_list"] == []


def test_get_newest_mail(ptt_bots):
    """Tests getting the newest mail from the mailbox."""
    verified = False
    for ptt_bot in ptt_bots:
        mail_index = ptt_bot.get_newest_index(PyPtt.NewIndex.MAIL)

        assert isinstance(mail_index, int)
        if mail_index == 0:
            _handle_empty_mailbox(ptt_bot)
            continue

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
        verified = True

    if not verified:
        pytest.skip("No bot in this run had any mail. Nothing to assert get_mail against.")


def test_get_recent_mails(ptt_bots):
    """Tests getting the 5 most recent mails."""
    verified = False
    for ptt_bot in ptt_bots:
        mail_index = ptt_bot.get_newest_index(PyPtt.NewIndex.MAIL)

        if mail_index == 0:
            _handle_empty_mailbox(ptt_bot)
            continue

        # Test getting the last 5 mails
        for i in range(min(5, mail_index)):
            current_index = mail_index - i
            mail_info = ptt_bot.get_mail(current_index)

            assert mail_info is not None, f'get_mail returned None for index {current_index} on host {ptt_bot.host}'
            assert isinstance(mail_info, dict), f'mail_info is not a dict for index {current_index} on host {ptt_bot.host}'
            assert PyPtt.MailField.title in mail_info
            assert mail_info[PyPtt.MailField.title]
        verified = True

    if not verified:
        pytest.skip("No bot in this run had any mail. Nothing to assert get_mail against.")