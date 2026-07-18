"""
No-network unit tests for the pure validation helpers in _api_del_post.py.
These call the module functions directly and don't need a live PTT session.
"""
import pytest

import PyPtt
from PyPtt import _api_del_post


class TestCheckBadPostReason:
    def test_within_limit_ok(self):
        _api_del_post._check_bad_post_reason('測' * 25)  # 50 bytes, exactly at the limit

    def test_over_limit_raises(self):
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_del_post._check_bad_post_reason('測' * 25 + 'x')  # 51 bytes

    def test_control_char_raises(self):
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_del_post._check_bad_post_reason('bad\x07reason')


class TestCheckReasonStatic:
    """`_check_reason` is the early, post_info-independent guard: control
    chars, Big5-encodability, and a rough ceiling (_REASON_MAX_POSSIBLE_BYTES
    == 41 - 13 - 1 - 1 - 1 == 25 bytes) that assumes the shortest possible
    (1-byte) moderator/author PTT ids -- the most bytes a reason could ever
    fit under any real id pair. It therefore never rejects a reason that
    might be legal once the real ids are known; that exact, smaller,
    id-dependent budget is _check_reason_budget's job (see below)."""

    def test_within_rough_ceiling_ok(self):
        _api_del_post._check_reason('測' * 12 + 'x')  # 25 bytes, exactly the rough ceiling

    def test_over_rough_ceiling_raises(self):
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_del_post._check_reason('測' * 12 + 'xx')  # 26 bytes

    def test_control_char_raises(self):
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_del_post._check_reason('bad\x07reason')

    def test_non_big5_raises(self):
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_del_post._check_reason('emoji not in big5uao \U0001F600')


class TestCheckReasonBudget:
    """`_check_reason_budget` is the exact, post_info-dependent guard: reason
    gets appended, after a leading space, to pttbbs's prefilled
    "(已被<moderator_id>刪除) <author_id>" title inside a 41-Big5-byte buffer
    (_REASON_TITLE_BUFFER_BYTES). Budget for a 9-char/9-char id pair (e.g.
    pypttbot1 deleting pypttbot2's post, as used in the local imageptt
    integration tests) is 41 - 13 - 9 - 9 - 1 == 9 bytes -- confirmed live
    against a local pttbbs rebuilt with SAFE_ARTICLE_DELETE enabled."""

    MOD_ID = 'pypttbot1'
    AUTHOR_ID = 'pypttbot2'

    def test_within_limit_ok(self):
        _api_del_post._check_reason_budget('測測測測x', self.MOD_ID, self.AUTHOR_ID)  # 9 bytes, exactly at the limit

    def test_over_limit_by_one_byte_raises(self):
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_del_post._check_reason_budget('測測測測測', self.MOD_ID, self.AUTHOR_ID)  # 10 bytes

    def test_over_limit_ascii_raises(self):
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_del_post._check_reason_budget('x' * 10, self.MOD_ID, self.AUTHOR_ID)

    def test_budget_shrinks_with_longer_ids(self):
        """A 12-char/12-char id pair (PTT's real max, IDLEN==12) leaves only
        3 bytes of budget -- a reason that fits the 9/9 pair above no
        longer fits."""
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_del_post._check_reason_budget('測測測測x', 'a' * 12, 'b' * 12)
        _api_del_post._check_reason_budget('x', 'a' * 12, 'b' * 12)  # 1 byte still fits the 3-byte budget
