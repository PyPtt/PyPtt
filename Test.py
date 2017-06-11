import sys
import time
import PTTTelnetCrawlerLibrary
import PTTTelnetCrawlerLibraryErrorCode
import os.path
try:
    sys.path.append("../IDPassword")
    import IDPassword

    ID = IDPassword.ID
    Password = IDPassword.Password
except ModuleNotFoundError:
    #Define your id password here
    ID = 'Your ID'
    Password = 'Your Password'

KickOtherLogin = False

BoardList = ['Wanted', 'Gossiping']
BoardList = ['Gossiping']
PostIDList = ['1PC1YXYj', '1PCBfel1', '1D89C0oV', 'QQQQQQQQ']

PTTCrawler = None

def gotoTopDemo():
    for i in range(5):
        ErrorCode = PTTCrawler.gotoTop()
        if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.Success:
            PTTCrawler.Log('gotoTop success')
        else:
            PTTCrawler.Log('gotoTop fail')
            
def GotoBoardDemo():
    for i in range(3):
        for Board in BoardList:
            if PTTCrawler.gotoBoard(Board) == PTTTelnetCrawlerLibraryErrorCode.Success:
                PTTCrawler.Log('Go to ' + Board + ' success')
            else:
                PTTCrawler.Log('Go to ' + Board + ' fail')
                break

def PostDemo():
    #發文類別       1
    #簽名檔        	0
    for i in range(5):
        
        #ErrorCode = PTTCrawler.post('Test', '連續自動PO文測試 ' + str(i), '自動PO文測試\r\n\r\n使用PTT Telnet Crawler Library 測試\r\n\r\nhttps://goo.gl/qlDRCt', 1, 0)
        ErrorCode = PTTCrawler.post('Test', '連續自動PO文測試 ' + str(i), '自動PO文測試\r\n\r\n(羞', 1, 0)
        if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.Success:
            PTTCrawler.Log('Post in Test success')
        else:
            PTTCrawler.Log('Post in Test fail')                

def GetNewestPostIndexDemo():

    for i in range(3):
        for Board in BoardList:
            ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex(Board)
            if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.Success:
                PTTCrawler.Log(str(i) + ' Get ' + Board + ' get newest post index success: ' + str(NewestIndex))
            else:
                PTTCrawler.Log(str(i) + ' Get ' + Board + ' get newest post index fail')
                return False
            #time.sleep(1)
def GotoPostDemo():

    ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex('Gossiping')
    TryPost = 5
    if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
        PTTCrawler.Log('Get newest post index fail')
        return False
    for i in range(TryPost):
        ErrorCode = PTTCrawler.gotoPostByIndex('Gossiping', NewestIndex - i)
        
        if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.Success:
            PTTCrawler.Log(str(i) + ' Go to Gossiping post index: ' + str(NewestIndex - i) + ' success')
        else:
            PTTCrawler.Log(str(i) + ' Go to Gossiping post index: ' + str(NewestIndex - i) + ' fail')
            return False
    
    for i in PostIDList:
        ErrorCode = PTTCrawler.gotoPostByID('Wanted', i)
        
        if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.Success:
            PTTCrawler.Log(str(i) + ' Go to Wanted post id: ' + i + ' success')
        else:
            PTTCrawler.Log(str(i) + ' Go to Wanted post id: ' + i + ' fail')
            return False
def GetPostInfoDemo():

    ErrorCode, NewestIndex = PTTCrawler.getNewestPostIndex('Gossiping')
    if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
        PTTCrawler.Log('Get newest post index fail')
        return False
    TryPost = 1000
    if NewestIndex == -1:
        PTTCrawler.Log('Get newest post index fail')
        return False
        
    for i in range(TryPost):
        
        ErrorCode, Post = PTTCrawler.getPostInfoByIndex('Gossiping', NewestIndex - i)
        if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.PostDeleted:
            PTTCrawler.Log('Post has been deleted')
            continue
        if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.WebFormatError:
            PTTCrawler.Log('Web structure error')
            continue
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            PTTCrawler.Log('Get post by index fail')
            return False
        PTTCrawler.Log(str(int(((i + 1) * 100) / TryPost)) + ' % ' + str(NewestIndex - i) + ' Title: ' + Post.getTitle())
        ErrorCode, Post = PTTCrawler.getPostInfoByID('Gossiping', Post.getPostID())
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            PTTCrawler.Log('Get post by ID fail error code: ' + str(ErrorCode))
            return False
        PTTCrawler.Log(str(int(((i + 1) * 100) / TryPost)) + ' % ' + Post.getPostID() + ' Title: ' + Post.getTitle())
        
def GetNewestIndexDemo():
    for i in range(3):        
        NewestIndex = PTTCrawler.getNewestPostIndex('Wanted')
        PTTCrawler.Log('Wanted newest index: ' + str(NewestIndex))
def GetPostInformationByIndexDemo():
    NewestIndex = PTTCrawler.getNewestPostIndex('Wanted')
    TryPost = 3
    if NewestIndex == -1:
        PTTCrawler.Log('Wanted get newest index fail')
        return None
    PTTCrawler.Log('Wanted newest index: ' + str(NewestIndex))    
    for i in range(TryPost):
        Post = PTTCrawler.getPostInformationByIndex('Wanted', NewestIndex - i)
        if not Post == None:
            PTTCrawler.Log(str(i) + ' Title: ' + Post.getTitle())
        else:
            PTTCrawler.Log('getPostInformationByIndex fail: ' + str(NewestIndex - i))
            #Do not return
def GetNewPostIndexDemo():
    NewestIndex = PTTCrawler.getNewestPostIndex('Wanted')
    LastIndex = NewestIndex - 5
    for i in range(3):
        #Return new post list LastIndex ~ newest without LastIndex
        LastIndexList = PTTCrawler.getNewPostIndex('Wanted', LastIndex)
        if not len(LastIndexList) == 0:
            for NewPostIndex in LastIndexList:
                PTTCrawler.Log('Detected new post: ' + str(NewPostIndex))
            LastIndex = LastIndexList.pop()
def PushDemo():
    for i in range(3):
        NewestPostIndex = PTTCrawler.getNewestPostIndex('Test')
        if PTTCrawler.pushByIndex('Test', NewestPostIndex, PTTCrawler.PushType_Push, 'https://goo.gl/qlDRCt by post index'):
            PTTCrawler.Log('pushByIndex Push success')
        else:
            PTTCrawler.Log('pushByIndex Push fail')
            
    for i in range(3):
        NewPost = PTTCrawler.getPostInformationByIndex('Test', NewestPostIndex)
        
        if NewPost == None:
            PTTCrawler.Log('getPostInformationByIndex fail')
            break
        if PTTCrawler.pushByID('Test', NewPost.getPostID(), PTTCrawler.PushType_Push, 'https://goo.gl/qlDRCt by post id'):
            PTTCrawler.Log('pushByID Push success')
        else:
            PTTCrawler.Log('pushByID Push fail')
def MainDemo():
    #0 不加簽名檔
    for i in range(3):
        if PTTCrawler.mail(ID, '自動寄信測試標題', '自動測試 如有誤寄打擾 抱歉QQ', 0):
            PTTCrawler.Log('Mail to ' + ID + ' success')
        else:
            PTTCrawler.Log('Mail to ' + ID + ' fail')
def GiveMoneyDemo():

    WhoAreUwantToGiveMoney = 'CodingMan'
    
    for i in range(3):
        if PTTCrawler.giveMoney(WhoAreUwantToGiveMoney, 10, Password):
            PTTCrawler.Log('Give money to ' + WhoAreUwantToGiveMoney + ' success')
        else:
            PTTCrawler.Log('Give money to ' + WhoAreUwantToGiveMoney + ' fail')
def GetPostFloorByIndex():
    
    NewestIndex = PTTCrawler.getNewestPostIndex('Wanted')
    for PostIndex in range(NewestIndex - 5, NewestIndex):
        Floor = PTTCrawler.getPostFloorByIndex('Wanted', PostIndex)
        if Floor == -1:
            PTTCrawler.Log('Get post index ' + str(PostIndex) + ' floor fail')
        else:
            PTTCrawler.Log('Get post index ' + str(PostIndex) + ' has ' + str(Floor) + ' floor')

def GetTimeDemo():

    for i in range(5):
        Time = PTTCrawler.getTime()
        PTTCrawler.Log('Ptt time: ' + Time)
        time.sleep(1)
            
if __name__ == '__main__':
    print('Welcome to PTT Telnet Crawler Library Demo')

    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, Password, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
        PTTCrawler.Log('Login fail')
        sys.exit()
    
    gotoTopDemo()
    GotoBoardDemo()
    GetNewestPostIndexDemo()
    #PostDemo()
    #PushDemo()
    GotoPostDemo()
    GetPostInfoDemo()
    #GetNewPostIndexDemo()
    #MainDemo()
    #GiveMoneyDemo()
    #GetPostFloorByIndex()
    #GetTimeDemo()
    
    PTTCrawler.logout()
    
    