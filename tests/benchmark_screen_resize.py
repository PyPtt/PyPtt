"""
Benchmark: get_post WITH vs WITHOUT dynamic screen-height expansion.

The `expanded_screen` context manager in _api_util.py temporarily resizes the
PTT terminal from 24 rows to 100 rows during get_content(), reducing the number
of send() round-trips needed to page through a post.  This script measures the
actual difference in:

  - Wall-clock time for 100 posts
  - Total send() calls for those posts
  - Average send() calls per post

Usage:
    python3 tests/benchmark_screen_resize.py

Requires .env with PTT1_ID and PTT1_PW.
"""
from __future__ import annotations

import contextlib
import os
import sys
import time
import threading
from pathlib import Path
from statistics import mean, median, stdev

# ─── Load .env ────────────────────────────────────────────────────────────────
_env_path = Path(__file__).parent.parent / '.env'
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _, _v = _line.partition('=')
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

_repo_root = str(Path(__file__).parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import PyPtt
from PyPtt import exceptions, connect_core
import PyPtt._api_util as _api_util

# ─── Config ───────────────────────────────────────────────────────────────────
PTT_ID = os.environ.get('PTT1_ID', '')
PTT_PW = os.environ.get('PTT1_PW', '')
BOARD = 'Gossiping'
TARGET_POSTS = 100
INTER_POST_SLEEP = 0.05   # seconds between posts
MAX_RETRIES = 3

# ─── send() call counter ─────────────────────────────────────────────────────
_send_count = 0
_send_lock = threading.Lock()
_original_send = connect_core.API.send


def _patched_send(self, msg, target_list, screen_timeout=0, refresh=True, secret=False):
    global _send_count
    with _send_lock:
        _send_count += 1
    return _original_send(self, msg, target_list, screen_timeout=screen_timeout,
                          refresh=refresh, secret=secret)


connect_core.API.send = _patched_send


# ─── No-op context manager for disabling expanded_screen ─────────────────────
@contextlib.contextmanager
def _noop_expanded_screen(api):
    """Drop-in replacement: do NOT resize the terminal window."""
    yield


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _login(silent: bool = True) -> PyPtt.API:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            bot = PyPtt.API(log_level=PyPtt.LogLevel.SILENT if silent else PyPtt.LogLevel.INFO)
            bot.login(PTT_ID, PTT_PW, kick_other_session=True)
            return bot
        except exceptions.LoginTooOften:
            wait = 15 * attempt
            print(f'  [login] LoginTooOften — wait {wait}s (attempt {attempt})')
            time.sleep(wait)
        except exceptions.WrongIDorPassword:
            print('  [login] Wrong ID or password')
            sys.exit(1)
        except Exception as e:
            wait = 15 * attempt
            print(f'  [login] {e} — wait {wait}s')
            time.sleep(wait)
    print('  [login] All retries exhausted')
    sys.exit(1)


def _fetch_post_indices(bot: PyPtt.API) -> list[int]:
    """Return up to TARGET_POSTS valid (non-deleted) post indices from BOARD."""
    newest = bot.get_newest_index(index_type=PyPtt.NewIndex.BOARD, board=BOARD)
    print(f'  Newest index on {BOARD}: {newest}')

    indices = []
    idx = newest
    checked = 0
    max_scan = TARGET_POSTS * 3   # scan at most 3× to find enough non-deleted

    while len(indices) < TARGET_POSTS and idx > 0 and checked < max_scan:
        try:
            meta = bot.get_post(BOARD, index=idx, query=True)
            status = meta.get('post_status') if meta else None
            if status not in (
                PyPtt.PostStatus.DELETED_BY_AUTHOR,
                PyPtt.PostStatus.DELETED_BY_MODERATOR,
                PyPtt.PostStatus.DELETED_BY_UNKNOWN,
            ) and meta and meta.get('pass_format_check', True):
                indices.append(idx)
        except Exception:
            pass
        idx -= 1
        checked += 1

    print(f'  Collected {len(indices)} post indices (scanned {checked})')
    return indices


def _run(label: str, post_indices: list[int], use_expanded_screen: bool) -> dict:
    """Login fresh, crawl all post_indices, return timing & send() stats."""
    global _send_count

    print(f'\n{"─" * 56}')
    print(f'  Run: {label}')
    print(f'  expanded_screen: {"ON" if use_expanded_screen else "OFF (noop)"}')
    print(f'{"─" * 56}')

    if not use_expanded_screen:
        _api_util.expanded_screen = _noop_expanded_screen
    else:
        _api_util.expanded_screen = _real_expanded_screen

    bot = _login()
    _send_count = 0
    send_baseline = _send_count

    total_success = 0
    total_skipped = 0
    total_failed = 0
    per_post_sends: list[int] = []
    per_post_times: list[float] = []

    wall_start = time.perf_counter()

    for i, post_index in enumerate(post_indices, start=1):
        s_before = _send_count
        t_before = time.perf_counter()

        post = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                post = bot.get_post(BOARD, index=post_index)
                break
            except (exceptions.ConnectionClosed, exceptions.LoginTooOften) as e:
                wait = 10 * attempt
                print(f'    [retry] {type(e).__name__} — wait {wait}s')
                time.sleep(wait)
                try:
                    bot.logout()
                except Exception:
                    pass
                bot = _login()
            except Exception as e:
                total_failed += 1
                break

        t_after = time.perf_counter()
        s_after = _send_count

        if post is None:
            total_failed += 1
            time.sleep(INTER_POST_SLEEP)
            continue

        status = post.get('post_status') if post else None
        if status in (
            PyPtt.PostStatus.DELETED_BY_AUTHOR,
            PyPtt.PostStatus.DELETED_BY_MODERATOR,
            PyPtt.PostStatus.DELETED_BY_UNKNOWN,
        ):
            total_skipped += 1
        else:
            total_success += 1

        sends = s_after - s_before
        elapsed = t_after - t_before
        per_post_sends.append(sends)
        per_post_times.append(elapsed)

        if i % 25 == 0 or i == len(post_indices):
            avg_s = mean(per_post_sends) if per_post_sends else 0
            avg_t = mean(per_post_times) if per_post_times else 0
            print(f'  [{i:3d}/{len(post_indices)}]  '
                  f'send/post={avg_s:.2f}  '
                  f's/post={avg_t:.2f}s')

        time.sleep(INTER_POST_SLEEP)

    wall_elapsed = time.perf_counter() - wall_start
    total_sends = _send_count - send_baseline

    try:
        bot.logout()
    except Exception:
        pass

    return {
        'label': label,
        'use_expanded_screen': use_expanded_screen,
        'wall_elapsed': wall_elapsed,
        'total_sends': total_sends,
        'success': total_success,
        'skipped': total_skipped,
        'failed': total_failed,
        'per_post_sends': per_post_sends,
        'per_post_times': per_post_times,
    }


def _print_result(r: dict) -> None:
    ps = r['per_post_sends']
    pt = r['per_post_times']
    n = len(ps)

    print(f"\n  {r['label']}")
    print(f"    expanded_screen : {'ON' if r['use_expanded_screen'] else 'OFF'}")
    print(f"    Posts attempted : {r['success'] + r['skipped'] + r['failed']}")
    print(f"      Success       : {r['success']}")
    print(f"      Skipped       : {r['skipped']}")
    print(f"      Failed        : {r['failed']}")
    print(f"    Wall time       : {r['wall_elapsed']:.1f}s")
    print(f"    Total send()    : {r['total_sends']}")
    if n:
        print(f"    send()/post     : mean={mean(ps):.2f}  "
              f"median={median(ps):.1f}  "
              f"stdev={stdev(ps) if n > 1 else 0:.2f}  "
              f"min={min(ps)}  max={max(ps)}")
        print(f"    time/post (s)   : mean={mean(pt):.3f}  "
              f"median={median(pt):.3f}  "
              f"stdev={stdev(pt) if n > 1 else 0:.3f}  "
              f"min={min(pt):.3f}  max={max(pt):.3f}")


def _print_comparison(a: dict, b: dict) -> None:
    ps_a = a['per_post_sends']
    ps_b = b['per_post_sends']
    pt_a = a['per_post_times']
    pt_b = b['per_post_times']

    if not ps_a or not ps_b:
        return

    sends_a = mean(ps_a)
    sends_b = mean(ps_b)
    time_a = mean(pt_a)
    time_b = mean(pt_b)

    sends_delta = sends_a - sends_b
    sends_pct = (sends_delta / sends_b * 100) if sends_b else 0
    time_delta = time_a - time_b
    time_pct = (time_delta / time_b * 100) if time_b else 0

    print(f"\n  Comparison (A vs B):")
    print(f"    send()/post  : A={sends_a:.2f}  B={sends_b:.2f}  "
          f"diff={sends_delta:+.2f}  ({sends_pct:+.1f}%)")
    print(f"    time/post(s) : A={time_a:.3f}  B={time_b:.3f}  "
          f"diff={time_delta:+.3f}s  ({time_pct:+.1f}%)")
    if sends_a < sends_b:
        print(f"    → A is faster by {abs(sends_pct):.1f}% fewer send() calls")
    elif sends_b < sends_a:
        print(f"    → B is faster by {abs(sends_pct):.1f}% fewer send() calls")
    else:
        print("    → No difference in send() count")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not PTT_ID or not PTT_PW:
        print('ERROR: PTT1_ID and PTT1_PW must be set (check .env)')
        sys.exit(1)

    print('=' * 56)
    print(f'  Benchmark: get_post screen-resize  ({TARGET_POSTS} posts)')
    print(f'  Board: {BOARD}')
    print('=' * 56)

    # Keep a reference to the real expanded_screen so we can restore it
    global _real_expanded_screen
    _real_expanded_screen = _api_util.expanded_screen

    # Phase 1: collect post indices (use expanded_screen = ON during collection)
    print('\n[Phase 1] Collecting post indices ...')
    _api_util.expanded_screen = _real_expanded_screen
    index_bot = _login()
    post_indices = _fetch_post_indices(index_bot)
    try:
        index_bot.logout()
    except Exception:
        pass

    if len(post_indices) < TARGET_POSTS:
        print(f'WARNING: only found {len(post_indices)} posts (wanted {TARGET_POSTS})')

    # Phase 2: run WITH expanded_screen (A)
    result_a = _run(
        label='A — WITH expanded_screen (100 rows)',
        post_indices=post_indices,
        use_expanded_screen=True,
    )

    # Cool-down to avoid LoginTooOften on rapid re-login
    print('\n  [cool-down 10s before run B ...]')
    time.sleep(10)

    # Phase 3: run WITHOUT expanded_screen (B)
    result_b = _run(
        label='B — WITHOUT expanded_screen (24 rows, noop)',
        post_indices=post_indices,
        use_expanded_screen=False,
    )

    # ─── Summary ─────────────────────────────────────────────────────────────
    print('\n' + '=' * 56)
    print('  BENCHMARK RESULTS')
    print('=' * 56)
    _print_result(result_a)
    _print_result(result_b)
    _print_comparison(result_a, result_b)
    print('=' * 56)


if __name__ == '__main__':
    main()
