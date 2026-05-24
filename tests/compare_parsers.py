"""
Cross-check PyPtt.screens.VT100Parser against pyte (battle-tested reference
VT100 emulator) on real PTT byte streams.

For every fixture in tests/fixtures/vt100/, we:
  1. parse with PyPtt's VT100Parser
  2. parse with pyte.Screen / pyte.ByteStream
  3. diff the resulting 24-row screens line by line (after rstrip)

Any divergence is printed with both versions side-by-side.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pyte

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PyPtt.screens import VT100Parser


FIXTURE_DIR = Path(__file__).resolve().parent / 'fixtures' / 'vt100'


def parse_pyptt(data: bytes, encoding: str) -> list[str]:
    return VT100Parser(data, encoding).screen.split('\n')


def parse_pyte(data: bytes, encoding: str) -> list[str]:
    # 80x24 terminal, matching PTT's default geometry.
    screen = pyte.Screen(80, 24)
    stream = pyte.ByteStream(screen)
    # ByteStream takes raw bytes; pyte handles decoding internally if we set
    # the screen's mode beforehand. For UTF-8 / big5-uao we feed bytes and
    # rely on pyte's UTF-8 default. For big5-uao we pre-decode.
    if encoding == 'utf-8':
        stream.feed(data)
    else:
        # pyte only ships UTF-8; for big5-uao, decode then feed via Stream.
        text_stream = pyte.Stream(screen)
        text_stream.feed(data.decode(encoding, errors='replace'))
    return list(screen.display)


def diff_rows(name: str, a_rows: list[str], b_rows: list[str]) -> int:
    diff_count = 0
    print(f'\n{"=" * 78}')
    print(f' {name}')
    print(f'{"=" * 78}')
    for i in range(24):
        a = a_rows[i].rstrip() if i < len(a_rows) else ''
        b = b_rows[i].rstrip() if i < len(b_rows) else ''
        if a == b:
            continue
        diff_count += 1
        # Show diff with row index. PyPtt = our parser, pyte = reference.
        print(f'\n  row {i:2d} DIFF')
        print(f'    PyPtt : {a!r}')
        print(f'    pyte  : {b!r}')
    if diff_count == 0:
        print('  (no differences)')
    else:
        print(f'\n  → {diff_count} row(s) differ')
    return diff_count


def main() -> int:
    fixtures = sorted(FIXTURE_DIR.glob('*.bin'))
    if not fixtures:
        print(f'no fixtures in {FIXTURE_DIR} — run capture_vt100_fixtures.py first',
              file=sys.stderr)
        return 1

    total = 0
    for bin_path in fixtures:
        name = bin_path.stem
        encoding = bin_path.with_suffix('.encoding').read_text().strip()
        data = bin_path.read_bytes()

        pyptt_rows = parse_pyptt(data, encoding)
        try:
            pyte_rows = parse_pyte(data, encoding)
        except Exception as e:
            print(f'\n{name}: pyte raised {e!r}')
            continue
        total += diff_rows(name, pyptt_rows, pyte_rows)

    print(f'\n{"=" * 78}')
    print(f' TOTAL: {total} differing row(s) across {len(fixtures)} fixtures')
    print(f'{"=" * 78}')
    return 0 if total == 0 else 2


if __name__ == '__main__':
    sys.exit(main())
