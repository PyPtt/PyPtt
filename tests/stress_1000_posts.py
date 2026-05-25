"""
Stress test: read 1000 PTT posts, validate screen-height optimisation and check for content corruption.

Usage:
    python3 tests/stress_1000_posts.py

Requires .env with PTT1_ID and PTT1_PW.
"""
from __future__ import annotations

import os
import sys
import time
import threading
from pathlib import Path

# Load .env from repo root
_env_path = Path(__file__).parent.parent / '.env'
if _env_path.exists():
    with open(_env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# Add project root to sys.path
_repo_root = str(Path(__file__).parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import PyPtt
from PyPtt import exceptions, connect_core

# ─── Monkey-patch connect_core.API.send to count calls ──────────────────────
_send_call_count = 0
_send_lock = threading.Lock()

_original_send = connect_core.API.send


def _patched_send(self, msg, target_list, screen_timeout=0, refresh=True, secret=False):
    global _send_call_count
    with _send_lock:
        _send_call_count += 1
    return _original_send(self, msg, target_list, screen_timeout=screen_timeout,
                          refresh=refresh, secret=secret)


connect_core.API.send = _patched_send


# ─── Config ─────────────────────────────────────────────────────────────────
PTT_ID = os.environ.get('PTT1_ID', '')
PTT_PW = os.environ.get('PTT1_PW', '')
BOARD = 'Gossiping'
TARGET_POSTS = 1000
INTER_POST_SLEEP = 0.1   # seconds between posts to avoid hammering PTT
MAX_RETRIES = 5


# ─── Header injection detection ─────────────────────────────────────────────

def _is_header_injected(content: str) -> bool:
    """Return True if the content looks like it has a PTT post header injected
    in the MIDDLE of the body (not the very first lines).

    Only flag clear-cut cases: '\n作者 ' or '\n標題 ' more than 3 lines into the
    content AND the match is immediately preceded by an empty line.
    """
    lines = content.split('\n')
    if len(lines) < 4:
        return False

    # Only inspect lines beyond the first 3 (which could legitimately start
    # with 作者/標題 in some edge posts).
    body_from_line4 = '\n'.join(lines[3:])

    for marker in ('\n作者 ', '\n標題 '):
        pos = body_from_line4.find(marker)
        while pos != -1:
            # Check that the character immediately before the marker (i.e.,
            # the line before) is an empty line — PTT header format always has
            # a blank line before 作者.
            preceding = body_from_line4[:pos]
            if preceding.endswith('\n') or preceding == '':
                # Preceded by empty line (or very start of search region) — suspicious
                return True
            pos = body_from_line4.find(marker, pos + 1)

    return False


# ─── Login with retry ────────────────────────────────────────────────────────

def create_bot_with_retry() -> PyPtt.API:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            bot = PyPtt.API(log_level=PyPtt.LogLevel.SILENT)
            bot.login(PTT_ID, PTT_PW, kick_other_session=True)
            print(f'[LOGIN] Logged in as {PTT_ID}')
            return bot
        except exceptions.LoginTooOften:
            wait = 15 * attempt
            print(f'[LOGIN] LoginTooOften — waiting {wait}s (attempt {attempt}/{MAX_RETRIES})')
            time.sleep(wait)
        except exceptions.WrongIDorPassword:
            print('[LOGIN] Wrong ID or password — check .env')
            sys.exit(1)
        except Exception as e:
            wait = 15 * attempt
            print(f'[LOGIN] Error: {e} — waiting {wait}s (attempt {attempt}/{MAX_RETRIES})')
            time.sleep(wait)
    print('[LOGIN] Failed to login after all retries')
    sys.exit(1)


# ─── Get post list with retry ─────────────────────────────────────────────────

def get_post_list_with_retry(bot: PyPtt.API, board: str, limit: int) -> list:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f'[LIST] Fetching {limit} posts from {board} ...')
            post_list = bot.get_post_list(board, limit=limit)
            print(f'[LIST] Got {len(post_list)} posts')
            return post_list
        except (exceptions.ConnectionClosed, exceptions.LoginTooOften) as e:
            wait = 15 * attempt
            print(f'[LIST] {type(e).__name__}: {e} — waiting {wait}s and re-logging in')
            time.sleep(wait)
            bot.logout()
            bot = create_bot_with_retry()
        except Exception as e:
            wait = 15 * attempt
            print(f'[LIST] Unexpected error: {e} — waiting {wait}s')
            time.sleep(wait)
    print('[LIST] Failed to get post list after all retries')
    sys.exit(1)


# ─── Main stress loop ─────────────────────────────────────────────────────────

def main():
    global _send_call_count

    if not PTT_ID or not PTT_PW:
        print('ERROR: PTT1_ID and PTT1_PW must be set (check .env)')
        sys.exit(1)

    print('=' * 60)
    print(f'PTT Stress Test: 1000 posts from {BOARD}')
    print('=' * 60)

    start_time = time.time()
    _send_call_count = 0

    bot = create_bot_with_retry()

    # Step 1: fetch the list
    send_before_list = _send_call_count
    post_list = get_post_list_with_retry(bot, BOARD, TARGET_POSTS)
    send_after_list = _send_call_count
    send_for_list = send_after_list - send_before_list

    # Counters
    total_attempted = 0
    total_success = 0
    total_deleted = 0
    total_failed = 0
    total_injected = 0
    failures = []   # list of (index, reason)
    injections = [] # list of (index, snippet)

    send_before_posts = _send_call_count

    print(f'\n[STRESS] Starting to read {len(post_list)} posts ...\n')

    for i, post_meta in enumerate(post_list):
        post_index = post_meta.get('index')
        if post_index is None:
            continue

        total_attempted += 1

        # Progress report every 50 posts
        if total_attempted % 50 == 1:
            elapsed = time.time() - start_time
            sends_so_far = _send_call_count - send_before_posts
            avg_sends = sends_so_far / max(1, total_attempted - 1)
            print(f'  [{total_attempted:4d}/{len(post_list)}] '
                  f'elapsed={elapsed:.0f}s  '
                  f'send()_calls_so_far={sends_so_far}  '
                  f'avg_per_post={avg_sends:.1f}')

        # --- Fetch the post with retry ---
        post = None
        fetch_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                post = bot.get_post(BOARD, index=post_index)
                fetch_error = None
                break
            except (exceptions.ConnectionClosed, exceptions.LoginTooOften) as e:
                wait = 15 * attempt
                print(f'    [RETRY] idx={post_index} {type(e).__name__} — '
                      f'waiting {wait}s and re-logging in')
                time.sleep(wait)
                try:
                    bot.logout()
                except Exception:
                    pass
                bot = create_bot_with_retry()
                fetch_error = str(e)
            except exceptions.NoSuchBoard as e:
                fetch_error = f'NoSuchBoard: {e}'
                break
            except Exception as e:
                fetch_error = f'{type(e).__name__}: {e}'
                # Don't retry on generic errors unless connection-related
                if 'connect' in str(e).lower() or 'closed' in str(e).lower():
                    wait = 15 * attempt
                    time.sleep(wait)
                    try:
                        bot.logout()
                    except Exception:
                        pass
                    bot = create_bot_with_retry()
                else:
                    break

        if fetch_error is not None and post is None:
            total_failed += 1
            failures.append((post_index, fetch_error))
            time.sleep(INTER_POST_SLEEP)
            continue

        # --- Analyse the returned post ---
        if post is None:
            total_failed += 1
            failures.append((post_index, 'get_post returned None unexpectedly'))
            time.sleep(INTER_POST_SLEEP)
            continue

        post_status = post.get('post_status')
        # Deleted / non-existent posts
        if post_status in (
            PyPtt.PostStatus.DELETED_BY_AUTHOR,
            PyPtt.PostStatus.DELETED_BY_MODERATOR,
            PyPtt.PostStatus.DELETED_BY_UNKNOWN,
        ):
            total_deleted += 1
            time.sleep(INTER_POST_SLEEP)
            continue

        # If pass_format_check is False, it's a substandard post — not our bug
        if not post.get('pass_format_check', False):
            total_deleted += 1   # treat as skipped
            time.sleep(INTER_POST_SLEEP)
            continue

        content = post.get('content')

        # Check a: content must exist and be non-empty
        if content is None or content == '':
            total_failed += 1
            failures.append((post_index, 'content is None or empty'))
            time.sleep(INTER_POST_SLEEP)
            continue

        # Check b: must not start with 作者 or 標題 (header injection at the top)
        stripped = content.lstrip('\n')
        if stripped.startswith('作者') or stripped.startswith('標題'):
            total_injected += 1
            snippet = content[:120].replace('\n', '↵')
            injections.append((post_index, f'starts_with_header: {snippet}'))
            # Still count as success for the content-exists check
            total_success += 1
            time.sleep(INTER_POST_SLEEP)
            continue

        # Check c: injection in MIDDLE of body
        if _is_header_injected(content):
            total_injected += 1
            # find the offending line for the report
            lines = content.split('\n')
            for li, ln in enumerate(lines[3:], start=3):
                if ln.startswith('作者 ') or ln.startswith('標題 '):
                    snippet = f'line {li}: {ln[:80]}'
                    break
            else:
                snippet = content[200:320].replace('\n', '↵')
            injections.append((post_index, f'mid_body_injection: {snippet}'))
            total_success += 1
            time.sleep(INTER_POST_SLEEP)
            continue

        # Check d: line count is reasonable
        line_count = content.count('\n') + 1
        if not (1 <= line_count <= 5000):
            total_failed += 1
            failures.append((post_index, f'unreasonable line count: {line_count}'))
            time.sleep(INTER_POST_SLEEP)
            continue

        total_success += 1
        time.sleep(INTER_POST_SLEEP)

    # ─── Final Summary ───────────────────────────────────────────────────────
    elapsed_total = time.time() - start_time
    send_for_posts = _send_call_count - send_before_posts
    send_total = _send_call_count

    print('\n' + '=' * 60)
    print('STRESS TEST SUMMARY')
    print('=' * 60)
    print(f'Board             : {BOARD}')
    print(f'Total elapsed     : {elapsed_total:.1f}s')
    print(f'')
    print(f'Posts attempted   : {total_attempted}')
    print(f'  Successes       : {total_success}')
    print(f'  Deleted/skipped : {total_deleted}')
    print(f'  Failures        : {total_failed}')
    print(f'  Injections      : {total_injected}')
    print(f'')
    print(f'send() calls')
    print(f'  For post list   : {send_for_list}')
    print(f'  For posts       : {send_for_posts}')
    print(f'  Total           : {send_total}')
    if total_success + total_failed > 0:
        avg = send_for_posts / max(1, total_attempted - total_deleted)
        print(f'  Avg per post    : {avg:.2f}')
    print()

    if total_injected > 0:
        print(f'CORRUPTION DETECTED: {total_injected} header-injection case(s)')
        for idx, reason in injections[:20]:
            print(f'  index={idx}: {reason}')
    else:
        print('No content corruption detected.')

    if total_failed > 0:
        print(f'\nFailed posts ({min(20, total_failed)} shown):')
        for idx, reason in failures[:20]:
            print(f'  index={idx}: {reason}')

    print('=' * 60)

    try:
        bot.logout()
    except Exception:
        pass

    # Exit with error code if any corruption or high failure rate
    corruption_or_fail = total_injected > 0 or total_failed > max(50, total_attempted * 0.1)
    sys.exit(1 if corruption_or_fail else 0)


if __name__ == '__main__':
    main()
