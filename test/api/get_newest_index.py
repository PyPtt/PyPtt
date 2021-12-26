import time

import PyPtt
import util


def test(ptt_bot: PyPtt.API):
    if ptt_bot.host == PyPtt.HOST.PTT1:
        test_board = [
            'Gossiping',
            'Wanted'
        ]
    else:
        test_board = [
            'WhoAmI',
        ]
    for board in test_board:
        for _ in range(3):
            index = ptt_bot.get_newest_index(
                PyPtt.NewIndex.BBS,
                board)
            util.logger.info(f'{board} newest index', index)

    for _ in range(3):
        index = ptt_bot.get_newest_index(PyPtt.NewIndex.MAIL)
        util.logger.info(f'mail newest index', index)


def func():
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2]

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
