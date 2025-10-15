import json
import time

import pytest

import PyPtt


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
