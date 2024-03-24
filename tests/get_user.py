import json
import os
import sys

sys.path.append(os.getcwd())

import PyPtt
from PyPtt import log
from tests import util


def test(ptt_bot: PyPtt.API):
    test_users = [
        'CodingMan',
    ]

    for test_user in test_users:
        user_info = ptt_bot.get_user(test_user)

        print(json.dumps(user_info, indent=4, ensure_ascii=False))


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
