import sys
import time
import PTT
import json
import getpass

# If you want to automatically login define Account.txt
# {"ID":"YourID", "Password":"YourPW"}
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
    #發文類別       1
    #簽名檔        	0
    for i in range(1):
        
        ErrorCode = PTTCrawler.post('Test', '自動PO文測試', '標準測試流程，如有打擾請告知。\r\n\r\n使用PTT Crawler Library 測試\r\n\r\nhttps://goo.gl/5hdAqu', 1, 0)
        if ErrorCode == PTTCrawler.Success:
            PTTCrawler.Log('Post in Test success')
        elif ErrorCode == PTTCrawler.NoPermission:
            PTTCrawler.Log('發文權限不足')
        else:
            PTTCrawler.Log('Post in Test fail') 

def GetNewestPostIndexDemo():

    for i in range(2):
        for Board in BoardList:
            ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex(Board)
            if ErrorCode == PTTCrawler.Success:
                PTTCrawler.Log(str(i) + ' Get ' + Board + ' get newest post index success: ' + str(NewestIndex))
            else:
                PTTCrawler.Log(str(i) + ' Get ' + Board + ' get newest post index fail')
                return False
            #time.sleep(1)

def GetPostInfoDemo():

    ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex('Wanted')
    if ErrorCode != PTTCrawler.Success:
        PTTCrawler.Log('Get newest post index fail')
        return False
    TryPost = 3
    if NewestIndex == -1:
        PTTCrawler.Log('Get newest post index fail')
        return False

    for i in range(TryPost):
        
        ErrorCode, Post = PTTCrawler.getPostInfoByIndex('Wanted', NewestIndex - i)
        if ErrorCode == PTTCrawler.PostDeleted:
            PTTCrawler.Log('Post has been deleted')
            continue
        if ErrorCode == PTTCrawler.WebFormatError:
            PTTCrawler.Log('Web structure error')
            continue
        if ErrorCode != PTTCrawler.Success:
            PTTCrawler.Log('Get post by index fail')
            return False
        PTTCrawler.Log(str(int(((i) * 2 * 100) / (TryPost * 2))) + ' % ' + str(NewestIndex - i) + ' Title: ' + Post.getTitle())

        PTTCrawler.Log('Content: \r\n' + Post.getPostContent())

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
            PTTCrawler.Log('Get post by ID fail error code: ' + str(ErrorCode))
            return False
        PTTCrawler.Log(str(int(((i + 1) * 2 * 100) / (TryPost * 2))) + ' % ' + Post.getPostID() + ' Title: ' + Post.getTitle())
        
        PTTCrawler.Log('-----------------------')
        ################## 文章資訊 Post information ##################
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
        
        
def GetNewPostIndexListDemo():
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
                PTTCrawler.Log('Detected new post: ' + str(NewPostIndex))
            LastIndex = LastIndexList.pop()
def PushDemo():
    ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex('Test')
    if ErrorCode != PTTCrawler.Success:
        PTTCrawler.Log('getNewestPostIndex ErrorCode: ' + str(ErrorCode))
        return False
    PTTCrawler.Log('NewestIndex: ' + str(NewestIndex))
    for i in range(10):
        ErrorCode = PTTCrawler.pushByIndex('Test', PTTCrawler.PushType_Push, 'https://goo.gl/5hdAqu type 1', NewestIndex)
        if ErrorCode == PTTCrawler.Success:
            PTTCrawler.Log('pushByIndex Push success')
        elif ErrorCode == PTTCrawler.ErrorInput:
            PTTCrawler.Log('pushByIndex wrong input')
            return False
        elif ErrorCode == PTTCrawler.NoPermission:
            PTTCrawler.Log('pushByIndex 無發文權限')
            return False
        else:
            PTTCrawler.Log('pushByIndex Push fail')
            return False
            
    ErrorCode, NewPost = PTTCrawler.getPostInfoByIndex('Test', NewestIndex)
    if ErrorCode != PTTCrawler.Success:
        PTTCrawler.Log('getPostInfoByIndex ErrorCode: ' + str(ErrorCode))
        return False
    if NewPost == None:
        PTTCrawler.Log('getPostInfoByIndex fail')
        return False
    for i in range(10):
        
        ErrorCode = PTTCrawler.pushByID('Test', PTTCrawler.PushType_Push, 'https://goo.gl/5hdAqu type 2', NewPost.getPostID())
        if ErrorCode == PTTCrawler.Success:
            PTTCrawler.Log('pushByID Push success')
        elif ErrorCode == PTTCrawler.ErrorInput:
            PTTCrawler.Log('pushByID wrong input')
            return False
        elif ErrorCode == PTTCrawler.NoPermission:
            PTTCrawler.Log('pushByID 無發文權限')
            return False
        else:
            PTTCrawler.Log('pushByID Push fail')
            return False
def MainDemo():
    #0 不加簽名檔
    for i in range(1):
        ErrorCode = PTTCrawler.mail(ID, '自動寄信測試標題', '自動測試 如有誤寄打擾 抱歉QQ', 0)
        if ErrorCode == PTTCrawler.Success:
            PTTCrawler.Log('Mail to ' + ID + ' success')
        else:
            PTTCrawler.Log('Mail to ' + ID + ' fail')
def GiveMoneyDemo():

    WhoAreUwantToGiveMoney = 'CodingMan'
    Donate = input('請問願意贊助作者 10 P幣嗎？[Y/n] ').lower()
    
    if Donate == 'y' or Donate == '':
        ErrorCode = PTTCrawler.giveMoney(WhoAreUwantToGiveMoney, 10, Password)
        
        if ErrorCode == PTTCrawler.Success:
            PTTCrawler.Log('Give money to ' + WhoAreUwantToGiveMoney + ' success')
        else:
            PTTCrawler.Log('Give money to ' + WhoAreUwantToGiveMoney + ' fail')

def GetTimeDemo():

    for i in range(3):
        ErrorCode, Time = PTTCrawler.getTime()
        if ErrorCode != PTTCrawler.Success:
            PTTCrawler.Log('Get time error')
            return False
        PTTCrawler.Log('Ptt time: ' + Time + '!')
        time.sleep(1)
def GetUserInfoDemo():
    
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
        
        PTTCrawler.Log('UserID: ' + UserInfo.getID())
        PTTCrawler.Log('UserMoney: ' + str(UserInfo.getMoney()))
        PTTCrawler.Log('UserLoginTime: ' + str(UserInfo.getLoginTime()))
        PTTCrawler.Log('UserPost: ' + str(UserInfo.getPost()))
        PTTCrawler.Log('UserState: ' + UserInfo.getState() + '!')
        PTTCrawler.Log('UserMail: ' + UserInfo.getMail() + '!')
        PTTCrawler.Log('UserLastLogin: ' + UserInfo.getLastLogin() + '!')
        PTTCrawler.Log('UserLastIP: ' + UserInfo.getLastIP() + '!')
        PTTCrawler.Log('UserFiveChess: ' + UserInfo.getFiveChess() + '!')
        PTTCrawler.Log('UserChess: ' + UserInfo.getChess() + '!')
        
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
        
         
if __name__ == '__main__':
    print('Welcome to PTT Crawler Library Demo')
    
    KickOtherLogin = False
    PTTCrawler = PTT.Crawler(ID, Password, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
        PTTCrawler.Log('Login fail')
        sys.exit()
    #PTTCrawler.setLogLevel(PTTCrawler.LogLevel_DEBUG)
    
    GetNewestPostIndexDemo()
    PostDemo()
    PushDemo()
    GetPostInfoDemo()
    GetNewPostIndexListDemo()
    MainDemo()
    GetTimeDemo()
    GetUserInfoDemo()
    GiveMoneyDemo()
    PTTCrawler.logout()
    
    
