import sys
import time
import PTTTelnetCrawlerLibrary

def GoToBoard(ID, PW, KickOtherLogin, Board):
    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, PW, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
        return False
    if PTTCrawler.gotoBoard(Board):
        print("Go to " + Board + " success")
    else:
        print("Go to " + Board + " fail")
    
    if PTTCrawler.gotoBoard(Board):
        print("Go to " + Board + " success")
    else:
        print("Go to " + Board + " fail")
    
    if PTTCrawler.gotoBoard(Board):
        print("Go to " + Board + " success")
    else:
        print("Go to " + Board + " fail")
    PTTCrawler.logout()

def Post(ID, PW, KickOtherLogin, Board, Title, Content, PostType, SignType):
    
    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, PW, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
        return False
    PTTCrawler.post(Board, Title + " 1", Content, PostType, SignType)
    PTTCrawler.post(Board, Title + " 2", Content, PostType, SignType)
    PTTCrawler.post(Board, Title + " 3", Content, PostType, SignType)
    PTTCrawler.logout()
    return True
def GetPostInformationByID(ID, PW, KickOtherLogin, Board, PostID):

    result = False
    
    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, PW, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
        return False
    
    Post = PTTCrawler.getPostInformationByID(Board, PostID)
    result = not Post == None
    PTTCrawler.logout()
    return result

def GetPostInformationByIndex(ID, PW, KickOtherLogin, Board, PostIndex):
    result = False
    
    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, PW, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
        return False
    
    Post = PTTCrawler.getPostInformationByIndex(Board, PostIndex)
    result = not Post == None
    PTTCrawler.logout()
    return result
    
def GetNewestPostIndex(ID, PW, KickOtherLogin, Board):

    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, PW, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
        return False
    
    index = PTTCrawler.getNewestPostIndex(Board)
    if index == -1:
        print("Fail")
        return False
    print("Index: " + str(index))
    
    index = PTTCrawler.getNewestPostIndex(Board)
    if index == -1:
        print("Fail")
        return False
    print("Index: " + str(index))
    
    index = PTTCrawler.getNewestPostIndex(Board)
    if index == -1:
        print("Fail")
        return False
    print("Index: " + str(index))
    PTTCrawler.logout()
    return True

def GetNewPostIndex(ID, PW, KickOtherLogin, Board):
    result = False
    
    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, PW, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
        return False
    
    LastIndex = 0
    LastIndexList = [0]
    for i in range(30):    
        try:
            if not len(LastIndexList) == 0:
                LastIndex = LastIndexList.pop()
            
            LastIndexList = PTTCrawler.getNewPostIndex(Board, LastIndex)
            
            if not len(LastIndexList) == 0:
                for NewPostIndex in LastIndexList:
                    print("Detected new post: " + str(NewPostIndex))
            time.sleep(2)
        except KeyboardInterrupt:
            break;
    PTTCrawler.logout()
    result = True
    return result

def Push(ID, PW, KickOtherLogin, Board, PushType, PushContent):
    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, PW, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
        return False
    
    NewestPostIndex = 0
    
    for i in range(3):
        NewestPostIndex = PTTCrawler.getNewestPostIndex(Board)
        if PTTCrawler.pushByIndex(Board, NewestPostIndex, PTTCrawler.PushType_Push, PushContent + " by post index"):
            print("pushByIndex Push success")
        else:
            print("pushByIndex Push fail")
            
    for i in range(3):
        NewPost = PTTCrawler.getPostInformationByIndex(Board, NewestPostIndex)
        
        if NewPost == None:
            print("getPostInformationByIndex fail")
            break
        
        if PTTCrawler.pushByID(Board, NewPost.getPostID(), PTTCrawler.PushType_Push, PushContent + " by post id"):
            print("pushByID Push success")
        else:
            print("pushByID Push fail")
    PTTCrawler.logout()
    return True

def Mail(ID, PW, KickOtherLogin, MailTitle, MailContent, SignType):
    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, PW, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
            return False
    
    for i in range(2):
        if PTTCrawler.mail(ID, MailTitle, MailContent, SignType):
            print("Mail to " + ID + " success")
        else:
            print("Mail to " + ID + " fail")
    
    PTTCrawler.logout()
if __name__ == "__main__":
    print("Welcome to PTT Telnet Crawler Library Demo")

    ID = 'CodingMan'
    Password = '04260426'
    KickOtherLogin = False

    #發文類別           1
    #簽名檔        	0
    #GoToBoard(ID, Password, KickOtherLogin, 'Test')
    #Post(ID, Password, KickOtherLogin, 'Test','連續自動PO文測試', '自動PO文測試 啾咪', 1, 0)
    #GetPostInformationByID(ID, Password, KickOtherLogin, 'GO', "1PAIyWdT")
    #GetPostInformationByIndex(ID, Password, KickOtherLogin, 'Wanted', 68935)
    #GetNewestPostIndex(ID, Password, KickOtherLogin, 'Wanted')
    #GetNewPostIndex(ID, Password, KickOtherLogin, 'Wanted')
    """
    Push =         1
    Boo =          2
    Arrow =        3
    """
    #Push(ID, Password, KickOtherLogin, "Test", 1, "偵測最新文章推文測試")
    Mail(ID, Password, KickOtherLogin, "測試標題", "自動測試 如有誤寄打擾 抱歉QQ", 0)