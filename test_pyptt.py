import sys

import PyPtt
from tests import util
from tests.api import get_time, get_post, get_newest_index, post
from tests.basic import init, login_logout, performance


def test():
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2]

    init.test()

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LOG_LEVEL.TRACE,
        )
        util.login(ptt_bot)

        # performance.test(ptt_bot)

        get_time.test(ptt_bot)
        post.test(ptt_bot)

        ptt_bot.logout()


# if __name__ == '__main__':
#     test()
