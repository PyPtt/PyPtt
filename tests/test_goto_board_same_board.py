"""No-network tests for goto_board's same-board shortcut.

When the previous API left PyPtt on the same board (article list, search
result, or an article opened from either), goto_board must not go back to the
main menu and re-enter the board; it only sends ← and confirms the list header
names the board. A search result is reused when the search conditions are the
same. Anything it cannot confirm takes the full path.
"""
from types import SimpleNamespace

import pytest

import PyPtt
from PyPtt import _api_util
from PyPtt import command
from PyPtt import config
from PyPtt.data_type import SearchType
from tests.test_board_setting_flow import ARTICLE_LIST, FakeCore

LEFT, ENTER, CTRL_C = command.left, command.enter, command.ctrl_c
FULL_PATH = command.go_main_menu + 'qsgive' + ENTER + CTRL_C * 5

POST = ('作者  someone (nick)                                 看板  give\n'
        ' 標題  [贈送] 測試文章\n 時間  Sun Oct 19 08:00:00 2026\n\nbody\n' + '\n' * 17 +
        '  瀏覽 第 1/1 頁 (100%)  目前顯示: 第 01~05 行  (y)回應(X%)推文(h)說明(←)離開 ')
QUERY_POPUP = (ARTICLE_LIST.rsplit('\n', 1)[0] +
               '\n ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ 請按任意鍵繼續 ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ')
OTHER_LIST = ARTICLE_LIST.replace('看板《give》', '看板《Test》')
MAIL_LIST = '''【郵件選單】                                                   信箱《SomeBM》
   編號   日 期 作 者          信  件  標  題
>    1 + 10/18 someone      測試
  (y)回信 (x)站內轉寄 (d/D)刪信 (^P)寄發新信 (←)離開 (h)說明 '''


SEARCH_LIST = (ARTICLE_LIST.replace('看板《give》', '系列《give》')
               .replace(' 文章列表  (^P)', ' 系列文章  (^P)'))
NO_RESULT = ARTICLE_LIST.rsplit('\n', 1)[0] + '\n ◆ 找不到符合條件的文章。                [按任意鍵繼續] '
KEYWORD = [(SearchType.KEYWORD, '贈送')]
AUTHOR = [(SearchType.AUTHOR, 'someone')]
KEYWORD_CMD = '/贈送' + ENTER
AUTHOR_CMD = 'asomeone' + ENTER


def make_api(screen_list, start, current_board='give', current_search=()):
    return SimpleNamespace(
        connect_core=FakeCore(screen_list, start),
        config=config.Config(),
        _is_login=True,
        cursor='>',
        _goto_board_list={'give'},
        _current_board=current_board,
        _current_search=tuple(current_search),
    )


class TestSameBoardShortcut:
    def test_article_list_of_same_board_sends_nothing(self):
        api = make_api([], start=ARTICLE_LIST)
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == []

    def test_board_name_is_case_insensitive(self):
        api = make_api([], start=ARTICLE_LIST)
        _api_util.goto_board(api, 'GIVE')
        assert api.connect_core.keys == []

    def test_article_of_same_board_sends_one_left(self):
        api = make_api([ARTICLE_LIST], start=POST)
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [LEFT]
        assert api._current_board == 'give'

    def test_refresh_redraws_instead_of_entering(self):
        # get_board_info 要最新的人氣：重畫一次，不重新進板
        api = make_api([ARTICLE_LIST], start=ARTICLE_LIST)
        _api_util.goto_board(api, 'give', refresh=True)
        assert api.connect_core.keys == [command.refresh]

    def test_refresh_from_article(self):
        api = make_api([ARTICLE_LIST, ARTICLE_LIST], start=POST)
        _api_util.goto_board(api, 'give', refresh=True)
        assert api.connect_core.keys == [LEFT, command.refresh]

    def test_query_popup_is_dismissed(self):
        # get_post(query=True) 停在「請按任意鍵繼續」
        api = make_api([ARTICLE_LIST], start=QUERY_POPUP)
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [' ']

    def test_popup_then_article(self):
        api = make_api([POST, ARTICLE_LIST], start=QUERY_POPUP)
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [' ', LEFT]

    def test_end_from_shortcut_jumps_to_bottom(self):
        api = make_api([ARTICLE_LIST, ARTICLE_LIST], start=POST)
        _api_util.goto_board(api, 'give', end=True)
        assert api.connect_core.keys == [LEFT, '1' + ENTER + '$']


class TestFallsBackToFullPath:
    def test_different_board(self):
        api = make_api([OTHER_LIST, ARTICLE_LIST], start=OTHER_LIST, current_board='test')
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [FULL_PATH]
        assert api._current_board == 'give'

    def test_unknown_current_board(self):
        # 第一次進板，或搜尋過後 (forget_current_board)
        api = make_api([ARTICLE_LIST], start=ARTICLE_LIST, current_board=None)
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [FULL_PATH]

    def test_header_names_another_board(self):
        # 追蹤的看板跟畫面不一致 (例如其他 API 換過地方) 時，以畫面為準
        api = make_api([ARTICLE_LIST], start=OTHER_LIST)
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [FULL_PATH]

    def test_left_from_article_lands_elsewhere(self):
        # 停在信件內文：← 回到信箱，不是看板
        api = make_api([MAIL_LIST, ARTICLE_LIST], start=POST)
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [LEFT, FULL_PATH]

    def test_left_times_out_with_data(self):
        api = make_api(['half drawn', ARTICLE_LIST], start=POST)
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [LEFT, FULL_PATH]

    def test_main_menu_screen(self):
        api = make_api([ARTICLE_LIST], start='【主功能表】                    批踢踢實業坊')
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [FULL_PATH]

    def test_refresh_redraw_not_list_takes_full_path(self):
        api = make_api(['garbage', ARTICLE_LIST], start=ARTICLE_LIST)
        _api_util.goto_board(api, 'give', refresh=True)
        assert api.connect_core.keys == [command.refresh, FULL_PATH]

    def test_popup_over_other_screen_takes_full_path(self):
        # 提示框關掉後不是這個看板 (例如查詢使用者之後)
        api = make_api(['【主功能表】   看板《give》\n (h)說明', ARTICLE_LIST], start=QUERY_POPUP)
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [' ', FULL_PATH]

    def test_silent_timeout_after_left_raises(self):
        api = make_api([None], start=POST)
        with pytest.raises(PyPtt.exceptions.ConnectionClosed):
            _api_util.goto_board(api, 'give')


class TestSearch:
    def test_same_search_list_sends_nothing(self):
        api = make_api([], start=SEARCH_LIST, current_search=KEYWORD)
        _api_util.goto_board(api, 'give', search_list=KEYWORD)
        assert api.connect_core.keys == []

    def test_article_from_same_search_sends_one_left(self):
        api = make_api([SEARCH_LIST], start=POST, current_search=KEYWORD)
        _api_util.goto_board(api, 'give', search_list=KEYWORD)
        assert api.connect_core.keys == [LEFT]
        assert api._current_search == tuple(KEYWORD)

    def test_plain_list_wanted_from_search_list(self):
        # 搜尋結果 ← 一次就回到一般列表
        api = make_api([ARTICLE_LIST], start=SEARCH_LIST, current_search=KEYWORD)
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [LEFT]
        assert api._current_search == ()

    def test_plain_list_wanted_from_article_in_search(self):
        api = make_api([SEARCH_LIST, ARTICLE_LIST], start=POST, current_search=KEYWORD)
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [LEFT, LEFT]

    def test_other_search_goes_back_and_searches_again(self):
        api = make_api([ARTICLE_LIST, SEARCH_LIST], start=SEARCH_LIST, current_search=KEYWORD)
        _api_util.goto_board(api, 'give', search_list=AUTHOR)
        assert api.connect_core.keys == [LEFT, AUTHOR_CMD]
        assert api._current_search == tuple(AUTHOR)

    def test_search_from_plain_list(self):
        api = make_api([SEARCH_LIST], start=ARTICLE_LIST)
        _api_util.goto_board(api, 'give', search_list=KEYWORD + AUTHOR)
        assert api.connect_core.keys == [KEYWORD_CMD + AUTHOR_CMD]
        assert api._current_search == tuple(KEYWORD + AUTHOR)

    def test_full_path_then_search(self):
        api = make_api([ARTICLE_LIST, SEARCH_LIST], start=OTHER_LIST, current_board='test')
        _api_util.goto_board(api, 'give', search_list=KEYWORD)
        assert api.connect_core.keys == [FULL_PATH, KEYWORD_CMD]
        assert (api._current_board, api._current_search) == ('give', tuple(KEYWORD))

    def test_no_result_dismisses_and_stays_in_board(self):
        api = make_api([NO_RESULT, ARTICLE_LIST], start=ARTICLE_LIST)
        with pytest.raises(PyPtt.exceptions.NoSearchResult):
            _api_util.goto_board(api, 'give', search_list=KEYWORD)
        assert api.connect_core.keys == [KEYWORD_CMD, ' ']
        assert (api._current_board, api._current_search) == ('give', ())

    def test_unknown_screen_after_search_is_no_such_board(self):
        api = make_api(['garbage'], start=ARTICLE_LIST)
        with pytest.raises(PyPtt.exceptions.NoSuchBoard):
            _api_util.goto_board(api, 'give', search_list=KEYWORD)
        assert api._current_board is None

    def test_no_result_then_unknown_screen_forgets_board(self):
        api = make_api([NO_RESULT, 'garbage'], start=ARTICLE_LIST)
        with pytest.raises(PyPtt.exceptions.NoSearchResult):
            _api_util.goto_board(api, 'give', search_list=KEYWORD)
        assert api._current_board is None

    def test_search_list_without_record_is_not_reused(self):
        # 畫面在搜尋結果，但記錄的條件不同 (或沒有記錄)：退回一般列表重搜
        api = make_api([ARTICLE_LIST, SEARCH_LIST], start=SEARCH_LIST, current_search=())
        _api_util.goto_board(api, 'give', search_list=KEYWORD)
        assert api.connect_core.keys == [LEFT, KEYWORD_CMD]

    def test_search_list_of_other_board(self):
        other = SEARCH_LIST.replace('系列《give》', '系列《Test》')
        api = make_api([ARTICLE_LIST], start=other, current_search=KEYWORD)
        _api_util.goto_board(api, 'give', search_list=None)
        assert api.connect_core.keys == [FULL_PATH]


class TestCrowdedHeader:
    # 板主名單長又有「你有新信件」時，PTT 整段省略標頭的「看板《X》」/「系列《X》」(PTT1 實測 Japan_Travel)
    CROWDED = '【板主:modone01/modtwo002/modthree1/mod04】    你有新信件                      '
    PLAIN = ARTICLE_LIST.replace(ARTICLE_LIST.split('\n', 1)[0], CROWDED)
    SEARCH = SEARCH_LIST.replace(SEARCH_LIST.split('\n', 1)[0], CROWDED)
    NO_RESULT = NO_RESULT.replace(NO_RESULT.split('\n', 1)[0], CROWDED)

    def test_search_result_recognized_by_footer(self):
        api = make_api([self.PLAIN, self.SEARCH], start=self.PLAIN, current_board=None)
        _api_util.goto_board(api, 'give', search_list=KEYWORD)
        assert api.connect_core.keys == [FULL_PATH, KEYWORD_CMD]
        assert (api._current_board, api._current_search) == ('give', tuple(KEYWORD))

    def test_no_result_stays_in_board(self):
        api = make_api([self.PLAIN, self.NO_RESULT, self.PLAIN], start=self.PLAIN, current_board=None)
        with pytest.raises(PyPtt.exceptions.NoSearchResult):
            _api_util.goto_board(api, 'give', search_list=KEYWORD)
        assert (api._current_board, api._current_search) == ('give', ())

    def test_same_board_shortcut_needs_board_name(self):
        # 看不到看板名稱就確認不了還在同一個看板，照完整路徑
        api = make_api([self.PLAIN], start=self.PLAIN)
        _api_util.goto_board(api, 'give')
        assert api.connect_core.keys == [FULL_PATH]

    def test_kind_without_name(self):
        api = make_api([], start=self.PLAIN)
        assert _api_util.board_list_kind(api, self.PLAIN, 'give') is None
        assert _api_util.board_list_kind(api, self.PLAIN, 'give', require_name=False) == 'plain'
        assert _api_util.board_list_kind(api, self.SEARCH, 'give', require_name=False) == 'search'


def test_forget_current_board():
    api = make_api([], start=ARTICLE_LIST, current_search=KEYWORD)
    _api_util.forget_current_board(api)
    assert api._current_board is None
    assert api._current_search == ()
