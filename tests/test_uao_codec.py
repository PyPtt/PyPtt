"""
Regression tests for the vendored Big5-UAO codec (PyPtt/_uao).

`_decode` batches ASCII runs (one C-level decode instead of a chr()/append per
byte). These tests pin the invariant that the batched path produces exactly the
same output as a naive byte-by-byte decode, across ASCII runs, character
boundaries, incremental feeding and UAO-specific characters that stdlib `big5`
gets wrong or cannot represent.
"""

import codecs

import pytest

import PyPtt.screens  # noqa: F401 — importing registers the big5uao codec


def naive_decode(data: bytes, errors: str = 'replace') -> str:
    """Reference: decode one unit at a time, no ASCII batching."""
    from PyPtt._uao.b2u import b2u_table
    get = b2u_table.get
    out = []
    i, n = 0, len(data)
    while i < n:
        c = data[i]
        if c < 0x80:
            out.append(chr(c))
            i += 1
            continue
        pair = get(c * 0x100 + data[i + 1]) if i + 1 < n else None
        if pair is not None:
            out.append(pair)
            i += 2
            continue
        single = get(c)
        if single is not None:
            out.append(single)
            i += 1
            continue
        out.append('�')  # errors='replace'
        i += 1
    return ''.join(out)


ASCII_CASES = [
    b'',
    b'hello world 12345',
    b'   leading and trailing spaces   ',
    b'[Ctrl-P] [d]delete [z]digest (100%)',
]


@pytest.mark.parametrize('data', ASCII_CASES)
def test_ascii_runs_decode_verbatim(data):
    assert data.decode('big5uao') == data.decode('ascii')


def test_mixed_ascii_and_cjk():
    s = '  9439   3 1/10 littrabble   ◎ [問題] 測試中文標題 discussion'
    assert s.encode('big5uao').decode('big5uao') == s


def test_uao_specific_characters_round_trip():
    # Characters where stdlib big5 disagrees with UAO or can't encode them.
    for s in ['‧', '～', '￥', '￠', '﹨', '⊕', '◎', '※', '←', '→', '─']:
        assert s.encode('big5uao').decode('big5uao') == s


@pytest.mark.parametrize('errors', ['replace', 'ignore', 'strict'])
def test_batched_matches_naive_on_valid_content(errors):
    s = '看板《Python》 test 混合 content 123 ‧～ ◎[軟工] tail'
    data = s.encode('big5uao')
    assert data.decode('big5uao', errors) == naive_decode(data)


def test_incremental_byte_by_byte_matches_batch():
    s = '批踢踢 Python 測試 ‧～￥ ◎[軟工] 12345'
    data = s.encode('big5uao')
    dec = codecs.getincrementaldecoder('big5uao')('replace')
    out = ''.join(dec.decode(bytes([b])) for b in data) + dec.decode(b'', final=True)
    assert out == data.decode('big5uao') == s


def test_incremental_splits_multibyte_across_chunks():
    data = '中文'.encode('big5uao')
    dec = codecs.getincrementaldecoder('big5uao')('replace')
    # Split inside the first character's byte pair.
    out = dec.decode(data[:1]) + dec.decode(data[1:], final=True)
    assert out == '中文'


def test_lone_0xff_maps_to_uao_private_use():
    assert b'\xff'.decode('big5uao') == ''
