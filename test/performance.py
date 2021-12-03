import time

from SingleLog.log import Logger

import PyPtt
import util

from PyPtt_0_9 import PTT


def performance_test(ptt_bot):
    test_time = 500
    logger.info(f'效能測試 get_time {test_time} 次')

    start_time = time.time()
    for _ in range(test_time):
        ptt_time = ptt_bot.get_time()

        # if ptt_time is None:
        #     logger.info('PTT_TIME is None')
        #     break
        # logger.info(ptt_time)
    end_time = time.time()
    logger.info('Performance Test get_time ' +
                str(round(end_time - start_time, 2)) + ' s')

    ptt_bot.logout()

    logger.info('Performance Test finish')


def func():

    ptt_bot_list = [
        PyPtt.API(),
        PTT.API()]

    for ptt_bot in ptt_bot_list:
        util.login(ptt_bot)

        performance_test(ptt_bot)

        ptt_bot.logout()


if __name__ == '__main__':
    logger = Logger('TEST')
    func()
