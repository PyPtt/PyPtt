"""PTT 主選單狀態列有長短兩種寫法, 兩種都必須認得。

長: [5/23 星期六 16:40] [ 射手時 ]    線上27866人, 我是CodingMan      [呼叫器]打開
短: 8/19週三22:35   [ 七夕 ]    線上30721人,我是DeepLearning 呼叫器關閉     (h)說明

短的那種把逗號後的空格與呼叫器的中括號都吃掉了, 日期也從 '星期六' 縮成 '週三'。
"""
import re

from PyPtt import data_type
from PyPtt._api_call_status import _call_status_map, _call_status_pattern
from PyPtt._api_get_time import pattern as time_pattern
from PyPtt.screens import Target

LONG = '[5/23 星期六 16:40] [ 射手時 ]    線上27866人, 我是CodingMan      [呼叫器]打開 '
SHORT = '8/19週三22:35   [ 七夕 ]    線上30721人,我是DeepLearning 呼叫器關閉     (h)說明'

MENU_BODY = '                      (G)oodbye         離開，再見…'


def test_main_menu_markers_match_both_status_lines():
    for status in (LONG, SHORT):
        screen = MENU_BODY + '\n' + status
        assert all(t in screen for t in Target.MainMenu), status


def test_get_time_line_filter_and_pattern():
    for status, expected in ((LONG, '16:40'), (SHORT, '22:35')):
        assert '線上' in status and '我是' in status
        assert time_pattern.search(status).group(0) == expected


def test_call_status_pattern():
    assert _call_status_map[_call_status_pattern.search(LONG).group(1)] == data_type.CallStatus.ON
    assert _call_status_map[_call_status_pattern.search(SHORT).group(1)] == data_type.CallStatus.OFF


def test_call_status_pattern_covers_every_state():
    for word, expected in _call_status_map.items():
        for form in (f'[呼叫器]{word}', f'呼叫器{word}'):
            assert _call_status_map[_call_status_pattern.search(form).group(1)] == expected
