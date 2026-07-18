import json
import time

import pytest

import PyPtt
from tests import config
from tests import util


def test_del_own_post(ptt_bots):
    """Tests that a user can delete their own post."""
    for ptt_bot in ptt_bots:
        # 1. Post an article to delete
        post_title = f"PyPtt Delete Test Post {int(time.time())}"
        post_content = "This is a test post for deletion."
        ptt_bot.post(
            board='Test',
            title_index=1,
            title=post_title,
            content=post_content
        )
        time.sleep(1)  # Allow time for post to be indexed

        newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, board='Test')

        # 2. Verify we found our post
        for i in range(5):
            if newest_index - i <= 0:
                continue
            post_data = ptt_bot.get_post('Test', index=newest_index - i)

            if post_data['author'].startswith(ptt_bot.ptt_id):
                break

        assert post_data['author'].startswith(ptt_bot.ptt_id)
        assert post_data['title'] == f"[測試] {post_title}"

        # 3. Delete the post

        for i in range(5):  # Retry up to 3 times in case of transient issues
            if newest_index - i <= 0:
                continue
            try:
                ptt_bot.del_post(board='Test', index=newest_index - i)
            except PyPtt.exceptions.NoPermission:
                pass

        for i in range(5):
            if newest_index - i <= 0:
                continue
            try:
                deleted_post_data = ptt_bot.get_post('Test', index=newest_index - i)
            except PyPtt.exceptions.ParameterError:
                # On a small local board, deleting every remaining post can
                # shrink the board's live index range out from under this
                # stale `newest_index`; an out-of-range index unambiguously
                # means the post is gone, which is what this loop checks for.
                continue

            print(json.dumps(deleted_post_data, ensure_ascii=False, indent=2))

            if deleted_post_data[PyPtt.PostField.post_status] in [
                PyPtt.PostStatus.DELETED_BY_AUTHOR,
                PyPtt.PostStatus.DELETED_BY_MODERATOR,
                PyPtt.PostStatus.DELETED_BY_UNKNOWN
            ]:
                continue

            if deleted_post_data[PyPtt.PostField.author].split(' ')[0] != post_data[PyPtt.PostField.author].split(' ')[
                0]:
                continue

            # author is myself but not deleted
            assert False



def test_del_other_post_permission_error(ptt_bots):
    """Tests that deleting another user's post raises NoPermission."""
    for ptt_bot in ptt_bots:
        # Find a post on a public board not authored by the bot
        board = 'SYSOP'
        newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, board=board)

        target_index = -1
        for i in range(10):  # Check the last 10 posts
            index_to_check = newest_index - i
            if index_to_check <= 0:
                continue
            try:
                post = ptt_bot.get_post(board, index=index_to_check, query=True)
                if post[PyPtt.PostField.post_status] == PyPtt.PostStatus.EXISTS and not post['author'].startswith(
                        ptt_bot.ptt_id):
                    target_index = index_to_check
                    break
            except PyPtt.NoSuchPost:
                continue

        if target_index == -1:
            pytest.skip(f"Could not find a recent post by another user on {board} for host {ptt_bot.host}")

        # 5. Try to delete it and expect a permission error
        with pytest.raises(PyPtt.NoPermission):
            ptt_bot.del_post(board=board, index=target_index)


def test_del_own_post_with_reason_raises(ptt_bots):
    """Passing a reason for your own post is rejected: the annotation only
    applies when a moderator deletes another user's post."""
    for ptt_bot in ptt_bots:
        post_title = f"PyPtt Reason Reject Test {int(time.time())}"
        ptt_bot.post(board='Test', title_index=1, title=post_title,
                     content="This is a test post for deletion.")
        time.sleep(1)

        newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, board='Test')
        index = -1
        for i in range(5):
            if newest_index - i <= 0:
                continue
            post_data = ptt_bot.get_post('Test', index=newest_index - i)
            if post_data['author'].startswith(ptt_bot.ptt_id) and \
                    post_data['title'] == f"[測試] {post_title}":
                index = newest_index - i
                break
        assert index != -1

        # reason on your own post must raise, and must NOT delete it
        with pytest.raises(PyPtt.exceptions.ParameterError):
            ptt_bot.del_post(board='Test', index=index, reason='測試理由')

        # clean up: a plain delete still works
        ptt_bot.del_post(board='Test', index=index)


def test_del_other_post_with_reason_as_moderator(ptt_bots):
    """Tests that a board moderator can delete another user's post and
    annotate a reason on the resulting title."""
    if not config.MOD_BOARD:
        pytest.skip('MOD_BOARD env var not set')
    for ptt_bot in ptt_bots:
        if not util.is_primary_host(ptt_bot, ptt_bots):
            continue  # MOD_BOARD is moderated by the primary bot

        if ptt_bot.host == PyPtt.HOST.LOCALHOST:
            pytest.skip('local imageptt hard-deletes and reindexes moderator '
                        'posts, leaving no DELETED_BY_MODERATOR tombstone to read back')

        board = config.MOD_BOARD
        newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, board=board)

        # Find a recent existing post on MOD_BOARD not authored by the bot.
        target_index = -1
        for i in range(10):
            index_to_check = newest_index - i
            try:
                post = ptt_bot.get_post(board, index=index_to_check, query=True)
                if post[PyPtt.PostField.post_status] == PyPtt.PostStatus.EXISTS and not post['author'].startswith(
                        ptt_bot.ptt_id):
                    target_index = index_to_check
                    break
            except PyPtt.NoSuchPost:
                continue

        if target_index == -1:
            pytest.skip(f"Could not find a recent post by another user on {board} for host {ptt_bot.host}")

        ptt_bot.del_post(board=board, index=target_index, reason='PyPtt 自動測試刪文理由')

        deleted_post = ptt_bot.get_post(board, index=target_index, query=True)
        assert deleted_post[PyPtt.PostField.post_status] == PyPtt.PostStatus.DELETED_BY_MODERATOR


def _post_and_find_aid(ptt_bot, board: str, title: str) -> str:
    """Post a fresh article on `board` and return its AID."""
    ptt_bot.post(board=board, title_index=1, title=title,
                 content="This is a test post for bad-post deletion.")
    time.sleep(1)

    newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, board=board)
    for i in range(10):
        if newest_index - i <= 0:
            continue
        post_data = ptt_bot.get_post(board, index=newest_index - i)
        if post_data[PyPtt.PostField.author].split(' ')[0] != ptt_bot.ptt_id:
            continue

        # Match by containment rather than an exact match against a
        # reconstructed "[TAG] {title}" string: PTT prepends a title-type
        # tag we don't try to reproduce here (and don't hardcode -- just
        # strip whatever precedes the first "] "), and truncates long
        # titles from the right in the listing, so check whichever of
        # {title, stored body} is a prefix of the other instead of
        # requiring exact equality.
        stored_title = post_data[PyPtt.PostField.title]
        body = stored_title.split('] ', 1)[-1] if '] ' in stored_title else stored_title
        if body and (title.startswith(body) or body.startswith(title)):
            return post_data[PyPtt.PostField.aid]
    raise AssertionError('posted article not found')


def test_own_post_with_bad_post_type_raises(ptt_bots):
    """Passing bad_post_type for your own post is rejected: like `reason`,
    a bad-post strike only applies when a moderator deletes another user's
    post.

    This must exercise the "moderator deleting their *own* post" half of
    that check, not the "not a moderator at all" half: on 'Test' (where
    neither bot moderates), check_author is already True regardless of
    authorship, so a ParameterError there is a vacuous pass -- it doesn't
    prove the own-post branch of the check works. PyPttMod (LOCALHOST-only
    bootstrap board, moderated by pypttbot1) lets a real moderator delete
    their own post and hit that branch specifically."""
    ptt1_bot, ptt2_bot = ptt_bots
    if ptt1_bot.host != PyPtt.HOST.LOCALHOST:
        pytest.skip('needs a board the bot actually moderates; only the LOCALHOST '
                    'bootstrap provisions one (PyPttMod, moderated by pypttbot1)')
    if not config.MOD_BOARD:
        pytest.skip('MOD_BOARD env var not set')
    if not util.is_primary_host(ptt1_bot, ptt_bots):
        pytest.skip('MOD_BOARD is moderated by the primary bot')

    board = config.MOD_BOARD
    post_title = f"PyPtt BadPost Own Mod Post Test {int(time.time())}"
    aid = _post_and_find_aid(ptt1_bot, board, post_title)

    with pytest.raises(PyPtt.exceptions.ParameterError):
        ptt1_bot.del_post(board=board, aid=aid, bad_post_type=PyPtt.BadPostType.AD)

    # clean up: a plain delete still works
    ptt1_bot.del_post(board=board, aid=aid)


def test_bad_post_other_without_reason_raises(ptt_bots):
    """BadPostType.OTHER requires bad_post_reason to be supplied."""
    ptt1_bot, ptt2_bot = ptt_bots
    if ptt1_bot.host != PyPtt.HOST.LOCALHOST:
        pytest.skip('real PTT two-host setup cannot exercise this (poster is on PTT2, '
                    'board lives on PTT1); run against local imageptt (PTT_HOST=LOCALHOST)')

    if not config.MOD_BOARD:
        pytest.skip('MOD_BOARD env var not set')

    if not util.is_primary_host(ptt1_bot, ptt_bots):
        pytest.skip('MOD_BOARD is moderated by the primary bot')

    board = config.MOD_BOARD
    title = f"PyPtt BadPost Other Test {int(time.time())}"
    post_aid = _post_and_find_aid(ptt2_bot, board, title)

    with pytest.raises(PyPtt.exceptions.ParameterError):
        ptt1_bot.del_post(board=board, aid=post_aid, bad_post_type=PyPtt.BadPostType.OTHER)

    # clean up: the post must still be there (the error is raised before any
    # deletion happens), delete it without a bad-post strike this time.
    ptt1_bot.del_post(board=board, aid=post_aid)


def test_bad_post(ptt_bots):
    """A moderator deleting another user's post with bad_post_type records a
    bad-post (illegal_post/退) strike against the author. Unlike the R-reason
    test above, this isn't skipped for that reason on LOCALHOST: it asserts
    on the author's illegal_post counter, not on a DELETED_BY_MODERATOR
    tombstone title, so imageptt's hard-delete-and-reindex behaviour doesn't
    interfere. It *is* LOCALHOST-only for a different reason: covering
    BadPostType.OTHER's full flow (menu selection + the "請輸入原因" prompt)
    needs the poster and the MOD_BOARD moderator on the same host, which
    real PTT's PTT1/PTT2 split can never provide (the poster would need to
    be on PTT2 while MOD_BOARD lives on PTT1).

    Runs last in this module by design: pttbbs's real badpost penalty also
    temporarily bans the author from posting anywhere (~1 hour on imageptt),
    so applying it earlier would break every other test in this file that
    needs TEST_USER (the moderator-owned MOD_BOARD's non-moderator poster)
    to post. Both articles below are posted up front, before either
    bad-post call (and its posting ban) can land."""
    ptt1_bot, ptt2_bot = ptt_bots
    if ptt1_bot.host != PyPtt.HOST.LOCALHOST:
        pytest.skip('real PTT two-host setup cannot exercise this; run against local imageptt')

    if not config.MOD_BOARD:
        pytest.skip('MOD_BOARD env var not set')

    if not util.is_primary_host(ptt1_bot, ptt_bots):
        pytest.skip('MOD_BOARD is moderated by the primary bot')

    board = config.MOD_BOARD
    title_ad = f"PyPtt Bad Post AD Test {int(time.time())}"
    title_other = f"PyPtt Bad Post OTHER Test {int(time.time())}"

    aid_ad = _post_and_find_aid(ptt2_bot, board, title_ad)
    aid_other = _post_and_find_aid(ptt2_bot, board, title_other)

    baseline = ptt1_bot.get_user(config.TEST_USER)[PyPtt.UserField.illegal_post] or 0

    ptt1_bot.del_post(board=board, aid=aid_ad, bad_post_type=PyPtt.BadPostType.AD)

    after_ad = ptt1_bot.get_user(config.TEST_USER)[PyPtt.UserField.illegal_post]
    assert after_ad == baseline + 1

    ptt1_bot.del_post(board=board, aid=aid_other, bad_post_type=PyPtt.BadPostType.OTHER,
                       bad_post_reason='測試用理由')

    after_other = ptt1_bot.get_user(config.TEST_USER)[PyPtt.UserField.illegal_post]
    assert after_other == baseline + 2
