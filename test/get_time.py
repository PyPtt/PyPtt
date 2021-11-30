
from SingleLog.log import Logger

from PyPtt import PTT
import util

if __name__ == '__main__':
    logger = Logger('TEST')

    ptt_bot = PTT.API()

    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
        ptt_id, password = util.get_password('account_ptt_0.json')
    else:
        ptt_id, password = util.get_password('account_ptt2_0.json')
