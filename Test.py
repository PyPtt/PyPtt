import sys
import os
import time
import json
import random
import traceback
import PTTLibrary
import threading

from PTTLibrary import PTT


def getPW():
    try:
        with open('Account.txt') as AccountFile:
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
    PTT.Library(Language=PTT.Language.Chinese)
    print('===英文顯示===')
    PTT.Library(Language=PTT.Language.English)
    print('===Telnet===')
    PTT.Library(ConnectMode=PTT.ConnectMode.Telnet)
    print('===WebSocket===')
    PTT.Library(ConnectMode=PTT.ConnectMode.WebSocket)
    print('===Log DEBUG===')
    PTT.Library(LogLevel=PTT.LogLevel.DEBUG)
    print('===Log INFO===')
    PTT.Library(LogLevel=PTT.LogLevel.INFO)
    print('===Log SLIENT===')
    PTT.Library(LogLevel=PTT.LogLevel.SLIENT)
    print('===Log SLIENT======')

    print('===負向===')
    try:
        print('===語言 99===')
        PTT.Library(Language=99)
    except ValueError:
        print('通過')
    except:
        print('沒通過')
        return
    print('===語言放字串===')
    try:
        PTT.Library(Language='PTT.Language.English')
    except TypeError:
        print('通過')
    except:
        print('沒通過')
        return
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


def Loginout():

    print('WebSocket 登入登出測試')

    PTTBot = PTT.Library(
        ConnectMode=PTT.ConnectMode.WebSocket,
        LogLevel=PTT.LogLevel.DEBUG
    )
    try:
        PTTBot.login(ID,
                     Password,
                     # KickOtherLogin=True
                     )
    except PTT.Exceptions.LoginError:
        PTTBot.log('登入失敗')
        sys.exit()
    PTTBot.log('登入成功')
    PTTBot.logout()
    PTTBot.log('登出成功')

    print('等待五秒')
    time.sleep(5)
    return

    print('Telnet 登入登出測試')
    PTTBot = PTT.Library(
        ConnectMode=PTT.ConnectMode.Telnet,
        # LogLevel=PTT.LogLevel.DEBUG
    )
    try:
        PTTBot.login(ID, Password, KickOtherLogin=True)
    except PTT.Exceptions.LoginError:
        PTTBot.log('登入失敗')
        sys.exit()
    PTTBot.log('登入成功')
    PTTBot.logout()
    PTTBot.log('登出成功')


def PerformanceTest():

    TestTime = 1000
    print(f'效能測試 getTime {TestTime} 次')

    PTTBot = PTT.Library(
        ConnectMode=PTT.ConnectMode.WebSocket,
        LogLevel=PTT.LogLevel.SLIENT,
        # LogLevel=PTT.LogLevel.DEBUG,
    )
    try:
        PTTBot.login(ID, Password, KickOtherLogin=True)
    except PTT.Exceptions.LoginError:
        PTTBot.log('登入失敗')
        sys.exit()
    PTTBot.log('登入成功')

    StartTime = time.time()
    for _ in range(TestTime):
        PTT_TIME = PTTBot.getTime()

        if PTT_TIME is None:
            print('PTT_TIME is None')
            break
        # print(PTT_TIME)
    EndTime = time.time()
    PTTBot.logout()
    PTTBot.log('Performance Test WebSocket ' + str(
        round(EndTime - StartTime, 2)) + ' s')

    PTTBot.log('等待五秒')
    time.sleep(5)

    PTTBot = PTT.Library(
        ConnectMode=PTT.ConnectMode.Telnet,
        LogLevel=PTT.LogLevel.SLIENT,
        # LogLevel=PTT.LogLevel.DEBUG,
    )
    try:
        PTTBot.login(ID, Password, KickOtherLogin=True)
    except PTT.Exceptions.LoginError:
        PTTBot.log('登入失敗')
        sys.exit()
    PTTBot.log('登入成功')

    StartTime = time.time()
    for _ in range(TestTime):
        PTT_TIME = PTTBot.getTime()

        if PTT_TIME is None:
            print('PTT_TIME is None')
            break
        # print(PTT_TIME)
    EndTime = time.time()

    PTTBot.log('Performance Test Telnet ' +
               str(round(EndTime - StartTime, 2)) + ' s')

    print('Performance Test finish')


def GetPost():

    TestPostList = [
        # ('Python', 1),
        # ('NotExitBoard', 1),
        # ('Python', 7486),
        # 文章格式錯誤
        # ('Steam', 4444),
        # ('Baseball', 199787),
        # ('Stock', 92324),
        # 文章格式錯誤
        # ('Gossiping', 778570),
        # 文章格式錯誤
        # ('Stock', 99606),
        # 文章格式錯誤
        # ('movie', 457),
        # 文章格式錯誤
        # ('Wanted', 76417),
        # ('Gossiping', '1TU65Wi_')
    ]

    Query = False

    for (Board, Index) in TestPostList:
        try:
            if isinstance(Index, int):
                Post = PTTBot.getPost(
                    Board,
                    PostIndex=Index,
                    # SearchType=PTT.PostSearchType.Keyword,
                    # SearchCondition='公告',
                    Query=Query,
                )
            else:
                Post = PTTBot.getPost(
                    Board,
                    PostAID=Index,
                    # SearchType=PTT.PostSearchType.Keyword,
                    # SearchCondition='公告',
                    Query=Query,
                )
            if Post is None:
                print('Empty')
                continue

            if not Post.isFormatCheck():
                print('文章格式錯誤')
                continue

            print('Board: ' + Post.getBoard())
            print('AID: ' + Post.getAID())
            print('Author: ' + Post.getAuthor())
            print('List Date: ' + Post.getListDate())
            print('Title: ' + Post.getTitle())
            print('Money: ' + str(Post.getMoney()))
            print('URL: ' + Post.getWebUrl())
            if not Query:
                print('Date: ' + Post.getDate())
                print('Content: ' + Post.getContent())
                print('IP: ' + Post.getIP())

                # print('Location: ' + Post.getLocation())
                if Post.getLocation() is not None:
                    print('Location: ' + Post.getLocation())
                else:
                    print('無地區')
            # 在文章列表上的日期

                PushCount = 0
                BooCount = 0
                ArrowCount = 0

                for Push in Post.getPushList():
                    #     print(Push.getType())
                    #     print(Push.getAuthor())
                    #     print(Push.getContent())
                    #     print(Push.getIP())
                    #     print(Push.getTime())

                    if Push.getType() == PTT.PushType.Push:
                        PushCount += 1
                        Type = '推'
                    if Push.getType() == PTT.PushType.Boo:
                        BooCount += 1
                        Type = '噓'
                    if Push.getType() == PTT.PushType.Arrow:
                        ArrowCount += 1
                        Type = '→'

                    Author = Push.getAuthor()
                    Content = Push.getContent()

                    # Buffer = f'[{Author}] 給了一個{Type} 說 [{Content}]'
                    # if Push.getIP() is not None:
                    #     Buffer += f' 來自 [{Push.getIP()}]'
                    # Buffer += f' 時間是 [{Push.getTime()}]'

                    Buffer = f'{Type} {Author}: {Content} {Push.getIP()} {Push.getTime()}'
                    print(Buffer)

                print(
                    f'Total {PushCount} Pushs {BooCount} Boo {ArrowCount} Arrow = {PushCount - BooCount}'
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


def GetPostWithCondition():

    TestList = [
        # ('Python', PTT.PostSearchType.Keyword, '[公告]'),
        # ('ALLPOST', PTT.PostSearchType.Keyword, '(Wanted)'),
        # ('Wanted', PTT.PostSearchType.Keyword, '(本文已被刪除)')
        ('ALLPOST', PTT.PostSearchType.Keyword, '(Gossiping)')
    ]

    TestRange = 1
    Query = True

    for (Board, SearchType, Condition) in TestList:
        try:
            showCondition(Board, SearchType, Condition)
            Index = PTTBot.getNewestIndex(
                PTT.IndexType.Board,
                Board,
                SearchType=SearchType,
                SearchCondition=Condition,
            )
            print(f'{Board} 最新文章編號 {Index}')

            for i in range(TestRange):
                Post = PTTBot.getPost(
                    Board,
                    # PostIndex=Index - i,
                    PostIndex=9464,
                    SearchType=SearchType,
                    SearchCondition=Condition,
                    Query=Query
                )

                print('列表日期:')
                print(Post.getListDate())
                print('作者:')
                print(Post.getAuthor())
                print('標題:')
                print(Post.getTitle())

                if Post.getDeleteStatus() == PTT.PostDeleteStatus.NotDeleted:
                    if not Query:
                        print('內文:')
                        print(Post.getContent())
                elif Post.getDeleteStatus() == PTT.PostDeleteStatus.ByAuthor:
                    print('文章被作者刪除')
                elif Post.getDeleteStatus() == PTT.PostDeleteStatus.ByModerator:
                    print('文章被版主刪除')
                print('=' * 50)

        except Exception as e:

            traceback.print_tb(e.__traceback__)
            print(e)

    # TestList = [
    #     ('Python', PTT.PostSearchType.Keyword, '[公告]')
    # ]

    # for (Board, SearchType, Condition) in TestList:
    #     Index = PTTBot.getNewestIndex(
    #         PTT.IndexType.Board,
    #         Board,
    #         SearchType=SearchType,
    #         SearchCondition=Condition,
    #     )
    #     print(f'{Board} 最新文章編號 {Index}')

    #     Post = PTTBot.getPost(
    #         Board,
    #         PostIndex=Index,
    #         SearchType=SearchType,
    #         SearchCondition=Condition,
    #     )

    #     print('標題: ' + Post.getTitle())
    #     print('=' * 50)


def Post():

    Content = [
        '此為 PTT Library 貼文測試內容，如有打擾請告知。',
        '程式碼: https://tinyurl.com/y2wuh8ck',
        '開發手冊: https://hackmd.io/@CodingMan/PTTLibraryManual'
    ]
    Content = '\r\n\r\n'.join(Content)

    PTTBot.post(
        'Test',
        'PTT Library 程式貼文測試',
        Content,
        1,
        0
    )


def GetNewestIndex():

    TestBoardList = [
        'Wanted',
        'Gossiping',
        'Test',
        'Stock',
        'movie'
    ]

    for Board in TestBoardList:
        for _ in range(5):
            Index = PTTBot.getNewestIndex(PTT.IndexType.Board, Board=Board)
            print(f'{Board} 最新文章編號 {Index}')


def showValue(Msg, Value):
    print(f'{Msg} =>{Value}<=')


def detectNone(Name, Obj, Enable=True):
    if Obj is None and Enable:
        raise ValueError(Name + ' is None')

Query = False


def crawlHandler(Post):

    global Query

    if Post.getDeleteStatus() != PTT.PostDeleteStatus.NotDeleted:
        if Post.getDeleteStatus() == PTT.PostDeleteStatus.ByModerator:
            print(f'[版主刪除][{Post.getAuthor()}]')
        elif Post.getDeleteStatus() == PTT.PostDeleteStatus.ByAuthor:
            print(f'[作者刪除][{Post.getAuthor()}]')
        elif Post.getDeleteStatus() == PTT.PostDeleteStatus.ByUnknow:
            print(f'[不明刪除]')
        return

    if not Post.isFormatCheck():
        print('[格式錯誤]')
        return

    # if Post.getTitle().startswith('Fw:') or Post.getTitle().startswith('轉'):
    # print(f'[{Post.getAID()}][{Post.getAuthor()}][{Post.getTitle()}]')
    if not Query:
        print(f'[{Post.getAID()}][{Post.getTitle()}]')
    else:
        print(f'[{Post.getAID()}][{Post.getTitle()}]')
    
    detectNone('標題', Post.getTitle())
    detectNone('AID', Post.getAID())
    detectNone('Author', Post.getAuthor())
    detectNone('Money', Post.getMoney())
    detectNone('WebUrl', Post.getWebUrl())
    detectNone('ListDate', Post.getListDate())

    if not Query:
        detectNone('Date', Post.getDate())
        detectNone('Content', Post.getContent())
        detectNone('IP', Post.getIP())
        detectNone('Location', Post.getLocation())

        # print(Post.getContent())

    # time.sleep(0.2)


def CrawlBoard():

    global Query
    TestBoardList = [
        # 'Wanted',
        'Gossiping',
        'Stock',
        'movie',
        'C_Chat',
        'Baseball',
        'NBA',
        'HatePolitics'
    ]

    TestRange = 500
    TestRound = 1

    for _ in range(TestRound):

        for TestBoard in TestBoardList:
            NewestIndex = PTTBot.getNewestIndex(
                PTT.IndexType.Board,
                Board=TestBoard
            )
            StartIndex = NewestIndex - TestRange + 1

            print(f'預備爬行 {TestBoard} 編號 {StartIndex} ~ {NewestIndex} 文章')

            ErrorPostList, DelPostList = PTTBot.crawlBoard(
                crawlHandler,
                TestBoard,
                StartIndex=StartIndex,
                EndIndex=NewestIndex,
                Query=Query
            )

            if len(ErrorPostList) > 0:
                print('Error Post: \n' + '\n'.join(str(x)
                                                   for x in ErrorPostList))
            else:
                print('沒有偵測到錯誤文章')

            if len(DelPostList) > 0:
                # print('Del Post: \n' + '\n'.join([str(x) for x in DelPostList]))
                print(f'共有 {len(DelPostList)} 篇文章被刪除')


def CrawlBoardWithCondition():

    # TestRange = 10

    # for (Board, SearchType, Condition) in TestList:
    #     try:
    #         showCondition(Board, SearchType, Condition)
    #         NewestIndex = PTTBot.getNewestIndex(
    #             PTT.IndexType.Board,
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

    TestList = [
        # ('Stock', PTT.PostSearchType.Keyword, '盤中閒聊'),
        ('Baseball', PTT.PostSearchType.Push, '20')
    ]

    TestRange = 10000

    for (Board, SearchType, Condition) in TestList:
        showCondition(Board, SearchType, Condition)
        NewestIndex = PTTBot.getNewestIndex(
            PTT.IndexType.Board,
            Board,
            SearchType=SearchType,
            SearchCondition=Condition,
        )
        print(f'{Board} 最新文章編號 {NewestIndex}')

        StartIndex = NewestIndex - TestRange + 1

        ErrorPostList, DelPostList = PTTBot.crawlBoard(
            crawlHandler,
            Board,
            StartIndex=StartIndex,
            EndIndex=NewestIndex,
            SearchType=SearchType,
            SearchCondition=Condition,
        )

        # print('標題: ' + Post.getTitle())
        print('=' * 50)


def GetUser():

    try:
        User = PTTBot.getUser('CodingMan')
        if User is None:
            return

        PTTBot.log('使用者ID: ' + User.getID())
        PTTBot.log('使用者經濟狀況: ' + str(User.getMoney()))
        PTTBot.log('登入次數: ' + str(User.getLoginTime()))
        PTTBot.log('有效文章數: ' + str(User.getLegalPost()))
        PTTBot.log('退文文章數: ' + str(User.getIllegalPost()))
        PTTBot.log('目前動態: ' + User.getState())
        PTTBot.log('信箱狀態: ' + User.getMail())
        PTTBot.log('最後登入時間: ' + User.getLastLogin())
        PTTBot.log('上次故鄉: ' + User.getLastIP())
        PTTBot.log('五子棋戰績: ' + User.getFiveChess())
        PTTBot.log('象棋戰績:' + User.getChess())
        PTTBot.log('簽名檔:' + User.getSignatureFile())

    except PTT.Exceptions.NoSuchUser:
        print('無此使用者')

    try:
        User = PTTBot.getUser('sdjfklsdj')
    except PTT.Exceptions.NoSuchUser:
        print('無此使用者')


def Push():

    TestPostList = [
        # ('Gossiping', 95693),
        ('Test', 796)
    ]

    Content = '''
What is Ptt?
批踢踢 (Ptt) 是以學術性質為目的，提供各專業學生實習的平台，而以電子佈告欄系統 (BBS, Bulletin Board System) 為主的一系列服務。
期許在網際網路上建立起一個快速、即時、平等、免費，開放且自由的言論空間。批踢踢實業坊同時承諾永久學術中立，絕不商業化、絕不營利。
'''
    for (Board, Index) in TestPostList:
        PTTBot.push(Board, PTT.PushType.Push, Content, PostIndex=Index)


def ThrowWaterBall():

    TagetID = 'DeepLearning'

    TestWaterBall = [str(x % 10) for x in range(10)]
    TestWaterBall = TestWaterBall * 3
    TestWaterBall = '\n'.join(TestWaterBall)
    # TestWaterBall = '水球測試 :D'

    PTTBot.throwWaterBall(TagetID, TestWaterBall)
    time.sleep(3)


def GetWaterBall():

    OperateType = PTT.WaterBallOperateType.DoNothing
    # OperateType = PTT.WaterBallOperateType.Mail
    # OperateType = PT4T.WaterBallOperateType.Clear

    WaterBallList = PTTBot.getWaterBall(OperateType)

    if WaterBallList is None:
        return

    print('Result:')
    for WaterBall in WaterBallList:
        if WaterBall.getType() == PTT.WaterBallType.Catch:
            Temp = '★' + WaterBall.getTarget() + ' '
        elif WaterBall.getType() == PTT.WaterBallType.Send:
            Temp = 'To ' + WaterBall.getTarget() + ': '
        Temp += WaterBall.getContent() + ' [' + WaterBall.getDate() + ']'
        print(Temp)


def WaterBall():

    OperateType = PTT.WaterBallOperateType.Clear

    TestWaterBall = [str(x % 10) for x in range(10)]
    TagetID = 'DeepLearning'

    for Msg in TestWaterBall:
        PTTBot.throwWaterBall(TagetID, Msg)

        WaterBallList = PTTBot.getWaterBall(OperateType)

        if WaterBallList is None:
            return

        print('Result:')
        for WaterBall in WaterBallList:
            if WaterBall.getType() == PTT.WaterBallType.Catch:
                Temp = '★' + WaterBall.getTarget() + ' '
            elif WaterBall.getType() == PTT.WaterBallType.Send:
                Temp = 'To ' + WaterBall.getTarget() + ': '
            Temp += WaterBall.getContent() + ' [' + WaterBall.getDate() + ']'
            print(Temp)


def CallStatus():

    def showCallStatus(CallStatus):
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
        CallStatus = PTTBot.getCallStatus()
        showCallStatus(CallStatus)

    print('連續測試通過')

    InitCallStatus = random.randint(
        PTT.CallStatus.MinValue, PTT.CallStatus.MaxValue
    )

    TestQueue = [x for x in range(
        PTT.CallStatus.MinValue, PTT.CallStatus.MaxValue + 1
    )]
    random.shuffle(TestQueue)

    print('初始呼叫器狀態')
    showCallStatus(InitCallStatus)
    print('測試切換呼叫器狀態順序')
    for CurrentTestStatus in TestQueue:
        showCallStatus(CurrentTestStatus)

    PTTBot.setCallStatus(InitCallStatus)
    CallStatus = PTTBot.getCallStatus()
    if CallStatus != InitCallStatus:
        print('設定初始呼叫器狀態: 不通過')
        return
    print('設定初始呼叫器狀態: 通過')

    for CurrentTestStatus in TestQueue:
        print('準備設定呼叫器狀態')
        showCallStatus(CurrentTestStatus)

        PTTBot.setCallStatus(CurrentTestStatus)
        CallStatus = PTTBot.getCallStatus()
        showCallStatus(CallStatus)
        if CallStatus != CurrentTestStatus:
            print('設定呼叫器狀態: 不通過')
            return
        print('設定呼叫器狀態: 通過')

    print('呼叫器測試全數通過')


def GiveMoney():

    PTTBot.giveMoney('DeepLearning', 1)


def Mail():

    Content = '\r\n\r\n'.join(
        [
            '如有誤寄，對..對不起',
            'PTT Library 程式寄信測試內容',
            '程式碼: https://tinyurl.com/y2wuh8ck'
        ]
    )

    try:
        PTTBot.mail(
            'sdjfkdsjfls',
            '程式寄信標題',
            Content,
            0
        )
    except PTT.Exceptions.NoSuchUser:
        pass

    PTTBot.mail(
        ID,
        '程式寄信標題',
        Content,
        0
    )


def HasNewMail():

    result = PTTBot.hasNewMail()
    print(result)


ThreadBot = None


def ThreadingTest():
    def ThreadFunc():
        global ThreadBot
        ThreadBot = PTT.Library(
            # LogLevel=PTT.LogLevel.TRACE,
            # LogLevel=PTT.LogLevel.DEBUG,
        )
        try:
            ThreadBot.login(
                ID,
                Password,
                #  KickOtherLogin=True
            )
        except PTT.Exceptions.LoginError:
            ThreadBot.log('登入失敗')
            return

        ThreadBot.logout()
        print('多線程測試完成')

    t = threading.Thread(
        target=ThreadFunc
    )
    t.start()
    t.join()
    # ThreadBot.log('Hi')
    sys.exit()


def GetBoardList():
    BoardList = PTTBot.getBoardList()
    print(' '.join(BoardList))
    print(f'總共有 {len(BoardList)} 個板名')


if __name__ == '__main__':
    os.system('cls')
    print('Welcome to PTT Library v ' + PTT.Version + ' test case')

    if len(sys.argv) == 2:
        if sys.argv[1] == '-ci':
            print('CI test run success!!')
            sys.exit()

    ID, Password = getPW()

    try:
        # Loginout()
        # PerformanceTest()
        # ThreadingTest()

        PTTBot = PTT.Library(
            # LogLevel=PTT.LogLevel.TRACE,
            # LogLevel=PTT.LogLevel.DEBUG,
        )
        try:
            PTTBot.login(
                ID,
                Password,
                KickOtherLogin=True
            )
        except PTT.Exceptions.LoginError:
            PTTBot.log('登入失敗')
            sys.exit()

        # GetPost()
        # GetPostWithCondition()
        # Post()
        # GetNewestIndex()
        CrawlBoard()
        # CrawlBoardWithCondition()
        # Push()
        # GetUser()
        # ThrowWaterBall()
        # GetWaterBall()
        # WaterBall()
        # CallStatus()
        # GiveMoney()
        # Mail()
        # HasNewMail()
        # GetBoardList()
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)

    PTTBot.logout()
