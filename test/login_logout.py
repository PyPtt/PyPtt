import time

from SingleLog.log import Logger

import util
from PyPtt import PTT

if __name__ == '__main__':
    logger = Logger('TEST')

    host_list = [
        # PTT.data_type.host_type.PTT1,
        PTT.data_type.host_type.PTT2
    ]

    for host in host_list:
        ptt_bot = PTT.API(
            host=host,
            # log_level=PTT.logger_level.TRACE,
        )
        util.login(ptt_bot, host)

        # time.sleep(2)

        ptt_bot.logout()
