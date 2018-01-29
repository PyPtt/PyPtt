import sys
import telnetlib
import time
import re
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import PTTUtil
import threading
import progressbar
import socket
import uao_decode

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class MailInformation(object):
    def __init__(self, Board, PostID, Author, Date, Title, WebUrl, Money, PostContent, PushList, OriginalData):

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
    def getPostBoard(self):
        return self.__Board
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

        self.__Version = '0.4.180129'
    
        self.__host = 'ptt.cc'
        self.__ID = ID
        self.__Password = Password
        self.__kickOtherLogin = kickOtherLogin
        
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
        self.InvalidURLError =                 13
        self.LoginFrequently =                 14

        self.PushType_Push =                    1
        self.PushType_Boo =                     2
        self.PushType_Arrow =                   3
        
        self.ReplyPost_Board =                  1
        self.ReplyPost_Mail =                   2
        
        self.__LoginMode_Login =                1
        self.__LoginMode_Recover =              2
        self.__LoginMode_MultiLogin =           3

        self.LogLevel_DEBUG =                   1
        self.LogLevel_WARNING =                 2
        self.LogLevel_INFO =                    3
        self.LogLevel_CRITICAL =                4
        self.LogLevel_SLIENT =                  5
        
        self.__LogLevel = self.LogLevel_INFO

        if LogLevel != -1:
            if LogLevel < self.LogLevel_DEBUG or self.LogLevel_SLIENT < LogLevel:
                self.Log('LogLevel error: ' + str(LogLevel))
                return None
            else:
                self.__LogLevel = LogLevel

        self.__DefaultTimeout =                 1
        
        self.__Cursor =                       '>'
        
        self.__KickTimes =                      0
        
        self.__MaxMultiLogin =                  3
        self.__ShowProgressBar =             True
        
        self.__TimeoutCountMax =                3
        
        self.__RequestCount =                   0
        self.__MaxRequestCount =                1
        self.__MinRequestCount =                1
        
        self.__TelnetConnectList = [None] * self.__MaxMultiLogin
        self.__TelnetPortList = [23, 23, 23, 23]
        self.__ReceiveData = [''] * self.__MaxMultiLogin
        self.__isConnected = [False] * self.__MaxMultiLogin
        self.__CurrentTimeout = [0] * self.__MaxMultiLogin
        self.__Timeout = [10] * self.__MaxMultiLogin
        self.__SleepTime = [0.5] * self.__MaxMultiLogin
        self.__TimeoutCount = [0] * self.__MaxMultiLogin
        
        self.__CrawPool = []
        
        self.__isBackground = False

        self.Log('歡迎使用 PTT Library v ' + self.__Version + '\r\n\r\n' + 
        '本函式庫提供您各式 PTT 操作功能\r\n\r\n' + 
        '使用方式簡單、開發快速，滿足您最嚴苛的需求。\r\n\r\n' + 
        '如有功能未能滿足您的需求，請來信告知。\r\n\r\n' + 
        'CodingMan\r\n')
        try:
            self.Log('偵測到前景執行使用編碼: ' + sys.stdin.encoding)
            self.__isBackground = False
        except Exception:
            self.Log('偵測到背景執行')
            self.__isBackground = True
        self.Log('使用者帳號: ' + ID)
        TempPW = ''

        for i in range(len(Password)):
            TempPW += '*'
        
        self.Log('密碼: ' + TempPW)
        if kickOtherLogin:
            self.Log('此連線將"會"剔除其他登入')
        else :
            self.Log('此連線將"不會"剔除其他登入')
        
        self.__connectRemote(0, self.__LoginMode_Login)
        
    def setLogLevel(self, LogLevel):
        if LogLevel < self.LogLevel_DEBUG or self.LogLevel_SLIENT < LogLevel:
            self.Log('LogLevel error')
            return self.ErrorInput
        self.__LogLevel = LogLevel
        return self.Success
    def Log(self, Message, LogLevel=-1):
        if LogLevel == -1:
            LogLevel = self.LogLevel_INFO
        if LogLevel < self.LogLevel_DEBUG or self.LogLevel_CRITICAL < LogLevel:
            self.Log('LogLevel error')
            return self.ErrorInput
        
        if self.__LogLevel <= LogLevel:
            if LogLevel == self.LogLevel_DEBUG:
                Prefix = '[除錯] '
            elif LogLevel == self.LogLevel_WARNING:
                Prefix = '[警告] '
            elif LogLevel == self.LogLevel_INFO:
                Prefix = '[資訊] '
            elif LogLevel == self.LogLevel_CRITICAL:
                Prefix = '[重要] '
        
            PTTUtil.Log(Prefix + Message)
        return self.Success
    def isLoginSuccess(self, TelnetConnectIndex=0):
        return self.__isConnected[TelnetConnectIndex]
    def __readScreen(self, TelnetConnectIndex, Message='', ExpectTarget=[]):
        
        #self.Log('__readScreen: into function TelnetConnectIndex: ' + str(TelnetConnectIndex), self.LogLevel_DEBUG)

        if ExpectTarget == None:
            ExpectTarget = []
        
        result = -1
        ErrorCode = self.UnknowError
        
        ReceiveTimes = 0

        self.__ReceiveData[TelnetConnectIndex] = ''
        
        if self.__CurrentTimeout[TelnetConnectIndex] == 0:
            self.__Timeout[TelnetConnectIndex] = self.__DefaultTimeout
        else:
            self.__Timeout[TelnetConnectIndex] = self.__CurrentTimeout[TelnetConnectIndex]
        
        try:
            self.__TelnetConnectList[TelnetConnectIndex].read_very_eager()
            self.__TelnetConnectList[TelnetConnectIndex].write(str(Message + '\x0C').encode('uao_decode'))
            StartTime = time.time()
            
            while True:
                time.sleep(self.__SleepTime[TelnetConnectIndex])
                ReceiveTimes += 1

                self.__ReceiveData[TelnetConnectIndex] += self.__TelnetConnectList[TelnetConnectIndex].read_very_eager().decode('big5', 'ignore') 
                
                DataMacthed = False
                for i in range(len(ExpectTarget)):
                
                    if ExpectTarget[i] in self.__ReceiveData[TelnetConnectIndex]:
                        result = i
                        DataMacthed = True
                        break
                
                if DataMacthed:
                    ErrorCode = self.Success
                    break
                
                NowTime = time.time()
                
                if NowTime - StartTime > self.__Timeout[TelnetConnectIndex]:
                    ErrorCode = self.WaitTimeout
                    self.__CurrentTimeout[TelnetConnectIndex] = 0
                    self.__TimeoutCount[TelnetConnectIndex] += 1
                    
                    if self.__TimeoutCount[TelnetConnectIndex] > self.__TimeoutCountMax:
                        self.__connectRemote(TelnetConnectIndex, self.__LoginMode_Recover)
                        self.__TimeoutCount[TelnetConnectIndex] = 0
                    return ErrorCode, result
        except ConnectionResetError:
            self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 被遠端主機重設', self.LogLevel_WARNING)
            if self.__isConnected[TelnetConnectIndex]:
                self.__connectRemote(TelnetConnectIndex, self.__LoginMode_Recover)
            self.__CurrentTimeout[TelnetConnectIndex] = 0
            self.__TimeoutCount[TelnetConnectIndex] = 0
            return self.ConnectResetError, result
        except EOFError:
            self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 被遠端主機剔除', self.LogLevel_WARNING)
            if self.__isConnected[TelnetConnectIndex]:
                self.__connectRemote(TelnetConnectIndex, self.__LoginMode_Recover)
            self.__CurrentTimeout[TelnetConnectIndex] = 0
            self.__TimeoutCount[TelnetConnectIndex] = 0
            return self.EOFErrorCode, result
        except AttributeError:
            self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 被遠端主機剔除或重設', self.LogLevel_WARNING)
            self.__connectRemote(TelnetConnectIndex, self.__LoginMode_Recover)
            self.__CurrentTimeout[TelnetConnectIndex] = 0
            return self.ConnectResetError, -1
        self.__TimeoutCount[TelnetConnectIndex] = 0
        self.__SleepTime[TelnetConnectIndex] = self.__SleepTime[TelnetConnectIndex] * (ReceiveTimes / 5.0)
        self.__CurrentTimeout[TelnetConnectIndex] = 0
        return ErrorCode, result
    
    def __checkState(self):
        if not self.__isConnected[TelnetConnectIndex]:
            return False
        if self.__KickTimes > 5:
            return False
        return True
    def __showScreen(self, ExpectTarget=[], TelnetConnectIndex=0):
        self.__readScreen(TelnetConnectIndex, '', ExpectTarget)
        if self.__LogLevel == self.LogLevel_DEBUG:
            print(self.__ReceiveData[TelnetConnectIndex])
    def __sendData(self, TelnetConnectIndex, Message, CaseList=[], Enter=True, Refresh=False):
        
        if Message == None:
            Message = ''
        if CaseList == None:
            CaseList = []
        
        self.__ReceiveData[TelnetConnectIndex] = ''
        
        ReceiveTimes = 0
        PostFix = ''
        
        if Enter:
            PostFix += '\r'
        if Refresh:
            PostFix += '\x0C'
        for i in range(len(CaseList)):
            if type(CaseList[i]) is str:
                CaseList[i] = CaseList[i].encode('uao_decode')
        
        if self.__isConnected[TelnetConnectIndex]:
            if self.__CurrentTimeout[TelnetConnectIndex] == 0:
                self.__Timeout[TelnetConnectIndex] = self.__DefaultTimeout
            else:
                self.__Timeout[TelnetConnectIndex] = self.__CurrentTimeout[TelnetConnectIndex]
        else:
            self.__Timeout[TelnetConnectIndex] = 10
        
        try:

            SendMessage = str(Message) + PostFix
            self.__TelnetConnectList[TelnetConnectIndex].read_very_eager()
            self.__TelnetConnectList[TelnetConnectIndex].write(SendMessage.encode('uao_decode'))
            ReturnIndex = self.__TelnetConnectList[TelnetConnectIndex].expect(CaseList, timeout=self.__Timeout[TelnetConnectIndex])[0]

        except EOFError:
            #QQ why kick me
            self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 被遠端主機剔除', self.LogLevel_WARNING)
            if self.__isConnected[TelnetConnectIndex]:
                self.__connectRemote(TelnetConnectIndex, self.__LoginMode_Recover)
            self.__CurrentTimeout[TelnetConnectIndex] = 0
            return self.EOFErrorCode, -1
        except ConnectionResetError:
            self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 被遠端主機重設', self.LogLevel_WARNING)
            if self.__isConnected[TelnetConnectIndex]:
                self.__connectRemote(TelnetConnectIndex, self.__LoginMode_Recover)
            self.__CurrentTimeout[TelnetConnectIndex] = 0
            return self.ConnectResetError, -1
        except AttributeError:
            self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 被遠端主機剔除或重設', self.LogLevel_WARNING)
            self.__connectRemote(TelnetConnectIndex, self.__LoginMode_Recover)
            self.__CurrentTimeout[TelnetConnectIndex] = 0
            return self.ConnectResetError, -1
        except socket.gaierror:
            self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 網路中斷', self.LogLevel_WARNING)
            self.__connectRemote(TelnetConnectIndex, self.__LoginMode_Recover)
            self.__CurrentTimeout[TelnetConnectIndex] = 0
            return self.ConnectResetError, -1
        if ReturnIndex == -1:
            self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 傳送資料超時', self.LogLevel_WARNING)
            self.__CurrentTimeout[TelnetConnectIndex] = 0
            return self.WaitTimeout, ReturnIndex
        self.__CurrentTimeout[TelnetConnectIndex] = 0
        return self.Success, ReturnIndex
    def __connectRemote(self, TelnetConnectIndex, LoginMode=1):
        
        self.__isConnected[TelnetConnectIndex] = False
        
        if LoginMode != self.__LoginMode_Login and LoginMode != self.__LoginMode_Recover and LoginMode != self.__LoginMode_MultiLogin:
            self.Log('Login mode input error')
            return self.ErrorInput
        
        if LoginMode == self.__LoginMode_Recover or LoginMode == self.__LoginMode_MultiLogin:
            SlientLogin = True
        else:
            SlientLogin = False
            
        CaseList = ['密碼不對', '您想刪除其他重複登入', '按任意鍵繼續', '您要刪除以上錯誤嘗試', '您有一篇文章尚未完成', '請輸入您的密碼', '編特別名單', '正在更新', '請輸入代號', '系統過載', '請勿頻繁登入']
        
        while not self.__isConnected[TelnetConnectIndex]:
        
            while True:
                try:
                    if self.__TelnetConnectList[TelnetConnectIndex] == None:
                        self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 啟動')
                        self.__TelnetConnectList[TelnetConnectIndex] = telnetlib.Telnet(self.__host, self.__TelnetPortList[TelnetConnectIndex])
                    break
                except ConnectionRefusedError:
                    self.Log('連接至 ' + self.__host + ' 失敗 10 秒後重試')
                    time.sleep(10)
                except TimeoutError:
                    self.Log('連接至 ' + self.__host + ' 失敗 10 秒後重試')
                    time.sleep(10)
                except socket.timeout:
                    self.Log('連接至 ' + self.__host + ' 失敗 10 秒後重試')
                    time.sleep(10)
                except socket.gaierror:
                    self.Log('連接至 ' + self.__host + ' 失敗 10 秒後重試')
                    time.sleep(10)
            self.Log('連接成功')
            
            SendMessage = ''
            Enter = False
            
            while not self.__isConnected[TelnetConnectIndex]:
            
                ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList, Enter)
                if ErrorCode != self.Success:
                    
                    self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 連接至 ' + self.__host + ' 失敗: ' + str(ErrorCode), self.LogLevel_WARNING)
                    
                    if TelnetConnectIndex != 0:
                        return self.UnknowError
                    
                    self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 2 秒後重新連接', self.LogLevel_WARNING)
                    self.__TelnetConnectList[TelnetConnectIndex] = None
                    time.sleep(2)
                    break
                if Index == 0:
                    self.Log('密碼不對')
                    return self.WrongPassword
                if Index == 1:
                    if self.__kickOtherLogin:
                        SendMessage = 'y'
                        Enter = True
                        if not SlientLogin:
                            self.Log('您想刪除其他重複登入 是')
                    else :
                        SendMessage = 'n'
                        Enter = True
                        if not SlientLogin:
                            self.Log('您想刪除其他重複登入 否')
                if Index == 2:
                    SendMessage = 'q'
                    Enter = False
                    if not SlientLogin:
                        self.Log('按任意鍵繼續')
                if Index == 3:
                    SendMessage = 'Y'
                    Enter = True
                    if not SlientLogin:
                        self.Log('您要刪除以上錯誤嘗試 是')
                if Index == 4:
                    SendMessage = 'q'
                    Enter = True
                    if not SlientLogin:
                        self.Log('您有一篇文章尚未完成 不保留')
                if Index == 5:
                    SendMessage = self.__Password
                    Enter = True
                    if not SlientLogin:
                        self.Log('請輸入您的密碼')
                if Index == 6:
                    self.__isConnected[TelnetConnectIndex] = True
                    if not SlientLogin:
                        self.Log('登入成功')
                    if LoginMode == self.__LoginMode_Recover:
                        self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 恢復連線成功')
                    if LoginMode == self.__LoginMode_MultiLogin:
                        self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 登入成功')
                    break
                if Index == 7:
                    SendMessage = 'q'
                    Enter = False
                    if not SlientLogin:
                        self.Log('正在更新資料...')
                    time.sleep(1)
                if Index == 8:
                    if not SlientLogin:
                        self.Log('輸入使用者代號')
                    SendMessage = self.__ID
                    Enter = True
                if Index == 9:
                    self.Log('系統過載 2 秒後重試')
                    time.sleep(2)
                    SendMessage = ''
                    Enter = False
                if Index == 10:
                    self.Log('請勿頻繁登入')
                    return self.LoginFrequently
        ErrorCode, Index = self.__readScreen(TelnetConnectIndex, '', ['> (', '●('])
        if ErrorCode != self.Success:
            self.Log(self.__ReceiveData[TelnetConnectIndex])
            self.Log('Detect cursor fail ErrorCode: ' + str(ErrorCode))
            self.__TelnetConnectList[TelnetConnectIndex] = None
            return ErrorCode
        if Index == 0:
            if not SlientLogin:
                self.Log('新式游標模式')
            self.__Cursor = '>'
        if Index == 1:
            if not SlientLogin:
                self.Log('舊式游標模式')
            self.__Cursor = '●'
        
        return self.Success
        
    def __gotoTop(self, TelnetConnectIndex=0):
        for i in range(3):
            ErrorCode = self.___gotoTop(TelnetConnectIndex)
            if ErrorCode == self.Success:
                if i != 0:
                    self.Log('__gotoTop recover Success', self.LogLevel_DEBUG)
                break
            if ErrorCode == self.EOFErrorCode and not self.__isConnected[TelnetConnectIndex]:
                break
        return ErrorCode
    def ___gotoTop(self, TelnetConnectIndex=0):
        
        self.__CurrentTimeout[TelnetConnectIndex] = 3
        ErrorCode, Index = self.__sendData(TelnetConnectIndex, 'q\x1b[D\x1b[D\x1b[D\x1b[D', ['[呼叫器]', '編特別名單', '娛樂與休閒', '系統資訊區', '主功能表', '私人信件區'], False, True)
        if ErrorCode != self.Success:
            return ErrorCode
        return self.Success
    def logout(self, TelnetConnectIndex=-1):
        
        if TelnetConnectIndex >-1:
        
            self.Log('準備登出連線 ' + str(TelnetConnectIndex), self.LogLevel_DEBUG)
        
            if self.__isConnected[TelnetConnectIndex] == False:
                self.Log('連線 ' + str(index) + ' 未連接')
                return self.Success
            
            self.__isConnected[TelnetConnectIndex] = False
            
            ErrorCode = self.__gotoTop(TelnetConnectIndex)
            if ErrorCode != self.Success:
                self.Log('登出出錯: ' + str(ErrorCode))
                return ErrorCode
            ErrorCode, _ = self.__readScreen(TelnetConnectIndex, 'g\ry\r', ['[按任意鍵繼續]'])
            self.__TelnetConnectList[TelnetConnectIndex].close()
            self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 登出成功')
            self.__TelnetConnectList[TelnetConnectIndex] = None
            
        if TelnetConnectIndex == -1:
            
            self.Log('準備登出所有連線')
            
            for index in range(self.__MaxMultiLogin):
                self.__isConnected[index] = False
            
            for index in range(self.__MaxMultiLogin):
                if self.__TelnetConnectList[index] == None:
                    self.Log('連線 ' + str(index) + ' 未連接')
                    continue
                self.Log('連線 ' + str(index) + ' 執行登出', self.LogLevel_DEBUG)
                ErrorCode = self.__gotoTop(index)
                if ErrorCode != self.Success:
                    self.Log('登出出錯: ' + str(ErrorCode))
                    continue
                ErrorCode, _ = self.__readScreen(index, 'g\ry\r', ['[按任意鍵繼續]'])
                self.__TelnetConnectList[index].close()
                self.Log('連線 ' + str(index) + ' 登出成功')
                self.__TelnetConnectList[index] = None
        
        return self.Success
    def __gotoBoard(self, Board, TelnetConnectIndex = 0):
        for i in range(5):
            ErrorCode = self.___gotoBoard(Board, TelnetConnectIndex)
            if ErrorCode == self.Success:
                if i != 0:
                    self.Log('GotoBoard recover Success', self.LogLevel_DEBUG)
                break
                
        return ErrorCode
    def ___gotoBoard(self, Board, TelnetConnectIndex):
        ErrorCode = self.__gotoTop(TelnetConnectIndex)
        if ErrorCode != self.Success:
            self.Log('Error code __gotoBoard 1: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode
        CaseList = ['請輸入看板名稱']
        SendMessage = 's'
        
        self.__CurrentTimeout[TelnetConnectIndex] = 5
        
        ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList, False)
        if ErrorCode != self.Success:
            self.Log('Error code __gotoBoard 2: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode
        
        #self.__showScreen()
        CaseList = ['請按任意鍵繼續', '其他任意鍵停止', '動畫播放中', '文章選讀']
        SendMessage = Board
        Enter = True
        
        MaxTry, TryTime = 5, 0
        while True:            
            ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList, Enter)
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
    
    def post(self, board, title, content, PostType, SignType, TelnetConnectIndex = 0):
        
        self.__CurrentTimeout[TelnetConnectIndex] = 10
        
        ErrorCode = self.__gotoBoard(board)
        if ErrorCode != self.Success:
            self.Log('post 1 Go to ' + board + ' fail', self.LogLevel_DEBUG)
            return ErrorCode
        
        CaseList = ['或不選', '使用者不可發言']
        SendMessage = '\x10'
        
        ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList, False)
        if ErrorCode != self.Success:
            self.Log('post 2 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode
        
        if Index == 1:
            self.Log('你被水桶惹 QQ')
            return self.NoPermission
        
        CaseList = ['標題']
        SendMessage = str(PostType)
        
        ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList)
        if ErrorCode != self.Success:
            self.Log('post 3 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode
        
        CaseList = ['編輯文章']
        SendMessage = title
        
        ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList)
        if ErrorCode != self.Success:
            
            self.Log('post 4 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode
        
        CaseList = ['確定要儲存檔案嗎']
        SendMessage = content + '\x18'
        
        ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList, False)
        if ErrorCode != self.Success:
            self.Log('post 5 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode
        
        self.__CurrentTimeout[TelnetConnectIndex] = 10
        
        CaseList = ['x=隨機', '請按任意鍵繼續', '看板《' + board + '》']
        SendMessage = 's'
        Enter = True
        Refresh = False
        while True:        
            ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList, Enter, Refresh)
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
    
    def getNewestPostIndex(self, Board, TelnetConnectIndex = 0):
        
        TryTime = 0
        
        for i in range(3):
            ErrorCode, Index = self.__getNewestPostIndex(Board, TelnetConnectIndex)
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
            time.sleep(self.__SleepTime[TelnetConnectIndex])
        
        #self.Log('TryTime: ' + str(TryTime))
        return ErrorCode, Index
    def __getNewestPostIndex(self, Board, TelnetConnectIndex = 0):
        ReturnIndex = -1
    
        ErrorCode = self.__gotoBoard(Board, TelnetConnectIndex)
        if ErrorCode != self.Success:
            self.Log('getNewestPostIndex 1 Go to ' + Board + ' fail', self.LogLevel_DEBUG)
            return ErrorCode, -1
        
        self.__CurrentTimeout[TelnetConnectIndex] = 3
        self.__readScreen(TelnetConnectIndex, '0\r$', ['★'])
        if ErrorCode == self.WaitTimeout:
            #self.Log('getNewestPostIndex 2.1 error code: ' + str(ErrorCode))
            #print(self.__ReceiveData[TelnetConnectIndex])
            return ErrorCode, -1

        AllIndex = re.findall(r'\d+ ', self.__ReceiveData[TelnetConnectIndex])
        
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
                #self.Log(self.__ReceiveData[TelnetConnectIndex], self.LogLevel_DEBUG)
                return self.ParseError, -1
        return self.Success, int(ReturnIndex)
    
    def __gotoPostByIndex(self, Board, PostIndex, TelnetConnectIndex=0):
        for i in range(3):
            ErrorCode = self.___gotoPostByIndex(Board, PostIndex, TelnetConnectIndex)
            if ErrorCode == self.Success:
                if i != 0:
                    self.Log('GotoPostByIndex try ' + str(i + 1) + ' recover Success', self.LogLevel_DEBUG)
                break
        return ErrorCode
    def ___gotoPostByIndex(self, Board, PostIndex, TelnetConnectIndex=0):
    
        ErrorCode = self.__gotoBoard(Board, TelnetConnectIndex)
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
            
        self.__CurrentTimeout[TelnetConnectIndex] = 5
        
        self.__readScreen(TelnetConnectIndex, str(PostIndex) + '\r', [IndexTarget])
        
        if IndexTarget in self.__ReceiveData[TelnetConnectIndex]:
            return self.Success
        else:
            #print(self.__ReceiveData[TelnetConnectIndex])
            return self.PostNotFound
    def __gotoPostByID(self, Board, PostID, TelnetConnectIndex = 0):
        self.Log('Into __gotoPostByID', self.LogLevel_DEBUG)
        ErrorCode = self.__gotoBoard(Board, TelnetConnectIndex)
        if ErrorCode != self.Success:
            self.Log('__gotoPostByID 1 Go to ' + Board + ' fail', self.LogLevel_DEBUG)
            return ErrorCode
        
        self.__readScreen(TelnetConnectIndex, '#' + PostID + '\r', '文章選讀')
        
        if '找不到這個文章代碼' in self.__ReceiveData[TelnetConnectIndex]:
            return self.PostNotFound
        
        return self.Success
        
    def getPostInfoByID(self, Board, PostID, Index=-1, TelnetConnectIndex = 0):
        self.Log('Into getPostInfoByID', self.LogLevel_DEBUG)
        for i in range(5):
            ErrorCode, Post = self.__getPostInfoByID(Board, PostID, Index, TelnetConnectIndex)
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
        isError = False
        for i in range(600):
            try:
                res = requests.get(
                    url = WebUrl,
                    cookies={'over18': '1'},
                    timeout=3
                )
                isError = False
                break
            except requests.exceptions.Timeout:
                
                self.__MaxRequestCount -= 1
                if self.__MaxRequestCount < self.__MinRequestCount:
                    self.__MaxRequestCount = self.__MinRequestCount
                
                time.sleep(1)
                isError = True
            except requests.exceptions.ConnectionError:
                #self.Log('__getPostinfoByUrl: requests conect error', self.LogLevel_DEBUG)
                self.Log('__getPostinfoByUrl: requests conect error', self.LogLevel_DEBUG)
                time.sleep(1)
                isError = True
            except requests.exceptions.InvalidURL:
                self.Log('不合法的網址: ' + WebUrl, self.LogLevel_CRITICAL)
                return self.InvalidURLError, '', '', '', '', None, ''
            except requests.exceptions.MissingSchema:
                self.Log('不合法的網址: ' + WebUrl, self.LogLevel_CRITICAL)
                return self.InvalidURLError, '', '', '', '', None, ''
        if isError:
            self.Log('getPostinfoByUrl requests 超時!', self.LogLevel_CRITICAL)
            return self.WaitTimeout, '', '', '', '', None, ''
            
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
    
    def __parsePost(self, TelnetConnectIndex = 0):
        RealPostID = ''
        RealWebUrl = ''
        RealMoney = -1
        ErrorCode = self.Success
        
        #┌─────────────────────────────────────┐
        #└─────────────────────────────────────┘
        
        self.Log(self.__ReceiveData[TelnetConnectIndex], self.LogLevel_DEBUG)

        if not '┌─────────────────────────────────────┐' in self.__ReceiveData[TelnetConnectIndex] or not '└─────────────────────────────────────┘' in self.__ReceiveData[TelnetConnectIndex]:
            return self.ParseError, RealPostID, RealMoney, RealWebUrl
        
        self.__ReceiveData[TelnetConnectIndex] = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('┌─────────────────────────────────────┐') : self.__ReceiveData[TelnetConnectIndex].find('└─────────────────────────────────────┘')]
        
        if '#' in self.__ReceiveData[TelnetConnectIndex]:
            RealPostID = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('#') + 1:]
            RealPostID = RealPostID[:RealPostID.find(' ')]
        else:
            self.Log('解析文章代碼失敗', self.LogLevel_DEBUG)
            ErrorCode = self.ParseError
            
        if 'https' in self.__ReceiveData[TelnetConnectIndex]:
            RealWebUrl = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('https://www.ptt.cc/bbs'):]
            
            self.Log(self.__ReceiveData[TelnetConnectIndex], self.LogLevel_DEBUG)
            self.Log(RealWebUrl, self.LogLevel_DEBUG)
            
            RealWebUrl = RealWebUrl[RealWebUrl.find('https'):RealWebUrl.find('.html') + 5]
            
            self.Log('QQ ' + RealWebUrl, self.LogLevel_DEBUG)
        else:
            self.Log('解析文章網址失敗', self.LogLevel_DEBUG)
            ErrorCode = self.ParseError
            
        if '這一篇文章值' in self.__ReceiveData[TelnetConnectIndex]:
            RealMoneyTemp = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('這一篇文章值') + len('這一篇文章值') : self.__ReceiveData[TelnetConnectIndex].find('Ptt幣')]
            RealMoney = int(re.search(r'\d+', RealMoneyTemp).group())
        else:
            self.Log('解析文章價錢失敗', self.LogLevel_DEBUG)
            ErrorCode = self.ParseError
        
        if ErrorCode != self.Success:
            return ErrorCode, RealPostID, RealMoney, RealWebUrl
            
        return self.Success, RealPostID, RealMoney, RealWebUrl
    def __getPostInfoByID(self, Board, PostID, Index=-1, TelnetConnectIndex = 0):
        self.Log('Into __getPostInfoByID', self.LogLevel_DEBUG)
        if Index != -1:
            self.Log('Into __gotoPostByIndex', self.LogLevel_DEBUG)
            ErrorCode = self.__gotoPostByIndex(Board, Index, TelnetConnectIndex)
            if ErrorCode != self.Success:
                self.Log('getPostInfoByIndex 1 goto post fail', self.LogLevel_DEBUG)
                return ErrorCode, None
        else:
            self.Log('Into __gotoPostByID', self.LogLevel_DEBUG)
            if len(PostID) != 8:
                self.Log('Error input: ' + PostID)
                return self.ErrorInput, None
        
            ErrorCode = self.__gotoPostByID(Board, PostID, TelnetConnectIndex)
            if ErrorCode != self.Success:
                self.Log('getPostInfoByID 1 goto post fail', self.LogLevel_DEBUG)
                return ErrorCode, None
        
        ErrorCode, Index = self.__readScreen(TelnetConnectIndex, 'Q', ['請按任意鍵繼續'])
        if ErrorCode == self.WaitTimeout:
            return self.PostDeleted, None
        if ErrorCode != self.Success:
            self.Log('getPostInfoByID 3 read screen error: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode, None
        
        ErrorCode, RealPostID, RealMoney, RealWebUrl = self.__parsePost(TelnetConnectIndex)
        
        while self.__RequestCount >= self.__MaxRequestCount:
            time.sleep(0.1)
        
        self.__RequestCount += 1
        ErrorCode, RealPostTitle, RealPostAuthor, RealPostDate, RealPostContent, RealPushList, OriginalText = self.__getPostinfoByUrl(RealWebUrl)
        self.__RequestCount -= 1
        
        if ErrorCode != self.Success:
            self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 取得文章失敗', self.LogLevel_DEBUG)
            return ErrorCode, None
        
        result = PostInformation(Board, RealPostID, RealPostAuthor, RealPostDate, RealPostTitle, RealWebUrl, RealMoney, RealPostContent, RealPushList, OriginalText)
        
        return self.Success, result
        
    def crawlSaveThread(self, ThreadIndex, Board):
        
        self.Log('線程 ' + str(ThreadIndex) + ' 啟動', self.LogLevel_DEBUG)
        
        while True:
            
            if self.__ConnectCount == 0:
                if len(self.__CrawPool) == 0:
                    break
            
            self.__CrawPoolLock.acquire()
            if len(self.__CrawPool) == 0:
                self.__CrawPoolLock.release()
                time.sleep(0.1)
                continue
                
            Index, RealPostID, RealMoney, RealWebUrl = self.__CrawPool.pop()
            self.__CrawPoolLock.release()
            
            self.Log('線程 ' + str(ThreadIndex) + ' 取得編號 ' + str(Index) + ' ' + RealWebUrl, self.LogLevel_DEBUG)
            
            ErrorCode, RealPostTitle, RealPostAuthor, RealPostDate, RealPostContent, RealPushList, OriginalText = self.__getPostinfoByUrl(RealWebUrl)
            
            if ErrorCode != self.Success:
                self.Log('線程 ' + str(ThreadIndex) + ' 取得文章失敗', self.LogLevel_DEBUG)
                if not self.__isBackground and self.__ShowProgressBar:
                    self.__ProgressBarCount += 1
                    self.__ProgressBar.update(self.__ProgressBarCount)
                continue
            #Find post
            
            Post = PostInformation(Board, RealPostID, RealPostAuthor, RealPostDate, RealPostTitle, RealWebUrl, RealMoney, RealPostContent, RealPushList, OriginalText)
            
            if not self.__isBackground and self.__ShowProgressBar:
                self.__ProgressBarCount += 1
                self.__ProgressBar.update(self.__ProgressBarCount)
            self.__SuccessPostCount += 1
            self.__PostHandler(Post)
        
        self.__SaveCount -= 1
        self.Log('線程 ' + str(ThreadIndex) + ' 結束', self.LogLevel_DEBUG)
        
    def crawlFindUrlThread(self, Board, StartIndex , EndIndex, TelnetConnectIndex):
        
        self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 開始取得編號 ' + str(StartIndex) + ' 到 ' + str(EndIndex) + ' 文章網址')
        
        for Index in range(StartIndex, EndIndex + 1):
        
            isSuccess = False
            FailReason = ''
            for i in range(3):
                ErrorCode = self.__gotoPostByIndex(Board, Index, TelnetConnectIndex)
                
                if ErrorCode != self.Success:
                    FailReason = '連線頻道 ' + str(TelnetConnectIndex) + ' crawlFindUrlThread 1 goto post fail'
                    continue
                
                ErrorCode, ScreenIndex = self.__readScreen(TelnetConnectIndex, 'Q', ['請按任意鍵繼續'])

                if ErrorCode == self.WaitTimeout:
                    FailReason = '連線頻道 ' + str(TelnetConnectIndex) + ' 讀取畫面超時'
                    continue
                if ErrorCode != self.Success:
                    FailReason = '連線頻道 ' + str(TelnetConnectIndex) + ' crawlFindUrlThread 3 __readScreen error: ' + str(ErrorCode)
                    break
                    
                ErrorCode, RealPostID, RealMoney, RealWebUrl = self.__parsePost(TelnetConnectIndex)
                if ErrorCode != self.Success:
                    FailReason = '連線頻道 ' + str(TelnetConnectIndex) + ' 解析文章失敗'
                    continue
                    
                isSuccess = True
                break
            
            if not isSuccess:
                self.Log(FailReason, self.LogLevel_DEBUG)
                if not self.__isBackground and self.__ShowProgressBar:
                    self.__ProgressBarCount += 1
                    self.__ProgressBar.update(self.__ProgressBarCount)
                continue
                
            if RealWebUrl != '':
                # Get RealWebUrl!!!
                #self.Log(str(len(self.__CrawPool)))
                #self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' : ' + RealWebUrl)
                self.__CrawPool.append((Index, RealPostID, RealMoney, RealWebUrl))
            
        self.Log('連線頻道 ' + str(TelnetConnectIndex) + ' 結束', self.LogLevel_DEBUG)
        self.__ConnectCount -= 1
        
    def crawlBoard(self, Board, PostHandler, StartIndex=0, EndIndex=0, ShowProgressBar=True):
    
        self.__PostHandler = PostHandler
    
        DefaultThreadNumber = 32
        
        self.Log('Into crawlBoard', self.LogLevel_DEBUG)
        
        self.__ShowProgressBar = ShowProgressBar
        
        if StartIndex == 0 and EndIndex == 0:
            self.Log('爬行 ' + Board + ' 板所有文章')
            
            ErrorCode, EndIndex = self.getNewestPostIndex(Board)
            if ErrorCode == self.Success:
                #self.Log('Get ' + Board + ' get newest post index success: ' + str(EndIndex))
                pass
            else:
                self.Log('取得' + Board + '板最新文章編號錯誤')
                return self.UnknowError
            
        if EndIndex < StartIndex:
            self.Log('文章編號範圍錯誤: ' + str(StartIndex) + ' 到 ' + str(EndIndex))
            return self.ErrorInput
        
        ConnectList = [0]
        self.__CrawPoolLock = threading.Lock()
        self.__TotalPost = EndIndex - StartIndex + 1

        if not self.__isBackground and self.__ShowProgressBar:
            self.__ProgressBar = progressbar.ProgressBar(max_value=self.__TotalPost)
            self.__ProgressBarCount = 0
        self.__SuccessPostCount = 0
        
        self.__RequestCount = 0
        self.__MaxRequestCount = DefaultThreadNumber
        self.__MinRequestCount = 4
        
        self.__ThreadLock = None
        
        if self.__MaxMultiLogin > 1:
            self.__kickOtherLogin = False
            self.Log('啟動多重登入模式')
        
        for i in range(1, self.__MaxMultiLogin):
            for ii in range(3):            
                if self.__connectRemote(i, self.__LoginMode_MultiLogin) == self.Success:
                    ConnectList.append(i)
                    break
        
        ConnectListTemp = ''
        
        for TelnetConnectIndex in ConnectList:
            ConnectListTemp += str(TelnetConnectIndex) + ' '
        self.Log('已啟動連線 ' + ConnectListTemp)
        
        if StartIndex == 0:
            StartIndex = 1
        self.Log('開始爬行 ' + Board + ' 板編號 ' + str(StartIndex) + ' 到 ' + str(EndIndex) + ' 的文章')

        ThreadUnit = int((EndIndex - StartIndex) / len(ConnectList))
        
        self.Log('總共 ' + str(self.__TotalPost) + ' 篇文章')
        
        self.__ConnectCount = len(ConnectList)
        self.__SaveCount = DefaultThreadNumber
        
        ThreadUnitCount = 0
        
        self.__CurrentLogLevel = self.__LogLevel
        
        self.setLogLevel(self.LogLevel_CRITICAL)
        
        for TelnetConnectIndex in ConnectList:
        
            ThreadStartIndex = 0
            ThreadEndIndex = 0

            if len(ConnectList) == 1:
                ThreadStartIndex = StartIndex
                ThreadEndIndex = EndIndex
            elif ThreadUnitCount == 0:

                ThreadStartIndex = StartIndex
                ThreadEndIndex = StartIndex + ThreadUnit
                
            elif TelnetConnectIndex == ConnectList[len(ConnectList) - 1]:
                
                ThreadStartIndex = StartIndex + ThreadUnitCount * ThreadUnit + 1
                ThreadEndIndex = EndIndex
            else:

                ThreadStartIndex = StartIndex + ThreadUnitCount * ThreadUnit + 1
                ThreadEndIndex = StartIndex + (ThreadUnitCount + 1) * ThreadUnit

            # print('ThreadStartIndex: ' + str(ThreadStartIndex))
            # print('ThreadEndIndex: ' + str(ThreadEndIndex))
            
            threading.Thread(target = self.crawlFindUrlThread, args = (Board, ThreadStartIndex, ThreadEndIndex, TelnetConnectIndex) ).start()
            
            ThreadUnitCount += 1
        
        for TelnetConnectIndex in range(DefaultThreadNumber):
            threading.Thread(target = self.crawlSaveThread, args = (TelnetConnectIndex, Board)).start()

        while True:
            time.sleep(1)
            if self.__ConnectCount == 0:
                if len(self.__CrawPool) == 0 and self.__SaveCount == 0:
                    if not self.__isBackground and self.__ShowProgressBar:
                        self.__ProgressBar.update(self.__TotalPost)
                        self.__ProgressBar.finish()
                    break

        for TelnetConnectIndex in ConnectList:
            if TelnetConnectIndex != 0:
                self.logout(TelnetConnectIndex)
        
        self.__LogLevel = self.__CurrentLogLevel
        
        self.Log('成功取得 ' + str(self.__SuccessPostCount) + ' 篇文章')
        
        return self.Success
    def getPostInfoByIndex(self, Board, Index, TelnetConnectIndex = 0):
        
        ErrorCode, Post = self.getPostInfoByID(Board, '', Index, TelnetConnectIndex)
        
        return ErrorCode, Post
    
    def getNewPostIndexList(self, Board, LastPostIndex, TelnetConnectIndex = 0):
        
        result = []
        ErrorCode, LastIndex = self.getNewestPostIndex(Board, TelnetConnectIndex)

        if ErrorCode != self.Success:
            return ErrorCode, result
        
        if LastPostIndex <= 0 or LastIndex < LastPostIndex:
            result.append(LastIndex)
        else:
            for IndexTemp in range(LastPostIndex + 1, LastIndex + 1):
                result.append(IndexTemp)
        return ErrorCode, result
    
    def pushByID(self, Board, PushType, PushContent, PostID, PostIndex=-1, TelnetConnectIndex = 0):
    
        for i in range(5):
            ErrorCode = self.__pushByID(Board, PushType, PushContent, PostID, PostIndex, TelnetConnectIndex)
            if ErrorCode == self.Success:
                if i != 0:
                    self.Log('pushByID recover Success', self.LogLevel_DEBUG)
                break
            if ErrorCode == self.NoPermission:
                break
        return ErrorCode
    def __pushByID(self, Board, PushType, PushContent, PostID, PostIndex=-1, TelnetConnectIndex = 0):
        self.__CurrentTimeout[TelnetConnectIndex] = 3

        if PostIndex != -1:
            ErrorCode = self.__gotoPostByIndex(Board, PostIndex, TelnetConnectIndex)
            if ErrorCode != self.Success:
                self.Log('pushByIndex 1 goto post fail', self.LogLevel_DEBUG)
                return ErrorCode
        else:
        
            if len(PostID) != 8:
                self.Log('pushByID Error input: ' + PostID)
                return self.ErrorInput
        
            ErrorCode = self.__gotoPostByID(Board, PostID, TelnetConnectIndex)
            if ErrorCode != self.Success:
                self.Log('pushByID 1 goto post fail', self.LogLevel_DEBUG)
                return ErrorCode

        Message = 'X'
        
        while True:
        
            ErrorCode, Index = self.__readScreen(TelnetConnectIndex, Message, ['您覺得這篇文章', '加註方式', '禁止快速連續推文', '禁止短時間內大量推文', '使用者不可發言'])
            if ErrorCode == self.WaitTimeout:
                print(self.__ReceiveData[TelnetConnectIndex])
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
                if '值得推薦' in self.__ReceiveData[TelnetConnectIndex]:
                    AllowPushTypeList[self.PushType_Push] = True
                if '給它噓聲' in self.__ReceiveData[TelnetConnectIndex]:
                    AllowPushTypeList[self.PushType_Boo] = True
                if '註解' in self.__ReceiveData[TelnetConnectIndex]:
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
                self.Log('無法快速推文，等待中...')
                Message = 'qX'
                time.sleep(1)
            if Index == 3:
                self.Log('系統阻擋過多推文，等待中...')
                Message = 'qX'
                time.sleep(2)
            if Index == 4:
                self.Log('你被水桶惹 QQ')
                return self.NoPermission
                
        if not AllowPushTypeList[self.PushType_Boo] and PushType == self.PushType_Boo:
            PushType = self.PushType_Arrow
        
        CaseList = ['']
        
        if ArrowOnly:
            SendMessage = PushContent + '\ry'
        else:
            SendMessage = str(PushType) + PushContent + '\ry'
        
        ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList, True, True)
        if ErrorCode != self.Success:
            self.Log('pushByID 3 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode

        return self.Success
    def pushByIndex(self, Board, PushType, PushContent, PostIndex, TelnetConnectIndex = 0):
        ErrorCode = self.pushByID(Board, PushType, PushContent, '', PostIndex, TelnetConnectIndex)
        return ErrorCode
    def mail(self, UserID, MailTitle, MailContent, SignType, TelnetConnectIndex = 0):
    
        ErrorCode = self.__gotoTop(TelnetConnectIndex)
        if ErrorCode != self.Success:
            print('mail goto top error code 1: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['主題：', '請選擇簽名檔', '已順利寄出，是否自存底稿', '任意鍵繼續', '電子郵件']
        SendMessage = 'M\rS\r' + UserID
        Enter = True
        while True:
            ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('無該使用: ' + UserID)
                return self.NoUser
            if ErrorCode != self.Success:
                self.Log('mail 2 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode
            if Index == 0:
                SendMessage = MailTitle + '\r' + MailContent + '\x18s'
                Enter = True
                self.__CurrentTimeout[TelnetConnectIndex] = 3
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
        
    def giveMoney(self, ID, Money, YourPassword, TelnetConnectIndex = 0):
        self.__CurrentTimeout[TelnetConnectIndex] = 3
        
        ErrorCode = self.__gotoTop(TelnetConnectIndex)
        if ErrorCode != self.Success:
            print('giveMoney goto top error code 1: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['量販店', '給其他人Ptt幣', '這位幸運兒的id', '請輸入金額', '請輸入您的密碼', '要修改紅包袋嗎', '確定進行交易嗎', '按任意鍵繼續']
        SendMessage = 'P'
        Enter = True
        while True:        
            ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('No such option: ' + SendMessage, self.LogLevel_DEBUG)
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
                self.__CurrentTimeout[TelnetConnectIndex] = 3
                self.Log('giveMoney 請輸入您的密碼', self.LogLevel_DEBUG)
            if Index == 5:
                SendMessage = 'n'
                Enter = True
                self.__CurrentTimeout[TelnetConnectIndex] = 3
                self.Log('giveMoney 要修改紅包袋嗎', self.LogLevel_DEBUG)
            if Index == 6:
                SendMessage = 'y'
                Enter = True
                self.__CurrentTimeout[TelnetConnectIndex] = 3
                self.Log('giveMoney 確定進行交易嗎', self.LogLevel_DEBUG)
            if Index == 7:
                self.Log('giveMoney 按任意鍵繼續', self.LogLevel_DEBUG)
                break
        return self.Success
        
    def getTime(self, TelnetConnectIndex = 0):
        for i in range(10):
            ErrorCode, Time = self.__getTime(TelnetConnectIndex)
            if ErrorCode == self.Success:
                if i != 0:
                    self.Log('getTime recover Success ' + str(i) + ' times', self.LogLevel_DEBUG)
                break
        
        if len(Time) == 4:
            Time = '0' + Time
        
        return ErrorCode, Time
    def __getTime(self, TelnetConnectIndex = 0):
        self.__CurrentTimeout[TelnetConnectIndex] = 2
        
        #Thanks for ervery one in Python
        
        ErrorCode = self.__gotoTop(TelnetConnectIndex)
        if ErrorCode != self.Success:
            print('getTime goto top error code 2: ' + str(ErrorCode))
            return ErrorCode, ''
        
        for i in range(3):
            self.__CurrentTimeout[TelnetConnectIndex] = 5
            ErrorCode, Index = self.__readScreen(TelnetConnectIndex, 'A\rqA\rq', ['呼叫器'])
            if ErrorCode == self.WaitTimeout:
                self.Log(self.__ReceiveData[TelnetConnectIndex], self.LogLevel_DEBUG)
                self.Log('getTime 2.1', self.LogLevel_DEBUG)
                #return ErrorCode, ''
            if ErrorCode != self.Success:
                self.Log('getTime 3 read screen error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
                #return ErrorCode, ''
            if '離開，再見…' in self.__ReceiveData[TelnetConnectIndex] and '呼叫器' in self.__ReceiveData[TelnetConnectIndex] and '星期' in self.__ReceiveData[TelnetConnectIndex]:
                break
        if not '離開，再見…' in self.__ReceiveData[TelnetConnectIndex] or not '呼叫器' in self.__ReceiveData[TelnetConnectIndex] or not '星期' in self.__ReceiveData[TelnetConnectIndex]:
            return self.ParseError, ''
        
        LastResult = self.__ReceiveData[TelnetConnectIndex]
        
        result = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('離開，再見…') + len('離開，再見…'):self.__ReceiveData[TelnetConnectIndex].find('呼叫器')]
        
        if result.find('星期') < 0:
            self.Log(LastResult, self.LogLevel_DEBUG)
            self.Log(result, self.LogLevel_DEBUG)
            self.Log('無法取得時間標的', self.LogLevel_DEBUG)
            return self.ParseError, ''
            
        result = result[result.find('星期') + len('星期'):]
        result = result[result.find(' ') + 1:result.find(']')]

        return self.Success, result
    
    def getUserInfo(self, ID, TelnetConnectIndex = 0):
        ErrorCode = self.__gotoTop(TelnetConnectIndex)
        if ErrorCode != self.Success:
            print('getUserInfo goto top error code 1: ' + str(ErrorCode))
            return ErrorCode, None
        CaseList = ['請輸入使用者代號', '請按任意鍵繼續', '顯示上幾次熱訊']
        SendMessage = 'T\rQ\r'
        Enter = False
        while True:        
            ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('No such option: ' + SendMessage, self.LogLevel_DEBUG)
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
        
                
        self.__CurrentTimeout[TelnetConnectIndex] = 3
        
        ErrorCode, Index = self.__readScreen(TelnetConnectIndex, '', ['請按任意鍵繼續'])
        
        if ErrorCode == self.WaitTimeout:
            return self.WaitTimeout, None
        if ErrorCode != self.Success:
            self.Log('getUserInfo 3 read screen time out', self.LogLevel_DEBUG)
            return ErrorCode, None
        
        if not '《ＩＤ暱稱》' in self.__ReceiveData[TelnetConnectIndex] or not '《經濟狀況》' in self.__ReceiveData[TelnetConnectIndex] or not '《登入次數》' in self.__ReceiveData[TelnetConnectIndex] or not '《有效文章》' in self.__ReceiveData[TelnetConnectIndex] or not '《目前動態》' in self.__ReceiveData[TelnetConnectIndex] or not '《私人信箱》' in self.__ReceiveData[TelnetConnectIndex] or not '《上次上站》' in self.__ReceiveData[TelnetConnectIndex] or not '《上次故鄉》' in self.__ReceiveData[TelnetConnectIndex] or not '《 五子棋 》' in self.__ReceiveData[TelnetConnectIndex] or not '《象棋戰績》' in self.__ReceiveData[TelnetConnectIndex]:
            self.Log('User info not complete')
            return self.WaitTimeout, None
        #print(self.__ReceiveData[TelnetConnectIndex])
        
        UserID = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《ＩＤ暱稱》') + len('《ＩＤ暱稱》'):self.__ReceiveData[TelnetConnectIndex].find(')') + 1]
        self.__ReceiveData[TelnetConnectIndex] = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find(')') + 1:]
        
        Temp = self.__ReceiveData[TelnetConnectIndex][:self.__ReceiveData[TelnetConnectIndex].find('《登入次數》')]

        UserMoney = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《經濟狀況》') + len('《經濟狀況》'):self.__ReceiveData[TelnetConnectIndex].find('《登入次數》')]
        
        while UserMoney.endswith('m') or UserMoney.endswith(' ') or UserMoney.endswith('[') or UserMoney.endswith('\r') or UserMoney.endswith('\n') or UserMoney.endswith('\x1B'):
            UserMoney = UserMoney[:len(UserMoney) - 1]
        
        self.__ReceiveData[TelnetConnectIndex] = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《登入次數》'):]

        UserLoginTime = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《登入次數》') + len('《登入次數》'):self.__ReceiveData[TelnetConnectIndex].find(')') + 1]
        UserLoginTime = int(re.search(r'\d+', UserLoginTime).group())
        self.__ReceiveData[TelnetConnectIndex] = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find(')') + 1:]
        
        UserPost = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《有效文章》') + len('《有效文章》'):self.__ReceiveData[TelnetConnectIndex].find(')') + 1]
        UserPost = int(re.search(r'\d+', UserPost).group())
        self.__ReceiveData[TelnetConnectIndex] = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find(')') + 1:]
        
        UserState = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《目前動態》') + len('《目前動態》'):self.__ReceiveData[TelnetConnectIndex].find('《私人信箱》')]
        
        while UserState.endswith('m') or UserState.endswith(' ') or UserState.endswith('[') or UserState.endswith('\r') or UserState.endswith('\n') or UserState.endswith('\x1B'):
            UserState = UserState[:len(UserState) - 1]
        
        self.__ReceiveData[TelnetConnectIndex] = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《私人信箱》'):]
        
        UserMail = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《私人信箱》') + len('《私人信箱》'):self.__ReceiveData[TelnetConnectIndex].find('《上次上站》')]
        
        while UserMail.endswith('m') or UserMail.endswith(' ') or UserMail.endswith('[') or UserMail.endswith('\r') or UserMail.endswith('\n') or UserMail.endswith('\x1B'):
            UserMail = UserMail[:len(UserMail) - 1]
        
        self.__ReceiveData[TelnetConnectIndex] = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《上次上站》'):]
        
        UserLastLogin = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《上次上站》') + len('《上次上站》'):self.__ReceiveData[TelnetConnectIndex].find('《上次故鄉》')]
        
        while UserLastLogin.endswith('m') or UserLastLogin.endswith(' ') or UserLastLogin.endswith('[') or UserMail.endswith('\r') or UserMail.endswith('\n') or UserMail.endswith('\x1B'):
            UserLastLogin = UserLastLogin[:len(UserLastLogin) - 1]
        
        self.__ReceiveData[TelnetConnectIndex] = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《上次故鄉》'):]
        
        UserLastIP = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《上次故鄉》') + len('《上次故鄉》'):self.__ReceiveData[TelnetConnectIndex].find('《 五子棋 》')]
        
        while UserLastIP.endswith('m') or UserLastIP.endswith(' ') or UserLastIP.endswith('[') or UserLastIP.endswith('\r') or UserLastIP.endswith('\n') or UserLastIP.endswith('\x1B'):
            UserLastIP = UserLastIP[:len(UserLastIP) - 1]
        
        self.__ReceiveData[TelnetConnectIndex] = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《 五子棋 》'):]
        
        UserFiveChess = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《 五子棋 》') + len('《 五子棋 》'):self.__ReceiveData[TelnetConnectIndex].find('《象棋戰績》')]
        
        while UserFiveChess.endswith('m') or UserFiveChess.endswith(' ') or UserFiveChess.endswith('[') or UserFiveChess.endswith('\r') or UserFiveChess.endswith('\n') or UserFiveChess.endswith('\x1B'):
            UserFiveChess = UserFiveChess[:len(UserFiveChess) - 1]
        
        while UserFiveChess.find('  ') != -1:
            UserFiveChess = UserFiveChess.replace('  ', ' ')
        
        self.__ReceiveData[TelnetConnectIndex] = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《象棋戰績》'):]
        
        UserChess = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('《象棋戰績》') + len('《象棋戰績》'):self.__ReceiveData[TelnetConnectIndex].find('和') + 1]
        
        while UserChess.endswith('m') or UserChess.endswith(' ') or UserChess.endswith('[') or UserChess.endswith('\r') or UserChess.endswith('\n') or UserChess.endswith('\x1B'):
            UserChess = UserChess[:len(UserChess) - 1]
        
        while UserChess.find('  ') != -1:
            UserChess = UserChess.replace('  ', ' ')
        
        self.__ReceiveData[TelnetConnectIndex] = self.__ReceiveData[TelnetConnectIndex][self.__ReceiveData[TelnetConnectIndex].find('和') + 1:]
        
        result = UserInformation(UserID, UserMoney, UserLoginTime, UserPost, UserState, UserMail, UserLastLogin, UserLastIP, UserFiveChess, UserChess)
        
        return self.Success, result
        
    def readPostFile(self, FileName):
        
        return PTTUtil.readPostFile(FileName)
    def getVersion(self):
        return self.__Version
    
    def replyPost(self, Board, Content, ReplyType, PostID='', Index=-1, TelnetConnectIndex = 0):

        if PostID == '' and Index == -1:
            self.Log('輸入參數錯誤')
            return self.ErrorInput
        
        if PostID != '':
            #def __gotoPostByID(self, Board, PostID, TelnetConnectIndex = 0):
            ErrorCode = self.__gotoPostByID(Board, PostID, TelnetConnectIndex)
            if ErrorCode != self.Success:
                self.Log('replyPost 1 移動至文章失敗', self.LogLevel_DEBUG)
                return ErrorCode
        elif Index != -1:
            #def __gotoPostByIndex(self, Board, PostIndex, TelnetConnectIndex=0):
            ErrorCode = self.__gotoPostByIndex(Board, Index, TelnetConnectIndex)
            if ErrorCode != self.Success:
                self.Log('replyPost 2 移動至文章失敗', self.LogLevel_DEBUG)
                return ErrorCode
                
        CaseList = [
        '二者皆是', 
        '很抱歉',
        '採用原標題', 
        '請問要引用原文嗎', 
        '編輯文章', 
        '確定要儲存檔案嗎',
        'x=隨機', 
        '請按任意鍵繼續', 
        '看板《' + Board + '》',
        '已順利寄出，是否自存底稿'
        ]
        SendMessage = 'rr'
        Enter = False
        self.__CurrentTimeout[TelnetConnectIndex] = 10
        
        while True:
            ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('無法回文', self.LogLevel_DEBUG)
                return self.WaitTimeout
            if ErrorCode != self.Success:
                self.Log('replyPost 2 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode
            if Index == 0:
                if ReplyType == self.ReplyPost_Board:
                    SendMessage = 'F'
                    self.Log('replyPost 回應至 (F)看板', self.LogLevel_DEBUG)
                elif ReplyType == self.ReplyPost_Mail:
                    SendMessage = 'M'
                    self.Log('replyPost 回應至 (M)作者信箱', self.LogLevel_DEBUG)
                elif ReplyType == (self.ReplyPost_Board + self.ReplyPost_Mail):
                    SendMessage = 'B'
                    self.Log('replyPost 回應至 (B)二者皆是', self.LogLevel_DEBUG)
                else:
                    self.Log('replyPost 不支援的回文選項: ' + str(ReplyType), self.LogLevel_DEBUG)
                self.__CurrentTimeout[TelnetConnectIndex] = 10
                Enter = True
            if Index == 1:
                SendMessage = 'Y'
                Enter = True
                self.__CurrentTimeout[TelnetConnectIndex] = 10
                self.Log('replyPost 回信給作者', self.LogLevel_DEBUG)
            if Index == 2:
                SendMessage = 'Y'
                Enter = True
                self.Log('replyPost 採用原標題', self.LogLevel_DEBUG)
            if Index == 3:
                SendMessage = 'Y'
                Enter = True
                self.Log('replyPost 引用原文', self.LogLevel_DEBUG)
            if Index == 4:
                SendMessage = Content + '\r\x18'
                Enter = True
                self.__CurrentTimeout[TelnetConnectIndex] = 10
                self.Log('replyPost 編輯文章', self.LogLevel_DEBUG)
            if Index == 5:
                SendMessage = 's'
                Enter = True
                self.Log('replyPost 儲存檔案', self.LogLevel_DEBUG)
            if Index == 6:
                SendMessage = str(0)
                Enter = True
            if Index == 7:
                SendMessage = 'q'
                Enter = False
            if Index == 8:
                #self.Log('Post Success')
                break
            if Index == 9:
                SendMessage = 'Y'
                Enter = True
                self.Log('replyPost 已順利寄出', self.LogLevel_DEBUG)
        
        return self.Success
    def getMail(self, inputMailIndex, TelnetConnectIndex = 0):
        try:
            MailIndex = int(inputMailIndex)
        except ValueError:
            self.Log('錯誤的信件編號: ' + str(inputMailIndex), self.LogLevel_INFO)
            return self.ErrorInput

        if MailIndex < 1:
            self.Log('過小的信件編號: ' + str(MailIndex), self.LogLevel_INFO)
            return self.ErrorInput

        ErrorCode = self.__gotoTop(TelnetConnectIndex)
        if ErrorCode != self.Success:
            print('無法移動至主選單: ' + str(ErrorCode))
            return ErrorCode
        # self.__showScreen()

        CaseList = [
            '我的信箱', 
            '鴻雁往返'
        ]
        SendMessage = 'm'
        Enter = True
        self.__CurrentTimeout[TelnetConnectIndex] = 10
        
        while True:
            ErrorCode, Index = self.__sendData(TelnetConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('無法前進至信箱', self.LogLevel_DEBUG)
                return self.WaitTimeout
            if ErrorCode != self.Success:
                self.Log('getMail 錯誤: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode
            if Index == 0:
                self.__CurrentTimeout[TelnetConnectIndex] = 10
                SendMessage = 'r'
                Enter = True
                self.Log('進入私人信件區', self.LogLevel_DEBUG)
            elif Index == 1:
                self.Log('進入郵件選單', self.LogLevel_DEBUG)
                # 置底
                # SendMessage = '$'
                # Enter = False
                # self.__showScreen()
                break
            else:
                self.Log('else', self.LogLevel_DEBUG)
                self.__showScreen()
                return self.UnknowError
        
        self.__CurrentTimeout[TelnetConnectIndex] = 3
        self.__readScreen(TelnetConnectIndex, '0\r$', ['鴻雁往返'])

        print(self.__ReceiveData[TelnetConnectIndex])
        # self.Log('MailIndex: ' + str(MailIndex), self.LogLevel_INFO)

        MaxMail = 0
        for i in reversed(range(1000)):
            if '/' + str(i) + '篇' in self.__ReceiveData[TelnetConnectIndex]:
                MaxMail = i
                break
        if MaxMail == 0:
            self.Log('取得信箱最高容量失敗')
            return self.UnknowError
        self.Log('此信箱最高容量: '+ str(MaxMail))

        if self.__Cursor == '>':
            MailIndexTest = 5
        elif self.__Cursor == '●':
            MailIndexTest = 4
        else:
            self.Log('無游標')
            return self.UnknowError
        NewestMailIndex = 0
        for i in reversed(range(MaxMail + 1)):
            TestString = self.__Cursor + (' ' * (MailIndexTest - len(str(i)))) + str(i)
            if TestString in self.__ReceiveData[TelnetConnectIndex]:
                NewestMailIndex = i
                break
        if NewestMailIndex == 0:
            self.Log('信箱中沒有郵件')
            return self.Success
        else:
            self.Log('信箱中最新郵件編號: ' + str(NewestMailIndex))

        
        
        return self.Success
if __name__ == '__main__':

    print('PTT Crawler Library v ' + self.__Version)
    print('CodingMan')
