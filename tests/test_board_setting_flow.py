"""No-network tests for the new (2026-10) PTT「看板設定與管理」flow used by
set_board_title and bucket.

A fake connect_core replays screens captured live on the give board (edit
menu, title prompt, Bakuman) and records every key PyPtt sends. The new edit
mode treats Enter/Space/most letters as "toggle this setting now", so the
tests pin both the exact key sequence on the happy path and that, once an
unknown screen shows up, PyPtt only sends ← / Ctrl-C to back out.
"""
from types import SimpleNamespace

import pytest

import PyPtt
from PyPtt import _api_bucket
from PyPtt import _api_set_board_title
from PyPtt import _api_util
from PyPtt import command
from PyPtt import connect_core
from PyPtt import screens

_ROWS = '''看板名稱: give 板主名單: SomeBM
{c1} 1.   中文敘述               [贈送] 歡迎來到贈送板
   2.   公開狀態 (是否隱形)    公開
   3.   隱板時進入十大排行榜   不可
   4.   非看板會員發文         開放
   5.   回應文章               不開放
   6.   自刪文章               開放
   7.   推薦文章 (推文)        開放
   8.   噓文                   開放
   9.   快速連推文章           開放
  10.   推文時記錄來源 IP      不會記錄
  11.   推文開頭自動對齊       不用對齊
  12.   板主刪除部份違規文字   無法
  13.   轉錄文章自動記錄       會 (需發文權限)
  14.   冷靜模式               未設定
  15.   未滿十八歲進入         允許
{c16}16.   [名單] 設定水桶名單    {lst}
  17.   [名單] 可見會員名單    {lst}
  18.   [名單] 投票限制名單    {lst}
  19.   [管理] 舉辦與管理投票  {lst}
  20.   [管理] 文章類別設定    {lst}
  21.   [管理] 發文注意事項    {lst}'''

_READONLY_FOOTER = ' 看板設定  (^P)開啟編輯 (PgUp)上頁 (PgDn)下頁 (1)跳號         (←)離開 (h)說明 '
_EDIT_FOOTER = ' 看板設定(編輯)  (Enter)切換/執行 (w)水桶名單 (v)可見名單     (←)離開 (h)說明 '


def _menu(header: str, bottom: str, lst: str, cursor16: bool = False) -> str:
    rows = _ROWS.format(c1='  ' if cursor16 else '> ', c16='> ' if cursor16 else '  ', lst=lst)
    return f' 看板設定與管理  [{header}]\n{rows}\n{bottom}'


READONLY = _menu('唯讀模式 (按 Ctrl-P 編輯)', _READONLY_FOOTER, '[唯讀檢視]')
VIEW_ONLY = _menu('唯讀檢視', ' 看板資訊  (PgUp)上頁 (PgDn)下頁 (1)跳號         (←)離開 (h)說明 ', '[唯讀檢視]')
EDIT = _menu('編輯模式 (按 Ctrl-P 唯讀)', _EDIT_FOOTER, '[進入編輯]')
EDIT_CURSOR16 = _menu('編輯模式 (按 Ctrl-P 唯讀)', _EDIT_FOOTER, '[進入編輯]', cursor16=True)
TITLE_PROMPT = _menu('編輯模式 (按 Ctrl-P 唯讀)', '請輸入看板新中文敘述: [贈送] 歡迎來到贈送板', '[進入編輯]')
UNCHANGED = _menu('編輯模式 (按 Ctrl-P 唯讀)', ' ◆ 未改變任何設定                                              [按任意鍵繼續] ',
                  '[進入編輯]')
SAVED = _menu('編輯模式 (按 Ctrl-P 唯讀)', ' ◆ 已儲存新設定                                                [按任意鍵繼續] ',
              '[進入編輯]')
UNKNOWN_MENU = ' 看板設定與管理  [某種沒見過的模式]\n' + _ROWS.format(c1='> ', c16='  ', lst='?') + '\n'

ARTICLE_LIST = '''【板主:SomeBM】                                                   看板《give》
[→]閱讀 [z]精華區 [Tab]文摘 [s]選擇看板 [b]進板 [i]看板設定 [^X]轉錄 [/]搜尋
   編號    日 期 作  者       文  章  標  題                            人氣:18
> 79947 +  10/18 someone      □ [贈送] 測試文章
 文章列表  (^P)發表 (y)回應 (X)推文 (d)刪除 (→)閱讀 (b)進板  (←)離開 (h)說明 '''

_BAKUMAN_HEADER = ' Bakuman 權限設定系統  看板: give ，類型: 停止發言(水桶)，名單上限: ∞'
BAKUMAN = _BAKUMAN_HEADER + '''
(A)增加 (D)提前清除 (S)取得目前狀態 (L)列出設定歷史 [Q]結束?

                   歡迎使用 Bakuman 權限設定系統!'''
BAKUMAN_ID = _BAKUMAN_HEADER + '\n請輸入使用者代號:'
BAKUMAN_PERIOD = _BAKUMAN_HEADER + '''
將使用者 CodingMan 加入看板 give 的禁言名單。
請以數字跟單位(預設為天)輸入期限:'''
BAKUMAN_REASON = BAKUMAN_PERIOD + ''' 1
期限將設定為 1 天之後: 10/20/2026 07:50:33
請輸入理由(空白可取消新增):'''
BAKUMAN_CONFIRM = _BAKUMAN_HEADER + '''

使用者 CodingMan 即將加入禁言名單 (期限: 1 天)
理由: PyPtt test

確認以上資料全部正確嗎？ [y/N]:'''
BAKUMAN_DONE = BAKUMAN_CONFIRM + ''' y
 ◆ 已將使用者加入禁言名單                                      [按任意鍵繼續] '''
BAKUMAN_BANNED = _BAKUMAN_HEADER + '''
 ◆ 使用者之前已被禁言，尚有 1 天；詳情可用(S)或(L)查看         [按任意鍵繼續] '''

LEFT, CTRL_C, CTRL_P, ENTER = command.left, command.ctrl_c, command.ctrl_p, command.enter
REFRESH = command.refresh  # Ctrl-L 重繪；PyPtt 每次送鍵本來就會附加，正式站實錄在編輯選單上無副作用


class FakeCore:
    """Replays one scripted screen per send() and records the keys sent.

    A None entry (or an exhausted script) is a silent timeout: no byte, no new
    screen. An Exception entry is raised from send() (e.g. UseTooManyResources).

    Matching mirrors connect_core: the first break_detect target that
    matches wins; no match (or no screen left) behaves like a timeout (-1)."""

    def __init__(self, screen_list, start=ARTICLE_LIST):
        self.screen_list = list(screen_list)
        self.queue = [start]
        self.keys = []
        self.closed = False
        self.last_timeout_was_silent = False

    def close(self):
        self.closed = True

    def get_screen_queue(self):
        return self.queue

    def send(self, msg, target_list, screen_timeout=0, refresh=True, secret=False):
        self.keys.append(msg)
        screen = self.screen_list.pop(0) if self.screen_list else None
        if isinstance(screen, BaseException):
            raise screen
        self.last_timeout_was_silent = screen is None
        if screen is None:
            return -1
        self.queue.append(screen)
        for index, target in enumerate(target_list):
            if target.is_match(screen, '>') and target.is_break():
                return index
        return -1


@pytest.fixture
def make_api(monkeypatch):
    for name in ('one_thread', 'goto_board', 'check_board', 'check_user_exist'):
        monkeypatch.setattr(_api_util, name, lambda *args, **kwargs: None)

    def _make(screen_list, start=ARTICLE_LIST):
        return SimpleNamespace(
            connect_core=FakeCore(screen_list, start),
            config=SimpleNamespace(screen_timeout=3.0, screen_long_timeout=10.0),
            _is_login=True,
            is_registered_user=True,
            cursor='>',
            _goto_board_list=set(),
        )

    return _make


def _typed(text: str) -> str:
    return _menu('編輯模式 (按 Ctrl-P 唯讀)', f'請輸入看板新中文敘述: {text}', '[進入編輯]')


def _assert_only_backout_keys(keys):
    for key in keys:
        assert key in (LEFT, CTRL_C, REFRESH), f'sent {key!r} after an unknown screen'


class TestSetBoardTitleNewFlow:
    def test_happy_path_keeps_category_prefix(self, make_api):
        text = '[贈送] 新標題 test'
        api = make_api([READONLY, EDIT, TITLE_PROMPT, _typed(text), EDIT, SAVED, ARTICLE_LIST])
        _api_set_board_title.set_board_title(api, 'give', '新標題 test')

        keys = api.connect_core.keys
        assert keys[:3] == ['I', CTRL_P, ENTER]
        assert keys[3].lstrip(command.backspace) == text
        assert keys[3].count(command.backspace) >= len('[贈送] 歡迎來到贈送板'.encode('big5uao'))
        assert keys[4:] == [ENTER, LEFT, LEFT]

    def test_edit_rows_with_hotkey_labels(self, make_api):
        # 2026-10-19 正式站編輯模式改版: 每列前面多了 '(b)' 這類熱鍵標示
        edit_v2 = EDIT.replace('>  1.   中文敘述               ', '>  1. (b)中文敘述                  ')
        assert '(b)中文敘述' in edit_v2
        text = '[贈送] 新標題 test'
        api = make_api([READONLY, edit_v2, TITLE_PROMPT, _typed(text), edit_v2, SAVED, ARTICLE_LIST])
        _api_set_board_title.set_board_title(api, 'give', '新標題 test')
        assert api.connect_core.keys[3].lstrip(command.backspace) == text

    def test_board_without_category_types_title_only(self, make_api):
        no_cat_edit = EDIT.replace('[贈送] 歡迎來到贈送板', '歡迎來到贈送板')
        no_cat_prompt = TITLE_PROMPT.replace('[贈送] 歡迎來到贈送板', '歡迎來到贈送板')
        api = make_api([READONLY, no_cat_edit, no_cat_prompt, _typed('abc'), EDIT, SAVED, ARTICLE_LIST])
        _api_set_board_title.set_board_title(api, 'give', 'abc')
        assert api.connect_core.keys[3].lstrip(command.backspace) == 'abc'

    def test_unknown_screen_after_ctrl_p_backs_out(self, make_api):
        api = make_api([READONLY, UNKNOWN_MENU, UNKNOWN_MENU, UNCHANGED, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.UnknownError):
            _api_set_board_title.set_board_title(api, 'give', 'x')
        keys = api.connect_core.keys
        assert keys[:2] == ['I', CTRL_P]
        assert keys[2:] == [REFRESH, LEFT, LEFT]

    def test_unrecognisable_screen_sends_one_left_then_closes(self, make_api):
        # 完全認不得的畫面: 重繪一次、試送一次 ←，仍確認不了文章列表就斷線
        api = make_api([READONLY, 'garbage screen', 'garbage screen', 'still garbage'])
        with pytest.raises(PyPtt.exceptions.ConnectionClosed):
            _api_set_board_title.set_board_title(api, 'give', 'x')
        assert api.connect_core.keys == ['I', CTRL_P, REFRESH, LEFT]
        assert api.connect_core.closed is True
        assert api._is_login is False

    def test_unrecognisable_screen_left_reaches_article_list(self, make_api):
        api = make_api([READONLY, 'garbage screen', 'garbage screen', UNCHANGED, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.UnknownError):
            _api_set_board_title.set_board_title(api, 'give', 'x')
        assert api.connect_core.keys == ['I', CTRL_P, REFRESH, LEFT, LEFT]

    def test_cursor_not_on_item_1_backs_out(self, make_api):
        api = make_api([READONLY, EDIT_CURSOR16, UNCHANGED, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.UnknownError):
            _api_set_board_title.set_board_title(api, 'give', 'x')
        _assert_only_backout_keys(api.connect_core.keys[2:])
        assert api.connect_core.keys[2:] == [LEFT, LEFT]

    def test_truncated_input_cancels_with_ctrl_c(self, make_api):
        # 輸入列沒顯示完整標題 (例如被截斷) → 不能送 Enter，要 Ctrl-C 取消
        api = make_api([READONLY, EDIT, TITLE_PROMPT, _typed('[贈送] 新標'), EDIT, UNCHANGED, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.UnknownError):
            _api_set_board_title.set_board_title(api, 'give', '新標題 test')
        keys = api.connect_core.keys
        assert keys[4:] == [CTRL_C, LEFT, LEFT]

    def test_non_moderator_view_only(self, make_api):
        api = make_api([VIEW_ONLY, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.NeedModeratorPermission):
            _api_set_board_title.set_board_title(api, 'give', 'x')
        assert api.connect_core.keys == ['I', LEFT]


class TestBucketNewFlow:
    def test_happy_path(self, make_api):
        api = make_api([READONLY, EDIT, BAKUMAN, BAKUMAN_ID, BAKUMAN_PERIOD, BAKUMAN_REASON, BAKUMAN_CONFIRM,
                        BAKUMAN_DONE, BAKUMAN, EDIT_CURSOR16, UNCHANGED, ARTICLE_LIST])
        _api_bucket.bucket(api, 'give', 1, 'PyPtt test', 'CodingMan')
        assert api.connect_core.keys == [
            'i', CTRL_P, 'w', 'a' + ENTER, 'CodingMan' + ENTER, '1' + ENTER, 'PyPtt test' + ENTER, 'y' + ENTER,
            LEFT, ENTER, LEFT, LEFT]

    def test_previously_banned_backs_out_then_raises(self, make_api):
        api = make_api([READONLY, EDIT, BAKUMAN, BAKUMAN_ID, BAKUMAN_BANNED, BAKUMAN, EDIT_CURSOR16, UNCHANGED,
                        ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.UserHasPreviouslyBeenBanned):
            _api_bucket.bucket(api, 'give', 1, 'PyPtt test', 'CodingMan')
        assert api.connect_core.keys[5:] == [LEFT, ENTER, LEFT, LEFT]

    def test_unknown_result_backs_out(self, make_api):
        failed = BAKUMAN_CONFIRM + ' y\n ◆ 失敗，請向站長報告                                          [按任意鍵繼續] '
        api = make_api([READONLY, EDIT, BAKUMAN, BAKUMAN_ID, BAKUMAN_PERIOD, BAKUMAN_REASON, BAKUMAN_CONFIRM,
                        failed, BAKUMAN, EDIT_CURSOR16, UNCHANGED, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.UnknownError):
            _api_bucket.bucket(api, 'give', 1, 'PyPtt test', 'CodingMan')
        assert api.connect_core.keys[8:] == [LEFT, ENTER, LEFT, LEFT]

    def test_unknown_screen_after_w_backs_out(self, make_api):
        api = make_api([READONLY, EDIT, UNKNOWN_MENU, UNCHANGED, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.UnknownError):
            _api_bucket.bucket(api, 'give', 1, 'PyPtt test', 'CodingMan')
        keys = api.connect_core.keys
        assert keys[:3] == ['i', CTRL_P, 'w']
        _assert_only_backout_keys(keys[3:])


class TestBoardSettingExitKey:
    @pytest.mark.parametrize('screen, key', [
        (READONLY, LEFT),
        (EDIT, LEFT),
        (UNCHANGED, LEFT),
        (TITLE_PROMPT, CTRL_C),
        (BAKUMAN, ENTER),
        (BAKUMAN_ID, CTRL_C),
        (BAKUMAN_CONFIRM, CTRL_C),
        (BAKUMAN_DONE, LEFT),
        (ARTICLE_LIST, None),
        ('garbage screen', None),
    ])
    def test_exit_key(self, screen, key):
        assert screens.board_setting_exit_key(screen) == key

    @pytest.mark.parametrize('screen', [READONLY, EDIT, UNCHANGED, TITLE_PROMPT, BAKUMAN, BAKUMAN_ID, BAKUMAN_DONE])
    def test_never_space_or_letters(self, screen):
        assert screens.board_setting_exit_key(screen) in (LEFT, CTRL_C, ENTER)


class TestReview2Findings:
    """review2-safety.md F1-F6: each test fails if its fix is reverted."""

    # F1: control characters would submit an input line early and turn the
    # rest of the string into edit-menu hotkeys.
    @pytest.mark.parametrize('title', ['abc\rgr', 'a\x7fb', 'tab\there', 'x\x1bOD'])
    def test_f1_title_control_chars_rejected_before_any_key(self, make_api, title):
        api = make_api([READONLY, EDIT, TITLE_PROMPT, EDIT, SAVED, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_set_board_title.set_board_title(api, 'give', title)
        assert api.connect_core.keys == []

    @pytest.mark.parametrize('reason, ptt_id', [('x\ry', 'CodingMan'), ('ok', 'Coding\rMan'), ('a\x7f', 'CodingMan')])
    def test_f1_bucket_control_chars_rejected_before_any_key(self, make_api, reason, ptt_id):
        api = make_api([READONLY, EDIT, BAKUMAN, BAKUMAN_ID, BAKUMAN_PERIOD, BAKUMAN_REASON, BAKUMAN_CONFIRM])
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_bucket.bucket(api, 'give', 1, reason, ptt_id)
        assert api.connect_core.keys == []

    # F2: board title / bucket reason are user content on the same screen;
    # the exit key must come from fixed positions, not a whole-screen search.
    @pytest.mark.parametrize('title', ['[Q]結束?', '輸入期限', '請輸入理由', '任意鍵', '請輸入看板新中文敘述:'])
    def test_f2_user_title_does_not_change_exit_key(self, title):
        for screen in (EDIT, EDIT_CURSOR16, READONLY):
            assert screens.board_setting_exit_key(screen.replace('歡迎來到贈送板', title)) == LEFT

    def test_f2_reason_with_anykey_on_confirm_screen_still_cancels(self):
        screen = BAKUMAN_CONFIRM.replace('理由: PyPtt test', '理由: 請按任意鍵繼續 [按任意鍵繼續]')
        assert screens.board_setting_exit_key(screen) == CTRL_C

    def test_f2_leave_with_prompt_like_title_exits_in_one_left(self, make_api):
        scr = EDIT.replace('歡迎來到贈送板', '輸入期限')
        api = make_api([UNCHANGED, ARTICLE_LIST], start=scr)
        assert _api_util.leave_board_setting(api) is True
        assert api.connect_core.keys == [LEFT, LEFT]

    def test_f3_timeouts_close_session(self, make_api):
        api = make_api([], start=EDIT)  # every send times out without a byte
        assert _api_util.leave_board_setting(api) is False
        # one ← on the edit menu, then only redraw requests (never ← again on a stale screen)
        assert api.connect_core.keys == [LEFT, REFRESH, REFRESH, REFRESH]
        assert api.connect_core.closed is True
        assert api._is_login is False

    def test_f3_failed_flow_closes_session_when_it_cannot_leave(self, make_api):
        api = make_api([READONLY, EDIT, TITLE_PROMPT, _typed('[贈送] x')] + [EDIT] * 30)
        with pytest.raises(PyPtt.exceptions.ConnectionClosed):
            _api_set_board_title.set_board_title(api, 'give', 'something else')
        _assert_only_backout_keys(api.connect_core.keys[4:])
        assert api.connect_core.closed is True

    # F5: after a timeout the last screen may be stale; redraw instead of
    # repeating the key (a second Enter would land on the edit menu).
    def test_f5_timeout_redraws_instead_of_repeating_key(self, make_api):
        api = make_api(['partial junk', EDIT_CURSOR16, UNCHANGED, ARTICLE_LIST], start=BAKUMAN)
        assert _api_util.leave_board_setting(api) is True
        assert api.connect_core.keys == [ENTER, REFRESH, LEFT, LEFT]

    # F4: the 30-byte limit includes the '[類別] ' prefix typed on the new UI.
    def test_f4_prefix_counts_toward_limit(self, make_api):
        api = make_api([READONLY, EDIT, UNCHANGED, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_set_board_title.set_board_title(api, 'give', 'a' * 24)  # 7 + 24 = 31 bytes
        assert api.connect_core.keys == ['I', CTRL_P, LEFT, LEFT]

    def test_f4_prefix_plus_title_at_limit_ok(self, make_api):
        text = '[贈送] ' + 'a' * 23  # 30 bytes
        api = make_api([READONLY, EDIT, TITLE_PROMPT, _typed(text), EDIT, SAVED, ARTICLE_LIST])
        _api_set_board_title.set_board_title(api, 'give', 'a' * 23)
        assert api.connect_core.keys[3].lstrip(command.backspace) == text

    # F6: bucket_days must be a positive int (bool is an int subclass).
    @pytest.mark.parametrize('days', [0, -1, True, False])
    def test_f6_bad_bucket_days_rejected_before_any_key(self, make_api, days):
        api = make_api([READONLY])
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_bucket.bucket(api, 'give', days, 'r', 'CodingMan')
        assert api.connect_core.keys == []


POST_BY_NICK = ('{} 作者  evil ({})                                 看板  Test\n'
                ' 標題  hi\n 時間  Sun Oct 19 08:00:00 2026\n\nbody\n' + '\n' * 17 +
                '  瀏覽 第 1/1 頁 (100%)  目前顯示: 第 01~05 行  (y)回應(X%)推文(h)說明(←)離開 ')
CRAFTED_TITLE = '[i]看板設定文章列表(b)進板'  # 26 Big5 bytes, contains every InBoard substring


class TestReview3Findings:
    """review3-safety.md N1/N2/N3/F5/F6: each test fails if its fix is reverted."""

    # N1: goto_board is back to origin/master; an article page whose header
    # carries a nickname like 權限設定系統 must not trigger any extra key.
    @pytest.mark.parametrize('nick', ['權限設定系統', '看板設定與管理', 'Bakuman 權限設定系統'])
    def test_n1_goto_board_sends_no_extra_key_on_article_page(self, make_api, monkeypatch, nick):
        monkeypatch.undo()  # real goto_board
        post = POST_BY_NICK.format('', nick)
        assert not screens.in_board_setting(post)
        assert screens.board_setting_exit_key(post) is None
        api = make_api([ARTICLE_LIST], start=post)
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [command.go_main_menu + 'qsgive' + ENTER + CTRL_C * 5]
        assert api._is_login is True

    def test_n1_header_must_start_the_line(self):
        # only a header that *starts* the top line counts; the nickname sits mid-line
        assert not screens.in_board_setting(POST_BY_NICK.format('', '看板設定與管理  [唯讀模式 (按 Ctrl-P 編輯)]'))
        assert screens.in_board_setting(READONLY)
        assert screens.in_board_setting(BAKUMAN)

    # N2: a board title containing every InBoard substring must not make the
    # edit menu count as the article list.
    def test_n2_crafted_title_is_not_article_list(self, make_api):
        edit = EDIT.replace('[贈送] 歡迎來到贈送板', CRAFTED_TITLE)
        assert connect_core.TargetUnit(screens.Target.InBoard).is_match(edit, '>')  # the trap
        api = make_api([])
        assert not _api_util.is_article_list(api, edit)
        assert _api_util.is_article_list(api, ARTICLE_LIST)

    def test_n2_failed_bucket_on_crafted_board_still_leaves(self, make_api):
        ro = READONLY.replace('[贈送] 歡迎來到贈送板', CRAFTED_TITLE)
        edit = EDIT.replace('[贈送] 歡迎來到贈送板', CRAFTED_TITLE)
        api = make_api([ro, edit, edit, UNCHANGED, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.UnknownError):
            _api_bucket.bucket(api, 'give', 1, 'r', 'CodingMan')
        assert api.connect_core.keys == ['i', CTRL_P, 'w', LEFT, LEFT]

    def test_n2_success_path_confirms_real_article_list(self, make_api):
        edit = EDIT.replace('[贈送] 歡迎來到贈送板', CRAFTED_TITLE)
        # the final ← "lands" on the edit menu again (it matches InBoard by substring)
        api = make_api([READONLY, EDIT, TITLE_PROMPT, _typed('[贈送] t'), EDIT, SAVED, edit, UNCHANGED, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.UnknownError):
            _api_set_board_title.set_board_title(api, 'give', 't')
        assert api.connect_core.keys[-3:] == [LEFT, LEFT, LEFT]

    # N3: exceptions raised by send() itself (UseTooManyResources) still leave.
    def test_n3_use_too_many_resources_leaves_first(self, make_api):
        api = make_api([READONLY, EDIT, PyPtt.exceptions.UseTooManyResources(), UNCHANGED, ARTICLE_LIST])
        api.connect_core.queue.append(EDIT)
        with pytest.raises(PyPtt.exceptions.UseTooManyResources):
            _api_set_board_title.set_board_title(api, 'give', 't')
        assert api.connect_core.keys == ['I', CTRL_P, ENTER, LEFT, LEFT]
        assert api._is_login is True

    def test_n3_connection_closed_during_leave_is_connection_closed(self, make_api):
        api = make_api([READONLY, 'garbage', PyPtt.exceptions.ConnectionClosed()])
        with pytest.raises(PyPtt.exceptions.ConnectionClosed):
            _api_set_board_title.set_board_title(api, 'give', 't')
        assert api._is_login is False

    # B1: KeyboardInterrupt mid-flow -> no more keys, session closed.
    def test_b1_keyboard_interrupt_closes_without_keys(self, make_api):
        api = make_api([READONLY, EDIT, KeyboardInterrupt()])
        with pytest.raises(KeyboardInterrupt):
            _api_set_board_title.set_board_title(api, 'give', 't')
        assert api.connect_core.keys == ['I', CTRL_P, ENTER]
        assert api.connect_core.closed is True
        assert api._is_login is False

    # F5: the step's own key timed out silently -> first leave key is a redraw.
    def test_f5_step_silent_timeout_redraws_first(self, make_api):
        api = make_api([READONLY, EDIT, BAKUMAN, BAKUMAN_ID, BAKUMAN_PERIOD, BAKUMAN_REASON, BAKUMAN_CONFIRM,
                        BAKUMAN_DONE, BAKUMAN, None, EDIT_CURSOR16, UNCHANGED, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.UnknownError):
            _api_bucket.bucket(api, 'give', 1, 'r', 'CodingMan')
        keys = api.connect_core.keys
        assert keys[9] == ENTER  # the silent CR at [Q]結束?
        assert keys[10:] == [REFRESH, LEFT, LEFT]

    # F6: upper bound from pttbbs (expiry must fit in 32 bits, 7-digit input).
    def test_f6_upper_bound(self, make_api):
        max_days = _api_bucket._bucket_days_max()
        assert 20000 < max_days < 40000  # ~2106-02-07 counted from the 2020s-2040s
        for days in (max_days + 1, 10 ** 9):
            api = make_api([])
            with pytest.raises(PyPtt.exceptions.ParameterError):
                _api_bucket.bucket(api, 'give', days, 'r', 'CodingMan')
            assert api.connect_core.keys == []
        api = make_api([READONLY, EDIT, BAKUMAN, BAKUMAN_ID, BAKUMAN_PERIOD, BAKUMAN_REASON, BAKUMAN_CONFIRM,
                        BAKUMAN_DONE, BAKUMAN, EDIT_CURSOR16, UNCHANGED, ARTICLE_LIST])
        _api_bucket.bucket(api, 'give', max_days, 'r', 'CodingMan')
        assert api.connect_core.keys[5] == f'{max_days}' + ENTER
