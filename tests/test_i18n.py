import pytest

import PyPtt
from PyPtt import i18n, exceptions

# Data from lang files for assertion
english_goodbye = [
    "good bye",
    "bye",
    "see you",
    "catch you later",
    "I hate to run, but...",
    "Until we meet again, I will wait"
]
english_goodbye = [s.lower() for s in english_goodbye]  # For case-insensitive comparison

mandarin_goodbye = [
    "再見",
    "下次再見",
    "再會",
    "祝平安",
    "謝謝你，我很開心",
    "我們會再見面的"
]


def test_i18n_english_init():
    """Tests i18n initialization for English and capitalization."""
    i18n.init(PyPtt.Language.ENGLISH)
    assert i18n.goodbye is not None
    # Check if the selected string is from the original list (case-insensitive)
    assert i18n.goodbye.lower() in english_goodbye
    # Check that the first letter is capitalized
    assert i18n.goodbye[0].isupper()


def test_i18n_mandarin_init():
    """Tests i18n initialization for Mandarin."""
    i18n.init(PyPtt.Language.MANDARIN)
    assert i18n.goodbye is not None
    assert i18n.goodbye in mandarin_goodbye


def test_i18n_replace():
    """Tests the i18n.replace function with a single argument."""
    i18n.init(PyPtt.Language.ENGLISH)
    replaced_string = i18n.replace(i18n.welcome, 'test version')
    assert replaced_string == 'PyPtt v test version'

    i18n.init(PyPtt.Language.MANDARIN)
    replaced_string_zh = i18n.replace(i18n.welcome, '測試版本')
    assert replaced_string_zh == 'PyPtt v 測試版本'


def test_i18n_replace_multiple_args():
    """Tests the i18n.replace function with multiple arguments."""
    i18n.init(PyPtt.Language.ENGLISH)
    replaced_en = i18n.replace(i18n.no_such_post, 'Test', '#123ABC')
    assert replaced_en == 'In Test, the post code is not EXISTS #123ABC'

    i18n.init(PyPtt.Language.MANDARIN)
    replaced = i18n.replace(i18n.no_such_post, 'Test', '#123ABC')
    assert replaced == 'Test 板找不到這個文章代碼 #123ABC'


def test_i18n_invalid_locale():
    """Tests that init raises ParameterError for an invalid locale."""
    with pytest.raises(exceptions.ParameterError):
        i18n.init('invalid_locale')


def test_i18n_caching(monkeypatch):
    """Tests the caching mechanism in i18n.init."""
    # Clear the cache for a clean test
    monkeypatch.setattr(i18n, '_lang_data', {})
    assert not i18n._lang_data

    # Init without cache
    i18n.init(PyPtt.Language.MANDARIN, cache=False)
    assert not i18n._lang_data

    # Init with cache
    i18n.init(PyPtt.Language.MANDARIN, cache=True)
    assert i18n._lang_data
    assert 'welcome' in i18n._lang_data
    assert i18n.welcome == i18n._lang_data['welcome']
