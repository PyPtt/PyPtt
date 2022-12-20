import time

import PyPtt

from PyPtt import PostField
from tests import util


def test(ptt_bot: PyPtt.API):
    content = '''
此為 PyPtt 貼文測試內容，如有打擾請告知。
github: https://github.com/PttCodingMan/PyPtt

開發手冊: https://github.com/PttCodingMan/PyPtt/tree/master/doc

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

    newest_index = ptt_bot.get_newest_index(index_type=PyPtt.NewIndex.BOARD, board='Test')

    # find post what we post
    post_list = []
    for i in range(10):
        post = ptt_bot.get_post(board='Test', index=newest_index - i)

        if post[PostField.post_status] != PyPtt.PostStatus.EXISTS:
            print(f'Post {newest_index - i} not exists')
            continue

        post_author = post[PostField.author]
        post_author = post_author.split(' ')[0]
        if post_author != ptt_bot.ptt_id:
            print(f'Post {newest_index - i} author not match', post_author)
            continue

        post_list.append(newest_index - i)
        if len(post_list) == check_range:
            break

    comment_check = []
    for index in post_list:
        for i in range(5):
            comment_check.append(f'={i}=')
            ptt_bot.comment(board='Test', comment_type=PyPtt.CommentType.ARROW, content=f'={i}=', index=index)
    comment_check = list(set(comment_check))

    time.sleep(1)

    for i, index in enumerate(post_list):

        util.logger.info('test', i)

        post = ptt_bot.get_post(board='Test', index=index)

        if post[PostField.post_status] != PyPtt.PostStatus.EXISTS:
            util.logger.info('fail')
            print(f'Post {index} not exists')
            break

        post_author = post[PostField.author]
        post_author = post_author.split(' ')[0]
        if post_author != ptt_bot.ptt_id:
            util.logger.info('fail')
            print(f'Post {index} author not match', post_author)
            break

        check = True
        for c in check_:
            if c not in post[PostField.content]:
                check = False
                break
        if not check:
            util.logger.info('fail')
            print(f'Post {index} content not match')
            break

        cur_comment_check = set()
        for comment in post[PostField.comments]:

            if comment[PyPtt.CommentField.content] in comment_check:
                cur_comment_check.add(comment[PyPtt.CommentField.content])
            else:
                util.logger.info('comment', comment[PyPtt.CommentField.content])

        if len(cur_comment_check) != len(comment_check):
            util.logger.info('fail')
            print(f'Post {index} comment not match')
            break

        util.logger.info('pass')

    for index in post_list:
        ptt_bot.del_post(board='Test', index=index)


def func():
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2
    ]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LOG_LEVEL.TRACE,
        )
        util.login(ptt_bot)

        test(ptt_bot)
        # util.del_all_post(ptt_bot)

        ptt_bot.logout()


if __name__ == '__main__':
    func()
