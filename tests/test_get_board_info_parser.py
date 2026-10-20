"""No-network tests for get_board_info's parsing of PTT's new 'i' screen.

PTT replaced the old "《board》看板設定" page with a numbered
"看板設定與管理 [唯讀檢視]" menu; the fixtures below are live captures of it
(trailing padding stripped). mobilesales and Gossiping differ on most fields,
which catches substring bugs such as '開放' matching '不開放'.
"""

import os
import re
import threading

import pytest

from PyPtt import _api_get_board_info
from PyPtt import command
from PyPtt import config
from PyPtt import connect_core
from PyPtt import exceptions
from PyPtt import log
from PyPtt import screens
from PyPtt.data_type import BoardField

BOARD_SCREEN = '\n'.join([
    '【板主:Samuellu】                 你有新信件                看板《mobilesales》',
    '[→]閱讀 [z]精華區 [Tab]文摘 [s]選擇看板 [b]進板 [i]看板設定 [^X]轉錄 [/]搜尋',
    '   編號    日 期 作  者       文  章  標  題                            人氣:65',
    '  79949 +  10/18 zxe841123    □ [賣/雙北/面交] iPhone 15 Pro 256G 黑色',
    ' 文章列表  (^P)發表 (y)回應 (X)推文 (d)刪除 (→)閱讀 (b)進板  (←)離開 (h)說明',
])

MOBILESALES_INFO = '\n'.join([
    ' 看板設定與管理  [唯讀檢視]',
    '看板名稱: mobilesales 板主名單: Samuellu',
    '>  1.   中文敘述               [Mobile] 遵守版規，進桶看通知信',
    '   2.   公開狀態 (是否隱形)    公開',
    '   3.   隱板時進入十大排行榜   不可',
    '   4.   非看板會員發文         開放',
    '   5.   回應文章               不開放',
    '   6.   自刪文章               不開放',
    '   7.   推薦文章 (推文)        開放',
    '   8.   噓文                   開放',
    '   9.   快速連推文章           開放',
    '  10.   推文時記錄來源 IP      自動記錄',
    '  11.   推文開頭自動對齊       對齊',
    '  12.   板主刪除部份違規文字   無法',
    '  13.   轉錄文章自動記錄       會 (需發文權限)',
    '  14.   冷靜模式               未設定',
    '  15.   未滿十八歲進入         允許',
    '  16.   [名單] 設定水桶名單    [唯讀檢視]',
    '  17.   [名單] 可見會員名單    [唯讀檢視]',
    '  18.   [名單] 投票限制名單    [唯讀檢視]',
    '  19.   [管理] 舉辦與管理投票  [唯讀檢視]',
    '  20.   [管理] 文章類別設定    [唯讀檢視]',
    '  21.   [管理] 發文注意事項    [唯讀檢視]',
    ' 看板資訊  (PgUp)上頁 (PgDn)下頁 (1)跳號                      (←)離開 (h)說明',
])

GOSSIPING_INFO = '\n'.join([
    ' 看板設定與管理  [唯讀檢視]',
    '看板名稱: Gossiping 板主名單: ubcs/初音未來/redDest',
    '>  1.   中文敘述               [八卦] 梅毒可解，崆峒神威！！',
    '   2.   公開狀態 (是否隱形)    公開',
    '   3.   隱板時進入十大排行榜   可以',
    '   4.   非看板會員發文         開放',
    '   5.   回應文章               開放',
    '   6.   自刪文章               開放',
    '   7.   推薦文章 (推文)        開放',
    '   8.   噓文                   開放',
    '   9.   快速連推文章           限制 (間隔 5 秒)',
    '  10.   推文時記錄來源 IP      自動記錄',
    '  11.   推文開頭自動對齊       不用對齊',
    '  12.   板主刪除部份違規文字   可',
    '  13.   轉錄文章自動記錄       會 (需發文權限)',
    '  14.   冷靜模式               未設定',
    '  15.   未滿十八歲進入         禁止',
    '  16.   [名單] 設定水桶名單    [唯讀檢視]',
    '  17.   [名單] 可見會員名單    [唯讀檢視]',
    '  18.   [名單] 投票限制名單    [唯讀檢視]',
    '  19.   [管理] 舉辦與管理投票  [唯讀檢視]',
    '  20.   [管理] 文章類別設定    [唯讀檢視]',
    '  21.   [管理] 發文注意事項    [唯讀檢視]',
    ' 看板資訊  (PgUp)上頁 (PgDn)下頁 (1)跳號                      (←)離開 (h)說明',
])


class FakeConnectCore:
    def __init__(self, screens):
        self._screens = list(screens)
        self.last_timeout_was_silent = False
        self.keys = []

    def send(self, msg, target_list, **kwargs):
        self.keys.append(msg)
        self._screens.pop(0)
        return 0

    def get_screen_queue(self):
        return [self._screens[0]]

    def close(self):
        self.closed = True


class FakeApi:
    def __init__(self, info_screen):
        self.config = config.Config()
        # goto_board() sends once, then get_board_info() sends 'i'; on the new
        # layout it then leaves the settings menu with ← back to the board.
        self.connect_core = FakeConnectCore(['', BOARD_SCREEN, info_screen, BOARD_SCREEN])
        self.cursor = '>'
        self._is_login = True
        self._thread_id = threading.get_ident()
        self._goto_board_list = set()


@pytest.fixture(autouse=True)
def quiet_logger():
    original = log.logger
    log.init(log.SILENT)
    yield
    log.logger = original


def _info(board, screen):
    return _api_get_board_info.get_board_info(FakeApi(screen), board, get_post_kind=False, call_by_others=True)


def test_mobilesales():
    info = _info('MobileSales', MOBILESALES_INFO)
    assert info[BoardField.board] == 'mobilesales'
    assert info[BoardField.online_user] == 64
    assert info[BoardField.moderators] == ['Samuellu']
    assert info[BoardField.mandarin_des] == '[Mobile] 遵守版規，進桶看通知信'
    assert info[BoardField.open_status] is True
    assert info[BoardField.into_top_ten_when_hide] is False
    assert info[BoardField.can_non_board_members_post] is True
    assert info[BoardField.can_reply_post] is False
    assert info[BoardField.self_del_post] is False
    assert info[BoardField.can_comment_post] is True
    assert info[BoardField.can_boo_post] is True
    assert info[BoardField.can_fast_push] is True
    assert info[BoardField.min_interval_between_comments] == 0
    assert info[BoardField.is_comment_record_ip] is True
    assert info[BoardField.is_comment_aligned] is True
    assert info[BoardField.can_moderators_del_illegal_content] is False
    assert info[BoardField.does_tran_post_auto_recorded_and_require_post_permissions] is True
    assert info[BoardField.is_cool_mode] is False
    assert info[BoardField.is_require18] is False
    assert info[BoardField.require_login_time] == 0
    assert info[BoardField.require_illegal_post] == 0
    assert info[BoardField.post_kind_list] == []


def test_gossiping():
    info = _info('gossiping', GOSSIPING_INFO)
    assert info[BoardField.board] == 'Gossiping'
    assert info[BoardField.moderators] == ['ubcs', '初音未來', 'redDest']
    assert info[BoardField.into_top_ten_when_hide] is True
    assert info[BoardField.can_reply_post] is True
    assert info[BoardField.self_del_post] is True
    assert info[BoardField.can_fast_push] is False
    assert info[BoardField.min_interval_between_comments] == 5
    assert info[BoardField.is_comment_aligned] is False
    assert info[BoardField.can_moderators_del_illegal_content] is True
    assert info[BoardField.is_require18] is True


def test_board_name_mismatch_raises_no_such_board():
    with pytest.raises(exceptions.NoSuchBoard):
        _info('Test', MOBILESALES_INFO)


def test_screen_targets_match_new_layout():
    # goto_board() 與各 API 都靠 InBoard 判斷「已在文章列表」；PTT 改版後舊字串全部對不上
    assert connect_core.TargetUnit(screens.Target.InBoard).is_match(BOARD_SCREEN, '>')
    # login() 會把帳號的游標 append 進全域 InBoardWithCursor（本機 pttbbs 是 ●）；fixture 沒有游標列，只驗前面的錨點
    base = screens.Target.InBoardWithCursor[:screens.Target.InBoardWithCursorLen]
    assert connect_core.TargetUnit(base).is_match(BOARD_SCREEN, '>')
    assert not connect_core.TargetUnit(screens.Target.InBoard).is_match(MOBILESALES_INFO, '>')
    assert connect_core.TargetUnit('(PgUp)上頁 (PgDn)下頁').is_match(MOBILESALES_INFO, '>')


# ---- 2026-10-19 layout: wider columns, posting-condition rows 16/17, and
# (edit mode only) hotkey labels like '(b)中文敘述' plus '(限站長)' notes.
# Live captures in tests/fixtures/board_info/ (trailing padding stripped).
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures', 'board_info')


def _fixture(name):
    with open(os.path.join(FIXTURE_DIR, name), encoding='utf-8') as f:
        return f.read()


_COMMON_GIVE = {
    BoardField.board: 'give',
    BoardField.moderators: ['janice001'],
    BoardField.mandarin_des: '[贈送] 歡迎來到贈送板',
    BoardField.open_status: True,
    BoardField.into_top_ten_when_hide: False,
    BoardField.can_non_board_members_post: True,
    BoardField.can_reply_post: False,
    BoardField.self_del_post: True,
    BoardField.can_comment_post: True,
    BoardField.can_boo_post: True,
    BoardField.can_fast_push: True,
    BoardField.min_interval_between_comments: 0,
    BoardField.is_comment_record_ip: False,
    BoardField.is_comment_aligned: False,
    BoardField.can_moderators_del_illegal_content: False,
    BoardField.does_tran_post_auto_recorded_and_require_post_permissions: True,
    BoardField.is_cool_mode: False,
    BoardField.is_require18: False,
    BoardField.require_login_time: 100,
    BoardField.require_illegal_post: 1,
}

EXPECTED_20261019 = {
    # 非板主「唯讀檢視」
    ('mobilesales', 'mobilesales_20261019.txt'): {
        BoardField.board: 'mobilesales',
        BoardField.moderators: ['Samuellu'],
        BoardField.mandarin_des: '[Mobile] 遵守版規，進桶看通知信',
        BoardField.into_top_ten_when_hide: False,
        BoardField.can_reply_post: False,
        BoardField.self_del_post: False,
        BoardField.can_fast_push: True,
        BoardField.is_comment_record_ip: True,
        BoardField.is_comment_aligned: True,
        BoardField.can_moderators_del_illegal_content: False,
        BoardField.is_require18: False,
        BoardField.require_login_time: 500,
        BoardField.require_illegal_post: 1,
    },
    ('Gossiping', 'gossiping_20261019.txt'): {
        BoardField.board: 'Gossiping',
        BoardField.moderators: ['ubcs', '初音未來', 'redDest'],
        BoardField.mandarin_des: '[八卦] 梅毒可解，崆峒神威！！',
        BoardField.into_top_ten_when_hide: True,
        BoardField.can_reply_post: True,
        BoardField.self_del_post: True,
        BoardField.can_fast_push: False,
        BoardField.min_interval_between_comments: 5,
        BoardField.is_comment_record_ip: True,
        BoardField.is_comment_aligned: False,
        BoardField.can_moderators_del_illegal_content: True,
        BoardField.is_require18: True,
        BoardField.require_login_time: 360,
        BoardField.require_illegal_post: 0,
    },
    ('Test', 'test_20261019.txt'): {
        BoardField.board: 'Test',
        BoardField.moderators: ['hank2579'],
        BoardField.mandarin_des: '[測試] 每週定期清除本板文章',
        BoardField.require_login_time: 0,  # 無限制
        BoardField.require_illegal_post: 0,  # 無限制
    },
    # 板主「唯讀模式 (按 Ctrl-P 編輯)」
    ('give', 'give_20261019.txt'): _COMMON_GIVE,
    # 板主「編輯模式」: 每列有 '(b)' 熱鍵標示與 '(限站長)' 權限註記
    ('give', 'give_edit_20261019.txt'): _COMMON_GIVE,
}


@pytest.mark.parametrize('board, fixture', list(EXPECTED_20261019))
def test_layout_20261019(board, fixture):
    info = _info(board, _fixture(fixture))
    for field, expected in EXPECTED_20261019[(board, fixture)].items():
        assert info[field] == expected, field


def test_layout_20261019_condition_rows_match_screen_text():
    # require_login_time / require_illegal_post 要與畫面原文的數字一致
    for (board, fixture) in EXPECTED_20261019:
        screen = _fixture(fixture)
        info = _info(board, screen)
        login = re.search(r'登入次數 +(\d+) 次以上', screen)
        illegal = re.search(r'退文篇數 +(\d+) 篇以下', screen)
        assert info[BoardField.require_login_time] == (int(login.group(1)) if login else 0)
        assert info[BoardField.require_illegal_post] == (int(illegal.group(1)) if illegal else 0)


def test_hotkey_label_on_first_row():
    info = _info('give', _fixture('give_edit_20261019.txt'))
    assert '(b)中文敘述' in _fixture('give_edit_20261019.txt')
    assert info[BoardField.mandarin_des] == '[贈送] 歡迎來到贈送板'


def test_leaves_settings_menu_after_parsing():
    # 新版選單沒有任意鍵提示；get_board_info 解析完要用 ← 退回文章列表，
    # 否則下一支 API 的 goto_board 開頭的 Space 會落在選單上。
    api = FakeApi(_fixture('give_20261019.txt'))
    _api_get_board_info.get_board_info(api, 'give', get_post_kind=False, call_by_others=True)
    assert api.connect_core.keys[-1] == command.left
    assert connect_core.TargetUnit(screens.Target.InBoard).is_match(api.connect_core.get_screen_queue()[-1], '>')


def test_left_that_does_not_reach_article_list_closes_session():
    # ← 之後若不是文章列表 (例如畫面沒變)，就斷線並丟 ConnectionClosed，不再送鍵
    api = FakeApi(_fixture('give_20261019.txt'))
    api.connect_core._screens[-1] = _fixture('give_20261019.txt')
    with pytest.raises(exceptions.ConnectionClosed):
        _api_get_board_info.get_board_info(api, 'give', get_post_kind=False, call_by_others=True)
    assert api.connect_core.keys[-1] == command.left
    assert api.connect_core.closed is True
    assert api._is_login is False


def test_no_such_board_after_i_still_leaves_menu():
    # 'i' 之後才發現看板名稱不符：也要先退出選單再丟 NoSuchBoard
    api = FakeApi(_fixture('give_20261019.txt'))
    with pytest.raises(exceptions.NoSuchBoard):
        _api_get_board_info.get_board_info(api, 'Test', get_post_kind=False, call_by_others=True)
    assert api.connect_core.keys[-1] == command.left
