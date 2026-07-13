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
        if post_data[PyPtt.PostField.author].split(' ')[0] == ptt_bot.ptt_id and \
                post_data[PyPtt.PostField.title] == f"[測試] {title}":
            return post_data[PyPtt.PostField.aid]
    raise AssertionError('posted article not found')


def test_own_post_with_bad_post_type_raises(ptt_bots):
    """Passing bad_post_type for your own post is rejected: like `reason`,
    a bad-post strike only applies when a moderator deletes another user's
    post."""
    for ptt_bot in ptt_bots:
        post_title = f"PyPtt BadPost Reject Test {int(time.time())}"
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

        with pytest.raises(PyPtt.exceptions.ParameterError):
            ptt_bot.del_post(board='Test', index=index, bad_post_type=PyPtt.BadPostType.AD)

        # clean up: a plain delete still works
        ptt_bot.del_post(board='Test', index=index)


def test_bad_post_other_without_reason_raises(ptt_bots):
    """BadPostType.OTHER requires bad_post_reason to be supplied."""
    if not config.MOD_BOARD:
        pytest.skip('MOD_BOARD env var not set')

    ptt1_bot, ptt2_bot = ptt_bots
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
    test above, this isn't skipped on LOCALHOST: it asserts on the author's
    illegal_post counter, not on a DELETED_BY_MODERATOR tombstone title, so
    imageptt's hard-delete-and-reindex behaviour doesn't interfere.

    Runs last in this module by design: pttbbs's real badpost penalty also
    temporarily bans the author from posting anywhere (~1 hour on imageptt),
    so applying it earlier would break every other test in this file that
    needs TEST_USER (the moderator-owned MOD_BOARD's non-moderator poster)
    to post."""
    if not config.MOD_BOARD:
        pytest.skip('MOD_BOARD env var not set')

    ptt1_bot, ptt2_bot = ptt_bots
    if not util.is_primary_host(ptt1_bot, ptt_bots):
        pytest.skip('MOD_BOARD is moderated by the primary bot')

    board = config.MOD_BOARD
    title = f"PyPtt Bad Post Test {int(time.time())}"
    post_aid = _post_and_find_aid(ptt2_bot, board, title)

    baseline = ptt1_bot.get_user(config.TEST_USER)[PyPtt.UserField.illegal_post] or 0

    ptt1_bot.del_post(board=board, aid=post_aid, bad_post_type=PyPtt.BadPostType.AD)

    after = ptt1_bot.get_user(config.TEST_USER)[PyPtt.UserField.illegal_post]
    assert after == baseline + 1
