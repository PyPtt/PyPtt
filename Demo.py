import sys
import time
import json
import traceback
import random

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


def LoginLogout():
    # 登入登出範例
    # 不支援 Multi-thread 如果有需求，請多開多個 Bot

    # Library() 參數
    #   LogLevel (Optional):
    #       PTT.LogLevel.DEBUG
    #       PTT.LogLevel.INFO (預設值)
    #       PTT.LogLevel.SLIENT
    #   Language (Optional):
    #       PTT.Language.Chinese (預設值)
    #       PTT.Language.English

    # login() 參數
    #   ID:
    #       你的 PTT 帳號
    #   Password:
    #       你的 PTT 密碼
    #   KickOtherLogin (Optional):
    #       是否剔除其他登入。
    #       預設值為 False

    # logout() 無參數輸入

    PTTBot = PTT.Library()
    try:
        PTTBot.login(ID, Password)
    except PTT.Exceptions.LoginError:
        PTTBot.log('登入失敗')
        return
    PTTBot.log('登入成功')
    PTTBot.logout()
    sys.exit()


def LogHandlerDemo():
    def handler(Msg):
        with open('LogHandler.txt', 'a', encoding='utf-8') as F:
            F.write(Msg + '\n')

    PTTBot = PTT.Library(
        LogHandler=handler
    )
    try:
        PTTBot.login(ID, Password)
    except PTT.Exceptions.LoginError:
        PTTBot.log('登入失敗')
        return
    PTTBot.log('登入成功')
    PTTBot.logout()
    sys.exit()


def GetTime():

    # 取得 PTT 時間範例

    PTT_TIME = PTTBot.getTime()
    print(PTT_TIME)


def GetPost():

    # 取得特定文章範例

    # getPost() 參數說明
    #   Board:
    #       文章版
    #   PostAID (Optional):
    #       可輸入目標文章的 AID，來取得內容
    #       此參數必須與 PostIndex，擇一輸入
    #   PostIndex (Optional):
    #       可輸入目標文章的編號，來取得內容
    #       此參數必須與 PostAID，擇一輸入
    #   SearchType (Optional):
    #       可以輸入搜尋類型來取得你想要的文章 ex: [公告]
    #       PTT.PostSearchType.Keyword                  關鍵字
    #       PTT.PostSearchType.Author                   作者
    #       PTT.PostSearchType.Push                     推文數
    #       PTT.PostSearchType.Mark                     標記 ex: m or s
    #       PTT.PostSearchType.Money                    稿酬
    #   SearchCondition (Optional):
    #       如果你使用了 SearchType，那麼你就需要在這個欄位輸入你想要的條件
    #
    #   回傳: 文章資訊

    ################## 文章資訊 Post information ##################
    # getBoard()                                    文章所在的版
    # getAID()                                      文章 ID ex: 1PCBfel1
    # getAuthor()                                   作者
    # getDate()                                     文章發布時間
    # getTitle()                                    文章標題
    # getContent()                                  文章內文
    # getMoney()                                    文章P幣
    # getIP()                                       發文位址
    # getWebUrl()                                   文章網址
    # getPushList()                                 文章即時推文清單
    # getDeleteStatus()                             文章被刪除的狀態 ex: 被作者或版主刪除
        # PTT.PostDeleteStatus.NotDeleted               沒有被刪除
        # PTT.PostDeleteStatus.ByAuthor                 被作者刪除
        # PTT.PostDeleteStatus.ByModerator              被版主刪除
    # getListDate()                                 文章列表的日期
    # hasControlCode()                              是否含有控制碼

    ################## 推文資訊 Push information ##################
    # getType()                                     推文類別 推噓箭頭
        # PTT.PushType.Push                             推文
        # PTT.PushType.Boo                              噓文
        # PTT.PushType.Arrow                            箭頭
    # getAuthor()                                   推文ID
    # getContent()                                  推文內文
    # getIP()                                       推文IP
    # getTime()                                     推文時間

    ################## 文章搜尋資訊 Post Search Type information ###
    # PTT.PostSearchType.Keyword                   搜尋關鍵字
    # PTT.PostSearchType.Author                    搜尋作者
    # PTT.PostSearchType.Push                      搜尋推文數
    # PTT.PostSearchType.Mark                      搜尋標記 m or s
    # PTT.PostSearchType.Money                     搜尋稿酬

    Post = PTTBot.getPost(
        'Python',
        PostIndex=7486
    )

    if Post is None:
        print('Post is None')
    if Post.getDeleteStatus() == PTT.PostDeleteStatus.ByAuthor:
        print('文章被作者刪了')
    if Post.getDeleteStatus() == PTT.PostDeleteStatus.ByModerator:
        print('文章被版主刪了')

    # 如果到這兒
    # 表示 Post.getDeleteStatus() == PTT.PostDeleteStatus.NotDeleted

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
        if Push.getType() == PTT.PushType.Push:
            Type = '推'
            PushCount += 1
        if Push.getType() == PTT.PushType.Boo:
            Type = '噓'
            BooCount += 1
        if Push.getType() == PTT.PushType.Arrow:
            Type = '箭頭'
            ArrowCount += 1

        Author = Push.getAuthor()
        Content = Push.getContent()

        Buffer = f'[{Author}] 給了一個{Type} 說 [{Content}]'
        if Push.getIP() is not None:
            Buffer += f' 來自 [{Push.getIP()}]'
        Buffer += f' 時間是 [{Push.getTime()}]'
        print(Buffer)

    print(f'Total {PushCount} Pushs {BooCount} Boo {ArrowCount} Arrow')


def Post_GetNewestIndex_Push():
    # 貼文範例
    # 取得某版最新文章編號範例
    # 推文範例

    # post() 參數說明
    #   Board:
    #       文章版
    #   Title:
    #       標題
    #   Content:
    #       文章內文
    #   PostType:
    #       標題分類，每個板都會有幾個標題分類讓你選，
    #       你可以選擇你要用哪一個
    #   SignFile:
    #       選擇用哪一個簽名檔

    # getNewestIndex() 參數說明
    #   IndexType:
    #       可以取得兩種不一樣的最新編號，
    #       PTT.IndexType.BBS                           某版的最新文章編號
    #       PTT.IndexType.Mail  (尚未啟用)               信箱的最新信件編號
    #   Board:
    #       文章版
    #   SearchType (Optional):
    #       可以輸入搜尋類型來取得你想要的文章 ex: [公告]
    #       PTT.PostSearchType.Keyword                  關鍵字
    #       PTT.PostSearchType.Author                   作者
    #       PTT.PostSearchType.Push                     推文數
    #       PTT.PostSearchType.Mark                     標記 ex: m or s
    #       PTT.PostSearchType.Money                    稿酬
    #   SearchCondition (Optional):
    #       如果你使用了 SearchType，那麼你就需要在這個欄位輸入你想要的條件
    #
    #   回傳: 最新編號

    # push() 參數說明
    #   Board:
    #       文章版
    #   PushType:
    #       推文類型，推噓或者箭頭
    #       PTT.PushType.Push                           推
    #       PTT.PushType.Boo                            噓
    #       PTT.PushType.Arrow                          箭頭
    #   PushContent:
    #       推文內容
    #   PostAID (Optional):
    #       可輸入目標文章的 AID，來取得內容
    #       此參數必須與 PostIndex，擇一輸入
    #   PostIndex (Optional):
    #       可輸入目標文章的編號，來取得內容
    #       此參數必須與 PostAID，擇一輸入

    Board = 'Test'

    Content = '\r\n\r\n'.join(
        [
            'PTT Library 貼文測試，如有打擾請告知。',
            '程式碼: https://tinyurl.com/y2wuh8ck'
        ]
    )

    PTTBot.post(
        # 版
        Board,
        # 標題
        'PTT Library 程式貼文測試',
        # 內文
        Content,
        # 標題分類
        1,
        # 簽名檔
        0
    )

    Index = PTTBot.getNewestIndex(PTT.IndexType.BBS, Board=Board)
    print(f'{Board} 最新文章編號 {Index}')

    Content = '''
What is Ptt?
批踢踢 (Ptt) 是以學術性質為目的，提供各專業學生實習的平台，而以電子佈告欄系統 (BBS, Bulletin Board System) 為主的一系列服務。
期許在網際網路上建立起一個快速、即時、平等、免費，開放且自由的言論空間。批踢踢實業坊同時承諾永久學術中立，絕不商業化、絕不營利。
'''
    PTTBot.push(Board, PTT.PushType.Push, Content, PostIndex=Index)


def CrawlBoard():
    # 大量爬文範例

    # crawlBoard() 參數說明
    #   PostHandler:
    #       每當取得一篇新文章，傳入的 handler 就會在內部被呼叫
    #   Board:
    #       文章版
    #   StartIndex:
    #       起始爬行文章編號
    #   EndIndex:
    #       結束爬行文章編號
    #   SearchType (Optional):
    #       可以輸入搜尋類型來取得你想要的文章 ex: [公告]
    #       PTT.PostSearchType.Keyword                  關鍵字
    #       PTT.PostSearchType.Author                   作者
    #       PTT.PostSearchType.Push                     推文數
    #       PTT.PostSearchType.Mark                     標記 ex: m or s
    #       PTT.PostSearchType.Money                    稿酬
    #   SearchCondition (Optional):
    #       如果你使用了 SearchType，那麼你就需要在這個欄位輸入你想要的條件
    #
    #   回傳: 出現錯誤的文章編號清單, 被刪除的文章編號清單

    # getNewestIndex() 參數說明
    #   IndexType:
    #       可以取得兩種不一樣的最新編號，
    #       PTT.IndexType.BBS                         某版的最新文章編號
    #       PTT.IndexType.Mail  (尚未啟用)               信箱的最新信件編號
    #   Board:
    #       文章版
    #   SearchType (Optional):
    #       可以輸入搜尋類型來取得你想要的文章 ex: [公告]
    #       PTT.PostSearchType.Keyword                  關鍵字
    #       PTT.PostSearchType.Author                   作者
    #       PTT.PostSearchType.Push                     推文數
    #       PTT.PostSearchType.Mark                     標記 ex: m or s
    #       PTT.PostSearchType.Money                    稿酬
    #   SearchCondition (Optional):
    #       如果你使用了 SearchType，那麼你就需要在這個欄位輸入你想要的條件
    #
    # 回傳: 最新編號

    def crawlHandler(Post):

        def detectNone(Name, Obj):
            if Obj is None:
                raise ValueError(f'{Name} is None')

        if Post.getDeleteStatus() != PTT.PostDeleteStatus.NotDeleted:
            return

        detectNone('標題', Post.getTitle())
        detectNone('AID', Post.getAID())
        detectNone('Author', Post.getAuthor())
        detectNone('Date', Post.getDate())
        detectNone('Content', Post.getContent())
        detectNone('Money', Post.getMoney())
        detectNone('WebUrl', Post.getWebUrl())
        detectNone('IP', Post.getIP())
        detectNone('ListDate', Post.getListDate())

    TestBoard = 'Python'
    TestRange = 100

    NewestIndex = PTTBot.getNewestIndex(
        PTT.IndexType.BBS,
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
        print('Del Post: \n' + '\n'.join(str(x) for x in DelPostList))
        print(f'共有 {len(DelPostList)} 篇文章被刪除')


def GetUser():

    # 取得使用者資訊範例

    # getUser() 參數說明
    #   UserID:
    #       你想要查詢的 ID
    #
    #   回傳: 使用者資訊

    ################## 使用者資訊 User information ##################
    # getID()                                       使用者 ID
    # getMoney()                                    經濟欄位
    # getLoginTime()                                登入次數
    # getLegalPost()                                有效文章數
    # getIllegalPost()                              退文文章數

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
        PTTBot.log('象棋戰績: ' + User.getChess())
        PTTBot.log('簽名檔:\n' + User.getSignatureFile())

    except PTT.Exceptions.NoSuchUser:
        print('無此使用者')


def ThrowWaterBall():

    # 丟水球範例

    TagetID = 'CodingMan'
    TestWaterBall = '哈囉，這是水球測試'

    try:
        PTTBot.throwWaterBall(TagetID, TestWaterBall)
    except PTT.Exceptions.NoSuchUser:
        print('無此使用者')
    except PTT.Exceptions.UserOffline:
        print('使用者離線')


def GetWaterBall():

    # 取得歷史水球範例

    # getWaterBall() 參數說明
    #   OperateType:
    #       看完歷史水球之後的操作
    #       PTT.WaterBallOperateType.DoNothing          不做任何動作
    #       PTT.WaterBallOperateType.Mail               存到信箱
    #       PTT.WaterBallOperateType.Clear              清除

    OperateType = PTT.WaterBallOperateType.DoNothing
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

    # 呼叫器範例

    # setCallStatus() 參數說明
    #   CallStatus:
    #       輸入你想要的呼叫器狀態
    #       PTT.CallStatus.On                           打開
    #       PTT.CallStatus.Unplug                       拔掉
    #       PTT.CallStatus.Waterproof                   防水
    #       PTT.CallStatus.Friend                       朋友
    #       PTT.CallStatus.Off                          關掉

    # getCallStatus() 參數說明
    #
    #   回傳: 呼叫器狀態
    #       PTT.CallStatus.On                           打開
    #       PTT.CallStatus.Unplug                       拔掉
    #       PTT.CallStatus.Waterproof                   防水
    #       PTT.CallStatus.Friend                       朋友
    #       PTT.CallStatus.Off                          關掉

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

    CallStatus = PTTBot.getCallStatus()
    showCallStatus(CallStatus)

    TestQueue = [x for x in range(
        PTT.CallStatus.MinValue, PTT.CallStatus.MaxValue + 1
    )]
    random.shuffle(TestQueue)
    TestQueue.remove(CallStatus)

    PTTBot.setCallStatus(TestQueue[0])
    CallStatus = PTTBot.getCallStatus()
    showCallStatus(CallStatus)


def GiveMoney():

    # 給 P 幣範例

    # giveMoney() 參數說明
    #   ID:
    #       輸入你想要給錢的 ID
    #   Money:
    #       輸入你想要給多少錢

    PTTBot.giveMoney('CodingMan', 100)


def Mail():

    # 寄信範例

    # mail() 參數說明
    #   ID:
    #       輸入你想要寄信的 ID
    #   Title:
    #       標題
    #   Content:
    #       內文
    #   SignFile:
    #       簽名檔

    Content = '\r\n\r\n'.join(
        [
            '如有誤寄，對..對不起',
            'PTT Library 程式寄信測試內容',
            '程式碼: https://tinyurl.com/y2wuh8ck'
        ]
    )

    try:
        PTTBot.mail(
            ID,
            '程式寄信標題',
            Content,
            0
        )
    except PTT.Exceptions.NoSuchUser:
        print('No Such User')


def HasNewMail():

    # 是否有新信範例

    # hasNewMail() 無參數輸入
    #
    # 回傳值: 有幾封新信

    HowManyNewMail = PTTBot.hasNewMail()
    if HowManyNewMail > 0:
        print(f'You got {HowManyNewMail} mail(s)')
    else:
        print('No new mail')


def GetBoardList():
    BoardList = PTTBot.getBoardList()
    print(f'總共有 {len(BoardList)} 個板名')

if __name__ == '__main__':
    print('Welcome to PTT Library v ' + PTT.Version + ' Demo')

    ID, Password = getPW()

    # LoginLogout()
    # LogHandlerDemo()

    PTTBot = PTT.Library()
    try:
        PTTBot.login(ID, Password)
    except PTT.Exceptions.LoginError:
        PTTBot.log('登入失敗')
        sys.exit()
    PTTBot.log('登入成功')

    # GetTime()
    # GetPost()
    # Post_GetNewestIndex_Push()
    # CrawlBoard()
    # GetUser()
    # ThrowWaterBall()
    # GetWaterBall()
    # CallStatus()
    # GiveMoney()
    # Mail()
    HasNewMail()
    # GetBoardList()

    PTTBot.logout()
