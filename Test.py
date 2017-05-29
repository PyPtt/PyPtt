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
def ListALLPost(ID, PW, KickOtherLogin, Board):
    
    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, PW, KickOtherLogin)
    if PTTCrawler.isConnected():
        if PTTCrawler.login():
            PTTCrawler.listPost(Board)
    PTTCrawler.logout()
    
if __name__ == "__main__":
    print("Welcome to PTT Telnet Crawler Library Demo")

    ID = 'Your PTT ID'
    Password = 'Your PTT Password'
    KickOtherLogin = False

    #發文類別           1
    #簽名檔選項  	0
    Post(ID, Password, KickOtherLogin, 'test','發文類別測試', '發文類別測試 QQ', 1, 0)
