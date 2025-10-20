"""
This file contains tests for the value checking functions in PyPtt.check_value.
"""
import pytest
from PyPtt import check_value, exceptions, i18n

# Initialize i18n for exception messages
@pytest.fixture(scope="module", autouse=True)
def init_i18n_for_exceptions():
    i18n.init('zh_TW')

# Tests for check_type


def test_check_type_success():
    """Tests that check_type passes for correct types."""
    assert check_value.check_type("hello", str, "my_string") is None
    assert check_value.check_type(123, int, "my_int") is None
    assert check_value.check_type(True, bool, "my_bool") is None
    assert check_value.check_type([1, 2], list, "my_list") is None
    assert check_value.check_type((1, 2), (list, tuple), "my_tuple") is None


def test_check_type_failure():
    """Tests that check_type raises TypeError for incorrect types."""
    with pytest.raises(TypeError, match=r"\[PyPtt\] my_string 必須為字串, but got 123"):
        check_value.check_type(123, str, "my_string")
    with pytest.raises(TypeError, match=r"\[PyPtt\] my_int 必須為數字, but got hello"):
        check_value.check_type("hello", int, "my_int")
    with pytest.raises(TypeError, match=r"\[PyPtt\] my_bool 必須為布林值, but got 0"):
        check_value.check_type(0, bool, "my_bool")
    with pytest.raises(TypeError, match=r"\[PyPtt\] my_list 必須為字串, but got \[1, 2\]"):
        check_value.check_type([1, 2], str, "my_list")

# Tests for check_range


def test_check_range_success():
    """Tests that check_range passes for values within the specified range."""
    assert check_value.check_range(5, 1, 10, "in_range") is None
    assert check_value.check_range(1, 1, 10, "min_boundary") is None
    assert check_value.check_range(10, 1, 10, "max_boundary") is None
    assert check_value.check_range(5, max_value=10, name="no_min") is None
    assert check_value.check_range(5, min_value=1, name="no_max") is None


def test_check_range_failure():
    """Tests that check_range raises ParameterError for out-of-range values."""
    with pytest.raises(exceptions.ParameterError, match="too_low 0 必須大於 0"):
        check_value.check_range(0, 1, 10, "too_low")
    with pytest.raises(exceptions.ParameterError, match="too_high 11 必須小於 11"):
        check_value.check_range(11, 1, 10, "too_high")
    with pytest.raises(TypeError, match="wrong_type 必須為數字, but got 5"):
        check_value.check_range("5", 1, 10, "wrong_type")

# Tests for check_index


def test_check_index_success():
    """Tests that check_index passes for valid index values."""
    assert check_value.check_index("my_index", 5, 10) is None
    assert check_value.check_index("my_index", 1, 10) is None
    assert check_value.check_index("my_index", 10, 10) is None
    assert check_value.check_index("my_index", 5) is None  # no max_value


def test_check_index_failure():
    """Tests that check_index raises errors for invalid index values."""
    with pytest.raises(exceptions.ParameterError, match="my_index 必須大於 0"):
        check_value.check_index("my_index", 0)
    with pytest.raises(exceptions.ParameterError, match="my_index 必須大於 0"):
        check_value.check_index("my_index", -1)
    with pytest.raises(exceptions.ParameterError, match="my_index 11 必須介於 0 ~ 10"):
        check_value.check_index("my_index", 11, 10)
    with pytest.raises(TypeError, match="my_index 必須為數字, but got 5"):
        check_value.check_index("my_index", "5")

# Tests for check_index_range


def test_check_index_range_success():
    """Tests that check_index_range passes for valid ranges."""
    assert check_value.check_index_range("start", 2, "end", 10, 20) is None
    assert check_value.check_index_range("start", 1, "end", 10) is None  # no max_value
    assert check_value.check_index_range("start", 5, "end", 5) is None


def test_check_index_range_failure():
    """Tests that check_index_range raises errors for invalid ranges."""
    with pytest.raises(exceptions.ParameterError, match="start 0 必須大於 0"):
        check_value.check_index_range("start", 0, "end", 10)
    with pytest.raises(exceptions.ParameterError, match="end 1 必須大於 1"):
        check_value.check_index_range("start", 1, "end", 1)
    with pytest.raises(exceptions.ParameterError, match="end 5 必須大於 start 10"):
        check_value.check_index_range("start", 10, "end", 5)
    with pytest.raises(exceptions.ParameterError, match="end 25 必須小於 20"):
        check_value.check_index_range("start", 1, "end", 25, 20)
    with pytest.raises(exceptions.ParameterError, match="start 21 必須小於 20"):
        check_value.check_index_range("start", 21, "end", 25, 20)
    with pytest.raises(TypeError, match="start 必須為數字, but got 1"):
        check_value.check_index_range("start", "1", "end", 10)
    with pytest.raises(TypeError, match="end 必須為數字, but got 10"):
        check_value.check_index_range("start", 1, "end", "10")
