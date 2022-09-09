import time

import PyPtt
import config
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
    current_id = config.PTT1_ID if ptt_bot.host == PyPtt.HOST.PTT1 else config.PTT2_ID

    for _ in range(check_range):
        ptt_bot.post(board='Test', title_index=1, title='PyPtt 程式貼文測試', content=content, sign_file=0)

    time.sleep(1)

    newest_index = ptt_bot.get_newest_index(index_type=PyPtt.NewIndex.BOARD, board='Test')

    check_count = 0
    for i in range(10):
        post = ptt_bot.get_post(board='Test', index=newest_index - i)

        if post[PostField.post_status] != PyPtt.PostStatus.EXISTS:
            print(f'Post {newest_index - i} not exists')
            continue

        post_author = post[PostField.author]
        post_author = post_author.split(' ')[0]
        if post_author != current_id:
            print(f'Post {newest_index - i} author not match', post_author)
            continue

        util.logger.info('test ', check_count)

        check = True
        for c in check_:
            if c not in post[PostField.content]:
                check = False
                break
        util.logger.stage('pass' if check else 'fail')

        ptt_bot.del_post(board='Test', index=newest_index - i)

        check_count += 1
        if check_count == check_range:
            break


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

        ptt_bot.logout()


if __name__ == '__main__':
    func()
