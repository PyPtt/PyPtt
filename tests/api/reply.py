import time

import PyPtt
from PyPtt import PostField
from tests import util

current_id = None


def test(ptt_bot: PyPtt.API):
    ptt_bot.post(board='Test', title_index=1, title='PyPtt 程式貼文測試', content='測試內文', sign_file=0)

    time.sleep(1)

    newest_index = ptt_bot.get_newest_index(index_type=PyPtt.NewIndex.BOARD, board='Test')

    for i in range(5):
        cur_post = ptt_bot.get_post(board='Test', index=newest_index - i)

        if cur_post[PostField.post_status] != PyPtt.PostStatus.EXISTS:
            continue

        cur_author = cur_post[PostField.author]
        cur_author = cur_author.split(' ')[0]
        if cur_author.lower() != ptt_bot.ptt_id.lower():
            continue

        ptt_bot.reply_post(
            reply_to=PyPtt.ReplyTo.BOARD, board='Test', index=newest_index - i, content='PyPtt 程式回覆測試')

        break
    newest_index += 1

    time.sleep(1)

    posts = []

    # 在十篇範圍內找尋我們的文章
    for i in range(10):
        cur_post = ptt_bot.get_post(board='Test', index=newest_index - i)

        if cur_post[PostField.post_status] != PyPtt.PostStatus.EXISTS:
            continue

        cur_author = cur_post[PostField.author]
        cur_author = cur_author.split(' ')[0]
        if cur_author.lower() != ptt_bot.ptt_id.lower():
            continue

        posts.append(cur_post[PostField.aid])

    util.logger.info('test')
    if len(posts) < 2:
        util.logger.info('len(posts) < 2, fail')
        return

    check = [
        '[測試] PyPtt 程式貼文測試',
        'Re: [測試] PyPtt 程式貼文測試'
    ]

    check_result = True
    for aid in posts:
        post = ptt_bot.get_post(board='Test', aid=aid)

        if post[PostField.post_status] != PyPtt.PostStatus.EXISTS:
            util.logger.info('post[PostField.post_status] != PyPtt.PostStatus.EXISTS, fail')
            check_result = False
            break

        if post[PostField.title] not in check:
            util.logger.info('post[PostField.title] not in check, fail')
            check_result = False
            break

        check.remove(post[PostField.title])

    if check_result:
        util.logger.info('pass')
    else:
        util.logger.info('fail')

    util.del_all_post(ptt_bot)


def func():
    global current_id
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2
    ]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LogLevel.TRACE,
        )
        util.login(ptt_bot)

        test(ptt_bot)

        ptt_bot.logout()


if __name__ == '__main__':
    func()
