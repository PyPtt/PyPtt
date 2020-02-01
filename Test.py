import sys
import os
import time
import json
import random
import traceback
import threading

from PTTLibrary import PTT


def getPW(passfile):
    try:
        with open(passfile) as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        print('Please note PTT ID and Password in Account.txt')
        print('{"ID":"YourID", "Password":"YourPassword"}')
        sys.exit()

    return ID, Password


def Init():
    print('===正向===')
    print('===預設值===')
    PTT.Library()
    print('===中文顯示===')
    PTT.Library(language=PTT.Language.Chinese)
    print('===英文顯示===')
    PTT.Library(language=PTT.Language.English)
    print('===Log DEBUG===')
    PTT.Library(log_level=PTT.LogLevel.DEBUG)
    print('===Log INFO===')
    PTT.Library(log_level=PTT.LogLevel.INFO)
    print('===Log SLIENT===')
    PTT.Library(log_level=PTT.LogLevel.SILENT)
    print('===Log SLIENT======')

    print('===負向===')
    try:
        print('===語言 99===')
        PTT.Library(language=99)
    except ValueError:
        print('通過')
    except:
        print('沒通過')
        sys.exit(-1)
    print('===語言放字串===')
    try:
        PTT.Library(language='PTT.Language.English')
    except TypeError:
        print('通過')
    except:
        print('沒通過')
        sys.exit(-1)
    # print('===Telnet===')
    # PTT.Library(ConnectMode=PTT.ConnectMode.Telnet)
    # print('===WebSocket===')
    # PTT.Library(ConnectMode=PTT.ConnectMode.WebSocket)
    # print('===Log DEBUG===')
    # PTT.Library(LogLevel=PTT.LogLevel.DEBUG)
    # print('===Log INFO===')
    # PTT.Library(LogLevel=PTT.LogLevel.INFO)
    # print('===Log SLIENT===')
    # PTT.Library(LogLevel=PTT.LogLevel.SLIENT)
    # print('===Log SLIENT======')


def performance_test():
    test_time = 100
    print(f'效能測試 get_time {test_time} 次')

    start_time = time.time()
    for _ in range(test_time):
        ptt_time = PTTBot.get_time()

        if ptt_time is None:
            print('PTT_TIME is None')
            break
        print(ptt_time)
    end_time = time.time()
    PTTBot.logout()
    print('Performance Test WebSocket ' + str(
        round(end_time - start_time, 2)) + ' s')

    # PTTBot.log('等待五秒')
    # time.sleep(5)

    # PTTBot = PTT.Library(
    #     ConnectMode=PTT.ConnectMode.Telnet,
    #     LogLevel=PTT.LogLevel.SLIENT,
    #     # LogLevel=PTT.LogLevel.DEBUG,
    # )
    # try:
    #     PTTBot.login(ID, Password, KickOtherLogin=True)
    # except PTT.Exceptions.LoginError:
    #     PTTBot.log('登入失敗')
    #     sys.exit()
    # PTTBot.log('登入成功')

    # StartTime = time.time()
    # for _ in range(TestTime):
    #     PTT_TIME = PTTBot.get_time()

    #     if PTT_TIME is None:
    #         print('PTT_TIME is None')
    #         break
    #     # print(PTT_TIME)
    # end_time = time.time()

    # PTTBot.log('Performance Test Telnet ' +
    #            str(round(end_time - StartTime, 2)) + ' s')

    print('Performance Test finish')
    sys.exit()


def get_post():
    test_post_list = [
        # ('Python', 1),
        # ('NotExitBoard', 1),
        # ('Python', '1TJH_XY0'),
        # 文章格式錯誤
        # ('Steam', 4444),
        # ('Stock', 92324),
        # ('Stock', '1TVnEivO'),
        # 文章格式錯誤
        # ('movie', 457),
        # ('Gossiping', '1TU65Wi_'),
        # ('Gossiping', '1TWadtnq'),
        # ('Gossiping', '1TZBBkWP'),
        # ('joke', '1Tc6G9eQ'),
        # 135193
        # ('Test', 575),
        # 待證文章
        # ('Test', '1U3pLzi0'),

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
        # 1T4yyKuE
        # 1TXRkuDW
        # 1TYTfSZW
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
                post = PTTBot.get_post(
                    board,
                    post_index=index,
                    # SearchType=PTT.PostSearchType.Keyword,
                    # SearchCondition='公告',
                    query=query,
                )
            else:
                post = PTTBot.get_post(
                    board,
                    post_aid=index,
                    # SearchType=PTT.PostSearchType.Keyword,
                    # SearchCondition='公告',
                    query=query,
                )
            if post is None:
                print('Empty')
                continue

            if not post.is_format_check():
                print('文章格式錯誤')
                continue

            if post.is_lock():
                print('鎖文狀態')
                continue

            # show('Origin Post\n', post.get_origin_post())
            print('Origin Post\n' + post.get_origin_post())
            print('=' * 30 + ' Origin Post Finish')
            show('Board', post.get_board())
            show('AID', post.get_aid())
            show('Author', post.get_author())
            show('List Date', post.get_list_date())
            show('Title', post.get_title())
            show('Money', post.get_money())
            show('URL', post.get_web_url())

            if post.is_unconfirmed():
                print('待證實文章')

            if not query:
                show('Date', post.get_date())
                show('Content', post.get_content())
                show('IP', post.get_ip())
                show('Location', post.get_location())

                # 在文章列表上的日期

                push_count = 0
                boo_count = 0
                arrow_count = 0

                for push in post.get_push_list():
                    #     print(Push.getType())
                    #     print(Push.getAuthor())
                    #     print(Push.getContent())
                    #     print(Push.getIP())
                    #     print(Push.get_time())

                    if push.get_type() == PTT.PushType.Push:
                        push_count += 1
                        push_type = '推'
                    if push.get_type() == PTT.PushType.Boo:
                        boo_count += 1
                        push_type = '噓'
                    if push.get_type() == PTT.PushType.Arrow:
                        arrow_count += 1
                        push_type = '→'

                    author = push.get_author()
                    content = push.get_content()

                    # Buffer = f'[{Author}] 給了一個{Type} 說 [{Content}]'
                    # if Push.getIP() is not None:
                    #     Buffer += f' 來自 [{Push.getIP()}]'
                    # Buffer += f' 時間是 [{Push.get_time()}]'

                    if push.get_ip() is not None:
                        buffer = f'{push_type} {author}: {content} {push.get_ip()} {push.get_time()}'
                    else:
                        buffer = f'{push_type} {author}: {content} {push.get_time()}'
                    print(buffer)

                print(
                    f'Total {push_count} Pushs {boo_count} Boo {arrow_count} Arrow = {push_count - boo_count}'
                )
        except Exception as e:

            traceback.print_tb(e.__traceback__)
            print(e)


TestList = [
    ('Wanted', PTT.PostSearchType.Keyword, '[公告]'),
    ('Wanted', PTT.PostSearchType.Author, 'gogin'),
    ('Wanted', PTT.PostSearchType.Push, '10'),
    ('Wanted', PTT.PostSearchType.Mark, 'm'),
    ('Wanted', PTT.PostSearchType.Money, '5'),
    ('Gossiping', PTT.PostSearchType.Keyword, '[公告]'),
    ('Gossiping', PTT.PostSearchType.Author, 'ReDmango'),
    ('Gossiping', PTT.PostSearchType.Push, '10'),
    ('Gossiping', PTT.PostSearchType.Mark, 'm'),
    ('Gossiping', PTT.PostSearchType.Money, '5'),

    ('Gossiping', PTT.PostSearchType.Push, '-100'),
    ('Gossiping', PTT.PostSearchType.Push, '150'),
]


def showCondition(Board, SearchType, Condition):
    if SearchType == PTT.PostSearchType.Keyword:
        Type = '關鍵字'
    if SearchType == PTT.PostSearchType.Author:
        Type = '作者'
    if SearchType == PTT.PostSearchType.Push:
        Type = '推文數'
    if SearchType == PTT.PostSearchType.Mark:
        Type = '標記'
    if SearchType == PTT.PostSearchType.Money:
        Type = '稿酬'

    print(f'{Board} 使用 {Type} 搜尋 {Condition}')


def get_post_with_condition():
    # PTT1
    test_list = [
        ('Python', PTT.PostSearchType.Keyword, '[公告]'),
        ('ALLPOST', PTT.PostSearchType.Keyword, '(Wanted)'),
        ('Wanted', PTT.PostSearchType.Keyword, '(本文已被刪除)'),
        ('ALLPOST', PTT.PostSearchType.Keyword, '(Gossiping)'),
        ('Gossiping', PTT.PostSearchType.Keyword, '普悠瑪'),
        # PTT2
        # ('PttSuggest', PTT.PostSearchType.Keyword, '[問題]'),
        # ('PttSuggest', PTT.PostSearchType.Push, '10'),
    ]

    test_range = 1
    query = False

    for (board, search_type, condition) in test_list:
        showCondition(board, search_type, condition)
        index = PTTBot.get_newest_index(
            PTT.IndexType.BBS,
            board,
            search_type=search_type,
            search_condition=condition,
        )
        print(f'{board} 最新文章編號 {index}')

        for i in range(test_range):
            post = PTTBot.get_post(
                board,
                post_index=index - i,
                # PostIndex=611,
                search_type=search_type,
                search_condition=condition,
                query=query
            )

            print('列表日期:')
            print(post.get_list_date())
            print('作者:')
            print(post.get_author())
            print('標題:')
            print(post.get_title())

            if post.get_delete_status() == PTT.PostDeleteStatus.NotDeleted:
                if not query:
                    print('內文:')
                    print(post.get_content())
            elif post.get_delete_status() == PTT.PostDeleteStatus.ByAuthor:
                print('文章被作者刪除')
            elif post.get_delete_status() == PTT.PostDeleteStatus.ByModerator:
                print('文章被版主刪除')
            print('=' * 50)

    # TestList = [
    #     ('Python', PTT.PostSearchType.Keyword, '[公告]')
    # ]

    # for (Board, SearchType, Condition) in TestList:
    #     index = PTTBot.getNewestIndex(
    #         PTT.IndexType.BBS,
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
    content = [
        '此為 PTT Library 貼文測試內容，如有打擾請告知。',
        'github: https://tinyurl.com/umqff3v',
        '開發手冊: https://hackmd.io/@CodingMan/PTTLibraryManual'
    ]
    content = '\r\n\r\n'.join(content)

    for _ in range(3):
        PTTBot.post(
            'Test',
            'PTT Library 程式貼文測試',
            content,
            1,
            0
        )


def get_newest_index():
    test_board_list = [
        'Wanted',
        'Gossiping',
        'Test',
        'Stock',
        'movie'

        # PTT2
        # 'PttSuggest',
        # 'Test',
        # 'WhoAmI',
        # 'CodingMan'
    ]

    for board in test_board_list:
        for _ in range(100):
            index = PTTBot.get_newest_index(PTT.IndexType.BBS, board=board)
            print(f'{board} 最新文章編號 {index}')


def showValue(Msg, Value):
    print(f'{Msg} =>{Value}<=')


def detectNone(Name, Obj, Enable=True):
    if Obj is None and Enable:
        raise ValueError(Name + ' is None')


Query = False


def crawlHandler(Post):
    global Query

    if Post.get_delete_status() != PTT.PostDeleteStatus.NotDeleted:
        if Post.get_delete_status() == PTT.PostDeleteStatus.ByModerator:
            # print(f'[版主刪除][{Post.getAuthor()}]')
            pass
        elif Post.get_delete_status() == PTT.PostDeleteStatus.ByAuthor:
            # print(f'[作者刪除][{Post.getAuthor()}]')
            pass
        elif Post.get_delete_status() == PTT.PostDeleteStatus.ByUnknown:
            # print(f'[不明刪除]')
            pass
        return

    # if Post.getTitle().startswith('Fw:') or Post.getTitle().startswith('轉'):
    # print(f'[{Post.get_aid()}][{Post.getAuthor()}][{Post.getTitle()}]')
    # print(f'[{Post.getContent()}]')

    # print(f'[{Post.getAuthor()}][{Post.getTitle()}]')

    PushNumber = Post.get_push_number()
    if PushNumber is not None:
        if PushNumber == '爆':
            pass
        elif PushNumber.startswith('X'):
            N = PushNumber[1:]
        else:
            if not PushNumber.isdigit():
                print(f'[{Post.get_aid()}][{Post.get_push_number()}]')
                print(f'[{Post.get_aid()}][{Post.get_push_number()}]')
                print(f'[{Post.get_aid()}][{Post.get_push_number()}]')
                raise ValueError()
        # print(f'[{Post.get_aid()}][{Post.getPushNumber()}]')

    detectNone('標題', Post.get_title())
    # detectNone('AID', Post.get_aid())
    detectNone('Author', Post.get_author())
    # detectNone('Money', Post.getMoney())
    detectNone('WebUrl', Post.get_web_url())
    # detectNone('ListDate', Post.getListDate())

    # if not Query:
    # detectNone('Date', Post.getDate())
    # detectNone('Content', Post.getContent())
    # detectNone('IP', Post.getIP())

    # time.sleep(0.2)


def crawl_board():
    global Query
    test_board_list = [
        # 'Test',
        'Wanted',
        'Gossiping',
        'Stock',
        'movie',
        'C_Chat',
        'Baseball',
        'NBA',
        'HatePolitics',

        # PTT2
        # 'Test',
        # 'WhoAmI',
        # 'PttSuggest'
    ]

    # CrawlType = PTT.IndexType.Web
    crawl_type = PTT.IndexType.BBS

    index_type = 'Index'

    test_range = 100
    test_round = 2

    for _ in range(test_round):

        for TestBoard in test_board_list:

            if crawl_type == PTT.IndexType.BBS:

                if index_type == 'Index':
                    newest_index = PTTBot.get_newest_index(
                        PTT.IndexType.BBS,
                        board=TestBoard
                    )
                    start_index = newest_index - test_range + 1

                    print(
                        f'預備爬行 {TestBoard} 編號 {start_index} ~ {newest_index} 文章')

                    print(f'TestBoard [{TestBoard}]')
                    error_post_list, del_post_list = PTTBot.crawl_board(
                        PTT.CrawlType.BBS,
                        crawlHandler,
                        TestBoard,
                        start_index=start_index,
                        end_index=newest_index,
                        query=Query
                    )
                elif index_type == 'AID':

                    start_aid = '1TnDKzxw'
                    end_aid = '1TnCPFGu'

                    error_post_list, del_post_list = PTTBot.crawl_board(
                        PTT.CrawlType.BBS,
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

            elif crawl_type == PTT.IndexType.Web:

                newest_index = PTTBot.get_newest_index(
                    PTT.IndexType.Web,
                    board=TestBoard
                )
                end_page = newest_index

                start_page = end_page - test_range + 1

                print(f'預備爬行 {TestBoard} 最新頁數 {newest_index}')
                print(f'預備爬行 {TestBoard} 編號 {start_page} ~ {end_page} 文章')

                error_post_list, del_post_list = PTTBot.crawl_board(
                    PTT.CrawlType.Web,
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
    #             PTT.IndexType.BBS,
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

    test_list = [
        ('Stock', PTT.PostSearchType.Keyword, '盤中閒聊'),
        ('Baseball', PTT.PostSearchType.Push, '20')
    ]

    test_range = 100

    for (board, search_type, search_condition) in test_list:
        showCondition(board, search_type, search_condition)
        newest_index = PTTBot.get_newest_index(
            PTT.IndexType.BBS,
            board,
            search_type=search_type,
            search_condition=search_condition,
        )
        print(f'{board} 最新文章編號 {newest_index}')

        start_index = newest_index - test_range + 1

        error_post_list, del_post_list = PTTBot.crawl_board(
            PTT.CrawlType.BBS,
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
        user = PTTBot.get_user('CodingMan')
        if user is None:
            return

        PTTBot.log('使用者ID: ' + user.get_id())
        PTTBot.log('使用者經濟狀況: ' + str(user.get_money()))
        PTTBot.log('登入次數: ' + str(user.get_login_time()))
        PTTBot.log('有效文章數: ' + str(user.get_legal_post()))
        PTTBot.log('退文文章數: ' + str(user.get_illegal_post()))
        PTTBot.log('目前動態: ' + user.get_state())
        PTTBot.log('信箱狀態: ' + user.get_mail())
        PTTBot.log('最後登入時間: ' + user.get_last_login())
        PTTBot.log('上次故鄉: ' + user.get_last_ip())
        PTTBot.log('五子棋戰績: ' + user.get_five_chess())
        PTTBot.log('象棋戰績:' + user.get_chess())
        PTTBot.log('簽名檔:' + user.get_signature_file())

    except PTT.Exceptions.NoSuchUser:
        print('無此使用者')

    try:
        user = PTTBot.get_user('sdjfklsdj')
    except PTT.Exceptions.NoSuchUser:
        print('無此使用者')


def push():
    test_post_list = [
        ('Gossiping', 95692),
        # ('Test', 'QQQQQQ'),
        # ('Test', 624),
        # ('Wanted', '1Teyovc3')
    ]

    content = '''
推文測試
'''
    testround: int = 10
    for (board, index) in test_post_list:
        for _ in range(testround):
            if isinstance(index, int):
                PTTBot.push(board, PTT.PushType.Push, content, post_index=index)
            else:
                PTTBot.push(board, PTT.PushType.Push, content, post_aid=index)

    # Index = PTTBot.getNewestIndex(
    #     PTT.IndexType.BBS,
    #     Board='Test'
    # )
    # PTTBot.push('Test', PTT.PushType.Push, Content, PostIndex=Index + 1)


def throw_waterball():
    pttid = 'DeepLearning'

    # TestWaterBall = [str(x) + '_' * 35 + ' 水球測試結尾' for x in range(30)]
    # # TestWaterBall = TestWaterBall * 3
    # TestWaterBall = '\n'.join(TestWaterBall)
    test_waterball = '水球測試1 :D\n水球測試2 :D'

    PTTBot.throw_waterball(pttid, test_waterball)
    # time.sleep(3)


def get_waterball():
    operate_type = PTT.WaterBallOperateType.DoNothing
    # OperateType = PTT.WaterBallOperateType.Mail
    # OperateType = PT4T.WaterBallOperateType.Clear

    waterball_list = PTTBot.get_waterball(operate_type)

    if waterball_list is None:
        return

    print('Result:')
    for waterball in waterball_list:
        if waterball.get_type() == PTT.WaterBallType.Catch:
            temp = '★' + waterball.get_target() + ' '
        elif waterball.get_type() == PTT.WaterBallType.Send:
            temp = 'To ' + waterball.get_target() + ': '
        temp += waterball.get_content() + ' [' + waterball.get_date() + ']'
        print(temp)


def WaterBall():
    OperateType = PTT.WaterBallOperateType.Clear

    TestWaterBall = [str(x % 10) for x in range(10)]
    TagetID = 'DeepLearning'

    for Msg in TestWaterBall:
        PTTBot.throw_waterball(TagetID, Msg)

        WaterBallList = PTTBot.get_waterball(OperateType)

        if WaterBallList is None:
            return

        print('Result:')
        for WaterBall in WaterBallList:
            if WaterBall.get_type() == PTT.WaterBallType.Catch:
                Temp = '★' + WaterBall.get_target() + ' '
            elif WaterBall.get_type() == PTT.WaterBallType.Send:
                Temp = 'To ' + WaterBall.get_target() + ': '
            Temp += WaterBall.get_content() + ' [' + WaterBall.get_date() + ']'
            print(Temp)


def callstatus():
    def show_callstatus(CallStatus):
        if CallStatus == PTT.CallStatus.On:
            print('呼叫器狀態[打開]')
        elif CallStatus == PTT.CallStatus.Off:
            print('呼叫器狀態[關閉]')
        elif CallStatus == PTT.CallStatus.Unplug:
            print('呼叫器狀態[拔掉]')
        elif CallStatus == PTT.CallStatus.Waterproof:
            print('呼叫器狀態[防水]')
        elif CallStatus == PTT.CallStatus.Friend:
            print('呼叫器狀態[朋友]')
        else:
            print(f'Unknow CallStatus: {CallStatus}')

    for _ in range(5):
        call_status = PTTBot.get_callstatus()
        show_callstatus(call_status)

    print('連續測試通過')

    InitCallStatus = random.randint(
        PTT.CallStatus.MinValue, PTT.CallStatus.MaxValue
    )

    TestQueue = [x for x in range(
        PTT.CallStatus.MinValue, PTT.CallStatus.MaxValue + 1
    )]
    random.shuffle(TestQueue)

    print('初始呼叫器狀態')
    show_callstatus(InitCallStatus)
    print('測試切換呼叫器狀態順序')
    for CurrentTestStatus in TestQueue:
        show_callstatus(CurrentTestStatus)

    PTTBot.set_callstatus(InitCallStatus)
    call_status = PTTBot.get_callstatus()
    if call_status != InitCallStatus:
        print('設定初始呼叫器狀態: 不通過')
        return
    print('設定初始呼叫器狀態: 通過')

    for CurrentTestStatus in TestQueue:
        print('準備設定呼叫器狀態')
        show_callstatus(CurrentTestStatus)

        PTTBot.set_callstatus(CurrentTestStatus)
        call_status = PTTBot.get_callstatus()
        show_callstatus(call_status)
        if call_status != CurrentTestStatus:
            print('設定呼叫器狀態: 不通過')
            return
        print('設定呼叫器狀態: 通過')

    print('呼叫器測試全數通過')


def give_money():
    PTTBot.give_money('DeepLearning', 1)


def mail():
    content = '\r\n\r\n'.join(
        [
            '如有誤寄，對..對不起',
            'PTT Library 程式寄信測試內容',
            'github: https://tinyurl.com/umqff3v'
        ]
    )

    try:
        PTTBot.mail(
            'sdjfkdsjfls',
            '程式寄信標題',
            content,
            0
        )
    except PTT.Exceptions.NoSuchUser:
        pass

    PTTBot.mail(
        ID,
        '程式寄信標題',
        content,
        0
    )


def has_new_mail():
    result = PTTBot.has_new_mail()
    print(result)


ThreadBot = None


def threading_test():
    id1, password1 = getPW('Account3.txt')
    id2, password2 = getPW('Account.txt')

    def thread_func1():
        thread_bot1 = PTT.Library()
        try:
            thread_bot1.login(
                id1,
                password1,
                #  KickOtherLogin=True
            )
        except PTT.Exceptions.LoginError:
            thread_bot1.log('登入失敗')
            return

        thread_bot1.logout()
        print('1 多線程測試完成')

    def thread_func2():
        thread_bot2 = PTT.Library()
        try:
            thread_bot2.login(
                id2,
                password2,
                #  KickOtherLogin=True
            )
        except PTT.Exceptions.LoginError:
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
    board_list = PTTBot.get_board_list()
    # print(' '.join(BoardList))
    print(f'總共有 {len(board_list)} 個板名')
    print(f'總共有 {len(set(board_list))} 個不重複板名')


def reply_post():
    reply_post_index = 612

    PTTBot.reply_post(
        PTT.ReplyType.Board,
        'Test',
        '測試回應到板上，如有打擾抱歉',
        post_index=reply_post_index
    )

    PTTBot.reply_post(
        PTT.ReplyType.Mail,
        'Test',
        '測試回應到信箱，如有打擾抱歉',
        post_index=reply_post_index
    )

    PTTBot.reply_post(
        PTT.ReplyType.Board_Mail,
        'Test',
        '測試回應到板上還有信箱，如有打擾抱歉',
        post_index=reply_post_index
    )


def set_board_title():
    from time import gmtime, strftime

    while True:
        time_format = strftime('%H:%M:%S')
        try:
            PTTBot.set_board_title(
                'give',
                f'現在時間 {time_format}'
            )
        except PTT.Exceptions.ConnectionClosed:
            while True:
                try:
                    PTTBot.login(
                        ID,
                        Password
                    )
                    break
                except PTT.Exceptions.LoginError:
                    PTTBot.log('登入失敗')
                    time.sleep(1)
                except PTT.Exceptions.ConnectError:
                    PTTBot.log('登入失敗')
                    time.sleep(1)
        print('已經更新時間 ' + time_format, end='\r')
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print('已經更新時間 ' + time_format)
            PTTBot.set_board_title(
                'give',
                '[贈送] 注意標題  不合砍文'
            )
            print('板標已經恢復')
            break


def mark_post():
    mark_type = PTT.MarkType.S

    # PTTBot.markPost(
    #     MarkType,
    #     'CodingMan',
    #     PostIndex=2
    # )

    # PTTBot.markPost(
    #     MarkType,
    #     'CodingMan',
    #     PostIndex=3
    # )

    # PTTBot.markPost(
    #     MarkType,
    #     'CodingMan',
    #     PostIndex=4
    # )

    # if MarkType == PTT.MarkType.D:
    #     PTTBot.markPost(
    #         PTT.MarkType.DeleteD,
    #         'CodingMan',
    #         PostIndex=4
    #     )

    PTTBot.mark_post(
        mark_type,
        'give',
        post_index=2000
    )

    # PTTBot.mark_post(
    #     mark_type,
    #     'give',
    #     post_index=2000
    # )


def getPostIndexTest():
    BoardList = [
        'Wanted',
        'Gossiping'
    ]
    Range = 100

    for Board in BoardList:

        Index = PTTBot.get_newest_index(
            PTT.IndexType.BBS,
            Board,
        )

        for i in range(Range):

            Post = PTTBot.get_post(
                Board,
                post_index=Index - i,
                query=True
            )

            if Post is None:
                print('Empty')
                continue

            if Post.get_delete_status() != PTT.PostDeleteStatus.NotDeleted:
                print('被刪除文章')
                continue

            print(Post.get_aid())

            PostIndex = PTTBot._get_post_index(Board, Post.get_aid())
            print(PostIndex)
            if Index - i != PostIndex:
                print('!!!!!!!!!!!!!!!!!!!!!!!!!')
                return

        print('=' * 50)


def get_favourite_board():
    favourite_board_list = PTTBot.get_favourite_board()

    for board in favourite_board_list:
        buff = f'[{board.get_board()}][{board.get_type()}][{board.get_board_title()}]'
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

    board_info = PTTBot.get_board_info('Gossiping')
    print('板名: ', board_info.get_board())
    print('線上人數: ', board_info.get_online_user())
    print('中文敘述: ', board_info.get_chinese_des())
    print('板主: ', board_info.get_moderators())
    print('公開狀態(是否隱形): ', board_info.is_open())
    print('隱板時是否可進入十大排行榜: ', board_info.can_into_top_ten_when_hide())
    print('是否開放非看板會員發文: ', board_info.can_non_board_members_post())
    print('是否開放回應文章: ', board_info.can_reply_post())
    print('是否開放自刪文章: ', board_info.can_self_del_post())
    print('是否開放推薦文章: ', board_info.can_push_post())
    print('是否開放噓文: ', board_info.can_boo_post())
    print('是否可以快速連推文章: ', board_info.can_fast_push())
    print('推文最低間隔時間: ', board_info.get_min_interval())
    print('推文時是否記錄來源 IP: ', board_info.is_push_record_ip())
    print('推文時是否對齊開頭: ', board_info.is_push_aligned())
    print('板主是否可刪除部份違規文字: ', board_info.can_moderator_can_del_illegal_content())
    print('轉錄文章是否自動記錄，且是否需要發文權限: ',
          board_info.is_tran_post_auto_recorded_and_require_post_permissions())
    print('是否為冷靜模式: ', board_info.is_cool_mode())
    print('是否需要滿十八歲才可進入: ', board_info.is_require18())
    print('發文與推文限制登入次數需多少次以上: ', board_info.get_require_login_time())
    print('發文與推文限制退文篇數多少篇以下: ', board_info.get_require_illegal_post())


def bucket():
    PTTBot.bucket(
        'give',
        7,
        'Bucket Reason',
        'CodingMan'
    )


def search_user():
    user_list = PTTBot.search_user(
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


if __name__ == '__main__':
    print('Welcome to PTT Library v ' + PTT.Version + ' test case')

    RunCI = False
    TravisCI = False
    if len(sys.argv) == 2:
        if sys.argv[1] == '-ci':
            RunCI = True

    if RunCI:

        ID = os.getenv('PTTLibrary_ID')
        Password = os.getenv('PTTLibrary_Password')
        if ID is None or Password is None:
            print('從環境變數取得帳號密碼失敗')
            ID, Password = getPW('Account.txt')
            TravisCI = False
        else:
            TravisCI = True

        Init()
        PTTBot = PTT.Library(
            # LogLevel=PTT.LogLevel.TRACE,
        )
        try:
            PTTBot.login(
                ID,
                Password,
                # KickOtherLogin=True
            )
            pass
        except PTT.Exceptions.LoginError:
            PTTBot.log('登入失敗')
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
                    PTTBot.logout()
                    sys.exit(1)


        def GetPostTestFunc(board, IndexAID, targetEx, checkformat, checkStr):
            try:
                if isinstance(IndexAID, int):
                    Post = PTTBot.get_post(
                        board,
                        post_index=IndexAID,
                    )
                else:
                    Post = PTTBot.get_post(
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
                PTTBot.logout()
                sys.exit(1)

            if checkStr is None and targetEx is None and not checkformat:
                print(Post.get_content())

            if checkformat and not Post.is_format_check():
                showTestResult(board, IndexAID, True)
                return

            if checkStr is not None and checkStr not in Post.get_content():
                PTTBot.logout()
                sys.exit(1)

            if isinstance(IndexAID, int):
                print(f'{board} index {IndexAID} 測試通過')
            else:
                print(f'{board} AID {IndexAID} 測試通過')


        try:

            TestPostList = [
                ('Python', 1, None, False, '總算可以來想想板的走向了..XD'),
                ('NotExitBoard', 1, PTT.Exceptions.NoSuchBoard, False, None),
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

            for b, i, ex, checkformat, c in TestPostList:
                GetPostTestFunc(b, i, ex, checkformat, c)

            print('取得文章測試全部通過')

            TestBoardList = [
                'Wanted',
                'Gossiping',
                'Test',
                'Stock',
                'movie'
            ]

            for Board in TestBoardList:
                BasicIndex = 0
                for _ in range(50):
                    Index = PTTBot.get_newest_index(
                        PTT.IndexType.BBS,
                        board=Board
                    )

                    if BasicIndex == 0:
                        print(f'{Board} 最新文章編號 {Index}')
                        BasicIndex = Index
                    elif abs(BasicIndex - Index) > 5:
                        print(f'{Board} 最新文章編號 {Index}')
                        print(f'BasicIndex {BasicIndex}')
                        print(f'Index {Index}')
                        print('取得看板最新文章編號測試失敗')

                        PTTBot.logout()
                        sys.exit(1)
            print('取得看板最新文章編號測試全部通過')

            Title = 'PTT Library 程式貼文基準測試標題'
            Content = f'''
PTT Library v {PTTBot.get_version()}

PTT Library 程式貼文基準測試內文

この日本のベンチマーク
'''
            if TravisCI:
                Content = '''
此次測試由 Travis CI 啟動
''' + Content
            else:
                Content = f'''
此次測試由 {ID} 啟動
''' + Content
            Content = Content.replace('\n', '\r\n')

            Board = 'Test'
            PTTBot.post(
                Board,
                Title,
                Content,
                1,
                1
            )

            Index = PTTBot.get_newest_index(
                PTT.IndexType.BBS,
                board=Board
            )

            BasicPostAID = None
            BasicPostIndex = 0
            for i in range(5):

                Post = PTTBot.get_post(
                    Board,
                    post_index=Index - i,
                )

                if ID in Post.get_author() and 'PTT Library 程式貼文基準測試內文' in Post.get_content() and \
                        Title in Post.get_title():
                    print('使用文章編號取得基準文章成功')
                    Post = PTTBot.get_post(
                        Board,
                        post_aid=Post.get_aid(),
                    )
                    if ID in Post.get_author() and 'PTT Library 程式貼文基準測試內文' in Post.get_content() and \
                            Title in Post.get_title():
                        print('使用文章代碼取得基準文章成功')
                        BasicPostAID = Post.get_aid()
                        BasicPostIndex = Index - i
                        break

            if BasicPostAID is None:
                print('取得基準文章失敗')
                PTTBot.logout()
                sys.exit(1)
            print('取得基準文章成功')
            print('貼文測試全部通過')

            try:
                Content1 = '編號推文基準文字123'
                PTTBot.push(Board, PTT.PushType.Push,
                            Content1, post_aid='QQQQQQQ')
                print('推文反向測試失敗')
                PTTBot.logout()
                sys.exit(1)
            except PTT.Exceptions.NoSuchPost:
                print('推文反向測試通過')

            try:
                Index = PTTBot.get_newest_index(
                    PTT.IndexType.BBS,
                    board=Board
                )
                Content1 = '編號推文基準文字123'
                PTTBot.push(Board, PTT.PushType.Push,
                            Content1, post_index=Index + 1)
                print('推文反向測試失敗')
                PTTBot.logout()
                sys.exit(1)
            except ValueError:
                print('推文反向測試通過')

            Content1 = '編號推文基準文字123'
            PTTBot.push(Board, PTT.PushType.Push,
                        Content1, post_index=BasicPostIndex)

            Content2 = '代碼推文基準文字123'
            PTTBot.push(Board, PTT.PushType.Push,
                        Content2, post_aid=BasicPostAID)

            Post = PTTBot.get_post(
                Board,
                post_aid=BasicPostAID,
            )

            Content1Check = False
            Content2Check = False
            for push in Post.get_push_list():
                if Content1 in push.get_content():
                    Content1Check = True
                if Content2 in push.get_content():
                    Content2Check = True

            if not Content1Check:
                print('編號推文基準測試失敗')
                PTTBot.logout()
                sys.exit(1)
            print('編號推文基準測試成功')
            if not Content2Check:
                print('代碼推文基準測試失敗')
                PTTBot.logout()
                sys.exit(1)
            print('代碼推文基準測試成功')

            Content = '推文基準測試全部通過'
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)

            TestList = [
                ('Python', PTT.PostSearchType.Keyword, '[公告]'),
                ('ALLPOST', PTT.PostSearchType.Keyword, '(Wanted)'),
                ('Wanted', PTT.PostSearchType.Keyword, '(本文已被刪除)'),
                ('ALLPOST', PTT.PostSearchType.Keyword, '(Gossiping)'),
                ('Gossiping', PTT.PostSearchType.Keyword, '普悠瑪'),
            ]

            TestRange = 1

            for (Board, SearchType, Condition) in TestList:
                showCondition(Board, SearchType, Condition)
                Index = PTTBot.get_newest_index(
                    PTT.IndexType.BBS,
                    Board,
                    search_type=SearchType,
                    search_condition=Condition,
                )
                print(f'{Board} 最新文章編號 {Index}')

                for i in range(TestRange):
                    Post = PTTBot.get_post(
                        Board,
                        post_index=Index - i,
                        search_type=SearchType,
                        search_condition=Condition,
                        query=False
                    )

                    print('列表日期:')
                    print(Post.get_list_date())
                    print('作者:')
                    print(Post.get_author())
                    print('標題:')
                    print(Post.get_title())

                    if Post.get_delete_status() == PTT.PostDeleteStatus.NotDeleted:
                        if not Query:
                            print('內文:')
                            print(Post.get_content())
                    elif Post.get_delete_status() == PTT.PostDeleteStatus.ByAuthor:
                        print('文章被作者刪除')
                    elif Post.get_delete_status() == PTT.PostDeleteStatus.ByModerator:
                        print('文章被版主刪除')
                    print('=' * 50)

                Content = f'{Board} 取得文章測試完成'
                PTTBot.push('Test', PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)

            Board = 'Test'

            Content = '取得文章測試全部通過'
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)

            Content = '貼文測試全部通過'
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)

            TestBoardList = [
                'Wanted',
                'joke',
                'Gossiping',
                'C_Chat'
            ]

            # 改成 10 篇，不然 100 篇太耗時間了
            Range = 10
            for testboard in TestBoardList:

                NewestIndex = PTTBot.get_newest_index(
                    PTT.IndexType.BBS,
                    board=testboard
                ) - 10000
                # 到很久之前的文章去才不會撞到被刪掉的文章

                ErrorPostList, DelPostList = PTTBot.crawl_board(
                    PTT.CrawlType.BBS,
                    crawlHandler,
                    testboard,
                    start_index=NewestIndex - Range + 1,
                    end_index=NewestIndex,
                    query=Query
                )

                StartPost = None
                offset = 0
                while True:
                    StartPost = PTTBot.get_post(
                        testboard,
                        post_index=NewestIndex - Range + 1 - offset,
                    )
                    offset += 1
                    if StartPost is None:
                        continue
                    if StartPost.get_aid() is None:
                        continue
                    break

                EndPost = None
                offset = 0
                while True:
                    EndPost = PTTBot.get_post(
                        testboard,
                        post_index=NewestIndex + offset,
                    )
                    offset += 1
                    if EndPost is None:
                        continue
                    if EndPost.get_aid() is None:
                        continue
                    break

                print(testboard)
                print(f'StartPost index {NewestIndex - Range + 1}')
                print(f'EndPost index {NewestIndex}')

                ErrorPostList, DelPostList = PTTBot.crawl_board(
                    PTT.CrawlType.BBS,
                    crawlHandler,
                    testboard,
                    start_aid=StartPost.get_aid(),
                    end_aid=EndPost.get_aid()
                )
                Content = f'{testboard} 爬板測試完成'
                PTTBot.push(Board, PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)

            Content = '爬板測試全部完成'
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)

            User = PTTBot.get_user(ID)
            if User is None:
                print('取得使用者測試失敗')
                Content = '取得使用者測試失敗'
                PTTBot.push(Board, PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)
                PTTBot.logout()
                sys.exit(1)

            PTTBot.log('使用者ID: ' + User.get_id())
            PTTBot.log('使用者經濟狀況: ' + str(User.get_money()))
            PTTBot.log('登入次數: ' + str(User.get_login_time()))
            PTTBot.log('有效文章數: ' + str(User.get_legal_post()))
            PTTBot.log('退文文章數: ' + str(User.get_illegal_post()))
            PTTBot.log('目前動態: ' + User.get_state())
            PTTBot.log('信箱狀態: ' + User.get_mail())
            PTTBot.log('最後登入時間: ' + User.get_last_login())
            PTTBot.log('上次故鄉: ' + User.get_last_ip())
            PTTBot.log('五子棋戰績: ' + User.get_five_chess())
            PTTBot.log('象棋戰績:' + User.get_chess())
            PTTBot.log('簽名檔:' + User.get_signature_file())

            try:
                User = PTTBot.get_user('sdjfklsdj')
                print('取得使用者反向測試失敗')
                Content = '取得使用者反向測試失敗'
                PTTBot.push(Board, PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)

                PTTBot.logout()
                sys.exit(1)
            except PTT.Exceptions.NoSuchUser:
                print('取得使用者反向測試通過')

            NewMail1 = PTTBot.has_new_mail()
            print(f'有 {NewMail1} 封新信')
            Content = '取得幾封新信測試通過'
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)

            try:
                PTTBot.mail(
                    'sdjfkdsjfls',
                    '程式寄信標題',
                    Content,
                    0
                )

                Content = '寄信反向測試失敗'
                print(Content)
                PTTBot.push(Board, PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)
                PTTBot.logout()
                sys.exit(1)

            except PTT.Exceptions.NoSuchUser:
                Content = '寄信反向測試成功'
                print(Content)
                PTTBot.push(Board, PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)

            Content = '''如有誤寄，對..對不起
PTT Library 程式寄信測試內容

github: https://tinyurl.com/umqff3v
'''
            Content = Content.replace('\n', '\r\n')
            PTTBot.mail(
                ID,
                '程式寄信標題',
                Content,
                0
            )

            NewMail2 = PTTBot.has_new_mail()
            print(f'有 {NewMail2} 封新信')
            if NewMail2 > NewMail1:
                Content = '寄信測試通過'
                PTTBot.push(Board, PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)
            else:
                Content = '寄信測試失敗'
                print(Content)
                PTTBot.push(Board, PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)
                PTTBot.logout()
                sys.exit(1)

            Content = '寄信測試成功'
            print(Content)
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)

            BoardList = PTTBot.get_board_list()
            print(f'總共有 {len(BoardList)} 個板名')
            print(f'總共有 {len(set(BoardList))} 個不重複板名')

            Content = '取得全站看板測試通過'
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)
            Content = f'總共有 {len(set(BoardList))} 個不重複板名'
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)

            try:
                PTTBot.get_board_info('NotExistBoard')

                print('取得看板資訊反向測試失敗')
                Content = '取得看板資訊反向測試失敗'
                PTTBot.push(Board, PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)

                PTTBot.logout()
                sys.exit(1)
            except PTT.Exceptions.NoSuchBoard:
                print('取得看板資訊反向測試成功')
                Content = '取得看板資訊反向測試成功'
                PTTBot.push(Board, PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)

            BoardInfo = PTTBot.get_board_info('Gossiping')
            print('板名: ', BoardInfo.get_board())
            print('線上人數: ', BoardInfo.get_online_user())
            # setting
            print('中文敘述: ', BoardInfo.get_chinese_des())
            print('板主: ', BoardInfo.get_moderators())
            print('公開狀態(是否隱形): ', BoardInfo.is_open())
            print('隱板時是否可進入十大排行榜: ', BoardInfo.can_into_top_ten_when_hide())
            print('是否開放非看板會員發文: ', BoardInfo.can_non_board_members_post())
            print('是否開放回應文章: ', BoardInfo.can_reply_post())
            print('是否開放自刪文章: ', BoardInfo.can_self_del_post())
            print('是否開放推薦文章: ', BoardInfo.can_push_post())
            print('是否開放噓文: ', BoardInfo.can_boo_post())
            print('是否可以快速連推文章: ', BoardInfo.can_fast_push())
            print('推文最低間隔時間: ', BoardInfo.get_min_interval())
            print('推文時是否記錄來源 IP: ', BoardInfo.is_push_record_ip())
            print('推文時是否對齊開頭: ', BoardInfo.is_push_aligned())
            print('板主是否可刪除部份違規文字: ', BoardInfo.can_moderator_can_del_illegal_content())
            print('轉錄文章是否自動記錄，且是否需要發文權限: ',
                  BoardInfo.is_tran_post_auto_recorded_and_require_post_permissions())
            print('是否為冷靜模式: ', BoardInfo.is_cool_mode())
            print('是否需要滿十八歲才可進入: ', BoardInfo.is_require18())
            print('發文與推文限制登入次數需多少次以上: ', BoardInfo.get_require_login_time())
            print('發文與推文限制退文篇數多少篇以下: ', BoardInfo.get_require_illegal_post())

            Content = '取得看板資訊測試成功'
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)

            FBlist = PTTBot.get_favourite_board()
            for testboard in FBlist:
                if testboard.get_board() is None or testboard.get_type() is None or testboard.get_board_title() is None:
                    Content = '取得我的最愛測試失敗'
                    PTTBot.push(Board, PTT.PushType.Arrow,
                                Content, post_aid=BasicPostAID)
                    PTTBot.logout()
                    sys.exit(1)

            Content = '取得我的最愛測試成功'
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)

            userlist = PTTBot.search_user(
                'coding'
            )
            if len(userlist) != 14:
                Content = '查詢網友測試失敗'
                PTTBot.push(Board, PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)
                PTTBot.logout()
                sys.exit(1)
            Content = '查詢網友測試成功'
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)

            PTTBot.reply_post(
                PTT.ReplyType.Board,
                Board,
                '使用文章編號測試回應到板上',
                post_index=BasicPostIndex
            )

            Index = PTTBot.get_newest_index(
                PTT.IndexType.BBS,
                board=Board
            )

            TestPass = False
            for i in range(5):

                Post = PTTBot.get_post(
                    Board,
                    post_index=Index - i,
                )

                if ID in Post.get_author() and '使用文章編號測試回應到板上' in Post.get_content():
                    TestPass = True
                    Content = '使用文章編號測試回應到板上成功'
                    print(Content)
                    PTTBot.push(
                        Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)
                    break
            if not TestPass:
                Content = '使用文章編號測試回應到板上失敗'
                PTTBot.push(Board, PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)
                PTTBot.logout()
                sys.exit(1)

            PTTBot.reply_post(
                PTT.ReplyType.Board,
                Board,
                '使用文章ID測試回應到板上',
                post_aid=BasicPostAID
            )

            Index = PTTBot.get_newest_index(
                PTT.IndexType.BBS,
                board=Board
            )

            TestPass = False
            for i in range(5):

                Post = PTTBot.get_post(
                    Board,
                    post_index=Index - i,
                )

                if ID in Post.get_author() and '使用文章ID測試回應到板上' in Post.get_content():
                    TestPass = True
                    Content = '使用文章ID測試回應到板上成功'
                    print(Content)
                    PTTBot.push(
                        Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)
                    break
            if not TestPass:
                Content = '使用文章ID測試回應到板上失敗'
                PTTBot.push(Board, PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)
                PTTBot.logout()
                sys.exit(1)

            if TravisCI:
                ID2 = os.getenv('PTTLibrary_ID2')
                Password2 = os.getenv('PTTLibrary_Password2')
            else:
                ID2, Password2 = getPW('Account2.txt')

            PTTBot2 = PTT.Library(
                # LogLevel=PTT.LogLevel.TRACE,
            )
            try:
                PTTBot2.login(
                    ID2,
                    Password2,
                    # KickOtherLogin=True
                )
                pass
            except PTT.Exceptions.LoginError:
                PTTBot2.log('PTTBot2登入失敗')
                sys.exit(1)

            OperateType = PTT.WaterBallOperateType.Clear
            PTTBot.get_waterball(OperateType)
            PTTBot2.get_waterball(OperateType)

            PTTBot.set_callstatus(PTT.CallStatus.Off)
            PTTBot2.set_callstatus(PTT.CallStatus.Off)

            TestPass = False
            PTTBot2.throw_waterball(ID, '水球測試基準訊息')
            WaterBallList = PTTBot.get_waterball(OperateType)
            for WaterBall in WaterBallList:
                if not WaterBall.get_type() == PTT.WaterBallType.Catch:
                    continue

                Target = WaterBall.get_target()
                Content = WaterBall.get_content()

                print(f'收到來自 {Target} 的水球 [{Content}]')

                if '水球測試基準訊息' in Content:
                    TestPass = True
                    break

            if not TestPass:
                Content = '水球測試基準測試失敗'
                print(Content)
                PTTBot.push(Board, PTT.PushType.Arrow,
                            Content, post_aid=BasicPostAID)
                PTTBot.logout()
                PTTBot2.logout()
                sys.exit(1)

            Content = '水球測試基準測試成功'
            print(Content)
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)
            PTTBot2.logout()

            Content = '自動化測試全部完成'
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)

        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
            Content = str(e)
            PTTBot.push(Board, PTT.PushType.Arrow,
                        Content, post_aid=BasicPostAID)
        except KeyboardInterrupt:
            pass

        PTTBot.logout()
    else:
        ID, Password = getPW('Account3.txt')
        try:
            # threading_test()
            PTTBot = PTT.Library(
                # log_level=PTT.LogLevel.TRACE,
                # log_level=PTT.LogLevel.DEBUG,
                # host=PTT.Host.PTT2
            )
            try:
                PTTBot.login(
                    ID,
                    Password,
                    # KickOtherLogin=True
                )
                pass
            except PTT.Exceptions.LoginError:
                PTTBot.log('登入失敗')
                sys.exit()

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
            # WaterBall()
            # callstatus()
            # give_money()
            # mail()
            # has_new_mail()
            # get_board_list()
            # get_board_info()
            # reply_post()
            # get_favourite_board()
            # search_user()

            # bucket()
            # set_board_title()
            # mark_post()

            # private test
            # getPostIndexTest()
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
        except KeyboardInterrupt:
            pass

        PTTBot.logout()
