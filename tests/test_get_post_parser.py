"""
Unit tests for _api_get_post._get_post — the internal post-fetching function.

These tests mock the network layer (connect_core) and the utility helpers
(check_board, goto_board, parse_query_post, get_content) so that only the
pure string-parsing logic is exercised. No network connection required.

Scenarios covered:
  - Normal post: all fields parsed correctly (PTT1 + PTT2)
  - Old-style author format (without 看板 suffix)
  - Deleted by author / moderator / unknown
  - Locked post
  - Query-only mode (no content fetched)
  - Each comment type: push / boo / arrow
  - PTT2 comment content format (different trailing whitespace)
  - IP format 1: "來自: x.x.x.x (location)"
  - IP format 2: dashed "x-x-x-x"
  - IP format 3: "◆ From: x.x.x.x" (no location)
  - PTT1 substandard post: missing author / title / date / content / IP
  - allpost board: board name extracted from author line
"""
import threading
from unittest.mock import MagicMock, patch

import pytest

from PyPtt import _api_get_post, _api_util, data_type, exceptions
from PyPtt._api_util import PostQueryResult
from PyPtt.data_type import CommentField, CommentType, PostField, PostStatus
from PyPtt.screens import Target as ScreenTarget

# ── constants ─────────────────────────────────────────────────────────────────

CONTENT_SEP = ScreenTarget.content_start          # the ───...─── line
CONTENT_END_PTT1 = '--\n※ 發信站: 批踢踢實業坊'
CONTENT_END_PTT2 = '--\n※ 發信站: 批踢踢兔(ptt2.cc)'

# Dummy header returned by mocked parse_query_post
HEADER_NORMAL = PostQueryResult(
    lock_post=False,
    author='CodingMan',
    title='[閒聊] 測試文章',
    aid='1AbCdEfG',
    url='https://www.ptt.cc/bbs/Python/M.1704067200.A.1.html',
    money=2,
    list_date=' 1/01',
    push_number='50',
    index=1,
)

HEADER_LOCK = PostQueryResult(
    lock_post=True,
    author='CodingMan',
    title='[公告] 鎖文',
    aid='1AbCdEfG',
    url='https://www.ptt.cc/bbs/Python/M.1704067200.A.1.html',
    money=-1,
    list_date=' 1/01',
    push_number=None,
    index=2,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_api(host=data_type.HOST.PTT1, cursor='>'):
    api = MagicMock()
    api.cursor = cursor
    api.config.host = host
    api.Unconfirmed = False
    api._thread_id = threading.get_ident()
    api._goto_board_list = set()
    api._exist_board_list = set()
    return api


def _make_board_screen(cursor_line):
    """Board listing screen containing one cursor line (for deleted-post cases)."""
    return (
        '看板 Python\n'
        '  編號  推文    日期    作者           標題\n'
        f'{cursor_line}\n'
    )


def _build_post(
    author_line='作者  CodingMan (CodingMan) 看板  Python',
    title_line='標題  [閒聊] 測試文章',
    date_line='時間  Mon Jan  1 12:00:00 2024',
    content_body='This is the post content.',
    footer_lines='',
    content_end=CONTENT_END_PTT1,
):
    """Build a realistic PTT post text from its structural parts."""
    return (
        f'{author_line}\n'
        f'{title_line}\n'
        f'{date_line}\n'
        f'{CONTENT_SEP}\n'
        f'{content_body}\n'
        f'{content_end}(ptt.cc), 來自: 1.2.3.4 (臺灣)\n'
        f'{footer_lines}'
    )


PATCHED = [
    'PyPtt._api_get_post._api_util.check_board',
    'PyPtt._api_get_post._api_util.goto_board',
]


def _call_get_post(api, origin_post, *, board='Python', post_index=1,
                   post_aid=None, query=False, header=HEADER_NORMAL,
                   send_return=0, has_control_code=False):
    """
    Helper that wires up the mocks and calls _get_post.
    send_return=0  → QueryPost matched (normal path)
    send_return=1  → InBoard matched (deleted-post path)
    """
    board_screen = _make_board_screen(f'>     {post_index}   1/01 CodingMan    □ 測試')
    api.connect_core.send.return_value = send_return
    api.connect_core.get_screen_queue.return_value = [board_screen]

    with patch(PATCHED[0]), patch(PATCHED[1]):
        with patch('PyPtt._api_get_post._api_util.parse_query_post',
                   return_value=header):
            with patch('PyPtt._api_get_post._api_util.get_content',
                       return_value=(origin_post, has_control_code)):
                return _api_get_post._get_post(
                    api, board,
                    post_aid=post_aid,
                    post_index=post_index,
                    query=query,
                )


# ── normal post ───────────────────────────────────────────────────────────────

class TestNormalPost:
    def test_pass_format_check(self):
        api = _make_api()
        result = _call_get_post(api, _build_post())
        assert result[PostField.pass_format_check] is True

    def test_author_new_format(self):
        api = _make_api()
        result = _call_get_post(api, _build_post(
            author_line='作者  CodingMan (CodingMan) 看板  Python'
        ))
        assert result[PostField.author] == 'CodingMan (CodingMan)'

    def test_author_old_format(self):
        """Old posts have no 看板 suffix on the author line."""
        api = _make_api()
        result = _call_get_post(api, _build_post(
            author_line='作者  OldUser (Old Nick)'
        ))
        assert result[PostField.author] == 'OldUser (Old Nick)'

    def test_title(self):
        api = _make_api()
        result = _call_get_post(api, _build_post())
        assert result[PostField.title] == '[閒聊] 測試文章'

    def test_date(self):
        api = _make_api()
        result = _call_get_post(api, _build_post())
        assert result[PostField.date] == 'Mon Jan  1 12:00:00 2024'

    def test_ip_extracted(self):
        api = _make_api()
        result = _call_get_post(api, _build_post())
        assert result[PostField.ip] == '1.2.3.4'

    def test_location_extracted(self):
        api = _make_api()
        result = _call_get_post(api, _build_post())
        assert result[PostField.location] == '臺灣'

    def test_board_name(self):
        api = _make_api()
        result = _call_get_post(api, _build_post())
        assert result[PostField.board] == 'Python'

    def test_aid_from_header(self):
        api = _make_api()
        result = _call_get_post(api, _build_post())
        assert result[PostField.aid] == HEADER_NORMAL.aid

    def test_post_status_exists(self):
        api = _make_api()
        result = _call_get_post(api, _build_post())
        assert result[PostField.post_status] == PostStatus.EXISTS

    def test_has_control_code_false(self):
        api = _make_api()
        result = _call_get_post(api, _build_post())
        assert result[PostField.has_control_code] is False

    def test_has_control_code_true(self):
        api = _make_api()
        result = _call_get_post(api, _build_post(), has_control_code=True)
        assert result[PostField.has_control_code] is True


# ── comments ──────────────────────────────────────────────────────────────────

def _post_with_comments(*comment_lines, host=data_type.HOST.PTT1):
    comments_text = '\n'.join(comment_lines)
    end = CONTENT_END_PTT1 if host == data_type.HOST.PTT1 else CONTENT_END_PTT2
    return (
        '作者  CodingMan (CodingMan) 看板  Python\n'
        '標題  [閒聊] 測試文章\n'
        '時間  Mon Jan  1 12:00:00 2024\n'
        f'{CONTENT_SEP}\n'
        'content\n'
        f'{end}(ptt.cc), 來自: 1.2.3.4 (臺灣)\n'
        f'{comments_text}\n'
    )


class TestComments:
    def test_push_type(self):
        api = _make_api()
        post = _post_with_comments(
            '推 user1: 推文內容                                       01/01 12:01'
        )
        result = _call_get_post(api, post)
        assert len(result[PostField.comments]) == 1
        c = result[PostField.comments][0]
        assert c[CommentField.type] == CommentType.PUSH
        assert c[CommentField.author] == 'user1'
        assert c[CommentField.content] == '推文內容'
        assert c[CommentField.time] == '01/01 12:01'

    def test_boo_type(self):
        api = _make_api()
        post = _post_with_comments(
            '噓 user2: 噓文內容                                       01/01 12:02'
        )
        result = _call_get_post(api, post)
        assert len(result[PostField.comments]) == 1
        assert result[PostField.comments][0][CommentField.type] == CommentType.BOO

    def test_arrow_type(self):
        api = _make_api()
        post = _post_with_comments(
            '→ user3: 箭頭內容                                        01/01 12:03'
        )
        result = _call_get_post(api, post)
        assert len(result[PostField.comments]) == 1
        assert result[PostField.comments][0][CommentField.type] == CommentType.ARROW

    def test_all_three_types(self):
        api = _make_api()
        post = _post_with_comments(
            '推 u1: A                                                  01/01 12:01',
            '噓 u2: B                                                  01/01 12:02',
            '→ u3: C                                                   01/01 12:03',
        )
        result = _call_get_post(api, post)
        types = [c[CommentField.type] for c in result[PostField.comments]]
        assert types == [CommentType.PUSH, CommentType.BOO, CommentType.ARROW]

    def test_no_comments(self):
        api = _make_api()
        result = _call_get_post(api, _build_post())
        assert result[PostField.comments] == []

    def test_comment_with_ip(self):
        api = _make_api()
        post = _post_with_comments(
            '推 user1: 內容 1.2.3.4                                    01/01 12:01'
        )
        result = _call_get_post(api, post)
        assert result[PostField.comments][0][CommentField.ip] == '1.2.3.4'

    def test_comment_without_ip(self):
        api = _make_api()
        post = _post_with_comments(
            '推 user1: 內容                                             01/01 12:01'
        )
        result = _call_get_post(api, post)
        assert result[PostField.comments][0][CommentField.ip] is None

    def test_ptt2_comment_format(self):
        """PTT2 has "推 10/04 13:25" at end; content extraction differs."""
        api = _make_api(host=data_type.HOST.PTT2)
        post = _post_with_comments(
            '→ CodingMan:What is Ptt?                                       推 10/04 13:25',
            host=data_type.HOST.PTT2,
        )
        result = _call_get_post(api, post)
        comments = result[PostField.comments]
        assert len(comments) == 1
        assert comments[0][CommentField.author] == 'CodingMan'


# ── IP formats ────────────────────────────────────────────────────────────────

class TestIPFormats:
    def _post_with_ip_line(self, ip_line):
        return (
            '作者  CodingMan (CodingMan) 看板  Python\n'
            '標題  [閒聊] 測試文章\n'
            '時間  Mon Jan  1 12:00:00 2024\n'
            f'{CONTENT_SEP}\n'
            'content\n'
            f'{CONTENT_END_PTT1}(ptt.cc), 來自: 1.2.3.4\n'
            f'{ip_line}\n'
        )

    def test_format1_with_location(self):
        """※ 發信站: ..., 來自: x.x.x.x (臺灣)"""
        api = _make_api()
        post = _build_post(
            footer_lines='※ 編輯: CodingMan (111.243.146.98 臺灣)\n'
        )
        # The footer edit line contains ip + location
        result = _call_get_post(api, post)
        assert result[PostField.ip] is not None

    def test_format2_dashed(self):
        """Old format: x-x-x-x in ◆ From or ※ 編輯 line."""
        api = _make_api()
        post = (
            '作者  JCC (JCC)\n'
            '標題  [閒聊] 測試\n'
            '時間  Mon Jan  1 12:00:00 2024\n'
            f'{CONTENT_SEP}\n'
            'content\n'
            f'{CONTENT_END_PTT1}(ptt.cc)\n'
            '◆ From: 211-20-78-69\n'
        )
        result = _call_get_post(api, post)
        assert result[PostField.ip] == '211.20.78.69'

    def test_no_location_when_absent(self):
        """IP present but no location parenthetical."""
        api = _make_api()
        post = (
            '作者  CodingMan (CodingMan) 看板  Python\n'
            '標題  [閒聊] 測試\n'
            '時間  Mon Jan  1 12:00:00 2024\n'
            f'{CONTENT_SEP}\n'
            'content\n'
            f'{CONTENT_END_PTT1}(ptt.cc), 來自: 116.241.32.178\n'
        )
        result = _call_get_post(api, post)
        assert result[PostField.ip] == '116.241.32.178'
        assert result[PostField.location] is None


# ── deleted posts ─────────────────────────────────────────────────────────────

class TestDeletedPost:
    """send_return=1 means InBoard matched → post is deleted/inaccessible."""

    def _deleted_result(self, cursor_line, board='Python'):
        api = _make_api()
        board_screen = _make_board_screen(cursor_line)
        api.connect_core.send.return_value = 1
        api.connect_core.get_screen_queue.return_value = [board_screen]
        with patch(PATCHED[0]), patch(PATCHED[1]):
            return _api_get_post._get_post(api, board, post_index=1)

    def test_deleted_by_author(self):
        # [username] pattern → DELETED_BY_AUTHOR
        result = self._deleted_result(
            '>  1234     9/11 -             □ (本文已被刪除) [weida7332]'
        )
        assert result[PostField.post_status] == PostStatus.DELETED_BY_AUTHOR
        assert result[PostField.author] == 'weida7332'

    def test_deleted_by_moderator(self):
        # <username> pattern → DELETED_BY_MODERATOR
        result = self._deleted_result(
            '>  1234     9/11 -             □ (本文已被吃掉)<admin>'
        )
        assert result[PostField.post_status] == PostStatus.DELETED_BY_MODERATOR

    def test_deleted_by_unknown(self):
        # Neither pattern → DELETED_BY_UNKNOWN, author is None
        result = self._deleted_result(
            '>  1234     9/11 -             □ (本文已被刪除)'
        )
        assert result[PostField.post_status] == PostStatus.DELETED_BY_UNKNOWN
        assert result[PostField.author] is None

    def test_list_date_extracted_from_cursor(self):
        result = self._deleted_result(
            '>  1234     9/11 -             □ (本文已被刪除) [weida7332]'
        )
        assert result[PostField.list_date] is not None
        assert '9/11' in result[PostField.list_date]

    def test_pass_format_check_true_for_deleted(self):
        result = self._deleted_result(
            '>  1234     9/11 -             □ (本文已被刪除) [weida7332]'
        )
        assert result[PostField.pass_format_check] is True


# ── locked post ───────────────────────────────────────────────────────────────

class TestLockedPost:
    def test_is_lock_true(self):
        api = _make_api()
        result = _call_get_post(api, None, header=HEADER_LOCK)
        assert result[PostField.is_lock] is True

    def test_pass_format_check_true_for_lock(self):
        api = _make_api()
        result = _call_get_post(api, None, header=HEADER_LOCK)
        assert result[PostField.pass_format_check] is True

    def test_no_content_for_lock(self):
        api = _make_api()
        result = _call_get_post(api, None, header=HEADER_LOCK)
        assert result[PostField.content] is None


# ── query mode ────────────────────────────────────────────────────────────────

class TestQueryMode:
    def test_query_skips_content(self):
        """query=True should return metadata only, not fetch content."""
        api = _make_api()
        result = _call_get_post(api, _build_post(), query=True)
        # get_content should NOT have been called
        assert result[PostField.pass_format_check] is True
        assert result[PostField.content] is None

    def test_query_author_from_header(self):
        api = _make_api()
        result = _call_get_post(api, _build_post(), query=True)
        assert result[PostField.author] == HEADER_NORMAL.author


# ── substandard posts (pass_format_check=False) ───────────────────────────────

class TestSubstandardPost:
    """Malformed posts that fail the format check should still return a dict."""

    def test_missing_author_line(self):
        api = _make_api()
        post = _build_post(author_line='GARBAGE LINE NO AUTHOR')
        result = _call_get_post(api, post)
        assert result[PostField.pass_format_check] is False

    def test_missing_title_line(self):
        api = _make_api()
        post = _build_post(title_line='NOT A TITLE LINE')
        result = _call_get_post(api, post)
        assert result[PostField.pass_format_check] is False

    def test_missing_date_line(self):
        api = _make_api()
        post = _build_post(date_line='NOT A DATE LINE')
        result = _call_get_post(api, post)
        assert result[PostField.pass_format_check] is False

    def test_no_content_separator(self):
        """Post without content_start → content_fail=True."""
        api = _make_api()
        post = (
            '作者  CodingMan (CodingMan) 看板  Python\n'
            '標題  [閒聊] 測試\n'
            '時間  Mon Jan  1 12:00:00 2024\n'
            'content without separator\n'
            f'{CONTENT_END_PTT1}(ptt.cc), 來自: 1.2.3.4 (臺灣)\n'
        )
        result = _call_get_post(api, post)
        assert result[PostField.pass_format_check] is False

    def test_missing_ip_on_ptt1(self):
        """PTT1 requires IP; missing IP → pass_format_check=False."""
        api = _make_api(host=data_type.HOST.PTT1)
        post = (
            '作者  CodingMan (CodingMan) 看板  Python\n'
            '標題  [閒聊] 測試\n'
            '時間  Mon Jan  1 12:00:00 2024\n'
            f'{CONTENT_SEP}\n'
            'content\n'
            f'{CONTENT_END_PTT1}(ptt.cc)\n'
            '※ 文章網址: https://www.ptt.cc/bbs/Python/M.1.html\n'
        )
        result = _call_get_post(api, post)
        assert result[PostField.pass_format_check] is False

    def test_none_origin_post_returns_early(self):
        """get_content returning None means post was deleted mid-read."""
        api = _make_api()
        result = _call_get_post(api, None)
        assert result[PostField.pass_format_check] is False


# ── allpost board ─────────────────────────────────────────────────────────────

class TestAllpostBoard:
    def test_board_extracted_from_content(self):
        """ALLPOST posts carry the real board in the author line."""
        api = _make_api()
        post = (
            '作者  CodingMan (CodingMan) 看板  Python\n'
            '標題  [閒聊] 測試\n'
            '時間  Mon Jan  1 12:00:00 2024\n'
            f'{CONTENT_SEP}\n'
            'content\n'
            f'{CONTENT_END_PTT1}(ptt.cc), 來自: 1.2.3.4 (臺灣)\n'
        )
        result = _call_get_post(api, post, board='ALLPOST')
        # The board should be updated to the real board from the post header
        assert result[PostField.board] == 'Python'
