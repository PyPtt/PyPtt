import json
import random

import PyPtt
import pytest
import time

def test_comment(ptt_bots):
    """
    Tests commenting on a post on both PTT1 and PTT2.
    """
    for ptt_bot in ptt_bots:
        if ptt_bot.host == PyPtt.HOST.PTT1:
            test_list = [('Test', None)]
        else:
            test_list = [('Test', None)]

        for board, post_id in test_list:
            post_info = None
            if post_id is None:
                try:
                    newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, board)
                    for i in range(100):

                        current_post = ptt_bot.get_post(board, index=newest_index - i)
                        if current_post and current_post.get(PyPtt.PostField.post_status) == PyPtt.PostStatus.EXISTS:
                            post_info = current_post
                            break
                except PyPtt.NoSearchResult:
                    pytest.skip(f"Board '{board}' seems to be empty, skipping comment test.")

            elif isinstance(post_id, int):
                post_info = ptt_bot.get_post(board, index=post_id, query=True)
            elif isinstance(post_id, str):
                post_info = ptt_bot.get_post(board, aid=post_id, query=True)

            if not post_info or post_info.get(PyPtt.PostField.post_status) != PyPtt.PostStatus.EXISTS:
                pytest.skip(f"Could not find a suitable post to comment on in board '{board}'.")

            # Test comment by index
            try:
                ptt_bot.comment(
                    board=board,
                    comment_type=PyPtt.CommentType.ARROW,
                    content='PyPtt comment test by index',
                    index=post_info['index'],
                )
            except PyPtt.NoPermission as e:
                pytest.fail(f"Failed to comment by index on {ptt_bot.host}: {e}")

            # The API might have a cooldown
            time.sleep(5)

            # Test comment by aid
            try:
                ptt_bot.comment(
                    board=board,
                    comment_type=PyPtt.CommentType.ARROW,
                    content='PyPtt comment test by AID',
                    aid=post_info['aid'],
                )
            except PyPtt.NoPermission as e:
                pytest.fail(f"Failed to comment by AID on {ptt_bot.host}: {e}")
            except PyPtt.NoFastComment:
                # If we hit this, the first comment was successful.
                # We can consider this a pass for the second comment attempt under cooldown.
                pass

            print(json.dumps(post_info, indent=2, ensure_ascii=False))

            for i in range(5):
                ptt_bot.comment(
                    board=board,
                    comment_type=PyPtt.CommentType.ARROW,
                    content=f'PyPtt comment test {i}',
                    index=post_info['index'],
                )

            post_info = ptt_bot.get_post(
                board=board, aid=post_info['aid']
            )

            check_count = 0
            check_target = ['PyPtt comment test by index', 'PyPtt comment test by AID']
            check_target.extend(
                [f'PyPtt comment test {i}' for i in range(5)]
            )

            for comment in post_info.get(PyPtt.PostField.comments, [])[-len(check_target):]:
                print('checking comment:', comment)
                if comment.get('content') in check_target:
                    check_count += 1

            assert check_count == len(check_target), f"Not all comments found in post on {ptt_bot.host}."