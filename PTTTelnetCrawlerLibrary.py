import sys
import telnetlib
import time
import PTTTelnetCrawlerLibraryUtil

class PTTTelnetCrawlerLibrary(object):
    def __init__(self, ID, password, kickOtherLogin):

        PTTTelnetCrawlerLibraryUtil.Log("ID: " + ID)
        PTTTelnetCrawlerLibraryUtil.Log("Password: " + password)
        if kickOtherLogin:
            PTTTelnetCrawlerLibraryUtil.Log("This connection will kick other login")
        else :
            PTTTelnetCrawlerLibraryUtil.Log("This connection will NOT kick other login")

        PTTTelnetCrawlerLibraryUtil.Log("Start connect to PTT")
        self._host = 'ptt.cc'
        self._user = ID.encode('big5')
        self._password = password.encode('big5')
        self._kickOtherLogin = kickOtherLogin
        self._telnet = telnetlib.Telnet(self._host)
        self._content = ''
        self._isConnected = False
        time.sleep(1)

        if self.connect():
            if self.login():
                self._isConnected = True
        
    @property
    def is_success(self):

        NeedWait = True

        while NeedWait:
        
            if u"密碼不對" in self._content:
                PTTTelnetCrawlerLibraryUtil.Log("Wrong password")
                sys.exit()
            elif u"您想刪除其他重複登入" in self._content:

                if self._kickOtherLogin:
                    self._telnet.write(b"y\r\n")
                    PTTTelnetCrawlerLibraryUtil.Log("Detect other login")
                    PTTTelnetCrawlerLibraryUtil.Log("Kick other login success")
                else :
                    self._telnet.write(b"n\r\n")
                    PTTTelnetCrawlerLibraryUtil.Log("Detect other login")

            elif u"請按任意鍵繼續" in self._content:
                self._telnet.write(b"\r\n")

            elif u"您要刪除以上錯誤嘗試" in self._content:
                PTTTelnetCrawlerLibraryUtil.Log("刪除以上錯誤嘗試...")
                self._telnet.write(b"y\r\n")
                    
            elif u"您有一篇文章尚未完成" in self._content:
                PTTTelnetCrawlerLibraryUtil.Log('刪除尚未完成的文章....')
                self._telnet.write(b"q\r\n")
            else:
                NeedWait = False
            if NeedWait:
                self.waitResponse()
        return True

    @property
    def input_user_password(self):
        if u"請輸入代號" in self._content:
            self._telnet.write(self._user + b"\r\n")
            self._telnet.write(self._password + b"\r\n")
            
            self.waitResponse()
                
            return self.is_success

        return False

    def isLoginSuccess(self):
        return self._isConnected
    def waitResponse(self):
        self._content = ''
        while len(self._content) == 0:
            time.sleep(1)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
    
    def connect(self):
        self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        if u"系統過載" in self._content:
            PTTTelnetCrawlerLibraryUtil.Log('System is overload')
            sys.exit(0)
        return True

    def login(self):

        result = self.input_user_password
        #self.toUserMenu()
        
        if result:
            PTTTelnetCrawlerLibraryUtil.Log('Login success')
        else :
            PTTTelnetCrawlerLibraryUtil.Log("Login fail")

        return result

    def toUserMenu(self):
        # q = 上一頁，直到回到首頁為止，g = 離開，再見

        self._telnet.write(b"qqqqqqqqqq\r\n")
        self.waitResponse()
            
    def toBoard(self, Board):
        # s 進入要發文的看板
        self._telnet.write(b's')
        self._telnet.write(Board.encode('big5') + b'\r\n')
        self.waitResponse()
        if u"動畫播放中" in self._content:
            #PTTTelnetCrawlerLibraryUtil.Log("First time into " + Board)
            self._telnet.read_very_eager().decode('big5', 'ignore')
            self._telnet.write(b'q')
            self.waitResponse()
        if u"看板《" + Board + u"》":
            return True
        else :
            return False

    def logout(self):
        self.toUserMenu()
        self._telnet.write(b"g\r\ny\r\n")
        self._telnet.close()
        PTTTelnetCrawlerLibraryUtil.Log("Logout success")

    def post(self, board, title, content, PostType, SignType):
        self.toUserMenu()
        if not self.toBoard(board):
            PTTTelnetCrawlerLibraryUtil.Log("Into " + board + " fail")
            return False

        # 請參考 http://donsnotes.com/tech/charsets/ascii.html#cntrl
        # Ctrl+P
        self._telnet.write(b'\x10')
        # 發文類別
        self._telnet.write(str(PostType).encode('big5') + b'\r\n')
        self._telnet.write(title.encode('big5') + b'\r\n')
        self.waitResponse()
        # Ctrl+X
        self._telnet.write(content.encode('big5') + b'\x18')
        self.waitResponse()
        # 儲存文章
        self._telnet.write(b's\r\n')
        # 不加簽名檔
        self._telnet.write(str(SignType).encode('big5') + b'\r\n')
        PTTTelnetCrawlerLibraryUtil.Log(title + " post success")

        return True
    def listPost(self, board):
        pass

if __name__ == "__main__":

    print("PTT Telnet Crawler Library v 0.1.170528")
    print("PTT CodingMan")
