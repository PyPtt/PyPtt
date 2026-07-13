import json
import logging

import PyPtt
from tests import config

logger = logging.getLogger()


def log_to_file(msg: str):
    with open('single_log.txt', 'a', encoding='utf8') as f:
        f.write(f'{msg}\n')


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


def login(ptt_bot: PyPtt.API, kick: bool = True, max_retries: int = 3, retry_delay: int = 10,
          account: int = None):
    import time

    if account == 1:
        ptt_id, ptt_pw = config.PTT1_ID, config.PTT1_PW
    elif account == 2:
        ptt_id, ptt_pw = config.PTT2_ID, config.PTT2_PW
    elif ptt_bot.host == PyPtt.HOST.PTT1:
        ptt_id, ptt_pw = config.PTT1_ID, config.PTT1_PW
    else:
        ptt_id, ptt_pw = config.PTT2_ID, config.PTT2_PW

    for attempt in range(max_retries):
        try:
            ptt_bot.login(ptt_id=ptt_id, ptt_pw=ptt_pw, kick_other_session=kick)
            return
        except PyPtt.WrongIDorPassword:
            logger.info('帳號密碼錯誤')
            assert False, '帳號密碼錯誤，不重試'
        except (PyPtt.LoginError, PyPtt.LoginTooOften) as e:
            if attempt < max_retries - 1:
                wait = retry_delay * (attempt + 1)
                logger.info(f'登入失敗 ({e})，{wait} 秒後重試 ({attempt + 1}/{max_retries})')
                time.sleep(wait)
            else:
                assert False, f'登入失敗，已重試 {max_retries} 次: {e}'

    if not ptt_bot.is_registered_user:
        logger.info('未註冊使用者')

        if ptt_bot.process_picks != 0:
            logger.info(f'註冊單處理順位 {ptt_bot.process_picks}')


def show_data(data, key: str = None):
    if isinstance(data, dict):
        logger.info(f'{key}: {data[key]}')


def del_all_post(ptt_bot: PyPtt.API):
    newest_index = ptt_bot.get_newest_index(index_type=PyPtt.NewIndex.BOARD, board='Test')

    for i in range(30):
        try:
            ptt_bot.del_post(board='Test', index=newest_index - i)
        except Exception:
            pass
