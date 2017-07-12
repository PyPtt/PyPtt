import sys
import telnetlib
import time
import re
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import PTTUtil
import threading

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class UserInformation(object):
    def __init__(self, UserID, UserMoney, UserLoginTime, UserPost, UserState, UserMail, UserLastLogin, UserLastIP, UserFiveChess, UserChess):
        self.__UserID = str(UserID)
        self.__UserMoney = str(UserMoney)
        self.__UserLoginTime = int(UserLoginTime)
        self.__UserPost = int(UserPost)
        self.__UserState = str(UserState)
        self.__UserMail = str(UserMail)
        self.__UserLastLogin = str(UserLastLogin)
        self.__UserLastIP = str(UserLastIP)
        self.__UserFiveChess = str(UserFiveChess)
        self.__UserChess = str(UserChess)
    def getID(self):
        return self.__UserID
    def getMoney(self):
        return self.__UserMoney
    def getLoginTime(self):
        return self.__UserLoginTime
    def getPost(self):
        return self.__UserPost
    def getState(self):
        return self.__UserState
    def getMail(self):
        return self.__UserMail
    def getLastLogin(self):
        return self.__UserLastLogin
    def getLastIP(self):
        return self.__UserLastIP
    def getFiveChess(self):
        return self.__UserFiveChess
    def getChess(self):
        return self.__UserChess
        
class PushInformation(object):
    def __init__(self, PushType, PushID, PushContent, PushTime):
        self.__PushType = int(PushType)
        self.__PushID = str(PushID)
        self.__PushContent = str(PushContent)
        self.__PushTime = str(PushTime)
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
        self.__Board = str(Board)
        self.__PostID = str(PostID)
        self.__Author = str(Author)
        self.__Date = str(Date)
        self.__Title = str(Title)
        self.__PostContent = str(PostContent)
        self.__Money = Money
        self.__WebUrl = str(WebUrl)
        self.__PushList = PushList
        self.__OriginalData = str(OriginalData)

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
    
class Crawler(object):
    def __init__(self, ID, Password, kickOtherLogin, LogLevel=-1):
 
        self.__host = 'ptt.cc'
        self.__ID = ID
        self.__Password = Password
        self.__kickOtherLogin = kickOtherLogin
        self.__ReceiveData = ''
        self.__isConnected = False
        
        
        
        self.Success =                          0
        self.UnknowError =                    0.1
        self.ConnectError =                     1
        self.EOFErrorCode =                     2
        self.ConnectResetError =                3
        self.WaitTimeout =                      4
        self.WrongPassword =                    5
        self.ErrorInput =                       6
        self.PostNotFound =                     7
        self.ParseError =                       8
        self.PostDeleted =                      9
        self.WebFormatError =                  10
        self.NoPermission =                    11
        self.NoUser =                          12

        self.PushType_Push =                    1
        self.PushType_Boo =                     2
        self.PushType_Arrow =                   3

        self.LogLevel_DEBUG =                   1
        self.LogLevel_WARNING =                 2
        self.LogLevel_RELEASE =                 3
        self.LogLevel_CRITICAL =                4
        self.LogLevel_SLIENT =                  5
        
        self.__LogLevel = self.LogLevel_RELEASE
        
        if LogLevel != -1:
            if LogLevel < self.LogLevel_DEBUG or self.LogLevel_SLIENT < LogLevel:
                self.Log('LogLevel error: ' + str(LogLevel))
                return None
            else:
                self.__LogLevel = LogLevel
        
        self.__SleepTime =                    0.5
        self.__DefaultTimeout =                 1
        self.__Timeout =                       10
        self.__CurrentTimeout =                 0
        
        self.__Cursor =                       '>'
        
        self.__KickTimes =                      0
        
        self.__MaxMultiLoing =                  4
        
        self.__TelnetConnectList = [None] * self.__MaxMultiLoing
        
        self.Log('ID: ' + ID)
        TempPW = ''

        for i in range(len(Password)):
            TempPW += '*'
        
        self.Log('Password: ' + TempPW)
        if kickOtherLogin:
            self.Log('This connection will KICK other login')
        else :
            self.Log('This connection will NOT kick other login')
        
        self.__connectRemote(0)
        
    def setLogLevel(self, LogLevel):
        if LogLevel < self.LogLevel_DEBUG or self.LogLevel_SLIENT < LogLevel:
            self.Log('LogLevel error')
            return self.ErrorInput
        self.__LogLevel = LogLevel
        return self.Success
    def Log(self, Message, LogLevel=-1):
        if LogLevel == -1:
            LogLevel = self.LogLevel_RELEASE
        if LogLevel < self.LogLevel_DEBUG or self.LogLevel_SLIENT < LogLevel:
            self.Log('LogLevel error')
            return self.ErrorInput
        if self.__LogLevel <= LogLevel:
            PTTUtil.Log(Message)
        return self.Success
    def isLoginSuccess(self):
        return self.__isConnected
    def __readScreen(self, TelnetConnectIndex, Message='', ExpectTarget=[]):
        
        self.Log('__readScreen: into function', self.LogLevel_DEBUG)
        if ExpectTarget == None:
            ExpectTarget = []
        
        self.Log('__readScreen: into function', self.LogLevel_DEBUG)
        if ExpectTarget == None:
            ExpectTarget = []
        
        result = -1
        ErrorCode = self.UnknowError
        
        ReceiveTimes = 0
        self.__Timeouted = False
        self.__ReceiveData = ''
        
        if self.__CurrentTimeout == 0:
            self.__Timeout = self.__DefaultTimeout
        else:
            self.__Timeout = self.__CurrentTimeout
        
        try:
            self.__TelnetConnectList[TelnetConnectIndex].read_very_eager()
            self.__TelnetConnectList[TelnetConnectIndex].write(str(Message + '\x0C').encode('big5'))
            StartTime = time.time()
            
            while True:
                time.sleep(self.__SleepTime)
                ReceiveTimes += 1
                
                self.__ReceiveData += self.__TelnetConnectList[TelnetConnectIndex].read_very_eager().decode('big5', 'ignore')
                
                DataMacthed = False
                for i in range(len(ExpectTarget)):
                
                    if ExpectTarget[i] in self.__ReceiveData:
                        result = i
                        DataMacthed = True
                        break
                
                if DataMacthed:
                    ErrorCode = self.Success
                    break
                
                NowTime = time.time()
                
                if NowTime - StartTime > self.__Timeout:
                    self.__Timeouted = True
                    ErrorCode = self.WaitTimeout
                    break
        except ConnectionResetError:
            PTTUtil.Log('Remote reset connection...')
            self.__connectRemote(True)
            return self.ConnectResetError, result
        except EOFError:
            PTTUtil.Log('Remote kick connection...')
            self.__connectRemote(True)
            self.__CurrentTimeout = 0
            return self.EOFErrorCode, result
        
        self.__SleepTime = self.__SleepTime * (ReceiveTimes / 5.0)
        self.__CurrentTimeout = 0
        return ErrorCode, result
    
    def __checkState(self):
        if not self.__isConnected:
            return False
        if self.__KickTimes > 5:
            return False
        return True
    def __showScreen(self, ExpectTarget=[]):
        self.__readScreen('', ExpectTarget)
        if self.__LogLevel == self.LogLevel_DEBUG:
            print(self.__ReceiveData)
    def __sendData(self, TelnetConnectIndex, Message, CaseList=[], Enter=True, Refresh=False):
        
        if Message == None:
            Message = ''
        if CaseList == None:
            CaseList = []
        
        self.__ReceiveData = ''
        
        ReceiveTimes = 0
        PostFix = ''
        
        if Enter:
            PostFix += '\r'
        if Refresh:
            PostFix += '\x0C'
        for i in range(len(CaseList)):
            if type(CaseList[i]) is str:
                CaseList[i] = CaseList[i].encode('big5')
        
        if self.__isConnected:
            if self.__CurrentTimeout == 0:
                self.__Timeout = self.__DefaultTimeout
            else:
                self.__Timeout = self.__CurrentTimeout
        else:
            self.__Timeout = 10
        
        try:

            SendMessage = str(Message) + PostFix
            self.__TelnetConnectList[TelnetConnectIndex].read_very_eager()
            self.__TelnetConnectList[TelnetConnectIndex].write(SendMessage.encode('big5'))
            ReturnIndex = self.__TelnetConnectList[TelnetConnectIndex].expect(CaseList, timeout=self.__Timeout)[0]

        except EOFError:
            #QQ why kick me
            PTTUtil.Log('Remote kick connection...')
            self.__connectRemote(True)
            self.__CurrentTimeout = 0
            return self.EOFErrorCode, -1
        except ConnectionResetError:
            PTTUtil.Log('Remote reset connection...')
            self.__connectRemote(True)
            self.__CurrentTimeout = 0
            return self.ConnectResetError, -1
        
        if ReturnIndex == -1:
            self.Log('Send data timeout', self.LogLevel_DEBUG)
            self.__CurrentTimeout = 0
            return self.WaitTimeout, ReturnIndex
        self.__CurrentTimeout = 0
        return self.Success, ReturnIndex
    def __connectRemote(self, TelnetConnectIndex, Recovery=False):
        self.__isConnected = False
        
        while True:
            while True:
                try:
                    self.__TelnetConnectList[TelnetConnectIndex] = telnetlib.Telnet(self.__host)
                    break
                except ConnectionRefusedError:
                    self.Log('Connect to ' + self.__host + ' fail, retry 1 sec later', self.LogLevel_RELEASE)
                    time.sleep(1)
            ErrorCode, Index = self.__sendData(TelnetConnectIndex, '', ['請輸入代號', '系統過載'], False)
            if ErrorCode != self.Success:
                return ErrorCode
            if Index == 0:
                if not Recovery:
                    self.Log('Connect Success')
                break
            if Index == 1:
                self.Log('System overload')
                time.sleep(2)
            
        CaseList = ['密碼不對', '您想刪除其他重複登入', '按任意鍵繼續', '您要刪除以上錯誤嘗試', '您有一篇文章尚未完成', '請輸入您的密碼', '編特別名單', '正在更新']
        SendMessage = self.__ID
        Enter = True
        
        while True:
            ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode != self.Success:
                return ErrorCode
            if Index == 0:
                self.Log('Wrong password')
                return self.WrongPassword
            if Index == 1:
                if self.__kickOtherLogin:
                    SendMessage = 'y'
                    Enter = True
                    if not Recovery:
                        self.Log('Detect other login')
                        self.Log('Kick other login Success')
                else :
                    SendMessage = 'n'
                    Enter = True
                    if not Recovery:
                        self.Log('Detect other login')
            if Index == 2:
                SendMessage = 'q'
                Enter = False
                if not Recovery:
                    self.Log('Press any key to continue')
            if Index == 3:
                SendMessage = 'Y'
                Enter = True
                if not Recovery:
                    self.Log('Delete error password log')
            if Index == 4:
                SendMessage = 'q'
                Enter = True
                if not Recovery:
                    self.Log('Delete the post not finished')    
            if Index == 5:
                SendMessage = self.__Password
                Enter = True
                if not Recovery:
                    self.Log('Input ID Success')
            if Index == 6:
                if not Recovery:
                    self.Log('Login Success')
                break
            if Index == 7:
                SendMessage = ''
                Enter = True
                if not Recovery:
                    self.Log('Wait update')
                time.sleep(1)
        
        ErrorCode, Index = self.__readScreen(TelnetConnectIndex, '', ['> (', '●('])
        if ErrorCode != self.Success:
            self.Log(self.__ReceiveData)
            self.Log('Detect cursor fail ErrorCode: ' + str(ErrorCode))
            return ErrorCode
        if Index == 0:
            self.__Cursor = '>'
        if Index == 1:
            self.__Cursor = '●'
        
        if Recovery:
            self.Log('Recover connection success')
        self.__isConnected = True
        '''
        BoardList = ['Wanted', 'Gossiping', 'Test', 'Python']
        
        i = 0
        
        for Board in BoardList:
            ErrorCode, NewestIndex = self.getNewestPostIndex(Board)
            if ErrorCode == self.Success:
                self.Log('Detect network environment: ' + str(int(((i + 1) * 100) / len(BoardList))) + ' % ')
            else:
                self.Log('Detect network environment: ' + str(int(((i + 1) * 100) / len(BoardList))) + ' % ' + ' fail')
                return False
            i+=1
        '''
        return self.Success
        
    def __gotoTop(self, TelnetConnectListIndex):
        for i in range(3):
            ErrorCode = self.___gotoTop(TelnetConnectListIndex)
            if ErrorCode == self.Success:
                if i != 0:
                    self.Log('__gotoTop recover Success', self.LogLevel_DEBUG)
                break
        return ErrorCode
    def ___gotoTop(self, TelnetConnectListIndex):
        
        self.__CurrentTimeout = 3
        ErrorCode, Index = self.__sendData(TelnetConnectListIndex, 'q\x1b[D\x1b[D\x1b[D\x1b[D', ['[呼叫器]', '編特別名單', '娛樂與休閒', '系統資訊區', '主功能表', '私人信件區'], False, True)
        if ErrorCode != self.Success:
            return ErrorCode
        return self.Success
    def logout(self):
        
        for index in range(self.__MaxMultiLoing):
            
            if self.__TelnetConnectList[index] == None:
                continue
            
            ErrorCode = self.__gotoTop(index)
            if ErrorCode != self.Success:
                self.Log('Error code 1: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode
            ErrorCode, Index = self.__readScreen(index, 'g\ry\r', ['[按任意鍵繼續]'])
            self.__TelnetConnectList[0].close()
            self.Log('Connection ' + str(index) + ' logout Success')
        
        return self.Success
    def __gotoBoard(self, Board, TelentConnectIndex = 0):
        for i in range(5):
            ErrorCode = self.___gotoBoard(Board, TelentConnectIndex)
            if ErrorCode == self.Success:
                if i != 0:
                    self.Log('GotoBoard recover Success', self.LogLevel_DEBUG)
                break
                
        return ErrorCode
    def ___gotoBoard(self, Board, TelentConnectIndex):
        ErrorCode = self.__gotoTop(TelentConnectIndex)
        if ErrorCode != self.Success:
            self.Log('Error code __gotoBoard 1: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode
        CaseList = ['請輸入看板名稱']
        SendMessage = 's'
        
        self.__CurrentTimeout = 5
        
        ErrorCode, Index = self.__sendData(TelentConnectIndex, SendMessage, CaseList, False)
        if ErrorCode != self.Success:
            self.Log('Error code __gotoBoard 2: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode
        
        #self.__showScreen()
        CaseList = ['請按任意鍵繼續', '其他任意鍵停止', '動畫播放中', '文章選讀']
        SendMessage = Board
        Enter = True
        
        MaxTry, TryTime = 5, 0
        while True:            
            ErrorCode, Index = self.__sendData(TelentConnectIndex, SendMessage, CaseList, Enter)
            #self.Log('GotoBoard index: ' + str(Index), self.LogLevel_DEBUG)
            if ErrorCode != self.Success:
                self.__showScreen()
                self.Log('Error code __gotoBoard 3: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode
            if Index == 0 or Index == 1 or Index == 2:
                SendMessage = 'q'
                Enter = False
            if Index == 3:
                break
            TryTime += 1
            if TryTime > MaxTry:
                self.Log('___gotoBoard while too many times', self.LogLevel_DEBUG)
                return self.WaitTimeout
        #print('--------------------------------------------------------')
        #self.__showScreen()
        return self.Success
    
    def post(self, board, title, content, PostType, SignType, TelentConnectIndex = 0):
        
        self.__CurrentTimeout = 10
        
        ErrorCode = self.__gotoBoard(board)
        if ErrorCode != self.Success:
            self.Log('post 1 Go to ' + board + ' fail', self.LogLevel_DEBUG)
            return ErrorCode
        
        CaseList = ['1-8或不選', '使用者不可發言']
        SendMessage = '\x10'
        
        ErrorCode, Index = self.__sendData(TelentConnectIndex, SendMessage, CaseList, False)
        if ErrorCode != self.Success:
            self.Log('post 2 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode
        
        if Index == 1:
            self.Log('You are in the bucket QQ')
            return self.NoPermission
        
        CaseList = ['標題']
        SendMessage = str(PostType)
        
        ErrorCode, Index = self.__sendData(TelentConnectIndex, SendMessage, CaseList)
        if ErrorCode != self.Success:
            self.Log('post 3 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode
        
        CaseList = ['編輯文章']
        SendMessage = title
        
        ErrorCode, Index = self.__sendData(TelentConnectIndex, SendMessage, CaseList)
        if ErrorCode != self.Success:
            
            self.Log('post 4 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode
        
        CaseList = ['確定要儲存檔案嗎']
        SendMessage = content + '\x18'
        
        ErrorCode, Index = self.__sendData(TelentConnectIndex, SendMessage, CaseList, False)
        if ErrorCode != self.Success:
            self.Log('post 5 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode
        
        self.__CurrentTimeout = 10
        
        CaseList = ['x=隨機', '請按任意鍵繼續', '看板《' + board + '》']
        SendMessage = 's'
        Enter = True
        Refresh = False
        while True:        
            ErrorCode, Index = self.__sendData(TelentConnectIndex, SendMessage, CaseList, Enter, Refresh)
            if ErrorCode != self.Success:
                self.__showScreen()
                self.Log('post 6 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode
            if Index == 0:
                SendMessage = str(SignType)
                Enter = True
                Refresh = False
            if Index == 1:
                SendMessage = 'q'
                Enter = False
                Refresh = False
            if Index == 2:
                #self.Log('Post Success')
                break
                
        return self.Success
    
    def getNewestPostIndex(self, Board, TelentConnectIndex = 0):
        
        TryTime = 0
        
        for i in range(3):
            ErrorCode, Index = self.__getNewestPostIndex(Board, TelentConnectIndex)
            TryTime += 1
            if ErrorCode == self.Success:
                if i != 0:
                    self.Log('getNewestPostIndex try ' + str(i + 1) + ' ecovery Success', self.LogLevel_DEBUG)
                break
            elif ErrorCode == self.ParseError:
                self.Log('getNewestPostIndex parse error retry..', self.LogLevel_DEBUG)
                pass
            elif ErrorCode == self.WaitTimeout:
                self.Log('getNewestPostIndex time out retry..', self.LogLevel_DEBUG)
                pass
            else:
                self.Log('ErrorCode: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode, Index
            time.sleep(self.__SleepTime)
        
        #self.Log('TryTime: ' + str(TryTime))
        return ErrorCode, Index
    def __getNewestPostIndex(self, Board, TelentConnectIndex = 0):
        ReturnIndex = -1
    
        ErrorCode = self.__gotoBoard(Board, TelentConnectIndex)
        if ErrorCode != self.Success:
            self.Log('getNewestPostIndex 1 Go to ' + Board + ' fail', self.LogLevel_DEBUG)
            return ErrorCode, -1
        
        
        self.__CurrentTimeout = 3
        self.__readScreen(TelentConnectIndex, '0\r$', ['★'])
        if ErrorCode == self.WaitTimeout:
            #self.Log('getNewestPostIndex 2.1 error code: ' + str(ErrorCode))
            #print(self.__ReceiveData)
            return ErrorCode, -1

        AllIndex = re.findall(r'\d+ ', self.__ReceiveData)
        
        AllIndex = list(set(map(int, AllIndex)))
        AllIndex.sort()
        
        if len(AllIndex) == 0:
            self.Log('self.ParseError type 1', self.LogLevel_DEBUG)
            return self.ParseError, -1
        
        AllIndexTemp = list(AllIndex)
        
        while True:
            
            ReturnIndexTemp = AllIndex.pop()
            
            if len(str(ReturnIndexTemp)) <= 6:

                HasFront = True
                HasBack = True
                
                DetectRange = 5
                '''
                print(AllIndexTemp)
                print(str(ReturnIndexTemp))
                '''
                for i in range(DetectRange):
                    if not (ReturnIndexTemp - i) in AllIndexTemp:
                        HasFront = False
                        break
                
                for i in range(DetectRange):
                    if not (ReturnIndexTemp + i) in AllIndexTemp:
                        HasBack = False
                        break
                
                if HasFront or HasBack:
                    ReturnIndex = ReturnIndexTemp
                    break
            if len(AllIndex) == 0:
                self.Log('self.ParseError type 2: ' + str(AllIndexTemp), self.LogLevel_DEBUG)
                #self.Log(self.__ReceiveData, self.LogLevel_DEBUG)
                return self.ParseError, -1
        return self.Success, int(ReturnIndex)
    
    def __gotoPostByIndex(self, Board, PostIndex, TelnetConnectIndex = 0):
        for i in range(3):
            ErrorCode = self.___gotoPostByIndex(Board, PostIndex, TelnetConnectIndex)
            if ErrorCode == self.Success:
                if i != 0:
                    self.Log('GotoPostByIndex try ' + str(i + 1) + ' recover Success', self.LogLevel_DEBUG)
                break
        return ErrorCode
    def ___gotoPostByIndex(self, Board, PostIndex, TelnetConnectIndex = 0):
    
        ErrorCode = self.__gotoBoard(Board)
        if ErrorCode != self.Success:
            self.Log('__gotoPostByIndex 1 Go to ' + Board + ' fail', self.LogLevel_DEBUG)
            self.__showScreen()
            return ErrorCode
            
        if self.__Cursor == '>':
            IndexTarget = '>{0: >6}'.format(str(PostIndex))
        else:
            IndexTargetTemp = str(PostIndex)
            if len(IndexTargetTemp) == 6:
                IndexTargetTemp = IndexTargetTemp[1:]
            IndexTarget = self.__Cursor + '{0: >5}'.format(IndexTargetTemp)
            
        self.__CurrentTimeout = 5
        
        self.__readScreen(TelnetConnectIndex, str(PostIndex) + '\r', [IndexTarget])
        
        if IndexTarget in self.__ReceiveData:
            return self.Success
        else:
            #print(self.__ReceiveData)
            return self.PostNotFound
    def __gotoPostByID(self, Board, PostID, TelentConnectIndex = 0):
        self.Log('Into __gotoPostByID', self.LogLevel_DEBUG)
        ErrorCode = self.__gotoBoard(Board, TelentConnectIndex)
        if ErrorCode != self.Success:
            self.Log('__gotoPostByID 1 Go to ' + Board + ' fail', self.LogLevel_DEBUG)
            return ErrorCode
        
        self.__readScreen(TelentConnectIndex, '#' + PostID + '\r', '文章選讀')
        
        if '找不到這個文章代碼' in self.__ReceiveData:
            return self.PostNotFound
        
        return self.Success
        
    def getPostInfoByID(self, Board, PostID, Index=-1, TelentConnectIndex = 0):
        self.Log('Into getPostInfoByID', self.LogLevel_DEBUG)
        for i in range(5):
            ErrorCode, Post = self.__getPostInfoByID(Board, PostID, Index, TelentConnectIndex)
            if ErrorCode == self.Success:
                if i != 0:
                    self.Log('getPostInfoByID recover Success', self.LogLevel_DEBUG)
                break
            if ErrorCode == self.WebFormatError:
                break
            if ErrorCode == self.PostDeleted:
                break
        return ErrorCode, Post
        
    def __getPostinfoByUrl(self, WebUrl):
    
        self.Log('__getPostinfoByUrl: requests get', self.LogLevel_DEBUG)
        for i in range(5):
            try:
                res = requests.get(
                    url = WebUrl,
                    cookies={'over18': '1'},
                    timeout=3
                )
                break
            except requests.exceptions.Timeout:
                self.Log('__getPostinfoByUrl: requests time out', self.LogLevel_DEBUG)
            except requests.exceptions.ConnectionError:
                self.Log('__getPostinfoByUrl: requests conect error', self.LogLevel_DEBUG)
        soup =  BeautifulSoup(res.text, 'html.parser')
        main_content = soup.find(id='main-content')
        
        if main_content == None:
            return self.WebFormatError, '', '', '', '', None, ''

        metas = main_content.select('div.article-metaline')
        filtered = [ v for v in main_content.stripped_strings if v[0] not in ['※', '◆'] and  v[:2] not in ['--'] ]
        
        content = ' '.join(filtered)
        content = re.sub(r'(\s)+', '', content )

        try:
            author = metas[0].select('span.article-meta-value')[0].string
            title = metas[1].select('span.article-meta-value')[0].string
            date = metas[2].select('span.article-meta-value')[0].string
        except IndexError:
            self.Log('div.article-metaline is not exist', self.LogLevel_DEBUG)
            return self.WebFormatError, '', '', '', '', None, ''
        RealPostTitle = title
        RealPostAuthor = author
        RealPostDate = date
        RealPostContent = ''
        PostContentArea = False
        
        PushArea = False
        
        PushType = 0
        PushID = ''
        PushContent = ''
        PushDate = ''
        PushIndex = 0
        
        RealPushList = []
        for ContentLine in filtered:
            self.Log('ContentLine-> ' + ContentLine, self.LogLevel_DEBUG)
            if not PostContentArea and (ContentLine.startswith('推') or ContentLine.startswith('噓') or ContentLine.startswith('→')):
                PushArea = True
                PushIndex = 0
            if PushArea:
                if PushIndex == 0:
                    if '推' in ContentLine:
                        PushType = self.PushType_Push
                    elif '噓' in ContentLine:
                        PushType = self.PushType_Boo
                    elif '→' in ContentLine:
                        PushType = self.PushType_Arrow
                    self.Log('PushType-> ' + str(PushType), self.LogLevel_DEBUG)
                if PushIndex == 1:
                    PushID = ContentLine
                if PushIndex == 2:
                    PushContent = ContentLine[2:]
                if PushIndex == 3:
                    PushDate = ContentLine
                    PushArea = False
                PushIndex += 1
                
                if PushIndex >=4:
                    PushIndex = 0
                    self.Log('Push final-> ' + str(PushType) + ' ' + PushID + ' ' + PushContent + ' ' + PushDate, self.LogLevel_DEBUG)
                    RealPushList.append(PushInformation(PushType, PushID, PushContent, PushDate))
            if date in ContentLine:
                PostContentArea = True
                continue
            if WebUrl in ContentLine:
                PostContentArea = False
            if PostContentArea:
                RealPostContent += ContentLine + '\r'
        
        return self.Success, RealPostTitle, RealPostAuthor, RealPostDate, RealPostContent, RealPushList, res.text
    def __getPostInfoByID(self, Board, PostID, Index=-1, TelentConnectIndex = 0):
        self.Log('Into __getPostInfoByID', self.LogLevel_DEBUG)
        if Index != -1:
            self.Log('Into __gotoPostByIndex', self.LogLevel_DEBUG)
            ErrorCode = self.__gotoPostByIndex(Board, Index, TelentConnectIndex)
            if ErrorCode != self.Success:
                self.Log('getPostInfoByIndex 1 goto post fail', self.LogLevel_DEBUG)
                return ErrorCode, None
        else:
            self.Log('Into __gotoPostByID', self.LogLevel_DEBUG)
            if len(PostID) != 8:
                self.Log('Error input: ' + PostID)
                return self.ErrorInput, None
        
            ErrorCode = self.__gotoPostByID(Board, PostID, TelentConnectIndex)
            if ErrorCode != self.Success:
                self.Log('getPostInfoByID 1 goto post fail', self.LogLevel_DEBUG)
                return ErrorCode, None
        
        ErrorCode, Index = self.__readScreen(TelentConnectIndex, 'Q', ['請按任意鍵繼續'])
        if ErrorCode == self.WaitTimeout:
            return self.PostDeleted, None
        if ErrorCode != self.Success:
            self.Log('getPostInfoByID 3 read screen error: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode, None
        
        if Index == 0:
            #Get query screen self.Success
            pass

        RealPostID = ''
        RealWebUrl = ''
        RealMoney = -1
        
        if Index == -1:
            RealPostID = PostID
            
        else:
            if '#' in self.__ReceiveData:
                RealPostID = self.__ReceiveData[self.__ReceiveData.find('#') + 1:]
                RealPostID = RealPostID[:RealPostID.find(' ')]
            else:
                self.Log('Find PostID fail')
                return self.ParseError, None
        
        if 'https' in self.__ReceiveData:
            RealWebUrl = self.__ReceiveData[self.__ReceiveData.find('https'):self.__ReceiveData.find('.html') + 5]
        else:
            self.Log('Find weburl fail')
            return self.ParseError, None
        
        if '這一篇文章值' in self.__ReceiveData:
            RealMoneyTemp = self.__ReceiveData[self.__ReceiveData.find('這一篇文章值') + len('這一篇文章值') : self.__ReceiveData.find('Ptt幣')]
            RealMoney = int(re.search(r'\d+', RealMoneyTemp).group())
        else:
            self.Log('Find post money fail')
            return self.ParseError, None
        '''
        print('RealWebUrl ' + RealWebUrl)
        print('RealPostID ' + RealPostID)
        print('RealMoney ' + str(RealMoney))
        '''
        
        ErrorCode, RealPostTitle, RealPostAuthor, RealPostDate, RealPostContent, RealPushList, OriginalText = self.__getPostinfoByUrl(RealWebUrl)
        if ErrorCode != self.Success:
            return ErrorCode, None
        #######################
        '''
        print('RealPostTitle ' + RealPostTitle)
        print('RealPostAuthor ' + RealPostAuthor)
        print('RealPostDate ' + RealPostDate)
        print('RealPostContent ' + RealPostContent)
        '''
        result = PostInformation(Board, RealPostID, RealPostAuthor, RealPostDate, RealPostTitle, RealWebUrl, RealMoney, RealPostContent, RealPushList, OriginalText)
        
        return self.Success, result
        
    def crawlThread(self, ThreadIndex, Board):
        
        self.Log('Start thread ' + str(ThreadIndex), self.LogLevel_DEBUG)
        
        while self.__ThreadRunning:
            if len(self.__CrawPool) == 0:
                time.sleep(0.97)
                continue
            Index, WebUrl = self.__CrawPool.pop()
            self.Log('Thread ' + str(ThreadIndex) + ': ' + str(Index) + ' ' + WebUrl, self.LogLevel_DEBUG)
            
            ErrorCode, RealPostTitle, RealPostAuthor, RealPostDate, RealPostContent, RealPushList, OriginalText = self.__getPostinfoByUrl(WebUrl)
            
            if ErrorCode != self.Success:
                #self.Log()
                continue
            self.Log('Thread ' + str(ThreadIndex) + ': ' + str(Index) + ' ' + RealPostTitle)
        self.Log('Thread ' + str(ThreadIndex) + ' finish', self.LogLevel_DEBUG)
    def crawlBoard(self, Board, StartIndex=0, EndIndex=0, DefaultThreadNumber=512):
        
        self.Log('Into crawlBoard', self.LogLevel_DEBUG)
        
        if StartIndex == 0 and EndIndex == 0:
            self.Log('Crawl ' + Board + ' all posts')
            
            ErrorCode, EndIndex = self.getNewestPostIndex(Board)
            if ErrorCode == self.Success:
                #self.Log('Get ' + Board + ' get newest post index success: ' + str(EndIndex))
                pass
            else:
                self.Log('Get ' + Board + ' get newest post index fail')
                return self.UnknowError
        else:
            if EndIndex < StartIndex:
                self.Log('EndIndex must bigger than  StartIndex')
                return self.ErrorInput
        #Login All
        self.Log('Multi login mode')
        
        for i in range(1, self.__MaxMultiLoing):
            self.Log('Start connection ' + str(i))
            self.__connectRemote(True, i)
        #Login All
        return 0
        StartIndex = 1
        self.Log('Start crawl ' + Board + ' ' + str(StartIndex) + ' to ' + str(EndIndex))
        
        self.__CrawPool = []
        ThreadList = []
        
        self.__ThreadRunning = True
        
        for i in range(DefaultThreadNumber):
            threading.Thread(target = self.crawlThread, args = (i, Board)).start()

        for Index in range(StartIndex, EndIndex + 1):
            ErrorCode = self.__gotoPostByIndex(Board, Index)
            if ErrorCode != self.Success:
                self.Log('crawlBoard 1 goto post fail', self.LogLevel_DEBUG)
                continue
            ErrorCode, ScreenIndex = self.__readScreen('Q', ['請按任意鍵繼續'])
            if ErrorCode == self.WaitTimeout:
                return self.PostDeleted, None
            if ErrorCode != self.Success:
                self.Log('crawlBoard 2 read screen error: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode, None
            
            if ScreenIndex == 0:
                #Get query screen self.Success
                pass
            
            RealWebUrl = ''
            
            if 'https' in self.__ReceiveData:
                RealWebUrl = self.__ReceiveData[self.__ReceiveData.find('https'):self.__ReceiveData.find('.html') + 5]
            
            if RealWebUrl != '':
                # Get RealWebUrl!!!
                #self.Log(str(len(self.__CrawPool)))
                self.__CrawPool.append((Index, RealWebUrl))
        
        while len(self.__CrawPool) != 0:
            time.sleep(1)
        
        self.__ThreadRunning = False
        
        self.Log(Board + ' crawl complete')
        return self.Success
    def getPostInfoByIndex(self, Board, Index, TelentConnectIndex = 0):
        
        ErrorCode, Post = self.getPostInfoByID(Board, '', Index, TelentConnectIndex)
        
        return ErrorCode, Post
    
    def getNewPostIndexList(self, Board, LastPostIndex, TelentConnectIndex = 0):
        
        result = []
        ErrorCode, LastIndex = self.getNewestPostIndex(Board, TelentConnectIndex)

        if ErrorCode != self.Success:
            return result
        
        if LastPostIndex <= 0 or LastIndex < LastPostIndex:
            result.append(LastIndex)
        else:
            for IndexTemp in range(LastPostIndex + 1, LastIndex + 1):
                result.append(IndexTemp)
        return ErrorCode, result
    
    def pushByID(self, Board, PushType, PushContent, PostID, PostIndex=-1, TelentConnectIndex = 0):
    
        for i in range(5):
            ErrorCode = self.__pushByID(Board, PushType, PushContent, PostID, PostIndex, TelentConnectIndex)
            if ErrorCode == self.Success:
                if i != 0:
                    self.Log('pushByID recover Success', self.LogLevel_DEBUG)
                break
            if ErrorCode == self.NoPermission:
                break
        return ErrorCode
    def __pushByID(self, Board, PushType, PushContent, PostID, PostIndex=-1, TelentConnectIndex = 0):
        self.__CurrentTimeout = 3
        
        TelnetConnectIndex = 0
        
        if PostIndex != -1:
            ErrorCode = self.__gotoPostByIndex(Board, PostIndex, TelentConnectIndex)
            if ErrorCode != self.Success:
                self.Log('pushByIndex 1 goto post fail', self.LogLevel_DEBUG)
                return ErrorCode
        else:
        
            if len(PostID) != 8:
                self.Log('pushByID Error input: ' + PostID)
                return self.ErrorInput
        
            ErrorCode = self.__gotoPostByID(Board, PostID, TelentConnectIndex)
            if ErrorCode != self.Success:
                self.Log('pushByID 1 goto post fail', self.LogLevel_DEBUG)
                return ErrorCode
        
        #CaseList = ['您覺得這篇文章', '加註方式', '禁止快速連續推文']
        
        Message = 'X'
        
        while True:
        
            ErrorCode, Index = self.__readScreen(TelentConnectIndex, Message, ['您覺得這篇文章', '加註方式', '禁止快速連續推文', '禁止短時間內大量推文', '使用者不可發言'])
            if ErrorCode == self.WaitTimeout:
                print(self.__ReceiveData)
                self.Log('No push option')
                return self.NoPermission
            if ErrorCode != self.Success:
                self.Log('pushByID 2 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode
            
            Pushable = False
            
            ArrowOnly = False
            
            AllowPushTypeList = [False, False, False, False]
            
            AllowPushTypeList[self.PushType_Push] = False
            AllowPushTypeList[self.PushType_Boo] = False
            AllowPushTypeList[self.PushType_Arrow] = False
            
            if Index == 0:
                if '值得推薦' in self.__ReceiveData:
                    AllowPushTypeList[self.PushType_Push] = True
                if '給它噓聲' in self.__ReceiveData:
                    AllowPushTypeList[self.PushType_Boo] = True
                if '註解' in self.__ReceiveData:
                    AllowPushTypeList[self.PushType_Arrow] = True
                Pushable = True
                break
            if Index == 1:
                AllowPushTypeList[self.PushType_Arrow] = True
                PushType = self.PushType_Arrow
                ArrowOnly = True
                Pushable = True
                break
            if Index == 2:
                PTTUtil.Log('No fast push, wait...')
                Message = 'qX'
                time.sleep(1)
            if Index == 3:
                PTTUtil.Log('System abort many push, wait...')
                Message = 'qX'
                time.sleep(2)
            if Index == 4:
                PTTUtil.Log('You are in the bucket QQ')
                return self.NoPermission
                
        if not AllowPushTypeList[self.PushType_Boo] and PushType == self.PushType_Boo:
            PushType = self.PushType_Arrow
        
        CaseList = ['']
        
        if ArrowOnly:
            SendMessage = PushContent + '\ry'
        else:
            SendMessage = str(PushType) + PushContent + '\ry'
        
        ErrorCode, Index = self.__sendData(TelentConnectIndex, SendMessage, CaseList, True, True)
        if ErrorCode != self.Success:
            self.Log('pushByID 3 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode

        return self.Success
    def pushByIndex(self, Board, PushType, PushContent, PostIndex, TelentConnectIndex = 0):
        ErrorCode = self.pushByID(Board, PushType, PushContent, '', PostIndex, TelentConnectIndex)
        return ErrorCode
    def mail(self, UserID, MailTitle, MailContent, SignType, TelentConnectIndex = 0):
    
        ErrorCode = self.__gotoTop(TelentConnectIndex)
        if ErrorCode != self.Success:
            print('mail goto top error code 1: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['主題：', '請選擇簽名檔', '已順利寄出，是否自存底稿', '任意鍵繼續', '電子郵件']
        SendMessage = 'M\rS\r' + UserID
        Enter = True
        while True:
            ErrorCode, Index = self.__sendData(TelentConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('No such user: ' + UserID)
                return self.NoUser
            if ErrorCode != self.Success:
                self.Log('mail 2 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode
            if Index == 0:
                SendMessage = MailTitle + '\r' + MailContent + '\x18s'
                Enter = True
                self.__CurrentTimeout = 3
                self.Log('mail 主題', self.LogLevel_DEBUG)
            if Index == 1:
                SendMessage = str(SignType)
                Enter = True
                self.Log('mail 請選擇簽名檔', self.LogLevel_DEBUG)
            if Index == 2:
                SendMessage = 'Y'
                Enter = True
                self.Log('mail 已順利寄出', self.LogLevel_DEBUG)
            if Index == 3:
                SendMessage = 'q'
                Enter = False
                self.Log('mail 任意鍵繼續', self.LogLevel_DEBUG)
            if Index == 4:
                self.Log('mail 回到電子郵件', self.LogLevel_DEBUG)
                break
        
        return self.Success
        
    def giveMoney(self, ID, Money, YourPassword, TelentConnectIndex = 0):
        self.__CurrentTimeout = 3
        
        ErrorCode = self.__gotoTop(TelentConnectIndex)
        if ErrorCode != self.Success:
            print('giveMoney goto top error code 1: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['量販店', '給其他人Ptt幣', '這位幸運兒的id', '請輸入金額', '請輸入您的密碼', '要修改紅包袋嗎', '確定進行交易嗎', '按任意鍵繼續']
        SendMessage = 'P'
        Enter = True
        while True:        
            ErrorCode, Index = self.__sendData(TelentConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('No such option: ' + SendMessage)
                return self.NoUser
            if ErrorCode != self.Success:
                self.Log('mail 2 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode
            if Index == 0:
                SendMessage = 'P'
                Enter = True
                self.Log('giveMoney 量販店', self.LogLevel_DEBUG)
            if Index == 1:
                SendMessage = '0'
                Enter = True
                self.Log('giveMoney 給其他人Ptt幣', self.LogLevel_DEBUG)
            if Index == 2:
                SendMessage = ID
                Enter = True
                self.Log('giveMoney 這位幸運兒的id', self.LogLevel_DEBUG)
            if Index == 3:
                SendMessage = '\t' + str(Money)
                Enter = True
                self.Log('giveMoney 請輸入金額', self.LogLevel_DEBUG)
            if Index == 4:
                SendMessage = str(YourPassword)
                Enter = True
                self.__CurrentTimeout = 3
                self.Log('giveMoney 請輸入您的密碼', self.LogLevel_DEBUG)
            if Index == 5:
                SendMessage = 'n'
                Enter = True
                self.__CurrentTimeout = 3
                self.Log('giveMoney 要修改紅包袋嗎', self.LogLevel_DEBUG)
            if Index == 6:
                SendMessage = 'y'
                Enter = True
                self.__CurrentTimeout = 3
                self.Log('giveMoney 確定進行交易嗎', self.LogLevel_DEBUG)
            if Index == 7:
                self.Log('giveMoney 按任意鍵繼續', self.LogLevel_DEBUG)
                break
        return self.Success
        
    def getTime(self, TelentConnectIndex = 0):
        for i in range(3):
            ErrorCode, Time = self.__getTime(TelentConnectIndex)
            if ErrorCode == self.Success:
                if i != 0:
                    self.Log('getTime recover Success ' + str(i) + ' times', self.LogLevel_DEBUG)
                break
        return ErrorCode, Time
    def __getTime(self, TelentConnectIndex = 0):
        self.__CurrentTimeout = 2
        
        #Thanks for ervery one in Python
        
        ErrorCode = self.__gotoTop(TelentConnectIndex)
        if ErrorCode != self.Success:
            print('getTime goto top error code 2: ' + str(ErrorCode))
            return ErrorCode, ''
        
        for i in range(3):
            self.__CurrentTimeout = 5
            ErrorCode, Index = self.__readScreen(TelentConnectIndex, 'A\rqA\rq', ['[呼叫器]'])
            if ErrorCode == self.WaitTimeout:
                self.Log(self.__ReceiveData, self.LogLevel_DEBUG)
                self.Log('getTime 2.1', self.LogLevel_DEBUG)
                #return ErrorCode, ''
            if ErrorCode != self.Success:
                self.Log('getTime 3 read screen error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
                #return ErrorCode, ''
            '''
            if not '離開，再見…' in self.__ReceiveData or not '[呼叫器]' in self.__ReceiveData:
                self.Log(self.__ReceiveData, self.LogLevel_DEBUG)
                self.Log('Not in user menu 1', self.LogLevel_DEBUG)
                return self.ParseError, ''
            '''
            if '離開，再見…' in self.__ReceiveData and '[呼叫器]' in self.__ReceiveData and '星期' in self.__ReceiveData:
                break
        if not '離開，再見…' in self.__ReceiveData or not '[呼叫器]' in self.__ReceiveData or not '星期' in self.__ReceiveData:
            return self.ParseError, ''
        result = self.__ReceiveData[self.__ReceiveData.find('離開，再見…') + len('離開，再見…'):self.__ReceiveData.find('[呼叫器]')]
        
        if not '星期' in result:
            self.Log(result, self.LogLevel_DEBUG)
            self.Log('Not in user menu 2', self.LogLevel_DEBUG)
            return self.ParseError, ''
        
        result = result[result.find('星期') + len('星期'):]
        result = result[result.find(' ') + 1:result.find(']')]

        return self.Success, result
    
    def getUserInfo(self, ID, TelentConnectIndex = 0):
        ErrorCode = self.__gotoTop(TelentConnectIndex)
        if ErrorCode != self.Success:
            print('getUserInfo goto top error code 1: ' + str(ErrorCode))
            return ErrorCode, None
        CaseList = ['請輸入使用者代號', '請按任意鍵繼續', '顯示上幾次熱訊']
        SendMessage = 'T\rQ\r'
        Enter = False
        while True:        
            ErrorCode, Index = self.__sendData(TelentConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('No such option: ' + SendMessage)
                return ErrorCode, None
            if ErrorCode != self.Success:
                self.Log('getUserInfo 2 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode, None
            if Index == 0:
                #self.Log('Input user ID')
                SendMessage = str(ID)
                Enter = True
            if Index == 1:
                break
            if Index == 2:
                #self.Log('No such user')
                return self.NoUser, None
        
                
        self.__CurrentTimeout = 3
        
        ErrorCode, Index = self.__readScreen(TelentConnectIndex, '', ['請按任意鍵繼續'])
        
        if ErrorCode == self.WaitTimeout:
            return self.WaitTimeout, None
        if ErrorCode != self.Success:
            self.Log('getUserInfo 3 read screen time out', self.LogLevel_DEBUG)
            return ErrorCode, None
        
        if not '《ＩＤ暱稱》' in self.__ReceiveData or not '《經濟狀況》' in self.__ReceiveData or not '《登入次數》' in self.__ReceiveData or not '《有效文章》' in self.__ReceiveData or not '《目前動態》' in self.__ReceiveData or not '《私人信箱》' in self.__ReceiveData or not '《上次上站》' in self.__ReceiveData or not '《上次故鄉》' in self.__ReceiveData or not '《 五子棋 》' in self.__ReceiveData or not '《象棋戰績》' in self.__ReceiveData:
            self.Log('User info not complete')
            return self.WaitTimeout, None
        #print(self.__ReceiveData)
        
        UserID = self.__ReceiveData[self.__ReceiveData.find('《ＩＤ暱稱》') + len('《ＩＤ暱稱》'):self.__ReceiveData.find(')') + 1]
        self.__ReceiveData = self.__ReceiveData[self.__ReceiveData.find(')') + 1:]
        
        Temp = self.__ReceiveData[:self.__ReceiveData.find('《登入次數》')]

        UserMoney = self.__ReceiveData[self.__ReceiveData.find('《經濟狀況》') + len('《經濟狀況》'):self.__ReceiveData.find('《登入次數》')]
        
        while UserMoney.endswith('m') or UserMoney.endswith(' ') or UserMoney.endswith('[') or UserMoney.endswith('\r') or UserMoney.endswith('\n') or UserMoney.endswith('\x1B'):
            UserMoney = UserMoney[:len(UserMoney) - 1]
        
        self.__ReceiveData = self.__ReceiveData[self.__ReceiveData.find('《登入次數》'):]

        UserLoginTime = self.__ReceiveData[self.__ReceiveData.find('《登入次數》') + len('《登入次數》'):self.__ReceiveData.find(')') + 1]
        UserLoginTime = int(re.search(r'\d+', UserLoginTime).group())
        self.__ReceiveData = self.__ReceiveData[self.__ReceiveData.find(')') + 1:]
        
        UserPost = self.__ReceiveData[self.__ReceiveData.find('《有效文章》') + len('《有效文章》'):self.__ReceiveData.find(')') + 1]
        UserPost = int(re.search(r'\d+', UserPost).group())
        self.__ReceiveData = self.__ReceiveData[self.__ReceiveData.find(')') + 1:]
        
        UserState = self.__ReceiveData[self.__ReceiveData.find('《目前動態》') + len('《目前動態》'):self.__ReceiveData.find('《私人信箱》')]
        
        while UserState.endswith('m') or UserState.endswith(' ') or UserState.endswith('[') or UserState.endswith('\r') or UserState.endswith('\n') or UserState.endswith('\x1B'):
            UserState = UserState[:len(UserState) - 1]
        
        self.__ReceiveData = self.__ReceiveData[self.__ReceiveData.find('《私人信箱》'):]
        
        UserMail = self.__ReceiveData[self.__ReceiveData.find('《私人信箱》') + len('《私人信箱》'):self.__ReceiveData.find('《上次上站》')]
        
        while UserMail.endswith('m') or UserMail.endswith(' ') or UserMail.endswith('[') or UserMail.endswith('\r') or UserMail.endswith('\n') or UserMail.endswith('\x1B'):
            UserMail = UserMail[:len(UserMail) - 1]
        
        self.__ReceiveData = self.__ReceiveData[self.__ReceiveData.find('《上次上站》'):]
        
        UserLastLogin = self.__ReceiveData[self.__ReceiveData.find('《上次上站》') + len('《上次上站》'):self.__ReceiveData.find('《上次故鄉》')]
        
        while UserLastLogin.endswith('m') or UserLastLogin.endswith(' ') or UserLastLogin.endswith('[') or UserMail.endswith('\r') or UserMail.endswith('\n') or UserMail.endswith('\x1B'):
            UserLastLogin = UserLastLogin[:len(UserLastLogin) - 1]
        
        self.__ReceiveData = self.__ReceiveData[self.__ReceiveData.find('《上次故鄉》'):]
        
        UserLastIP = self.__ReceiveData[self.__ReceiveData.find('《上次故鄉》') + len('《上次故鄉》'):self.__ReceiveData.find('《 五子棋 》')]
        
        while UserLastIP.endswith('m') or UserLastIP.endswith(' ') or UserLastIP.endswith('[') or UserLastIP.endswith('\r') or UserLastIP.endswith('\n') or UserLastIP.endswith('\x1B'):
            UserLastIP = UserLastIP[:len(UserLastIP) - 1]
        
        self.__ReceiveData = self.__ReceiveData[self.__ReceiveData.find('《 五子棋 》'):]
        
        UserFiveChess = self.__ReceiveData[self.__ReceiveData.find('《 五子棋 》') + len('《 五子棋 》'):self.__ReceiveData.find('《象棋戰績》')]
        
        while UserFiveChess.endswith('m') or UserFiveChess.endswith(' ') or UserFiveChess.endswith('[') or UserFiveChess.endswith('\r') or UserFiveChess.endswith('\n') or UserFiveChess.endswith('\x1B'):
            UserFiveChess = UserFiveChess[:len(UserFiveChess) - 1]
        
        while UserFiveChess.find('  ') != -1:
            UserFiveChess = UserFiveChess.replace('  ', ' ')
        
        self.__ReceiveData = self.__ReceiveData[self.__ReceiveData.find('《象棋戰績》'):]
        
        UserChess = self.__ReceiveData[self.__ReceiveData.find('《象棋戰績》') + len('《象棋戰績》'):self.__ReceiveData.find('和') + 1]
        
        while UserChess.endswith('m') or UserChess.endswith(' ') or UserChess.endswith('[') or UserChess.endswith('\r') or UserChess.endswith('\n') or UserChess.endswith('\x1B'):
            UserChess = UserChess[:len(UserChess) - 1]
        
        while UserChess.find('  ') != -1:
            UserChess = UserChess.replace('  ', ' ')
        
        self.__ReceiveData = self.__ReceiveData[self.__ReceiveData.find('和') + 1:]
        
        '''
        print('QQ' + self.__ReceiveData)
        
        print('UserID: ' + UserID)
        print('UserMoney: ' + str(UserMoney))
        print('UserLoginTime: ' + str(UserLoginTime))
        print('UserPost: ' + str(UserPost))
        print('UserState: ' + UserState + '!')
        print('UserMail: ' + UserMail + '!')
        print('UserLastLogin: ' + UserLastLogin + '!')
        print('UserLastIP: ' + UserLastIP + '!')
        print('UserFiveChess: ' + UserFiveChess + '!')
        print('UserChess: ' + UserChess + '!')
        '''
        result = UserInformation(UserID, UserMoney, UserLoginTime, UserPost, UserState, UserMail, UserLastLogin, UserLastIP, UserFiveChess, UserChess)
        
        return self.Success, result
if __name__ == '__main__':

    print('PTT Crawler Library v 0.2.170622 beta')
    print('PTT CodingMan')
