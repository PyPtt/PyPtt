import time
from tests import util

import PyPtt
from PyPtt_0_9 import PTT


def test(ptt_bot):
    test_time = 500
    util.logger.info(f'效能測試 get_time {test_time} 次')

    start_time = time.time()
    for _ in range(test_time):
        ptt_time = ptt_bot.get_time()

        assert ptt_time is not None

        # if ptt_time is None:
        #     util.logger.info('PTT_TIME is None')
        #     break
        # util.logger.info(ptt_time)
    end_time = time.time()
    util.logger.info(
        F'Performance Test get_time {end_time - start_time} s')

    util.logger.info('Performance Test finish')


def func():

    ptt_bot_list = [
        PyPtt.API(),
        PTT.API()]

    for ptt_bot in ptt_bot_list:
        util.login(ptt_bot)

        test(ptt_bot)

        ptt_bot.logout()


if __name__ == '__main__':
    func()
