import sys
import time
import json
import getpass
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


def LoginLogout():
    # 登入登出範例

    # Library 參數
    #   LogLevel (Optional):
    #       PTT.LogLevel.DEBUG
    #       PTT.LogLevel.INFO (預設值)
    #       PTT.LogLevel.SLIENT
    #   Language (Optional):
    #       PTT.Language.Chinese (預設值)
    #       PTT.Language.English

    # login 參數
    #   ID:
    #       你的 PTT 帳號
    #   Password:
    #       你的 PTT 密碼
    #   KickOtherLogin (Optional):
    #       是否剔除其他登入。
    #       預設值為 False

    # logout 無參數輸入

    PTTBot = PTT.Library()
    try:
        PTTBot.login(ID, Password)
    except PTT.Exceptions.LoginError:
        PTTBot.log('登入失敗')
        return
    PTTBot.log('登入成功')
    PTTBot.logout()


def GetTime():

    # 取得 PTT 時間範例

    PTT_TIME = PTTBot.getTime()
    print(PTT_TIME)


def GetPost():

    # 取得特定文章範例

    # 參數說明
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
        'Gossiping',
        PostIndex=301676
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
            if Push.getType() == PTT.PushType.Push:
                PushCount += 1
            if Push.getType() == PTT.PushType.Boo:
                BooCount += 1
            if Push.getType() == PTT.PushType.Arrow:
                ArrowCount += 1

        print(f'Total {PushCount} Pushs {BooCount} Boo {ArrowCount} Arrow')


def Post():
    # 貼文範例

    # 參數說明
    #   Board:
    #       文章版
    #   Title:
    #       標題
    #   Content:
    #       文章內文
    #   PostType:
    #       貼文類型，每個板都會有幾個文章標題讓你選，
    #       你可以選擇你要用哪一個
    #   SignType:
    #       選擇用哪一個簽名檔

    Content = '\r\n\r\n'.join(
        [
            'PTT Library 貼文測試，如有打擾請告知。',
            '程式碼: https://tinyurl.com/y2wuh8ck'
        ]
    )

    PTTBot.post(
        'Test',
        'PTT Library 程式貼文測試',
        Content,
        1,
        0
    )


def GetNewestIndex():
    # 取得某版最新文章編號範例

    # 參數說明
    #   IndexType:
    #       可以取得兩種不一樣的最新編號，
    #       某版的最新文章編號
    #       信箱的最新信件編號 (尚未啟用)
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

    Board = 'Gossiping'

    Index = PTTBot.getNewestIndex(PTT.IndexType.Board, Board=Board)
    print(f'{Board} 最新文章編號 {Index}')


def CrawlBoard():
    # 大量爬文範例

    # 參數說明
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

    TestBoard = 'Gossiping'
    TestRange = 100

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
        print('Del Post: \n' + '\n'.join(str(x) for x in DelPostList))
        print(f'共有 {len(DelPostList)} 篇文章被刪除')

if __name__ == '__main__':
    print('Welcome to PTT Library v ' + PTT.Version + ' Demo')

    ID, Password = getPW()

    # LoginLogout()

    PTTBot = PTT.Library()
    try:
        PTTBot.login(ID, Password)
    except PTT.Exceptions.LoginError:
        PTTBot.log('登入失敗')
        sys.exit()
    PTTBot.log('登入成功')

    # GetTime()
    # GetPost()
    # Post()
    # GetNewestIndex()
    CrawlBoard()

    PTTBot.logout()
