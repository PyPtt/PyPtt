import sys
import os
import time
import json
import getpass
import traceback
import PTTLibrary
from PTTLibrary import PTT


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
    except PTTLibrary.ConnectCore.LoginError:
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
    except PTTLibrary.ConnectCore.LoginError:
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
    except PTTLibrary.ConnectCore.LoginError:
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
    except PTTLibrary.ConnectCore.LoginError:
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

    PTTBot.log('Performance Test Telnet ' + str(round(EndTime - StartTime, 2)) + ' s')

    print('Performance Test finish')


def GetPost():

    global PTTBot

    try:
        Post = PTTBot.getPost(
            'Wanted',
            PostIndex=7172,
            SearchType=PTT.PostSearchType.Keyword,
            SearchCondition='公告')

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
    PTTBot.getNewestIndex(PTT.IndexType.Board, Board='Wanted')

if __name__ == '__main__':
    os.system('cls')
    print('Welcome to PTT Library v ' + PTT.Version + ' test case')

    if len(sys.argv) == 2:
        if sys.argv[1] == '-ci':
            print('CI test run success!!')
            sys.exit()

    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        ID = input('請輸入帳號: ')
        Password = getpass.getpass('請輸入密碼: ')

    try:
        # Loginout()
        # PerformanceTest()

        PTTBot = PTT.Library(
            ConnectMode=PTT.ConnectMode.WebSocket,
            LogLevel=PTT.LogLevel.TRACE,
            # LogLevel=PTT.LogLevel.DEBUG,
        )
        try:
            PTTBot.login(ID,
                         Password,
                        #  KickOtherLogin=True
                         )
        except PTTLibrary.Exceptions.LoginError:
            PTTBot.log('登入失敗')
            sys.exit()
        
        # GetPost()
        # Post()
        GetNewestIndex()
    except Exception as e:

        traceback.print_tb(e.__traceback__)
        print(e)
    
    PTTBot.logout()