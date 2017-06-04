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
        self.__PushType = PushType
        self.__PushID = PushID
        self.__PushContent = PushContent
        self.__PushTime = PushTime
    def getPushType(self):
        return self.__PushType
    def getPushID(self):
        return self.__PushID
    def getPushContent(self):
        return self.__PushContent
    def getPushTime(self):
        return self.__PushTime    
class PostInformation(object):
    def __init__(self, Board, PostID, Index, Author, Date, Title, WebUrl, Money, PostContent, PushList, OriginalData):
        self.__Board = Board
        self.__PostID = PostID
        self.__Author = Author
        self.__Date = Date
        self.__Index = Index
        self.__Title = Title
        self.__PostContent = PostContent
        self.__Money = Money
        self.__WebUrl = WebUrl
        self.__PushList = PushList
        self.__OriginalData = OriginalData

    def getPostID(self):
        return self.__PostID
    def getPostIndex(self):
        return self.__Index
    def getPostAuthor(self):
        return self.__Author
    def getPostDate(self):
        return self.__Date
    def getTitle(self):
        return self.__Title
    def getPostContent(self):
        return self.__PostContent
    def getMoney(self):
        return self.__Money
    def getWebUrl(self):
        return self.__WebUrl
    def getPushList(self):
        return self.__PushList
    def getOriginalData(self):
        return self.__OriginalData
    
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
        self.__host = 'ptt.cc'
        self.__user = ID.encode('big5')
        self.__password = password.encode('big5')
        self.__kickOtherLogin = kickOtherLogin
        self.__telnet = telnetlib.Telnet(self.__host)
        self.__content = ''
        self.__isConnected = False
        
        self.__LastNewestPostIndex = {}
        
        self.PushType_Push =         1
        self.PushType_Boo =          2
        self.PushType_Arrow =        3
                
        time.sleep(1)

        if self.__connect():
            if self.__login():
                self.__isConnected = True
        
    @property
    def __is_success(self):

        NeedWait = True

        while NeedWait:
            if u"密碼不對" in self.__content:
                PTTTelnetCrawlerLibraryUtil.Log("Wrong password")
                sys.exit()
            elif u"您想刪除其他重複登入" in self.__content:

                if self.__kickOtherLogin:
                    self.__telnet.write(b"y\r\n")
                    PTTTelnetCrawlerLibraryUtil.Log("Detect other login")
                    PTTTelnetCrawlerLibraryUtil.Log("Kick other login success")
                else :
                    self.__telnet.write(b"n\r\n")
                    PTTTelnetCrawlerLibraryUtil.Log("Detect other login")

            elif u"按任意鍵繼續" in self.__content:
                self.__telnet.write(b"\r\n")

            elif u"您要刪除以上錯誤嘗試" in self.__content:
                PTTTelnetCrawlerLibraryUtil.Log("Delete error password log")
                self.__telnet.write(b"y\r\n")
                    
            elif u"您有一篇文章尚未完成" in self.__content:
                PTTTelnetCrawlerLibraryUtil.Log('Delete post not finished')
                self.__telnet.write(b"q\r\n")
            elif u"正在更新" in self.__content:
                PTTTelnetCrawlerLibraryUtil.Log('Wait system update')
            else:
                NeedWait = False
            if NeedWait:
                self.__waitResponse()
        return True

    @property
    def input_user_password(self):
        if u"請輸入代號" in self.__content:
            self.__telnet.write(self.__user + b"\r\n")
            self.__telnet.write(self.__password + b"\r\n")
            
            self.__waitResponse()
                
            return self.__is_success

        return False

    def isLoginSuccess(self):
        return self.__isConnected
    def __waitResponse(self):
        self.__content = ''
        
        RetryTime = 0
        MaxWaitingTime = 30
        if self.__isConnected:
            SleepTime = 0.1
        else:
            SleepTime = 1
        
        while len(self.__content) <= 8:
            self.__telnet.write(b"\x0C")
            time.sleep(SleepTime)
            self.__content = self.__telnet.read_very_eager().decode('big5', 'ignore')
            self.__content = re.sub(r'\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))', '', self.__content)
            
            RetryTime = RetryTime + 1
            if len(self.__content) <= 8 and MaxWaitingTime - RetryTime * SleepTime <= 10:
                PTTTelnetCrawlerLibraryUtil.Log('Lost connect...time out in ' + str(int(MaxWaitingTime - RetryTime * SleepTime)) + " sec")
            
            if RetryTime * SleepTime >= MaxWaitingTime:
                raise Exception("Wait repsonse time out")
        
        if self.__content.find(u"文章選讀") > 0:
            self.__content = self.__content[:self.__content.find(u"文章選讀")]
        
    def __connect(self):
        self.__content = self.__telnet.read_very_eager().decode('big5', 'ignore')
        if u"系統過載" in self.__content:
            PTTTelnetCrawlerLibraryUtil.Log('System is overload')
            sys.exit(0)
        return True
    def Log(self, Message):
        PTTTelnetCrawlerLibraryUtil.Log(Message)
    def __login(self):

        result = self.input_user_password
        
        if result:
            PTTTelnetCrawlerLibraryUtil.Log('Login success')
        else :
            PTTTelnetCrawlerLibraryUtil.Log("Login fail")

        return result

    def gotoUserMenu(self):
        #\x1b[D 左
        #A上 B下C右D左
        self.__telnet.write(b'\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D')
        self.__waitResponse()
        
    def gotoBoard(self, Board):
        for i in range(10):
            if self.__gotoBoard(Board):
                return True
        return False
    def __gotoBoard(self, Board):
        # s 進入要發文的看板
        self.gotoUserMenu()
        
        self.__telnet.write(b's')
        self.__waitResponse()
        self.__telnet.write(Board.encode('big5') + b'\r\n')
        time.sleep(0.1)
        self.__waitResponse()
        
        GotoBoardRetryTime = 0
        while u"動畫播放中" in self.__content or u"請按任意鍵繼續" in self.__content or u"其他任意鍵停止" in self.__content or not u"看板《" + Board + u"》" in self.__content:
            self.__telnet.write(b'q')
            self.__waitResponse()
            GotoBoardRetryTime += 1
            if GotoBoardRetryTime >= 10:
                #print(self.__content)
                return False
        
        if u"看板《" + Board + u"》" in self.__content and u"【板主:" in self.__content:
            return True
        else:
            #print(self.__content)
            return False

    def logout(self):
        self.gotoUserMenu()
        self.__telnet.write(b"g\r\ny\r\n")
        self.__telnet.close()
        PTTTelnetCrawlerLibraryUtil.Log("Logout success")

    def post(self, board, title, content, PostType, SignType):
    
        if not self.gotoBoard(board):
            PTTTelnetCrawlerLibraryUtil.Log("Go to " + board + " fail")
            return False

        # 請參考 http://donsnotes.com/tech/charsets/ascii.html#cntrl
        # Ctrl+P
        self.__telnet.write(b'\x10')
        # 發文類別
        self.__telnet.write(str(PostType).encode('big5') + b'\r\n')
        self.__telnet.write(title.encode('big5') + b'\r\n')
        self.__waitResponse()
        # Ctrl+X
        self.__telnet.write(content.encode('big5') + b'\x18')
        self.__waitResponse()
        # 儲存文章
        self.__telnet.write(b's\r\n')
        self.__telnet.write(str(SignType).encode('big5') + b'\r\n')
        return True
    
    def gotoPostByIndex(self, Board, PostIndex):
        for i in range(20):
            try:
                if self.__gotoPostByIndex(Board, PostIndex):
                    return True
            except Exception:
                return False
        return False
    def __gotoPostByIndex(self, Board, PostIndex):
        if not self.gotoBoard(Board):
            PTTTelnetCrawlerLibraryUtil.Log("Go to " + Board + " fail")
            return False
        Target = '>{0: >6}'.format(str(PostIndex))
        
        self.__telnet.write(str(PostIndex).encode('big5') + b'\r\n')
        self.__waitResponse()
        
        if not Target in self.__content:
            raise Exception("This post does not exist")
        
        FindPost = False
        MarkList = [m.start() for m in re.finditer(u'>', self.__content)]
        
        #print(MarkList)
        if len(MarkList) == 1:
            self.__content = self.__content[MarkList[0]:]
        if len(MarkList) == 2 or len(MarkList) == 3:
            self.__content = self.__content[MarkList[1]:]     
        if len(MarkList) == 3:
            self.__content = self.__content[:MarkList[2]]
        
        NextTarget = str(PostIndex + 1)
        if Target in self.__content:
            self.__content = self.__content[self.__content.find(Target):]
            if NextTarget in self.__content:
                self.__content = self.__content[:self.__content.find(NextTarget)]
            #print(self.__content)
            #print(self.__content.find(u"("))
            #print(self.__content.find(u"-"))
            if self.__content.find(u"(") <= 26 and self.__content.find(u"-") < self.__content.find(u"("):
                PTTTelnetCrawlerLibraryUtil.Log("This post has been deleted")
                raise Exception("This post has been deleted")
            else:
                return True
        return False
    def gotoPostByID(self, Board, PostID):
    
        if not self.gotoBoard(Board):
            PTTTelnetCrawlerLibraryUtil.Log("Go to " + Board + " fail")
            return False
        self.__telnet.write(b'#' + PostID.encode('big5') + b'\r\n')
        self.__waitResponse()
        if u"找不到這個文章代碼(AID)" in self.__content:
            PTTTelnetCrawlerLibraryUtil.Log("Find post id " + PostID + " fail")
            return False
        
        return True
    
    def pushByIndex(self, Board, PostIndex, PushType, PushContent):
    
        if not self.gotoPostByIndex(Board, PostIndex):
            PTTTelnetCrawlerLibraryUtil.Log("Go to post fail")
            return False
        
        if PushType != self.PushType_Push and PushType != self.PushType_Boo and PushType != self.PushType_Arrow:
            PTTTelnetCrawlerLibraryUtil.Log("Not support this push type: " + str(PushType))
            return False
        
        self.__telnet.write(b'X')
        self.__waitResponse()
        
        Pushable = False
        
        ArrowOnly = False
        
        AllowPushTypeList = [False, False, False, False]
        
        AllowPushTypeList[self.PushType_Push] = False
        AllowPushTypeList[self.PushType_Boo] = False
        AllowPushTypeList[self.PushType_Arrow] = False
        
        for InforTempString in self.__content.split("\r\n"):
            #print(InforTempString)
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
            if u"本板禁止快速連續推文" in InforTempString:
                PTTTelnetCrawlerLibraryUtil.Log("No fast push, please wait")
                return False
        if not Pushable:
            PTTTelnetCrawlerLibraryUtil.Log("No push option")
            return False
        
        if not AllowPushTypeList[self.PushType_Boo] and PushType == self.PushType_Boo:
            PushType = self.PushType_Arrow
        
        if ArrowOnly:
            self.__telnet.write(PushContent.encode('big5') + b'\r\ny\r\n')
        else:
            self.__telnet.write(str(PushType).encode('big5') + PushContent.encode('big5') + b'\r\ny\r\n')
        self.__waitResponse()
        
        return True
    
    def pushByID(self, Board, PostID, PushType, PushContent):
    
        if not self.gotoPostByID(Board, PostID):
            PTTTelnetCrawlerLibraryUtil.Log("Go to post fail")
            return False
        
        if PushType != self.PushType_Push and PushType != self.PushType_Boo and PushType != self.PushType_Arrow:
            PTTTelnetCrawlerLibraryUtil.Log("Not support this push type: " + str(PushType))
            return False
        
        self.__telnet.write(b'X')
        self.__waitResponse()
        
        Pushable = False
        
        ArrowOnly = False
        
        AllowPushTypeList = [False, False, False, False]
        
        AllowPushTypeList[self.PushType_Push] = False
        AllowPushTypeList[self.PushType_Boo] = False
        AllowPushTypeList[self.PushType_Arrow] = False
        
        for InforTempString in self.__content.split("\r\n"):
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
            if u"本板禁止快速連續推文" in InforTempString:
                PTTTelnetCrawlerLibraryUtil.Log("No fast push, please wait")
                return False
        if not Pushable:
            PTTTelnetCrawlerLibraryUtil.Log("No push option")
            return False
        
        if not AllowPushTypeList[self.PushType_Boo] and PushType == self.PushType_Boo:
            PushType = self.PushType_Arrow
        
        if ArrowOnly:
            self.__telnet.write(PushContent.encode('big5') + b'\r\ny\r\n')
        else:
            self.__telnet.write(str(PushType).encode('big5') + PushContent.encode('big5') + b'\r\ny\r\n')
        self.__waitResponse()
        
        return True
    
    def mail(self, UserID, MailTitle, MailContent, SignType):
        
        self.gotoUserMenu()
       
        self.__telnet.write(b'M\r\nS\r\n' + UserID.encode('big5') + b'\r\n')
        self.__waitResponse()
        
        if not u"主題：" in self.__content:
            PTTTelnetCrawlerLibraryUtil.Log("No this PTT user " + UserID)
            print(self.__content)
            return False
        self.__telnet.write(MailTitle.encode('big5') + b'\r\n')
        self.__waitResponse()
        self.__telnet.write(MailContent.encode('big5') + b'\x18')# Ctrl+X
        self.__waitResponse()
        
        # 儲存文章
        self.__telnet.write(b's\r\n')
        self.__waitResponse()
        
        if u"請選擇簽名檔" in self.__content:
            self.__telnet.write(str(SignType).encode('big5') + b'\r\n')
            self.__waitResponse()
        
        if u"已順利寄出，是否自存底稿" in self.__content:
            self.__telnet.write(b'Y\r\n')
            self.__waitResponse()
        
        if u"任意鍵繼續" in self.__content:
            self.__telnet.write(b'\r\n')
            self.__waitResponse()
        
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
        
        MarkList = [m.start() for m in re.finditer(u'>', self.__content)]                    
        if len(MarkList) == 0:
            return False
        
        self.__content = self.__content[MarkList[len(MarkList) - 1]:]
        
        for InforTempString in self.__content.split("\r\n"):
            if u">" in InforTempString:
                try:
                    PostIndex = re.search(r'\d+', InforTempString).group()
                    break
                except AttributeError:
                    pass
        if PostIndex == -1:
            PTTTelnetCrawlerLibraryUtil.Log("Find PostIndex fail")
            return None
        
        #Query post information
        self.__telnet.write(b'Q')
        self.__waitResponse()

        for InforTempString in self.__content.split("\r\n"):
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
        #print(PostWebUrl)
        res = requests.get(
            url = PostWebUrl,
            cookies={'over18': '1'}
        )
        
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
        
        PostContentArea = False
        
        PushArea = False
        
        PushType = 0
        PushID = ""
        PushContent = ""
        PushDate = ""
        PushIndex = 0
        
        PushList = []
        for ContentLine in filtered:
            #print(ContentLine)
            if u"推" in ContentLine or u"噓" in ContentLine or u"→" in ContentLine:
                PushArea = True
            if PushArea:
                if PushIndex == 0:
                    if u"推" in ContentLine:
                        PushType = self.PushType_Push
                    elif u"噓" in ContentLine:
                        PushType = self.PushType_Boo
                    elif u"→" in ContentLine:
                        PushType = self.PushType_Arrow
                if PushIndex == 1:
                    PushID = ContentLine
                if PushIndex == 2:
                    PushContent = ContentLine[2:]
                if PushIndex == 3:
                    PushDate = ContentLine
                    
                PushIndex += 1
                
                if PushIndex >=4:
                    PushIndex = 0
                    #print(str(PushType) + " " + PushID + " " + PushContent + " " + PushDate)
                    PushList.append(PushInformation(PushType, PushID, PushContent, PushDate))
            if date == ContentLine:
                PostContentArea = True
                continue
            if PostWebUrl == ContentLine or u"推" in ContentLine or u"噓" in ContentLine or u"→" in ContentLine:
                PostContentArea = False
            if PostContentArea:
                PostContent += ContentLine + "\r\n"
        
        if PostTitle == "":
            PTTTelnetCrawlerLibraryUtil.Log("Find PostTitle fail")
            return None
        if PostAuthor == "":
            PTTTelnetCrawlerLibraryUtil.Log("Find PostAuthor fail")
            return None
        if PostDate == "":
            PTTTelnetCrawlerLibraryUtil.Log("Find PostDate fail")
            return None
        
        result = PostInformation(Board, PostID, PostIndex, PostAuthor, PostDate, PostTitle, PostWebUrl, PostMoney, PostContent, PushList, res.text)

        return result
    def getPostInformationByIndex(self, Board, Index):
    
        if not self.gotoPostByIndex(Board, Index):
            PTTTelnetCrawlerLibraryUtil.Log("Go to post fail")
            return None
        
        PostID = ""
        
        self.__telnet.write(b'Q')
        self.__waitResponse()
        
        for InforTempString in self.__content.split("\r\n"):
            if u"│ 文章代碼(AID): #" in InforTempString:
                PostID = InforTempString.replace(u"│ 文章代碼(AID): #", "")
                PostID = PostID[0 : PostID.find(" ")].replace("\x1b[m", "")
                break
        if PostID == "":
            PTTTelnetCrawlerLibraryUtil.Log("This post has been deleted...")
            return None
        result = self.getPostInformationByID(Board, PostID)

        return result
    
    def getNewestPostIndex(self, Board):
        for i in range(10):
            result = self.__getNewestPostIndex(Board)
            if not result == -1:
                return result
        return -1
    def __getNewestPostIndex(self, Board):
        result = -1
        if not self.gotoBoard(Board):
            PTTTelnetCrawlerLibraryUtil.Log("Goto " + Board + " fail")
            return result
        
        self.__telnet.write(b'$')
        self.__waitResponse()
        
        DetectRange = 30
        
        Line = 0
        GoUp = False
        
        if self.__content.find(u">") == -1:
            return -1
        
        if u">   ★" in self.__content:
            GoUp = True
        #else:
            #print(self.__content)
            #print(str(len(self.__content)))
        
        while GoUp:
            self.__telnet.write(b'\x1b[A')
            self.__waitResponse()
            if u">   ★" in self.__content:
                continue
            MarkList = [m.start() for m in re.finditer(u'>', self.__content)]        
            
            if len(MarkList) == 0:
                return False
            
            self.__content = self.__content[MarkList[len(MarkList) - 1]:]
            
            if u"★" in self.__content:
                self.__content = self.__content[:self.__content.find(u"★")]
            
            if u"看板《" + Board + "》" in self.__content:
                return -1
            
            try:
                #print(self.__content)
                result = int(re.search(r'\d+', self.__content).group())
            except AttributeError:
                #print(self.__content)
                #print("Parse index error")
                return -1
            break
        
        try:
            LastNewestPostIndexTemp = self.__LastNewestPostIndex[Board]
        except KeyError:
            self.__LastNewestPostIndex[Board] = -1
        
        CheckIndexDelta = False
        
        if not result == -1:
            for i in range(10, -10, -1):
                if self.__LastNewestPostIndex[Board] + i == result:
                    if self.gotoPostByIndex(Board, result):
                        CheckIndexDelta = True
                    break
        if (result != self.__LastNewestPostIndex[Board] or result == -1) and not self.__LastNewestPostIndex[Board] == -1 and not CheckIndexDelta:
            
            NewResult = result
            
            for ResultTempIndex in range(3, -4, -1):
                if self.gotoPostByIndex(Board, self.__LastNewestPostIndex[Board] + ResultTempIndex):
                    NewResult = self.__LastNewestPostIndex[Board] + ResultTempIndex
                    break
            
            if NewResult != result:
                if result == -1:
                    PTTTelnetCrawlerLibraryUtil.Log("Detect error recover mode: correct result to " + str(NewResult))
                else:
                    PTTTelnetCrawlerLibraryUtil.Log("Check new index: correct result to " + str(NewResult))
                result = NewResult
            else:
                PTTTelnetCrawlerLibraryUtil.Log("Check new index: OK")
        if result != -1:
            self.__LastNewestPostIndex[Board] = result
        return result
    def getNewPostIndex(self, Board, LastPostIndex):
        
        result = []
        LastIndex = self.getNewestPostIndex(Board)
        
        if LastIndex == -1:
            return result
        
        if LastPostIndex <= 0 or LastIndex < LastPostIndex:
            result.append(LastIndex)
        else:
            for IndexTemp in range(LastPostIndex + 1, LastIndex + 1):
                result.append(IndexTemp)
        return result
    
    def getPostFloorByIndex(self, Board, PostIndex):
        
        Post = self.getPostInformationByIndex(Board, PostIndex)
        
        if Post == None:
            return -1
        return len(Post.getPushList())
    def giveMoney(self, ID, Money, YourPassword):
    
        self.gotoUserMenu()
        
        self.__telnet.write(b'P\r\n')
        self.__waitResponse()
        
        if not u"量販店" in self.__content:
            PTTTelnetCrawlerLibraryUtil.Log("Go to Play fail")
            return False
        
        self.__telnet.write(b'P\r\n')
        self.__waitResponse()
        
        if not u"給其他人Ptt幣" in self.__content :
            PTTTelnetCrawlerLibraryUtil.Log("Go to Pay fail")
            return False
        
        self.__telnet.write(b'0\r\n')
        self.__waitResponse()
        
        if not u"這位幸運兒的id" in self.__content :
            PTTTelnetCrawlerLibraryUtil.Log("Pay fail")
            return False
        
        self.__telnet.write(ID.encode('big5') + b'\r\n')
        self.__waitResponse()
        
        if not u"請輸入金額" in self.__content :
            PTTTelnetCrawlerLibraryUtil.Log("Input ID fail")
            return False
        
        self.__telnet.write(b'\t')
        self.__waitResponse()
        
        self.__telnet.write(str(Money).encode('big5') + b'\r\n')
        time.sleep(3)
        self.__waitResponse()
        
        if u"請輸入您的密碼" in self.__content :
            self.__telnet.write(YourPassword.encode('big5') + b'\r\n')
            self.__waitResponse()
        
        while not u"按任意鍵繼續" in self.__content:
            #self.__waitResponse()
            if u"要修改紅包袋嗎" in self.__content:
                self.__telnet.write(b'n\r\n')
            if u"確定進行交易嗎" in self.__content :
                self.__telnet.write(b'y\r\n')
            self.__waitResponse()
        
        self.__telnet.write(b'\r\n')
        self.__waitResponse()
        return True
if __name__ == "__main__":

    print("PTT Telnet Crawler Library v 0.1.170604")
    print("PTT CodingMan")
