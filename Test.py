import sys
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
def GetPostInformation(ID, PW, KickOtherLogin, Board, PostID):

    result = False
    
    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, PW, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
        return False
    
    result = PTTCrawler.getPostInformationByID(Board, PostID)

    PTTCrawler.logout()
    return result
    
if __name__ == "__main__":
    print("Welcome to PTT Telnet Crawler Library Demo")

    ID = 'CodingMan'
    Password = 'love1214'
    KickOtherLogin = False

    #發文類別           1
    #簽名檔        	0
    #Post(ID, Password, KickOtherLogin, 'test','發文類別測試', '發文類別測試 QQ', 1, 0)
    GetPostInformation(ID, Password, KickOtherLogin, 'GO', "1PAIyWdT")
