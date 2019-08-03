import sys
import os
import time
import json
import traceback
import PTTLibrary
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

    global PTTBot

    try:

        Post = PTTBot.getPost(
            'Wanted',
            PostIndex=79697,
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
            print('List Date' + Post.getListDate())

            print(f'{len(Post.getPushList())} pushs')

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

            print(f'{PushCount} Pushs {BooCount} Boo {ArrowCount} Arrow')
    except Exception as e:

        traceback.print_tb(e.__traceback__)
        print(e)


def Post():
    global PTTBot

    # for i in range(3):
    #     PTTBot.post('Test', 'PTT Library 自動測試 ' + str(i), '測試貼文', 1, 0)

    PTTBot.post('Test',
                'PTT Library 自動測試',
                PTT.Command.ControlCode + 's',
                1, 0)


def GetNewestIndex():
    global PTTBot

    for _ in range(30):
        PTTBot.getNewestIndex(PTT.IndexType.Board, Board='Wanted')
        time.sleep(1)


def showValue(Msg, Value):
    print(f'{Msg} =>{Value}<=')


def detectNone(Name, Obj):
    if Obj is None:
        raise ValueError(f'{Name} is None')


DelPostCount = 0


def crawlHandler(Post):

    if Post.getDeleteStatus() != PTT.DataType.PostDeleteStatus.NotDeleted:
        global DelPostCount
        DelPostCount += 1
        return

    detectNone('標題', Post.getTitle())
    detectNone('AID', Post.getAID())
    detectNone('Author', Post.getAuthor())
    detectNone('Date', Post.getDate())
    detectNone('Content', Post.getContent())
    # print(Post.getContent())
    detectNone('Money', Post.getMoney())
    detectNone('WebUrl', Post.getWebUrl())
    detectNone('IP', Post.getIP())
    detectNone('ListDate', Post.getListDate())


def CrawlBoard():
    global PTTBot

    TestBoard = 'Wanted'
    TestRange = 100

    NewestIndex = PTTBot.getNewestIndex(PTT.IndexType.Board, Board=TestBoard)
    StartIndex = NewestIndex - TestRange + 1

    print(f'預備爬行編號 {StartIndex} ~ {NewestIndex} 文章')

    ErrorPostList, DelPostList = PTTBot.crawlBoard(
        crawlHandler,
        TestBoard,
        StartIndex=StartIndex,
        EndIndex=NewestIndex

        # StartIndex=79525,
        # EndIndex=79525
    )

    if len(ErrorPostList) > 0:
        print('Error Post: \n' + '\n'.join(str(x) for x in ErrorPostList))

    if len(DelPostList) > 0:
        print('Del Post: \n' + '\n'.join(str(x) for x in DelPostList))
        print(f'共有 {len(DelPostList)} 篇文章被刪除')


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
    Content = '''
What is Ptt?
批踢踢 (Ptt) 是以學術性質為目的，提供各專業學生實習的平台，而以電子佈告欄系統 (BBS, Bulletin Board System) 為主的一系列服務。
期許在網際網路上建立起一個快速、即時、平等、免費，開放且自由的言論空間。批踢踢實業坊同時承諾永久學術中立，絕不商業化、絕不營利。
'''
    # PTTBot.push('Test', PTT.PushType.Push, 'Test', PostIndex=225)
    # PTTBot.push('Test', PTT.PushType.Push, Content, PostIndex=225)
    PTTBot.push('Gossiping', PTT.PushType.Push, Content, PostIndex=95693)


def ThrowWaterBall():

    TagetID = 'DeepLearning'

    TestWaterBall = [str(x % 10) for x in range(10)]
    TestWaterBall = TestWaterBall * 3
    TestWaterBall = '\n'.join(TestWaterBall)
    # TestWaterBall = 'Q_Q'

    PTTBot.throwWaterBall(TagetID, TestWaterBall)


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


if __name__ == '__main__':
    os.system('cls')
    print('Welcome to PTT Library v ' + PTT.Version + ' test case')

    # print(len('\x1B[[d+;]'))
    # print(len('[[d+;]'))

    # sys.exit()

    if len(sys.argv) == 2:
        if sys.argv[1] == '-ci':
            print('CI test run success!!')
            sys.exit()

    ID, Password = getPW()

    try:
        # Loginout()
        # PerformanceTest()

        PTTBot = PTT.Library(
            ConnectMode=PTT.ConnectMode.WebSocket,
            # LogLevel=PTT.LogLevel.TRACE,
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
            sys.exit()

        # GetPost()
        # Post()
        # GetNewestIndex()
        # CrawlBoard()
        # Push()
        # GetUser()
        # ThrowWaterBall()
        # GetWaterBall()
        WaterBall()
    except Exception as e:

        traceback.print_tb(e.__traceback__)
        print(e)

    PTTBot.logout()
