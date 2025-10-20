"""
This file contains tests for the data types in PyPtt.data_type.
"""
import pytest
import time
from PyPtt import data_type

# Tests for TimedDict

def test_timed_dict_set_get():
    """Tests setting and getting items from TimedDict."""
    td = data_type.TimedDict(timeout=1)
    td['key'] = 'value'
    assert td['key'] == 'value'
    assert 'key' in td

def test_timed_dict_timeout():
    """Tests that items expire after the timeout."""
    td = data_type.TimedDict(timeout=0.1)
    td['key'] = 'value'
    assert 'key' in td
    time.sleep(0.2)
    with pytest.raises(KeyError):
        _ = td['key']
    assert 'key' not in td

def test_timed_dict_len_and_cleanup():
    """Tests the __len__ method and the cleanup mechanism."""
    td = data_type.TimedDict(timeout=0.1)
    td['a'] = 1
    td['b'] = 2
    assert len(td) == 2
    time.sleep(0.2)
    # __len__ calls cleanup, so the length should now be 0
    assert len(td) == 0
    # Check that items are actually gone
    assert 'a' not in td
    assert 'b' not in td

def test_timed_dict_no_timeout():
    """Tests TimedDict with timeout set to 0 (no expiration)."""
    td = data_type.TimedDict(timeout=0)
    td['key'] = 'value'
    time.sleep(0.1)  # Should not expire
    assert td['key'] == 'value'
    assert len(td) == 1

def test_timed_dict_update_timestamp():
    """Tests that updating an item also updates its expiration timestamp."""
    td = data_type.TimedDict(timeout=0.2)
    td['key'] = 'value1'
    time.sleep(0.1)
    assert 'key' in td
    td['key'] = 'value2'  # This should reset the timer for 'key'
    time.sleep(0.15)
    assert td['key'] == 'value2'  # Should still exist
