"""
This file contains tests for the utility functions in PyPtt.lib_util.
"""
import pytest
from unittest.mock import MagicMock
import requests

from PyPtt import lib_util, exceptions, data_type


@pytest.mark.parametrize("path, expected", [
    ("/path/to/file.txt", "file"),
    ("another_file.py", "another_file"),
    ("no_extension", "no_extension"),
    ("/path/with.dots/file.name.ext", "file.name"),
    ("", ""),
    (".gitignore", ".gitignore"),
])
def test_get_file_name(path, expected):
    """Tests the get_file_name function."""
    assert lib_util.get_file_name(path) == expected


def test_get_current_func_name():
    """Tests the get_current_func_name function."""
    assert lib_util.get_current_func_name() == 'test_get_current_func_name'


@pytest.mark.parametrize("haystack, needle, n, expected", [
    ("abcabcabc", "abc", 0, 0),
    ("abcabcabc", "abc", 1, 3),
    ("abcabcabc", "abc", 2, 6),
    ("abcabcabc", "abc", 3, -1),
    ("aaaaa", "a", 4, 4),
    ("aaaaa", "b", 0, -1),
])
def test_findnth(haystack, needle, n, expected):
    """Tests the findnth function."""
    assert lib_util.findnth(haystack, needle, n) == expected


def test_get_random_str():
    """Tests the get_random_str function."""
    length = 10
    random_str = lib_util.get_random_str(length)
    assert len(random_str) == length
    assert all(c in '0123456789abcdefABCDEF' for c in random_str)


def test_get_aid_from_url_valid():
    """Tests the get_aid_from_url function with valid URLs."""
    url = 'https://www.ptt.cc/bbs/Python/M.1565335521.A.880.html'
    board, aid = lib_util.get_aid_from_url(url)
    assert board == 'Python'
    assert aid == '1TJH_XY0'

    url = 'https://www.ptt.cc/bbs/NCCU09_PSYCH/M.1322976839.A.0E3.html'
    board, aid = lib_util.get_aid_from_url(url)
    assert board == 'NCCU09_PSYCH'
    assert aid == '1EsmP73Z'


def test_get_aid_from_url_invalid():
    """Tests the get_aid_from_url function with invalid inputs."""
    with pytest.raises(exceptions.ParameterError, match='wrong parameter url must be www.ptt.cc post url'):
        lib_util.get_aid_from_url('https://google.com')
    with pytest.raises(TypeError):
        lib_util.get_aid_from_url(123)


def test_sync_version_smaller(monkeypatch):
    """Tests sync_version when the remote version is smaller."""
    mock_response = MagicMock()
    mock_response.text = "__version__ = '99.0.0'"
    mock_get = MagicMock(return_value=mock_response)
    monkeypatch.setattr('requests.get', mock_get)
    monkeypatch.setattr('PyPtt.lib_util.__version__', '0.1.0')
    lib_util.sync_version_compare = data_type.Compare.UNKNOWN
    compare, remote_version = lib_util.sync_version()
    assert compare == data_type.Compare.SMALLER
    assert remote_version == '99.0.0'


def test_sync_version_bigger(monkeypatch):
    """Tests sync_version when the remote version is bigger."""
    mock_response = MagicMock()
    mock_response.text = "__version__ = '0.0.1'"
    mock_get = MagicMock(return_value=mock_response)
    monkeypatch.setattr('requests.get', mock_get)
    monkeypatch.setattr('PyPtt.lib_util.__version__', '0.1.0')
    lib_util.sync_version_compare = data_type.Compare.UNKNOWN
    compare, remote_version = lib_util.sync_version()
    assert compare == data_type.Compare.BIGGER
    assert remote_version == '0.0.1'


def test_sync_version_same(monkeypatch):
    """Tests sync_version when the remote version is the same."""
    mock_response = MagicMock()
    mock_response.text = "__version__ = '0.1.0'"
    mock_get = MagicMock(return_value=mock_response)
    monkeypatch.setattr('requests.get', mock_get)
    monkeypatch.setattr('PyPtt.lib_util.__version__', '0.1.0')
    lib_util.sync_version_compare = data_type.Compare.UNKNOWN
    compare, remote_version = lib_util.sync_version()
    assert compare == data_type.Compare.SAME
    assert remote_version == '0.1.0'


def test_sync_version_dev(monkeypatch):
    """Tests sync_version with a development version string."""
    mock_response = MagicMock()
    mock_response.text = "__version__ = '0.1.0'"
    mock_get = MagicMock(return_value=mock_response)
    monkeypatch.setattr('requests.get', mock_get)
    monkeypatch.setattr('PyPtt.lib_util.__version__', '0.1.0-dev1')
    lib_util.sync_version_compare = data_type.Compare.UNKNOWN
    compare, remote_version = lib_util.sync_version()
    assert compare == data_type.Compare.SAME
    assert remote_version == '0.1.0'


def test_sync_version_fail(monkeypatch):
    """Tests sync_version when the network request fails."""
    mock_get = MagicMock(side_effect=requests.exceptions.ReadTimeout)
    monkeypatch.setattr('requests.get', mock_get)
    lib_util.sync_version_compare = data_type.Compare.UNKNOWN
    compare, remote_version = lib_util.sync_version()
    assert compare == data_type.Compare.SAME
    assert remote_version == ''


@pytest.mark.parametrize("input_text, expected_text", [
    ("a\nb\nc", "a\r\nb\r\nc"),
    ("a\r\nb\r\nc", "a\r\nb\r\nc"),
    ("a\nb\r\nc", "a\r\nb\r\nc"),
    ("", ""),
])
def test_uniform_new_line(input_text, expected_text):
    """Tests the uniform_new_line function."""
    assert lib_util.uniform_new_line(input_text) == expected_text


def test_check_aid_valid():
    """Tests the check_aid function with valid AIDs."""
    assert lib_util.check_aid('1TJH_XY0') == '#1TJH_XY0'
    assert lib_util.check_aid('#1TJH_XY0') == '#1TJH_XY0'


def test_check_aid_invalid():
    """Tests the check_aid function with invalid inputs."""
    with pytest.raises(exceptions.ParameterError, match='aid is not valid'):
        lib_util.check_aid('1234567')
    with pytest.raises(exceptions.ParameterError, match='aid is not valid'):
        lib_util.check_aid('123456789')
    with pytest.raises(exceptions.ParameterError, match='aid is not valid'):
        lib_util.check_aid('!@#$%^&*')
    with pytest.raises(exceptions.ParameterError, match='aid is None'):
        lib_util.check_aid(None)
    with pytest.raises(TypeError, match='aid is not str'):
        lib_util.check_aid(12345678)

def test_check_aid_cache():
    """Tests the lru_cache on the check_aid function."""
    lib_util.check_aid.cache_clear()
    assert lib_util.check_aid.cache_info().currsize == 0

    # First call, should be a miss
    lib_util.check_aid('1TJH_XY0')
    info = lib_util.check_aid.cache_info()
    assert info.hits == 0
    assert info.misses == 1
    assert info.currsize == 1

    # Second call with same arg, should be a hit
    lib_util.check_aid('1TJH_XY0')
    info = lib_util.check_aid.cache_info()
    assert info.hits == 1
    assert info.misses == 1
    assert info.currsize == 1

    # Call with different arg, should be a miss
    lib_util.check_aid('1EsmP73Z')
    info = lib_util.check_aid.cache_info()
    assert info.hits == 1
    assert info.misses == 2
    assert info.currsize == 2

    lib_util.check_aid.cache_clear()
    assert lib_util.check_aid.cache_info().currsize == 0