"""No-network tests for the PTT1 2026-11「移除文章」flow a moderator gets when
deleting someone else's post.

Before this flow existed, `d` went straight to "請確定刪除(Y/N)". Now it opens a
reason menu, asks whether to bad-post the article (only for posts younger than
a week), shows a confirmation screen that previews the public board-management
log entry, and only then removes the post. PyPtt didn't recognise any of these
screens and reported NoPermission.

A fake connect_core replays screens captured live on PTT1 (ids replaced) and
runs the same "first matching TargetUnit wins, send its response, repeat until
a break target" loop as connect_core.send, recording every key PyPtt sends.
"""
from types import SimpleNamespace

import pytest

import PyPtt
from PyPtt import _api_del_post
from PyPtt import _api_util
from PyPtt import command
from PyPtt import data_type

ENTER = command.enter

ARTICLE_LIST = '''【板主:somebm】           [贈送] 歡迎來到贈送板                 看板《give》
[→]閱讀 [z]精華區 [Tab]文摘 [s]選擇看板 [b]進板 [i]看板設定 [^X]轉錄 [/]搜尋
   編號    日 期 作  者       文  章  標  題                            人氣:24
> 80015    11/23 someone      □ [贈送] 全國 機車手機支架
 文章列表  (^P)發表 (y)回應 (X)推文 (d)刪除 (→)閱讀 (b)進板  (←)離開 (h)說明 '''

_HEADER = ''' 移除文章  give
  80015 11/23 someone      [贈送] 全國 機車手機支架'''

_MENU_ROWS = '''請選取理由：(在選項上按e可修改預設值, 也可按o輸入一次性理由)
> 1. 廣告
  2. 不當用辭
  3. 人身攻擊
  4. 違反板規
  5. 清理看板
  6. (空)
  7. (空)
  8. (空)
  9. (空)
此理由會與執行者的資訊一起被記入下列紀錄：
- 在看板管理紀錄(自動公告，可編輯)您的身份會顯示為[板主]
- 看板管理稽核紀錄(管理者才可看，不可編輯)另記錄執行者[somebm]與來源IP'''
_MENU_FOOTER = ' 選擇理由  (Enter)確定 (e)編輯並儲存 (o)其他(不儲存) (1-9)選擇 (q)取消 (h)說明'

REASON_MENU = f'{_HEADER}\n{_MENU_ROWS}\n{_MENU_FOOTER}'
REASON_INPUT = f'{_HEADER}\n{_MENU_ROWS}\n請輸入理由(空白返回):\n{_MENU_FOOTER}'


def _bad_prompt(reason):
    return f'{_HEADER}\n理由: {reason}\n同時惡退此文?(y/N/q取消)[N]'


def _confirm(reason, bad_setting):
    action = '退回文章' if bad_setting == '惡退' else '移除文章'
    return f'''{_HEADER}
理由: {reason}
退文設定: {bad_setting}
預計記入看板管理紀錄(自動公告)：
11/23/2026 20:14 板主 {action}: {reason}
  文章: 11/23 someone [贈送] 全國 機車手機支架
預計記入看板管理稽核紀錄(相同內容省略)：
  執行: somebm (127.0.0.1)
移除後，原文會寄到作者的信箱。
預計移除後的標題：
  (本文已被移除) <someone>: {reason}
請確定移除(Y/N/R修改標題)?[N]'''


REMOVED = f'''{_HEADER}
已移除文章。
原文已寄到作者的信箱。
 ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ 請按任意鍵繼續 ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄'''

IN_DIGEST = ARTICLE_LIST.rsplit('\n', 1)[0] + \
    '\n ◆ 文章被收入文摘(g)，請先解除                                 [按任意鍵繼續] '


class LoopCore:
    """Replays one scripted screen per round trip, like connect_core.send:
    on each screen the first matching TargetUnit wins; a break target returns
    its index, otherwise its response is "sent" (recorded) and the next screen
    is shown. break_detect_after_send returns right after sending."""

    def __init__(self, screen_list):
        self.screen_list = list(screen_list)
        self.queue = [ARTICLE_LIST]
        self.keys = []

    def get_screen_queue(self):
        return self.queue

    def send(self, msg, target_list, screen_timeout=0, refresh=True, secret=False):
        self.keys.append(msg)
        while self.screen_list:
            screen = self.screen_list.pop(0)
            self.queue.append(screen)
            for index, target in enumerate(target_list):
                if not target.is_match(screen, '>'):
                    continue
                if target._Handler is not None:
                    target._Handler(screen)
                if target.is_break():
                    return index
                self.keys.append(target.get_response(screen))
                if target.is_break_after_send():
                    return -1
                break
            else:
                return -1
        return -1


@pytest.fixture
def make_api(monkeypatch):
    for name in ('one_thread', 'goto_board'):
        monkeypatch.setattr(_api_util, name, lambda *args, **kwargs: None)
    monkeypatch.setattr(_api_util, 'check_board',
                        lambda *args, **kwargs: {data_type.BoardField.moderators: ['somebm']})

    def _make(screen_list):
        post_info = {
            data_type.PostField.post_status: data_type.PostStatus.EXISTS,
            data_type.PostField.author: 'someone',
        }
        return SimpleNamespace(
            connect_core=LoopCore(screen_list),
            ptt_id='somebm',
            _is_login=True,
            is_registered_user=True,
            get_post=lambda *args, **kwargs: post_info,
        )

    return _make


def _flow_keys(api):
    # keys[0] is "#AID Enter d"; the rest are the responses PyPtt chose
    return api.connect_core.keys[1:]


class TestRemoveFlow:
    def test_default_reason_is_typed_not_picked_from_menu(self, make_api):
        """Without reason/bad_post_type the one-time reason 違反板規 is typed via (o).
        The menu cursor sits on「1. 廣告」, so a bare Enter would log the removal as 廣告."""
        api = make_api([REASON_MENU, REASON_INPUT, _bad_prompt('違反板規'), _confirm('違反板規', '一般刪文，非退文'),
                        REMOVED, ARTICLE_LIST])
        _api_del_post.del_post(api, 'give', post_aid='1AbCdEfG')
        assert _flow_keys(api) == ['o', '違反板規' + ENTER, 'n' + ENTER, 'y' + ENTER, ' ']
        assert ENTER not in _flow_keys(api)[:1]

    def test_reason_is_used(self, make_api):
        api = make_api([REASON_MENU, REASON_INPUT, _bad_prompt('板規7'), _confirm('板規7', '一般刪文，非退文'),
                        REMOVED, ARTICLE_LIST])
        _api_del_post.del_post(api, 'give', post_aid='1AbCdEfG', reason='板規7')
        assert _flow_keys(api) == ['o', '板規7' + ENTER, 'n' + ENTER, 'y' + ENTER, ' ']

    def test_bad_post_other_uses_bad_post_reason(self, make_api):
        api = make_api([REASON_MENU, REASON_INPUT, _bad_prompt('收錢不寄'), _confirm('收錢不寄', '惡退'),
                        REMOVED, ARTICLE_LIST])
        _api_del_post.del_post(api, 'give', post_aid='1AbCdEfG',
                               bad_post_type=PyPtt.BadPostType.OTHER, bad_post_reason='收錢不寄')
        assert _flow_keys(api) == ['o', '收錢不寄' + ENTER, 'y' + ENTER, 'y' + ENTER, ' ']
        assert api.bad_post_done

    def test_bad_post_type_becomes_reason_text(self, make_api):
        api = make_api([REASON_MENU, REASON_INPUT, _bad_prompt('廣告'), _confirm('廣告', '惡退'),
                        REMOVED, ARTICLE_LIST])
        _api_del_post.del_post(api, 'give', post_aid='1AbCdEfG', bad_post_type=PyPtt.BadPostType.AD)
        assert _flow_keys(api)[:3] == ['o', '廣告' + ENTER, 'y' + ENTER]

    def test_post_older_than_a_week_skips_bad_post(self, make_api):
        """PTT doesn't ask「同時惡退此文」for posts older than a week; the delete still
        happens, and a requested bad-post is reported as not recorded."""
        api = make_api([REASON_MENU, REASON_INPUT, _confirm('廣告', '文章超過一週 (跳過)'), REMOVED, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.BadPostNotRecorded):
            _api_del_post.del_post(api, 'give', post_aid='1AbCdEfG', bad_post_type=PyPtt.BadPostType.AD)
        assert _flow_keys(api) == ['o', '廣告' + ENTER, 'y' + ENTER, ' ']

    def test_post_older_than_a_week_without_bad_post(self, make_api):
        api = make_api([REASON_MENU, REASON_INPUT, _confirm('違反板規', '文章超過一週 (跳過)'), REMOVED, ARTICLE_LIST])
        _api_del_post.del_post(api, 'give', post_aid='1AbCdEfG')
        assert _flow_keys(api) == ['o', '違反板規' + ENTER, 'y' + ENTER, ' ']

    def test_post_in_digest_raises_without_deleting(self, make_api):
        api = make_api([IN_DIGEST, ARTICLE_LIST])
        with pytest.raises(PyPtt.exceptions.PostInDigest):
            _api_del_post.del_post(api, 'give', post_aid='1AbCdEfG')
        # only the popup is dismissed; nothing that could answer a later prompt
        assert _flow_keys(api) == [' ']


class TestNewFlowReason:
    @pytest.mark.parametrize('reason, bad_post_type, bad_post_reason, expected', [
        (None, None, None, '違反板規'),
        ('板規7', None, None, '板規7'),
        ('板規7', PyPtt.BadPostType.AD, None, '板規7'),
        (None, PyPtt.BadPostType.AD, None, '廣告'),
        (None, PyPtt.BadPostType.BAD_LANGUAGE, None, '不當用辭'),
        (None, PyPtt.BadPostType.PERSONAL_ATTACK, None, '人身攻擊'),
        (None, PyPtt.BadPostType.OTHER, '收錢不寄', '收錢不寄'),
    ])
    def test_mapping(self, reason, bad_post_type, bad_post_reason, expected):
        assert _api_del_post._new_flow_reason(reason, bad_post_type, bad_post_reason) == expected
