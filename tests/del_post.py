import os
import sys

sys.path.append(os.getcwd())

import PyPtt
from tests import util


def test(ptt_bot: PyPtt.API):
    ptt_bot.post(board='Test', title_index=1, title='PyPtt 程式貼文測試', content='測試內文', sign_file=0)

    newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, 'Test')

    for i in range(10):
        ptt_bot.get_post(board='Test', index=newest_index - i)


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


if __name__ == '__main__':
    func()
