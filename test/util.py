import json
import sys

from SingleLog.log import Logger

from PyPtt import PTT

logger = Logger('TEST_UTIL')


def get_id_pw(password_file):
    try:
        with open(password_file) as AccountFile:
            account = json.load(AccountFile)
            ptt_id = account['id']
            password = account['pw']
    except FileNotFoundError:
        print(f'Please write PTT ID and Password in {password_file}')
        print('{"id":"your ptt id", "pw":"your ptt pw"}')
        sys.exit()

    return ptt_id, password


def login(ptt_bot: PTT.API, host):
    if host == PTT.data_type.host_type.PTT1:
        ptt_id, ptt_pw = get_id_pw('account_ptt_0.json')
    else:
        ptt_id, ptt_pw = get_id_pw('account_ptt2_0.json')

    try:
        ptt_bot.login(ptt_id, ptt_pw)
    except PTT.exceptions.LoginError:
        logger.info('登入失敗')
        sys.exit()
    except PTT.exceptions.WrongIDorPassword:
        logger.info('帳號密碼錯誤')
        sys.exit()
    except PTT.exceptions.LoginTooOften:
        logger.info('請稍等一下再登入')
        sys.exit()

    if ptt_bot.unregistered_user:
        logger.info('未註冊使用者')

        if ptt_bot.process_picks != 0:
            logger.info(f'註冊單處理順位 {ptt_bot.process_picks}')

    if ptt_bot.registered_user:
        logger.info('已註冊使用者')
