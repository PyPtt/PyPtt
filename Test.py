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
        
        ErrorCode = PTTCrawler.post('Test', '自動PO文測試', '自動PO文測試\r\n\r\n使用PTT Crawler Library 測試\r\n\r\nhttps://goo.gl/5hdAqu', 1, 0)
        #ErrorCode = PTTCrawler.post('Test', '攻佔版面測試', '此版已經被攻陷 版眾束手就擒吧!!!\r\n\r\n使用PTT Crawler Library 測試\r\n\r\nhttps://goo.gl/5hdAqu', 1, 0)
        if ErrorCode == PTT.Success:
            PTTCrawler.Log('Post in Test success')
        else:
            PTTCrawler.Log('Post in Test fail')                

def GetNewestPostIndexDemo():

    for i in range(2):
        for Board in BoardList:
            ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex(Board)
            if ErrorCode == PTT.Success:
                PTTCrawler.Log(str(i) + ' Get ' + Board + ' get newest post index success: ' + str(NewestIndex))
            else:
                PTTCrawler.Log(str(i) + ' Get ' + Board + ' get newest post index fail')
                return False
            #time.sleep(1)

def GetPostInfoDemo():

    ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex('Gossiping')
    if ErrorCode != PTT.Success:
        PTTCrawler.Log('Get newest post index fail')
        return False
    TryPost = 3
    if NewestIndex == -1:
        PTTCrawler.Log('Get newest post index fail')
        return False
        
    for i in range(TryPost):
        
        ErrorCode, Post = PTTCrawler.getPostInfoByIndex('Gossiping', NewestIndex - i)
        if ErrorCode == PTT.PostDeleted:
            PTTCrawler.Log('Post has been deleted')
            continue
        if ErrorCode == PTT.WebFormatError:
            PTTCrawler.Log('Web structure error')
            continue
        if ErrorCode != PTT.Success:
            PTTCrawler.Log('Get post by index fail')
            return False
        PTTCrawler.Log(str(int(((i + 1) * 100) / TryPost)) + ' % ' + str(NewestIndex - i) + ' Title: ' + Post.getTitle())
        ErrorCode, Post = PTTCrawler.getPostInfoByID('Gossiping', Post.getPostID())
        if ErrorCode != PTT.Success:
            PTTCrawler.Log('Get post by ID fail error code: ' + str(ErrorCode))
            return False
        PTTCrawler.Log(str(int(((i + 1) * 100) / TryPost)) + ' % ' + Post.getPostID() + ' Title: ' + Post.getTitle())
        
def GetNewPostIndexListDemo():
    ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex('Wanted')
    if ErrorCode != PTT.Success:
        return False
    
    LastIndex = NewestIndex - 5
    for i in range(3):
        #Return new post list LastIndex ~ newest without LastIndex
        ErrorCode, LastIndexList = PTTCrawler.getNewPostIndexList('Wanted', LastIndex)
        if ErrorCode != PTT.Success:
            return False
        if not len(LastIndexList) == 0:
            for NewPostIndex in LastIndexList:
                PTTCrawler.Log('Detected new post: ' + str(NewPostIndex))
            LastIndex = LastIndexList.pop()
def PushDemo():
    ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex('Test')
    if ErrorCode != PTT.Success:
        PTTCrawler.Log('getNewestPostIndex ErrorCode: ' + str(ErrorCode))
        return False
    PTTCrawler.Log('NewestIndex: ' + str(NewestIndex))
    for i in range(10):
        ErrorCode = PTTCrawler.pushByIndex('Test', PTTCrawler.PushType_Push, 'https://goo.gl/5hdAqu type 1', NewestIndex)
        if ErrorCode == PTT.Success:
            PTTCrawler.Log('pushByIndex Push success')
        else:
            PTTCrawler.Log('pushByIndex Push fail')
    ErrorCode, NewPost = PTTCrawler.getPostInfoByIndex('Test', NewestIndex)
    if ErrorCode != PTT.Success:
        PTTCrawler.Log('getPostInfoByIndex ErrorCode: ' + str(ErrorCode))
        return False
    if NewPost == None:
        PTTCrawler.Log('getPostInfoByIndex fail')
        return False
    for i in range(10):
        
        ErrorCode = PTTCrawler.pushByID('Test', PTTCrawler.PushType_Push, 'https://goo.gl/5hdAqu type 2', NewPost.getPostID())
        if ErrorCode == PTT.Success:
            PTTCrawler.Log('pushByID Push success')
        else:
            PTTCrawler.Log('pushByID Push fail')
def MainDemo():
    #0 不加簽名檔
    for i in range(1):
        ErrorCode = PTTCrawler.mail(ID, '自動寄信測試標題', '自動測試 如有誤寄打擾 抱歉QQ', 0)
        if ErrorCode == PTT.Success:
            PTTCrawler.Log('Mail to ' + ID + ' success')
        else:
            PTTCrawler.Log('Mail to ' + ID + ' fail')
def GiveMoneyDemo():

    WhoAreUwantToGiveMoney = 'CodingMan'
    
    for i in range(3):
        ErrorCode = PTTCrawler.giveMoney(WhoAreUwantToGiveMoney, 2, Password)
        
        if ErrorCode == PTT.Success:
            PTTCrawler.Log('Give money to ' + WhoAreUwantToGiveMoney + ' success')
        else:
            PTTCrawler.Log('Give money to ' + WhoAreUwantToGiveMoney + ' fail')

def GetTimeDemo():

    for i in range(3):
        ErrorCode, Time = PTTCrawler.getTime()
        if ErrorCode != PTT.Success:
            PTTCrawler.Log('Get time error')
            return False
        PTTCrawler.Log('Ptt time: ' + Time + '!')
        time.sleep(1)
def GetUserInfoDemo():
    
    for IDs in [ID, 'FakeID_____']:
        
        PTTCrawler.Log('---------------------------')
        PTTCrawler.Log('Start query: ' + IDs)
        ErrorCode, UserInfo = PTTCrawler.getUserInfo(IDs)
        if ErrorCode == PTT.NoUser:
            PTTCrawler.Log('No such user')
            continue
        if ErrorCode != PTT.Success:
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
    
if __name__ == '__main__':
    print('Welcome to PTT Crawler Library Demo')
    
    KickOtherLogin = False
    PTTCrawler = PTT.Crawler(ID, Password, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
        PTTCrawler.Log('Login fail')
        sys.exit()
    PTTCrawler.setLogLevel(PTT.LogLevel_DEBUG)
    
    GetNewestPostIndexDemo()
    PostDemo()
    PushDemo()
    GetPostInfoDemo()
    GetNewPostIndexListDemo()
    #MainDemo()
    #GiveMoneyDemo()
    GetTimeDemo()
    GetUserInfoDemo()
    PTTCrawler.logout()
    
    