import sys
import telnetlib
import time


class Ptt(object):
    def __init__(self, host, user, password):
        self._host = host
        self._user = user.encode('big5')
        self._password = password.encode('big5')
        self._telnet = telnetlib.Telnet(host)
        self._content = ''

    @property
    def is_success(self):
        if u"密碼不對" in self._content:
            print("密碼不對或無此帳號。程式結束")
            sys.exit()
        if u"您想刪除其他重複登入" in self._content:
            print("刪除其他重複登入的連線....")
            self._telnet.write(b"y\r\n")
            time.sleep(5)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        if u"請按任意鍵繼續" in self._content:
            print("資訊頁面，按任意鍵繼續...")
            self._telnet.write(b"\r\n")
            time.sleep(2)
        if u"您要刪除以上錯誤嘗試" in self._content:
            print("刪除以上錯誤嘗試...")
            self._telnet.write(b"y\r\n")
            time.sleep(2)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        if u"您有一篇文章尚未完成" in self._content:
            print('刪除尚未完成的文章....')
            # 放棄尚未編輯完的文章
            self._telnet.write(b"q\r\n")
            time.sleep(2)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        return True

    @property
    def input_user_password(self):
        if u"請輸入代號" in self._content:
            print('輸入帳號中...')
            self._telnet.write(self._user + b"\r\n")
            print('輸入密碼中...')
            self._telnet.write(self._password + b"\r\n")
            time.sleep(2)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
            return self.is_success
        return False

    def is_connect(self):
        self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        if u"系統過載" in self._content:
            print('系統過載, 請稍後再來')
            sys.exit(0)
        return True

    def login(self):
        if self.input_user_password:
            print("----------------------------------------------")
            print("------------------ 登入完成 ------------------")
            print("----------------------------------------------")
            return True
        print("沒有可輸入帳號的欄位，網站可能掛了")
        return False

    def logout(self):
        print("登出中...")
        # q = 上一頁，直到回到首頁為止，g = 離開，再見
        self._telnet.write(b"qqqqqqqqqg\r\ny\r\n")
        time.sleep(1)
        self._telnet.close()
        print("----------------------------------------------")
        print("------------------ 登出完成 ------------------")
        print("----------------------------------------------")

    def post(self, board, title, content):
        print("發文中...")
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
        print("----------------------------------------------")
        print("------------------ 發文成功 ------------------")
        print("----------------------------------------------")

if __name__ == "__main__":
    host = 'ptt.cc'
    user = 'CodingMan'
    password = 'love1214'
    ptt = Ptt(host, user, password)
    time.sleep(1)
    if ptt.is_connect():
        if ptt.login():
            ptt.post('test', '發文文字測試', '這是一篇測試,哇哈哈')
    ptt.logout()
