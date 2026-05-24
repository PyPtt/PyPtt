"""
Unit tests for _api_get_post_list line-parsing logic.

Drive get_post_list() with a mocked api that returns a hand-crafted board
listing screen, then assert the parsed post records line up with the input.
No network required.

The fixed-column offsets in _api_get_post_list ([:8], [8:10], [10:12], etc.)
were calibrated to the "1 extra leading space" layout that VT100Parser used
to produce. After the cursor-tracking overhaul the implicit pad is gone, so
the function adds an explicit `f' {line}'` prefix to keep the offsets valid.
These tests pin that contract down.
"""
import threading
from unittest.mock import MagicMock

import pytest

import PyPtt
from PyPtt import _api_get_post_list, data_type, i18n

# i18n strings are accessed by _api_get_post_list's error paths; init once.
i18n.init(PyPtt.Language.ENGLISH)


def _build_screen(cursor_line: str, after_cursor_lines: list[str] | None = None) -> str:
    """Compose a 24-row listing screen with header + cursor + (body) + footer.

    Real PTT layout when paginating to start_index:
      [0]   board title row
      [1]   hotkey hints
      [2]   column header (編號, 日 期, ...)
      [3]   cursor row (the starting index PTT landed on)
      [4..] subsequent listing rows
      [23]  footer hints

    `_api_get_post_list` skips lines until it finds the cursor row, then
    parses it and every later row. So body rows should come *after* the
    cursor row to be visible to the parser.
    """
    header = [
        '【徵求中】                      Python 程式語言                  看板《Python》',
        '[←]離開 [→]閱讀 [Ctrl-P]發表文章 [d]刪除 [z]精華區 [i]看板資訊/設定 [h]說明',
        '   編號    日 期 作  者       文  章  標  題                           人氣:1  ',
    ]
    footer = ' 文章選讀  (y)回應(X)推文(^X)轉錄 (=[]<>)相關主題(/?a)找標題/作者 (b)進板畫面  '
    rows = [cursor_line] + (after_cursor_lines or [])
    blank_pad = 24 - len(header) - len(rows) - 1
    if blank_pad > 0:
        rows.extend([''] * blank_pad)
    elif blank_pad < 0:
        rows = rows[:24 - len(header) - 1]
    return '\n'.join(header + rows + [footer])


def _build_api(screen: str, cursor: str = '>', newest: int = 9458):
    api = MagicMock()
    api._is_login = True
    api._thread_id = threading.get_ident()  # bypass one_thread guard
    api.cursor = cursor
    api.config.screen_height = 24  # required by expanded_screen()
    api.get_newest_index = MagicMock(return_value=newest)
    api.connect_core = MagicMock()
    api.connect_core.send = MagicMock(return_value=0)
    api.connect_core.get_screen_queue = MagicMock(return_value=[screen])
    return api


# ── basic row layouts ─────────────────────────────────────────────────────────

class TestLineLayouts:
    """Each row format PTT can render, verified through the public function."""

    def test_simple_single_digit_push(self):
        # PTT layout: 3 leading spaces + index(4) + space + push(1) + ' ' + date.
        cursor = '>  9458   2 5/07 fragmentwing □ [問題] openpyxl 全局Font？'
        api = _build_api(_build_screen(cursor, []))
        posts = _api_get_post_list.get_post_list(api, 'Python', limit=1)
        assert len(posts) == 1
        p = posts[0]
        assert p[data_type.PostField.index] == 9458
        assert p[data_type.PostField.push_number] == '2'
        assert p[data_type.PostField.list_date] == '5/07'
        assert p[data_type.PostField.author] == 'fragmentwing'
        assert '[問題] openpyxl 全局Font？' in p[data_type.PostField.title]

    def test_two_digit_push(self):
        # 10+ pushes occupy 2 chars, eat into the date column gap.
        cursor = '>  9447  17 7/17 ok8ok8       □ [閒聊] 各位現在用 os.path'
        api = _build_api(_build_screen(cursor, []), newest=9447)
        posts = _api_get_post_list.get_post_list(api, 'Python', limit=1)
        assert posts[0][data_type.PostField.push_number] == '17'
        assert posts[0][data_type.PostField.list_date] == '7/17'

    def test_plus_prefix_push(self):
        # '+N' is the "new pushes this session" marker; PTT packs it tight
        # against a 2-digit-month date with no separating space.
        cursor = '>  9449 + 610/09 edward740706 □ [問題] OMIA PLUS 自學嗎?'
        api = _build_api(_build_screen(cursor, []), newest=9449)
        posts = _api_get_post_list.get_post_list(api, 'Python', limit=1)
        assert posts[0][data_type.PostField.push_number] == '6'
        assert posts[0][data_type.PostField.list_date] == '10/09'
        assert posts[0][data_type.PostField.author] == 'edward740706'

    def test_tilde_prefix_push(self):
        # '~N' is the alt push prefix that should slice the same as '+N'.
        cursor = '>  9456 ~ 7 2/24 leolarrel    □ [問題] super() 與 MRO'
        api = _build_api(_build_screen(cursor, []), newest=9456)
        posts = _api_get_post_list.get_post_list(api, 'Python', limit=1)
        assert posts[0][data_type.PostField.push_number] == '7'
        assert posts[0][data_type.PostField.list_date] == '2/24'

    def test_no_push_count(self):
        # New post / no pushes yet → push column is blank spaces.
        cursor = '>  9457     4/17 Sumiremywife □ [問題] 關於爬蟲的一些問題'
        api = _build_api(_build_screen(cursor, []), newest=9457)
        posts = _api_get_post_list.get_post_list(api, 'Python', limit=1)
        assert posts[0][data_type.PostField.push_number] == ''
        assert posts[0][data_type.PostField.list_date] == '4/17'

    def test_reply_marker_R_in_title(self):
        # Title section includes the kind marker ('R:', '□', '轉', '鎖').
        cursor = '>  9440   4 1/15 ddavid       R: [問題] @property 真正的運用是啥'
        api = _build_api(_build_screen(cursor, []), newest=9440)
        posts = _api_get_post_list.get_post_list(api, 'Python', limit=1)
        assert posts[0][data_type.PostField.title].lstrip().startswith('R:')


# ── multi-row listing (non-cursor rows align too) ─────────────────────────────

class TestMultiRowListing:
    """The fix's key claim: non-cursor rows pick up the same leading-space
    pad as cursor rows, so the column offsets work uniformly."""

    def test_non_cursor_rows_parse_with_same_offsets(self):
        # Cursor lands on the starting index; later rows follow.
        cursor = '>  9449   610/09 edward740706 □ [問題] OMIA PLUS 自學嗎?'
        after = [
            '   9450 + 110/22 dosiris      □ [問題] 關於正規表示法',
            '   9451 ~ 110/29 kakar0to     □ [問題] python 3.14 free thread',
            '   9452 ~ 112/13 iread        □ 執行 Python 程式的六種方法',
        ]
        api = _build_api(_build_screen(cursor, after), newest=9452)
        posts = _api_get_post_list.get_post_list(api, 'Python', limit=4)
        assert [p[data_type.PostField.index] for p in posts] == [9449, 9450, 9451, 9452]
        assert [p[data_type.PostField.list_date] for p in posts] == \
            ['10/09', '10/22', '10/29', '12/13']
        assert [p[data_type.PostField.author] for p in posts] == \
            ['edward740706', 'dosiris', 'kakar0to', 'iread']
        # Non-cursor rows must NOT have the '□' marker bleeding into author.
        for p in posts[1:]:
            assert '□' not in p[data_type.PostField.author]


# ── regression: master before the fix would mis-slice these ───────────────────

class TestRegressionAgainstMasterBug:
    """Before the prepend-space fix, non-cursor rows lost one character per
    column: '10/22' → '0/22', 'dosiris' → 'osiris', and the '□' marker
    leaked into the author slot. These tests would have failed on master."""

    @pytest.mark.parametrize('cursor_line,want', [
        ('>  9450 + 110/22 dosiris      □ [問題] 關於正規表示法',
         {'index': 9450, 'date': '10/22', 'author': 'dosiris', 'push': '1'}),
        ('>  9447  17 7/17 ok8ok8       □ [閒聊] os.path',
         {'index': 9447, 'date': '7/17', 'author': 'ok8ok8', 'push': '17'}),
        ('>  9453 + 212/23 tamacugi     □ [閒聊] 合購股票pythony資料庫',
         {'index': 9453, 'date': '12/23', 'author': 'tamacugi', 'push': '2'}),
    ])
    def test_no_off_by_one_on_packed_layouts(self, cursor_line, want):
        api = _build_api(_build_screen(cursor_line, []), newest=want['index'])
        posts = _api_get_post_list.get_post_list(api, 'Python', limit=1)
        p = posts[0]
        assert p[data_type.PostField.index] == want['index']
        assert p[data_type.PostField.list_date] == want['date']
        assert p[data_type.PostField.author] == want['author']
        assert p[data_type.PostField.push_number] == want['push']
