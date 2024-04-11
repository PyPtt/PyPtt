import os
import sys
import time

sys.path.append(os.getcwd())

import PyPtt
from tests import util


def test(ptt_bot):
    test_time = 2500
    print(f'效能測試 get_time {test_time} 次')

    start_time = time.time()
    for _ in range(test_time):
        ptt_time = ptt_bot.get_time()

        assert ptt_time is not None

    end_time = time.time()
    print(
        F'Performance Test get_time {end_time - start_time} s')

    print('Performance Test finish')


def func():
    ptt_bot_list = [
        PyPtt.API()]

    for ptt_bot in ptt_bot_list:
        util.login(ptt_bot)

        test(ptt_bot)

        ptt_bot.logout()


if __name__ == '__main__':
    func()
