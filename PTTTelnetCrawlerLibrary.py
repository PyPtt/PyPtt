# -*- coding: utf8 -*-
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
    def __init__(self, Board, PostID, Author, Date, Title, WebUrl, Money, PostContent, PushList, OriginalData):
        self.__Board = Board
        self.__PostID = PostID
        self.__Author = Author
        self.__Date = Date
        self.__Title = Title
        self.__PostContent = PostContent
        self.__Money = Money
        self.__WebUrl = WebUrl
        self.__PushList = PushList
        self.__OriginalData = OriginalData

    def getPostID(self):
        return self.__PostID
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
 
        PTTTelnetCrawlerLibraryUtil.Log('ID: ' + ID)

        TempPW = ''

        for i in range(len(password)):
            TempPW += '*'
        
        PTTTelnetCrawlerLibraryUtil.Log('Password: ' + TempPW)
        if kickOtherLogin:
            PTTTelnetCrawlerLibraryUtil.Log('This connection will kick other login')
        else :
            PTTTelnetCrawlerLibraryUtil.Log('This connection will NOT kick other login')

        self.__host = 'ptt.cc'
        self.__user = ID
        self.__password = password
        self.__kickOtherLogin = kickOtherLogin
        self.__telnet = telnetlib.Telnet(self.__host)
        self.__content = ''
        self.__isConnected = False
        
        self.__LastNewestPostIndex = {}
        
        self.PushType_Push =         1
        self.PushType_Boo =          2
        self.PushType_Arrow =        3
        
        self.__BasicSleepTime = 1
        self.__CurrentSleepTime = 2
        self.__StableTime = 0
        
        time.sleep(1)
        PTTTelnetCrawlerLibraryUtil.Log('Start connect to PTT')
        if self.__connect():
            if self.__login():
                self.__isConnected = True
        
    @property
    def __is_success(self):

        NeedWait = True

        while NeedWait:
            if '密碼不對' in self.__content:
                PTTTelnetCrawlerLibraryUtil.Log('Wrong password')
                sys.exit()
            elif '您想刪除其他重複登入' in self.__content:

                if self.__kickOtherLogin:
                    self.__sendData('y\r\n')
                    PTTTelnetCrawlerLibraryUtil.Log('Detect other login')
                    PTTTelnetCrawlerLibraryUtil.Log('Kick other login success')
                else :
                    self.__sendData('n\r\n')
                    PTTTelnetCrawlerLibraryUtil.Log('Detect other login')

            elif '按任意鍵繼續' in self.__content:
                self.__sendData('\r\n')

            elif '您要刪除以上錯誤嘗試' in self.__content:
                PTTTelnetCrawlerLibraryUtil.Log('Delete error password log')
                self.__sendData('y\r\n')
                    
            elif '您有一篇文章尚未完成' in self.__content:
                PTTTelnetCrawlerLibraryUtil.Log('Delete post not finished')
                self.__sendData('q\r\n')
            elif '正在更新' in self.__content:
                PTTTelnetCrawlerLibraryUtil.Log('Wait system update')
            else:
                NeedWait = False
            if NeedWait:
                self.__waitResponse()
        return True

    @property
    def input_user_password(self):
        if '請輸入代號' in self.__content:
            self.__sendData(self.__user + '\r\n')
            self.__sendData(self.__password + '\r\n')
            
            return self.__is_success
        return False

    def isLoginSuccess(self):
        return self.__isConnected
        
    def __sendData(self, Message, ExtraWait = False, ExtraWaitSec = 0):
        self.__telnet.write(str(Message).encode('big5'))
        if ExtraWaitSec > 0:
            time.sleep(ExtraWaitSec)        
        self.__waitResponse(ExtraWait)
    def __waitResponse(self, ExtraWait = False):
        self.__content = ''
        
        RetryTime = 0
        MaxWaitingTime = 30
        
        if self.__isConnected:
            SleepTime = self.__CurrentSleepTime / 100
        else:
            SleepTime = 1
        
        OKbefore = False
        OKafter = False
        
        MinDataSize = 12
        
        while len(self.__content) <= MinDataSize:
        
            OKbefore = False
            OKafter = False
        
            self.__telnet.write(b'\x0C')
            if ExtraWait:
                time.sleep(SleepTime)
            time.sleep(SleepTime)
            self.__content = self.__telnet.read_very_eager().decode('big5', 'ignore')
            
            if '>' in self.__content:
                OKbefore = True
            
            self.__content = self.__content.replace('\x1b', '')
            
            #Does someone can write perfect re code for this?
            
            self.__content = self.__content.replace('[K', '')
            self.__content = self.__content.replace('[m', '')
            self.__content = self.__content.replace('[H', '')
            self.__content = self.__content.replace('[2J', '')
            
            self.__content = self.__content.replace('[0;1;37;44m', '')
                        
            ColorList = ['H', 'm']
            
            for i in range(0, 48):
                self.__content = self.__content.replace('[' + str(i) + 'm', '')
                for ii in range(1, 48):
                    for Color in ColorList:
                        self.__content = self.__content.replace('[' + str(i) + ';' + str(ii) + Color, '')
            
            for i in range(0, 38):
                for ii in range(0, 2):
                    for iii in range(30, 48):
                        self.__content = self.__content.replace('[' + str(ii) + ';' + str(i) + ';' + str(iii) + 'm', '')
            
            for i in range(0, 2):
                for ii in range(0, 2):
                    for iii in range(37, 48):
                        for iiii in range(37, 48):
                            self.__content = self.__content.replace('[' + str(i) + ';' + str(ii) + ';' + str(iii) + ';' + str(iiii) + 'm', '')
            
            if '【板主:' in self.__content:
                self.__content = self.__content[self.__content.find('【板主:'):]
            
            if '>' in self.__content:
                OKafter = True
            
            RetryTime = RetryTime + 1
            if len(self.__content) <= MinDataSize and MaxWaitingTime - RetryTime * SleepTime <= 10:
                PTTTelnetCrawlerLibraryUtil.Log('Lost connect...time out in ' + str(int(MaxWaitingTime - RetryTime * SleepTime)) + ' sec')
            
            if RetryTime * SleepTime >= MaxWaitingTime:
                raise Exception('Wait repsonse time out')
                
        if OKbefore and not OKafter:
            #print("!!!!!!!!!!!!!!!!!remove color error!!!!!!!!!!!!!!!!!!!!!!!!!")
            pass
        #print(self.__content)
        
        if RetryTime == 1:
            if self.__StableTime >= 4:
                self.__CurrentSleepTime = int(self.__CurrentSleepTime / 2.0)
                if self.__CurrentSleepTime <= 0:
                    self.__CurrentSleepTime = self.__BasicSleepTime
                self.__StableTime = 0
                #print('self.__CurrentSleepTime: ' + str(self.__CurrentSleepTime))
            else:
                self.__StableTime += 1
        elif RetryTime == 2:
            self.__CurrentSleepTime += self.__BasicSleepTime
            self.__StableTime = 0
        elif RetryTime >= 3:
            self.__CurrentSleepTime = self.__CurrentSleepTime * RetryTime
            self.__StableTime = 0
            #PTTTelnetCrawlerLibraryUtil.Log('Detect network deley')
        
        if self.__content.find('文章選讀') > 0:
            self.__content = self.__content[:self.__content.find('文章選讀')]
        
    def __connect(self):
        self.__content = self.__telnet.read_very_eager().decode('big5', 'ignore')
        if '系統過載' in self.__content:
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
            PTTTelnetCrawlerLibraryUtil.Log('Login fail')

        return result

    def gotoUserMenu(self):
        #\x1b[D 左
        #A上 B下C右D左
        self.__sendData('\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D')
        
    def gotoBoard(self, Board):
        for i in range(5):
            if self.__gotoBoard(Board):
                return True
            time.sleep(self.__CurrentSleepTime / 100)
        return False
    def __gotoBoard(self, Board):
        # s 進入要發文的看板
        self.gotoUserMenu()
        
        self.__sendData('s')
        self.__sendData(Board + '\r\n', True)
        GotoBoardRetryTime = 0
        while '動畫播放中' in self.__content or '請按任意鍵繼續' in self.__content or '其他任意鍵停止' in self.__content or not '看板《' + Board + '》' in self.__content:
            self.__sendData('q')
            GotoBoardRetryTime += 1
            if GotoBoardRetryTime >= 5:
                break
        
        if '看板《' + Board + '》' in self.__content and '【板主:' in self.__content:
            return True
        else:
            #print(self.__content)
            return False

    def logout(self):
        self.gotoUserMenu()
        self.__telnet.write(b'g\r\ny\r\n')
        self.__telnet.close()
        PTTTelnetCrawlerLibraryUtil.Log('Logout success')

    def post(self, board, title, content, PostType, SignType):
    
        if not self.gotoBoard(board):
            PTTTelnetCrawlerLibraryUtil.Log('Go to ' + board + ' fail')
            return False

        # 請參考 http://donsnotes.com/tech/charsets/ascii.html#cntrl
        # Ctrl+P
        self.__sendData('\x10')
        # 發文類別
        self.__sendData(str(PostType) + '\r\n')
        self.__sendData(title + '\r\n')
        # Ctrl+X
        self.__sendData(content + '\x18')
        # 儲存文章
        self.__sendData('s\r\n')
        self.__sendData(str(SignType) + '\r\n')
        return True
    
    def gotoPostByIndex(self, Board, PostIndex):
        for i in range(10):
            try:
                if self.__gotoPostByIndex(Board, PostIndex):
                    return True
                time.sleep(self.__CurrentSleepTime / 100)
            except Exception:
                return False
        return False
    def __gotoPostByIndex(self, Board, PostIndex):
        if not self.gotoBoard(Board):
            PTTTelnetCrawlerLibraryUtil.Log('Go to ' + Board + ' fail')
            return False
        Target = '>{0: >6}'.format(str(PostIndex))
        
        self.__sendData(str(PostIndex) + '\r\n')
        
        if not Target in self.__content:
            #print("safeline 1")
            #print(self.__content)
            #print(str(len(self.__content)))
            return False
        
        NextTarget = str(PostIndex + 1)
        if Target in self.__content:
            self.__content = self.__content[self.__content.find(Target):]
            if NextTarget in self.__content:
                self.__content = self.__content[:self.__content.find(NextTarget)]
            #print(self.__content)
            #print(self.__content.find('('))
            #print(self.__content.find('-'))
            if self.__content.find('(') <= 26 and self.__content.find('-') < self.__content.find('('):
                PTTTelnetCrawlerLibraryUtil.Log('This post has been deleted')
                raise Exception('This post has been deleted')
            else:
                return True
        print('__gotoPostByIndex ' + self.__content)
        print('__gotoPostByIndex ' + OrigrinalContent)
        print(MarkList)
        
        return False
    def gotoPostByID(self, Board, PostID):
    
        if not self.gotoBoard(Board):
            PTTTelnetCrawlerLibraryUtil.Log('Go to ' + Board + ' fail')
            return False
        self.__sendData('#' + PostID + '\r\n')
        
        if '找不到這個文章代碼(AID)' in self.__content:
            PTTTelnetCrawlerLibraryUtil.Log('Find post id ' + PostID + ' fail')
            return False
        
        return True
    
    def pushByIndex(self, Board, PostIndex, PushType, PushContent):
    
        if not self.gotoPostByIndex(Board, PostIndex):
            PTTTelnetCrawlerLibraryUtil.Log('Go to post index fail')
            return False
        
        if PushType != self.PushType_Push and PushType != self.PushType_Boo and PushType != self.PushType_Arrow:
            PTTTelnetCrawlerLibraryUtil.Log('Not support this push type: ' + str(PushType))
            return False
        
        self.__sendData('X')

        Pushable = False
        
        ArrowOnly = False
        
        AllowPushTypeList = [False, False, False, False]
        
        AllowPushTypeList[self.PushType_Push] = False
        AllowPushTypeList[self.PushType_Boo] = False
        AllowPushTypeList[self.PushType_Arrow] = False
        
        for InforTempString in self.__content.split('\r\n'):
            #print(InforTempString)
            if '您覺得這篇文章' in InforTempString:
                if '1.值得推薦' in InforTempString:
                    AllowPushTypeList[self.PushType_Push] = True
                if '2.給它噓聲' in InforTempString:
                    AllowPushTypeList[self.PushType_Boo] = True
                if '3.只加→註解' in InforTempString:
                    AllowPushTypeList[self.PushType_Arrow] = True
                Pushable = True
                break
            if '使用 → 加註方式' in InforTempString:
                AllowPushTypeList[self.PushType_Arrow] = True
                PushType = self.PushType_Arrow
                ArrowOnly = True
                Pushable = True
                break
            if '本板禁止快速連續推文' in InforTempString:
                PTTTelnetCrawlerLibraryUtil.Log('No fast push, please wait')
                return False
        if not Pushable:
            PTTTelnetCrawlerLibraryUtil.Log('No push option')
            return False
        
        if not AllowPushTypeList[self.PushType_Boo] and PushType == self.PushType_Boo:
            PushType = self.PushType_Arrow
        
        if ArrowOnly:
            self.__sendData(PushContent + '\r\ny\r\n')
        else:
            self.__sendData(PushType + PushContent + '\r\ny\r\n')
        
        return True
    
    def pushByID(self, Board, PostID, PushType, PushContent):
    
        if not self.gotoPostByID(Board, PostID):
            PTTTelnetCrawlerLibraryUtil.Log('Go to post fail')
            return False
        
        if PushType != self.PushType_Push and PushType != self.PushType_Boo and PushType != self.PushType_Arrow:
            PTTTelnetCrawlerLibraryUtil.Log('Not support this push type: ' + str(PushType))
            return False
        
        self.__sendData('X')
        
        Pushable = False
        
        ArrowOnly = False
        
        AllowPushTypeList = [False, False, False, False]
        
        AllowPushTypeList[self.PushType_Push] = False
        AllowPushTypeList[self.PushType_Boo] = False
        AllowPushTypeList[self.PushType_Arrow] = False
        
        for InforTempString in self.__content.split('\r\n'):
            if '您覺得這篇文章' in InforTempString:
                if '1.值得推薦' in InforTempString:
                    AllowPushTypeList[self.PushType_Push] = True
                if '2.給它噓聲' in InforTempString:
                    AllowPushTypeList[self.PushType_Boo] = True
                if '3.只加→註解' in InforTempString:
                    AllowPushTypeList[self.PushType_Arrow] = True
                Pushable = True
                break
            if '使用 → 加註方式' in InforTempString:
                AllowPushTypeList[self.PushType_Arrow] = True
                PushType = self.PushType_Arrow
                ArrowOnly = True
                Pushable = True
                break
            if '本板禁止快速連續推文' in InforTempString:
                PTTTelnetCrawlerLibraryUtil.Log('No fast push, please wait')
                return False
        if not Pushable:
            PTTTelnetCrawlerLibraryUtil.Log('No push option')
            return False
        
        if not AllowPushTypeList[self.PushType_Boo] and PushType == self.PushType_Boo:
            PushType = self.PushType_Arrow
        
        if ArrowOnly:
            self.__sendData(PushContent + '\r\ny\r\n')
        else:
            self.__sendData(PushType + PushContent + '\r\ny\r\n')
        
        return True
    
    def mail(self, UserID, MailTitle, MailContent, SignType):
        
        self.gotoUserMenu()
       
        self.__sendData('M\r\nS\r\n' + UserID + '\r\n')
        
        if not '主題：' in self.__content:
            PTTTelnetCrawlerLibraryUtil.Log('No this PTT user ' + UserID)
            print(self.__content)
            return False
        self.__sendData(MailTitle + '\r\n')
        self.__sendData(MailContent + '\x18')
        
        # 儲存文章
        self.__sendData('s\r\n')
        
        if '請選擇簽名檔' in self.__content:
            self.__sendData(str(SignType) + '\r\n')
        
        if '已順利寄出，是否自存底稿' in self.__content:
            self.__sendData('Y\r\n')
            
        if '任意鍵繼續' in self.__content:
            self.__sendData('\r\n')
            
        return True
    
    def getPostInformationByID(self, Board, PostID):
        
        result = None   
    
        if not self.gotoPostByID(Board, PostID):
            PTTTelnetCrawlerLibraryUtil.Log('Go to post id fail')
            return None

        PostAuthor = ''
        PostTitle = ''
        PostDate = ''
        PostWebUrl = ''
        PostMoney = -1
        PostContent = ''
        
        #Query post information
        self.__sendData('Q', True)
        
        #print('=.= ' + self.__content)
        if not 'https://' in self.__content or not '.html' in self.__content:
            PTTTelnetCrawlerLibraryUtil.Log('Find http fail')
            return None
        PostWebUrl = self.__content[self.__content.find('https://'):self.__content.find('.html')] + '.html'
        
        if not '這一篇文章值' in self.__content:
            PTTTelnetCrawlerLibraryUtil.Log('Find 這一篇文章值 fail')
            return None
        PostMoney = re.search(r'\d+', self.__content[self.__content.find('這一篇文章值'):]).group()
        
        if PostWebUrl == '':
            PTTTelnetCrawlerLibraryUtil.Log('Find PostWebUrl fail')
            return None
        if PostMoney == -1:
            PTTTelnetCrawlerLibraryUtil.Log('Find PostMoney fail')
            return None
        
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        #print(PostWebUrl)
        res = requests.get(
            url = PostWebUrl,
            cookies={'over18': '1'}
        )
        
        soup =  BeautifulSoup(res.text,'html.parser')
        main_content = soup.find(id='main-content')
        
        metas = main_content.select('div.article-metaline')
        filtered = [ v for v in main_content.stripped_strings if v[0] not in ['※', '◆'] and  v[:2] not in ['--'] ]
        
        content = ' '.join(filtered)
        content = re.sub(r'(\s)+', '', content )
        if len(metas) == 0:
            PTTTelnetCrawlerLibraryUtil.Log('div.article-metaline is not exist')
            raise Exception('div.article-metaline is not exist')
            
        author = metas[0].select('span.article-meta-value')[0].string
        title = metas[1].select('span.article-meta-value')[0].string
        date = metas[2].select('span.article-meta-value')[0].string
        
        PostTitle = title
        PostAuthor = author
        PostDate = date
        
        PostContentArea = False
        
        PushArea = False
        
        PushType = 0
        PushID = ''
        PushContent = ''
        PushDate = ''
        PushIndex = 0
        
        PushList = []
        for ContentLine in filtered:
            #print(ContentLine)
            if '推' in ContentLine or '噓' in ContentLine or '→' in ContentLine:
                PushArea = True
            if PushArea:
                if PushIndex == 0:
                    if '推' in ContentLine:
                        PushType = self.PushType_Push
                    elif '噓' in ContentLine:
                        PushType = self.PushType_Boo
                    elif '→' in ContentLine:
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
                    #print(str(PushType) + ' ' + PushID + ' ' + PushContent + ' ' + PushDate)
                    PushList.append(PushInformation(PushType, PushID, PushContent, PushDate))
            if date == ContentLine:
                PostContentArea = True
                continue
            if PostWebUrl == ContentLine or '推' in ContentLine or '噓' in ContentLine or '→' in ContentLine:
                PostContentArea = False
            if PostContentArea:
                PostContent += ContentLine + '\r\n'
        
        if PostTitle == '':
            PTTTelnetCrawlerLibraryUtil.Log('Find PostTitle fail')
            return None
        if PostAuthor == '':
            PTTTelnetCrawlerLibraryUtil.Log('Find PostAuthor fail')
            return None
        if PostDate == '':
            PTTTelnetCrawlerLibraryUtil.Log('Find PostDate fail')
            return None
        
        if '請按任意鍵繼續' in self.__content:
            self.__sendData('\r\n')
        result = PostInformation(Board, PostID, PostAuthor, PostDate, PostTitle, PostWebUrl, PostMoney, PostContent, PushList, res.text)

        return result
    
    def getPostInformationByIndex(self, Board, Index):
        for i in range(5):
            try:
                result = self.__getPostInformationByIndex(Board, Index)
                if result != None:
                    return result
            except Exception:
                return None
            time.sleep(self.__CurrentSleepTime / 100)
        return None
    def __getPostInformationByIndex(self, Board, Index):
    
        if not self.gotoPostByIndex(Board, Index):
            PTTTelnetCrawlerLibraryUtil.Log('Go to post index fail')
            raise Exception('This post has been deleted..')
        
        PostID = ''
        
        for i in range(3):
            self.__sendData('Q')
            for InforTempString in self.__content.split('\r\n'):
                if '│ 文章代碼(AID): #' in InforTempString:
                    PostID = InforTempString.replace('│ 文章代碼(AID): #', '')
                    PostID = PostID[0 : PostID.find(' ')].replace('\x1b[m', '')
                    break
                if '請按任意鍵繼續' in self.__content:
                    self.__sendData('\r\n')
            if PostID != '':
                break
        if PostID == '':
            PTTTelnetCrawlerLibraryUtil.Log('This post has been deleted...')
            raise Exception('This post has been deleted...')
        result = self.getPostInformationByID(Board, PostID)

        return result
    
    def getNewestPostIndex(self, Board):
        for i in range(20):
            result = self.__getNewestPostIndex(Board)
            if not result == -1:
                return result
            time.sleep(self.__CurrentSleepTime / 100)
        return -1
    def __getNewestPostIndex(self, Board):
        result = -1
        if not self.gotoBoard(Board):
            PTTTelnetCrawlerLibraryUtil.Log('Goto ' + Board + ' fail')
            return result
        
        self.__sendData('$')
        #print(self.__content)
        DetectRange = 30
        
        Line = 0
        GoUp = False
        
        if '>   ★' in self.__content:
            GoUp = True
        #else:
            #print(self.__content)
            #print(str(len(self.__content)))
        
        while GoUp:
            self.__sendData('\x1b[A')
            
            if not '>' in self.__content:
                result = -1
                break
            if '>   ★' in self.__content:
                continue
            
            self.__content = self.__content[self.__content.find('>'):]
            #print(self.__content)
            if '★' in self.__content:
                self.__content = self.__content[:self.__content.find('★')]
            
            if '看板《' + Board + '》' in self.__content:
                result = -1
                break
            
            try:
                #print(self.__content)
                result = int(re.search(r'\d+', self.__content).group())
            except AttributeError:
                result = -1
            break
        
        try:
            LastNewestPostIndexTemp = self.__LastNewestPostIndex[Board]
        except KeyError:
            self.__LastNewestPostIndex[Board] = -1
            
        #print('result: ' + str(result))
        #print('[Board]: ' + str(self.__LastNewestPostIndex[Board]))
            
        if result != -1 and self.__LastNewestPostIndex[Board] != -1:
            for i in range(10, -10, -1):
                if (self.__LastNewestPostIndex[Board] + i) == result:
                    if self.gotoPostByIndex(Board, result):
                        self.__LastNewestPostIndex[Board] = result
                        return result
        if (result != self.__LastNewestPostIndex[Board] or result == -1) and self.__LastNewestPostIndex[Board] != -1:
            #print('Execute recover mode')
            
            NewResult = result
            
            for ResultTempIndex in range(3, -4, -1):
                if self.gotoPostByIndex(Board, self.__LastNewestPostIndex[Board] + ResultTempIndex):
                    NewResult = self.__LastNewestPostIndex[Board] + ResultTempIndex
                    break
            
            
            
            if NewResult != result:
                if result == -1:
                    #PTTTelnetCrawlerLibraryUtil.Log('!!!Detect error recover mode: correct result to ' + str(NewResult))
                    pass
                else:
                    #PTTTelnetCrawlerLibraryUtil.Log('!!!Check new index: correct result to ' + str(NewResult))
                    pass
                result = NewResult
            else:
                if result == -1:
                    result = self.__LastNewestPostIndex[Board]
                else:
                    pass
        if result != -1:
            self.__LastNewestPostIndex[Board] = result
        else:
            #PTTTelnetCrawlerLibraryUtil.Log('Execute recover mode fail')
            pass
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
        
        self.__sendData('P\r\n', True)
        
        if not '量販店' in self.__content:
            print(self.__content)
            PTTTelnetCrawlerLibraryUtil.Log('Go to Play fail')
            return False
        
        self.__sendData('P\r\n', True)
        
        if not '給其他人Ptt幣' in self.__content :
            print(self.__content)
            PTTTelnetCrawlerLibraryUtil.Log('Go to Pay fail')
            return False
        
        self.__sendData('0\r\n', True)
        
        if not '這位幸運兒的id' in self.__content :
            print(self.__content)
            PTTTelnetCrawlerLibraryUtil.Log('Pay fail')
            return False
        
        self.__sendData(ID + '\r\n', True)
        
        if not '請輸入金額' in self.__content :
            print(self.__content)
            PTTTelnetCrawlerLibraryUtil.Log('Input ID fail')
            return False
        
        self.__sendData('\t')
        
        self.__sendData(str(Money) + '\r\n', True, 3)
        
        if '請輸入您的密碼' in self.__content :
            self.__sendData(YourPassword + '\r\n')
        
        while not '按任意鍵繼續' in self.__content:
            if '要修改紅包袋嗎' in self.__content:
                self.__sendData('n\r\n')
            if '確定進行交易嗎' in self.__content :
                self.__sendData('y\r\n')
            self.__waitResponse()
        
        self.__sendData('\r\n')
        return True
    def getTime(self):
    
        self.gotoUserMenu()
        
        if not 'oodbye離開，再見…' in self.__content:
            return ''
        self.__content = self.__content[self.__content.find('oodbye離開，再見…'):]
        
        if not '[' in self.__content:
            return ''
        self.__content = self.__content[self.__content.find('['):]
        
        print(self.__content)
        
        if not ']' in self.__content:
            return ''
        self.__content = self.__content[:self.__content.find(']')]
        
        
        
        print(self.__content)
        print(len(self.__content))
        print('[' in self.__content)
        MarkList = [m.start() for m in re.finditer('[', self.__content)]
        
        if len(MarkList) < 3:
            PTTTelnetCrawlerLibraryUtil.Log('Parse time error')
            return ''
        print(MarkList)
        self.__content = self.__content[MarkList[len(MarkList) - 3]: ]
        print(self.__content)
        
if __name__ == '__main__':

    print('PTT Telnet Crawler Library v 0.1.170604')
    print('PTT CodingMan')
