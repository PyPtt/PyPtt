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
        
        self.PushType_Push =         1
        self.PushType_Boo =          2
        self.PushType_Arrow =        3

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
                PTTTelnetCrawlerLibraryUtil.Log("Delete error password log....")
                self._telnet.write(b"y\r\n")
                    
            elif u"您有一篇文章尚未完成" in self._content:
                PTTTelnetCrawlerLibraryUtil.Log('Delete post not finished')
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
        self._telnet.write(b"\x0C")
        
        RetryTime = 0
        MaxWaitingTime = 10
        SleepTime = 1
        
        while len(self._content) == 0:
            time.sleep(SleepTime)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
            
            RetryTime = RetryTime + 1
            
            if len(self._content) == 0:
                PTTTelnetCrawlerLibraryUtil.Log('Catch lost...raise exception in ' + str(MaxWaitingTime - RetryTime * SleepTime) + " sec")
            
            if RetryTime * SleepTime >= MaxWaitingTime:
                raise Exception("Wait repsonse time out")
            
    def connect(self):
        self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        if u"系統過載" in self._content:
            PTTTelnetCrawlerLibraryUtil.Log('System is overload')
            sys.exit(0)
        return True
    def Log(self, Message):
        PTTTelnetCrawlerLibraryUtil.Log(Message)
    def login(self):

        result = self.input_user_password
        
        if result:
            PTTTelnetCrawlerLibraryUtil.Log('Login success')
        else :
            PTTTelnetCrawlerLibraryUtil.Log("Login fail")

        return result

    def gotoUserMenu(self):
        #\x1b[D 左
        #A上 B下C右D左
        self._telnet.write(b'\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D')
        self.waitResponse()
            
    def gotoBoard(self, Board):
                
        # s 進入要發文的看板
        self.gotoUserMenu()
        self._telnet.write(b's' + Board.encode('big5') + b'\r\n')
        self.waitResponse()
        
        while u"動畫播放中" in self._content or u"請按任意鍵繼續" in self._content or u"其他任意鍵停止" in self._content or not u"看板《" + Board + u"》" in self._content:
            self._telnet.write(b'q')
            self.waitResponse()
        
        #print(self._content)
        if u"看板《" + Board + u"》" in self._content and u"\x1B[H\x1B[2J\x1B[1;37;44m【板主:" in self._content:
            return True
        else:
            print(self._content)
            return False

    def logout(self):
        self.gotoUserMenu()
        self._telnet.write(b"g\r\ny\r\n")
        self._telnet.close()
        PTTTelnetCrawlerLibraryUtil.Log("Logout success")

    def post(self, board, title, content, PostType, SignType):
    
        if not self.gotoBoard(board):
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
        self._telnet.write(str(SignType).encode('big5') + b'\r\n')
        return True
    
    def gotoPostByIndex(self, Board, PostIndex):
    
        if not self.gotoBoard(Board):
            PTTTelnetCrawlerLibraryUtil.Log("Into " + Board + " fail")
            return False
        
        self._telnet.write(str(PostIndex).encode('big5') + b'\r\n')
        self.waitResponse()
        
        FindPost = False
        
        for InforTempString in self._content.split("\r\n"):
            if u">" in InforTempString and str(PostIndex) in InforTempString:
                FindPost = True
                break
        if not FindPost:
            PTTTelnetCrawlerLibraryUtil.Log("Find post fail")
            return False
        return True
        
    def gotoPostByID(self, Board, PostID):
    
        if not self.gotoBoard(Board):
            PTTTelnetCrawlerLibraryUtil.Log("Into " + Board + " fail")
            return False
        self._telnet.write(b'#' + PostID.encode('big5') + b'\r\n')
        self.waitResponse()
        if u"找不到這個文章代碼(AID)" in self._content:
            PTTTelnetCrawlerLibraryUtil.Log("Find post id " + PostID + " fail")
            return False
        
        return True
    
    def pushByIndex(self, Board, PostIndex, PushType, PushContent):
    
        if not self.gotoPostByIndex(Board, PostIndex):
            PTTTelnetCrawlerLibraryUtil.Log("Go to post fail")
            return False
        
        """
        PTTTelnetCrawlerLibrary_PushType_Push =         0x01
        PTTTelnetCrawlerLibrary_PushType_Boo =          0x02
        PTTTelnetCrawlerLibrary_PushType_Arrow =        0x03
        """
        
        if PushType != self.PushType_Push and PushType != self.PushType_Boo and PushType != self.PushType_Arrow:
            PTTTelnetCrawlerLibraryUtil.Log("Not support this push type: " + str(PushType))
            return False
        
        
        self._telnet.write(b'X')
        self.waitResponse()
        
        Pushable = False
        
        ArrowOnly = False
        
        AllowPushTypeList = [False, False, False, False]
        
        AllowPushTypeList[self.PushType_Push] = False
        AllowPushTypeList[self.PushType_Boo] = False
        AllowPushTypeList[self.PushType_Arrow] = False
        
        for InforTempString in self._content.split("\r\n"):
            if u"您覺得這篇文章" in InforTempString:
                if u"1.值得推薦" in InforTempString:
                    AllowPushTypeList[self.PushType_Push] = True
                if u"2.給它噓聲" in InforTempString:
                    AllowPushTypeList[self.PushType_Boo] = True
                if u"3.只加→註解" in InforTempString:
                    AllowPushTypeList[self.PushType_Arrow] = True
                Pushable = True
                break
            if u"使用 → 加註方式" in InforTempString:
                AllowPushTypeList[self.PushType_Arrow] = True
                PushType = self.PushType_Arrow
                ArrowOnly = True
                Pushable = True
                break
        
        if not Pushable:
            PTTTelnetCrawlerLibraryUtil.Log("No push option")
            return False
        
        if not AllowPushTypeList[self.PushType_Boo] and PushType == self.PushType_Boo:
            PushType = self.PushType_Arrow
        
        if ArrowOnly:
            self._telnet.write(PushContent.encode('big5') + b'\r\ny\r\n')
        else:
            self._telnet.write(str(PushType).encode('big5') + PushContent.encode('big5') + b'\r\ny\r\n')
        self.waitResponse()
        
        return True
    
    def pushByID(self, Board, PostID, PushType, PushContent):
    
        if not self.gotoPostByID(Board, PostID):
            PTTTelnetCrawlerLibraryUtil.Log("Go to post fail")
            return False
        
        """
        PTTTelnetCrawlerLibrary_PushType_Push =         0x01
        PTTTelnetCrawlerLibrary_PushType_Boo =          0x02
        PTTTelnetCrawlerLibrary_PushType_Arrow =        0x03
        """
        
        if PushType != self.PushType_Push and PushType != self.PushType_Boo and PushType != self.PushType_Arrow:
            PTTTelnetCrawlerLibraryUtil.Log("Not support this push type: " + str(PushType))
            return False
        
        
        self._telnet.write(b'X')
        self.waitResponse()
        
        Pushable = False
        
        ArrowOnly = False
        
        AllowPushTypeList = [False, False, False, False]
        
        AllowPushTypeList[self.PushType_Push] = False
        AllowPushTypeList[self.PushType_Boo] = False
        AllowPushTypeList[self.PushType_Arrow] = False
        
        for InforTempString in self._content.split("\r\n"):
            if u"您覺得這篇文章" in InforTempString:
                if u"1.值得推薦" in InforTempString:
                    AllowPushTypeList[self.PushType_Push] = True
                if u"2.給它噓聲" in InforTempString:
                    AllowPushTypeList[self.PushType_Boo] = True
                if u"3.只加→註解" in InforTempString:
                    AllowPushTypeList[self.PushType_Arrow] = True
                Pushable = True
                break
            if u"使用 → 加註方式" in InforTempString:
                AllowPushTypeList[self.PushType_Arrow] = True
                PushType = self.PushType_Arrow
                ArrowOnly = True
                Pushable = True
                break
        
        if not Pushable:
            PTTTelnetCrawlerLibraryUtil.Log("No push option")
            return False
        
        if not AllowPushTypeList[self.PushType_Boo] and PushType == self.PushType_Boo:
            PushType = self.PushType_Arrow
        
        if ArrowOnly:
            self._telnet.write(PushContent.encode('big5') + b'\r\ny\r\n')
        else:
            self._telnet.write(str(PushType).encode('big5') + PushContent.encode('big5') + b'\r\ny\r\n')
        self.waitResponse()
        
        return True
    
    def mail(self, UserID, MailTitle, MailContent, SignType):
        
        self.gotoUserMenu()
       
        self._telnet.write(b'M\r\nS\r\n' + UserID.encode('big5') + b'\r\n')
        self.waitResponse()
        
        if not u"主題：" in self._content:
            PTTTelnetCrawlerLibraryUtil.Log("No this PTT user " + UserID)
            print(self._content)
            return False
        self._telnet.write(MailTitle.encode('big5') + b'\r\n')
        self.waitResponse()
        self._telnet.write(MailContent.encode('big5') + b'\x18')# Ctrl+X
        self.waitResponse()
        
        # 儲存文章
        self._telnet.write(b's\r\n')
        self.waitResponse()
        
        if u"請選擇簽名檔" in self._content:
            self._telnet.write(str(SignType).encode('big5') + b'\r\n')
            self.waitResponse()
        
        if u"已順利寄出，是否自存底稿" in self._content:
            self._telnet.write(b'Y\r\n')
            self.waitResponse()
        
        if u"任意鍵繼續" in self._content:
            self._telnet.write(b'\r\n')
            self.waitResponse()
        
        return True
    
    def getPostInformationByID(self, Board, PostID):
        
        result = None   
    
        if not self.gotoPostByID(Board, PostID):
            PTTTelnetCrawlerLibraryUtil.Log("Go to post fail")
            return None

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
        if content.find("--" + PostWebUrl) >= 0:
            PostContent = content[0 : content.find("--" + PostWebUrl)]
        elif content.find(PostWebUrl) >= 0:
            PostContent = content[0 : content.find(PostWebUrl)]
        else:
            print(PostContent)
            PTTTelnetCrawlerLibraryUtil.Log("Content parse error")
            return None
            
        if PostContent.find(PostDate.replace(" ", "")) == -1:
            print(PostContent)
            return None
        PostContent = PostContent[PostContent.find(PostDate.replace(" ", "")) + len(PostDate.replace(" ", "")): len(PostContent)]
        
        if PostTitle == "":
            PTTTelnetCrawlerLibraryUtil.Log("Find PostTitle fail")
            return None
        if PostAuthor == "":
            PTTTelnetCrawlerLibraryUtil.Log("Find PostAuthor fail")
            return None
        if PostDate == "":
            PTTTelnetCrawlerLibraryUtil.Log("Find PostDate fail")
            return None
        
        result = PostInformation(Board, PostID, PostIndex, PostAuthor, PostDate, PostTitle, PostWebUrl, PostMoney, PostContent, res.text)

        return result
    def getPostInformationByIndex(self, Board, Index):
    
        if not self.gotoPostByIndex(Board, Index):
            PTTTelnetCrawlerLibraryUtil.Log("Go to post fail")
            return None
        
        PostID = ""
        
        self._telnet.write(b'Q')
        self.waitResponse()
        
        for InforTempString in self._content.split("\r\n"):
            if u"│ 文章代碼(AID): \x1B[1;37m#" in InforTempString:
                PostID = InforTempString.replace(u"│ 文章代碼(AID): \x1B[1;37m#", "")
                PostID = PostID[0 : PostID.find(" ")].replace("\x1b[m", "")
                break
        if PostID == "":
            PTTTelnetCrawlerLibraryUtil.Log("Query post fail, maybe has been deleted...")
            return None
        result = self.getPostInformationByID(Board, PostID)

        return result
        
    def getNewestPostIndex(self, Board):
        result = -1
        
        if not self.gotoBoard(Board):
            PTTTelnetCrawlerLibraryUtil.Log("Into " + Board + " fail")
            return result
        
        GoDown = True
        
        for InforTempString in self._content.split("\r\n"):
            if u">" in InforTempString[0 : InforTempString.find(u"□")] and u"★" in InforTempString[0 : InforTempString.find(u"□")]:
                GoDown = False
        
        while GoDown:
            self._telnet.write(b'\x1b[B')
            self.waitResponse()
            for InforTempString in self._content.split("\r\n"):
                if u">" in InforTempString[0 : InforTempString.find(u"□")] and u"★" in InforTempString[0 : InforTempString.find(u"□")]:
                    GoDown = False
                    break
        
        GoUp = True

        while GoUp:
            self._telnet.write(b'\x1b[A')
            self.waitResponse()
            for InforTempString in self._content.split("\r\n"):
                if u">" in InforTempString[0 : InforTempString.find(u"□")] and not u"★" in InforTempString[0 : InforTempString.find(u"□")]:
                    GoUp = False
                    break

        Line = 0
        for InforTempString in self._content.split("\r\n"):
            #print(str(Line) + " " + InforTempString)
            if u">" in InforTempString[0 : InforTempString.find(u"□")] and Line >=2:
                BoardLine = InforTempString[InforTempString.find(u">") : InforTempString.find(u">") + 8]
                result = int(re.search(r'\d+', BoardLine).group())
                break
            Line += 1
        
        return result
    def getNewPostIndex(self, Board, LastPostIndex):
        
        result = []
        LastIndex = self.getNewestPostIndex(Board)
        #print(LastIndex)
        #print(LastPostIndex)
        if LastPostIndex <= 0 or LastIndex < LastPostIndex:
            result.append(LastIndex)
        else:
            for IndexTemp in range(LastPostIndex + 1, LastIndex + 1):
                result.append(IndexTemp)
        return result
        
if __name__ == "__main__":

    print("PTT Telnet Crawler Library v 0.1.170601")
    print("PTT CodingMan")
