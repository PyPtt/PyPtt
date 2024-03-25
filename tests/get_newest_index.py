import os
import sys

sys.path.append(os.getcwd())

import PyPtt
from PyPtt import log
from tests import util


def test_board_index(ptt_bot: PyPtt.API):
    if ptt_bot.host == PyPtt.HOST.PTT1:
        test_list = [
            ('Python', PyPtt.SearchType.KEYWORD, '[公告]'),
            ('ALLPOST', PyPtt.SearchType.KEYWORD, '(Wanted)'),
            ('Wanted', PyPtt.SearchType.KEYWORD, '(本文已被刪除)'),
            ('ALLPOST', PyPtt.SearchType.KEYWORD, '(Gossiping)'),
            ('Gossiping', PyPtt.SearchType.KEYWORD, '普悠瑪'),
            ('book', PyPtt.SearchType.KEYWORD, 'AWS'),
        ]
    else:
        test_list = [
            ('PttSuggest', PyPtt.SearchType.KEYWORD, '[問題]'),
            # ('PttSuggest', PyPtt.SearchType.COMMENT, '10'),
        ]

    for board, search_type, search_condition in test_list:
        for _ in range(3):
            index = ptt_bot.get_newest_index(
                PyPtt.NewIndex.BOARD,
                board)
            log.logger.info(f'{board} newest index', index)

            index = ptt_bot.get_newest_index(
                PyPtt.NewIndex.BOARD,
                board=board,
                search_type=search_type,
                search_condition=search_condition)
            log.logger.info(f'{board} newest index with search', index)


def test_mail_index(ptt_bot: PyPtt.API):
    for _ in range(3):
        index = ptt_bot.get_newest_index(
            PyPtt.NewIndex.MAIL)
        log.logger.info('mail newest index', index)


def func():
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2
    ]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LogLevel.DEBUG,
        )
        try:
            util.login(ptt_bot)
            test_mail_index(ptt_bot)
        finally:
            ptt_bot.logout()


if __name__ == '__main__':
    func()
