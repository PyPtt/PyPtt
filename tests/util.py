import json
import logging

import PyPtt
from PyPtt import PostField
from . import config


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


def login(ptt_bot: PyPtt.API, kick: bool = True):
    if ptt_bot.host == PyPtt.HOST.PTT1:
        ptt_id, ptt_pw = config.PTT1_ID, config.PTT1_PW
    else:
        ptt_id, ptt_pw = config.PTT2_ID, config.PTT2_PW

    for _ in range(3):
        try:
            ptt_bot.login(ptt_id=ptt_id, ptt_pw=ptt_pw, kick_other_session=kick)
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

    if not ptt_bot.is_registered_user:
        logger.info('未註冊使用者')

        if ptt_bot.process_picks != 0:
            logger.info(f'註冊單處理順位 {ptt_bot.process_picks}')


def show_data(data, key: str = None):
    if isinstance(data, dict):
        logger.info(f'{key}: {data[key]}')


def del_all_post(ptt_bot: PyPtt.API):
    newest_index = ptt_bot.get_newest_index(index_type=PyPtt.NewIndex.BOARD, board='Test')

    post_list = []
    for i in range(30):
        post = ptt_bot.get_post(board='Test', index=newest_index - i)

        if post[PostField.post_status] != PyPtt.PostStatus.EXISTS:
            continue

        post_author = post[PostField.author]
        post_author: str = post_author.split(' ')[0]
        if post_author.lower() != ptt_bot.ptt_id.lower():
            continue

        post_list.append(newest_index - i)

    for index in post_list:
        ptt_bot.del_post(board='Test', index=index)
