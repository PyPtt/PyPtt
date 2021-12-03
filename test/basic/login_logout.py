from SingleLog.log import Logger

import PyPtt
import util


def func():
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LOG_LEVEL.TRACE,
        )
        util.login(ptt_bot, host)
        ptt_bot.logout()

        util.login(ptt_bot, host)
        ptt_bot.logout()

    logger.info('login logout test ok')


if __name__ == '__main__':

    logger = Logger('TEST')
    func()
