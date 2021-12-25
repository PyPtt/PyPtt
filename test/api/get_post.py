import json

from SingleLog.log import Logger

import PyPtt
import util


def test_no_condition(ptt_bot: PyPtt.API):
    result = []

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

    for board, index in test_post_list:
        if isinstance(index, int):
            article = ptt_bot.get_post(
                board,
                index=index)
        else:
            article = ptt_bot.get_post(
                board,
                aid=index)
        # if article[PyPtt.Article.delete_status] != PyPtt.ArticleDeleteStatus.exist:
        #     logger.info(f'{board} {index}', 'deleted')
        #     continue

        result.append(article)
        print('+==+' * 10)
        print(article[PyPtt.Post.content])

    return result


def get_post_with_condition(ptt_bot: PyPtt.API):
    def show_condition(test_board, search_type, condition):
        if search_type == PyPtt.SearchType.KEYWORD:
            type_str = '關鍵字'
        if search_type == PyPtt.SearchType.AUTHOR:
            type_str = '作者'
        if search_type == PyPtt.SearchType.PUSH:
            type_str = '推文數'
        if search_type == PyPtt.SearchType.MARK:
            type_str = '標記'
        if search_type == PyPtt.SearchType.MONEY:
            type_str = '稿酬'

        print(f'{test_board} 使用 {type_str} 搜尋 {condition}')

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
            ('PttSuggest', PyPtt.SearchType.PUSH, '10'),
        ]

    test_range = 1
    query = False

    for (board, search_type, condition) in test_list:
        show_condition(board, search_type, condition)
        index = ptt_bot.get_newest_index(
            PyPtt.NewIndex.BBS,
            board,
            search_type=search_type,
            search_condition=condition)
        print(f'{board} 最新文章編號 {index}')

        for i in range(test_range):
            post = ptt_bot.get_post(
                board,
                index=index - i,
                # PostIndex=611,
                search_type=search_type,
                search_condition=condition,
                query=query)

            print('列表日期:')
            print(post.list_date)
            print('作者:')
            print(post.author)
            print('標題:')
            print(post.title)

            if post.delete_status == PyPtt.PostDelStatus.exist:
                if not query:
                    print('內文:')
                    print(post.content)
            elif post.delete_status == PyPtt.PostDelStatus.deleted_by_author:
                print('文章被作者刪除')
            elif post.delete_status == PyPtt.PostDelStatus.deleted_by_moderator:
                print('文章被版主刪除')
            print('=' * 50)

    # TestList = [
    #     ('Python', PTT.data_type.post_search_type.KEYWORD, '[公告]')
    # ]

    # for (board, SearchType, Condition) in TestList:
    #     index = PTTBot.getNewestIndex(
    #         PTT.data_type.index_type.BBS,
    #         board,
    #         SearchType=SearchType,
    #         SearchCondition=Condition,
    #     )
    #     print(f'{board} 最新文章編號 {index}')

    #     Post = PTTBot.getPost(
    #         board,
    #         PostIndex=index,
    #         SearchType=SearchType,
    #         SearchCondition=Condition,
    #     )

    #     print('標題: ' + Post.getTitle())
    #     print('=' * 50)

    search_list = [
        (PyPtt.SearchType.KEYWORD, '新聞'),
        (PyPtt.SearchType.AUTHOR, 'Code'),
    ]

    index = ptt_bot.get_newest_index(
        PyPtt.NewIndex.BBS,
        'Gossiping',
        search_type=PyPtt.SearchType.KEYWORD,
        search_condition='新聞',
        search_list=search_list)
    print(f'Gossiping 最新文章編號 {index}')

    for current_index in range(1, index + 1):
        post_info = ptt_bot.get_post(
            'Gossiping',
            index=current_index,
            search_type=PyPtt.SearchType.KEYWORD,
            search_condition='新聞',
            search_list=search_list,
            query=True)

        print(current_index, post_info.title)


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

    for ptt_bot in ptt_bot_list:
        util.login(ptt_bot)

        result = test_no_condition(ptt_bot)

        ptt_bot.logout()

        print(json.dumps(result, ensure_ascii=False, indent=4))
    # assert (result[0] == result[1])


if __name__ == '__main__':
    logger = Logger('TEST')
    logger.info('PyPtt version', PyPtt.version)
    func()
