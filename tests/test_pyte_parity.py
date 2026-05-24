"""
Cross-check PyPtt.screens.VT100Parser against the pyte reference emulator
on real PTT byte streams (replayed from tests/fixtures/vt100/*.bin).

Why this test exists
--------------------
VT100Parser is hand-rolled. pyte is the de-facto reference VT100/ANSI
emulator in Python. Catching cell-position regressions in our parser by
running both over the same bytes and diffing the resulting 24-row screens
is the strongest signal we get without rendering on a real terminal.

Why the diff isn't zero
-----------------------
PyPtt and pyte use *different but internally consistent* models for the
` \\x08` (space-then-backspace) byte pattern PTT sends to "draw forward"
of a wide character:

  - PyPtt collapses ` \\x08` pairs to nothing during preprocessing, so
    only the wide char ends up on the screen ('[←]', '※ 發信站').
  - pyte treats `\\x08` as a literal cursor-left, leaving the leading
    spaces in place so the wide char ends up adjacent to a placeholder
    space ('[← ]', '※  發信站').

Both representations have the same visible width on a terminal — they
differ only in how many chars they occupy in the returned string.

What this test guards
---------------------
The *count* of differing rows per fixture is pinned to a baseline. If a
regression introduces real positional shifts (e.g. column off-by-one or
byte-vs-cell confusion comes back), the count will jump well past the
baseline and the test will fail with a clear breakdown.
"""
from pathlib import Path

import pytest

pyte = pytest.importorskip('pyte')  # dev dep; not required at runtime

from PyPtt.screens import VT100Parser

FIXTURE_DIR = Path(__file__).resolve().parent / 'fixtures' / 'vt100'

# Per-fixture cap on row-level diffs against pyte. Numbers reflect the
# residual `\x08`/wide-char-convention differences described in the module
# docstring — verified manually as benign. Bump only with justification.
DIFF_BASELINES = {
    'board_info_python': 3,
    'favourite_boards': 17,
    'main_menu': 10,
    'post_full': 11,
    'post_listing': 6,
    'user_profile': 1,
}


def _parse_pyte(data: bytes, encoding: str) -> list[str]:
    """Run pyte over the same bytes; drop wide-char placeholder cells so
    the resulting strings are comparable to PyPtt's string-position model.
    """
    screen = pyte.Screen(80, 24)
    if encoding == 'utf-8':
        stream = pyte.ByteStream(screen)
        stream.feed(data)
    else:
        stream = pyte.Stream(screen)
        stream.feed(data.decode(encoding, errors='replace'))
    rows = []
    for y in range(24):
        chars = []
        for x in range(80):
            cell = screen.buffer[y][x]
            if cell.data == '':
                continue  # trailing half of a wide char
            chars.append(cell.data)
        rows.append(''.join(chars).rstrip())
    return rows


def _parse_pyptt(data: bytes, encoding: str) -> list[str]:
    return [r.rstrip() for r in VT100Parser(data, encoding).screen.split('\n')]


def _load(name: str) -> tuple[bytes, str]:
    data = (FIXTURE_DIR / f'{name}.bin').read_bytes()
    encoding = (FIXTURE_DIR / f'{name}.encoding').read_text().strip()
    return data, encoding


@pytest.mark.parametrize('name', sorted(DIFF_BASELINES.keys()))
def test_pyte_parity_within_baseline(name):
    data, encoding = _load(name)
    pyptt_rows = _parse_pyptt(data, encoding)
    pyte_rows = _parse_pyte(data, encoding)

    diffs = [(i, a, b) for i, (a, b) in enumerate(zip(pyptt_rows, pyte_rows))
             if a != b]
    baseline = DIFF_BASELINES[name]

    if len(diffs) > baseline:
        # Build a readable failure that shows the first few unexpected diffs
        # so the regression is easy to diagnose.
        sample = '\n'.join(
            f'  row {i:2d}:\n    PyPtt: {a!r}\n    pyte : {b!r}'
            for i, a, b in diffs[:5]
        )
        pytest.fail(
            f'{name}: {len(diffs)} differing rows (baseline {baseline}).\n'
            f'First diffs:\n{sample}\n'
            f'If diffs are legitimate (new wide-char/backspace pattern), '
            f'update DIFF_BASELINES; otherwise this is a parser regression.'
        )


def _normalize(s: str) -> str:
    """Strip spaces and U+FFFD (replacement char) for content-only comparison.

    `\\ufffd` appears when a fixture buffer was truncated mid-UTF-8 — that's
    a capture artifact, not a parser difference.
    """
    return s.replace(' ', '').replace('�', '')


def test_no_fixture_has_column_shift_diff():
    """A column shift would manifest as a diff where the same chars appear
    but offset by one position. This is the failure mode we *especially*
    want to catch — it would silently corrupt every downstream parser that
    uses positional slicing (_api_get_post_list, etc.).

    Heuristic: for every diff row, if removing spaces and replacement chars
    makes the two strings equal, the diff is purely a spacing/capture
    artifact (the kind we expect). Anything else is a real regression.
    """
    offenders = []
    for name in DIFF_BASELINES:
        data, encoding = _load(name)
        pyptt_rows = _parse_pyptt(data, encoding)
        pyte_rows = _parse_pyte(data, encoding)
        for i, (a, b) in enumerate(zip(pyptt_rows, pyte_rows)):
            if a == b:
                continue
            if _normalize(a) != _normalize(b):
                offenders.append((name, i, a, b))

    if offenders:
        sample = '\n'.join(
            f'  {name} row {i}:\n    PyPtt: {a!r}\n    pyte : {b!r}'
            for name, i, a, b in offenders[:5]
        )
        pytest.fail(
            f'{len(offenders)} row(s) differ by more than just spacing — '
            f'likely a column-shift or character-loss regression.\n'
            f'First offenders:\n{sample}'
        )
