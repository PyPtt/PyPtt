from SingleLog.log import Logger

import util
import PyPtt

if __name__ == '__main__':
    logger = Logger('TEST')

    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2
    ]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PTT.logger_level.TRACE,
        )
        util.login(ptt_bot, host)

        # time.sleep(2)

        ptt_bot.logout()
