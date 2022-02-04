import json

from SingleLog.log import Logger

import PyPtt

from . import config

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
        assert False

    return ptt_id, password


def login(ptt_bot: PyPtt.API):
    if ptt_bot.host == PyPtt.HOST.PTT1:
        ptt_id, ptt_pw = config.PTT1_ID, config.PTT1_PW
    else:
        ptt_id, ptt_pw = config.PTT2_ID, config.PTT2_PW

    for _ in range(3):
        try:
            ptt_bot.login(ptt_id, ptt_pw)
            break
        except PyPtt.LoginError:
            logger.info('登入失敗')
            assert False
        except PyPtt.WrongIDorPassword:
            logger.info('帳號密碼錯誤')
            assert False
        except PyPtt.LoginTooOften:
            logger.info('請稍等一下再登入')
            assert False

    if ptt_bot.unregistered_user:
        logger.info('未註冊使用者')

        if ptt_bot.process_picks != 0:
            logger.info(f'註冊單處理順位 {ptt_bot.process_picks}')

    if ptt_bot.registered_user:
        logger.info('已註冊使用者')
