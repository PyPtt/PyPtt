import json
import sys

import PyPtt
from tests import util


def test_no_condition(ptt_bot: PyPtt.API):
    result = []

    if ptt_bot.host == PyPtt.HOST.PTT1:
        test_post_list = [
            ('Python', 1),
            # ('NotExitBoard', 1),
            ('Python', '1TJH_XY0'),
            # ('Python', '1TJdL7L8'),
            # # 文章格式錯誤
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
    else:
        test_post_list = [
            ('WhoAmI', 1),
        ]

    for board, index in test_post_list:
        if isinstance(index, int):
            post = ptt_bot.get_post(
                board,
                index=index)

            ptt_bot.get_post(
                board,
                index=index,
                query=True)
        else:
            post = ptt_bot.get_post(
                board,
                aid=index)

            ptt_bot.get_post(
                board,
                aid=index,
                query=True)

        result.append(post)
        # util.log.py.info('+==+' * 10)
        # util.log.py.info(post[PyPtt.PostField.content])

    return result


def get_post_with_condition(ptt_bot: PyPtt.API):
    def show_condition(test_board, search_type, condition):
        if search_type == PyPtt.SearchType.KEYWORD:
            type_str = '關鍵字'
        if search_type == PyPtt.SearchType.AUTHOR:
            type_str = '作者'
        if search_type == PyPtt.SearchType.COMMENT:
            type_str = '推文數'
        if search_type == PyPtt.SearchType.MARK:
            type_str = '標記'
        if search_type == PyPtt.SearchType.MONEY:
            type_str = '稿酬'

        util.logger.info(f'{test_board} 使用 {type_str} 搜尋 {condition}')

    if ptt_bot.config.host == PyPtt.HOST.PTT1:
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
            ('PttSuggest', PyPtt.SearchType.COMMENT, '10'),
        ]

    result = []

    test_range = 1
    query = False

    for (board, search_type, condition) in test_list:
        show_condition(board, search_type, condition)
        index = ptt_bot.get_newest_index(
            PyPtt.NewIndex.BOARD,
            board,
            search_type=search_type,
            search_condition=condition)
        util.logger.info(f'{board} 最新文章編號 {index}')

        for i in range(test_range):
            post = ptt_bot.get_post(
                board,
                index=index - i,
                # PostIndex=611,
                search_type=search_type,
                search_condition=condition,
                query=query)

            # print(json.dumps(post, indent=4))

            util.logger.info('列表日期', post.get('list_date'))
            util.logger.info('作者', post.get('author'))
            util.logger.info('標題', post.get('title'))

            if post.get('post_status') == PyPtt.PostStatus.EXISTS:
                pass
                # if not query:
                #     util.log.py.info('內文', post.get('content'))
            elif post.get('post_status') == PyPtt.PostStatus.DELETED_BY_AUTHOR:
                util.logger.info('文章被作者刪除')
            elif post.get('post_status') == PyPtt.PostStatus.DELETED_BY_MODERATOR:
                util.logger.info('文章被版主刪除')
            util.logger.info('=' * 50)

            result.append(post)

    return result


def test(ptt_bot: PyPtt.API):
    result = test_no_condition(ptt_bot)

    print(result)
    util.logger.info(json.dumps(result, indent=4, ensure_ascii=False))

    # result = get_post_with_condition(ptt_bot)
    # util.log.py.info(json.dumps(result, ensure_ascii=False, indent=4))


def func():

    host_list = [
        PyPtt.HOST.PTT1,
        # PyPtt.HOST.PTT2
    ]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LOG_LEVEL.TRACE,
        )
        util.login(ptt_bot)

        test(ptt_bot)

        ptt_bot.logout()

    # assert (result[0] == result[1])


if __name__ == '__main__':
    func()