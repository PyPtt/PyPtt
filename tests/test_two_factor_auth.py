"""Unit tests for the 2FA login flow: login() -> TwoFactorAuthRequired -> submit_otp().

No network: connect_core is replaced by a fake whose send() runs the real
TargetUnit matching against scripted screens. The screen strings come from
pttbbs (daemon/logind/logind.c, mbbsd/mbbsd.c).
"""
import pytest

import PyPtt
from PyPtt import _api_loginout
from PyPtt import command
from PyPtt import exceptions
from PyPtt import log
from PyPtt import screens

# logind draws the prompt at row 22 after "正在檢查帳號與密碼..." on the same row.
LOGIND_PROMPT = '請輸入兩階段(2FA)驗證碼(6位限時數字 或8位救援碼):'
# mbbsd's checkuser_2fa() has one more space after 「或」.
MBBSD_PROMPT = '此帳號需要兩階段驗證。\n請輸入兩階段(2FA)驗證碼(6位限時數字 或 8位救援碼):'
LOGIND_WRONG_CODE = '驗證碼錯誤！請確認後重新輸入。\n' + LOGIND_PROMPT
MBBSD_WRONG_CODE = '驗證碼錯誤。請確定在時限前輸入完畢。\n' + MBBSD_PROMPT
MBBSD_TOO_MANY = '兩階段驗證失敗次數過多。\n請輸入代號，或以 guest 參觀，或以 new 註冊:'
MAIN_MENU = '【主功能表】\n> (A)nnounce\n  (T)alk\n  (G)oodbye   離開，再見'


class FakeConnectCore:
    """send() walks the scripted screens with the real TargetUnit semantics:
    a matching target raises its exception, a break target returns its index,
    any other match consumes the screen and moves on to the next one. A screen
    that is an Exception instance is raised as-is (e.g. ConnectionClosed)."""

    def __init__(self, *rounds):
        # one list of screens per send() call
        self._rounds = list(rounds)
        self.sent = []
        self.connected = 0
        self.closed = 0
        self._last_screen = ''
        self.last_timeout_was_silent = False

    def connect(self):
        self.connected += 1

    def close(self):
        self.closed += 1

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
    # _finish_login() rewrites these module-level lists with the detected cursor.
    saved = {name: list(getattr(screens.Target, name))
             for name in ('InBoardWithCursor', 'InMailBoxWithCursor', 'CursorToGoodbye')}
    yield
    for name, value in saved.items():
        setattr(screens.Target, name, value)


def make_api(*rounds):
    api = PyPtt.API(log_level=log.SILENT)
    api.connect_core = FakeConnectCore(*rounds)
    return api


def login_until_otp(prompt=LOGIND_PROMPT, *rounds):
    api = make_api(['正在檢查帳號與密碼...', prompt], *rounds)
    with pytest.raises(PyPtt.TwoFactorAuthRequired) as exc:
        api.login('pypttbot1', 'test1234')
    return api, exc.value


@pytest.mark.parametrize('prompt', [LOGIND_PROMPT, MBBSD_PROMPT], ids=['logind', 'mbbsd'])
def test_login_raises_and_keeps_connection(prompt):
    api, exc = login_until_otp(prompt)

    assert exc.reason == PyPtt.TwoFactorAuthReason.FIRST
    assert exc.ptt_id == 'pypttbot1'
    assert isinstance(exc, PyPtt.LoginError)
    assert api._pending_otp is True
    assert api._is_login is False
    assert api.connect_core.closed == 0


def test_submit_otp_success_finishes_login():
    api, _ = login_until_otp(LOGIND_PROMPT, ['密碼正確！ 開始登入系統...', MAIN_MENU])

    api.submit_otp('123456')

    assert api._is_login is True
    assert api._pending_otp is False
    msg, kwargs = api.connect_core.sent[-1]
    assert msg == '123456' + command.enter
    assert kwargs['secret'] is True
    assert kwargs['refresh'] is False


def test_submit_otp_accepts_recovery_code_and_strips_whitespace():
    api, _ = login_until_otp(LOGIND_PROMPT, [MAIN_MENU])

    api.submit_otp(' 12345678\n')

    assert api._is_login is True
    assert api.connect_core.sent[-1][0] == '12345678' + command.enter


@pytest.mark.parametrize('wrong_screen, prompt', [
    (LOGIND_WRONG_CODE, LOGIND_PROMPT),
    (MBBSD_WRONG_CODE, MBBSD_PROMPT),
], ids=['logind', 'mbbsd'])
def test_wrong_code_keeps_pending_then_retry_succeeds(wrong_screen, prompt):
    api, _ = login_until_otp(prompt, [wrong_screen], [MAIN_MENU])

    with pytest.raises(PyPtt.TwoFactorAuthRequired) as exc:
        api.submit_otp('000000')
    assert exc.value.reason == PyPtt.TwoFactorAuthReason.WRONG_CODE
    assert exc.value.ptt_id == 'pypttbot1'
    assert api._pending_otp is True
    assert api.connect_core.closed == 0

    api.submit_otp('123456')
    assert api._is_login is True
    assert api._pending_otp is False


def test_logind_disconnect_after_too_many_failures():
    # logind sends its goodbye screen and drops the connection once LOGINATTEMPTS is hit.
    api, _ = login_until_otp(LOGIND_PROMPT, [exceptions.ConnectionClosed()])

    with pytest.raises(PyPtt.TwoFactorAuthFailed):
        api.submit_otp('000000')
    assert api._pending_otp is False


def test_mbbsd_too_many_failures_closes_connection():
    api, _ = login_until_otp(MBBSD_PROMPT, [MBBSD_TOO_MANY])

    with pytest.raises(PyPtt.TwoFactorAuthFailed) as exc:
        api.submit_otp('000000')
    # TwoFactorAuthFailed must not be mistaken for "retry with another code"
    assert not isinstance(exc.value, PyPtt.TwoFactorAuthRequired)
    assert isinstance(exc.value, PyPtt.LoginError)
    assert api._pending_otp is False
    assert api.connect_core.closed == 1


def test_submit_otp_without_pending_login():
    api = make_api()
    with pytest.raises(PyPtt.RequireLogin):
        api.submit_otp('123456')


@pytest.mark.parametrize('otp', ['12345', '1234567', '123456789', 'abcdef', '12 3456', ''])
def test_submit_otp_rejects_bad_format_without_echoing_it(otp):
    api, _ = login_until_otp()
    with pytest.raises(PyPtt.ParameterError) as exc:
        api.submit_otp(otp)
    if otp.strip():
        assert otp not in str(exc.value)
    # a format error is the caller's bug, not PTT's answer: keep the connection
    assert api._pending_otp is True


def test_submit_otp_rejects_non_string_without_echoing_it():
    api, _ = login_until_otp()
    with pytest.raises(TypeError) as exc:
        api.submit_otp(123456)
    assert '123456' not in str(exc.value)


def test_login_again_abandons_pending_connection():
    api, _ = login_until_otp(LOGIND_PROMPT, ['正在檢查帳號與密碼...', LOGIND_PROMPT])

    with pytest.raises(PyPtt.TwoFactorAuthRequired):
        api.login('pypttbot1', 'test1234')
    assert api.connect_core.closed == 1
    assert api.connect_core.connected == 2
    assert api._pending_otp is True


def test_logout_drops_pending_connection():
    api, _ = login_until_otp()

    api.logout()

    assert api.connect_core.closed == 1
    assert api._pending_otp is False


def _feed(raw: bytes) -> str:
    screen = screens.IncrementalScreen('big5uao', 24)
    screen.feed(raw)
    return screen.screen


def test_logind_byte_stream_matches_prompt_and_wrong_code():
    # The bytes logind.c writes: move, clear-to-eol, ANSI reset, Big5 message,
    # then draw_input()'s reverse-video field padded with spaces and backspaces.
    reset = b'\x1b[m'
    field = b'\x1b[7m' + b' ' * 9 + b'\b' * 9
    prompt = b'\x1b[22;1H\x1b[K' + reset + LOGIND_PROMPT.encode('big5') + field
    fail = (b'\x1b[21;1H\x1b[K' + reset + b'\x1b[1;31m' + '驗證碼錯誤！請確認後重新輸入。'.encode('big5')
            + reset)

    first = _feed(b'\x1b[22;1H\x1b[K' + reset + '正在檢查帳號與密碼...'.encode('big5') + prompt)
    assert _api_loginout._otp_prompt in first

    wrong = _feed(b'123456' + fail + prompt)
    assert _api_loginout._otp_wrong_code in wrong
    assert _api_loginout._otp_prompt in wrong
