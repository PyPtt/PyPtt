"""Unit tests for login() -> TwoFactorAuthRequired -> submit_otp().

No network: connect_core is replaced by a fake whose send() runs the real
TargetUnit matching against scripted screens. The screen strings come from
pttbbs (daemon/logind/logind.c, mbbsd/mbbsd.c).
"""
import pytest

import PyPtt
from PyPtt import command
from PyPtt import exceptions
from PyPtt import log
from PyPtt import screens

LOGIND_PROMPT = '請輸入兩階段(2FA)驗證碼(6位限時數字 或8位救援碼):'
LOGIND_WRONG_CODE = '驗證碼錯誤！請確認後重新輸入。\n' + LOGIND_PROMPT
MBBSD_PROMPT = '此帳號需要兩階段驗證。\n請輸入兩階段(2FA)驗證碼(6位限時數字 或 8位救援碼):'
MAIN_MENU = '【主功能表】\n> (A)nnounce\n  (T)alk\n  (G)oodbye   離開，再見'


class FakeConnectCore:
    """send() walks one scripted round of screens with the real TargetUnit
    semantics: a match raises the target's exception, a break target returns
    its index, any other match moves on to the next screen. An Exception in
    the round is raised as-is."""

    def __init__(self, *rounds):
        self._rounds = list(rounds)
        self.sent = []
        self._last_screen = ''

    def connect(self):
        pass

    def send(self, msg, target_list, **kwargs):
        self.sent.append((msg, kwargs))
        for screen in (self._rounds.pop(0) if self._rounds else []):
            if isinstance(screen, Exception):
                raise screen
            self._last_screen = screen
            for index, target in enumerate(target_list):
                if target.is_match(screen, PyPtt.data_type.Cursor.NEW):
                    target.raise_exception()
                    if target.is_break():
                        return index
                    break
        return -1

    def get_screen_queue(self):
        return [self._last_screen]


@pytest.fixture(autouse=True)
def quiet_logger():
    original = log.logger
    log.init(log.SILENT)
    yield
    log.logger = original


@pytest.fixture(autouse=True)
def restore_screen_targets():
    # a successful login rewrites these module-level lists with the detected cursor
    saved = {name: list(getattr(screens.Target, name))
             for name in ('InBoardWithCursor', 'InMailBoxWithCursor', 'CursorToGoodbye')}
    yield
    for name, value in saved.items():
        setattr(screens.Target, name, value)


def login_until_otp(prompt, *rounds):
    api = PyPtt.API(log_level=log.SILENT)
    api.connect_core = FakeConnectCore(['正在檢查帳號與密碼...', prompt], *rounds)
    with pytest.raises(PyPtt.TwoFactorAuthRequired):
        api.login('pypttbot1', 'test1234')
    assert api._is_login is False
    return api


@pytest.mark.parametrize('prompt', [LOGIND_PROMPT, MBBSD_PROMPT], ids=['logind', 'mbbsd'])
def test_submit_otp_finishes_login(prompt):
    api = login_until_otp(prompt, ['密碼正確！ 開始登入系統...', MAIN_MENU])

    api.submit_otp(' 123456\n')

    assert api._is_login is True
    msg, kwargs = api.connect_core.sent[-1]
    assert msg == '123456' + command.enter
    assert kwargs['secret'] is True


def test_mbbsd_success_message_is_not_mistaken_for_prompt():
    # mbbsd prints 「2FA 兩階段驗證成功」 on success; the old '兩階段' matcher would fire on it.
    api = login_until_otp(MBBSD_PROMPT, ['2FA 兩階段驗證成功。', MAIN_MENU])

    api.submit_otp('123456')

    assert api._is_login is True


def test_wrong_code_can_retry_on_same_connection():
    api = login_until_otp(LOGIND_PROMPT, [LOGIND_WRONG_CODE], [MAIN_MENU])

    with pytest.raises(PyPtt.TwoFactorAuthRequired):
        api.submit_otp('000000')
    api.submit_otp('123456')

    assert api._is_login is True


def test_disconnect_after_too_many_failures_needs_new_login():
    # logind sends its goodbye screen and drops the connection once LOGINATTEMPTS is hit.
    api = login_until_otp(LOGIND_PROMPT, [exceptions.ConnectionClosed()])

    with pytest.raises(PyPtt.ConnectionClosed):
        api.submit_otp('000000')
    with pytest.raises(PyPtt.RequireLogin):
        api.submit_otp('123456')


def test_submit_otp_without_pending_login():
    api = PyPtt.API(log_level=log.SILENT)
    with pytest.raises(PyPtt.RequireLogin):
        api.submit_otp('123456')


def test_logind_byte_stream_matches_prompt():
    # What logind.c writes: move, clear-to-eol, ANSI reset, Big5 prompt, then
    # draw_input()'s reverse-video field padded with spaces and backspaces.
    raw = (b'\x1b[22;1H\x1b[K\x1b[m' + LOGIND_PROMPT.encode('big5')
           + b'\x1b[7m' + b' ' * 9 + b'\b' * 9)
    screen = screens.IncrementalScreen('big5uao', 24)
    screen.feed(raw)
    assert '請輸入兩階段(2FA)驗證碼' in screen.screen
