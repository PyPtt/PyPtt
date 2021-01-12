import sys
import os
import time
import json
import random
import traceback
import threading

from PyPtt import PTT


def get_password(password_file):
    try:
        with open(password_file) as AccountFile:
            account = json.load(AccountFile)
            ptt_id = account['ID']
            password = account['Password']
    except FileNotFoundError:
        print(f'Please note PTT ID and Password in {password_file}')
        print('{"ID":"YourID", "Password":"YourPassword"}')
        sys.exit()

    return ptt_id, password


def init():
    print('===正向===')
    print('===預設值===')
    PTT.API()
    print('===中文顯示===')
    PTT.API(language=PTT.i18n.language.CHINESE)
    print('===英文顯示===')
    PTT.API(language=PTT.i18n.language.ENGLISH)
    print('===log DEBUG===')
    PTT.API(log_level=PTT.log.level.DEBUG)
    print('===log INFO===')
    PTT.API(log_level=PTT.log.level.INFO)
    print('===log SLIENT===')
    PTT.API(log_level=PTT.log.level.SILENT)
    print('===log SLIENT======')

    print('===負向===')
    try:
        print('===語言 99===')
        PTT.API(language=99)
    except ValueError:
        print('通過')
    except:
        print('沒通過')
        sys.exit(-1)
    print('===語言放字串===')
    try:
        PTT.API(language='PTT.i18n.language.ENGLISH')
    except TypeError:
        print('通過')
    except:
        print('沒通過')
        sys.exit(-1)

    def handler(msg):
        with open('log.txt', 'a', encoding='utf-8') as f:
            f.write(msg + '\n')

    ptt_bot = PTT.API(
        log_handler=handler)
    ptt_bot.log('Test log')


def performance_test():
    test_time = 2000
    print(f'效能測試 get_time {test_time} 次')

    start_time = time.time()
    for _ in range(test_time):
        ptt_time = ptt_bot.get_time()

        if ptt_time is None:
            print('PTT_TIME is None')
            break
        # print(ptt_time)
    end_time = time.time()
    print('Performance Test get_time ' + str(
        round(end_time - start_time, 2)) + ' s')

    start_time = time.time()
    for _ in range(test_time):
        ptt_time = ptt_bot.fast_get_time()

        if ptt_time is None:
            print('PTT_TIME is None')
            break
        # print(ptt_time)
    end_time = time.time()
    print('Performance Test fast_get_time ' + str(
        round(end_time - start_time, 2)) + ' s')

    ptt_bot.logout()


    print('Performance Test finish')
    sys.exit()

#             for _ in range(1000):
#             ptt_time = ptt_bot.fast_get_time()
#             if len(ptt_time) != 5:
#                 print('error!', ptt_time)
#                 break
#             # print(ptt_time)


def get_post():
    def show(name, value):
        if value is not None:
            print(f'{name} [{value}]')
        else:
            print(f'無{name}')

    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
        test_post_list = [
            ('Python', 1),
            ('NotExitBoard', 1),
            ('Python', '1TJH_XY0'),
            # 文章格式錯誤
            ('Steam', 4444),
            ('Stock', 92324),
            ('Stock', '1TVnEivO'),
            # 文章格式錯誤
            ('movie', 457),
            ('Gossiping', '1UDnXefr'),
            ('joke', '1Tc6G9eQ'),
            # 135193
            ('Test', 575),
            # 待證文章
            ('Test', '1U3pLzi0'),
            # 古早文章
            ('LAW', 1),
            # 辦刪除文章
            ('Test', 347),
            # push number parse error
            ('Ptt25sign', '1VppdKLW'),
        ]
    else:
        test_post_list = [
            # PTT2
            ('PttSuggest', 1),
            ('PttSuggest', '0z7TVw00'),
            # 文章格式錯誤
            # 發信站:
            ('PttSuggest', '1EbQObff'),
            # 文章起始消失跳躍，導致沒有結尾 (已經修正)
            ('WhoAmI', '1Tc0ooap'),
            # Test
            # 文章格式錯誤
            # 瞎改
            ('Test', '1Sp1W7Fi'),
            ('Test', '1TXRkuDW'),
            ('WhoAmI', '1TqJhzQH')
        ]

    query = False

    for (board, index) in test_post_list:
        try:

            print('看板', board, index)
            if isinstance(index, int):
                post_info = ptt_bot.get_post(
                    board,
                    post_index=index,
                    # SearchType=PTT.data_type.post_search_type.KEYWORD,
                    # SearchCondition='公告',
                    query=query)
            else:
                post_info = ptt_bot.get_post(
                    board,
                    post_aid=index,
                    # SearchType=PTT.data_type.post_search_type.KEYWORD,
                    # SearchCondition='公告',
                    query=query)
            if post_info is None:
                print('Empty')
                continue

            if not post_info.pass_format_check:
                print('文章格式錯誤')
                continue

            if post_info.is_lock:
                print('鎖文狀態')
                continue

            if post_info.delete_status != PTT.data_type.post_delete_status.NOT_DELETED:
                print('文章已經被刪除')
                continue

            # show('Origin Post\n', post.origin_post)
            if not query:
                print('Origin Post\n' + post_info.origin_post)
                print('=' * 30 + ' Origin Post Finish')
            show('Board', post_info.board)
            show('AID', post_info.aid)
            show('push num', post_info.push_number)
            show('index', post_info.index)
            show('Author', post_info.author)
            show('push_number', post_info.push_number)
            show('List Date', post_info.list_date)
            show('Title', post_info.title)
            show('Money', post_info.money)
            show('URL', post_info.web_url)

            if post_info.is_unconfirmed:
                print('待證實文章')

            if not query:
                show('Date', post_info.date)
                show('Content', post_info.content)
                show('IP', post_info.ip)
                show('Location', post_info.location)

                # 在文章列表上的日期

                push_count = 0
                boo_count = 0
                arrow_count = 0

                for push_obj in post_info.push_list:
                    #     print(Push.getType())
                    #     print(Push.getAuthor())
                    #     print(Push.getContent())
                    #     print(Push.getIP())
                    #     print(Push.time)

                    if push_obj.type == PTT.data_type.push_type.PUSH:
                        push_count += 1
                        push_type = '推'
                    if push_obj.type == PTT.data_type.push_type.BOO:
                        boo_count += 1
                        push_type = '噓'
                    if push_obj.type == PTT.data_type.push_type.ARROW:
                        arrow_count += 1
                        push_type = '→'

                    author = push_obj.author
                    content = push_obj.content

                    # Buffer = f'[{Author}] 給了一個{Type} 說 [{Content}]'
                    # if Push.getIP() is not None:
                    #     Buffer += f' 來自 [{Push.getIP()}]'
                    # Buffer += f' 時間是 [{Push.time}]'

                    if push_obj.ip is not None:
                        buffer = f'{push_type} {author}: {content} {push_obj.ip} {push_obj.time}'
                    else:
                        buffer = f'{push_type} {author}: {content} {push_obj.time}'
                    print(buffer)

                # print(post_info.origin_post)

                print(
                    f'Total {push_count} Pushs {boo_count} Boo {arrow_count} Arrow = {push_count - boo_count}')
        except Exception as e:

            traceback.print_tb(e.__traceback__)
            print(e)


def get_aid_from_url():
    # test_url = [
    #     'https://www.ptt.cc/bbs/NDHU-His_WV/M.1072146614.A.D59.html',
    #     'https://www.ptt.cc/bbs/NDMC-M99c/M.1084922723.A.html',
    # ]
    #
    # for url in test_url:
    #     board, aid = ptt_bot.get_aid_from_url(url)
    #     print(board, aid)
    #
    # return

    bug_board = [
        'ck55th316'
    ]

    def random_board_test():
        board_list = ptt_bot.get_board_list()
        board_list = [x for x in board_list if x not in bug_board]

        test_range = 5000

        test_board = random.sample(board_list, test_range)

        for test_board in test_board:

            print(test_board)

            newest_index = ptt_bot.get_newest_index(PTT.data_type.index_type.BBS, board=test_board)
            print(f'newest_index {newest_index}')
            if newest_index == 0:
                continue
            while True:
                current_index = random.randrange(1, newest_index + 1)
                print(current_index)

                post_info = ptt_bot.get_post(test_board, post_index=current_index, query=True)
                if post_info.delete_status != PTT.data_type.post_delete_status.NOT_DELETED:
                    continue

                if post_info.web_url is None:
                    print(f'error url is None {test_board} {current_index}')
                    break

                if post_info.aid is None:
                    print(f'error aid is None {test_board} {current_index}')
                    continue

                convert_board, convert_aid = ptt_bot.get_aid_from_url(post_info.web_url)

                if convert_board != test_board:
                    print('board not match')
                    print(f'post_info {test_board}')
                    print(f'convert {convert_board}')
                    raise ValueError()

                if convert_aid != post_info.aid:
                    print('aid not match')
                    print(f'post_info {post_info.aid}')
                    print(f'convert {convert_aid}')
                    raise ValueError()

                break
        print('===================================')

    def random_post_test():
        test_board = 'Gossiping'
        newest_index = ptt_bot.get_newest_index(PTT.data_type.index_type.BBS, board=test_board)
        print(f'{test_board} newest_index {newest_index}')

        test_range = 5000

        start_index = random.randrange(1, newest_index + 1 - test_range)
        print(start_index)

        for current_index in range(start_index, start_index + test_range):
            print(current_index)
            post_info = ptt_bot.get_post(test_board, post_index=current_index, query=True)
            if post_info.delete_status != PTT.data_type.post_delete_status.NOT_DELETED:
                continue

            if post_info.web_url is None:
                print(f'error url is None {test_board} {current_index}')
                break

            if post_info.aid is None:
                print(f'error aid is None {test_board} {current_index}')
                continue

            convert_board, convert_aid = ptt_bot.get_aid_from_url(post_info.web_url)

            if convert_board != test_board:
                print('board not match')
                print(f'post_info {test_board}')
                print(f'convert {convert_board}')
                raise ValueError()

            if convert_aid != post_info.aid:
                print('aid not match')
                print(f'post_info {post_info.aid}')
                print(f'convert {convert_aid}')
                raise ValueError()

    random_post_test()


test_list = {
    ('Wanted', PTT.data_type.post_search_type.KEYWORD, '[公告]'),
    ('Wanted', PTT.data_type.post_search_type.AUTHOR, 'gogin'),
    ('Wanted', PTT.data_type.post_search_type.PUSH, '10'),
    ('Wanted', PTT.data_type.post_search_type.MARK, 'm'),
    ('Wanted', PTT.data_type.post_search_type.MONEY, '5'),
    ('Gossiping', PTT.data_type.post_search_type.KEYWORD, '[公告]'),
    ('Gossiping', PTT.data_type.post_search_type.AUTHOR, 'ReDmango'),
    ('Gossiping', PTT.data_type.post_search_type.PUSH, '10'),
    ('Gossiping', PTT.data_type.post_search_type.MARK, 'm'),
    ('Gossiping', PTT.data_type.post_search_type.MONEY, '5'),

    ('Gossiping', PTT.data_type.post_search_type.PUSH, '-100'),
    ('Gossiping', PTT.data_type.post_search_type.PUSH, '150'),
}


def show_condition(test_board, search_type, condition):
    if search_type == PTT.data_type.post_search_type.KEYWORD:
        type_str = '關鍵字'
    if search_type == PTT.data_type.post_search_type.AUTHOR:
        type_str = '作者'
    if search_type == PTT.data_type.post_search_type.PUSH:
        type_str = '推文數'
    if search_type == PTT.data_type.post_search_type.MARK:
        type_str = '標記'
    if search_type == PTT.data_type.post_search_type.MONEY:
        type_str = '稿酬'

    print(f'{test_board} 使用 {type_str} 搜尋 {condition}')


def get_post_with_condition():
    # PTT1

    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
        test_list = [
            ('Python', PTT.data_type.post_search_type.KEYWORD, '[公告]'),
            ('ALLPOST', PTT.data_type.post_search_type.KEYWORD, '(Wanted)'),
            ('Wanted', PTT.data_type.post_search_type.KEYWORD, '(本文已被刪除)'),
            ('ALLPOST', PTT.data_type.post_search_type.KEYWORD, '(Gossiping)'),
            ('Gossiping', PTT.data_type.post_search_type.KEYWORD, '普悠瑪'),
        ]
    else:
        test_list = [
            ('PttSuggest', PTT.data_type.post_search_type.KEYWORD, '[問題]'),
            ('PttSuggest', PTT.data_type.post_search_type.PUSH, '10'),
        ]

    test_range = 1
    query = False

    for (board, search_type, condition) in test_list:
        show_condition(board, search_type, condition)
        index = ptt_bot.get_newest_index(
            PTT.data_type.index_type.BBS,
            board,
            search_type=search_type,
            search_condition=condition)
        print(f'{board} 最新文章編號 {index}')

        for i in range(test_range):
            post = ptt_bot.get_post(
                board,
                post_index=index - i,
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

            if post.delete_status == PTT.data_type.post_delete_status.NOT_DELETED:
                if not query:
                    print('內文:')
                    print(post.content)
            elif post.delete_status == PTT.data_type.post_delete_status.AUTHOR:
                print('文章被作者刪除')
            elif post.delete_status == PTT.data_type.post_delete_status.MODERATOR:
                print('文章被版主刪除')
            print('=' * 50)

    # TestList = [
    #     ('Python', PTT.data_type.post_search_type.KEYWORD, '[公告]')
    # ]

    # for (Board, SearchType, Condition) in TestList:
    #     index = PTTBot.getNewestIndex(
    #         PTT.data_type.index_type.BBS,
    #         Board,
    #         SearchType=SearchType,
    #         SearchCondition=Condition,
    #     )
    #     print(f'{Board} 最新文章編號 {index}')

    #     Post = PTTBot.getPost(
    #         Board,
    #         PostIndex=index,
    #         SearchType=SearchType,
    #         SearchCondition=Condition,
    #     )

    #     print('標題: ' + Post.getTitle())
    #     print('=' * 50)

    search_list = [
        (PTT.data_type.post_search_type.KEYWORD, '新聞'),
        (PTT.data_type.post_search_type.AUTHOR, 'Code'),
    ]

    index = ptt_bot.get_newest_index(
        PTT.data_type.index_type.BBS,
        'Gossiping',
        search_type=PTT.data_type.post_search_type.KEYWORD,
        search_condition='新聞',
        search_list=search_list)
    print(f'Gossiping 最新文章編號 {index}')

    for current_index in range(1, index + 1):
        post_info = ptt_bot.get_post(
            'Gossiping',
            post_index=current_index,
            search_type=PTT.data_type.post_search_type.KEYWORD,
            search_condition='新聞',
            search_list=search_list,
            query=True)

        print(current_index, post_info.title)


def post():
    content = '''
此為 PyPtt 貼文測試內容，如有打擾請告知。
github: https://github.com/PttCodingMan/PyPtt

開發手冊: https://github.com/PttCodingMan/PyPtt/tree/master/doc
ポ
ポポ
ポポポ
☂
☂☂
☂☂☂
'''
    content = content.replace('\n', '\r\n')

    for _ in range(3):
        ptt_bot.post(
            # 看板
            'Test',
            # 標題
            'PyPtt 程式貼文測試',
            # 內文
            content,
            # 標題分類
            1,
            # 簽名檔
            0)


def get_newest_index():
    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
        test_board_list = [
            'Wanted',
            'Gossiping',
            'Test',
            'Stock',
            'movie'
        ]
    else:
        test_board_list = [
            'PttSuggest',
            'Test',
            'WhoAmI',
            'CodingMan'
        ]

    test_range = 100

    for board in test_board_list:
        for _ in range(test_range):
            index = ptt_bot.get_newest_index(PTT.data_type.index_type.BBS, board=board)
            print(f'{board} 最新文章編號 {index}')

    ###############################################

    index = ptt_bot.get_newest_index(PTT.data_type.index_type.MAIL)
    print(f'最新郵件編號 {index}')

    index = ptt_bot.get_newest_index(
        PTT.data_type.index_type.MAIL,
        search_type=PTT.data_type.mail_search_type.KEYWORD,
        search_condition='uPtt system')
    print(f'最新郵件編號 {index}')

    search_list = [
        (PTT.data_type.mail_search_type.KEYWORD, 'uPtt'),
        (PTT.data_type.mail_search_type.KEYWORD, 'key')
    ]

    index = ptt_bot.get_newest_index(
        PTT.data_type.index_type.MAIL,
        search_list=search_list)
    print(f'最新郵件編號 {index}')


def showValue(Msg, Value):
    print(f'{Msg} =>{Value}<=')


def detectNone(Name, Obj, Enable=True):
    if Obj is None and Enable:
        raise ValueError(Name + ' is None')


query = False


def crawlHandler(Post):
    global query

    if Post.delete_status != PTT.data_type.post_delete_status.NOT_DELETED:
        if Post.delete_status == PTT.data_type.post_delete_status.MODERATOR:
            # print(f'[版主刪除][{Post.getAuthor()}]')
            pass
        elif Post.delete_status == PTT.data_type.post_delete_status.AUTHOR:
            # print(f'[作者刪除][{Post.getAuthor()}]')
            pass
        elif Post.delete_status == PTT.data_type.post_delete_status.UNKNOWN:
            # print(f'[不明刪除]')
            pass
        return

    # if Post.getTitle().startswith('Fw:') or Post.getTitle().startswith('轉'):
    # print(f'[{Post.aid}][{Post.getAuthor()}][{Post.getTitle()}]')
    # print(f'[{Post.getContent()}]')

    # print(f'[{Post.getAuthor()}][{Post.getTitle()}]')

    PushNumber = Post.push_number
    if PushNumber is not None:
        if PushNumber == '爆':
            pass
        elif PushNumber.startswith('X'):
            N = PushNumber[1:]
        else:
            pass
            # if not PushNumber.isdigit():
            #     print(f'[{Post.aid}][{Post.push_number}]')
            #     print(f'[{Post.aid}][{Post.push_number}]')
            #     print(f'[{Post.aid}][{Post.push_number}]')
            #     raise ValueError()
        # print(f'[{Post.aid}][{Post.getPushNumber()}]')

    detectNone('標題', Post.title)
    # detectNone('AID', Post.aid)
    detectNone('Author', Post.author)
    # detectNone('Money', Post.getMoney())

    # detectNone('WebUrl', Post.web_url)
    # detectNone('ListDate', Post.getListDate())

    # if not Query:
    # detectNone('Date', Post.getDate())
    # detectNone('Content', Post.getContent())
    # detectNone('IP', Post.getIP())

    # time.sleep(0.2)


def crawl_board():
    global query
    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
        test_board_list = [
            'Test',
            'Wanted',
            'Gossiping',
            'Stock',
            'movie',
            'C_Chat',
            'Baseball',
            'NBA',
            'HatePolitics',
        ]
    else:
        test_board_list = [
            'Test',
            'WhoAmI',
            'PttSuggest'
        ]

    # crawl_type = PTT.data_type.index_type.WEB
    crawl_type = PTT.data_type.index_type.BBS

    index_type = 'Index'

    test_range = 100
    test_round = 2

    for _ in range(test_round):

        for TestBoard in test_board_list:

            if crawl_type == PTT.data_type.index_type.BBS:

                if index_type == 'Index':
                    newest_index = ptt_bot.get_newest_index(
                        PTT.data_type.index_type.BBS,
                        board=TestBoard)
                    start_index = newest_index - test_range + 1

                    print(
                        f'預備爬行 {TestBoard} 編號 {start_index} ~ {newest_index} 文章')

                    print(f'TestBoard [{TestBoard}]')
                    error_post_list, del_post_list = ptt_bot.crawl_board(
                        PTT.data_type.crawl_type.BBS,
                        crawlHandler,
                        TestBoard,
                        start_index=start_index,
                        end_index=newest_index,
                        query=query)
                elif index_type == 'AID':

                    start_aid = '1TnDKzxw'
                    end_aid = '1TnCPFGu'

                    error_post_list, del_post_list = ptt_bot.crawl_board(
                        PTT.data_type.crawl_type.BBS,
                        crawlHandler,
                        TestBoard,
                        start_aid=start_aid,
                        end_aid=end_aid)
                if len(error_post_list) > 0:
                    print('格式錯誤文章: \n' + '\n'.join(str(x)
                                                   for x in error_post_list))
                else:
                    print('沒有偵測到格式錯誤文章')

                if len(del_post_list) > 0:
                    print(f'共有 {len(del_post_list)} 篇文章被刪除')

            elif crawl_type == PTT.data_type.index_type.WEB:

                newest_index = ptt_bot.get_newest_index(
                    PTT.data_type.index_type.WEB,
                    board=TestBoard)
                end_page = newest_index

                start_page = end_page - test_range + 1

                print(f'預備爬行 {TestBoard} 最新頁數 {newest_index}')
                print(f'預備爬行 {TestBoard} 編號 {start_page} ~ {end_page} 文章')

                error_post_list, del_post_list = ptt_bot.crawl_board(
                    PTT.data_type.crawl_type.WEB,
                    crawlHandler,
                    TestBoard,
                    start_page=start_page,
                    end_page=end_page)

                if len(del_post_list) > 0:
                    print('\n'.join(del_post_list))
                    print(f'共有 {len(del_post_list)} 篇文章被刪除')


def crawl_board_with_condition():
    # TestRange = 10

    # for (Board, SearchType, Condition) in TestList:
    #     try:
    #         showCondition(Board, SearchType, Condition)
    #         NewestIndex = PTTBot.getNewestIndex(
    #             PTT.data_type.index_type.BBS,
    #             Board,
    #             SearchType=SearchType,
    #             SearchCondition=Condition,
    #         )
    #         print(f'{Board} 最新文章編號 {NewestIndex}')

    #         StartIndex = NewestIndex - TestRange + 1

    #         ErrorPostList, DelPostList = PTTBot.crawlBoard(
    #             crawlHandler,
    #             Board,
    #             StartIndex=StartIndex,
    #             EndIndex=NewestIndex,
    #             SearchType=SearchType,
    #             SearchCondition=Condition,
    #         )

    #         # print('標題: ' + Post.getTitle())
    #         print('=' * 50)

    #     except Exception as e:

    #         traceback.print_tb(e.__traceback__)
    #         print(e)

    # if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
    #     test_list = [
    #         # ptt1
    #         ('Stock', PTT.data_type.post_search_type.KEYWORD, '盤中閒聊'),
    #         ('Baseball', PTT.data_type.post_search_type.PUSH, '20')
    #     ]
    # else:
    #     test_list = [
    #         ('WhoAmI', PTT.data_type.post_search_type.KEYWORD, '[閒聊]'),
    #         ('WhoAmI', PTT.data_type.post_search_type.PUSH, '10')
    #     ]
    #
    # test_range = 100
    #
    # for (board, search_type, search_condition) in test_list:
    #     show_condition(board, search_type, search_condition)
    #     newest_index = ptt_bot.get_newest_index(
    #         PTT.data_type.index_type.BBS,
    #         board,
    #         search_type=search_type,
    #         search_condition=search_condition)
    #     print(f'{board} 最新文章編號 {newest_index}')
    #
    #     start_index = newest_index - test_range + 1
    #
    #     error_post_list, del_post_list = ptt_bot.crawl_board(
    #         PTT.data_type.crawl_type.BBS,
    #         crawlHandler,
    #         board,
    #         start_index=start_index,
    #         end_index=newest_index,
    #         search_type=search_type,
    #         search_condition=search_condition,
    #     )
    #     print('=' * 50)

    search_list = [
        (PTT.data_type.post_search_type.KEYWORD, '新聞'),
        (PTT.data_type.post_search_type.AUTHOR, 'Code'),
    ]

    newest_index = ptt_bot.get_newest_index(
        PTT.data_type.index_type.BBS,
        'Gossiping',
        search_list=search_list)
    print(f'Gossiping 最新文章編號 {newest_index}')

    error_post_list, del_post_list = ptt_bot.crawl_board(
        PTT.data_type.crawl_type.BBS,
        crawlHandler,
        'Gossiping',
        start_index=1,
        end_index=newest_index,
        search_list=search_list)


def get_user():
    test_user = [
        # 暱稱有特殊字元
        'for40255',
        'CodingMan'
    ]

    test_user = ptt_bot.search_user('c', max_page=1)
    test_user = test_user[:10]
    print(f'共有 {len(test_user)} 使用者')

    for user in test_user:
        try:
            ptt_bot.log(user)
            user = ptt_bot.get_user(user)
            if user is None:
                return

            ptt_bot.log('使用者ID: ' + user.id)
            ptt_bot.log('使用者經濟狀況: ' + str(user.money))
            ptt_bot.log('登入次數: ' + str(user.login_time))
            ptt_bot.log('有效文章數: ' + str(user.legal_post))
            ptt_bot.log('退文文章數: ' + str(user.illegal_post))
            ptt_bot.log('目前動態: ' + user.status)
            ptt_bot.log('信箱狀態: ' + user.mail_status)
            ptt_bot.log('最後登入時間: ' + user.last_login)
            ptt_bot.log('上次故鄉: ' + user.last_ip)
            ptt_bot.log('五子棋戰績: ' + user.five_chess)
            ptt_bot.log('象棋戰績:' + user.chess)
            ptt_bot.log('簽名檔:' + user.signature_file)

            ptt_bot.log('=====================')

        except PTT.exceptions.NoSuchUser:
            print('無此使用者')

    try:
        user = ptt_bot.get_user('sdjfklsdj')
    except PTT.exceptions.NoSuchUser:
        print('無此使用者')


def push():
    test_post_list = [
        # ('Gossiping', 95692),
        # ('Test', 'QQQQQQ'),
        ('Test', 383),
        # ('Wanted', '1Teyovc3')
    ]

    # 分段推文
    content = '批踢踢實業坊，簡稱批踢踢、PTT，是一個臺灣電子布告欄（BBS），採用Telnet BBS技術運作，建立在台灣學術網路的資源之上，以學術性質為原始目的，提供線上言論空間。目前由國立臺灣大學電子布告欄系統研究社管理，大部份的系統原始碼由國立臺灣大學資訊工程學系的學生與校友進行維護，並且邀請法律專業人士擔任法律顧問。它有兩個分站，分別為批踢踢兔與批踢踢參。目前在批踢踢實業坊與批踢踢兔註冊總人數約150萬人，尖峰時段兩站超過15萬名使用者同時上線，擁有超過2萬個不同主題的看板，每日超過2萬篇新文章及50萬則推文被發表，是台灣使用人次最多的網路論壇之一。'
    # 短推文
    # content = '安安'
    # 連續重複推文
    #     content = '''安安
    # 安安
    # 安安
    # 安安
    # 安安
    #     '''

    testround: int = 3
    for (board, index) in test_post_list:
        for i in range(testround):
            if isinstance(index, int):
                ptt_bot.push(board, PTT.data_type.push_type.PUSH, content, post_index=index)
            else:
                ptt_bot.push(board, PTT.data_type.push_type.PUSH, content, post_aid=index)

    # Index = PTTBot.getNewestIndex(
    #     PTT.data_type.index_type.BBS,
    #     Board='Test'
    # )
    # PTTBot.push('Test', PTT.data_type.push_type.PUSH, Content, PostIndex=Index + 1)


def throw_waterball():
    ptt_id = 'DeepLearning'

    # TestWaterBall = [str(x) + '_' * 35 + ' 水球測試結尾' for x in range(30)]
    # # TestWaterBall = TestWaterBall * 3
    # TestWaterBall = '\n'.join(TestWaterBall)
    test_waterball = '水球測試1 :D\n水球測試2 :D'

    ptt_bot.throw_waterball(ptt_id, test_waterball)
    # time.sleep(3)


def get_waterball():
    # operate_type = PTT.data_type.waterball_operate_type.NOTHING
    # OperateType = PTT.data_type.waterball_operate_type.MAIL
    operate_type = PTT.data_type.waterball_operate_type.CLEAR

    while True:
        newest_index = ptt_bot.get_newest_index(PTT.data_type.index_type.MAIL)
        waterball_list = ptt_bot.get_waterball(operate_type)

        if waterball_list is None:
            return

        # print('Result:')
        for waterball in waterball_list:
            if waterball.type == PTT.data_type.waterball_type.CATCH:
                temp = '★' + waterball.target + ' '
            elif waterball.type == PTT.data_type.waterball_type.SEND:
                temp = 'To ' + waterball.target + ': '
            temp += waterball.content + ' [' + waterball.date + ']'
            print(temp)

        time.sleep(0.5)


def call_status():
    def show_call_status(call_status):
        if call_status == PTT.data_type.call_status.ON:
            print('呼叫器狀態[打開]')
        elif call_status == PTT.data_type.call_status.OFF:
            print('呼叫器狀態[關閉]')
        elif call_status == PTT.data_type.call_status.UNPLUG:
            print('呼叫器狀態[拔掉]')
        elif call_status == PTT.data_type.call_status.WATERPROOF:
            print('呼叫器狀態[防水]')
        elif call_status == PTT.data_type.call_status.FRIEND:
            print('呼叫器狀態[朋友]')
        else:
            print(f'Unknow call_status: {call_status}')

    for _ in range(5):
        current_call_status = ptt_bot.get_call_status()
        show_call_status(current_call_status)

    print('連續測試通過')

    init_call_status = random.randint(
        PTT.data_type.call_status.min_value, PTT.data_type.call_status.max_value
    )

    test_queue = [x for x in range(
        PTT.data_type.call_status.min_value, PTT.data_type.call_status.max_value + 1
    )]
    random.shuffle(test_queue)

    print('初始呼叫器狀態')
    show_call_status(init_call_status)
    print('測試切換呼叫器狀態順序')
    for CurrentTeststatus in test_queue:
        show_call_status(CurrentTeststatus)

    ptt_bot.set_call_status(init_call_status)
    current_call_status = ptt_bot.get_call_status()
    if current_call_status != init_call_status:
        print('設定初始呼叫器狀態: 不通過')
        return
    print('設定初始呼叫器狀態: 通過')

    for CurrentTeststatus in test_queue:
        print('準備設定呼叫器狀態')
        show_call_status(CurrentTeststatus)

        ptt_bot.set_call_status(CurrentTeststatus)
        current_call_status = ptt_bot.get_call_status()
        show_call_status(current_call_status)
        if current_call_status != CurrentTeststatus:
            print('設定呼叫器狀態: 不通過')
            return
        print('設定呼叫器狀態: 通過')

    print('呼叫器測試全數通過')


def give_money():
    for _ in range(3):
        ptt_bot.give_money('DeepLearning', 1)


def mail():
    content = '\r\n\r\n'.join(
        [
            '如有誤寄，對..對不起',
            'PyPtt 程式寄信測試內容',
            'github: https://tinyurl.com/umqff3v'
        ]
    )

    try:
        ptt_bot.mail(
            'sdjfkdsjfls',
            '程式寄信標題',
            content,
            0)
    except PTT.exceptions.NoSuchUser:
        pass

    ptt_bot.mail(
        ptt_id,
        '程式寄信標題',
        content,
        0,
        False)

    newest_index = ptt_bot.get_newest_index(
        PTT.data_type.index_type.MAIL)
    print(f'最新郵件編號 {newest_index}')
    # ptt_bot.del_mail(newest_index)


def has_new_mail():
    result = ptt_bot.has_new_mail()
    ptt_bot.log(f'{result} 封新信')

    result = ptt_bot.has_new_mail()
    ptt_bot.log(f'{result} 封新信')


ThreadBot = None


def threading_test():
    id1, password1 = get_password('Account3.txt')
    id2, password2 = get_password('Account.txt')

    def thread_func1():
        thread_bot1 = PTT.API()
        try:
            thread_bot1.login(
                id1,
                password1,
                #  kick_other_login=True
            )
        except PTT.exceptions.LoginError:
            thread_bot1.log('登入失敗')
            return

        thread_bot1.logout()
        print('1 多線程測試完成')

    def thread_func2():
        thread_bot2 = PTT.API()
        try:
            thread_bot2.login(
                id2,
                password2,
                #  kick_other_login=True
            )
        except PTT.exceptions.LoginError:
            thread_bot2.log('登入失敗')
            return

        thread_bot2.logout()
        print('2 多線程測試完成')

    t1 = threading.Thread(
        target=thread_func1
    )
    t2 = threading.Thread(
        target=thread_func2
    )

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # ThreadBot.log('Hi')
    sys.exit()


def get_board_list():
    board_list = ptt_bot.get_board_list()
    # print(' '.join(BoardList))
    print(f'總共有 {len(board_list)} 個板名')
    print(f'總共有 {len(set(board_list))} 個不重複板名')


def reply_post():
    reply_post_index = 383

    ptt_bot.reply_post(
        PTT.data_type.reply_type.BOARD,
        'Test',
        '測試回應到板上，如有打擾抱歉',
        post_index=reply_post_index)

    ptt_bot.reply_post(
        PTT.data_type.reply_type.MAIL,
        'Test',
        '測試回應到信箱，如有打擾抱歉',
        post_index=reply_post_index)

    ptt_bot.reply_post(
        PTT.data_type.reply_type.BOARD_MAIL,
        'Test',
        '測試回應到板上還有信箱，如有打擾抱歉',
        post_index=reply_post_index)


def set_board_title():
    from time import strftime

    test_board = 'QQboard'

    while True:
        time_format = strftime('%H:%M:%S')
        try:
            ptt_bot.set_board_title(
                test_board,
                f'現在時間 {time_format}'
            )
        except PTT.exceptions.ConnectionClosed:
            while True:
                try:
                    ptt_bot.login(
                        ptt_id,
                        password
                    )
                    break
                except PTT.exceptions.LoginError:
                    ptt_bot.log('登入失敗')
                    time.sleep(1)
                except PTT.exceptions.ConnectError:
                    ptt_bot.log('登入失敗')
                    time.sleep(1)
        print('已經更新時間 ' + time_format, end='\r')
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print('已經更新時間 ' + time_format)
            ptt_bot.set_board_title(
                test_board,
                f'[{test_board}]'
            )
            print('板標已經恢復')
            break


def mark_post():
    board = 'CodingMan'
    mark_type = PTT.data_type.mark_type.S

    ptt_bot.mark_post(
        mark_type,
        board,
        post_index=850
    )

    ptt_bot.mark_post(
        mark_type,
        board,
        post_index=851
    )

    # if mark_type == PTT.data_type.mark_type.D:
    #     ptt_bot.mark_post(
    #         PTT.data_type.mark_type.DeleteD,
    #         'CodingMan'
    #     )

    # ptt_bot.mark_post(
    #     mark_type,
    #     'QQBoard',
    #     post_index=2000
    # )

    # PTTBot.mark_post(
    #     mark_type,
    #     'CodingMan',
    #     post_index=2000
    # )


def get_favourite_board():
    favourite_board_list = ptt_bot.get_favourite_board()

    for board in favourite_board_list:
        buff = f'[{board.board}][{board.type}][{board.title}]'
        print(buff)


def get_board_info():
    #  《Gossiping》看板設定

    # b - 中文敘述: 綜合 ◎【八卦】沒有開放政問 珍惜帳號
    #     板主名單: arsonlolita/xianyao/Bignana/XXXXGAY
    # h - 公開狀態(是否隱形): 公開
    # g - 隱板時 可以 進入十大排行榜
    # e - 開放 非看板會員發文
    # y - 開放 回應文章
    # d - 開放 自刪文章                            發文與推文限制:
    # r - 開放 推薦文章                              登入次數 700 次以上
    # s - 開放 噓文                                  退文篇數 0 篇以下
    # f - 限制 快速連推文章, 最低間隔時間: 5 秒
    # i - 推文時 自動 記錄來源 IP                  名單編輯與其它: (需板主權限)
    # a - 推文時 不用對齊 開頭                       w)設定水桶 v)可見會員名單
    # k - 板主 可 刪除部份違規文字                   m)舉辦投票 o)投票名單
    # x - 轉錄文章 會 自動記錄，且 需要 發文權限     c)文章類別 n)發文注意事項
    # j - 未 設為冷靜模式                            p)進板畫面
    # 8 - 禁止 未滿十八歲進入

    # board_list = ptt_bot.get_board_list()
    # for board in board_list:
    #     board_info = ptt_bot.get_board_info(board)
    #
    #     if not board_info.is_push_record_ip:
    #         continue
    #     if board_info.is_push_aligned:
    #         continue
    #
    #     print(f'{board} !!!!!!!!!!')
    #     # break
    # return

    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
        test_board_list = [
            'Python',
            'L_LifePlan',
            'NDHU-sl103'
        ]
    else:
        test_board_list = [
            'WhoAmI'
        ]

    get_post_kind = True

    for board in test_board_list:
        board_info = ptt_bot.get_board_info(board, get_post_kind=get_post_kind)
        print('==============')
        print('板名: ', board_info.board)
        print('線上人數: ', board_info.online_user)
        print('中文敘述: ', board_info.chinese_des)
        print('板主: ', board_info.moderators)
        print('公開狀態(是否隱形): ', board_info.is_open)
        print('隱板時是否可進入十大排行榜: ', board_info.is_into_top_ten_when_hide)
        print('是否開放非看板會員發文: ', board_info.can_non_board_members_post)
        print('是否開放回應文章: ', board_info.can_reply_post)
        print('是否開放自刪文章: ', board_info.can_self_del_post)
        print('是否開放推薦文章: ', board_info.can_push_post)
        print('是否開放噓文: ', board_info.can_boo_post)
        print('是否可以快速連推文章: ', board_info.can_fast_push)
        print('推文最低間隔時間: ', board_info.min_interval)
        print('推文時是否記錄來源 IP: ', board_info.is_push_record_ip)
        print('推文時是否對齊開頭: ', board_info.is_push_aligned)
        print('板主是否可刪除部份違規文字: ', board_info.can_moderator_del_illegal_content)
        print('轉錄文章是否自動記錄，且是否需要發文權限: ',
              board_info.is_tran_post_auto_recorded_and_require_post_permissions)
        print('是否為冷靜模式: ', board_info.is_cool_mode)
        print('是否需要滿十八歲才可進入: ', board_info.is_require18)
        print('發文與推文限制登入次數需多少次以上: ', board_info.require_login_time)
        print('發文與推文限制退文篇數多少篇以下: ', board_info.require_illegal_post)

        if get_post_kind:
            print('發文種類:', ' '.join(board_info.post_kind))


def get_bottom_post_list():
    test_board_list = [
        'Wanted',
        'Python',
        'Gossiping'
    ]

    print('=' * 50)
    for board in test_board_list:

        bottom_post_list = ptt_bot.get_bottom_post_list(board)
        if len(bottom_post_list) == 0:
            print(f'{board} 板無置頂文章')
        else:
            print(f'{board} 共有 {len(bottom_post_list)} 置頂文章')
            for post in bottom_post_list:
                print(post.title)

        print('=' * 50)


def del_post():
    content = '''
此為 PyPtt 貼文測試內容，如有打擾請告知。
github: https://github.com/PttCodingMan/PyPtt
'''
    content = content.replace('\n', '\r\n')

    for _ in range(3):
        ptt_bot.post(
            # 看板
            'Test',
            # 標題
            'PyPtt 程式貼文測試',
            # 內文
            content,
            # 標題分類
            1,
            # 簽名檔
            0)

    index = ptt_bot.get_newest_index(PTT.data_type.index_type.BBS, 'Test')

    for i in range(5):
        current_index = index - int(i)
        try:
            ptt_bot.del_post('Test', post_index=current_index)
            ptt_bot.log(f'Test {current_index} 刪除成功')
        except PTT.exceptions.NoPermission:
            ptt_bot.log(f'Test {current_index} 無刪除權限')
        except PTT.exceptions.DeletedPost:
            ptt_bot.log(f'Test {current_index} 已經被刪除')
        except PTT.exceptions.NoSuchPost:
            ptt_bot.log(f'Test {current_index} 無此文章')


def bucket():
    ptt_bot.bucket(
        'QQBoard',
        7,
        'Bucket Reason',
        'CodingMan')


def search_user():
    user_list = ptt_bot.search_user(
        'abcd',
        min_page=1,
        max_page=2
    )
    print(user_list)
    print(len(user_list))

    # if 'abcd0800' in userlist:
    #     print('exist')
    # else:
    #     print('Not exist')


def get_mail():
    mail_index = ptt_bot.get_newest_index(PTT.data_type.index_type.MAIL)
    ptt_bot.log(
        '最新信件編號',
        mail_index)

    for i in reversed(range(1, mail_index + 1)):
        ptt_bot.log(
            '檢查信件編號',
            i)

        mail_info = ptt_bot.get_mail(i)

        print(mail_info.title)

    for _ in range(3):
        newest_index = ptt_bot.get_newest_index(PTT.data_type.index_type.MAIL)
        print(f'最新信箱編號 {newest_index}')
        mail_info = ptt_bot.get_mail(newest_index)

        if mail_info is not None:
            print(mail_info.author)

    mail_index = ptt_bot.get_newest_index(
        PTT.data_type.index_type.MAIL,
        search_type=PTT.data_type.mail_search_type.KEYWORD,
        search_condition='uPtt system')

    ptt_bot.log(
        '最新信件編號',
        mail_index)

    for i in reversed(range(1, mail_index + 1)):
        ptt_bot.log(
            '檢查信件編號',
            i)

        mail_info = ptt_bot.get_mail(
            i,
            search_type=PTT.data_type.mail_search_type.KEYWORD,
            search_condition='uPtt system')

        print(mail_info.title)

    search_list = [
        (PTT.data_type.mail_search_type.KEYWORD, 'uPtt'),
        (PTT.data_type.mail_search_type.KEYWORD, 'key')
    ]

    mail_index = ptt_bot.get_newest_index(
        PTT.data_type.index_type.MAIL,
        search_list=search_list)

    for i in reversed(range(1, mail_index + 1)):
        ptt_bot.log(
            '檢查信件編號',
            i)

        mail_info = ptt_bot.get_mail(
            i,
            search_list=search_list)

        print(mail_info.title)


def mail_recviver():
    while True:
        # ptt_bot.config.log_level = PTT.log.level.TRACE
        newest_index = ptt_bot.get_newest_index(PTT.data_type.index_type.MAIL)
        # ptt_bot.config.log_level = PTT.log.level.INFO
        ptt_bot.log(f'最新信箱編號 {newest_index}')
        #
        # user = ptt_bot.get_user(ptt_id)
        # ptt_bot.log(f'信箱狀態: {user.mail_status}')

        for index in range(1, newest_index + 1):
            mail_info = ptt_bot.get_mail(newest_index)
            print(mail_info.author)
            print(mail_info.content)
            ptt_bot.del_mail(index)

        print('完成休息')
        time.sleep(3)


def change_pw():
    ptt_bot.change_pw(password)


if __name__ == '__main__':
    print('Welcome to PyPtt v ' + PTT.version.V + ' test case')

    try:
        # init()
        # threading_test()
        ptt_bot = PTT.API(
            # log_level=PTT.log.level.TRACE,
            # log_level=PTT.log.level.DEBUG,
            # host=PTT.data_type.host_type.PTT2

            # for 本機測試
            # connect_mode=PTT.connect_core.connect_mode.TELNET,
            # host=PTT.data_type.host_type.LOCALHOST,
            # port=8888,

            # for 自定義 url 測試
            # connect_mode=PTT.connect_core.connect_mode.TELNET,
            # host='localhost',
            # port=8888,

            # language=PTT.i18n.language.ENGLISH
        )

        if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
            ptt_id, password = get_password('test_account_1.txt')
        else:
            ptt_id, password = get_password('test_account_2.txt')
        try:
            ptt_bot.login(
                ptt_id,
                password,
                # kick_other_login=True
            )
        except PTT.exceptions.LoginError:
            ptt_bot.log('登入失敗')
            sys.exit()
        except PTT.exceptions.WrongIDorPassword:
            ptt_bot.log('帳號密碼錯誤')
            sys.exit()
        except PTT.exceptions.LoginTooOften:
            ptt_bot.log('請稍等一下再登入')
            sys.exit()

        if ptt_bot.unregistered_user:
            print('未註冊使用者')

            if ptt_bot.process_picks != 0:
                print(f'註冊單處理順位 {ptt_bot.process_picks}')

        if ptt_bot.registered_user:
            print('已註冊使用者')

        ###################################

        ###################################

        # performance_test()

        # get_post()
        # get_post_with_condition()
        # post()
        # get_newest_index()
        # crawl_board()
        # crawl_board_with_condition()
        # push()
        # get_user()
        # throw_waterball()
        # get_waterball()
        # call_status()
        # give_money()
        # mail()
        # has_new_mail()
        # get_board_list()
        # get_board_info()
        # reply_post()
        # get_favourite_board()
        # search_user()
        # get_mail()
        # mail_recviver()
        # change_pw()
        # get_aid_from_url()
        # get_bottom_post_list()
        # del_post()

        # bucket()
        # set_board_title()
        # mark_post()


    except Exception as e:
        print(type(e))
        traceback.print_tb(e.__traceback__)
        print(e)
    except KeyboardInterrupt:
        pass

    ptt_bot.logout()
