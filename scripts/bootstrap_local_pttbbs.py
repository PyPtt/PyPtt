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
    (b) create boards Test / Python / Announce (no moderator), PyPttMod
        (moderated by pypttbot1), and AnonTest (BRD_ANONYMOUS +
        BRD_DEFAULTANONYMOUS, for tests/test_post_anonymous.py), then
        reload the board + BM shm caches.
    (c) log in via this repo's PyPtt (host=LOCALHOST) and seed the data the
        test suite reads: a post on Test and on Python by each bot, a
        self-mail for each bot (so `get_newest_index(NewIndex.MAIL) > 0`),
        a cross-push of pypttbot2's Python post by pypttbot1 (so
        SearchType.COMMENT searches have a match), and a PyPttMod post
        authored by pypttbot2 (a non-BM author, needed by
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

# (board, moderator_id, post_types[, anon_mode]) -- anon_mode defaults to ''
# (not anonymous) when omitted; see scripts/mkboard.py's docstring.
BOARDS = [
    ('Test', '', POST_TYPES),
    ('Python', '', POST_TYPES),
    ('Announce', '', POST_TYPES),
    ('PyPttMod', 'pypttbot1', POST_TYPES),
    # BRD_ANONYMOUS + BRD_DEFAULTANONYMOUS: an Enter response to the "請輸入
    # 你想用的ID" prompt deterministically resolves to "Anonymous." here, which
    # is what tests/test_post_anonymous.py (issue #84) relies on.
    ('AnonTest', '', POST_TYPES, 'defanon'),
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
    for board_spec in BOARDS:
        board, moderator, post_types, *anon_mode = board_spec
        args = [board, moderator, post_types, *anon_mode]
        container_exec(container, '/usr/bin/python3', 'mkboard.py', *args,
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

        # Cross-push pypttbot2's 'Python' article so LOCALHOST-only tests that
        # search by push count (SearchType.COMMENT, e.g.
        # test_get_newest_index.py) have at least one match. Self-push is
        # disallowed by default, so pypttbot1 pushes pypttbot2's post rather
        # than its own -- which means it must find a post actually authored
        # by pypttbot2, not just "the newest post on the board": if
        # pypttbot2's post above silently failed on some run, the newest post
        # could be pypttbot1's own, and pushing that would be a self-push
        # PTT rejects. This intentionally isn't wrapped in a broad
        # try/except: this seed is a hard prerequisite for the COMMENT-search
        # tests, so a failure here should fail bootstrap loudly (non-zero
        # exit) rather than silently leave the suite without it. Safe to
        # re-run: pttbbs allows repeat pushes from the same user on the same
        # article, so this just adds another push line -- the match count
        # only ever grows, never shrinks or errors.
        python_newest = bots[0].get_newest_index(PyPtt.NewIndex.BOARD, board='Python')
        pypttbot2_index = None
        for i in range(10):
            index_to_check = python_newest - i
            if index_to_check <= 0:
                break
            post = bots[0].get_post('Python', index=index_to_check, query=True)
            if post[PyPtt.PostField.author].split(' ')[0] == bots[1].ptt_id:
                pypttbot2_index = index_to_check
                break
        if pypttbot2_index is None:
            raise RuntimeError(
                f"couldn't find a Python-board post authored by {bots[1].ptt_id} to "
                "cross-push (needed for SearchType.COMMENT tests)")
        bots[0].comment(board='Python', comment_type=PyPtt.CommentType.PUSH,
                         content='cross-push for PyPtt LOCALHOST search tests',
                         index=pypttbot2_index)
        print(f'  pushed Python #{pypttbot2_index} (post by {bots[1].ptt_id}) as {bots[0].ptt_id}')

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
