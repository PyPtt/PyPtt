import sys
import time
import PTTTelnetCrawlerLibrary

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
    while True:
    
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
    
if __name__ == "__main__":
    print("Welcome to PTT Telnet Crawler Library Demo")

    ID = 'Your PTT ID'
    Password = 'Your PTT Password'
    KickOtherLogin = False

    #發文類別           1
    #簽名檔        	0
    #Post(ID, Password, KickOtherLogin, 'test','發文類別測試', '發文類別測試 QQ', 1, 0)
    #GetPostInformationByID(ID, Password, KickOtherLogin, 'GO', "1PAIyWdT")
    GetPostInformationByIndex(ID, Password, KickOtherLogin, 'Wanted', 68935)
    #GetNewestPostIndex(ID, Password, KickOtherLogin, 'Wanted')
    #GetNewPostIndex(ID, Password, KickOtherLogin, 'Wanted')