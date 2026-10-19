"""No-network regression tests for the six APIs broken by PTT's 2026-10 UI update.

Screens under tests/fixtures/new_screens/ are real captures: the *_new / post_* /
newest_index_* / give_money_* files come from the production-site sweep logs, the
*_old files from the local bbsdocker/imageptt (old pttbbs) container.

ScreenCore replays those screens through the real TargetUnit matching, so a
target string that stops matching the captured screen fails the test.
"""
import asyncio
import pathlib
import re
import threading
from unittest.mock import MagicMock

import pytest

import PyPtt
from PyPtt import (_api_get_favourite_board, _api_get_newest_index, _api_get_post_list, _api_give_money,
                   _api_util, command, config, connect_core, data_type, exceptions, i18n, screens)

i18n.init(PyPtt.Language.ENGLISH)

FIX = pathlib.Path(__file__).parent / 'fixtures' / 'new_screens'


def _fx(name: str) -> str:
    return (FIX / name).read_text(encoding='utf-8')


class ScreenCore:
    """connect_core stand-in: each send() shows the next captured screen (the last
    one repeats) and runs the real targets on it, like connect_core._decode_screen."""

    def __init__(self, screen_list, cursor='>'):
        self._screens = list(screen_list)
        self._cursor = cursor
        self._queue = []
        self.sent = []
        self.last_timeout_was_silent = False

    def send(self, msg, target_list, screen_timeout=0, refresh=True, secret=False):
        self.sent.append(msg)
        while True:
            if len(self.sent) > 60:
                raise RuntimeError('runaway send loop')
            screen = self._screens.pop(0) if len(self._screens) > 1 else self._screens[0]
            self._queue.append(screen)
            for i, target in enumerate(target_list):
                if target.is_match(screen, self._cursor):
                    target.raise_exception()
                    if target.is_break():
                        return i
                    self.sent.append(target.get_response(screen))
                    break
            else:
                return -1

    def get_screen_queue(self):
        return self._queue[-1:]


def _mock_api(core, cursor='>'):
    api = MagicMock()
    api._is_login = True
    api._thread_id = threading.get_ident()
    api.cursor = cursor
    api.connect_core = core
    return api


# ── 1. get_post_list: the NAWS redraw must be swallowed ─────────────────────────

class FakeWs:
    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.sent = []

    async def send(self, data):
        self.sent.append(data)

    async def recv(self):
        if self.chunks:
            return self.chunks.pop(0)
        await asyncio.sleep(3600)


def _frame(text: str) -> bytes:
    return b'\x1b[H\x1b[2J' + '\r\n'.join(line.rstrip() for line in text.split('\n')).encode('utf-8')


def _sync(body: bytes) -> bytes:
    return b'\x1b[?2026h' + body + b'\x1b[?2026l'


def _real_core(chunks):
    fake_api = MagicMock()
    fake_api.config = config.Config()
    fake_api.config.screen_timeout = 0.2
    fake_api.config.screen_height = 24
    fake_api.cursor = '>'
    core = connect_core.API(fake_api)
    core.current_encoding = 'utf-8'
    core._core = FakeWs(chunks)
    return core


def _cursor_row(screen: str) -> str:
    return [line for line in screen.split('\n') if line.startswith('>')][0]


@pytest.mark.parametrize('redraw', [
    [_sync(_frame(_fx('post_list_stale.txt')))],                     # new PTT: one bracketed frame
    [b'\x1b[?2026h' + _frame(_fx('post_list_stale.txt'))[:900],      # new PTT: bracket split over frames
     _frame(_fx('post_list_stale.txt'))[900:] + b'\x1b[?2026l'],
    [_frame(_fx('post_list_stale.txt'))],                            # old pttbbs: no bracket
], ids=['sync', 'sync-split', 'old'])
def test_set_screen_height_swallows_resize_redraw(redraw):
    core = _real_core(redraw + [_frame(_fx('post_list_fresh.txt'))])
    core.set_screen_height(100)
    index = core.send('778447\r', [connect_core.TargetUnit(screens.Target.InBoard, break_detect=True)])
    assert index == 0
    assert _cursor_row(core.get_screen_queue()[-1]).startswith('>778447')


def test_set_screen_height_without_redraw_returns():
    core = _real_core([])
    core.set_screen_height(100)
    assert core.config.screen_height == 100


def test_get_post_list_reads_the_jump_not_the_resize_redraw():
    # goto_board reply, then PTT's redraw for the NAWS (cursor still on the ★ row), then the jump reply.
    stale = _sync(_frame(_fx('post_list_stale.txt')))
    core = _real_core([stale, stale, _frame(_fx('post_list_fresh.txt'))])
    api = _mock_api(core)
    api.config = core.config
    api._goto_board_list = set()
    api.get_newest_index = MagicMock(return_value=778451)  # cached: no navigation of its own

    posts = _api_get_post_list.get_post_list(api, 'Gossiping', limit=5)

    assert [p[data_type.PostField.index] for p in posts] == list(range(778447, 778452))
    assert posts[0][data_type.PostField.author] == 'danny0830'
    assert posts[-1][data_type.PostField.author] == 'razan'
    assert api.config.screen_height == 24
    assert b'qsGossiping\r' in core._core.sent[0]  # navigates even when get_newest_index was cached


# ── 2. get_post: long post's last page has no "(←)離開" ──────────────────────────

LAST_PAGE_STATUS = '  瀏覽 第 12/12 頁 (100%)  目前顯示: 第 1050~1148 行 (y)回應(X)推文    (h)說明 '


def _content_api(screen_list):
    api = _mock_api(ScreenCore(screen_list))
    api.config.screen_height = 100  # already expanded: no resize
    return api


def _last_page() -> str:
    return '\n'.join(_fx('post_page11.txt').split('\n')[:-1] + [LAST_PAGE_STATUS])


def test_post_end_matches_last_page_without_leave_hint():
    assert connect_core.TargetUnit(screens.Target.PostEnd).is_match(_last_page(), '>')


def test_get_content_stops_on_long_post_last_page():
    api = _content_api([_fx('post_page11.txt'), _last_page()])
    content, _ = _api_util.get_content(api)
    assert content is not None
    assert len(api.connect_core.sent) == 2


def test_get_content_raises_on_unrecognized_screen():
    # Pressing → past the end leaves the post; that list screen used to send it round and round.
    api = _content_api([_fx('post_page11.txt'), _fx('post_list_stale.txt')])
    with pytest.raises(exceptions.UnknownError):
        _api_util.get_content(api)


def test_get_content_raises_when_lines_stop_advancing():
    api = _content_api([_fx('post_page11.txt')])  # same page forever
    with pytest.raises(exceptions.UnknownError):
        _api_util.get_content(api)


# ── 3. get_newest_index: no search result opens the cursor post ──────────────────

@pytest.fixture
def no_board_nav(monkeypatch):
    monkeypatch.setattr(_api_util, 'check_board', lambda *a, **k: None)
    monkeypatch.setattr(_api_util, 'goto_board', lambda *a, **k: None)


def _newest_api(screen_list):
    api = _mock_api(ScreenCore(screen_list))
    api._newest_index_data = {}
    return api


def test_newest_index_no_search_result(no_board_nav):
    api = _newest_api([_fx('newest_index_board.txt'), _fx('newest_index_in_post.txt')])
    with pytest.raises(exceptions.NoSearchResult):
        _api_get_newest_index.get_newest_index(api, data_type.NewIndex.BOARD, board='Test',
                                               search_type=data_type.SearchType.AUTHOR,
                                               search_condition='janice001')


def test_newest_index_plain_board_still_parses(no_board_nav):
    api = _newest_api([_fx('newest_index_board.txt')])
    assert _api_get_newest_index.get_newest_index(api, data_type.NewIndex.BOARD, board='Test') == 824


def test_newest_index_unknown_screen_is_still_no_such_board(no_board_nav):
    api = _newest_api([_fx('give_money_amount_prompt.txt')])
    with pytest.raises(exceptions.NoSuchBoard):
        _api_get_newest_index.get_newest_index(api, data_type.NewIndex.BOARD, board='NoSuchBoardZZ')


# ── 4. give_money: new amount prompt ─────────────────────────────────────────────

def test_give_money_sends_tab_and_amount(monkeypatch):
    # The prompt screen also shows "這位幸運兒的id: CodingMan"; the amount target must win,
    # and "金額過少" is a parameter problem, not NoMoney.
    monkeypatch.setattr(_api_util, 'check_user_exist', lambda *a, **k: None)
    core = ScreenCore([_fx('give_money_amount_prompt.txt'), _fx('give_money_too_small.txt')])
    api = _mock_api(core)
    api.is_registered_user = True
    with pytest.raises(exceptions.ParameterError):
        _api_give_money.give_money(api, 'CodingMan', 10, None, None)
    assert core.sent[1] == command.tab + '10' + command.enter


@pytest.mark.parametrize('prompt', [
    '要給多少Ptt幣呢? (可按 TAB 切換輸入稅前/稅後金額, 稅率固定 10%)',    # PTT 2026-10
    '要給他多少Dtt幣呢? (可按 TAB 切換輸入稅前/稅後金額, 稅率固定 10%)',  # local old pttbbs
    '要給他多少Ptt幣呢?',                                                # pre-2026 PTT
])
def test_give_money_amount_prompt_variants(monkeypatch, prompt):
    monkeypatch.setattr(_api_util, 'check_user_exist', lambda *a, **k: None)
    core = ScreenCore([f'【給予Ptt幣】\n這位幸運兒的id: CodingMan\n{prompt}\n 請輸入金額:', '按任意鍵繼續'])
    api = _mock_api(core)
    api.is_registered_user = True
    _api_give_money.give_money(api, 'CodingMan', 10, None, None)
    assert core.sent[1] == command.tab + '10' + command.enter


# ── 5. get_all_boards: board list screen anchor ─────────────────────────────────

@pytest.mark.parametrize('name', ['all_boards_new.txt', 'all_boards_old.txt'])
def test_board_list_target_matches(name):
    assert connect_core.TargetUnit(screens.Target.InBoardList).is_match(_fx(name), '>')


# ── 6. get_favourite_boards: names parsed from row content ──────────────────────

def _favourites(names, cursor):
    return _api_get_favourite_board.get_favourite_board(_mock_api(ScreenCore([_fx(n) for n in names], cursor), cursor))


def test_favourites_new_screen():
    pages = [f'favourites_new_p{i}.txt' for i in range(1, 6)]
    fav = _favourites(pages, '>')
    names = [f['board'] for f in fav]
    assert len(names) == 83
    raw = '\n'.join(_fx(p) for p in pages)
    for name in names:  # every parsed name appears whole on screen, not missing its first letter
        assert re.search(rf'[ ˇ]{re.escape(name)} ', raw), name
    assert names[:4] == ['ALLPOST', 'AllTogether', 'Announce', 'AppsForBBS']
    for name in ['give', 'Gossiping', 'BM', 'cat', 'Cloud', 'MCP_Test', 'ZZZZZ', 'Billiard']:
        assert name in names
    by_name = {f['board']: f for f in fav}
    assert by_name['ALLPOST']['type'] == '文章'
    assert by_name['ALLPOST']['title'] == '跨板式LOCAL新文章'
    assert by_name['AllTogether']['title'] == '[歐兔] 當你的眼睛瞇著笑'
    assert by_name['Cloud']['title'] == '雲端服務使用心得 與 討論建構技術'
    assert by_name['iOS']['title'] == '[iOS] Welcome Apple HomeView (Si…'
    assert by_name['Stock']['title'] == '[股票]'


def test_favourites_old_screen():
    fav = _favourites(['favourites_old.txt'], data_type.Cursor.OLD)
    assert fav == [
        {'board': 'Test', 'type': '測試', 'title': 'PyPtt Test'},
        {'board': 'Python', 'type': '測試', 'title': 'PyPtt Python'},
    ]


@pytest.mark.parametrize('name', ['favourites_new_p1.txt', 'favourites_old.txt'])
def test_favourites_target_matches(name):
    target_list = []
    core = MagicMock()
    core.send.side_effect = lambda cmd, tl, *a, **k: target_list.extend(tl) or 0
    core.get_screen_queue.return_value = [_fx('favourites_new_p5.txt')]
    _api_get_favourite_board.get_favourite_board(_mock_api(core))
    assert target_list[0].is_match(_fx(name), '>')
