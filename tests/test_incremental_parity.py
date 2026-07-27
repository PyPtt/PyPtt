"""
Parity tests for PyPtt.screens.IncrementalScreen.

The receive loop in connect_core streams bytes and must decide, after every
arriving chunk, whether the current screen matches a target. Re-parsing the
whole accumulated buffer on every chunk is O(N²); IncrementalScreen feeds each
byte through the VT100 state machine exactly once instead.

Correctness is anchored to the batch VT100Parser: feeding the same bytes in any
chunking — down to one byte at a time, the worst case for split escapes, split
multibyte characters and split ' \\x08' wide-char pairs — must yield the exact
same screen string. These tests pin that invariant so a future change to either
parser can't silently diverge.
"""

import glob
import random
from pathlib import Path

import pytest

from PyPtt.screens import IncrementalScreen, VT100Parser

FIXTURE_DIR = Path(__file__).resolve().parent / 'fixtures' / 'vt100'

CHUNK_SIZES = [1, 2, 3, 5, 7, 13, 64, 256, 100000]


def feed_in_chunks(data: bytes, encoding: str, chunk: int,
                   read_each: bool = False) -> str:
    parser = IncrementalScreen(encoding, 24)
    for i in range(0, len(data), chunk):
        parser.feed(data[i:i + chunk])
        if read_each:
            # Reading .screen mid-stream (as the receive loop does for target
            # matching) must not corrupt the committed state.
            _ = parser.screen
    return parser.screen


# ── crafted byte streams that stress the chunk boundaries ─────────────────────

CRAFTED = [
    b'',
    b'hello world',
    b'\x1b[1;37;44mHELLO\x1b[0m',                       # color strip
    b'BEFORE\x1b[2JAFTER',                              # clear screen
    b'A\x1b[2JB\x1b[2JC',                               # only last 2J wins
    b'helloworld\x1b[1;6H\x1b[K',                       # erase to EOL
    b'abc \x08def',                                     # single ' \x08'
    b'a    \x08\x08\x08\x08b',                          # cascading ' \x08'
    b'   \x08\x08\x08\x08\x08x',                        # more BS than spaces
    b'\x1b[5;3HHi\nNext',                               # positioning + newline
    b'  \x08\x08\xe2\x97\x8e tail',                     # ◎ via reservation pair
    b'\x1b[10;1H  \x08\x08\xe2\x80\xbb\x1b[10;3H \xe7\x99\xbc\xe4\xbf\xa1\xe7\xab\x99: x',
    b'\x1b[6nHELLO',                                    # unknown escape -> bail
    b'line1\r\nline2',                                  # CRLF
    b'helloworld\x1b[1;2HXY',                           # replace mode
    b'\x1b[100;1HX',                                    # row clamp
    b'\xe2\x94\x80' * 40,                               # long box-drawing run
    '中文範例'.encode('utf-8'),                          # wide chars
]


@pytest.mark.parametrize('data', CRAFTED)
@pytest.mark.parametrize('chunk', CHUNK_SIZES)
def test_crafted_parity_utf8(data, chunk):
    ref = VT100Parser(data, 'utf-8', 24).screen
    assert feed_in_chunks(data, 'utf-8', chunk) == ref
    assert feed_in_chunks(data, 'utf-8', chunk, read_each=True) == ref


BIG5_TEXTS = ['中文', '程式範例', '◎[軟工]※←→─▄▆', '看板《Python》 測試']


@pytest.mark.parametrize('text', BIG5_TEXTS)
@pytest.mark.parametrize('chunk', [1, 2, 3, 5, 64])
def test_big5uao_parity(text, chunk):
    data = text.encode('big5')
    ref = VT100Parser(data, 'big5uao', 24).screen
    assert feed_in_chunks(data, 'big5uao', chunk) == ref


def test_big5uao_realistic_stream_parity():
    # A PTT-shaped big5uao screen: clear, positioning, wide chars via the
    # ' \x08' reservation pattern, box drawing, erase-to-EOL, comment glyphs.
    def b5(s):
        return s.encode('big5')

    stream = (
        b'\x1b[2J\x1b[1;1H' + b5('看板《Python》')
        + b'\x1b[3;1H  \x08\x08' + b5('◎') + b5(' [問題] 測試中文標題 ')
        + b'\x1b[5;1H' + b5('※ 發信站: 批踢踢實業坊(ptt.cc)')
        + b'\x1b[6;1H' + b5('推 user123: 這是一則推文') + b'\x1b[K'
        + b'\x1b[10;1H' + b5('─' * 30)
        + b'\x1b[23;1H' + b5('瀏覽 第 1/2 頁')
    )
    ref = VT100Parser(stream, 'big5uao', 24).screen
    for chunk in CHUNK_SIZES:
        assert feed_in_chunks(stream, 'big5uao', chunk) == ref
        assert feed_in_chunks(stream, 'big5uao', chunk, read_each=True) == ref


# ── real captured PTT byte streams, every boundary ────────────────────────────

FIXTURES = sorted(glob.glob(str(FIXTURE_DIR / '*.bin')))


@pytest.mark.parametrize('fixture', FIXTURES, ids=lambda p: Path(p).stem)
@pytest.mark.parametrize('chunk', CHUNK_SIZES)
def test_fixture_parity(fixture, chunk):
    data = Path(fixture).read_bytes()
    encoding = Path(fixture[:-4] + '.encoding').read_text().strip()
    ref = VT100Parser(data, encoding, 24).screen
    assert feed_in_chunks(data, encoding, chunk) == ref
    assert feed_in_chunks(data, encoding, chunk, read_each=True) == ref


# ── send-round boundaries: a sequence split across two rounds ─────────────────
#
# connect_core renders one screen per send() round and blanks the parser
# between rounds. The byte stream, however, does not stop at a round boundary:
# the last chunk of a round can end mid-escape-sequence or mid-multibyte
# character. That tail is held back by _safe_cut, so rebuilding the parser for
# the next round used to drop it — a round whose first chunk was `[24;76H...`
# (its ESC lost with the previous parser) rendered as literal on-screen text.
# new_round() keeps the held tail and the incremental decoder, resetting only
# the rendered screen.

# (round 1 bytes that fully commit, unfinished tail, round 2 bytes, encoding)
ROUND_SEAMS = [
    (b'\x1b[2J\x1b[1;1HROUND1', b'\x1b', b'[24;76HX', 'utf-8'),          # lone ESC
    (b'\x1b[2J\x1b[1;1HROUND1', b'\x1b[24', b';76HX', 'utf-8'),          # mid CSI params
    (b'\x1b[2J\x1b[1;1HROUND1', b'\x1b[24;', b'76HX', 'utf-8'),
    (b'\x1b[2J\x1b[1;1H', b'\xe4\xb8', b'\xadX', 'utf-8'),               # 中 split (utf-8)
    (b'\x1b[2J\x1b[1;1H', b'\xa4', b'\xa4X', 'big5uao'),                 # 中 split (big5)
    (b'\x1b[2J\x1b[1;1H', b'  \x08\x08', b'\xe2\x97\x8eX', 'utf-8'),      # ◎ reservation pair
]


@pytest.mark.parametrize('committed,tail,round2,encoding', ROUND_SEAMS)
def test_new_round_carries_unfinished_tail(committed, tail, round2, encoding):
    """Round 2's screen must be what the batch parser makes of the unfinished
    tail plus round 2's bytes — the tail belongs to the byte stream, not to
    the round that happened to be reading when it arrived."""
    parser = IncrementalScreen(encoding, 24)
    parser.feed(committed + tail)
    _ = parser.screen                 # the receive loop reads every chunk
    parser.new_round()
    parser.feed(round2)

    assert parser.screen == VT100Parser(tail + round2, encoding, 24).screen


def test_new_round_does_not_render_orphan_escape_as_text():
    """The observed symptom: an ESC left dangling at the end of one round made
    the next round print its CSI verbatim (`[24;76H▄` on screen)."""
    parser = IncrementalScreen('utf-8', 24)
    parser.feed(b'\x1b[2J\x1b[1;1HROUND1\x1b')
    parser.new_round()
    parser.feed(b'[24;76H\xe2\x96\x84')

    screen = parser.screen
    assert '[24;76H' not in screen
    assert 'ROUND1' not in screen                     # round 1's screen is gone
    assert screen.split('\n')[23].strip() == '▄'      # rendered at row 24


def test_new_round_blanks_the_screen_but_keeps_decoding():
    """new_round() is round-scoped only: the previous round's rendered screen
    must not leak, and a parser frozen by an unknown escape must un-freeze."""
    parser = IncrementalScreen('utf-8', 24)
    parser.feed(b'\x1b[2J\x1b[1;1HOLD\x1b[6nDROPPED')   # ESC[6n -> bail
    assert 'OLD' in parser.screen

    parser.new_round()
    assert parser.screen == '\n' * 23
    parser.feed(b'\x1b[1;1HNEW')
    assert parser.screen.split('\n')[0] == 'NEW'


@pytest.mark.parametrize('fixture', FIXTURES, ids=lambda p: Path(p).stem)
def test_fixture_parity_random_chunking(fixture):
    # Randomised chunk boundaries with a mid-stream .screen read each step —
    # exactly how the receive loop drives the parser.
    data = Path(fixture).read_bytes()
    encoding = Path(fixture[:-4] + '.encoding').read_text().strip()
    ref = VT100Parser(data, encoding, 24).screen
    for seed in range(25):
        rnd = random.Random(seed)
        parser = IncrementalScreen(encoding, 24)
        i = 0
        while i < len(data):
            n = rnd.randint(1, 9)
            parser.feed(data[i:i + n])
            _ = parser.screen
            i += n
        assert parser.screen == ref, f'seed={seed}'
