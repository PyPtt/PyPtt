import os
import sys

sys.path.append(os.getcwd())

import PyPtt
from tests import util


def test(ptt_bot):
    if ptt_bot.host == PyPtt.HOST.PTT1:
        test_list = [
            # comment the newest post
            ('Test', None),
        ]
    else:
        test_list = [
            # comment the newest post
            ('Test', None),
        ]

    for board, post_id in test_list:
        if post_id is None:
            newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, board)

            for i in range(100):
                post_info = ptt_bot.get_post(board, index=newest_index - i)

                # if the post is not deleted, save the post
                if post_info[PyPtt.PostField.post_status] == PyPtt.PostStatus.EXISTS:
                    break

            print('post_id', post_id)
        elif isinstance(post_id, int):
            post_info = ptt_bot.get_post(board, index=post_id, query=True)
        elif isinstance(post_id, str):
            post_info = ptt_bot.get_post(board, aid=post_id, query=True)

        print(post_info)

        # comment by index
        ptt_bot.comment(
            board=board,
            comment_type=PyPtt.CommentType.ARROW,
            content='comment by index',
            index=post_info['index'],
        )

        # comment by aid
        ptt_bot.comment(
            board=board,
            comment_type=PyPtt.CommentType.ARROW,
            content='comment by aid',
            aid=post_info['aid'],
        )


def func():
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2
    ]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LogLevel.DEBUG,
        )
        try:
            util.login(ptt_bot)
            test(ptt_bot)
        finally:
            ptt_bot.logout()

    # assert (result[0] == result[1])


if __name__ == '__main__':
    func()
