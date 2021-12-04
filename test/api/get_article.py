import json

from SingleLog.log import Logger

import PyPtt
import util

test_post_list = [
    ('Python', 1),
    # ('NotExitBoard', 1),
    # ('Python', '1TJH_XY0'),
    # # 文章格式錯誤
    # ('Steam', 4444),
    # ('Stock', 92324),
    # ('Stock', '1TVnEivO'),
    # # 文章格式錯誤
    # ('movie', 457),
    # ('Gossiping', '1UDnXefr'),
    # ('joke', '1Tc6G9eQ'),
    # # 135193
    # ('Test', 575),
    # # 待證文章
    # ('Test', '1U3pLzi0'),
    # # 古早文章
    # ('LAW', 1),
    # # 辦刪除文章
    # ('Test', 347),
    # # comment number parse error
    # ('Ptt25sign', '1VppdKLW'),
]


def test(ptt_bot: PyPtt.API):
    result = {}
    for board, index in test_post_list:
        article = ptt_bot.get_article(
            board,
            post_index=index,
            query=True)

        result = article

    return result


def func():
    ptt_bot_list = [
        PyPtt.API(
            # log_level=PyPtt.LOG_LEVEL.TRACE
        ),
        # PTT.API()
    ]

    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2]

    result = []
    for ptt_bot in ptt_bot_list:
        util.login(ptt_bot)

        result.append(test(ptt_bot))

        ptt_bot.logout()

    print(json.dumps(result, ensure_ascii=False, indent=4))
    # assert (result[0] == result[1])


if __name__ == '__main__':
    logger = Logger('TEST')
    func()
