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
    except PTTLibrary.Exceptions.LoginError:
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
    except PTTLibrary.Exceptions.LoginError:
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
    except PTTLibrary.Exceptions.LoginError:
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
    except PTTLibrary.Exceptions.LoginError:
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
        ('Python', 1),
        ('NotExitBoard', 1),
    ]

    for (Board, Index) in TestPostList:
        try:
            Post = PTTBot.getPost(
                Board,
                PostIndex=Index,
                # SearchType=PTT.PostSearchType.Keyword,
                # SearchCondition='公告'
            )

            if Post is not None:
                print('Board: ' + Post.getBoard())
                print('AID: ' + Post.getAID())
                print('Author: ' + Post.getAuthor())
                print('Date: ' + Post.getDate())
                print('Title: ' + Post.getTitle())
                print('Content: ' + Post.getContent())
                print('Money: ' + str(Post.getMoney()))
                print('URL: ' + Post.getWebUrl())
                print('IP: ' + Post.getIP())
                # 在文章列表上的日期
                print('List Date: ' + Post.getListDate())

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
                    if Push.getType() == PTT.PushType.Boo:
                        BooCount += 1
                    if Push.getType() == PTT.PushType.Arrow:
                        ArrowCount += 1

                print(
                    f'Total {PushCount} Pushs {BooCount} Boo {ArrowCount} Arrow'
                )
        except Exception as e:

            traceback.print_tb(e.__traceback__)
            print(e)


TestList = [
    # ('Wanted', PTT.PostSearchType.Keyword, '[公告]'),
    # ('Wanted', PTT.PostSearchType.Author, 'gogin'),
    # ('Wanted', PTT.PostSearchType.Push, '10'),
    # ('Wanted', PTT.PostSearchType.Mark, 'm'),
    # ('Wanted', PTT.PostSearchType.Money, '5'),
    # ('Gossiping', PTT.PostSearchType.Keyword, '[公告]'),
    # ('Gossiping', PTT.PostSearchType.Author, 'ReDmango'),
    # ('Gossiping', PTT.PostSearchType.Push, '10'),
    # ('Gossiping', PTT.PostSearchType.Mark, 'm'),
    # ('Gossiping', PTT.PostSearchType.Money, '5'),

    # ('Gossiping', PTT.PostSearchType.Push, '-100'),
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

            Post = PTTBot.getPost(
                Board,
                PostIndex=Index,
                SearchType=SearchType,
                SearchCondition=Condition,
            )

            print('標題: ' + Post.getTitle())
            print('=' * 50)

        except Exception as e:

            traceback.print_tb(e.__traceback__)
            print(e)


def Post():

    # PTTBot.post(
    #     'Test',
    #     'PTT Library 自動測試',
    #     PTT.Command.ControlCode + 's',
    #     1,
    #     0
    # )

    Content = [
        'PTT Library 貼文測試，如有打擾請告知。',
        '程式碼: https://tinyurl.com/y2wuh8ck'
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
        'Test'
    ]

    for Board in TestBoardList:
        for _ in range(10):
            Index = PTTBot.getNewestIndex(PTT.IndexType.Board, Board=Board)
            print(f'{Board} 最新文章編號 {Index}')


def showValue(Msg, Value):
    print(f'{Msg} =>{Value}<=')


def detectNone(Name, Obj, Enable=True):
    if Obj is None and Enable:
        raise ValueError(Name + ' is None')


def crawlHandler(Post):

    if Post.getDeleteStatus() != PTT.PostDeleteStatus.NotDeleted:
        return

    detectNone('標題', Post.getTitle())
    detectNone('AID', Post.getAID())
    detectNone('Author', Post.getAuthor())
    detectNone('Date', Post.getDate())
    detectNone('Content', Post.getContent())
    detectNone('Money', Post.getMoney())
    detectNone('WebUrl', Post.getWebUrl())
    # detectNone('IP', Post.getIP())
    # detectNone('ListDate', Post.getListDate())


def CrawlBoard():

    TestBoardList = [
        'Wanted',
        'Gossiping'
    ]

    TestBoard = 'Wanted'
    TestRange = 100

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
            EndIndex=NewestIndex
        )

        if len(ErrorPostList) > 0:
            print('Error Post: \n' + '\n'.join(str(x) for x in ErrorPostList))

        if len(DelPostList) > 0:
            print('Del Post: \n' + '\n'.join([str(x) for x in DelPostList]))
            print(f'共有 {len(DelPostList)} 篇文章被刪除')


def CrawlBoardWithCondition():

    TestRange = 10

    for (Board, SearchType, Condition) in TestList:
        try:
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

        except Exception as e:

            traceback.print_tb(e.__traceback__)
            print(e)


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

    except PTTLibrary.Exceptions.NoSuchUser:
        print('無此使用者')


def Push():

    TestPostList = [
        # ('Gossiping', 95693),
        ('Test', 656)
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

    # TestWaterBall = [str(x % 10) for x in range(10)]
    # TestWaterBall = TestWaterBall * 3
    # TestWaterBall = '\n'.join(TestWaterBall)
    TestWaterBall = '水球測試 :D'

    PTTBot.throwWaterBall(TagetID, TestWaterBall)
    time.sleep(3)


def GetWaterBall():

    OperateType = PTT.WaterBallOperateType.DoNothing
    # OperateType = PTT.WaterBallOperateType.Mail
    # OperateType = PTT.WaterBallOperateType.Clear

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


def HashNewMail():

    result = PTTBot.hasNewMail()
    print(result)
    result = PTTBot.hasNewMail()
    print(result)


PTTBot = None


def ThreadingTest():
    global PTTBot
    def ThreadFunc():
        global PTTBot
        PTTBot = PTT.Library(
            ConnectMode=PTT.ConnectMode.WebSocket,
            LogLevel=PTT.LogLevel.TRACE,
            # LogLevel=PTT.LogLevel.DEBUG,
        )
        try:
            PTTBot.login(
                ID,
                Password,
                #  KickOtherLogin=True
            )
        except PTTLibrary.Exceptions.LoginError:
            PTTBot.log('登入失敗')
            return
        print('多線程測試完成')

    t = threading.Thread(
        target=ThreadFunc
    )
    t.start()
    t.join()
    PTTBot.logout()
    sys.exit()


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
            ConnectMode=PTT.ConnectMode.WebSocket,
            # LogLevel=PTT.LogLevel.TRACE,
        )
        try:
            PTTBot.login(
                ID,
                Password,
                #  KickOtherLogin=True
            )
        except PTTLibrary.Exceptions.LoginError:
            PTTBot.log('登入失敗')
            sys.exit()

        GetPost()
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
        # HashNewMail()
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)

    PTTBot.logout()
