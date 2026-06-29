import json
import time

import pytest

import PyPtt
from tests import config


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
            post_data = ptt_bot.get_post('Test', index=newest_index - i)

            if post_data['author'].startswith(ptt_bot.ptt_id):
                break

        assert post_data['author'].startswith(ptt_bot.ptt_id)
        assert post_data['title'] == f"[測試] {post_title}"

        # 3. Delete the post

        for i in range(5):  # Retry up to 3 times in case of transient issues
            try:
                ptt_bot.del_post(board='Test', index=newest_index - i)
            except PyPtt.exceptions.NoPermission:
                pass

        for i in range(5):
            deleted_post_data = ptt_bot.get_post('Test', index=newest_index - i)

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


def test_del_other_post_with_reason_as_moderator(ptt_bots):
    """Tests that a board moderator can delete another user's post and
    annotate a reason on the resulting title."""
    if not config.MOD_BOARD:
        pytest.skip('MOD_BOARD env var not set')
    for ptt_bot in ptt_bots:
        if ptt_bot.host != PyPtt.HOST.PTT1:
            continue  # MOD_BOARD is a PTT1 board

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
