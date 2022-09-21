import PyPtt
from tests import util


def test_board_index(ptt_bot: PyPtt.API):
    if ptt_bot.host == PyPtt.HOST.PTT1:
        test_list = [
            ('Python', PyPtt.SearchType.KEYWORD, '[公告]'),
            ('ALLPOST', PyPtt.SearchType.KEYWORD, '(Wanted)'),
            ('Wanted', PyPtt.SearchType.KEYWORD, '(本文已被刪除)'),
            ('ALLPOST', PyPtt.SearchType.KEYWORD, '(Gossiping)'),
            ('Gossiping', PyPtt.SearchType.KEYWORD, '普悠瑪'),
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
            util.logger.info(f'{board} newest index', index)

            index = ptt_bot.get_newest_index(
                PyPtt.NewIndex.BOARD,
                board=board,
                search_type=search_type,
                search_condition=search_condition)
            util.logger.info(f'{board} newest index with search', index)


def test_mail_index(ptt_bot: PyPtt.API):
    for _ in range(3):
        index = ptt_bot.get_newest_index(
            PyPtt.NewIndex.MAIL)
        util.logger.info('mail newest index', index)



def func():
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2
    ]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LOG_LEVEL.TRACE,
        )
        util.login(ptt_bot)

        test_mail_index(ptt_bot)

        ptt_bot.logout()


if __name__ == '__main__':
    func()
