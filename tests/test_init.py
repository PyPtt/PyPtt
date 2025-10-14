from unittest.mock import MagicMock

import pytest

import PyPtt


def test_default_initialization():
    """Tests default initialization of PyPtt.API."""
    api = PyPtt.API()
    assert api is not None


def test_language_initialization():
    """Tests PyPtt.API initialization with different languages."""
    api_mandarin = PyPtt.API(language=PyPtt.Language.MANDARIN)
    assert api_mandarin is not None

    api_english = PyPtt.API(language=PyPtt.Language.ENGLISH)
    assert api_english is not None


def test_log_level_initialization():
    """Tests PyPtt.API initialization with different log levels."""
    api_debug = PyPtt.API(log_level=PyPtt.LogLevel.DEBUG)
    assert api_debug is not None

    api_info = PyPtt.API(log_level=PyPtt.LogLevel.INFO)
    assert api_info is not None

    api_silent = PyPtt.API(log_level=PyPtt.LogLevel.SILENT)
    assert api_silent is not None


def test_host_initialization():
    """Tests PyPtt.API initialization with different hosts."""
    ptt_bot_ptt1 = PyPtt.API(host=PyPtt.HOST.PTT1)
    assert ptt_bot_ptt1.host == PyPtt.HOST.PTT1

    ptt_bot_ptt2 = PyPtt.API(host=PyPtt.HOST.PTT2)
    assert ptt_bot_ptt2.host == PyPtt.HOST.PTT2


def test_invalid_host_and_connect_mode():
    """Tests that PyPtt.API raises ParameterError for invalid host/connect_mode combinations."""
    with pytest.raises(PyPtt.ParameterError):
        PyPtt.API(host=PyPtt.HOST.PTT1, connect_mode=PyPtt.ConnectMode.TELNET)

    with pytest.raises(PyPtt.ParameterError):
        PyPtt.API(host=PyPtt.HOST.PTT2, connect_mode=PyPtt.ConnectMode.TELNET)


def test_invalid_language_type():
    """Tests that PyPtt.API raises TypeError for invalid language types."""
    with pytest.raises(TypeError):
        PyPtt.API(language=99)

    with pytest.raises(TypeError):
        PyPtt.API(language='PyPtt.i18n.language.ENGLISH')


def test_timeout_initialization():
    """Tests PyPtt.API initialization with custom timeouts."""
    api = PyPtt.API(
        screen_timeout=5.0,
        screen_long_timeout=15.0,
        screen_post_timeout=90.0
    )
    assert api.config.screen_timeout == 5.0
    assert api.config.screen_long_timeout == 15.0
    assert api.config.screen_post_timeout == 90.0


def test_invalid_timeout_type():
    """Tests that PyPtt.API raises TypeError for invalid timeout types."""
    with pytest.raises(TypeError):
        PyPtt.API(screen_timeout='invalid')
    with pytest.raises(TypeError):
        PyPtt.API(screen_long_timeout='invalid')
    with pytest.raises(TypeError):
        PyPtt.API(screen_post_timeout='invalid')


def test_port_initialization():
    """Tests PyPtt.API initialization with a custom port."""
    api = PyPtt.API(port=443, host='localhost')
    assert api.config.port == 443


def test_invalid_port_value():
    """Tests that PyPtt.API raises an error for invalid port values."""
    with pytest.raises(TypeError):
        PyPtt.API(port='23')
    with pytest.raises(PyPtt.ParameterError):
        PyPtt.API(port=0)
    with pytest.raises(PyPtt.ParameterError):
        PyPtt.API(port=65535)


def test_connect_mode_initialization():
    """Tests PyPtt.API initialization with a valid connect mode."""
    api = PyPtt.API(connect_mode=PyPtt.ConnectMode.WEBSOCKETS)
    assert api.config.connect_mode == PyPtt.ConnectMode.WEBSOCKETS


def test_check_update_true(monkeypatch):
    """Tests check_update=True calls sync_version."""
    mock_sync_version = MagicMock(return_value=(PyPtt.data_type.Compare.SAME, '1.0.0'))
    monkeypatch.setattr('PyPtt.lib_util.sync_version', mock_sync_version)
    PyPtt.API(check_update=True)
    mock_sync_version.assert_called_once()


def test_check_update_false(monkeypatch):
    """Tests check_update=False does not call sync_version."""
    mock_sync_version = MagicMock()
    monkeypatch.setattr('PyPtt.lib_util.sync_version', mock_sync_version)
    PyPtt.API(check_update=False)
    mock_sync_version.assert_not_called()


def test_logger_callback_initialization():
    """Tests PyPtt.API initialization with a logger_callback."""
    def my_logger(message):
        pass
    api = PyPtt.API(logger_callback=my_logger)
    assert api is not None


def test_invalid_log_level_type():
    """Tests that PyPtt.API raises TypeError for invalid log_level type."""
    with pytest.raises(TypeError):
        PyPtt.API(log_level='DEBUG')
