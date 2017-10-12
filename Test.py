import sys
import time
import PTT
import json
import getpass

# 如果你想要自動登入，建立 Account.txt
# 然後裡面填上 {"ID":"YourID", "Password":"YourPW"}

try:
    with open('Account.txt') as AccountFile:
        Account = json.load(AccountFile)
        ID = Account['ID']
        Password = Account['Password']
except FileNotFoundError:
    ID = input('Input ID: ')
    Password = getpass.getpass('Input password: ')
BoardList = ['Wanted', 'Gossiping', 'Test', 'NBA', 'Baseball', 'LOL', 'C_Chat']
PostIDList = ['1PC1YXYj', '1PCBfel1', '1D89C0oV']

PTTCrawler = None

def PostDemo():

    JapanText = "水馬赤いな。ア、イ、ウ、エ、オ。\r\n\
浮藻に子蝦もおよいでる。 \r\n\
\r\n\
柿の木、栗の木。カ、キ、ク、ケ、コ。 \r\n\
啄木鳥こつこつ、枯れけやき。 \r\n\
\r\n\
大角豆に醋をかけ、サ、シ、ス、セ、ソ。 \r\n\
その魚浅瀬で刺しました。 \r\n\
\r\n\
立ちましょ、喇叭で、タ、チ、ツ、テ、ト。 \r\n\
トテトテタッタと飛び立った。 \r\n\
\r\n\
蛞蝓のろのろ、ナ、ニ、ヌ、ネ、ノ。 \r\n\
納戸にぬめって、なにねばる。 \r\n\
\r\n\
鳩ぽっぽ、ほろほろ。ハ、ヒ、フ、ヘ、ホ。 \r\n\
日向のお部屋にや笛を吹く。 \r\n\
\r\n\
蝸牛、螺旋巻、マ、ミ、ム、メ、モ。 \r\n\
梅の実落ちても見もしまい。 \r\n\
\r\n\
焼栗、ゆで栗。ヤ、イ、ユ、エ、ヨ。 \r\n\
山田に灯のつく宵の家。 \r\n\
\r\n\
雷鳥は寒かろ、ラ、リ、ル、レ、ロ。 \r\n\
蓮花が咲いたら、瑠璃の鳥。 \r\n\
\r\n\
わい、わい、わっしょい。ワ、ヰ、ウ、ヱ、ヲ。 \r\n\
植木屋、井戸換へ、お祭りだ。"

    #這個範例是如何PO文
    #第一個參數是你要PO文的板
    #第二個參數是文章標題
    #第三個參數是文章內文
    #第四個參數是發文類別       1
    #第五個參數是簽名檔        	0
    
    #回傳值 就是錯誤碼

    for i in range(1):
        
        ErrorCode = PTTCrawler.post('Test', '自動PO文測試', '\r\n標準測試流程，如有打擾請告知。\r\n\r\n使用PTT Crawler Library 測試\r\n\r\nhttps://goo.gl/5hdAqu', 1, 0)
        if ErrorCode == PTTCrawler.Success:
            PTTCrawler.Log('在 Test 板發文成功')
        elif ErrorCode == PTTCrawler.NoPermission:
            PTTCrawler.Log('發文權限不足')
        else:
            PTTCrawler.Log('在 Test 板發文失敗')
        
        ErrorCode = PTTCrawler.post('Test', '日文支援測試', JapanText + '\r\n日文支援測試，如有打擾請告知。\r\n\r\n使用PTT Crawler Library 測試\r\n\r\nhttps://goo.gl/5hdAqu', 1, 0)
        if ErrorCode == PTTCrawler.Success:
            PTTCrawler.Log('在 Test 板發文成功')
        elif ErrorCode == PTTCrawler.NoPermission:
            PTTCrawler.Log('發文權限不足')
        else:
            PTTCrawler.Log('在 Test 板發文失敗')


def GetNewestPostIndexDemo():

    #這個範例是如何取得某版的最新文章編號
    #第一個參數是板面
    
    #回傳值 就是錯誤碼跟最新文章編號
    for i in range(2):
        for Board in BoardList:
            ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex(Board)
            if ErrorCode == PTTCrawler.Success:
                PTTCrawler.Log('取得 ' + Board + ' 板最新文章編號成功: ' + str(NewestIndex))
            else:
                PTTCrawler.Log('取得 ' + Board + ' 板最新文章編號失敗')
                return False
            #time.sleep(1)

def GetPostInfoDemo():
    
    #這個範例是如何取得單一文章資訊
    #getPostInfoByIndex
    #第一個參數是板面
    #第二個參數就是你想查詢的文章編號
    #如果你不幸的只有文章代碼 那就使用 getPostInfoByID
    #getPostInfoByID
    #第一個參數是板面
    #第二個參數就是你想查詢的文章代碼
    
    #回傳值 就是錯誤碼跟文章資訊
    
    #文章資訊的資料結構可參考如下
    
    ################## 文章資訊 Post information ##################
    # getPostBoard              文章所在版面
    # getPostID                 文章 ID ex: 1PCBfel1
    # getPostAuthor             作者
    # getPostDate               文章發布時間
    # getTitle                  文章標題
    # getPostContent            文章內文
    # getMoney                  文章P幣
    # getWebUrl                 文章網址
    # getPushList               文章推文清單 備註: 推文是從網頁解析，極有可能不即時
    # getOriginalData           文章網頁原始資料 (開發用)
    
    ################## 推文資訊 Push information ##################
    # getPushType               推文類別 推噓箭頭?
    # getPushID                 推文ID
    # getPushContent            推文內文
    # getPushTime               推文時間
    
    ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex('Wanted')
    if ErrorCode != PTTCrawler.Success:
        PTTCrawler.Log('取得最新文章編號失敗')
        return False
    TryPost = 3
    if NewestIndex == -1:
        PTTCrawler.Log('取得最新文章編號失敗')
        return False

    for i in range(TryPost)[::-1]:
        
        ErrorCode, Post = PTTCrawler.getPostInfoByIndex('Wanted', NewestIndex - i)
        if ErrorCode == PTTCrawler.PostDeleted:
            PTTCrawler.Log('文章已經被刪除')
            continue
        if ErrorCode == PTTCrawler.WebFormatError:
            PTTCrawler.Log('網頁結構錯誤')
            continue
        if ErrorCode != PTTCrawler.Success:
            PTTCrawler.Log('使用文章編號取得文章詳細資訊失敗: ' + str(ErrorCode))
            return False
        PTTCrawler.Log(str(int(((i) * 2 * 100) / (TryPost * 2))) + ' % ')

        PTTCrawler.Log('文章代碼: ' + Post.getPostID())
        PTTCrawler.Log('作者: ' + Post.getPostAuthor())
        PTTCrawler.Log('時間: ' + Post.getPostDate())
        PTTCrawler.Log('標題: ' + Post.getTitle())
        PTTCrawler.Log('價錢: ' + str(Post.getMoney()))
        PTTCrawler.Log('網址: ' + Post.getWebUrl())
        PTTCrawler.Log('內文: \r\n' + Post.getPostContent())

        for Push in Post.getPushList():
            if Push.getPushType() == PTTCrawler.PushType_Push:
                PushTypeString = '推'
            elif Push.getPushType() == PTTCrawler.PushType_Boo:
                PushTypeString = '噓'
            elif Push.getPushType() == PTTCrawler.PushType_Arrow:
                PushTypeString = '→'
                
            PTTCrawler.Log(PushTypeString + ' ' + Push.getPushID() + ' ' + Push.getPushContent() + ' ' + Push.getPushTime())
        
        ErrorCode, Post = PTTCrawler.getPostInfoByID('Wanted', Post.getPostID())
        if ErrorCode != PTTCrawler.Success:
            PTTCrawler.Log('使用文章代碼取得文章詳細資訊失敗: ' + str(ErrorCode))
            return False
        PTTCrawler.Log(str(int(((i + 1) * 2 * 100) / (TryPost * 2))) + ' % ' + Post.getPostID() + ' 標題: ' + Post.getTitle())
        
        PTTCrawler.Log('-----------------------')
        
def GetNewPostIndexListDemo():

    #這個範例是如何取得某版的最新文章編號清單
    #跟上一次使用 getPostInfoByIndex 比較
    #第一個參數是板面
    #第二個參數就是你上一次查詢的最新文章編號 代入 0 就會等到有PO文才會有清單結果
    
    #詳細使用方式可以參考 範例程式中的 汪踢推文機器人
    
    #回傳值 就是錯誤碼跟最新文章編號清單

    ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex('Wanted')
    if ErrorCode != PTTCrawler.Success:
        return False
    
    LastIndex = NewestIndex - 5
    for i in range(3):
        #Return new post list LastIndex ~ newest without LastIndex
        ErrorCode, LastIndexList = PTTCrawler.getNewPostIndexList('Wanted', LastIndex)
        if ErrorCode != PTTCrawler.Success:
            return False
        if not len(LastIndexList) == 0:
            for NewPostIndex in LastIndexList:
                PTTCrawler.Log('偵測到新文章編號 ' + str(NewPostIndex))
            LastIndex = LastIndexList.pop()
def PushDemo():
    ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex('Test')
    if ErrorCode != PTTCrawler.Success:
        PTTCrawler.Log('取得最新文章編號失敗: ' + str(ErrorCode))
        return False
    PTTCrawler.Log('NewestIndex: ' + str(NewestIndex))
    for i in range(10):
        ErrorCode = PTTCrawler.pushByIndex('Test', PTTCrawler.PushType_Push, 'https://goo.gl/5hdAqu type 1', NewestIndex)
        if ErrorCode == PTTCrawler.Success:
            PTTCrawler.Log('使用文章編號: 推文成功')
        elif ErrorCode == PTTCrawler.ErrorInput:
            PTTCrawler.Log('使用文章編號: 參數錯誤')
            return False
        elif ErrorCode == PTTCrawler.NoPermission:
            PTTCrawler.Log('使用文章編號: 無發文權限')
            return False
        else:
            PTTCrawler.Log('使用文章編號: 推文失敗')
            return False
            
    ErrorCode, NewPost = PTTCrawler.getPostInfoByIndex('Test', NewestIndex)
    if ErrorCode != PTTCrawler.Success:
        PTTCrawler.Log('取得最新文章編號失敗: ' + str(ErrorCode))
        return False
    if NewPost == None:
        PTTCrawler.Log('取得最新文章編號失敗')
        return False
    for i in range(10):
        
        ErrorCode = PTTCrawler.pushByID('Test', PTTCrawler.PushType_Push, 'https://goo.gl/5hdAqu type 2', NewPost.getPostID())
        if ErrorCode == PTTCrawler.Success:
            PTTCrawler.Log('使用文章代碼: 推文成功')
        elif ErrorCode == PTTCrawler.ErrorInput:
            PTTCrawler.Log('使用文章代碼: 參數錯誤')
            return False
        elif ErrorCode == PTTCrawler.NoPermission:
            PTTCrawler.Log('使用文章代碼: 無發文權限')
            return False
        else:
            PTTCrawler.Log('使用文章代碼: 推文失敗')
            return False
def MainDemo():
    
    #這個範例是如何寄信給某鄉民

    #第一個參數是你想寄信的ID
    #第二個參數是信件標題
    #第三個參數是信件內容
    #第四個參數是簽名檔選擇 0 不加簽名檔
    
    for i in range(1):
        ErrorCode = PTTCrawler.mail(ID, '自動寄信測試標題', '自動測試 如有誤寄打擾 抱歉QQ', 0)
        if ErrorCode == PTTCrawler.Success:
            PTTCrawler.Log('寄信給 ' + ID + ' 成功')
        else:
            PTTCrawler.Log('寄信給 ' + ID + ' 失敗')
def GiveMoneyDemo():

    #這個範例是如何給P幣給某鄉民

    #第一個參數是你想寄信的ID
    #第二個參數是你想給予多少P幣
    #第三個參數是你自己的密碼
    
    WhoAreUwantToGiveMoney = 'CodingMan'
    Donate = input('請問願意贊助作者 10 P幣嗎？[Y/n] ').lower()
    
    if Donate == 'y' or Donate == '':
        ErrorCode = PTTCrawler.giveMoney(WhoAreUwantToGiveMoney, 10, Password)
        
        if ErrorCode == PTTCrawler.Success:
            PTTCrawler.Log('送P幣給 ' + WhoAreUwantToGiveMoney + ' 成功')
        else:
            PTTCrawler.Log('送P幣給 ' + WhoAreUwantToGiveMoney + ' 失敗')

def GetTimeDemo():

    #這個範例是取得PTT的時間，有時需要跟PTT對時的需求，比如說 準點報時
        
    for i in range(3):
        ErrorCode, Time = PTTCrawler.getTime()
        if ErrorCode != PTTCrawler.Success:
            PTTCrawler.Log('取得時間失敗')
            return False
        PTTCrawler.Log('Ptt time: ' + Time + '!')
        time.sleep(1)

def PostHandler(Post):
    
    #這是 crawlBoard 需要的 call back function
    #每當爬蟲取得新文章就會呼叫此函式一次
    #因此你可以在這自由地決定存檔的格式 或者任何你想做的分析
    
    #文章資料結構可參考如下
    ################## 文章資訊 Post information ##################
    # getPostBoard              文章所在版面
    # getPostID                 文章 ID ex: 1PCBfel1
    # getPostAuthor             作者
    # getPostDate               文章發布時間
    # getTitle                  文章標題
    # getPostContent            文章內文
    # getMoney                  文章P幣
    # getWebUrl                 文章網址
    # getPushList               文章推文清單 備註: 推文是從網頁解析，極有可能不即時
    # getOriginalData           文章網頁原始資料 (開發用)
    
    ################## 推文資訊 Push information ##################
    # getPushType               推文類別 推噓箭頭?
    # getPushID                 推文ID
    # getPushContent            推文內文
    # getPushTime               推文時間
    
    with open("CrawlBoardResult.txt", "a") as ResultFile:
        ResultFile.write(Post.getTitle() + '\n')
    
def CrawlBoardDemo():
    
    #範例是從編號 1 爬到 編號 100 的文章
    #如果想要取得所有文章可省略編號參數
    #PTTCrawler.crawlBoard('Wanted', PostHandler)
    #這樣就會全部文章都會爬下來
    
    ErrorCode = PTTCrawler.crawlBoard('Wanted', PostHandler, 1, 100)
    if ErrorCode == PTTCrawler.Success:
        PTTCrawler.Log('爬行成功')
        
def GetUserInfoDemo():
    
    #範例是追蹤 某些ID的情況
    #此API可以持續追蹤某ID的動態
    #詳細可以參考 範例程式中的 ID追蹤器
    
    #使用者資訊資料結構可參考如下
    
    ################## 使用者資訊 User information ##################
    # getID                     ID
    # getMoney                  使用者經濟狀況
    # getLoginTime              登入次數
    # getPost                   有效文章數
    # getState                  目前動態
    # getMail                   信箱狀態
    # getLastLogin              最後登入時間
    # getLastIP                 上次故鄉
    # getFiveChess              五子棋戰績
    # getChess                  象棋戰績
    
    for IDs in [ID, 'FakeID_____']:
        
        PTTCrawler.Log('---------------------------')
        PTTCrawler.Log('Start query: ' + IDs)
        ErrorCode, UserInfo = PTTCrawler.getUserInfo(IDs)
        if ErrorCode == PTTCrawler.NoUser:
            PTTCrawler.Log('No such user')
            continue
        if ErrorCode != PTTCrawler.Success:
            PTTCrawler.Log('getUserInfo fail error code: ' + str(ErrorCode))
            continue
        
        PTTCrawler.Log('使用者ID: ' + UserInfo.getID())
        PTTCrawler.Log('使用者經濟狀況: ' + str(UserInfo.getMoney()))
        PTTCrawler.Log('登入次數: ' + str(UserInfo.getLoginTime()))
        PTTCrawler.Log('有效文章數: ' + str(UserInfo.getPost()))
        PTTCrawler.Log('目前動態: ' + UserInfo.getState() + '!')
        PTTCrawler.Log('信箱狀態: ' + UserInfo.getMail() + '!')
        PTTCrawler.Log('最後登入時間: ' + UserInfo.getLastLogin() + '!')
        PTTCrawler.Log('上次故鄉: ' + UserInfo.getLastIP() + '!')
        PTTCrawler.Log('五子棋戰績: ' + UserInfo.getFiveChess() + '!')
        PTTCrawler.Log('象棋戰績: ' + UserInfo.getChess() + '!')

def ReplyPostDemo():
    
    ErrorCode = PTTCrawler.post('Test', '自動PO文測試', '標準測試流程，如有打擾請告知。\r\n\r\n使用PTT Crawler Library 測試\r\n\r\nhttps://goo.gl/5hdAqu', 1, 0)
    if ErrorCode == PTTCrawler.Success:
        PTTCrawler.Log('在 Test 板發文成功')
    elif ErrorCode == PTTCrawler.NoPermission:
        PTTCrawler.Log('發文權限不足')
    else:
        PTTCrawler.Log('在 Test 板發文失敗')
    
    ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex('Test')
    if ErrorCode == PTTCrawler.Success:
        PTTCrawler.Log('取得 ' + 'Test' + ' 板最新文章編號成功: ' + str(NewestIndex))
    else:
        PTTCrawler.Log('取得 ' + 'Test' + ' 板最新文章編號失敗')
        return False
    
    '''
    PTTCrawler.ReplyPost_Board =                1
    PTTCrawler.ReplyPost_Mail =                 2
    '''
    #def replyPost(self, Board, Content, ReplyType, PostID='', Index=-1, TelnetConnectIndex = 0):
    
    ErrorCode = PTTCrawler.replyPost('Test', '回文測試', PTTCrawler.ReplyPost_Board, Index=NewestIndex)
    if ErrorCode == PTTCrawler.Success:
        PTTCrawler.Log('在 Test 回文至板上成功!')
    else:
        PTTCrawler.Log('在 Test 回文至板上失敗 ' + str(ErrorCode))
    
    ErrorCode = PTTCrawler.replyPost('Test', '回文測試', PTTCrawler.ReplyPost_Mail, Index=NewestIndex)
    if ErrorCode == PTTCrawler.Success:
        PTTCrawler.Log('在 Test 回文至信箱成功!')
    else:
        PTTCrawler.Log('在 Test 回文至信箱失敗 ' + str(ErrorCode))
        
    ErrorCode = PTTCrawler.replyPost('Test', '回文測試', PTTCrawler.ReplyPost_Board + PTTCrawler.ReplyPost_Mail, Index=NewestIndex)
    if ErrorCode == PTTCrawler.Success:
        PTTCrawler.Log('在 Test 回文至版上與信箱成功!')
    else:
        PTTCrawler.Log('在 Test 回文至版上與信箱失敗 ' + str(ErrorCode))

    # Board = 'Wanted'
    # ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex(Board)
    # if ErrorCode == PTTCrawler.Success:
    #     PTTCrawler.Log('取得 ' + Board + ' 板最新文章編號成功: ' + str(NewestIndex))
    #     ErrorCode = PTTCrawler.replyPost(Board, '抱歉打擾了 需要在汪梯測試回文 對不起 QQ', PTTCrawler.ReplyPost_Mail, Index=NewestIndex)
    #     if ErrorCode == PTTCrawler.Success:
    #         PTTCrawler.Log('在 ' + Board + ' 回文至信箱成功!')
    #     else:
    #         PTTCrawler.Log('在 ' + Board + ' 回文至信箱失敗 ' + str(ErrorCode))
    # else:
    #     PTTCrawler.Log('取得 ' + Board + ' 板最新文章編號失敗')
if __name__ == '__main__':
    print('Welcome to PTT Crawler Library Demo')
    
    KickOtherLogin = True
    PTTCrawler = PTT.Crawler(ID, Password, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
        PTTCrawler.Log('登入失敗')
        sys.exit()
    # PTTCrawler.setLogLevel(PTTCrawler.LogLevel_DEBUG)
    
    GetNewestPostIndexDemo()
    PostDemo()
    PushDemo()
    GetPostInfoDemo()
    GetNewPostIndexListDemo()
    MainDemo()
    GetTimeDemo()
    GetUserInfoDemo()
    GiveMoneyDemo()
    CrawlBoardDemo()
    ReplyPostDemo()
    
    PTTCrawler.logout()
    
    
