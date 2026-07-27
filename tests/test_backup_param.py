"""
No-network unit tests for the `backup` parameter of mail / reply_post.

Regression guard: `backup` used to skip check_type, so a truthy non-bool
like the string 'False' silently answered 是否自存底稿 with 'y' and left a
backup in the sender's mailbox. `reply_post` had no `backup` parameter at
all and always answered 'Y'.
"""
import threading

import pytest

import PyPtt
from PyPtt import _api_mail, _api_reply_post

NON_BOOLS = ['False', 'false', '0', 0, 1, None]


class _StubAPI:
    """Just enough of PyPtt.API to reach the parameter checks."""
    _thread_id = threading.get_ident()
    _is_login = True
    is_registered_user = True


@pytest.mark.parametrize('backup', NON_BOOLS)
def test_mail_non_bool_backup_raises(backup):
    with pytest.raises(TypeError):
        _api_mail.mail(_StubAPI(), 'someone', 'title', 'content', 0, backup)


@pytest.mark.parametrize('backup', NON_BOOLS)
def test_reply_post_non_bool_backup_raises(backup):
    with pytest.raises(TypeError):
        _api_reply_post.reply_post(_StubAPI(), PyPtt.ReplyTo.BOARD, 'Test', 'content', 0, None, 1, backup)


def test_reply_post_exposes_backup():
    """回信給作者時的自存底稿以前寫死 'Y'，關不掉。"""
    import inspect
    assert inspect.signature(PyPtt.API.reply_post).parameters['backup'].default is True
