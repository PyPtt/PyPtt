#!/usr/bin/env python3
"""One-shot provisioning for a local pttbbs (`bbsdocker/imageptt`) container
so PyPtt's integration test suite (`tests/`) can run against it end-to-end.

The container has no persistent volume — every restart resets `.PASSWDS`,
`.BRD`, and all boards/posts — so this script is meant to be re-run after
every `docker run` / `podman run` (or restart) and tolerates already-applied
state (accounts get overwritten, boards get updated in place, seed posts are
best-effort and skip past "already exists"-style errors).

Usage:
    CONTAINER_TOOL=podman python scripts/bootstrap_local_pttbbs.py [container_name]

    container_name   Defaults to "pyptt-test".
    CONTAINER_TOOL    "docker" (default) or "podman".

Steps:
    (a) generate `.PASSWDS` for pypttbot1 / pypttbot2 / CodingMan and load it
        into the container via `uhash_loader`.
    (b) create boards Test / Python / Announce (no moderator) and PyPttMod
        (moderated by pypttbot1), then reload the board + BM shm caches.
    (c) log in via this repo's PyPtt (host=LOCALHOST) and seed the data the
        test suite reads: a post on Test and on Python by each bot, a
        self-mail for each bot (so `get_newest_index(NewIndex.MAIL) > 0`),
        and a PyPttMod post authored by pypttbot2 (a non-BM author, needed by
        `test_del_post.py::test_del_other_post_with_reason_as_moderator`).

See CLAUDE.md, "Testing against a local pttbbs", for the full workflow
(including which env vars to set when running `pytest tests/` afterwards).
"""
import os
import subprocess
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTAINER_TOOL = os.environ.get('CONTAINER_TOOL', 'docker')

ACCOUNTS = [
    ('pypttbot1', 'test1234'),
    ('pypttbot2', 'test5678'),
    ('CodingMan', 'coding123'),
    # A second "Coding"-prefixed account: search_user()'s screen parser only
    # handles the multi-match listing format, not the single-match
    # auto-complete prompt this imageptt build renders for a lone hit — see
    # tests/test_search_user.py. Having two matches keeps it on the
    # already-working code path without touching PyPtt/_api_search_user.py.
    ('CodingMan2', 'coding123'),
]

# Shared across every seeded board so title_index=1 always selects "測試"
# (the PTT convention tests assert on, e.g. `f"[測試] {title}"`) instead of
# misaligning the post-composer keystrokes on boards with no post-type list.
POST_TYPES = '測試,問題,心得,閒聊,公告,其他'

# (board, moderator_id, post_types)
BOARDS = [
    ('Test', '', POST_TYPES),
    ('Python', '', POST_TYPES),
    ('Announce', '', POST_TYPES),
    ('PyPttMod', 'pypttbot1', POST_TYPES),
]


def run(*args):
    print('+', ' '.join(args))
    subprocess.run(args, check=True)


def container_exec(container, *args, user=None, cwd=None):
    cmd = [CONTAINER_TOOL, 'exec']
    if user:
        cmd += ['-u', user]
    if cwd:
        cmd += ['-w', cwd]
    cmd += [container, *args]
    run(*cmd)


def step_accounts(container):
    print('--- (a) accounts ---')
    gen_script = os.path.join(REPO_ROOT, 'scripts', 'gen_local_passwds.py')
    passwds_path = os.path.join(REPO_ROOT, '.PASSWDS')
    pairs = [f'{uid}:{pw}' for uid, pw in ACCOUNTS]
    with open(passwds_path, 'wb') as f:
        subprocess.run([sys.executable, gen_script, *pairs], check=True, stdout=f)

    try:
        run(CONTAINER_TOOL, 'cp', passwds_path, f'{container}:/home/bbs/.PASSWDS')
        container_exec(container, 'sh', '-c',
                        'chown bbs:bbs /home/bbs/.PASSWDS && chmod 644 /home/bbs/.PASSWDS')
        container_exec(container, './bin/uhash_loader', user='bbs', cwd='/home/bbs')
    finally:
        os.remove(passwds_path)


def step_boards(container):
    print('--- (b) boards ---')
    mkboard_script = os.path.join(REPO_ROOT, 'scripts', 'mkboard.py')
    run(CONTAINER_TOOL, 'cp', mkboard_script, f'{container}:/home/bbs/mkboard.py')
    for board, moderator, post_types in BOARDS:
        container_exec(container, '/usr/bin/python3', 'mkboard.py', board, moderator, post_types,
                        user='bbs', cwd='/home/bbs')
    container_exec(container, './bin/shmctl', 'reloadbcache', user='bbs', cwd='/home/bbs')
    container_exec(container, './bin/shmctl', 'bBMC', user='bbs', cwd='/home/bbs')


def step_seed_data():
    print('--- (c) seed data ---')
    sys.path.insert(0, REPO_ROOT)
    import PyPtt

    def login(ptt_id, ptt_pw):
        bot = PyPtt.API(host=PyPtt.HOST.LOCALHOST, log_level=PyPtt.LOG_LEVEL.SILENT)
        bot.login(ptt_id=ptt_id, ptt_pw=ptt_pw, kick_other_session=True)
        return bot

    bots = [login(uid, pw) for uid, pw in ACCOUNTS[:2]]

    try:
        for bot in bots:
            for board in ('Test', 'Python'):
                try:
                    bot.post(board=board, title_index=1,
                             title=f'PyPtt seed post ({bot.ptt_id})',
                             content='Seed content for PyPtt local integration tests.\n',
                             sign_file=0)
                    print(f'  posted to {board} as {bot.ptt_id}')
                except Exception as e:
                    print(f'  post to {board} by {bot.ptt_id} skipped: {e}')

            try:
                bot.mail(ptt_id=bot.ptt_id, title='PyPtt seed mail',
                         content='Seed mail for PyPtt local integration tests.\n',
                         sign_file=0, backup=False)
                print(f'  mailed self as {bot.ptt_id}')
            except Exception as e:
                print(f'  mail to self by {bot.ptt_id} skipped: {e}')

        # A PyPttMod post NOT authored by pypttbot1 (the board's moderator),
        # for test_del_post.py::test_del_other_post_with_reason_as_moderator.
        try:
            bots[1].post(board='PyPttMod', title_index=1,
                         title='PyPtt seed post (non-moderator author)',
                         content='Seed content for the moderator del-post test.\n',
                         sign_file=0)
            print('  posted to PyPttMod as pypttbot2')
        except Exception as e:
            print(f'  post to PyPttMod by pypttbot2 skipped: {e}')
    finally:
        for bot in bots:
            try:
                bot.logout()
            except Exception:
                pass


def main():
    container = sys.argv[1] if len(sys.argv) > 1 else 'pyptt-test'
    step_accounts(container)
    step_boards(container)
    time.sleep(1)  # let shmctl's background bottom-post load settle
    step_seed_data()
    print('bootstrap done.')


if __name__ == '__main__':
    main()
