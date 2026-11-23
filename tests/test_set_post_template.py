"""No-network tests for set_post_template (看板設定 →「[管理] 文章類別設定」).

Screens are captured live on PTT1 (ids replaced). The flow goes through two
pttbbs editors; inside an editor every printable key is typed into the
buffer and ← only moves the cursor, so the tests pin the exact keys on the
happy path and that a failure backs out with Ctrl-X → (A)放棄, never saving.
"""
import pytest

import PyPtt
from PyPtt import _api_set_post_template
from PyPtt import _api_util
from PyPtt import command
from PyPtt import screens
from tests.test_board_setting_flow import ARTICLE_LIST, EDIT, EDIT_CURSOR16, READONLY, FakeCore

LEFT, CTRL_P, CTRL_X, CTRL_Y, ENTER = command.left, command.ctrl_p, command.ctrl_x, command.ctrl_y, command.enter
DOWN = command.down

_EDITOR_FOOTER = ' 編輯文章  (^X)存檔 (^C)色碼         (Esc-h)按鍵 (^Z)說明║插入│aipr║  1:  1'

CATEGORY_EDITOR = '''# 每一行代表一個類別，類別最多四個字（一個中文字算2字）
# 以 # 開頭為註解，儲存檔案時會自動忽略
# 若清空內容儲存，將會刪除看版的發文類別設定
# 儲存離開後，可繼續設定各類別之範本（Template）
贈送
心得
建議
公告
~
~
''' + _EDITOR_FOOTER

SAVE_PROMPT = '''【檔案處理】
[S/V]儲存 (A)放棄 (E)繼續 (R/W/D)讀寫刪暫存檔
確定要儲存檔案嗎？'''

ASK_TEMPLATE = SAVE_PROMPT + ''' a
文章 沒有 存入
要編輯現有類別的範本嗎？(y/N)'''


def _template_list(cursor: str = '贈送', preview: str = '1.贈送前請詳看板規1-3規定(站規)，違者重罰禁言一年並退文處分…') -> str:
    rows = [('贈送', '有', preview), ('心得', '有', '◎  心得文  對贈送後心得'), ('建議', '有', '◎  建議文'),
            ('公告', '無', '')]
    lines = [' 文章類別範本設定  give', '請按 Enter 編輯範本，按 d 刪除範本，按 ←/q 結束離開。', '   類別    範本  範本內容']
    for name, has, text in rows:
        mark = '>' if name == cursor else ' '
        lines.append(f'{mark}  {name}    {has}    {text}'.rstrip())
    lines.append(' 範本設定  (Enter)編輯 (d)刪除                                      (q/←)離開')
    return '\n'.join(lines)


TEMPLATE_EDITOR = '''1.贈送前請詳看板規1-3規定(站規)，違者重罰禁言一年並退文處分。
----------------------(以上看完後 請按CTRL+y刪除 謝謝合作)--------------------
物    品：
領取地點：(全國、自取、郵局、店到店、PCHOME、蝦皮)
~
~
''' + _EDITOR_FOOTER

EMPTY_EDITOR = '\n~\n~\n~\n' + _EDITOR_FOOTER

NEW_TEMPLATE = '★ 新範本第一行\n物    品：\n  （縮排保留）\n'
NEW_TEMPLATE_TYPED = '★ 新範本第一行\r\n物    品：\r\n  （縮排保留）\r\n'


@pytest.fixture
def make_api(monkeypatch):
    for name in ('one_thread', 'goto_board', 'check_board'):
        monkeypatch.setattr(_api_util, name, lambda *args, **kwargs: None)

    from types import SimpleNamespace

    def _make(screen_list):
        return SimpleNamespace(
            connect_core=FakeCore(screen_list, ARTICLE_LIST),
            config=SimpleNamespace(screen_timeout=3.0, screen_long_timeout=10.0),
            _is_login=True,
            is_registered_user=True,
            cursor='>',
            _goto_board_list=set(),
        )

    return _make


def _happy_screens(list_before=None):
    return [READONLY, EDIT, CATEGORY_EDITOR, SAVE_PROMPT, ASK_TEMPLATE, list_before or _template_list(),
            TEMPLATE_EDITOR, EMPTY_EDITOR, SAVE_PROMPT, _template_list(preview='★ 新範本第一行'),
            EDIT_CURSOR16, ARTICLE_LIST]


class TestSetPostTemplate:
    def test_happy_path(self, make_api):
        api = make_api(_happy_screens())
        _api_set_post_template.set_post_template(api, 'give', '贈送', NEW_TEMPLATE)
        assert api.connect_core.keys == [
            'i', CTRL_P, 'c', CTRL_X, 'a' + ENTER, 'y' + ENTER,
            ENTER, CTRL_Y * 50, NEW_TEMPLATE_TYPED + CTRL_X, 's' + ENTER, 'q', LEFT]

    def test_category_list_is_never_saved(self, make_api):
        """The first editor holds the category list; only (A)放棄 may answer its save prompt."""
        api = make_api(_happy_screens())
        _api_set_post_template.set_post_template(api, 'give', '贈送', NEW_TEMPLATE)
        keys = api.connect_core.keys
        assert keys[keys.index('c') + 2] == 'a' + ENTER

    def test_moves_cursor_to_post_type(self, make_api):
        screens_ = _happy_screens()
        screens_.insert(6, _template_list(cursor='建議'))
        api = make_api(screens_)
        _api_set_post_template.set_post_template(api, 'give', '建議', NEW_TEMPLATE)
        keys = api.connect_core.keys
        assert keys[6] == DOWN * 2
        assert keys[7] == ENTER

    def test_clears_until_editor_is_empty(self, make_api):
        screens_ = _happy_screens()
        screens_.insert(7, TEMPLATE_EDITOR)  # first Ctrl-Y batch didn't empty it
        api = make_api(screens_)
        _api_set_post_template.set_post_template(api, 'give', '贈送', NEW_TEMPLATE)
        assert api.connect_core.keys[7:9] == [CTRL_Y * 50, CTRL_Y * 50]

    def test_unknown_post_type_backs_out_without_editing(self, make_api):
        api = make_api([READONLY, EDIT, CATEGORY_EDITOR, SAVE_PROMPT, ASK_TEMPLATE, _template_list(),
                        EDIT_CURSOR16, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_set_post_template.set_post_template(api, 'give', '問卦', NEW_TEMPLATE)
        assert api.connect_core.keys[6:] == [LEFT, LEFT]

    def test_unknown_screen_after_save_abandons(self, make_api):
        """If the save doesn't land on the template list, PyPtt backs out of the
        editor with Ctrl-X → (A)放棄 and never answers 's' again."""
        api = make_api([READONLY, EDIT, CATEGORY_EDITOR, SAVE_PROMPT, ASK_TEMPLATE, _template_list(),
                        TEMPLATE_EDITOR, EMPTY_EDITOR, SAVE_PROMPT, EMPTY_EDITOR,
                        SAVE_PROMPT, _template_list(), EDIT_CURSOR16, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.UnknownError):
            _api_set_post_template.set_post_template(api, 'give', '贈送', NEW_TEMPLATE)
        backout = api.connect_core.keys[10:]
        assert backout == [CTRL_X, 'a' + ENTER, LEFT, LEFT]
        assert 's' + ENTER not in backout

    def test_template_not_saved_raises(self, make_api):
        not_saved = _template_list().replace('>  贈送    有', '>  贈送    無')
        api = make_api(_happy_screens()[:9] + [not_saved, EDIT_CURSOR16, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.UnknownError):
            _api_set_post_template.set_post_template(api, 'give', '贈送', NEW_TEMPLATE)

    @pytest.mark.parametrize('content', ['bad\x1bcolour', 'bell\x07', 'emoji \U0001F600'])
    def test_bad_content_rejected_before_any_key(self, make_api, content):
        api = make_api([])
        with pytest.raises(PyPtt.exceptions.ParameterError):
            _api_set_post_template.set_post_template(api, 'give', '贈送', content)
        assert api.connect_core.keys == []


class TestExitKeys:
    @pytest.mark.parametrize('screen, key', [
        (TEMPLATE_EDITOR, CTRL_X),
        (SAVE_PROMPT, 'a' + ENTER),
        (ASK_TEMPLATE, ENTER),
        (_template_list(), LEFT),
    ])
    def test_exit_key(self, screen, key):
        assert screens.board_setting_exit_key(screen) == key
        assert screens.in_board_setting(screen)

    def test_editor_is_not_article_list(self):
        editor_with_list_words = '[i]看板設定 文章列表 (b)進板\n~\n' + _EDITOR_FOOTER
        assert screens.in_board_setting(editor_with_list_words)
