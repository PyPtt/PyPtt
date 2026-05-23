"""
Capture real raw byte streams from PTT for VT100Parser regression tests.

Run once (against a live PTT session) to populate tests/fixtures/vt100/*.bin
with representative screen captures. The tests in test_vt100_parser.py then
parse those fixtures back through VT100Parser and assert on stable content.

The login phase is intentionally excluded from capture so password-bearing
screens never land on disk.

Usage:
    python3 tests/capture_vt100_fixtures.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Allow running as a script from project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import PyPtt
from PyPtt import screens


FIXTURE_DIR = Path(__file__).resolve().parent / 'fixtures' / 'vt100'
FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

# (label, bytes, encoding) tuples accumulated while capture is enabled.
_captured: list[tuple[bytes, str]] = []
_capture_enabled = False

_orig_init = screens.VT100Parser.__init__


def _patched_init(self, bytes_data: bytes, encoding: str) -> None:
    if _capture_enabled and bytes_data:
        _captured.append((bytes(bytes_data), encoding))
    _orig_init(self, bytes_data, encoding)


screens.VT100Parser.__init__ = _patched_init


def save(label: str, bytes_data: bytes, encoding: str) -> None:
    path = FIXTURE_DIR / f'{label}.bin'
    path.write_bytes(bytes_data)
    (FIXTURE_DIR / f'{label}.encoding').write_text(encoding)
    print(f'  saved {label}.bin ({len(bytes_data)} bytes, {encoding})')


def take_last(label: str) -> None:
    """Save the most-recent captured chunk under the given label."""
    if not _captured:
        print(f'  [skip] no capture available for {label}')
        return
    data, encoding = _captured[-1]
    save(label, data, encoding)


def main() -> int:
    load_dotenv()
    ptt_id = os.environ.get('PTT1_ID')
    ptt_pw = os.environ.get('PTT1_PW')
    if not ptt_id or not ptt_pw:
        print('PTT1_ID / PTT1_PW not set in .env', file=sys.stderr)
        return 1

    bot = PyPtt.API(host=PyPtt.HOST.PTT1)

    print('logging in (capture disabled)...')
    for attempt in range(3):
        try:
            bot.login(ptt_id=ptt_id, ptt_pw=ptt_pw, kick_other_session=True)
            break
        except PyPtt.LoginTooOften:
            wait = 10 * (attempt + 1)
            print(f'  LoginTooOften — sleeping {wait}s and retrying')
            time.sleep(wait)
    else:
        print('login failed', file=sys.stderr)
        return 1
    print('  logged in')

    global _capture_enabled
    try:
        # ─── main_menu ──────────────────────────────────────────────────
        _captured.clear()
        _capture_enabled = True
        # get_time() bounces through the main menu utility; the last buffer
        # is typically a fresh main-menu screen.
        bot.get_time()
        _capture_enabled = False
        take_last('main_menu')

        # ─── board_info_python ──────────────────────────────────────────
        _captured.clear()
        _capture_enabled = True
        bot.get_board_info(board='Python')
        _capture_enabled = False
        take_last('board_info_python')

        # ─── post_content ───────────────────────────────────────────────
        _captured.clear()
        _capture_enabled = True
        newest = bot.get_newest_index(index_type=PyPtt.NewIndex.BOARD, board='Python')
        bot.get_post(board='Python', index=newest)
        _capture_enabled = False
        take_last('post_full')
        # Also grab one earlier buffer to capture the post-listing screen.
        if len(_captured) >= 2:
            data, encoding = _captured[0]
            save('post_listing', data, encoding)

        # ─── user_profile ───────────────────────────────────────────────
        _captured.clear()
        _capture_enabled = True
        bot.get_user(user_id=ptt_id)
        _capture_enabled = False
        take_last('user_profile')

        # ─── favourite_boards ───────────────────────────────────────────
        _captured.clear()
        _capture_enabled = True
        try:
            bot.get_favourite_boards()
        except Exception as e:
            print(f'  get_favourite_boards failed: {e}')
        _capture_enabled = False
        take_last('favourite_boards')

    finally:
        _capture_enabled = False
        try:
            bot.logout()
            print('logged out')
        except Exception as e:
            print(f'logout failed: {e}')

    print(f'\nfixtures written to {FIXTURE_DIR}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
