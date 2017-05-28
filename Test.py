import sys
import PTTTelnetCrawlerLibrary

def Post(ID, PW, KickOtherLogin, Board, Title, Content):
    
    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, PW, KickOtherLogin)
    if PTTCrawler.isConnected():
        if PTTCrawler.login():
            PTTCrawler.post(Board, Title + " 1", Content)
            PTTCrawler.post(Board, Title + " 2", Content)
            PTTCrawler.post(Board, Title + " 3", Content)
            PTTCrawler.post(Board, Title + " 4", Content)
            PTTCrawler.post(Board, Title + " 5", Content)
    PTTCrawler.logout()

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

    Post(ID, Password, KickOtherLogin, 'test','發文文字測試', '這是一篇測試,哇哈哈 QQ')
