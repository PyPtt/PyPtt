"""
Unit tests for _api_util.parse_query_post.

Covers the cursor-line parsing that extracts post metadata from a PTT board
listing screen. No network connection required.
"""
from unittest.mock import MagicMock

import pytest

from PyPtt import _api_util


# ── helpers ───────────────────────────────────────────────────────────────────

def _api(cursor='>'):
    api = MagicMock()
    api.cursor = cursor
    return api


def _screen(cursor_line, *, aid='1AbCdEfG', money=2,
            url='https://www.ptt.cc/bbs/Python/M.1134139170.A.621.html'):
    """Minimal PTT query-post screen that parse_query_post expects."""
    return (
        f'{cursor_line}\n'
        f'┌── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ─┐\n'
        f'│ 文章代碼(AID): #{aid} (Python) [ptt.cc] 測試標題  │\n'
        f'│ 文章網址: {url}      │\n'
        f'│ 這一篇文章值 {money} Ptt幣                                              │\n'
        f'└── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ─┘'
    )


def _screen_no_money(cursor_line, *, aid='1AbCdEfG',
                     url='https://www.ptt.cc/bbs/Python/M.1134139170.A.621.html'):
    return (
        f'{cursor_line}\n'
        f'┌── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ─┐\n'
        f'│ 文章代碼(AID): #{aid} (Python) [ptt.cc] 測試標題  │\n'
        f'│ 文章網址: {url}      │\n'
        f'└── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ─┘'
    )


def _parse(cursor_line, **screen_kwargs):
    screen = _screen(cursor_line, **screen_kwargs)
    return _api_util.parse_query_post(_api(), screen)


def _parse_no_money(cursor_line):
    screen = _screen_no_money(cursor_line)
    return _api_util.parse_query_post(_api(), screen)


# ── push_number ───────────────────────────────────────────────────────────────

class TestPushNumber:
    """Character positions [7:11] of the cursor line encode the push count."""

    @staticmethod
    def _pn(cursor_line):
        return _parse(cursor_line).push_number

    def test_none_when_blank(self):
        # Positions [7:11] must be all spaces to produce None.
        # ">     1    1/01 ..." has index=1 followed by 4 spaces before the date.
        assert self._pn('>     1    1/01 CodingMan   □ [閒聊] 測試') is None

    def test_explode_plus_prefix(self):
        assert self._pn('>781508 +爆 9/17 jodojeda     □ [新聞] 測試') == '爆'

    def test_explode_tilde_prefix(self):
        assert self._pn('>781508 ~爆 9/17 jodojeda     □ [新聞] 測試') == '爆'

    def test_positive_number(self):
        assert self._pn('>781406 +50 9/17 kingofage111 □ [申請] 測試') == '50'

    def test_tilde_number(self):
        assert self._pn('>781406 ~50 9/17 kingofage111 □ [申請] 測試') == '50'

    def test_x_number(self):
        # X1 means about 10 pushes
        result = self._pn('>781406 +X1 9/17 kingofage111 R: [申請] 測試')
        assert result == 'X1'

    def test_m_prefix_marked(self):
        # M flag = marked; push count follows
        result = self._pn('> 79189 M 1 9/17 LittleCalf   □ [公告] 測試')
        # The actual numeric count is extracted, not the 'M' marker
        assert result == '1'


# ── title ─────────────────────────────────────────────────────────────────────

class TestTitle:
    @staticmethod
    def _title(cursor_line):
        return _parse(cursor_line).title

    def test_normal(self):
        assert self._title('>     1   1/01 CodingMan    □ [閒聊] PTT Library 更新') == '[閒聊] PTT Library 更新'

    def test_reply(self):
        result = self._title('>781406 +X1 9/17 kingofage111 R: [申請] ReDmango 請辭板主')
        assert result == 'R: [申請] ReDmango 請辭板主'

    def test_forward(self):
        result = self._title('>     1   1/01 CodingMan     轉 [新聞] 某個標題')
        assert result.startswith('Fw:')
        assert '某個標題' in result

    def test_locked(self):
        result = self._title('>     1   1/01 CodingMan     鎖 [公告] 鎖文測試')
        assert '鎖文測試' in result


# ── author ────────────────────────────────────────────────────────────────────

class TestAuthor:
    @staticmethod
    def _author(cursor_line):
        return _parse(cursor_line).author

    def test_normal(self):
        assert self._author('>     1   1/01 CodingMan    □ [閒聊] 測試') == 'CodingMan'

    def test_reply(self):
        assert self._author('>781406 +X1 9/17 kingofage111 R: [申請] 測試') == 'kingofage111'

    def test_forward(self):
        assert self._author('>     1   1/01 CodingMan     轉 [新聞] 測試') == 'CodingMan'

    def test_locked(self):
        assert self._author('>     1   1/01 CodingMan     鎖 [公告] 測試') == 'CodingMan'


# ── lock_post flag ────────────────────────────────────────────────────────────

class TestLockPost:
    @staticmethod
    def _lock(cursor_line):
        return _parse(cursor_line).lock_post

    def test_not_locked(self):
        assert self._lock('>     1   1/01 CodingMan    □ [閒聊] 測試') is False

    def test_locked(self):
        assert self._lock('>     1   1/01 CodingMan     鎖 [公告] 鎖文') is True

    def test_reply_not_locked(self):
        assert self._lock('>     1   1/01 CodingMan    R: [申請] 測試') is False

    def test_forward_not_locked(self):
        assert self._lock('>     1   1/01 CodingMan     轉 [新聞] 測試') is False


# ── list_date ─────────────────────────────────────────────────────────────────

class TestListDate:
    @staticmethod
    def _date(cursor_line):
        return _parse(cursor_line).list_date

    def test_single_digit_month(self):
        # "9/17" → last 5 chars of "9/17" = " 9/17"
        result = self._date('>  7485   9 8/09 CodingMan    □ [閒聊] 測試')
        assert '8/09' in result

    def test_double_digit_month(self):
        result = self._date('>     1  12/31 CodingMan    □ [閒聊] 測試')
        assert result == '12/31'

    def test_roc_year_prefix(self):
        # PTT sometimes shows ROC year: "112/09" → last 5 = "12/09"
        result = self._date('>     1   112/09 ericsk       □ [心得] 測試')
        assert result == '12/09'


# ── post_index ────────────────────────────────────────────────────────────────

class TestPostIndex:
    @staticmethod
    def _index(cursor_line):
        return _parse(cursor_line).index

    def test_small_index(self):
        assert self._index('>     1   1/01 CodingMan    □ [閒聊] 測試') == 1

    def test_medium_index(self):
        assert self._index('>  7485   9 8/09 CodingMan    □ [閒聊] 測試') == 7485

    def test_large_index(self):
        assert self._index('>781508 +爆 9/17 jodojeda     □ [新聞] 測試') == 781508


# ── AID ───────────────────────────────────────────────────────────────────────

class TestAID:
    def test_aid_extracted(self):
        cursor_line = '>     1   1/01 CodingMan    □ [閒聊] 測試'
        assert _parse(cursor_line, aid='1AbCdEfG').aid == '1AbCdEfG'

    def test_aid_different_value(self):
        cursor_line = '>     1   1/01 CodingMan    □ [閒聊] 測試'
        assert _parse(cursor_line, aid='13cPSYOX').aid == '13cPSYOX'


# ── URL ───────────────────────────────────────────────────────────────────────

class TestURL:
    def test_url_extracted(self):
        url = 'https://www.ptt.cc/bbs/Python/M.1134139170.A.621.html'
        cursor_line = '>     1   1/01 CodingMan    □ [閒聊] 測試'
        assert _parse(cursor_line, url=url).url == url


# ── money ─────────────────────────────────────────────────────────────────────

class TestMoney:
    def test_with_money(self):
        cursor_line = '>     1   1/01 CodingMan    □ [閒聊] 測試'
        assert _parse(cursor_line, money=5).money == 5

    def test_zero_money(self):
        cursor_line = '>     1   1/01 CodingMan    □ [閒聊] 測試'
        assert _parse(cursor_line, money=0).money == 0

    def test_no_money_line_returns_minus_one(self):
        cursor_line = '>     1   1/01 CodingMan    □ [閒聊] 測試'
        assert _parse_no_money(cursor_line).money == -1


# ── old-style cursor (●) ──────────────────────────────────────────────────────

class TestOldCursor:
    def test_old_cursor_recognized(self):
        cursor_line = '●     1   1/01 CodingMan    □ [閒聊] 測試'
        screen = _screen(cursor_line)
        result = _api_util.parse_query_post(_api(cursor='●'), screen)
        assert result.author == 'CodingMan'
        assert result.index == 1
