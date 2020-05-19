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
        with open('log.txt', 'a', encoding='utf-8') as F:
            F.write(msg + '\n')

    ptt_bot = PTT.API(
        log_handler=handler
    )
    ptt_bot.log('Test log')


def performance_test():
    test_time = 100
    print(f'效能測試 get_time {test_time} 次')

    start_time = time.time()
    for _ in range(test_time):
        ptt_time = ptt_bot.get_time()

        if ptt_time is None:
            print('PTT_TIME is None')
            break
        print(ptt_time)
    end_time = time.time()
    ptt_bot.logout()
    print('Performance Test WebSocket ' + str(
        round(end_time - start_time, 2)) + ' s')

    print('Performance Test finish')
    sys.exit()


def get_post():
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
            ('Gossiping', '1TU65Wi_'),
            ('Gossiping', '1TWadtnq'),
            ('Gossiping', '1TZBBkWP'),
            ('Gossiping', '1UDnXefr'),
            ('joke', '1Tc6G9eQ'),
            # 135193
            ('Test', 575),
            # 待證文章
            ('Test', '1U3pLzi0'),
        ]
    else:
        test_post_list = [
            # PTT2
            # ('PttSuggest', 1),
            # ('PttSuggest', '0z7TVw00'),
            # 文章格式錯誤
            # 發信站:
            # ('PttSuggest', '1EbQObff'),
            # 文章起始消失跳躍，導致沒有結尾 (已經修正)
            # ('WhoAmI', '1Tc0ooap'),
            # Test
            # 文章格式錯誤
            # 瞎改
            # ('Test', '1Sp1W7Fi'),
            # ('Test', '1TXRkuDW'),
            # ('WhoAmI', '1TqJhzQH')
        ]

    def show(name, value):
        if value is not None:
            print(f'{name} [{value}]')
        else:
            print(f'無{name}')

    query = False

    for (board, index) in test_post_list:
        try:
            if isinstance(index, int):
                post_info = ptt_bot.get_post(
                    board,
                    post_index=index,
                    # SearchType=PTT.data_type.post_search_type.KEYWORD,
                    # SearchCondition='公告',
                    query=query,
                )
            else:
                post_info = ptt_bot.get_post(
                    board,
                    post_aid=index,
                    # SearchType=PTT.data_type.post_search_type.KEYWORD,
                    # SearchCondition='公告',
                    query=query,
                )
            if post_info is None:
                print('Empty')
                continue

            if not post_info.pass_format_check:
                print('文章格式錯誤')
                continue

            if post_info.is_lock:
                print('鎖文狀態')
                continue

            # show('Origin Post\n', post.origin_post)
            print('Origin Post\n' + post_info.origin_post)
            print('=' * 30 + ' Origin Post Finish')
            show('Board', post_info.board)
            show('AID', post_info.aid)
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

                print(
                    f'Total {push_count} Pushs {boo_count} Boo {arrow_count} Arrow = {push_count - boo_count}'
                )
        except Exception as e:

            traceback.print_tb(e.__traceback__)
            print(e)


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
            search_condition=condition,
        )
        print(f'{board} 最新文章編號 {index}')

        for i in range(test_range):
            post = ptt_bot.get_post(
                board,
                post_index=index - i,
                # PostIndex=611,
                search_type=search_type,
                search_condition=condition,
                query=query
            )

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


def post():
    content = '''
此為 PyPtt 貼文測試內容，如有打擾請告知。
github: https://tinyurl.com/umqff3v

開發手冊: https://hackmd.io/@CodingMan/PTTLibraryManual
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
            0
        )


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

    for board in test_board_list:
        for _ in range(100):
            index = ptt_bot.get_newest_index(PTT.data_type.index_type.BBS, board=board)
            print(f'{board} 最新文章編號 {index}')

    index = ptt_bot.get_newest_index(PTT.data_type.index_type.MAIL)
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
                        board=TestBoard
                    )
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
                        query=query
                    )
                elif index_type == 'AID':

                    start_aid = '1TnDKzxw'
                    end_aid = '1TnCPFGu'

                    error_post_list, del_post_list = ptt_bot.crawl_board(
                        PTT.data_type.crawl_type.BBS,
                        crawlHandler,
                        TestBoard,
                        start_aid=start_aid,
                        end_aid=end_aid
                    )
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
                    board=TestBoard
                )
                end_page = newest_index

                start_page = end_page - test_range + 1

                print(f'預備爬行 {TestBoard} 最新頁數 {newest_index}')
                print(f'預備爬行 {TestBoard} 編號 {start_page} ~ {end_page} 文章')

                error_post_list, del_post_list = ptt_bot.crawl_board(
                    PTT.data_type.crawl_type.WEB,
                    crawlHandler,
                    TestBoard,
                    start_page=start_page,
                    end_page=end_page
                    # Query=Query
                )

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

    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
        test_list = [
            # ptt1
            ('Stock', PTT.data_type.post_search_type.KEYWORD, '盤中閒聊'),
            ('Baseball', PTT.data_type.post_search_type.PUSH, '20')
        ]
    else:
        test_list = [
            ('WhoAmI', PTT.data_type.post_search_type.KEYWORD, '[閒聊]'),
            ('WhoAmI', PTT.data_type.post_search_type.PUSH, '10')
        ]

    test_range = 100

    for (board, search_type, search_condition) in test_list:
        show_condition(board, search_type, search_condition)
        newest_index = ptt_bot.get_newest_index(
            PTT.data_type.index_type.BBS,
            board,
            search_type=search_type,
            search_condition=search_condition,
        )
        print(f'{board} 最新文章編號 {newest_index}')

        start_index = newest_index - test_range + 1

        error_post_list, del_post_list = ptt_bot.crawl_board(
            PTT.data_type.crawl_type.BBS,
            crawlHandler,
            board,
            start_index=start_index,
            end_index=newest_index,
            search_type=search_type,
            search_condition=search_condition,
        )

        # print('標題: ' + Post.getTitle())
        print('=' * 50)


def get_user():
    try:
        user = ptt_bot.get_user('CodingMan')
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
        ('Test', 793),
        # ('Wanted', '1Teyovc3')
    ]

    content = '批踢踢實業坊，簡稱批踢踢、PTT，是一個臺灣電子布告欄（BBS），採用Telnet BBS技術運作，建立在台灣學術網路的資源之上，以學術性質為原始目的，提供線上言論空間。目前由國立臺灣大學電子布告欄系統研究社管理，大部份的系統原始碼由國立臺灣大學資訊工程學系的學生與校友進行維護，並且邀請法律專業人士擔任法律顧問。它有兩個分站，分別為批踢踢兔與批踢踢參。目前在批踢踢實業坊與批踢踢兔註冊總人數約150萬人，尖峰時段兩站超過15萬名使用者同時上線，擁有超過2萬個不同主題的看板，每日超過2萬篇新文章及50萬則推文被發表，是台灣使用人次最多的網路論壇之一。'
    testround: int = 1
    for (board, index) in test_post_list:
        for i in range(testround):
            if isinstance(index, int):
                ptt_bot.push(board, PTT.data_type.push_type.PUSH, content + str(i), post_index=index)
            else:
                ptt_bot.push(board, PTT.data_type.push_type.PUSH, content + str(i), post_aid=index)

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
            0
        )
    except PTT.exceptions.NoSuchUser:
        pass

    ptt_bot.mail(
        ptt_id,
        '程式寄信標題',
        content,
        0
    )

    newest_index = ptt_bot.get_newest_index(PTT.data_type.index_type.MAIL)
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
    reply_post_index = 461

    ptt_bot.reply_post(
        PTT.data_type.reply_type.BOARD,
        'Test',
        '測試回應到板上，如有打擾抱歉',
        post_index=reply_post_index
    )

    ptt_bot.reply_post(
        PTT.data_type.reply_type.MAIL,
        'Test',
        '測試回應到信箱，如有打擾抱歉',
        post_index=reply_post_index
    )

    ptt_bot.reply_post(
        PTT.data_type.reply_type.BOARD_MAIL,
        'Test',
        '測試回應到板上還有信箱，如有打擾抱歉',
        post_index=reply_post_index
    )


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
    mark_type = PTT.data_type.mark_type.S

    # PTTBot.markPost(
    #     mark_type,
    #     'CodingMan',
    #     PostIndex=2
    # )

    # PTTBot.markPost(
    #     mark_type,
    #     'CodingMan',
    #     PostIndex=3
    # )

    # PTTBot.markPost(
    #     mark_type,
    #     'CodingMan',
    #     PostIndex=4
    # )

    # if mark_type == PTT.data_type.mark_type.D:
    #     PTTBot.markPost(
    #         PTT.data_type.mark_type.DeleteD,
    #         'CodingMan',
    #         PostIndex=4
    #     )

    ptt_bot.mark_post(
        mark_type,
        'QQBoard',
        post_index=2000
    )

    # PTTBot.mark_post(
    #     mark_type,
    #     'give',
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

    board_list = ptt_bot.get_board_list()
    for board in board_list:
        board_info = ptt_bot.get_board_info(board)

        if not board_info.is_push_record_ip:
            continue
        if board_info.is_push_aligned:
            continue

        print(f'{board} !!!!!!!!!!')
        # break
    return

    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
        board_info = ptt_bot.get_board_info('Gossiping')
    else:
        board_info = ptt_bot.get_board_info('WhoAmI')
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


def bucket():
    ptt_bot.bucket(
        'QQBoard',
        7,
        'Bucket Reason',
        'CodingMan'
    )


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
    for _ in range(3):
        newest_index = ptt_bot.get_newest_index(PTT.data_type.index_type.MAIL)
        print(f'最新信箱編號 {newest_index}')
        mail_info = ptt_bot.get_mail(newest_index)

        if mail_info is not None:
            # print(mail_info.origin_mail)
            print(mail_info.author)
            # print(mail_info.title)
            # print(mail_info.date)
            # print(mail_info.content)
            # print(mail_info.ip)
            # print(mail_info.location)

        # if newest_index > 1:
        #     mail_info = ptt_bot.get_mail(newest_index - 1)
        #     if mail_info is not None:
        #         print(mail_info.author)
        #         print(mail_info.title)
        #         print(mail_info.date)
        #         print(mail_info.content)
        #         print(mail_info.ip)
        #         print(mail_info.location)


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

    RunCI = False
    TravisCI = False
    if len(sys.argv) == 2:
        if sys.argv[1] == '-ci':
            RunCI = True

    if RunCI:

        ptt_id = os.getenv('PTTLibrary_ID')
        password = os.getenv('PTTLibrary_Password')
        if ptt_id is None or password is None:
            print('從環境變數取得帳號密碼失敗')
            ptt_id, password = get_password('Account.txt')
            TravisCI = False
        else:
            TravisCI = True

        init()
        ptt_bot = PTT.API(
            # log_level=PTT.log.level.TRACE,
        )
        try:
            ptt_bot.login(
                ptt_id,
                password,
                kick_other_login=True
            )
            pass
        except PTT.exceptions.LoginError:
            ptt_bot.log('登入失敗')
            sys.exit(1)


        # 基準測試

        def showTestResult(board, IndexAID, result):
            if result:
                if isinstance(IndexAID, int):
                    print(f'{board} index {IndexAID} 測試通過')
                else:
                    print(f'{board} AID {IndexAID} 測試通過')
            else:
                if isinstance(IndexAID, int):
                    print(f'{board} index {IndexAID} 測試失敗')
                else:
                    print(f'{board} AID {IndexAID} 測試失敗')
                    ptt_bot.logout()
                    sys.exit(1)


        def get_post_test_func(board, IndexAID, targetEx, checkformat, checkStr):
            try:
                if isinstance(IndexAID, int):
                    post_info = ptt_bot.get_post(
                        board,
                        post_index=IndexAID,
                    )
                else:
                    post_info = ptt_bot.get_post(
                        board,
                        post_aid=IndexAID,
                    )
            except Exception as e:
                if targetEx is not None and isinstance(e, targetEx):
                    showTestResult(board, IndexAID, True)
                    return
                showTestResult(board, IndexAID, False)

                traceback.print_tb(e.__traceback__)
                print(e)
                ptt_bot.logout()
                sys.exit(1)

            if checkStr is None and targetEx is None and not checkformat:
                print(post_info.content)

            if checkformat and not post_info.pass_format_check:
                showTestResult(board, IndexAID, True)
                return

            if checkStr is not None and checkStr not in post_info.content:
                ptt_bot.logout()
                sys.exit(1)

            if isinstance(IndexAID, int):
                print(f'{board} index {IndexAID} 測試通過')
            else:
                print(f'{board} AID {IndexAID} 測試通過')


        try:

            TestPostList = [
                ('Python', 1, None, False, '總算可以來想想板的走向了..XD'),
                ('NotExitBoard', 1, PTT.exceptions.NoSuchBoard, False, None),
                ('Python', '1TJH_XY0', None, False, '大家嗨，我是 CodingMan'),
                # 文章格式錯誤
                ('Steam', 4444, None, True, None),
                # 文章格式錯誤
                ('movie', 457, None, True, None),
                ('Gossiping', '1TU65Wi_', None, False, None),
                ('joke', '1Tc6G9eQ', None, False, None),
                # 待證文章
                ('Test', '1U3pLzi0', None, False, None),
            ]

            for b, i, ex, check_format, c in TestPostList:
                get_post_test_func(b, i, ex, check_format, c)

            print('取得文章測試全部通過')

            test_board_list = [
                'Wanted',
                'Gossiping',
                'Test',
                'Stock',
                'movie'
            ]

            for test_board in test_board_list:
                BasicIndex = 0
                for _ in range(50):
                    index = ptt_bot.get_newest_index(
                        PTT.data_type.index_type.BBS,
                        board=test_board
                    )

                    if BasicIndex == 0:
                        print(f'{test_board} 最新文章編號 {index}')
                        BasicIndex = index
                    elif abs(BasicIndex - index) > 5:
                        print(f'{test_board} 最新文章編號 {index}')
                        print(f'BasicIndex {BasicIndex}')
                        print(f'Index {index}')
                        print('取得看板最新文章編號測試失敗')

                        ptt_bot.logout()
                        sys.exit(1)
            print('取得看板最新文章編號測試全部通過')

            Title = 'PyPtt 程式貼文基準測試標題'
            content = f'''
PyPtt v {ptt_bot.get_version()}

PyPtt 程式貼文基準測試內文

この日本のベンチマーク
'''
            if TravisCI:
                content = '''
此次測試由 Travis CI 啟動
''' + content
            else:
                content = f'''
此次測試由 {ptt_id} 啟動
''' + content
            content = content.replace('\n', '\r\n')

            basic_board = 'Test'
            # 貼出基準文章
            ptt_bot.post(
                basic_board,
                Title,
                content,
                1,
                1
            )

            # 取得 Test 最新文章編號
            index = ptt_bot.get_newest_index(
                PTT.data_type.index_type.BBS,
                board=basic_board
            )

            # 搜尋基準文章
            basic_post_aid = None
            basic_post_index = 0
            for i in range(5):

                post_info = ptt_bot.get_post(
                    basic_board,
                    post_index=index - i,
                )

                if ptt_id in post_info.author and 'PyPtt 程式貼文基準測試內文' in post_info.content and \
                        Title in post_info.title:
                    print('使用文章編號取得基準文章成功')
                    post_info = ptt_bot.get_post(
                        basic_board,
                        post_aid=post_info.aid,
                    )
                    if ptt_id in post_info.author and 'PyPtt 程式貼文基準測試內文' in post_info.content and \
                            Title in post_info.title:
                        print('使用文章代碼取得基準文章成功')
                        basic_post_aid = post_info.aid
                        basic_post_index = index - i
                        break

            if basic_post_aid is None:
                print('取得基準文章失敗')
                ptt_bot.logout()
                sys.exit(1)
            print('取得基準文章成功')
            print('貼文測試全部通過')

            try:
                Content1 = '編號推文基準文字123'
                ptt_bot.push(basic_board, PTT.data_type.push_type.PUSH,
                             Content1, post_aid='QQQQQQQ')
                print('推文反向測試失敗')
                ptt_bot.logout()
                sys.exit(1)
            except PTT.exceptions.NoSuchPost:
                print('推文反向測試通過')

            try:
                index = ptt_bot.get_newest_index(
                    PTT.data_type.index_type.BBS,
                    board=basic_board
                )
                Content1 = '編號推文基準文字123'
                ptt_bot.push(basic_board, PTT.data_type.push_type.PUSH,
                             Content1, post_index=index + 1)
                print('推文反向測試失敗')
                ptt_bot.logout()
                sys.exit(1)
            except ValueError:
                print('推文反向測試通過')

            Content1 = '編號推文基準文字123'
            ptt_bot.push(basic_board, PTT.data_type.push_type.PUSH,
                         Content1, post_index=basic_post_index)

            Content2 = '代碼推文基準文字123'
            ptt_bot.push(basic_board, PTT.data_type.push_type.PUSH,
                         Content2, post_aid=basic_post_aid)

            post_info = ptt_bot.get_post(
                basic_board,
                post_aid=basic_post_aid,
            )

            Content1Check = False
            Content2Check = False
            for push in post_info.push_list:
                if Content1 in push.content:
                    Content1Check = True
                if Content2 in push.content:
                    Content2Check = True

            if not Content1Check:
                print('編號推文基準測試失敗')
                ptt_bot.logout()
                sys.exit(1)
            print('編號推文基準測試成功')
            if not Content2Check:
                print('代碼推文基準測試失敗')
                ptt_bot.logout()
                sys.exit(1)
            print('代碼推文基準測試成功')

            content = '推文基準測試全部通過'
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)

            test_list = [
                ('Python', PTT.data_type.post_search_type.KEYWORD, '[公告]'),
                ('ALLPOST', PTT.data_type.post_search_type.KEYWORD, '(Wanted)'),
                ('Wanted', PTT.data_type.post_search_type.KEYWORD, '(本文已被刪除)'),
                ('ALLPOST', PTT.data_type.post_search_type.KEYWORD, '(Gossiping)'),
                ('Gossiping', PTT.data_type.post_search_type.KEYWORD, '普悠瑪'),
            ]

            test_range = 1

            for (test_board, search_type, condition) in test_list:
                show_condition(test_board, search_type, condition)
                index = ptt_bot.get_newest_index(
                    PTT.data_type.index_type.BBS,
                    test_board,
                    search_type=search_type,
                    search_condition=condition,
                )
                print(f'{test_board} 最新文章編號 {index}')

                for i in range(test_range):
                    post_info = ptt_bot.get_post(
                        test_board,
                        post_index=index - i,
                        search_type=search_type,
                        search_condition=condition,
                        query=False
                    )

                    print('列表日期:')
                    print(post_info.list_date)
                    print('作者:')
                    print(post_info.author)
                    print('標題:')
                    print(post_info.title)

                    if post_info.delete_status == PTT.data_type.post_delete_status.NOT_DELETED:
                        if not query:
                            print('內文:')
                            print(post_info.content)
                    elif post_info.delete_status == PTT.data_type.post_delete_status.AUTHOR:
                        print('文章被作者刪除')
                    elif post_info.delete_status == PTT.data_type.post_delete_status.MODERATOR:
                        print('文章被版主刪除')
                    print('=' * 50)

                content = f'{test_board} 取得文章測試完成'
                ptt_bot.push('Test', PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)

            content = '取得文章測試全部通過'
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)

            content = '貼文測試全部通過'
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)

            test_board_list = [
                'Wanted',
                'joke',
                'Gossiping',
                'C_Chat'
            ]

            # 改成 10 篇，不然 100 篇太耗時間了
            Range = 10
            for test_board in test_board_list:
                newest_index = ptt_bot.get_newest_index(
                    PTT.data_type.index_type.BBS,
                    board=test_board
                ) - 10000
                # 到很久之前的文章去才不會撞到被刪掉的文章

                error_post_list, del_post_list = ptt_bot.crawl_board(
                    PTT.data_type.crawl_type.BBS,
                    crawlHandler,
                    test_board,
                    start_index=newest_index - Range + 1,
                    end_index=newest_index,
                    query=query
                )

                StartPost = None
                offset = 0
                while True:
                    StartPost = ptt_bot.get_post(
                        test_board,
                        post_index=newest_index - Range + 1 - offset,
                    )
                    offset += 1
                    if StartPost is None:
                        continue
                    if StartPost.aid is None:
                        continue
                    break

                EndPost = None
                offset = 0
                while True:
                    EndPost = ptt_bot.get_post(
                        test_board,
                        post_index=newest_index + offset,
                    )
                    offset += 1
                    if EndPost is None:
                        continue
                    if EndPost.aid is None:
                        continue
                    break

                print(test_board)
                print(f'StartPost index {newest_index - Range + 1}')
                print(f'EndPost index {newest_index}')

                error_post_list, del_post_list = ptt_bot.crawl_board(
                    PTT.data_type.crawl_type.BBS,
                    crawlHandler,
                    test_board,
                    start_aid=StartPost.aid,
                    end_aid=EndPost.aid
                )
                content = f'{test_board} 爬板測試完成'
                ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)

            content = '爬板測試全部完成'
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)

            user = ptt_bot.get_user(ptt_id)
            if user is None:
                print('取得使用者測試失敗')
                content = '取得使用者測試失敗'
                ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)
                ptt_bot.logout()
                sys.exit(1)

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

            try:
                user = ptt_bot.get_user('sdjfklsdj')
                print('取得使用者反向測試失敗')
                content = '取得使用者反向測試失敗'
                ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)

                ptt_bot.logout()
                sys.exit(1)
            except PTT.exceptions.NoSuchUser:
                print('取得使用者反向測試通過')

            NewMail1 = ptt_bot.has_new_mail()
            print(f'有 {NewMail1} 封新信')
            content = '取得幾封新信測試通過'
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)

            try:
                ptt_bot.mail(
                    'sdjfkdsjfls',
                    '程式寄信標題',
                    content,
                    0
                )

                content = '寄信反向測試失敗'
                print(content)
                ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)
                ptt_bot.logout()
                sys.exit(1)

            except PTT.exceptions.NoSuchUser:
                content = '寄信反向測試成功'
                print(content)
                ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)

            content = '''如有誤寄，對..對不起
PyPtt 程式寄信測試內容

github: https://tinyurl.com/umqff3v
'''
            content = content.replace('\n', '\r\n')
            ptt_bot.mail(
                ptt_id,
                '程式寄信標題',
                content,
                0
            )

            NewMail2 = ptt_bot.has_new_mail()
            print(f'有 {NewMail2} 封新信')
            if NewMail2 > NewMail1:
                content = '寄信測試通過'
                ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)
            else:
                content = '寄信測試失敗'
                print(content)
                ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)
                ptt_bot.logout()
                sys.exit(1)

            content = '寄信測試成功'
            print(content)
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)

            board_list = ptt_bot.get_board_list()
            print(f'總共有 {len(board_list)} 個板名')
            print(f'總共有 {len(set(board_list))} 個不重複板名')

            content = '取得全站看板測試通過'
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)
            content = f'總共有 {len(set(board_list))} 個不重複板名'
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)

            try:
                ptt_bot.get_board_info('NotExistBoard')

                print('取得看板資訊反向測試失敗')
                content = '取得看板資訊反向測試失敗'
                ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)

                ptt_bot.logout()
                sys.exit(1)
            except PTT.exceptions.NoSuchBoard:
                print('取得看板資訊反向測試成功')
                content = '取得看板資訊反向測試成功'
                ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)

            board_info = ptt_bot.get_board_info('Gossiping')
            print('板名: ', board_info.board)
            print('線上人數: ', board_info.online_user)
            # setting
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

            content = '取得看板資訊測試成功'
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)

            FBlist = ptt_bot.get_favourite_board()
            for test_board in FBlist:
                if test_board.board is None or test_board.type is None or test_board.title is None:
                    content = '取得我的最愛測試失敗'
                    ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                                 content, post_aid=basic_post_aid)
                    ptt_bot.logout()
                    sys.exit(1)

            content = '取得我的最愛測試成功'
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)

            user_list = ptt_bot.search_user(
                'coding'
            )
            if len(user_list) == 0:
                content = '查詢網友測試失敗'
                ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)
                ptt_bot.logout()
                sys.exit(1)
            content = '查詢網友測試成功'
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)

            ptt_bot.reply_post(
                PTT.data_type.reply_type.BOARD,
                basic_board,
                '使用文章編號測試回應到板上',
                post_index=basic_post_index
            )

            index = ptt_bot.get_newest_index(
                PTT.data_type.index_type.BBS,
                board=basic_board
            )

            TestPass = False
            for i in range(5):

                post_info = ptt_bot.get_post(
                    basic_board,
                    post_index=index - i,
                )

                if ptt_id in post_info.author and '使用文章編號測試回應到板上' in post_info.content:
                    TestPass = True
                    content = '使用文章編號測試回應到板上成功'
                    print(content)
                    ptt_bot.push(
                        basic_board, PTT.data_type.push_type.ARROW,
                        content, post_aid=basic_post_aid)
                    break
            if not TestPass:
                content = '使用文章編號測試回應到板上失敗'
                ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)
                ptt_bot.logout()
                sys.exit(1)

            ptt_bot.reply_post(
                PTT.data_type.reply_type.BOARD,
                basic_board,
                '使用文章ID測試回應到板上',
                post_aid=basic_post_aid
            )

            index = ptt_bot.get_newest_index(
                PTT.data_type.index_type.BBS,
                board=basic_board
            )

            TestPass = False
            for i in range(5):

                post_info = ptt_bot.get_post(
                    basic_board,
                    post_index=index - i,
                )

                if ptt_id in post_info.author and '使用文章ID測試回應到板上' in post_info.content:
                    TestPass = True
                    content = '使用文章ID測試回應到板上成功'
                    print(content)
                    ptt_bot.push(
                        basic_board, PTT.data_type.push_type.ARROW,
                        content, post_aid=basic_post_aid)
                    break
            if not TestPass:
                content = '使用文章ID測試回應到板上失敗'
                ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)
                ptt_bot.logout()
                sys.exit(1)

            if TravisCI:
                ID2 = os.getenv('PTTLibrary_ID2')
                Password2 = os.getenv('PTTLibrary_Password2')
            else:
                ID2, Password2 = get_password('Account2.txt')

            PTTBot2 = PTT.API(
                # log_level=PTT.log.level.TRACE,
            )
            try:
                PTTBot2.login(
                    ID2,
                    Password2,
                    # kick_other_login=True
                )
                pass
            except PTT.exceptions.LoginError:
                PTTBot2.log('PTTBot2登入失敗')
                sys.exit(1)

            operate_type = PTT.data_type.waterball_operate_type.CLEAR
            ptt_bot.get_waterball(operate_type)
            PTTBot2.get_waterball(operate_type)

            ptt_bot.set_call_status(PTT.data_type.call_status.OFF)
            PTTBot2.set_call_status(PTT.data_type.call_status.OFF)

            TestPass = False
            PTTBot2.throw_waterball(ptt_id, '水球測試基準訊息')
            waterball_list = ptt_bot.get_waterball(operate_type)
            for waterball_info in waterball_list:
                if not waterball_info.type == PTT.data_type.waterball_type.CATCH:
                    continue

                Target = waterball_info.target
                content = waterball_info.content

                print(f'收到來自 {Target} 的水球 [{content}]')

                if '水球測試基準訊息' in content:
                    TestPass = True
                    break

            if not TestPass:
                content = '水球測試基準測試失敗'
                print(content)
                ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                             content, post_aid=basic_post_aid)
                ptt_bot.logout()
                PTTBot2.logout()
                sys.exit(1)

            content = '水球測試基準測試成功'
            print(content)
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)
            PTTBot2.logout()

            content = '自動化測試全部完成'
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)

        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
            content = str(e)
            ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                         content, post_aid=basic_post_aid)
        except KeyboardInterrupt:
            pass

        ptt_bot.logout()
    else:
        ptt_id, password = get_password('Account3.txt')
        try:
            # init()
            # threading_test()
            ptt_bot = PTT.API(
                # log_level=PTT.log.level.TRACE,
                # log_level=PTT.log.level.DEBUG,
                # host=PTT.data_type.host_type.PTT2

                # for 本機測試
                # connect_mode=PTT.connect_core.connect_mode.TELNET,
                # host=PTT.data_type.host_type.LOCALhost,
                # port=8888,
            )
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
            get_newest_index()
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
            # get_post_index_test()
            # get_mail()
            # mail_recviver()
            # change_pw()

            # bucket()
            # set_board_title()
            # mark_post()


        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
        except KeyboardInterrupt:
            pass

        ptt_bot.logout()
