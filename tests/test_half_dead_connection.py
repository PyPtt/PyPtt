"""No-network regression tests for the half-dead-connection misreport.

When a send() times out having received zero bytes, connect_core records
`last_timeout_was_silent = True` and returns -1 (see
tests/test_connect_core_timeout.py). Callers that used to turn any -1 /
unparsable screen straight into a semantic "not found" exception then blamed
the board instead of the connection: `get_post`, `get_board_info` and
`get_newest_index` all reported NoSuchBoard on a connection that had simply
stopped talking.

These tests pin the fixed behaviour: on a silent timeout the caller raises
ConnectionClosed, and on a timeout that *did* receive bytes (a genuinely
missing board) it still raises NoSuchBoard.

The flag is reset at the top of every send(), so it only describes the most
recent one. Each test therefore scripts the exact send sequence the code
under test performs, mirroring that reset.
"""

import threading

import pytest

from PyPtt import _api_get_board_info
from PyPtt import _api_get_newest_index
from PyPtt import _api_get_post_index
from PyPtt import config
from PyPtt import data_type
from PyPtt import exceptions
from PyPtt import log

BOARD = 'Test'

# A board screen whose header line satisfies get_board_info's '作  者' /
# '日 期' scan, so parsing gets past the first NoSuchBoard site.
BOARD_SCREEN = '\n'.join([
    '  【 看板 】',
    '',
    '  編號     日 期  作  者        文 章 標 題      線上人數: 42',
    '   1     7/25  someone       [公告] hello',
])

# 看板設定 screen produced by the 'i' command.
BOARD_INFO_SCREEN = '\n'.join([
    f'《{BOARD}》看板設定',
    '中文敘述: 測試',
    '板主名單: (無)',
])


class FakeConnectCore:
    """Stands in for connect_core.API for the flag-check paths only.

    send() reproduces the two behaviours the callers depend on: it resets
    last_timeout_was_silent first (connect_core.py:448), then returns the
    next scripted (index, silent) pair. Once the script runs out it keeps
    returning a silent timeout, which is what a truly dead connection does.
    """

    def __init__(self, script, screens=('',)):
        self._script = list(script)
        self._screens = list(screens)
        self.last_timeout_was_silent = False
        self.sent = []

    def send(self, msg, target_list, **kwargs):
        self.sent.append(msg)
        # Real send() clears the flag before doing anything else.
        self.last_timeout_was_silent = False
        index, silent = self._script.pop(0) if self._script else (-1, True)
        self.last_timeout_was_silent = silent
        return index

    def get_screen_queue(self):
        return [self._screens[min(len(self.sent), len(self._screens)) - 1]]


class FakeApi:
    def __init__(self, connect_core_, board=BOARD):
        self.config = config.Config()
        self.connect_core = connect_core_
        self.cursor = data_type.Cursor.NEW
        self._is_login = True
        self._thread_id = threading.get_ident()
        self._goto_board_list = set()
        self._newest_index_data = {}
        # Pre-seeded so check_board() short-circuits instead of recursing
        # into get_board_info().
        self._exist_board_list = {board.lower()}
        self._board_info_list = {board.lower(): {}}


@pytest.fixture(autouse=True)
def quiet_logger():
    """get_board_info calls log.init() itself, clobbering the module-global
    logger. Save and restore it so this file can't perturb other tests."""
    original = log.logger
    log.init(log.SILENT)
    yield
    log.logger = original


# --- get_newest_index -------------------------------------------------


def _newest_index(script):
    api = FakeApi(FakeConnectCore(script, screens=(BOARD_SCREEN,)))
    return _api_get_newest_index.get_newest_index(
        api, data_type.NewIndex.BOARD, BOARD)


def test_newest_index_silent_timeout_raises_connection_closed():
    """goto_board's send succeeds, the '$' send goes fully silent."""
    with pytest.raises(exceptions.ConnectionClosed):
        _newest_index([(2, False), (-1, True)])


def test_newest_index_noisy_timeout_still_raises_no_such_board():
    """Bytes arrived but nothing matched: a real missing board."""
    with pytest.raises(exceptions.NoSuchBoard):
        _newest_index([(2, False), (-1, False)])


def test_newest_index_search_round_silent_timeout_raises_connection_closed():
    """The second (search) send at _api_get_newest_index.py:128 has its own
    flag check; the goto_board and first '$' sends must not mask it."""
    api = FakeApi(FakeConnectCore([(2, False), (2, False), (-1, True)],
                                  screens=(BOARD_SCREEN,)))
    with pytest.raises(exceptions.ConnectionClosed):
        _api_get_newest_index.get_newest_index(
            api, data_type.NewIndex.BOARD, BOARD,
            search_type=data_type.SearchType.KEYWORD, search_condition='x')


def test_newest_index_search_round_noisy_timeout_raises_no_such_board():
    api = FakeApi(FakeConnectCore([(2, False), (2, False), (-1, False)],
                                  screens=(BOARD_SCREEN,)))
    with pytest.raises(exceptions.NoSuchBoard):
        _api_get_newest_index.get_newest_index(
            api, data_type.NewIndex.BOARD, BOARD,
            search_type=data_type.SearchType.KEYWORD, search_condition='x')


# --- get_post_index ---------------------------------------------------


def _post_index(script):
    api = FakeApi(FakeConnectCore(script, screens=(BOARD_SCREEN,)))
    return _api_get_post_index.get_post_index(api, BOARD, '#1AbCdEfG')


def test_post_index_silent_timeout_raises_connection_closed():
    with pytest.raises(exceptions.ConnectionClosed):
        _post_index([(2, False), (-1, True)])


def test_post_index_noisy_timeout_still_raises_no_such_board():
    with pytest.raises(exceptions.NoSuchBoard):
        _post_index([(2, False), (-1, False)])


# --- get_board_info ---------------------------------------------------


def _board_info(script, screens):
    api = FakeApi(FakeConnectCore(script, screens=screens))
    return _api_get_board_info.get_board_info(
        api, BOARD, get_post_kind=False, call_by_others=False)


def test_board_info_silent_goto_board_raises_connection_closed():
    """goto_board() swallows its own -1, so the first thing that notices is
    the '作  者'/'日 期' scan failing on the stale screen
    (_api_get_board_info.py:43). The flag is still valid there: nothing
    sends between goto_board and the scan."""
    with pytest.raises(exceptions.ConnectionClosed):
        _board_info([(-1, True)], screens=('a stale unrelated screen',))


def test_board_info_noisy_goto_board_still_raises_no_such_board():
    with pytest.raises(exceptions.NoSuchBoard):
        _board_info([(-1, False)], screens=('a stale unrelated screen',))


def test_board_info_silent_timeout_on_missing_online_user_count():
    """Header line present but with no digits to parse
    (_api_get_board_info.py:53)."""
    screen = '  編號     日 期  作  者        文 章 標 題'
    with pytest.raises(exceptions.ConnectionClosed):
        _board_info([(-1, True)], screens=(screen,))


def test_board_info_noisy_timeout_on_missing_online_user_count():
    screen = '  編號     日 期  作  者        文 章 標 題'
    with pytest.raises(exceptions.NoSuchBoard):
        _board_info([(-1, False)], screens=(screen,))


def test_board_info_silent_i_command_raises_connection_closed():
    """goto_board succeeded; the 'i' send went silent, so the 看板設定 screen
    never arrived and boardname stays None (_api_get_board_info.py:80)."""
    with pytest.raises(exceptions.ConnectionClosed):
        _board_info([(0, False), (-1, True)],
                    screens=(BOARD_SCREEN, BOARD_SCREEN))


def test_board_info_noisy_i_command_still_raises_no_such_board():
    with pytest.raises(exceptions.NoSuchBoard):
        _board_info([(0, False), (-1, False)],
                    screens=(BOARD_SCREEN, BOARD_SCREEN))


def test_board_info_silent_timeout_on_board_name_mismatch():
    """A stale 看板設定 screen for some *other* board
    (_api_get_board_info.py:86)."""
    other = '《SomeOtherBoard》看板設定'
    with pytest.raises(exceptions.ConnectionClosed):
        _board_info([(0, False), (-1, True)], screens=(BOARD_SCREEN, other))


def test_board_info_noisy_timeout_on_board_name_mismatch():
    other = '《SomeOtherBoard》看板設定'
    with pytest.raises(exceptions.NoSuchBoard):
        _board_info([(0, False), (-1, False)], screens=(BOARD_SCREEN, other))


def test_board_info_happy_path_unaffected():
    """A fully successful run must not be turned into ConnectionClosed by
    the added checks."""
    board_info = _board_info([(0, False), (0, False)],
                             screens=(BOARD_SCREEN, BOARD_INFO_SCREEN))
    assert board_info[data_type.BoardField.board] == BOARD
    # 42 online minus ourselves
    assert board_info[data_type.BoardField.online_user] == 41
