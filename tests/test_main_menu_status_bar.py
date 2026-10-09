import pytest

from PyPtt import screens
from PyPtt._api_get_time import _find_time

NEW = '主選單   世界郵政日   10/9 週五 15:04 | janice001 | 線上24305人       (h)說明'
OLD = '[5/23 星期六 16:40] [ 射手時 ]  線上27866人, 我是CodingMan   [呼叫器]打開'
SHORT = '8/19週三22:35   [ 七夕 ]   線上30721人,我是DeepLearning 呼叫器關閉  (h)說明'


@pytest.mark.parametrize('bar, expected', [(NEW, '15:04'), (OLD, '16:40'), (SHORT, '22:35')])
def test_status_bar(bar, expected):
    screen = f'  (G)離開，再見\n\n{bar}'
    assert all(t in screen for t in screens.Target.MainMenu)
    assert _find_time(screen.split('\n')[-3:]) == expected


def test_find_time_none():
    assert _find_time(['沒有狀態列']) is None


def test_cursor_to_goodbye_matches_main_menu():
    # login 會在 CursorToGoodbye 尾端追加游標項目, 只比對 MainMenu 的前綴
    assert screens.Target.CursorToGoodbye[:len(screens.Target.MainMenu)] == screens.Target.MainMenu
