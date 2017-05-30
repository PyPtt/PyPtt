import sys
import telnetlib
import time
import re
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import PTTTelnetCrawlerLibraryUtil

class PushInformation(object):
    def __init__(self, PushType, PushID, PushContent, PushTime):
        self._PushType = PushType
        self._PushID = PushID
        self._PushContent = PushContent
        self._PostContent = PostContent
        self._PushTime = PushTime

class PostInformation(object):
    def __init__(self, Board, PostID, Index, Author, Date, Title, WebUrl, Money, PostContent, OriginalData):
        self._Board = Board
        self._PostID = PostID
        self._Author = Author
        self._Date = Date
        self._Index = Index
        self._Title = Title
        self._PostContent = PostContent
        self._Money = Money
        self._WebUrl = WebUrl
        self._OriginalData = OriginalData

    def getPostID(self):
        return self._PostID
    def getPostIndex(self):
        return self._Index
    def getPostAuthor(self):
        return self._Author
    def getPostDate(self):
        return self._Date
    def getTitle(self):
        return self._Title
    def getPostContent(self):
        return self._PostContent
    def getMoney(self):
        return self._Money
    def getWebUrl(self):
        return self._WebUrl
    def getOriginalData(self):
        return self._OriginalData
    
class PTTTelnetCrawlerLibrary(object):
    def __init__(self, ID, password, kickOtherLogin):
 
        PTTTelnetCrawlerLibraryUtil.Log("ID: " + ID)

        TempPW = ''

        for i in range(len(password)):
            TempPW += "*"
        
        PTTTelnetCrawlerLibraryUtil.Log("Password: " + TempPW)
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
        if u"動畫播放中" in self._content or u"請按任意鍵繼續" in self._content:
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
    
    def getPostInformationByID(self, Board, PostID):
        
        result = None   
    
        self.toUserMenu()
        if not self.toBoard(Board):
            PTTTelnetCrawlerLibraryUtil.Log("Into " + Board + " fail")
            return None
        self._telnet.write(b'#' + PostID.encode('big5') + b'\r\n')
        self.waitResponse()
        if u"找不到這個文章代碼(AID)" in self._content:
            PTTTelnetCrawlerLibraryUtil.Log("Find post id " + PostID + " fail")
            return None

        #Refresh screen
        self._telnet.write(b'\x0C')
        self.waitResponse()

        #PostID, Index, Title, WebUrl, Money, PostContent):
        PostIndex = -1
        PostAuthor = ""
        PostTitle = ""
        PostDate = ""
        PostWebUrl = ""
        PostMoney = -1
        PostContent = ""
        
        for InforTempString in self._content.split("\r\n"):
            if ">" in InforTempString:
                PostIndex = re.search(r'\d+', InforTempString).group()

        if PostIndex == -1:
            PTTTelnetCrawlerLibraryUtil.Log("Find PostIndex fail")
            return None
        
        #Query post information
        self._telnet.write(b'Q')
        self.waitResponse()

        for InforTempString in self._content.split("\r\n"):
            Line = InforTempString.replace("[1;37m", "")
            Line = Line.replace("[16;77H", "")
            Line = Line.replace("[15;77H", "")

            if u"https" in Line:
                PostWebUrl = Line[Line.index("https://") : Line.index(".html") + len(".html")]
            if u"這一篇文章值" in Line:
                PostMoney = re.search(r'\d+', Line).group()
        
        if PostWebUrl == "":
            PTTTelnetCrawlerLibraryUtil.Log("Find PostWebUrl fail")
            return None
        if PostMoney == -1:
            PTTTelnetCrawlerLibraryUtil.Log("Find PostMoney fail")
            return None
            
        
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
		
        res = requests.get(PostWebUrl)
        if 'over18' in res.url:
            PTTTelnetCrawlerLibraryUtil.Log("Detect 18 web")
            load = {
                'from': '/bbs/{}/index.html'.format(Board),
                'yes': 'yes'
            }
            res = WebRequest.post('https://www.ptt.cc/ask/over18', verify=False, data=load)
		
        ##################
        
        soup =  BeautifulSoup(res.text,"html.parser")
        main_content = soup.find(id="main-content")
        metas = main_content.select('div.article-metaline')
        filtered = [ v for v in main_content.stripped_strings if v[0] not in [u'※', u'◆'] and  v[:2] not in [u'--'] ]
        content = ' '.join(filtered)
        content = re.sub(r'(\s)+', '', content )
        
        author = metas[0].select('span.article-meta-value')[0].string
        title = metas[1].select('span.article-meta-value')[0].string
        date = metas[2].select('span.article-meta-value')[0].string
        
        PostTitle = title
        PostAuthor = author
        PostDate = date
        #print(content)
        try:
            if content.index("--" + PostWebUrl) > 0:
                PostContent = content[0 : content.index("--" + PostWebUrl)]
            else:
                PostContent = content[0 : content.index(PostWebUrl)]
            PostContent = PostContent[PostContent.index(PostDate.replace(" ", "")) + len(PostDate.replace(" ", "")): len(PostContent)]
        except ValueError:
            print("Error!")
            print(content)
            return None
        ##################
        
        if PostTitle == "":
            PTTTelnetCrawlerLibraryUtil.Log("Find PostTitle fail")
            return None
        if PostAuthor == "":
            PTTTelnetCrawlerLibraryUtil.Log("Find PostAuthor fail")
            return None
        if PostDate == "":
            PTTTelnetCrawlerLibraryUtil.Log("Find PostDate fail")
            return None
        
        """PTTTelnetCrawlerLibraryUtil.Log("Post id: " + PostID)
        PTTTelnetCrawlerLibraryUtil.Log("Post index: " + PostIndex)
        PTTTelnetCrawlerLibraryUtil.Log("Post title: " + PostTitle)
        PTTTelnetCrawlerLibraryUtil.Log("Post web url: " + PostWebUrl)
        PTTTelnetCrawlerLibraryUtil.Log("Post money: " + PostMoney)"""
        
        result = PostInformation(Board, PostID, PostIndex, PostAuthor, PostDate, PostTitle, PostWebUrl, PostMoney, PostContent, res.text)

        return result
    def getPostInformationByIndex(self, Board, Index):
        
        result = None   
    
        self.toUserMenu()
        if not self.toBoard(Board):
            PTTTelnetCrawlerLibraryUtil.Log("Into " + Board + " fail")
            return result
        
        NewestIndex = self.getNewestPostIndex(Board)
        
        if Index <= 0 or NewestIndex < Index:
            PTTTelnetCrawlerLibraryUtil.Log("Error index: " + str(Index))
            PTTTelnetCrawlerLibraryUtil.Log("0 ~ " + NewestIndex)
            return result
        
        self._telnet.write(str(Index).encode('big5') + b'\r\n')
        self.waitResponse()

        self._telnet.write(b'Q\x0C')
        self.waitResponse()
        
        PostID = ""
        
        for InforTempString in self._content.split("\r\n"):
            if u"│ 文章代碼(AID): \x1B[1;37m#" in InforTempString:
                PostID = InforTempString.replace(u"│ 文章代碼(AID): \x1B[1;37m#", "")
                PostID = PostID[0 : PostID.index(" ")]
                break
        #print(PostID)
        
        result = self.getPostInformationByID(Board, PostID)

        return result
        
    def getNewestPostIndex(self, Board):
        result = -1
        self.toUserMenu()
        if not self.toBoard(Board):
            PTTTelnetCrawlerLibraryUtil.Log("Into " + Board + " fail")
            return result

        self._telnet.write(b'\x0C')
        self.waitResponse()
        
        while not u"> \x1B[1;33m  ★" in self._content:
            self._telnet.write(b'\x1b\x4fB\x0C')
            self.waitResponse()
        while u"> \x1B[1;33m  ★" in self._content:
            self._telnet.write(b'\x1b\x4fA\x0C')
            self.waitResponse()

        #print(self._content)
        for InforTempString in self._content.split("\r\n"):
            if u">" in InforTempString:
                #print(InforTempString)
                result = int(re.search(r'\d+', InforTempString).group())
                break
        return result
    def getNewPostIndex(self, Board, LastPostIndex):
        
        result = []
        LastIndex = self.getNewestPostIndex(Board)
        if LastPostIndex <= 0 or LastIndex < LastPostIndex:
            result.append(LastIndex)
        else:
            for IndexTemp in range(LastPostIndex + 1, LastIndex + 1):
                result.append(IndexTemp)
        return result
        
if __name__ == "__main__":

    print("PTT Telnet Crawler Library v 0.1.170528")
    print("PTT CodingMan")
