import sys
import time
import re
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import threading
import progressbar
import socket
import requests
import paramiko

try:
    from . import Util
    from . import Version
    from . import ErrorCode
    from . import Information
except SystemError:
    import Util
    import Version
    import ErrorCode
    import Information

Debug = True

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Version = Version.Ver

class Library(object):
    def __init__(self, ID, Password, kickOtherLogin=True, LogLevel=-1):

        self.__host = 'ptt.cc'
        self.__ID = ID
        self.__Password = Password
        self.__kickOtherLogin = kickOtherLogin

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
        
        self.ErrorCode = ErrorCode.ErrorCode()

        self.__Refresh =                    '\x0C'

        # screen size
        self.width = 80
        self.height = 24
        # screen buffer
        self.screen = ''
        self.buf_size = self.width * self.height

        self.__LogLevel = self.LogLevel_INFO

        if LogLevel != -1:
            if LogLevel < self.LogLevel_DEBUG or self.LogLevel_SLIENT < LogLevel:
                self.Log('LogLevel error: ' + str(LogLevel))
                return None
            else:
                self.__LogLevel = LogLevel

        self.__DefaultTimeout =                 5
        
        self.__Cursor =                       '>'
        
        self.__MaxMultiLogin =                  3

        self.__ConnectList = [None] * self.__MaxMultiLogin
        self.__ReceiveData = [''] * self.__MaxMultiLogin
        self.__PreReceiveData = [''] * self.__MaxMultiLogin
        self.__isConnected = [False] * self.__MaxMultiLogin

        ###############################

        self.__KickTimes =                      0
        
        self.__ShowProgressBar =             True
        
        self.__TimeoutCountMax =                3
        
        self.__RequestCount =                   0
        self.__MaxRequestCount =                1
        self.__MinRequestCount =                1
        
        
        self.__PortList = [23, 23, 23, 23]
        
        self.__Timeout = [10] * self.__MaxMultiLogin
        self.__SleepTime = [0.5] * self.__MaxMultiLogin
        self.__TimeoutCount = [0] * self.__MaxMultiLogin
        
        self.__CrawPool = []
        
        self.__isBackground = False

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
        
        self.__connectRemote(0)
    
    def __showScreen(self, ErrorCode, CatchIndex, ConnectIndex=0):
        if Debug:
            print('-' * 50)
            print(self.__PreReceiveData[ConnectIndex])
            print('-' * 50)
            print(self.__ReceiveData[ConnectIndex])
            print('-' * 50)
            print('ErrorCode: ' + str(ErrorCode))
            print('CatchIndex: ' + str(CatchIndex))
                                    
    def setLogLevel(self, LogLevel):
        if LogLevel < self.LogLevel_DEBUG or self.LogLevel_SLIENT < LogLevel:
            self.Log('LogLevel error')
            return self.ErrorCode.ErrorInput
        self.__LogLevel = LogLevel
        return self.ErrorCode.Success
    def Log(self, Message, LogLevel=-1):
        if LogLevel == -1:
            LogLevel = self.LogLevel_INFO
        if LogLevel < self.LogLevel_DEBUG or self.LogLevel_CRITICAL < LogLevel:
            self.Log('LogLevel error')
            return self.ErrorCode.ErrorInput
        
        if self.__LogLevel <= LogLevel:
            if LogLevel == self.LogLevel_DEBUG:
                Prefix = '[除錯] '
            elif LogLevel == self.LogLevel_WARNING:
                Prefix = '[警告] '
            elif LogLevel == self.LogLevel_INFO:
                Prefix = '[資訊] '
            elif LogLevel == self.LogLevel_CRITICAL:
                Prefix = '[重要] '
        
            Util.Log(Prefix + Message)
        return self.ErrorCode.Success
    def isLoginSuccess(self, ConnectIndex=0):
        return self.__isConnected[ConnectIndex]
    def __operatePTT(self, ConnectIndex, SendMessage='', CatchTargetList=[], Refresh=False, ExtraWait=0):
        
        if CatchTargetList == None:
            CatchTargetList = []
        
        ErrorCode = self.ErrorCode.Success
        
        self.__PreReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex]
        self.__ReceiveData[ConnectIndex] = ''

        try:
            if SendMessage != '':
                while not self.__ConnectList[ConnectIndex].channel.send_ready():
                    time.sleep(0.1)
                if Refresh:
                    SendMessage += self.__Refresh
                self.__ConnectList[ConnectIndex].channel.send(SendMessage)
            
            if ExtraWait != 0:
                time.sleep(ExtraWait)
            time.sleep(0.1)

            self.__ReceiveData[ConnectIndex] = self.__wait_str(ConnectIndex)
            
            while self.__ConnectList[ConnectIndex].channel.recv_ready():
                self.__ReceiveData[ConnectIndex] += self.__recv_str(ConnectIndex)
                self.__ReceiveData[ConnectIndex] = self.__cleanScreen(self.__ReceiveData[ConnectIndex])

                # print(self.__ReceiveData[ConnectIndex])
                for i in range(len(CatchTargetList)):
                    
                    if CatchTargetList[i] in self.__ReceiveData[ConnectIndex]:
                        # print('check ' + CatchTargetList[i] + ' success')
                        self.__ConnectList[ConnectIndex].channel.settimeout(self.__DefaultTimeout)
                        return self.ErrorCode.Success, i
                    else:
                        pass
                        # print('check ' + CatchTargetList[i] + ' fail')
        except socket.timeout:
            ErrorCode = self.ErrorCode.WaitTimeout

        self.__ConnectList[ConnectIndex].channel.settimeout(self.__DefaultTimeout)
        return ErrorCode, -1
    def __cleanScreen(self, screen):
        if not screen:
            return screen
            # remove color codes
        screen = re.sub('\[[\d+;]*[mH]', '', screen)
        # remove carriage return
        screen = re.sub(r'[\r]', '', screen)
        # remove escape cahracters, capabale of partial replace
        screen = re.sub(r'[\x00-\x08]', '', screen)
        screen = re.sub(r'[\x0b\x0c]', '', screen)
        screen = re.sub(r'[\x0e-\x1f]', '', screen)
        screen = re.sub(r'[\x7f-\xff]', '', screen)
        return screen
    def __wait_str(self, ConnectIndex):
        ch = ''
        while True:
            ch = self.__ConnectList[ConnectIndex].channel.recv(1)
            if ch:
                break
        return self.__dec_bytes(ch)
    def __recv_str(self, ConnectIndex):
        return self.__dec_bytes(self.__ConnectList[ConnectIndex].channel.recv(self.buf_size))
    # decode byte array to UTF-8 string
    def __dec_bytes(self, bytes):
        return bytes.decode('utf-8', errors = 'ignore')
    def __connectRemote(self, ConnectIndex):
        
        self.__isConnected[ConnectIndex] = False

        RetryCount = 0
        Retry = False
        ErrorCode = self.ErrorCode.Success

        while not self.__isConnected[ConnectIndex]:

            if Retry:
                Retry = False
                RetryCount += 1
                if RetryCount == 3:
                    return ErrorCode
            else:
                RetryCount = 0
            
            try:
                self.__isConnected[ConnectIndex] = False
                if self.__ConnectList[ConnectIndex] != None:
                    self.__ConnectList[ConnectIndex] = None
                    self.Log('連線頻道 ' + str(ConnectIndex) + ' 重啟')
                else:
                    self.Log('連線頻道 ' + str(ConnectIndex) + ' 啟動')
                    # self.__ConnectList[ConnectIndex] = lib.(self.__host, self.__PortList[ConnectIndex])

                self.__ConnectList[ConnectIndex] = paramiko.SSHClient()
                self.__ConnectList[ConnectIndex].load_system_host_keys()
                self.__ConnectList[ConnectIndex].set_missing_host_key_policy(paramiko.WarningPolicy())
                self.__ConnectList[ConnectIndex].connect('ptt.cc', username = 'bbsu', password = '')
                
                self.__ConnectList[ConnectIndex].channel = self.__ConnectList[ConnectIndex].invoke_shell(width = self.width, height = self.height)
            except paramiko.AuthenticationException:
                # print('... Authentication failed')
                self.Log('連接至 ' + self.__host + ' SSH 認證失敗')
                return self.ErrorCode.SSHFail
            except Exception as e:
                # print('... Connection failed:', str(e))
                self.Log('連接至 ' + self.__host + ' 連線失敗')
                Retry = True
                ErrorCode = self.ErrorCode.UnknowError
                continue
            except paramiko.SSHException:
                self.Log('建立互動通道失敗')
                Retry = True
                ErrorCode = self.ErrorCode.UnknowError
                continue

            self.Log('建立互動通道成功')
            
            self.__ConnectList[ConnectIndex].channel.settimeout(self.__DefaultTimeout)

            SendMessage = ''
            Refresh = True
            ExtraWait = 0
            CatchList = [
                # 0
                '請輸入代號，或以 guest 參觀，或以 new 註冊:', 
                # 1
                '請輸入您的密碼:', 
                # 2
                '開始登入系統...',
                # 3
                '請按任意鍵繼續',
                # 4
                '您想刪除其他重複登入的連線嗎？[Y/n]',
                # 5
                '【 編特別名單 】',
                # 6
                '您要刪除以上錯誤嘗試的記錄嗎?',
                # 7
                '為避免系統負荷過重, 請稍後再試',
                # 8
                '正在更新與同步線上使用者及好友名單，系統負荷量大時會需時較久...',
                #9
                '您有一篇文章尚未完成',
                #10
                '郵件選單',
                #11
                '請檢查帳號及密碼大小寫有無輸入錯誤',
            ]
            
            while True:
                ErrorCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=Refresh, ExtraWait=ExtraWait)
                if ErrorCode != self.ErrorCode.Success:
                    return ErrorCode

                SendMessage = ''
                Refresh = False
                ExtraWait = 0

                if ErrorCode != 0:
                    self.Log('登入失敗 錯誤碼: ' + str(ErrorCode))
                    return ErrorCode
                if CatchIndex == 0:
                    self.Log('連線至首頁')
                    self.Log('輸入帳號')
                    SendMessage = self.__ID + '\r'
                elif CatchIndex == 1:
                    self.Log('輸入密碼')
                    SendMessage = self.__Password + '\r'
                    ExtraWait = 1
                elif CatchIndex == 2:
                    self.Log('登入成功!')
                    self.Log('等待載入主選單')
                    SendMessage = ' '
                    Refresh = True
                elif CatchIndex == 3:
                    self.Log('請按任意鍵繼續')
                    SendMessage = ' '
                    Refresh = True
                elif CatchIndex == 4:
                    if self.__kickOtherLogin:
                        self.Log('踢除其他登入...')
                        SendMessage = 'Y\r'
                    else:
                        self.Log('不踢除其他登入...')
                        SendMessage = 'n\r'
                    Refresh = True
                    ExtraWait = 1
                elif CatchIndex == 5:
                    self.Log('進入主選單')
                    self.__isConnected[ConnectIndex] = True
                    break
                elif CatchIndex == 6:
                    self.Log('刪除錯誤嘗試的記錄')
                    SendMessage = 'y\r'
                elif CatchIndex == 7:
                    self.Log('登入太頻繁 重新連線')
                    time.sleep(1)
                    Retry = True
                    ErrorCode = self.ErrorCode.LoginFrequently
                    continue
                elif CatchIndex == 8:
                    self.Log('正在更新與同步線上使用者及好友名單')
                    time.sleep(2)
                    SendMessage = ' '
                    Refresh = True
                elif CatchIndex == 9:
                    self.Log('放棄尚未完成文章')
                    SendMessage = 'q\r'
                elif CatchIndex == 10:
                    self.Log('信件數目超出上限請整理')
                    return self.ErrorCode.MailBoxFull
                elif CatchIndex == 11:
                    self.Log('密碼錯誤')
                    return self.ErrorCode.WrongPassword
                else:
                    self.__showScreen(ErrorCode, CatchIndex, ConnectIndex)
                    ErrorCode = self.ErrorCode.UnknowError
                    Retry = True
                    continue

        if '> (' in self.__ReceiveData[ConnectIndex]:
            self.Log('新式游標模式')
            self.__Cursor = '>'
        elif '●(' in self.__ReceiveData[ConnectIndex]:
            self.Log('舊式游標模式')
            self.__Cursor = '●'
        else:
            self.Log('無法偵測游標')
            return self.ErrorCode.UnknowError
        return self.ErrorCode.Success
    def __gotoMainMenu(self, ConnectIndex=0):
        
        ErrorCode, CatchIndex = self.__operatePTT(ConnectIndex, 'q\x1b[D\x1b[D\x1b[D\x1b[D', ['[呼叫器]', '編特別名單', '娛樂與休閒', '系統資訊區', '主功能表', '私人信件區'], Refresh=True)
        if ErrorCode != self.ErrorCode.Success:
            return ErrorCode
        if CatchIndex != -1:
            return self.ErrorCode.Success
        return self.ErrorCode.UnknowError
    def logout(self, ConnectIndex=-1):
        
        if ConnectIndex == -1:
            
            self.Log('準備登出所有頻道')
            
            for index in range(self.__MaxMultiLogin):
                self.__isConnected[index] = False
            
            for index in range(self.__MaxMultiLogin):
                if self.__ConnectList[index] == None:
                    # self.Log('連線 ' + str(index) + ' 未連接')
                    continue
                self.Log('頻道 ' + str(index) + ' 登出', self.LogLevel_DEBUG)
                ErrorCode = self.__gotoMainMenu(index)
                if ErrorCode != self.ErrorCode.Success:
                    self.Log('頻道 ' + str(index) + '登出出錯: ' + str(ErrorCode))
                    continue
                
                SendMessage = 'g\ry\r'
                Refresh = False
                ExtraWait = 1
                self.__ConnectList[index].channel.settimeout(3)
                ErrorCode, CatchIndex = self.__operatePTT(index, SendMessage=SendMessage, CatchTargetList=['按任意鍵繼續'], Refresh=Refresh, ExtraWait=ExtraWait)
                if ErrorCode != 0:
                    self.Log('頻道 ' + str(index) + '登出失敗 錯誤碼: ' + str(ErrorCode))
                    return
                if CatchIndex == 0:
                    self.__ConnectList[index].channel.close()
                    self.__ConnectList[index].close()
                    self.__ConnectList[index] = None
                    self.Log('頻道 ' + str(index) + ' 登出成功')
                else:
                    self.__showScreen(ErrorCode, CatchIndex, ConnectIndex)
                
        return self.ErrorCode.Success
    def __gotoBoard(self, Board, ConnectIndex):

        ErrorCode = self.__gotoMainMenu(ConnectIndex)
        if ErrorCode != self.ErrorCode.Success:
            self.Log('Error code __gotoBoard 1: ' + str(ErrorCode), self.LogLevel_DEBUG)
            self.__showScreen(0, 0, ConnectIndex)
            return ErrorCode

        CatchList = [
            # 0
            '請輸入看板名稱', 
            # 1
            '請按任意鍵繼續', 
            # 2
            '文章選讀',
            # 3
            '動畫播放中',
        ]
        SendMessage = 's'
        Refresh = False
        ExtraWait = 0

        ErrorCount = 0
        while True:
            ErrorCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=Refresh, ExtraWait=ExtraWait)
            if ErrorCode != self.ErrorCode.Success:
                return ErrorCode

            SendMessage = ''
            Refresh = False
            ExtraWait = 0

            if CatchIndex == 0:
                self.Log('輸入看板名稱')
                SendMessage = Board + '\r'
                # ExtraWait = 1
            elif CatchIndex == 1:
                self.Log('請按任意鍵繼續')
                SendMessage = ' '
            elif CatchIndex == 2:
                self.Log('進入 ' + Board + ' 板成功')
                return self.ErrorCode.Success
            elif CatchIndex == 3:
                self.Log('動畫播放中')
                SendMessage = 'q'
            else:
                self.Log('前往 ' + Board + ' 板時有無法處理的標的', self.LogLevel_DEBUG)
                # self.__showScreen(ErrorCode, CatchIndex, ConnectIndex)
                SendMessage = ' '
                ErrorCount += 1
                if ErrorCount >= 3:
                    return self.ErrorCode.UnknowError
        
        return self.ErrorCode.Success
    
    def getNewestPostIndex(self, Board, ConnectIndex = 0):
        
        result = -1
    
        ErrorCode = self.__gotoBoard(Board, ConnectIndex)
        if ErrorCode != self.ErrorCode.Success:
            self.Log('getNewestPostIndex 1 Go to ' + Board + ' fail', self.LogLevel_DEBUG)
            return ErrorCode, result
        
        CatchList = [
            # 0
            '文章選讀',
        ]
        SendMessage = '0\r$'
        Refresh = True
        ExtraWait = 0

        while True:
            ErrorCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=Refresh, ExtraWait=ExtraWait)
            if ErrorCode != self.ErrorCode.Success:
                return ErrorCode, result

            SendMessage = ''
            Refresh = False
            ExtraWait = 0

            if CatchIndex == 0:
                self.Log('游標移動至底部成功')
                break

        # self.__showScreen(ErrorCode, 0, 0)
        AllIndex = re.findall(r'\d+ ', self.__ReceiveData[ConnectIndex])
        AllIndex = list(set(map(int, AllIndex)))

        if len(AllIndex) == 0:
            self.__showScreen(ErrorCode, CatchIndex, ConnectIndex)
            return self.ErrorCode.ParseError, result

        AllIndex.sort(reverse=True)

        for IndexTemp in AllIndex:
            isContinue = True

            for i in range(5):
                if IndexTemp - i not in AllIndex:
                    isContinue = False
                    break
            
            if isContinue:
                result = IndexTemp
                break

        return self.ErrorCode.Success, result
    def __gotoPostByIndex(self, Board, PostIndex, ConnectIndex=0):
        for i in range(3):
            ErrorCode = self.___gotoPostByIndex(Board, PostIndex, ConnectIndex)
            if ErrorCode == self.ErrorCode.Success:
                if i != 0:
                    self.Log('GotoPostByIndex try ' + str(i + 1) + ' recover Success', self.LogLevel_DEBUG)
                break
        return ErrorCode
    def ___gotoPostByIndex(self, Board, PostIndex, ConnectIndex=0):
    
        ErrorCode = self.__gotoBoard(Board, ConnectIndex)
        if ErrorCode != self.ErrorCode.Success:
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
            
        self.__CurrentTimeout[ConnectIndex] = 5
        
        self.__readScreen(ConnectIndex, str(PostIndex) + '\r', [IndexTarget])
        
        if IndexTarget in self.__ReceiveData[ConnectIndex]:
            return self.ErrorCode.Success
        else:
            #print(self.__ReceiveData[ConnectIndex])
            return self.PostNotFound
    def __gotoPostByID(self, Board, PostID, ConnectIndex = 0):
        self.Log('Into __gotoPostByID', self.LogLevel_DEBUG)
        ErrorCode = self.__gotoBoard(Board, ConnectIndex)
        if ErrorCode != self.ErrorCode.Success:
            self.Log('__gotoPostByID 1 Go to ' + Board + ' fail', self.LogLevel_DEBUG)
            return ErrorCode
        
        self.__readScreen(ConnectIndex, '#' + PostID + '\r', '文章選讀')
        
        if '找不到這個文章代碼' in self.__ReceiveData[ConnectIndex]:
            return self.PostNotFound
        
        return self.ErrorCode.Success
        
    def getPostInfoByID(self, Board, PostID, Index=-1, ConnectIndex = 0):
        self.Log('Into getPostInfoByID', self.LogLevel_DEBUG)
        for i in range(5):
            ErrorCode, Post = self.__getPostInfoByID(Board, PostID, Index, ConnectIndex)
            if ErrorCode == self.ErrorCode.Success:
                if i != 0:
                    self.Log('getPostInfoByID recover Success', self.LogLevel_DEBUG)
                break
            if ErrorCode == self.WebFormatError:
                break
            if ErrorCode == self.PostDeleted:
                break
        return ErrorCode, Post    
    def post(self, Board, Title, Content, PostType, SignType, ConnectIndex = 0):
        
        ErrorCode = self.__gotoBoard(Board, ConnectIndex)
        if ErrorCode != self.ErrorCode.Success:
            self.Log('post 1 Go to ' + Board + ' fail', self.LogLevel_DEBUG)
            return ErrorCode
        
        return self.ErrorCode.Success
        
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
        
        return self.ErrorCode.Success, RealPostTitle, RealPostAuthor, RealPostDate, RealPostContent, RealPushList, res.text
    
    def __parsePost(self, ConnectIndex = 0):
        RealPostID = ''
        RealWebUrl = ''
        RealMoney = -1
        ErrorCode = self.ErrorCode.Success
        
        #┌─────────────────────────────────────┐
        #└─────────────────────────────────────┘
        
        self.Log(self.__ReceiveData[ConnectIndex], self.LogLevel_DEBUG)

        if not '┌─────────────────────────────────────┐' in self.__ReceiveData[ConnectIndex] or not '└─────────────────────────────────────┘' in self.__ReceiveData[ConnectIndex]:
            return self.ParseError, RealPostID, RealMoney, RealWebUrl
        
        self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('┌─────────────────────────────────────┐') : self.__ReceiveData[ConnectIndex].find('└─────────────────────────────────────┘')]
        
        if '#' in self.__ReceiveData[ConnectIndex]:
            RealPostID = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('#') + 1:]
            RealPostID = RealPostID[:RealPostID.find(' ')]
        else:
            self.Log('解析文章代碼失敗', self.LogLevel_DEBUG)
            ErrorCode = self.ParseError
            
        if 'https' in self.__ReceiveData[ConnectIndex]:
            RealWebUrl = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('https://www.ptt.cc/bbs'):]
            
            self.Log(self.__ReceiveData[ConnectIndex], self.LogLevel_DEBUG)
            self.Log(RealWebUrl, self.LogLevel_DEBUG)
            
            RealWebUrl = RealWebUrl[RealWebUrl.find('https'):RealWebUrl.find('.html') + 5]
            
            self.Log('QQ ' + RealWebUrl, self.LogLevel_DEBUG)
        else:
            self.Log('解析文章網址失敗', self.LogLevel_DEBUG)
            ErrorCode = self.ParseError
            
        if '這一篇文章值' in self.__ReceiveData[ConnectIndex]:
            RealMoneyTemp = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('這一篇文章值') + len('這一篇文章值') : self.__ReceiveData[ConnectIndex].find('Ptt幣')]
            RealMoney = int(re.search(r'\d+', RealMoneyTemp).group())
        else:
            self.Log('解析文章價錢失敗', self.LogLevel_DEBUG)
            ErrorCode = self.ParseError
        
        if ErrorCode != self.ErrorCode.Success:
            return ErrorCode, RealPostID, RealMoney, RealWebUrl
            
        return self.ErrorCode.Success, RealPostID, RealMoney, RealWebUrl
    def __getPostInfoByID(self, Board, PostID, Index=-1, ConnectIndex = 0):
        self.Log('Into __getPostInfoByID', self.LogLevel_DEBUG)
        if Index != -1:
            self.Log('Into __gotoPostByIndex', self.LogLevel_DEBUG)
            ErrorCode = self.__gotoPostByIndex(Board, Index, ConnectIndex)
            if ErrorCode != self.ErrorCode.Success:
                self.Log('getPostInfoByIndex 1 goto post fail', self.LogLevel_DEBUG)
                return ErrorCode, None
        else:
            self.Log('Into __gotoPostByID', self.LogLevel_DEBUG)
            if len(PostID) != 8:
                self.Log('Error input: ' + PostID)
                return self.ErrorInput, None
        
            ErrorCode = self.__gotoPostByID(Board, PostID, ConnectIndex)
            if ErrorCode != self.ErrorCode.Success:
                self.Log('getPostInfoByID 1 goto post fail', self.LogLevel_DEBUG)
                return ErrorCode, None
        
        ErrorCode, Index = self.__readScreen(ConnectIndex, 'Q', ['請按任意鍵繼續'])
        if ErrorCode == self.WaitTimeout:
            return self.PostDeleted, None
        if ErrorCode != self.ErrorCode.Success:
            self.Log('getPostInfoByID 3 read screen error: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode, None
        
        ErrorCode, RealPostID, RealMoney, RealWebUrl = self.__parsePost(ConnectIndex)
        
        while self.__RequestCount >= self.__MaxRequestCount:
            time.sleep(0.1)
        
        self.__RequestCount += 1
        ErrorCode, RealPostTitle, RealPostAuthor, RealPostDate, RealPostContent, RealPushList, OriginalText = self.__getPostinfoByUrl(RealWebUrl)
        self.__RequestCount -= 1
        
        if ErrorCode != self.ErrorCode.Success:
            self.Log('連線頻道 ' + str(ConnectIndex) + ' 取得文章失敗', self.LogLevel_DEBUG)
            return ErrorCode, None
        
        result = PostInformation(Board, RealPostID, RealPostAuthor, RealPostDate, RealPostTitle, RealWebUrl, RealMoney, RealPostContent, RealPushList, OriginalText)
        
        return self.ErrorCode.Success, result
        
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
            
            if ErrorCode != self.ErrorCode.Success:
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
        
    def crawlFindUrlThread(self, Board, StartIndex , EndIndex, ConnectIndex):
        
        self.Log('連線頻道 ' + str(ConnectIndex) + ' 開始取得編號 ' + str(StartIndex) + ' 到 ' + str(EndIndex) + ' 文章網址')
        
        for Index in range(StartIndex, EndIndex + 1):
        
            isSuccess = False
            FailReason = ''
            for i in range(3):
                ErrorCode = self.__gotoPostByIndex(Board, Index, ConnectIndex)
                
                if ErrorCode != self.ErrorCode.Success:
                    FailReason = '連線頻道 ' + str(ConnectIndex) + ' crawlFindUrlThread 1 goto post fail'
                    continue
                
                ErrorCode, ScreenIndex = self.__readScreen(ConnectIndex, 'Q', ['請按任意鍵繼續'])

                if ErrorCode == self.WaitTimeout:
                    FailReason = '連線頻道 ' + str(ConnectIndex) + ' 讀取畫面超時'
                    continue
                if ErrorCode != self.ErrorCode.Success:
                    FailReason = '連線頻道 ' + str(ConnectIndex) + ' crawlFindUrlThread 3 __readScreen error: ' + str(ErrorCode)
                    break
                    
                ErrorCode, RealPostID, RealMoney, RealWebUrl = self.__parsePost(ConnectIndex)
                if ErrorCode != self.ErrorCode.Success:
                    FailReason = '連線頻道 ' + str(ConnectIndex) + ' 解析文章失敗'
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
                #self.Log('連線頻道 ' + str(ConnectIndex) + ' : ' + RealWebUrl)
                self.__CrawPool.append((Index, RealPostID, RealMoney, RealWebUrl))
            
        self.Log('連線頻道 ' + str(ConnectIndex) + ' 結束', self.LogLevel_DEBUG)
        self.__ConnectCount -= 1
        
    def crawlBoard(self, Board, PostHandler, StartIndex=0, EndIndex=0, ShowProgressBar=True):
    
        self.__PostHandler = PostHandler
    
        DefaultThreadNumber = 32
        
        self.Log('Into crawlBoard', self.LogLevel_DEBUG)
        
        self.__ShowProgressBar = ShowProgressBar
        
        if StartIndex == 0 and EndIndex == 0:
            self.Log('爬行 ' + Board + ' 板所有文章')
            
            ErrorCode, EndIndex = self.getNewestPostIndex(Board)
            if ErrorCode == self.ErrorCode.Success:
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
        
        if self.__MaxMultiLogin > 1 and EndIndex - StartIndex + 1 > 10:
            self.__kickOtherLogin = False
            self.Log('啟動多重登入模式')
            for i in range(1, self.__MaxMultiLogin):
                for ii in range(3):            
                    if self.__connectRemote(i) == self.ErrorCode.Success:
                        ConnectList.append(i)
                        break
        else:
            self.Log('啟動單一登入模式')

        ConnectListTemp = ''
        
        for ConnectIndex in ConnectList:
            ConnectListTemp += str(ConnectIndex) + ' '
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
        
        for ConnectIndex in ConnectList:
        
            ThreadStartIndex = 0
            ThreadEndIndex = 0

            if len(ConnectList) == 1:
                ThreadStartIndex = StartIndex
                ThreadEndIndex = EndIndex
            elif ThreadUnitCount == 0:

                ThreadStartIndex = StartIndex
                ThreadEndIndex = StartIndex + ThreadUnit
                
            elif ConnectIndex == ConnectList[len(ConnectList) - 1]:
                
                ThreadStartIndex = StartIndex + ThreadUnitCount * ThreadUnit + 1
                ThreadEndIndex = EndIndex
            else:

                ThreadStartIndex = StartIndex + ThreadUnitCount * ThreadUnit + 1
                ThreadEndIndex = StartIndex + (ThreadUnitCount + 1) * ThreadUnit

            # print('ThreadStartIndex: ' + str(ThreadStartIndex))
            # print('ThreadEndIndex: ' + str(ThreadEndIndex))
            
            threading.Thread(target = self.crawlFindUrlThread, args = (Board, ThreadStartIndex, ThreadEndIndex, ConnectIndex) ).start()
            
            ThreadUnitCount += 1
        
        for ConnectIndex in range(DefaultThreadNumber):
            threading.Thread(target = self.crawlSaveThread, args = (ConnectIndex, Board)).start()

        while True:
            time.sleep(1)
            if self.__ConnectCount == 0:
                if len(self.__CrawPool) == 0 and self.__SaveCount == 0:
                    if not self.__isBackground and self.__ShowProgressBar:
                        self.__ProgressBar.update(self.__TotalPost)
                        self.__ProgressBar.finish()
                    break

        for ConnectIndex in ConnectList:
            if ConnectIndex != 0:
                self.logout(ConnectIndex)
        
        self.__LogLevel = self.__CurrentLogLevel
        
        self.Log('成功取得 ' + str(self.__SuccessPostCount) + ' 篇文章')
        
        return self.ErrorCode.Success
    def getPostInfoByIndex(self, Board, Index, ConnectIndex = 0):
        
        ErrorCode, Post = self.getPostInfoByID(Board, '', Index, ConnectIndex)
        
        return ErrorCode, Post
    
    def getNewPostIndexList(self, Board, LastPostIndex, ConnectIndex = 0):
        
        result = []
        ErrorCode, LastIndex = self.getNewestPostIndex(Board, ConnectIndex)

        if ErrorCode != self.ErrorCode.Success:
            return ErrorCode, result
        
        if LastPostIndex <= 0 or LastIndex < LastPostIndex:
            result.append(LastIndex)
        else:
            for IndexTemp in range(LastPostIndex + 1, LastIndex + 1):
                result.append(IndexTemp)
        return ErrorCode, result
    
    def pushByID(self, Board, PushType, PushContent, PostID, PostIndex=-1, ConnectIndex = 0):
    
        for i in range(5):
            ErrorCode = self.__pushByID(Board, PushType, PushContent, PostID, PostIndex, ConnectIndex)
            if ErrorCode == self.ErrorCode.Success:
                if i != 0:
                    self.Log('pushByID recover Success', self.LogLevel_DEBUG)
                break
            if ErrorCode == self.NoPermission:
                break
        return ErrorCode
    def __pushByID(self, Board, PushType, PushContent, PostID, PostIndex=-1, ConnectIndex = 0):
        self.__CurrentTimeout[ConnectIndex] = 3

        if PostIndex != -1:
            ErrorCode = self.__gotoPostByIndex(Board, PostIndex, ConnectIndex)
            if ErrorCode != self.ErrorCode.Success:
                self.Log('pushByIndex 1 goto post fail', self.LogLevel_DEBUG)
                return ErrorCode
        else:
        
            if len(PostID) != 8:
                self.Log('pushByID Error input: ' + PostID)
                return self.ErrorInput
        
            ErrorCode = self.__gotoPostByID(Board, PostID, ConnectIndex)
            if ErrorCode != self.ErrorCode.Success:
                self.Log('pushByID 1 goto post fail', self.LogLevel_DEBUG)
                return ErrorCode

        Message = 'X'
        
        while True:
        
            ErrorCode, Index = self.__readScreen(ConnectIndex, Message, ['您覺得這篇文章', '加註方式', '禁止快速連續推文', '禁止短時間內大量推文', '使用者不可發言'])
            if ErrorCode == self.WaitTimeout:
                print(self.__ReceiveData[ConnectIndex])
                self.Log('No push option')
                return self.NoPermission
            if ErrorCode != self.ErrorCode.Success:
                self.Log('pushByID 2 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode
            
            Pushable = False
            
            ArrowOnly = False
            
            AllowPushTypeList = [False, False, False, False]
            
            AllowPushTypeList[self.PushType_Push] = False
            AllowPushTypeList[self.PushType_Boo] = False
            AllowPushTypeList[self.PushType_Arrow] = False
            
            if Index == 0:
                if '值得推薦' in self.__ReceiveData[ConnectIndex]:
                    AllowPushTypeList[self.PushType_Push] = True
                if '給它噓聲' in self.__ReceiveData[ConnectIndex]:
                    AllowPushTypeList[self.PushType_Boo] = True
                if '註解' in self.__ReceiveData[ConnectIndex]:
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
        
        ErrorCode, Index = self.__sendData(ConnectIndex, SendMessage, CaseList, True, True)
        if ErrorCode != self.ErrorCode.Success:
            self.Log('pushByID 3 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
            return ErrorCode

        return self.ErrorCode.Success
    def pushByIndex(self, Board, PushType, PushContent, PostIndex, ConnectIndex = 0):
        ErrorCode = self.pushByID(Board, PushType, PushContent, '', PostIndex, ConnectIndex)
        return ErrorCode
    def mail(self, UserID, MailTitle, MailContent, SignType, ConnectIndex = 0):
    
        ErrorCode = self.__gotoTop(ConnectIndex)
        if ErrorCode != self.ErrorCode.Success:
            print('mail goto top error code 1: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['主題：', '請選擇簽名檔', '已順利寄出，是否自存底稿', '任意鍵繼續', '電子郵件']
        SendMessage = 'M\rS\r' + UserID
        Enter = True
        while True:
            ErrorCode, Index = self.__sendData(ConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('無該使用: ' + UserID)
                return self.NoUser
            if ErrorCode != self.ErrorCode.Success:
                self.Log('mail 2 error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode
            if Index == 0:
                SendMessage = MailTitle + '\r' + MailContent + '\x18s'
                Enter = True
                self.__CurrentTimeout[ConnectIndex] = 3
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
        
        return self.ErrorCode.Success
        
    def giveMoney(self, ID, Money, YourPassword, ConnectIndex = 0):
        self.__CurrentTimeout[ConnectIndex] = 3
        
        ErrorCode = self.__gotoTop(ConnectIndex)
        if ErrorCode != self.ErrorCode.Success:
            print('giveMoney goto top error code 1: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['量販店', '給其他人Ptt幣', '這位幸運兒的id', '請輸入金額', '請輸入您的密碼', '要修改紅包袋嗎', '確定進行交易嗎', '按任意鍵繼續']
        SendMessage = 'P'
        Enter = True
        while True:        
            ErrorCode, Index = self.__sendData(ConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('No such option: ' + SendMessage, self.LogLevel_DEBUG)
                return self.NoUser
            if ErrorCode != self.ErrorCode.Success:
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
                self.__CurrentTimeout[ConnectIndex] = 3
                self.Log('giveMoney 請輸入您的密碼', self.LogLevel_DEBUG)
            if Index == 5:
                SendMessage = 'n'
                Enter = True
                self.__CurrentTimeout[ConnectIndex] = 3
                self.Log('giveMoney 要修改紅包袋嗎', self.LogLevel_DEBUG)
            if Index == 6:
                SendMessage = 'y'
                Enter = True
                self.__CurrentTimeout[ConnectIndex] = 3
                self.Log('giveMoney 確定進行交易嗎', self.LogLevel_DEBUG)
            if Index == 7:
                self.Log('giveMoney 按任意鍵繼續', self.LogLevel_DEBUG)
                break
        return self.ErrorCode.Success
        
    def getTime(self, ConnectIndex = 0):
        for i in range(10):
            ErrorCode, Time = self.__getTime(ConnectIndex)
            if ErrorCode == self.ErrorCode.Success:
                if i != 0:
                    self.Log('getTime recover Success ' + str(i) + ' times', self.LogLevel_DEBUG)
                break
        
        if len(Time) == 4:
            Time = '0' + Time
        
        return ErrorCode, Time
    def __getTime(self, ConnectIndex = 0):
        self.__CurrentTimeout[ConnectIndex] = 2
        
        #Thanks for ervery one in Python
        
        ErrorCode = self.__gotoTop(ConnectIndex)
        if ErrorCode != self.ErrorCode.Success:
            print('getTime goto top error code 2: ' + str(ErrorCode))
            return ErrorCode, ''
        
        for i in range(3):
            self.__CurrentTimeout[ConnectIndex] = 5
            ErrorCode, Index = self.__readScreen(ConnectIndex, 'A\rqA\rq', ['呼叫器'])
            if ErrorCode == self.WaitTimeout:
                self.Log(self.__ReceiveData[ConnectIndex], self.LogLevel_DEBUG)
                self.Log('getTime 2.1', self.LogLevel_DEBUG)
                #return ErrorCode, ''
            if ErrorCode != self.ErrorCode.Success:
                self.Log('getTime 3 read screen error code: ' + str(ErrorCode), self.LogLevel_DEBUG)
                #return ErrorCode, ''
            if '離開，再見…' in self.__ReceiveData[ConnectIndex] and '呼叫器' in self.__ReceiveData[ConnectIndex] and '星期' in self.__ReceiveData[ConnectIndex]:
                break
        if not '離開，再見…' in self.__ReceiveData[ConnectIndex] or not '呼叫器' in self.__ReceiveData[ConnectIndex] or not '星期' in self.__ReceiveData[ConnectIndex]:
            return self.ParseError, ''
        
        LastResult = self.__ReceiveData[ConnectIndex]
        
        result = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('離開，再見…') + len('離開，再見…'):self.__ReceiveData[ConnectIndex].find('呼叫器')]
        
        if result.find('星期') < 0:
            self.Log(LastResult, self.LogLevel_DEBUG)
            self.Log(result, self.LogLevel_DEBUG)
            self.Log('無法取得時間標的', self.LogLevel_DEBUG)
            return self.ParseError, ''
            
        result = result[result.find('星期') + len('星期'):]
        result = result[result.find(' ') + 1:result.find(']')]

        return self.ErrorCode.Success, result
    
    def getUserInfo(self, ID, ConnectIndex = 0):
        ErrorCode = self.__gotoTop(ConnectIndex)
        if ErrorCode != self.ErrorCode.Success:
            print('getUserInfo goto top error code 1: ' + str(ErrorCode))
            return ErrorCode, None
        CaseList = ['請輸入使用者代號', '請按任意鍵繼續', '顯示上幾次熱訊']
        SendMessage = 'T\rQ\r'
        Enter = False
        while True:        
            ErrorCode, Index = self.__sendData(ConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('No such option: ' + SendMessage, self.LogLevel_DEBUG)
                return ErrorCode, None
            if ErrorCode != self.ErrorCode.Success:
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
        
                
        self.__CurrentTimeout[ConnectIndex] = 3
        
        ErrorCode, Index = self.__readScreen(ConnectIndex, '', ['請按任意鍵繼續'])
        
        if ErrorCode == self.WaitTimeout:
            return self.WaitTimeout, None
        if ErrorCode != self.ErrorCode.Success:
            self.Log('getUserInfo 3 read screen time out', self.LogLevel_DEBUG)
            return ErrorCode, None
        
        if not '《ＩＤ暱稱》' in self.__ReceiveData[ConnectIndex] or not '《經濟狀況》' in self.__ReceiveData[ConnectIndex] or not '《登入次數》' in self.__ReceiveData[ConnectIndex] or not '《有效文章》' in self.__ReceiveData[ConnectIndex] or not '《目前動態》' in self.__ReceiveData[ConnectIndex] or not '《私人信箱》' in self.__ReceiveData[ConnectIndex] or not '《上次上站》' in self.__ReceiveData[ConnectIndex] or not '《上次故鄉》' in self.__ReceiveData[ConnectIndex] or not '《 五子棋 》' in self.__ReceiveData[ConnectIndex] or not '《象棋戰績》' in self.__ReceiveData[ConnectIndex]:
            self.Log('User info not complete')
            return self.WaitTimeout, None
        #print(self.__ReceiveData[ConnectIndex])
        
        UserID = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《ＩＤ暱稱》') + len('《ＩＤ暱稱》'):self.__ReceiveData[ConnectIndex].find(')') + 1]
        self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find(')') + 1:]
        
        Temp = self.__ReceiveData[ConnectIndex][:self.__ReceiveData[ConnectIndex].find('《登入次數》')]

        UserMoney = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《經濟狀況》') + len('《經濟狀況》'):self.__ReceiveData[ConnectIndex].find('《登入次數》')]
        
        while UserMoney.endswith('m') or UserMoney.endswith(' ') or UserMoney.endswith('[') or UserMoney.endswith('\r') or UserMoney.endswith('\n') or UserMoney.endswith('\x1B'):
            UserMoney = UserMoney[:len(UserMoney) - 1]
        
        self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《登入次數》'):]

        UserLoginTime = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《登入次數》') + len('《登入次數》'):self.__ReceiveData[ConnectIndex].find(')') + 1]
        UserLoginTime = int(re.search(r'\d+', UserLoginTime).group())
        self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find(')') + 1:]
        
        UserPost = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《有效文章》') + len('《有效文章》'):self.__ReceiveData[ConnectIndex].find(')') + 1]
        UserPost = int(re.search(r'\d+', UserPost).group())
        self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find(')') + 1:]
        
        UserState = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《目前動態》') + len('《目前動態》'):self.__ReceiveData[ConnectIndex].find('《私人信箱》')]
        
        while UserState.endswith('m') or UserState.endswith(' ') or UserState.endswith('[') or UserState.endswith('\r') or UserState.endswith('\n') or UserState.endswith('\x1B'):
            UserState = UserState[:len(UserState) - 1]
        
        self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《私人信箱》'):]
        
        UserMail = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《私人信箱》') + len('《私人信箱》'):self.__ReceiveData[ConnectIndex].find('《上次上站》')]
        
        while UserMail.endswith('m') or UserMail.endswith(' ') or UserMail.endswith('[') or UserMail.endswith('\r') or UserMail.endswith('\n') or UserMail.endswith('\x1B'):
            UserMail = UserMail[:len(UserMail) - 1]
        
        self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《上次上站》'):]
        
        UserLastLogin = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《上次上站》') + len('《上次上站》'):self.__ReceiveData[ConnectIndex].find('《上次故鄉》')]
        
        while UserLastLogin.endswith('m') or UserLastLogin.endswith(' ') or UserLastLogin.endswith('[') or UserMail.endswith('\r') or UserMail.endswith('\n') or UserMail.endswith('\x1B'):
            UserLastLogin = UserLastLogin[:len(UserLastLogin) - 1]
        
        self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《上次故鄉》'):]
        
        UserLastIP = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《上次故鄉》') + len('《上次故鄉》'):self.__ReceiveData[ConnectIndex].find('《 五子棋 》')]
        
        while UserLastIP.endswith('m') or UserLastIP.endswith(' ') or UserLastIP.endswith('[') or UserLastIP.endswith('\r') or UserLastIP.endswith('\n') or UserLastIP.endswith('\x1B'):
            UserLastIP = UserLastIP[:len(UserLastIP) - 1]
        
        self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《 五子棋 》'):]
        
        UserFiveChess = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《 五子棋 》') + len('《 五子棋 》'):self.__ReceiveData[ConnectIndex].find('《象棋戰績》')]
        
        while UserFiveChess.endswith('m') or UserFiveChess.endswith(' ') or UserFiveChess.endswith('[') or UserFiveChess.endswith('\r') or UserFiveChess.endswith('\n') or UserFiveChess.endswith('\x1B'):
            UserFiveChess = UserFiveChess[:len(UserFiveChess) - 1]
        
        while UserFiveChess.find('  ') != -1:
            UserFiveChess = UserFiveChess.replace('  ', ' ')
        
        self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《象棋戰績》'):]
        
        UserChess = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('《象棋戰績》') + len('《象棋戰績》'):self.__ReceiveData[ConnectIndex].find('和') + 1]
        
        while UserChess.endswith('m') or UserChess.endswith(' ') or UserChess.endswith('[') or UserChess.endswith('\r') or UserChess.endswith('\n') or UserChess.endswith('\x1B'):
            UserChess = UserChess[:len(UserChess) - 1]
        
        while UserChess.find('  ') != -1:
            UserChess = UserChess.replace('  ', ' ')
        
        self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex][self.__ReceiveData[ConnectIndex].find('和') + 1:]
        
        result = UserInformation(UserID, UserMoney, UserLoginTime, UserPost, UserState, UserMail, UserLastLogin, UserLastIP, UserFiveChess, UserChess)
        
        return self.ErrorCode.Success, result
        
    def readPostFile(self, FileName):
        
        return Util.readPostFile(FileName)
    def getVersion(self):
        return Version
    
    def replyPost(self, Board, Content, ReplyType, PostID='', Index=-1, ConnectIndex = 0):

        if PostID == '' and Index == -1:
            self.Log('輸入參數錯誤')
            return self.ErrorInput
        
        if PostID != '':
            #def __gotoPostByID(self, Board, PostID, ConnectIndex = 0):
            ErrorCode = self.__gotoPostByID(Board, PostID, ConnectIndex)
            if ErrorCode != self.ErrorCode.Success:
                self.Log('replyPost 1 移動至文章失敗', self.LogLevel_DEBUG)
                return ErrorCode
        elif Index != -1:
            #def __gotoPostByIndex(self, Board, PostIndex, ConnectIndex=0):
            ErrorCode = self.__gotoPostByIndex(Board, Index, ConnectIndex)
            if ErrorCode != self.ErrorCode.Success:
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
        self.__CurrentTimeout[ConnectIndex] = 10
        
        while True:
            ErrorCode, Index = self.__sendData(ConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('無法回文', self.LogLevel_DEBUG)
                return self.WaitTimeout
            if ErrorCode != self.ErrorCode.Success:
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
                self.__CurrentTimeout[ConnectIndex] = 10
                Enter = True
            if Index == 1:
                SendMessage = 'Y'
                Enter = True
                self.__CurrentTimeout[ConnectIndex] = 10
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
                self.__CurrentTimeout[ConnectIndex] = 10
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
        
        return self.ErrorCode.Success
    def getMail(self, inputMailIndex, ConnectIndex = 0):
        try:
            MailIndex = int(inputMailIndex)
        except ValueError:
            self.Log('錯誤的信件編號: ' + str(inputMailIndex), self.LogLevel_INFO)
            return self.ErrorInput, None

        if MailIndex < 1:
            self.Log('過小的信件編號: ' + str(MailIndex), self.LogLevel_INFO)
            return self.ErrorInput, None

        ErrorCode = self.__gotoTop(ConnectIndex)
        if ErrorCode != self.ErrorCode.Success:
            print('無法移動至主選單: ' + str(ErrorCode))
            return ErrorCode, None
        
        ErrorCode, NewestMailIndex = self.getNewestMailIndex(ConnectIndex)
        if ErrorCode != self.ErrorCode.Success:
            print('無法移動至主選單: ' + str(ErrorCode))
            return ErrorCode, None

        if NewestMailIndex == 0:
            self.Log('信箱中沒有郵件')
            return self.ErrorCode.Success, None
        else:
            self.Log('信箱中最新郵件編號: ' + str(NewestMailIndex), self.LogLevel_DEBUG)

        if inputMailIndex > NewestMailIndex:
            self.Log('錯誤的輸入!輸入的郵件編號(' + str(inputMailIndex) + ')超過目前的郵件編號(' + str(NewestMailIndex) + ')')
            return self.ErrorInput, None
        
        self.__CurrentTimeout[ConnectIndex] = 2
        self.__readScreen(ConnectIndex, str(inputMailIndex) + '\r\r', ['瀏覽'])

        # print(self.__ReceiveData[ConnectIndex])
        
        MailAuthor = self.__ReceiveData[ConnectIndex]
        MailAuthor = MailAuthor[MailAuthor.find('作者 [0;44m ') + len('作者 [0;44m '):]
        MailAuthor = MailAuthor[:MailAuthor.find('\r')]
        while MailAuthor.endswith(' '):
            MailAuthor = MailAuthor[:-1]

        MailTitle = self.__ReceiveData[ConnectIndex]
        MailTitle = MailTitle[MailTitle.find('標題 [0;44m ') + len('標題 [0;44m '):]
        MailTitle = MailTitle[:MailTitle.find('\r')]
        while MailTitle.endswith(' '):
            MailTitle = MailTitle[:-1]
        
        MailDate = self.__ReceiveData[ConnectIndex]
        MailDate = MailDate[MailDate.find('時間 [0;44m ') + len('時間 [0;44m '):]
        MailDate = MailDate[:MailDate.find('\r')]
        while MailDate.endswith(' '):
            MailDate = MailDate[:-1]

        MailContentTemp = []
        MailContentTemp.append(self.__ReceiveData[ConnectIndex])
        MailContentTemp[0] = MailContentTemp[0][MailContentTemp[0].find('[36m───────────────────────────────────────[37m ') + len('[36m───────────────────────────────────────[37m '):]
        MailContentTemp[0] = MailContentTemp[0][MailContentTemp[0].find('[m') + len('[m'):]

        MailContentTemp[0] = MailContentTemp[0][:MailContentTemp[0].find('瀏覽 第') - 11]

        LastLineCount = [1, 22]
        MailPage = 2
        while '頁 (100%)' not in self.__ReceiveData[ConnectIndex]:
            
            self.__CurrentTimeout[ConnectIndex] = 2
            self.__readScreen(ConnectIndex, str(MailPage) + '\r', ['瀏覽'])
            MailPage += 1

            MailContentTempTemp = self.__ReceiveData[ConnectIndex]
            MailContentTempTemp = MailContentTempTemp[len('[H [2J'):]
            MailContentTempTemp = MailContentTempTemp[:MailContentTempTemp.find('瀏覽 第') - 11]

            LineCountTemp = self.__ReceiveData[ConnectIndex]
            LineCountTemp = LineCountTemp[LineCountTemp.find('目前顯示: 第 ') + len('目前顯示: 第 '):]
            LineCountTemp = LineCountTemp[:LineCountTemp.find(' 行')]
            LastLineCountTemp = list(map(int, re.findall(r'\d+', LineCountTemp)))

            # print(LastLineCount)
            # print(LastLineCountTemp)
            if LastLineCountTemp[0] != LastLineCount[1] + 1:
                SubLine = (LastLineCount[1] + 1) - LastLineCountTemp[0]
                # print('重疊: ' + str(SubLine) + ' 行')

                for i in range(SubLine):
                    MailContentTempTemp = MailContentTempTemp[MailContentTempTemp.find('\r') + 2:]
            
            MailContentTemp.append(MailContentTempTemp)
            LastLineCount = LastLineCountTemp
        MailContent = ''.join(MailContentTemp)
        
        MailIP = MailContent[MailContent.find('ptt.cc), 來自: ') + len('ptt.cc), 來自: '):]
        MailIP = MailIP[:MailIP.find('[')]
        MailIP = MailIP[:MailIP.find('\r')]
        MailIP = MailIP.replace(' ', '')

        MailContent = MailContent[:MailContent.find('※ 發信站: 批踢踢實業坊(ptt.cc), 來自:') - 5]
        
        result = MailInformation(MailAuthor, MailTitle, MailDate, MailContent, MailIP)

        return self.ErrorCode.Success, result
    def getNewestMailIndex(self, ConnectIndex = 0):

        ErrorCode = self.__gotoTop(ConnectIndex)
        if ErrorCode != self.ErrorCode.Success:
            print('無法移動至主選單: ' + str(ErrorCode))
            return ErrorCode, None
        # self.__showScreen()

        CaseList = [
            '我的信箱', 
            '鴻雁往返'
        ]
        SendMessage = 'm'
        Enter = True
        self.__CurrentTimeout[ConnectIndex] = 10
        
        while True:
            ErrorCode, Index = self.__sendData(ConnectIndex, SendMessage, CaseList, Enter)
            if ErrorCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('無法前進至信箱', self.LogLevel_DEBUG)
                return self.WaitTimeout, None
            if ErrorCode != self.ErrorCode.Success:
                self.Log('getMail 錯誤: ' + str(ErrorCode), self.LogLevel_DEBUG)
                return ErrorCode, None
            if Index == 0:
                self.__CurrentTimeout[ConnectIndex] = 10
                SendMessage = 'r'
                Enter = True
                self.Log('進入私人信件區', self.LogLevel_DEBUG)
            elif Index == 1:
                self.Log('進入郵件選單', self.LogLevel_DEBUG)
                break
            else:
                self.Log('else', self.LogLevel_DEBUG)
                self.__showScreen()
                return self.UnknowError, None
        
        self.__CurrentTimeout[ConnectIndex] = 2
        self.__readScreen(ConnectIndex, '0\r$', ['鴻雁往返'])

        MaxMail = 0
        for i in reversed(range(1000)):
            if '/' + str(i) + '篇' in self.__ReceiveData[ConnectIndex]:
                MaxMail = i
                break
        if MaxMail == 0:
            self.Log('取得信箱最高容量失敗')
            return self.UnknowError, None
        self.Log('此信箱最高容量: '+ str(MaxMail), self.LogLevel_DEBUG)

        if self.__Cursor == '>':
            MailIndexTest = 5
        elif self.__Cursor == '●':
            MailIndexTest = 4
        else:
            self.Log('無游標')
            return self.UnknowError, None
        NewestMailIndex = 0
        for i in reversed(range(MaxMail + 1)):
            TestString = self.__Cursor + (' ' * (MailIndexTest - len(str(i)))) + str(i)
            if TestString in self.__ReceiveData[ConnectIndex]:
                NewestMailIndex = i
                break
        if NewestMailIndex == 0:
            self.Log('信箱中沒有郵件')
            return self.ErrorCode.Success, None
        else:
            self.Log('信箱中最新郵件編號: ' + str(NewestMailIndex), self.LogLevel_DEBUG)
        
        return self.ErrorCode.Success, NewestMailIndex

if __name__ == '__main__':

    print('PTT Library v ' + Version.Ver)
    print('Developed by PTT CodingMan')