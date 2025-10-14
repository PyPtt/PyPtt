import time

import pytest

import PyPtt
from PyPtt import PostField, log, CommentType, PostStatus, NewIndex
from tests import util


def test_post_and_comment(ptt_bots):
    """Tests posting, commenting, and verifying the post content."""
    for ptt_bot in ptt_bots:
        content = '''
此為 PyPtt 貼文測試內容，如有打擾請告知。
官方網站: https://pyptt.cc

測試標記
781d16268c9f25a39142a17ff063ac029b1466ca14cb34f5d88fe8aadfeee053
'''

        temp = ''
        for i in range(100):
            content = f'{content}\n={i}='
            temp = f'{temp}\n={i}='

        check_ = [
            '781d16268c9f25a39142a17ff063ac029b1466ca14cb34f5d88fe8aadfeee053',
            temp
        ]

        check_range = 3

        for _ in range(check_range):
            ptt_bot.post(board='Test', title_index=1, title='PyPtt 程式貼文測試', content=content, sign_file=0)

        time.sleep(1)

        newest_index = ptt_bot.get_newest_index(index_type=NewIndex.BOARD, board='Test')

        # find post what we post
        post_list = []
        for i in range(10):
            post = ptt_bot.get_post(board='Test', index=newest_index - i)

            if post[PostField.post_status] != PostStatus.EXISTS:
                continue

            post_author = post[PostField.author].split(' ')[0]
            if post_author != ptt_bot.ptt_id:
                continue

            post_list.append(newest_index - i)
            if len(post_list) == check_range:
                break

        assert len(post_list) == check_range, "Could not find all posted articles."

        comment_check = []
        for i in range(5):
            comment_check.append(f'={i}=')
            ptt_bot.comment(board='Test', comment_type=CommentType.ARROW, content=f'={i}=', index=post_list[0])
        comment_check = list(set(comment_check))

        time.sleep(1)

        for i, index in enumerate(post_list):

            log.logger.info('test', i)

            post = ptt_bot.get_post(board='Test', index=index)

            assert post[PostField.post_status] == PostStatus.EXISTS, f"Post {index} not exists"

            post_author = post[PostField.author].split(' ')[0]
            assert post_author == ptt_bot.ptt_id, f"Post {index} author not match"

            for c in check_:
                assert c in post[PostField.content], f"Post {index} content not match"

            # Only check comments on the first post
            if i == 0:
                cur_comment_check = {comment[PyPtt.CommentField.content] for comment in post[PostField.comments]}
                assert len(cur_comment_check.intersection(comment_check)) == len(comment_check), f"Post {index} comment not match"

            log.logger.info('pass')
