import time

import PyPtt
from tests import util


def test(ptt_bot: PyPtt.API):
    util.login(ptt_bot, kick=True)
    ptt_bot.logout()

    max_wait_time = 5
    for sec in range(max_wait_time):
        util.logger.info('wait', max_wait_time - sec)
        time.sleep(1)

    util.login(ptt_bot, kick=False)
    ptt_bot.logout()


def func():
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LOG_LEVEL.TRACE,
        )
        test(ptt_bot)

    util.logger.info('login logout test ok')


if __name__ == '__main__':
    func()
