import sys
import telnetlib
import time
import PTTTelnetCrawlerLibraryUtil

class Ptt(object):
    def __init__(self, ID, password, kickOtherLogin):

        PTTTelnetCrawlerLibraryUtil.Log("Start connect to PTT")
        PTTTelnetCrawlerLibraryUtil.Log("ID: " + ID)
        PTTTelnetCrawlerLibraryUtil.Log("Password: " + password)
        if kickOtherLogin:
            PTTTelnetCrawlerLibraryUtil.Log("This connection will kick other login")
        else :
            PTTTelnetCrawlerLibraryUtil.Log("This connection will NOT kick other login")
            
        self._host = 'ptt.cc'
        self._user = ID.encode('big5')
        self._password = password.encode('big5')
        self._kickOtherLogin = kickOtherLogin
        self._telnet = telnetlib.Telnet(self._host)
        self._content = ''
        time.sleep(1)
        
    @property
    def is_success(self):
        if u"密碼不對" in self._content:
            PTTTelnetCrawlerLibraryUtil.Log("Wrong password")
            sys.exit()
        if u"您想刪除其他重複登入" in self._content:
            if self._kickOtherLogin:
                self._telnet.write(b"y\r\n")
                PTTTelnetCrawlerLibraryUtil.Log("Kick other login success")
            else :
                self._telnet.write(b"n\r\n")     
            time.sleep(5)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        if u"請按任意鍵繼續" in self._content:
            self._telnet.write(b"\r\n")
            time.sleep(2)
        if u"您要刪除以上錯誤嘗試" in self._content:
            PTTTelnetCrawlerLibraryUtil.Log("刪除以上錯誤嘗試...")
            self._telnet.write(b"y\r\n")
            time.sleep(2)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        if u"您有一篇文章尚未完成" in self._content:
            PTTTelnetCrawlerLibraryUtil.Log('刪除尚未完成的文章....')
            self._telnet.write(b"q\r\n")
            time.sleep(2)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')

        PTTTelnetCrawlerLibraryUtil.Log('Login success')
        return True

    @property
    def input_user_password(self):
        if u"請輸入代號" in self._content:
            self._telnet.write(self._user + b"\r\n")
            self._telnet.write(self._password + b"\r\n")
            time.sleep(2)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
            return self.is_success
        return False

    def isConnected(self):
        self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        if u"系統過載" in self._content:
            PTTTelnetCrawlerLibraryUtil.Log('System is overload')
            sys.exit(0)
        return True

    def isLogined(self):
        if self.input_user_password:
            return True
        PTTTelnetCrawlerLibraryUtil.Log("Connect error")
        return False
 
    def logout(self):
        # q = 上一頁，直到回到首頁為止，g = 離開，再見
        self._telnet.write(b"qqqqqqqqqg\r\ny\r\n")
        time.sleep(1)
        self._telnet.close()
        PTTTelnetCrawlerLibraryUtil.Log("Logout success")

    def post(self, board, title, content):
        # s 進入要發文的看板
        self._telnet.write(b's')
        self._telnet.write(board.encode('big5') + b'\r\n')
        time.sleep(1)
        self._telnet.write(b'q')
        time.sleep(2)
        # 請參考 http://donsnotes.com/tech/charsets/ascii.html#cntrl
        # Ctrl+P
        self._telnet.write(b'\x10')
        # 發文類別
        self._telnet.write(b'1\r\n')
        self._telnet.write(title.encode('big5') + b'\r\n')
        time.sleep(1)
        # Ctrl+X
        self._telnet.write(content.encode('big5') + b'\x18')
        time.sleep(1)
        # 儲存文章
        self._telnet.write(b's\r\n')
        # 不加簽名檔
        self._telnet.write(b'0\r\n')
        PTTTelnetCrawlerLibraryUtil.Log("Post success")

if __name__ == "__main__":

    print("PTT Telnet Crawler Library v 0.1.170528")
    print("PTT CodingMan")
