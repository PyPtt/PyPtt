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
    sys.exit()

    print('等待五秒')
    time.sleep(5)
    sys.exit()

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

    StartTime = time.time()
    for _ in range(TestTime):
        PTT_TIME = PTTBot.getTime()

        if PTT_TIME is None:
            print('PTT_TIME is None')
            break
        print(PTT_TIME)
    EndTime = time.time()
    PTTBot.logout()
    print('Performance Test WebSocket ' + str(
        round(EndTime - StartTime, 2)) + ' s')

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
    #     PTT_TIME = PTTBot.getTime()

    #     if PTT_TIME is None:
    #         print('PTT_TIME is None')
    #         break
    #     # print(PTT_TIME)
    # EndTime = time.time()

    # PTTBot.log('Performance Test Telnet ' +
    #            str(round(EndTime - StartTime, 2)) + ' s')

    print('Performance Test finish')
    sys.exit()


def GetPost():

    TestPostList = [
        # ('Python', 1),
        # ('NotExitBoard', 1),
        # ('Python', '1TJH_XY0'),
        # 文章格式錯誤
        # ('Steam', 4444),
        # ('Baseball', 199787),
        # ('Stock', 92324),
        # ('Stock', '1TVnEivO'),
        # 文章格式錯誤
        # ('movie', 457),
        # ('Gossiping', '1TU65Wi_'),
        # ('Gossiping', '1TWadtnq'),
        # ('Gossiping', '1TZBBkWP'),
        # ('joke', '1Tc6G9eQ'),
        # ('Test', 575),
        # 待證文章
        ('Test', '1U3pLzi0'),

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

    def show(Name, Value):
        if Value is not None:
            print(f'{Name} [{Value}]')
        else:
            print(f'無{Name}')

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

            if Post.isLock():
                print('鎖文狀態')
                continue

            show('Origin Post\n', Post.getOriginPost())
            print('=' * 30)
            show('Board', Post.getBoard())
            show('AID', Post.getAID())
            show('Author', Post.getAuthor())
            show('List Date', Post.getListDate())
            show('Title', Post.getTitle())
            show('Money', Post.getMoney())
            show('URL', Post.getWebUrl())

            if Post.isUnconfirmed():
                print('待證實文章')

            if not Query:
                show('Date', Post.getDate())
                show('Content', Post.getContent())
                show('IP', Post.getIP())
                show('Location', Post.getLocation())

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

                    if Push.getIP() is not None:
                        Buffer = f'{Type} {Author}: {Content} {Push.getIP()} {Push.getTime()}'
                    else:
                        Buffer = f'{Type} {Author}: {Content} {Push.getTime()}'
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

    # PTT1
    TestList = [
        ('Python', PTT.PostSearchType.Keyword, '[公告]'),
        ('ALLPOST', PTT.PostSearchType.Keyword, '(Wanted)'),
        ('Wanted', PTT.PostSearchType.Keyword, '(本文已被刪除)'),
        ('ALLPOST', PTT.PostSearchType.Keyword, '(Gossiping)'),
        ('Gossiping', PTT.PostSearchType.Keyword, '普悠瑪'),
        # PTT2
        # ('PttSuggest', PTT.PostSearchType.Keyword, '[問題]'),
        # ('PttSuggest', PTT.PostSearchType.Push, '10'),
    ]

    TestRange = 1
    Query = False

    for (Board, SearchType, Condition) in TestList:
        try:
            showCondition(Board, SearchType, Condition)
            Index = PTTBot.getNewestIndex(
                PTT.IndexType.BBS,
                Board,
                SearchType=SearchType,
                SearchCondition=Condition,
            )
            print(f'{Board} 最新文章編號 {Index}')

            for i in range(TestRange):
                Post = PTTBot.getPost(
                    Board,
                    PostIndex=Index - i,
                    # PostIndex=611,
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
    #         PTT.IndexType.BBS,
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
        'github: https://tinyurl.com/umqff3v',
        '開發手冊: https://hackmd.io/@CodingMan/PTTLibraryManual'
    ]
    Content = '\r\n\r\n'.join(Content)

    for _ in range(3):

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

        # PTT2
        # 'PttSuggest',
        # 'Test',
        # 'WhoAmI',
        # 'CodingMan'
    ]

    for Board in TestBoardList:
        for _ in range(1):
            Index = PTTBot.getNewestIndex(PTT.IndexType.BBS, Board=Board)
            print(f'{Board} 最新文章編號 {Index}')


def showValue(Msg, Value):
    print(f'{Msg} =>{Value}<=')


def detectNone(Name, Obj, Enable=True):
    if Obj is None and Enable:
        raise ValueError(Name + ' is None')


Query = True


def crawlHandler(Post):

    global Query

    if Post.getDeleteStatus() != PTT.PostDeleteStatus.NotDeleted:
        if Post.getDeleteStatus() == PTT.PostDeleteStatus.ByModerator:
            # print(f'[版主刪除][{Post.getAuthor()}]')
            pass
        elif Post.getDeleteStatus() == PTT.PostDeleteStatus.ByAuthor:
            # print(f'[作者刪除][{Post.getAuthor()}]')
            pass
        elif Post.getDeleteStatus() == PTT.PostDeleteStatus.ByUnknow:
            # print(f'[不明刪除]')
            pass
        return

    # if Post.getTitle().startswith('Fw:') or Post.getTitle().startswith('轉'):
    # print(f'[{Post.getAID()}][{Post.getAuthor()}][{Post.getTitle()}]')
    # print(f'[{Post.getContent()}]')

    # print(f'[{Post.getAuthor()}][{Post.getTitle()}]')

    PushNumber = Post.getPushNumber()
    if PushNumber is not None:
        if PushNumber == '爆':
            pass
        elif PushNumber.startswith('X'):
            N = PushNumber[1:]
        else:
            if not PushNumber.isdigit():
                print(f'[{Post.getAID()}][{Post.getPushNumber()}]')
                print(f'[{Post.getAID()}][{Post.getPushNumber()}]')
                print(f'[{Post.getAID()}][{Post.getPushNumber()}]')
                raise ValueError()
        # print(f'[{Post.getAID()}][{Post.getPushNumber()}]')

    detectNone('標題', Post.getTitle())
    # detectNone('AID', Post.getAID())
    detectNone('Author', Post.getAuthor())
    # detectNone('Money', Post.getMoney())
    detectNone('WebUrl', Post.getWebUrl())
    # detectNone('ListDate', Post.getListDate())

    # if not Query:
    # detectNone('Date', Post.getDate())
    # detectNone('Content', Post.getContent())
    # detectNone('IP', Post.getIP())

    # time.sleep(0.2)


def CrawlBoard():

    global Query
    TestBoardList = [
        # 'Test',
        'Wanted',
        'Gossiping',
        'Stock',
        'movie',
        # 'C_Chat',
        # 'Baseball',
        # 'NBA',
        # 'HatePolitics',

        # PTT2
        # 'Test',
        # 'WhoAmI',
        # 'PttSuggest'
    ]

    # CrawlType = PTT.IndexType.Web
    CrawlType = PTT.IndexType.BBS

    Type = 'Index'

    TestRange = 5000
    TestRound = 5

    for _ in range(TestRound):

        for TestBoard in TestBoardList:

            if CrawlType == PTT.IndexType.BBS:

                if Type == 'Index':
                    NewestIndex = PTTBot.getNewestIndex(
                        PTT.IndexType.BBS,
                        Board=TestBoard
                    )
                    StartIndex = NewestIndex - TestRange + 1

                    print(
                        f'預備爬行 {TestBoard} 編號 {StartIndex} ~ {NewestIndex} 文章')

                    print(f'TestBoard [{TestBoard}]')
                    ErrorPostList, DelPostList = PTTBot.crawlBoard(
                        crawlHandler,
                        PTT.CrawlType.BBS,
                        TestBoard,
                        StartIndex=StartIndex,
                        EndIndex=NewestIndex,
                        Query=Query
                    )
                elif Type == 'AID':

                    StartAID = '1TnDKzxw'
                    EndAID = '1TnCPFGu'

                    ErrorPostList, DelPostList = PTTBot.crawlBoard(
                        crawlHandler,
                        PTT.CrawlType.BBS,
                        TestBoard,
                        StartAID=StartAID,
                        EndAID=EndAID
                    )
                if len(ErrorPostList) > 0:
                    print('格式錯誤文章: \n' + '\n'.join(str(x)
                                                   for x in ErrorPostList))
                else:
                    print('沒有偵測到格式錯誤文章')

                if len(DelPostList) > 0:
                    print(f'共有 {len(DelPostList)} 篇文章被刪除')

            elif CrawlType == PTT.IndexType.Web:

                NewestIndex = PTTBot.getNewestIndex(
                    PTT.IndexType.Web,
                    Board=TestBoard
                )
                EndPage = NewestIndex

                StartPage = EndPage - TestRange + 1

                print(f'預備爬行 {TestBoard} 最新頁數 {NewestIndex}')
                print(f'預備爬行 {TestBoard} 編號 {StartPage} ~ {EndPage} 文章')

                ErrorPostList, DelPostList = PTTBot.crawlBoard(
                    crawlHandler,
                    PTT.CrawlType.Web,
                    TestBoard,
                    StartPage=StartPage,
                    EndPage=EndPage
                    # Query=Query
                )

                if len(DelPostList) > 0:
                    print('\n'.join(DelPostList))
                    print(f'共有 {len(DelPostList)} 篇文章被刪除')


def CrawlBoardWithCondition():

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

    TestList = [
        # ('Stock', PTT.PostSearchType.Keyword, '盤中閒聊'),
        ('Baseball', PTT.PostSearchType.Push, '20')
    ]

    TestRange = 100

    for (Board, SearchType, Condition) in TestList:
        showCondition(Board, SearchType, Condition)
        NewestIndex = PTTBot.getNewestIndex(
            PTT.IndexType.BBS,
            Board,
            SearchType=SearchType,
            SearchCondition=Condition,
        )
        print(f'{Board} 最新文章編號 {NewestIndex}')

        StartIndex = NewestIndex - TestRange + 1

        ErrorPostList, DelPostList = PTTBot.crawlBoard(
            crawlHandler,
            PTT.CrawlType.BBS,
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
        ('Test', 804),
        # ('Wanted', '1Teyovc3')
    ]

    Content = '''
推文測試
'''
    for (Board, Index) in TestPostList:
        if isinstance(Index, int):
            PTTBot.push(Board, PTT.PushType.Push, Content, PostIndex=Index)
        else:
            PTTBot.push(Board, PTT.PushType.Push, Content, PostAID=Index)


def ThrowWaterBall():

    TagetID = 'DeepLearning'

    # TestWaterBall = [str(x) + '_' * 35 + ' 水球測試結尾' for x in range(30)]
    # # TestWaterBall = TestWaterBall * 3
    # TestWaterBall = '\n'.join(TestWaterBall)
    TestWaterBall = '水球測試1 :D\n水球測試2 :D'

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
            'github: https://tinyurl.com/umqff3v'
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
    ID1 = 'QQ1'
    Password1 = 'xxxxx'

    ID2 = 'QQ2'
    Password2 = 'xxxxx'

    def ThreadFunc1():
        ThreadBot1 = PTT.Library()
        try:
            ThreadBot1.login(
                ID1,
                Password1,
                #  KickOtherLogin=True
            )
        except PTT.Exceptions.LoginError:
            ThreadBot1.log('登入失敗')
            return

        ThreadBot1.logout()
        print('1 多線程測試完成')

    def ThreadFunc2():
        ThreadBot2 = PTT.Library()
        try:
            ThreadBot2.login(
                ID2,
                Password2,
                #  KickOtherLogin=True
            )
        except PTT.Exceptions.LoginError:
            ThreadBot2.log('登入失敗')
            return

        ThreadBot2.logout()
        print('2 多線程測試完成')

    t1 = threading.Thread(
        target=ThreadFunc1
    )
    t2 = threading.Thread(
        target=ThreadFunc2
    )

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # ThreadBot.log('Hi')
    sys.exit()


def GetBoardList():

    BoardList = PTTBot.getBoardList()
    # print(' '.join(BoardList))
    print(f'總共有 {len(BoardList)} 個板名')
    print(f'總共有 {len(set(BoardList))} 個不重複板名')


def ReplyPost():

    ReplyPostIndex = 755

    PTTBot.replyPost(
        PTT.ReplyType.Board,
        'Test',
        '測試回應到板上，如有打擾抱歉',
        PostIndex=ReplyPostIndex
    )

    PTTBot.replyPost(
        PTT.ReplyType.Mail,
        'Test',
        '測試回應到信箱，如有打擾抱歉',
        PostIndex=ReplyPostIndex
    )

    PTTBot.replyPost(
        PTT.ReplyType.Board_Mail,
        'Test',
        '測試回應到板上還有信箱，如有打擾抱歉',
        PostIndex=ReplyPostIndex
    )


def SetBoardTitle():
    from time import gmtime, strftime

    while True:
        Time = strftime('%H:%M:%S')
        try:
            PTTBot.setBoardTitle(
                'CodingMan',
                f'現在時間 {Time}'
            )
        except PTT.Exceptions.ConnectionClosed:
            while True:
                try:
                    PTTBot.login(
                        ID,
                        Password,
                        KickOtherLogin=True
                    )
                    break
                except PTT.Exceptions.LoginError:
                    PTTBot.log('登入失敗')
                    time.sleep(1)
                except PTT.Exceptions.ConnectError:
                    PTTBot.log('登入失敗')
                    time.sleep(1)
        print('已經更新時間 ' + Time, end='\r')
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print('已經更新時間 ' + Time)
            PTTBot.setBoardTitle(
                'CodingMan',
                '專業程式 BUG 製造機'
            )
            print('板標已經恢復')
            break


def MarkPost():

    MarkType = PTT.MarkType.Unconfirmed

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

    PTTBot.markPost(
        MarkType,
        'give',
        PostIndex=2000
    )


def getPostIndexTest():

    BoardList = [
        'Wanted',
        'Gossiping'
    ]
    Range = 100

    for Board in BoardList:

        Index = PTTBot.getNewestIndex(
            PTT.IndexType.BBS,
            Board,
        )

        for i in range(Range):

            Post = PTTBot.getPost(
                Board,
                PostIndex=Index - i,
                Query=True
            )

            if Post is None:
                print('Empty')
                continue

            if Post.getDeleteStatus() != PTT.PostDeleteStatus.NotDeleted:
                print('被刪除文章')
                continue

            print(Post.getAID())

            PostIndex = PTTBot._getPostIndex(Board, Post.getAID())
            print(PostIndex)
            if Index - i != PostIndex:
                print('!!!!!!!!!!!!!!!!!!!!!!!!!')
                return

        print('=' * 50)


def GetFavouriteBoard():
    List = PTTBot.getFavouriteBoard()

    for board in List:
        Buff = f'[{board.getBoard()}][{board.getType()}][{board.getBoardTitle()}]'
        print(Buff)


def GetBoardInfo():

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

    getSetting = True

    BoardInfo = PTTBot.getBoardInfo('Gossiping', setting=getSetting)
    print('板名: ', BoardInfo.getBoard())
    print('線上人數: ', BoardInfo.getOnlineUser())
    if getSetting:
        print('中文敘述: ', BoardInfo.getChineseDes())
        print('板主: ', BoardInfo.getModerators())
        print('公開狀態(是否隱形): ', BoardInfo.isOpen())
        print('隱板時是否可進入十大排行榜: ', BoardInfo.canIntoTopTenWhenHide())
        print('是否開放非看板會員發文: ', BoardInfo.canNonBoardMembersPost())
        print('是否開放回應文章: ', BoardInfo.canReplyPost())
        print('是否開放自刪文章: ', BoardInfo.canSelfDelPost())
        print('是否開放推薦文章: ', BoardInfo.canPushPost())
        print('是否開放噓文: ', BoardInfo.canBooPost())
        print('是否可以快速連推文章: ', BoardInfo.canFastPush())
        print('推文最低間隔時間: ', BoardInfo.getMinInterval())
        print('推文時是否記錄來源 IP: ', BoardInfo.isPushRecordIP())
        print('推文時是否對齊開頭: ', BoardInfo.isPushAligned())
        print('板主是否可刪除部份違規文字: ', BoardInfo.canModeratorCanDelIllegalContent())
        print('轉錄文章是否自動記錄，且是否需要發文權限: ',
              BoardInfo.isTranPostAutoRecordedAndRequirePostPermissions())
        print('是否為冷靜模式: ', BoardInfo.isCoolMode())
        print('是否需要滿十八歲才可進入: ', BoardInfo.isRequire18())
        print('發文與推文限制需多少次以上: ', BoardInfo.getRequireLoginTime())
        print('發文與推文限制退文篇數多少篇以下: ', BoardInfo.getRequireIllegalPost())


def Bucket():
    PTTBot.bucket(
        'give',
        7,
        'Bucket Reason',
        'CodingMan'
    )


def SearchUser():
    userlist = PTTBot.searchUser(
        'abcd',
        # minpage=1,
        # maxpage=10
    )
    print(userlist)
    print(len(userlist))

    # if 'abcd0800' in userlist:
    #     print('exist')
    # else:
    #     print('Not exist')


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
        # ThreadingTest()

        PTTBot = PTT.Library(
            # LogLevel=PTT.LogLevel.TRACE,
            # LogLevel=PTT.LogLevel.DEBUG,
            # Host=PTT.Host.PTT2
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

        # PerformanceTest()

        # GetPost()
        # GetPostWithCondition()
        # Post()
        # GetNewestIndex()
        # CrawlBoard()
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
        # GetBoardInfo()
        # ReplyPost()
        # GetFavouriteBoard()
        # SearchUser()

        # Bucket()
        # SetBoardTitle()
        # MarkPost()

        # private test
        # getPostIndexTest()

        # FullTest()
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
    except KeyboardInterrupt:
        pass

    PTTBot.logout()
