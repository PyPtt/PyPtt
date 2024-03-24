import os
import sys

sys.path.append(os.getcwd())

import PyPtt
from tests import util


def test(ptt_bot: PyPtt.API):

    result = ptt_bot.get_bottom_post_list('Test')

    print(result)

def func():
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2
    ]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LogLevel.TRACE,
        )

        try:
            util.login(ptt_bot)
            test(ptt_bot)
        finally:
            ptt_bot.logout()


if __name__ == '__main__':
    func()
