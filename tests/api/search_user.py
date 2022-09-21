import json

import PyPtt
from tests import util


def test(ptt_bot: PyPtt.API):
    test_users = [
        'Coding',
    ]

    for test_user in test_users:
        result = ptt_bot.search_user(test_user)

        # print(json.dumps(user_info, indent=4, ensure_ascii=False))
        util.logger.info('result', result)


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
        try:
            util.login(ptt_bot)

            test(ptt_bot)

            ptt_bot.logout()
        finally:
            ptt_bot.logout()


if __name__ == '__main__':
    func()
