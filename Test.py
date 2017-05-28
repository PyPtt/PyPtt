import sys
import PTTTelnetCrawlerLibrary

def Post(ID, PW, KickOtherLogin, Board, Title, Content):
    
    ptt = PTTTelnetCrawlerLibrary.Ptt(ID, PW, KickOtherLogin)
    if ptt.isLogined():
        if ptt.login():
            ptt.post(Board, Title, Content)
    ptt.logout()

if __name__ == "__main__":
    print("Welcome to PTT Telnet Crawler Library Demo")

    ID = 'Your PTT ID'
    Password = 'Your PTT Password'
    KickOtherLogin = False

    Post(ID, Password, KickOtherLogin, 'test','發文文字測試', '這是一篇測試,哇哈哈 QQ')
