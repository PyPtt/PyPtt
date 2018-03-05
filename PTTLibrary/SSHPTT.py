import sys
import time
import re
import threading
import progressbar
import socket
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

Version = Version.Ver
LogLevel = Information.LogLevel()
PushType = Information.PushType()
ErrorCode = ErrorCode.ErrorCode()

class _ResponseUnit(object):
    def __init__(self, SendMessage, Refresh):
        self.__SendMessage = SendMessage
        self.__Refresh = Refresh
    def getSendMessaget(self):
        return self.__SendMessage
    def needRefresh(self):
        return self.__Refresh

class _DetectUnit(object):
    def __init__(self, DisplayMsg, DetectTarget, Response, BreakDetect=False, ErrCode=0):
        self.__DisplayMsg = DisplayMsg
        self.__DetectTarget = DetectTarget
        self.__Response = Response
        self.__BreakDetect = BreakDetect
        self.__ErrCode = ErrCode
    def isMatch(self, Screen):
        if self.__DetectTarget in Screen:
            return True
        return False
    def getDisplayMsg(self):
        return self.__DisplayMsg
    def getDetectTarget(self):
        return self.__DetectTarget
    def getResponse(self):
        return self.__Response
    def isBreakDetect(self):
        return self.__BreakDetect
    def getErrorCode(self):
        return self.__ErrCode

class Library(object):
    def __init__(self, ID, Password, kickOtherLogin=True, _LogLevel=-1):

        self.__host = 'ptt.cc'
        self.__ID = ID
        self.__Password = Password
        self.__kickOtherLogin = kickOtherLogin

        self.ReplyPost_Board =                  1
        self.ReplyPost_Mail =                   2

        self.__LoginMode_Login =                1
        self.__LoginMode_Recover =              2
        self.__LoginMode_MultiLogin =           3

        self.__Refresh =                    '\x0C'

        # screen size
        self.width = 80
        self.height = 24
        # screen buffer
        self.screen = ''
        self.buf_size = self.width * self.height

        self.__LogLevel = LogLevel.INFO

        if _LogLevel != -1:
            if _LogLevel < LogLevel.DEBUG or LogLevel.SLIENT < _LogLevel:
                self.Log('LogLevel error: ' + str(_LogLevel))
                return None
            else:
                self.__LogLevel = _LogLevel

        self.__DefaultTimeout =                 5
        
        self.__Cursor =                       '>'
        
        self.__MaxMultiLogin =                  3

        self.__ConnectList = [None] * self.__MaxMultiLogin
        self.__ReceiveData = [''] * self.__MaxMultiLogin
        self.__PreReceiveData = [''] * self.__MaxMultiLogin
        self.__isConnected = [False] * self.__MaxMultiLogin

        self.__isBackground = False

        self.__gotoMainMenu = '\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD'
        ###############################

        self.__KickTimes =                      0
        
        self.__ShowProgressBar =             True
        
        self.__TimeoutCountMax =                3
        
        self.__RequestCount =                   0
        self.__MaxRequestCount =                1
        self.__MinRequestCount =                1
                
        self.__Timeout = [10] * self.__MaxMultiLogin
        self.__SleepTime = [0.5] * self.__MaxMultiLogin
        self.__TimeoutCount = [0] * self.__MaxMultiLogin
        
        self.__CrawPool = []
        
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
        # if kickOtherLogin:
        #     self.Log('此連線將"會"剔除其他登入')
        # else :
        #     self.Log('此連線將"不會"剔除其他登入')
        
        self.__connectRemote(0)
    
    def __showScreen(self, ErrCode, CatchIndex, ConnectIndex=0):
        if self.__LogLevel == LogLevel.DEBUG or Debug:
            print('-' * 50)
            print(self.__PreReceiveData[ConnectIndex])
            print('-' * 50)
            print(self.__ReceiveData[ConnectIndex])
            print('-' * 50)
            print('ErrorCode: ' + str(ErrCode))
            print('CatchIndex: ' + str(CatchIndex))
                                    
    def setLogLevel(self, _LogLevel):
        if _LogLevel < LogLevel.DEBUG or LogLevel.SLIENT < _LogLevel:
            self.Log('LogLevel error')
            return ErrorCode.ErrorInput
        self.__LogLevel = _LogLevel
        return ErrorCode.Success
    def Log(self, Message, _LogLevel=-1):
        if _LogLevel == -1:
            _LogLevel = LogLevel.INFO
        if _LogLevel < LogLevel.DEBUG or LogLevel.CRITICAL < _LogLevel:
            self.Log('LogLevel error')
            return ErrorCode.ErrorInput
        
        if self.__LogLevel <= _LogLevel:
            if _LogLevel == LogLevel.DEBUG:
                Prefix = '[除錯] '
            elif _LogLevel == LogLevel.WARNING:
                Prefix = '[警告] '
            elif _LogLevel == LogLevel.INFO:
                Prefix = '[資訊] '
            elif _LogLevel == LogLevel.CRITICAL:
                Prefix = '[重要] '
        
            Util.Log(Prefix + Message)
        return ErrorCode.Success
    def isLoginSuccess(self, ConnectIndex=0):
        return self.__isConnected[ConnectIndex]
    def __operatePTT(self, ConnectIndex, SendMessage='', CatchTargetList=[], Refresh=False, ExtraWait=0):
        
        SendMessageTimeout = 10.0

        if CatchTargetList == None:
            CatchTargetList = []
        
        ErrCode = ErrorCode.Success
        
        self.__PreReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex]
        self.__ReceiveData[ConnectIndex] = ''

        try:
            if SendMessage != '':

                if Refresh:
                    SendMessage += self.__Refresh
                
                TimeCout = 0
                StartTime = time.time()
                time.sleep(0.02)
                while not self.__ConnectList[ConnectIndex].channel.send_ready():
                    time.sleep(0.01)

                    if TimeCout >= 100:
                        TimeCout = 0
                        NowTime = time.time()
                        if (NowTime - StartTime) >= SendMessageTimeout:
                            return ErrorCode.WaitTimeout, -1
                    TimeCout += 1

                self.__ConnectList[ConnectIndex].channel.send(SendMessage)
            
            # if ExtraWait != 0:
            #     time.sleep(ExtraWait)
            
            TimeCout = 0
            StartTime = time.time()
            time.sleep(0.02)
            while not self.__ConnectList[ConnectIndex].channel.recv_ready():
                time.sleep(0.01)

                if TimeCout >= 100:
                    TimeCout = 0
                    NowTime = time.time()
                    if (NowTime - StartTime) >= SendMessageTimeout:
                        return ErrorCode.WaitTimeout, -1
                TimeCout += 1

            self.__ReceiveData[ConnectIndex] = self.__wait_str(ConnectIndex)

            while self.__ConnectList[ConnectIndex].channel.recv_ready():
                self.__ReceiveData[ConnectIndex] += self.__recv_str(ConnectIndex)
            
        except socket.timeout:
            ErrCode = ErrorCode.WaitTimeout

        self.__ReceiveData[ConnectIndex] = self.__cleanScreen(self.__ReceiveData[ConnectIndex])

        for i in range(len(CatchTargetList)):
            if CatchTargetList[i] in self.__ReceiveData[ConnectIndex]:
                self.__ConnectList[ConnectIndex].channel.settimeout(self.__DefaultTimeout)
                return ErrorCode.Success, i

        self.__ConnectList[ConnectIndex].channel.settimeout(self.__DefaultTimeout)

        return ErrCode, -1
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
        
        global ErrorCode

        self.__isConnected[ConnectIndex] = False

        RetryCount = 0
        Retry = False
        ErrCode = ErrorCode.Success

        while not self.__isConnected[ConnectIndex]:

            if Retry:
                Retry = False
                RetryCount += 1
                if RetryCount == 3:
                    return ErrCode
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
                return ErrorCode.SSHFail
            except Exception as e:
                # print('... Connection failed:', str(e))
                self.Log('連接至 ' + self.__host + ' 連線失敗')
                Retry = True
                ErrCode = ErrorCode.UnknowError
                continue
            except paramiko.SSHException:
                self.Log('建立互動通道失敗')
                Retry = True
                ErrCode = ErrorCode.UnknowError
                continue

            self.Log('建立互動通道成功')
            
            self.__ConnectList[ConnectIndex].channel.settimeout(self.__DefaultTimeout)

            SendMessage = ''
            Refresh = True
            isBreakDetect = False
            # 先後順序代表偵測的優先順序
            DetectTargetList = [
                _DetectUnit(
                    '按任意鍵繼續',
                    '任意鍵', 
                    _ResponseUnit('\x1b\x4fD', False)
                ),
                _DetectUnit(
                    '放棄未完成文章',
                    '有一篇文章尚未完成', 
                    _ResponseUnit('q\r', False)
                ),
                _DetectUnit(
                    '郵件已滿，無法執行任何功能',
                    '郵件選單', 
                    _ResponseUnit(' ', False),
                    BreakDetect=True,
                    ErrCode = ErrorCode.MailBoxFull
                ),
                _DetectUnit(
                    '密碼錯誤',
                    '請檢查帳號及密碼大小寫有無輸入錯誤', 
                    _ResponseUnit(' ', False),
                    BreakDetect=True,
                    ErrCode = ErrorCode.WrongPassword
                ),
                _DetectUnit(
                    '系統負荷過重，重新執行連線',
                    '為避免系統負荷過重, 請稍後再試', 
                    _ResponseUnit(' ', False),
                    BreakDetect=True,
                    ErrCode = ErrorCode.WaitTimeout
                ),
                _DetectUnit(
                    '更新與同步線上使用者及好友名單',
                    '更新與同步線上使用者及好友名單', 
                    _ResponseUnit('\x1b\x4fD\x1b\x4fD', False)
                ),
                _DetectUnit(
                    '刪除重複登入的連線' if self.__kickOtherLogin else '不刪除重複登入的連線',
                    '刪除其他重複登入的連線', 
                    _ResponseUnit('y\r' if self.__kickOtherLogin else 'n\r', True)
                ),
                _DetectUnit(
                    '刪除錯誤嘗試紀錄',
                    '您要刪除以上錯誤嘗試的記錄嗎', 
                    _ResponseUnit('y\r', False)
                ),
                _DetectUnit(
                    '登入成功',
                    '【主功能表】', 
                    _ResponseUnit(' ', False),
                    BreakDetect=True,
                ),
                _DetectUnit(
                    '輸入密碼',
                    '請輸入您的密碼:', 
                    _ResponseUnit(self.__Password + '\r\r', True)
                ),
                _DetectUnit(
                    '輸入帳號',
                    '請輸入代號，或以 guest 參觀，或以 new 註冊:', 
                    _ResponseUnit(self.__ID + '\r', True)
                ),
            ]
            
            while not isBreakDetect:
                ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
                if ErrCode == ErrorCode.WaitTimeout:
                    self.Log('登入超時重新嘗試')
                    break
                elif ErrCode != ErrorCode.Success:
                    self.Log('登入操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                    return ErrCode
                
                # self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)

                isDetectedTarget = False

                for DetectTarget in DetectTargetList:
                    if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                        self.Log(DetectTarget.getDisplayMsg())

                        SendMessage = DetectTarget.getResponse().getSendMessaget()
                        Refresh = DetectTarget.getResponse().needRefresh
                        
                        isDetectedTarget = True
                        if DetectTarget.isBreakDetect():
                            self.__isConnected[ConnectIndex] = True
                            isBreakDetect = True
                            ErrCode = DetectTarget.getErrorCode()
                        break

                if not isDetectedTarget:
                    self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)
                    self.Log('無法解析的狀態 以上是最後兩個畫面')
                    sys.exit()
            if ErrCode == ErrorCode.WaitTimeout:
                Retry = True
            elif ErrCode != ErrorCode.Success:
                return ErrCode
            
        if '> (' in self.__ReceiveData[ConnectIndex]:
            self.Log('新式游標模式')
            self.__Cursor = '>'
        elif '●(' in self.__ReceiveData[ConnectIndex]:
            self.Log('舊式游標模式')
            self.__Cursor = '●'
        else:
            self.Log('無法偵測游標')
            return ErrorCode.UnknowError
        return ErrorCode.Success
    def logout(self, ConnectIndex=-1):
        
        if ConnectIndex == -1:
            
            self.Log('準備登出所有頻道')
            
            for index in range(self.__MaxMultiLogin):
                self.__isConnected[index] = False
            
            for index in range(self.__MaxMultiLogin):
                if self.__ConnectList[index] == None:
                    # self.Log('連線 ' + str(index) + ' 未連接')
                    continue
                self.Log('頻道 ' + str(index) + ' 登出', LogLevel.DEBUG)
                
                SendMessage = '\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD g\ry\r'
                Refresh = True
                ExtraWait = 0

                ErrCode, CatchIndex = self.__operatePTT(index, SendMessage=SendMessage, CatchTargetList=['按任意鍵繼續'], Refresh=Refresh, ExtraWait=ExtraWait)
                if ErrCode != 0:
                    # self.Log('頻道 ' + str(index) + ' 登出失敗 錯誤碼: ' + str(ErrCode))
                    self.__showScreen(ErrCode, CatchIndex, ConnectIndex)
                    return ErrorCode.UnknowError
                self.Log('頻道 ' + str(index) + ' 登出成功')
                
        return ErrorCode.Success
    def getNewestPostIndex(self, Board):

        for i in range(3):
            ErrCode, NewestIndex = self.__getNewestPostIndex(Board, ConnectIndex = 0)
            if ErrCode == ErrorCode.Success:
                return ErrCode, NewestIndex
        return ErrCode, NewestIndex
    def __getNewestPostIndex(self, Board, ConnectIndex = 0):
        
        result = 0
        
        CatchList = [
            # 0
            '文章選讀',
        ]

        SendMessage = '\x1b\x4fD\x1b\x4fD\x1b\x4fDqs' + Board + '\r\x03\x03 0\r$'
        Refresh = True
        ExtraWait = 0

        ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=Refresh, ExtraWait=ExtraWait)
        if ErrCode != ErrorCode.Success:
            return ErrCode, result

        # print(self.__ReceiveData[ConnectIndex])

        AllIndex = re.findall(r'\d+ ', self.__ReceiveData[ConnectIndex])
        
        if len(AllIndex) == 0:
            self.__showScreen(ErrCode, CatchIndex, ConnectIndex)
            return ErrorCode.UnknowError, result

        AllIndex = list(set(map(int, AllIndex)))

        AllIndex.sort(reverse=True)

        # print(AllIndex)

        for IndexTemp in AllIndex:
            # 確認是否連續 只有文章編號才可能連續
            isContinue = True

            for i in range(1, 3):
                if str(IndexTemp - i) not in self.__ReceiveData[ConnectIndex]:
                    isContinue = False
                    break
            
            if isContinue:
                result = IndexTemp
                break
        
        if result == 0:
            return ErrorCode.ParseError, result
        
        # 確認是否有因為上篇文章是數字結尾導致判斷錯誤的情況
        for i in range(1, 20):
            if str(result + 1) in self.__ReceiveData[ConnectIndex]:
                result += 1
            else: 
                break

        return ErrorCode.Success, result
    def post(self, Board, Title, Content, PostType, SignType):
        
        ConnectIndex = 0
        
        # 前進至板面

        if '看板《' + Board + '》' in self.__ReceiveData[ConnectIndex] and '文章選讀' in self.__ReceiveData[ConnectIndex]:
            self.Log('已經位於 ' + Board + ' 板', LogLevel.DEBUG)
        else:
            CatchList = [
                # 0
                '文章選讀',
            ]

            SendMessage = '\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fDqs' + Board + '\r\x03\x03 '
        
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=True)
            if ErrCode != ErrorCode.Success:
                return ErrCode

            if CatchIndex == -1:
                self.Log('前進至 ' + Board + '板失敗')
                print(self.__ReceiveData[ConnectIndex])
                return ErrorCode.UnknowError

        # 確認是否有發文權限

        CatchList = [
            # 0
            '或不選',
            # 1
            '使用者不可發言',
        ]

        SendMessage = '\x10'
        Refresh = False
        ExtraWait = 0

        Retry = False
        RetryCount = 0

        while True:
            
            if Retry:
                Retry = False
                RetryCount += 1
                if RetryCount == 3:
                    return ErrCode
            else:
                RetryCount = 0

            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=Refresh, ExtraWait=ExtraWait)
            if ErrCode != ErrorCode.Success:
                return ErrCode

            SendMessage = ' '
            Refresh = False
            ExtraWait = 0

            if CatchIndex == 0:
                self.Log('具備發文權限', LogLevel.DEBUG)
                break
            elif CatchIndex == 1:
                self.Log('你被水桶惹 QQ')
                return ErrorCode.NoPermission
            else:
                self.__showScreen(ErrCode, CatchIndex, ConnectIndex)
                return ErrorCode.UnknowError

        SendMessage = str(PostType) + '\r' + str(Title) + '\r' + str(Content) + '\x18'
        self.Log('送出文章', LogLevel.DEBUG)

        Refresh = True
        ExtraWait = 0

        CatchList = [
            # 0
            '確定要儲存檔案嗎',
        ]

        ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=Refresh, ExtraWait=ExtraWait)
        if ErrCode != ErrorCode.Success:
            return ErrCode

        if CatchIndex == 0:
            self.Log('儲存檔案', LogLevel.DEBUG)
            SendMessage = 's\r'
        else:
            self.__showScreen(ErrCode, CatchIndex, ConnectIndex)
            return ErrorCode.UnknowError

        CatchList = [
            # 0
            '任意鍵繼續', 
            # 1
            'x=隨機', 
            # 2
            '文章選讀',
        ]
        
        Refresh = True
        ExtraWait = 0
        while True:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=Refresh, ExtraWait=ExtraWait)
            if ErrCode != ErrorCode.Success:
                return ErrCode

            if CatchIndex == 0:
                break
            elif CatchIndex == 1:
                self.Log('選擇簽名檔: ' + str(SignType), LogLevel.DEBUG)
                SendMessage = str(SignType) + '\r'
            elif CatchIndex == 2:
                break
            else:
                self.__showScreen(ErrCode, CatchIndex, ConnectIndex = ConnectIndex)
                return ErrorCode.UnknowError
        
        return ErrorCode.Success
    def push(self, Board, inputPushType, PushContent, PostID='', PostIndex=0):
        
        PostIndex = int(PostIndex)
        PostID = str(PostID)

        if len(Board) == 0:
            self.Log('看板名稱輸入錯誤: ' + str(Board))
            return ErrorCode.ErrorInput

        if PostIndex != 0 and PostID != '':
            self.Log('文章編號與代碼輸入錯誤: 同時輸入')
            return ErrorCode.ErrorInput

        if PostIndex == 0 and PostID == '':
            self.Log('文章編號與代碼輸入錯誤: 皆無輸入')
            return ErrorCode.ErrorInput

        MaxPushLength = 45

        self.__PushShow = [False * 5]
        PushList = []
        Temp = ''

        TempStartIndex = 0
        TempEndIndex = TempStartIndex + 1

        while TempEndIndex < len(PushContent):

            Temp = ''
            while len(Temp.encode('big5')) < MaxPushLength:
                Temp = PushContent[TempStartIndex:TempEndIndex]
                
                if not len(Temp.encode('big5')) < MaxPushLength:
                    break
                elif PushContent.endswith(Temp):
                    break
                    
                TempEndIndex += 1
            
            PushList.append(Temp)
            
            TempStartIndex = TempEndIndex
            TempEndIndex = TempStartIndex + 1
        
        for Push in PushList:
            # print('Push:', Push)
            ErrCode = self.__push(Board, inputPushType, Push, PostID=PostID, PostIndex=PostIndex)

            if ErrCode != ErrorCode.Success:
                return ErrCode
        return ErrCode
    def __push(self, Board, inputPushType, PushContent, PostID='', PostIndex=0):
        
        ConnectIndex=0
        
        SendMessage = ''

        if '看板《' + Board + '》' in self.__ReceiveData[ConnectIndex] and '文章選讀' in self.__ReceiveData[ConnectIndex]:
            self.Log('已經位於 ' + Board + ' 板', LogLevel.DEBUG)
        else:
            # 前進至板面
            SendMessage += '\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fDqs' + Board + '\r\x03\x03 '
        
        # 前進至文章

        if PostID != '':
            SendMessage += '#' + PostID + '\r'
        else:
            SendMessage += str(PostIndex) + '\r'

        # 查看是否具備推文權限
        SendMessage += 'X'

        CatchList = [
            # 0
            '您覺得這篇文章',
            # 1
            '禁止快速連續推文',
            # 2
            '禁止短時間內大量推文',
            # 3
            '使用者不可發言',
            # 4
            '加註方式',
            # 5
            '◆ 本文已刪除',
        ]

        ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=True)
        if ErrCode != ErrorCode.Success:
            return ErrCode
        
        if CatchIndex == 0:
                
            self.Log('具備推文權限', LogLevel.DEBUG)

            if '值得推薦' in self.__ReceiveData[ConnectIndex]:
                Push = True
            else:
                Push = False

            if '給它噓聲' in self.__ReceiveData[ConnectIndex]:
                Boo = True
            else:
                Boo = False
            
            if '→註解' in self.__ReceiveData[ConnectIndex]:
                Arrow = True
            else:
                Arrow = False
            
            if inputPushType == PushType.Push:
                if not Push:
                    inputPushType = PushType.Arrow
            elif inputPushType == PushType.Boo:
                if not Boo:
                    inputPushType = PushType.Arrow
            elif inputPushType == PushType.Arrow:
                if not Arrow:
                    inputPushType = PushType.Push
            else:
                return ErrorCode.ErrorInput

            self.Log('準備推文')
            SendMessage = str(inputPushType) + str(PushContent) + '\ry\r'

        elif CatchIndex == 1:
            self.Log('禁止快速推文')
            return ErrorCode.NoFastPush
        elif CatchIndex == 2:
            self.Log('禁止機器人快速推文')
            return ErrorCode.NoFastPush
        elif CatchIndex == 3:
            self.Log('你被水桶惹 QQ')
            return ErrorCode.NoPermission
        elif CatchIndex == 4:
            if not self.__PushShow[CatchIndex]:
                self.Log('作者本人使用箭頭')
                self.__PushShow[CatchIndex] = True
            SendMessage = str(PushContent) + '\ry\r'
        elif CatchIndex == 5:
            self.Log('文章已經被刪除')
            return ErrorCode.PostDeleted
        else:
            self.__showScreen(ErrCode, CatchIndex, ConnectIndex)
            return ErrorCode.UnknowError
        
        CatchList = []

        ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=True)
        if ErrCode != ErrorCode.Success:
            return ErrCode

        # print(self.__ReceiveData[ConnectIndex])

        return ErrorCode.Success

    def __parsePostMail(self, PostList):

        LastIndex = len(PostList[0]) - PostList[0][::-1].find(')')

        PostAuthor = PostList[0][8:LastIndex]
        PostTitle = PostList[1][5:]
        while PostTitle.endswith(' '):
            PostTitle = PostTitle[:-1]
        PostDate = PostList[2][5:]
        while PostDate.endswith(' '):
            PostDate = PostDate[:-1]
        
        PostContentEndIndex = 0
        PostIP = 'Unknow IP'
        for i in range(5, len(PostList)):
            if '※ 發信站: 批踢踢實業坊(ptt.cc), 來自: ' in PostList[i]:
                while PostList[i].endswith(' '):
                    PostList[i] = PostList[i][:-1]
                PostIP = PostList[i].split(' ').pop()
                break
            if '※ 編輯:' in PostList[i]:
                while PostList[i].endswith(' '):
                    PostList[i] = PostList[i][:-1]
                TempList = PostList[i].split(' ')
                TempList.pop()
                TempList.pop()
                PostIP = TempList.pop()[1:-2]
        for i in range(5, len(PostList)):
            # print(PostList[i])
            if '※ 發信站: 批踢踢實業坊(ptt.cc), 來自: ' in PostList[i]:
                
                # print(PostIP, '==')
                PostContentEndIndex = i
                break
        PostContent = '\n'.join(PostList[5:PostContentEndIndex])

        PushList = []

        # print('-' * 30)
        for i in range(PostContentEndIndex + 2, len(PostList)):
            PushLine = PostList[i]
            while PushLine.startswith(' '):
                PushLine = PushLine[1:]
            # print(PushLine)

            if len(PushLine) == 0:
                continue

            CurrentPushType = PushType.Unknow

            if PushLine.startswith('推'):
                CurrentPushType = PushType.Push
            elif PushLine.startswith('噓'):
                CurrentPushType = PushType.Boo
            elif PushLine.startswith('→'):
                CurrentPushType = PushType.Arrow
            
            PushLine = PushLine[2:]
            PushAuthor = PushLine[:PushLine.find(':')]
            PushLine = PushLine[PushLine.find(':') + 1:]
            
            PushLineList = PushLine.split(' ')

            # print(len(PushLineList))

            if len(PushLineList) < 2:
                continue

            PushLineTime = PushLineList.pop()
            PushLineTime = PushLineList.pop() + ' ' + PushLineTime

            PushLineList = [x for x in PushLineList if x != '']

            PushContent = ' '.join(PushLineList)
            # while PushContent.endswith(' '):

            # print(CurrentPushType)
            # print(PushAuthor)
            # print(PushContent, '==')
            # print(PushLineTime)
            
            CurrentPush = Information.PushInformation(CurrentPushType, PushAuthor, PushContent, PushLineTime)
            PushList.append(CurrentPush)

        # print('PostAuthor:', PostAuthor, '==')
        # print('PostTitle:', PostTitle, '==')
        # print('PostDate:', PostDate, '==')
        # print('PostContent:', PostContent, '==')

        return PostAuthor, PostTitle, PostDate, PostContent, PostIP, PushList
    def getPostInfo(self, Board, PostID='', PostIndex=0):
        ConnectIndex = 0
        
        result = None
        
        PostIndex = int(PostIndex)
        PostID = str(PostID)

        if len(Board) == 0:
            self.Log('看板名稱輸入錯誤: ' + str(Board))
            return ErrorCode.ErrorInput, result

        if PostIndex != 0 and PostID != '':
            self.Log('文章編號與代碼輸入錯誤: 同時輸入')
            return ErrorCode.ErrorInput, result

        if PostIndex == 0 and PostID == '':
            self.Log('文章編號與代碼輸入錯誤: 皆無輸入')
            return ErrorCode.ErrorInput, result

        SendMessage = ''

        if '看板《' + Board + '》' in self.__ReceiveData[ConnectIndex] and '文章選讀' in self.__ReceiveData[ConnectIndex]:
            self.Log('已經位於 ' + Board + ' 板', LogLevel.DEBUG)
        else:
            # 前進至板面
            SendMessage += '\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fDqs' + Board + '\r\x03\x03 '
        
        # 前進至文章

        if PostID != '':
            SendMessage += '#' + PostID + '\rQ'
        else:
            SendMessage += str(PostIndex) + '\rQ'

        CatchList = [
            # 0
            '找不到這個文章代碼',
            # 1
            '─  ─  ─  ─  ─  ─  ─  ─  ',

        ]
        
        ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=True)
        if ErrCode != ErrorCode.Success:
            return ErrCode, result

        # print(self.__ReceiveData[ConnectIndex])

        if CatchIndex == 0:
            self.Log('此文章代碼不存在')
            return ErrorCode.PostNotFound, result
        elif CatchIndex == 1:
            # print(self.__ReceiveData[ConnectIndex])

            InformationEnd = '└  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ┘'
            screen = self.__ReceiveData[ConnectIndex]
            screen = screen[screen.find(CatchList[1]) + len(CatchList[1]):screen.find(InformationEnd)]

            screen = screen[screen.find('文章代碼(AID): #') + len('文章代碼(AID): #'):]
            if PostID == '':
                PostID = screen[:screen.find(' ')]

            PostTitle = screen[screen.find('ptt.cc') + len('ptt.cc') + 2:]
            PostTitle = PostTitle[:PostTitle.find('│')]
            while PostTitle.endswith(' ') or PostTitle.endswith('\r'):
                PostTitle = PostTitle[:-1]
            
            PostURL = screen[screen.find('https://www.ptt.cc/bbs'):]
            PostURL = PostURL[:PostURL.find(' ')]

            if '價格記錄' in screen:
                PostMoney = -1
            else:
                
                PostMoney = screen
                # print(len(PostMoney))
                print(PostMoney)
                for c in '這一篇文章值':
                    if c in PostMoney:
                        PostMoney = PostMoney[PostMoney.find(c):]
                print(PostMoney)
                # 
                try:
                    PostMoney = int(re.search(r'\d+', PostMoney).group())
                except AttributeError:
                    print('解析文章價錢失敗', screen)

                # print(screen)
        else:
            # print('-' * 50)
            # print(self.__ReceiveData[ConnectIndex])
            # self.Log('文章已經被刪除')
            return ErrorCode.PostDeleted, result

        SendMessage = '\x03\r'

        CatchList = [
            # 0
            '(  ←)離開',
            # 1
            '這份文件是可播放的文字動畫',
        ]
        
        ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=True)
        if ErrCode != ErrorCode.Success:
            return ErrCode, result

        if CatchIndex == 0:
            # print(self.__ReceiveData[ConnectIndex])
            # 
            self.Log('進入文章成功')
        elif CatchIndex == 1:
            SendMessage = 'n'

            CatchList = [
                # 0
                '(  ←)離開',
            ]
            
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=True)
            if ErrCode != ErrorCode.Success:
                return ErrCode, result
            if CatchIndex == 0:
                self.Log('停止播放動畫')
            else:
                self.Log('停止播放動畫失敗')
            
        else:
            
            LastLine = self.__ReceiveData[ConnectIndex].split('\n').pop()
            if '瀏覽' in LastLine or '目前顯示' in LastLine or '離開' in LastLine:
                self.Log('進入文章成功')
            else:
                print('進入文章 error')
                return ErrorCode.UnknowError, result

        LastLine = self.__ReceiveData[ConnectIndex].split('\n').pop()
        # print(LastLine)
        TotalPageTemp = re.findall(r'\d+', LastLine)
        TotalPage = list(map(int, TotalPageTemp))[1]
        # print(TotalPage)

        PageIndex = 2
        LastPageIndex = [1, 22]

        PostList = self.__ReceiveData[ConnectIndex].split('\n')[:-1]

        for i in range(TotalPage - 1):
        # while not '(100%)  目前顯示:' in self.__ReceiveData[ConnectIndex]:
            # print(PageIndex, TotalPage)
            SendMessage = str(PageIndex) + '\r'
            CatchList = [
                # 0
                '(  ←)離開',
            ]
            
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=True)
            if ErrCode != ErrorCode.Success:
                return ErrCode, result
            # print('=' * 50)
            # print(self.__ReceiveData[ConnectIndex])
            
            if CatchIndex == 0:
                PageIndex += 1

                Temp = self.__ReceiveData[ConnectIndex]
                Temp = Temp.replace('[2J', '')
                # while not PostContentTemp.startswith('推') and not PostContentTemp.startswith('→') and not PostContentTemp.startswith('噓'):
                #     PostContentTemp = PostContentTemp[1:]

                TempList = Temp.split('\n')
                
                PageLineRange = TempList.pop()
                PageLineRange = re.findall(r'\d+', PageLineRange)
                PageLineRange = list(map(int, PageLineRange))[3:]

                # print('PageLineRange:', PageLineRange)
                
                OverlapLine = LastPageIndex[1] - PageLineRange[0] + 1
                # print('OverlapLine:', OverlapLine)
                if OverlapLine >= 1:
                    # print('重疊', OverlapLine, '行')
                    TempList = TempList[OverlapLine:]
                
                LastPageIndex = PageLineRange

                PostList.extend(TempList)
            else:
                print('換頁錯誤')
        
        # for line in PostList:
        #     print('list line:', line)
        # return PostAuthor, PostTitle, PostTime, PostContent, PushList
        PostAuthor, PostTitle, PostDate, PostContent, PostIP, PushList = self.__parsePostMail(PostList)

        # print('PostID:', PostID)
        # print('PostTitle:', PostTitle)
        # print('PostURL:', PostURL)
        # print('PostMoney:', PostMoney)
        # print('PostAuthor:', PostAuthor)
        # print('PostDate:', PostDate)
        # print('PostContent:', PostContent + '=')
        # print('PostIP:', PostIP + '=')
        # print('-' * 50)

        result = Information.PostInformation(Board, PostID, PostAuthor, PostDate, PostTitle, PostURL, PostMoney, PostContent, PostIP, PushList)
        return ErrorCode.Success, result
    def mail(self, UserID, MailTitle, MailContent, SignType):
        
        ConnectIndex = 0

        MailContentListTemp = MailContent.split('\r')
        MailContentList = []

        MailContentListIndex = 0

        while len(MailContentListTemp) != 0:
            if len(MailContentListTemp) >= 20:
                MailContentList.append('\r'.join(MailContentListTemp[0:20]))
                for i in range(20):
                    MailContentListTemp.pop(0)
            else:
                MailContentList.append('\r'.join(MailContentListTemp))
                break
        
        SendMessage = self.__gotoMainMenu + 'M\rS\r' + UserID + '\r' + MailTitle + '\r'
        # MailContent + '\x18s\r' + str(SignType) + '\ry\r'
        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '編輯文章 ' + str(int((MailContentListIndex + 1) * 100 / len(MailContentList))) + ' %',
                '編輯文章', 
                _ResponseUnit(MailContentList[MailContentListIndex], True),
            ),
        ]
        
        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('超時')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                return ErrCode
            
            # self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)

            isDetectedTarget = False

            for i in range(len(DetectTargetList)):
                if DetectTargetList[i].isMatch(self.__ReceiveData[ConnectIndex]):
                    self.Log(DetectTargetList[i].getDisplayMsg())

                    SendMessage = DetectTargetList[i].getResponse().getSendMessaget()
                    Refresh = DetectTargetList[i].getResponse().needRefresh
                    
                    isDetectedTarget = True
                    if DetectTargetList[i].isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTargetList[i].getErrorCode()
                    
                    if '編輯文章' in DetectTargetList[i].getDisplayMsg():

                        MailContentListIndex += 1
                        if MailContentListIndex == len(MailContentList):
                            isBreakDetect = True
                            break

                        DetectTargetList[i] = _DetectUnit(
                            '編輯文章 ' + str(int((MailContentListIndex + 1) * 100 / len(MailContentList))) + ' %',
                            '編輯文章', 
                            _ResponseUnit('\r' + MailContentList[MailContentListIndex], True),
                        )

                    break

            if not isDetectedTarget:
                self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態 以上是最後兩個畫面')
                sys.exit()
        if ErrCode != ErrorCode.Success:
            return ErrCode
        
        SendMessage = '\x18'
        Refresh = True
        isBreakDetect = False
        
        DetectTargetList = [
            _DetectUnit(
                '任意鍵繼續',
                '任意鍵', 
                _ResponseUnit(self.__gotoMainMenu, False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '儲存檔案',
                '確定要儲存檔案嗎', 
                _ResponseUnit('s\r', False),
            ),
            _DetectUnit(
                '自存底稿',
                '是否自存底稿', 
                _ResponseUnit('y\r', True),
            ),
            _DetectUnit(
                '電子郵件選單',
                '【電子郵件】', 
                _ResponseUnit('\x1b\x4fD', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '電子郵件選單',
                '【主功能表】', 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
        ]
        
        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('超時')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                return ErrCode
            
            # self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)

            isDetectedTarget = False

            for i in range(len(DetectTargetList)):
                if DetectTargetList[i].isMatch(self.__ReceiveData[ConnectIndex]):
                    self.Log(DetectTargetList[i].getDisplayMsg())

                    SendMessage = DetectTargetList[i].getResponse().getSendMessaget()
                    Refresh = DetectTargetList[i].getResponse().needRefresh
                    
                    isDetectedTarget = True
                    if DetectTargetList[i].isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTargetList[i].getErrorCode()

                    break

            if not isDetectedTarget:
                self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態 以上是最後兩個畫面')
                sys.exit()
        if ErrCode != ErrorCode.Success:
            return ErrCode

        return ErrorCode.Success
    def getTime(self):
        
        ConnectIndex = 0

        # \x1b\x4fA (上, 下右左 BCD)
        SendMessage = '\x1b\x4fC\x1b\x4fD'
        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '於主功能表取得系統時間',
                '【主功能表】', 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
        ]
        
        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('超時')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                return ErrCode
            
            # self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)

            isDetectedTarget = False

            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                    self.Log(DetectTarget.getDisplayMsg(), _LogLevel=LogLevel.DEBUG)

                    SendMessage = DetectTarget.getResponse().getSendMessaget()
                    Refresh = DetectTarget.getResponse().needRefresh
                    
                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                    break

            if not isDetectedTarget:
                self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態 以上是最後兩個畫面')
                sys.exit()
        if ErrCode != ErrorCode.Success:
            return ErrCode
        
        LastLine = self.__ReceiveData[ConnectIndex].split('\n').pop()
        LastLineList = list(map(int, re.findall(r'\d+', LastLine)))
        result = str(LastLineList[2]) + ':' + str(LastLineList[3])
        # print(result)

        return ErrorCode.Success, result
    
    def getUserInfo(self, UserID):
        ConnectIndex = 0

        SendMessage = '\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fDT\rQ\r' + UserID + '\r'
        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '取得使用者資料頁面',
                '任意鍵', 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '查無該使用者',
                '【聊天說話】', 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.NoUser
            ),
        ]
        
        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('超時')
                return ErrCode, None
            elif ErrCode != ErrorCode.Success:
                self.Log('操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                return ErrCode, None
            
            # self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)

            isDetectedTarget = False

            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                    self.Log(DetectTarget.getDisplayMsg(), _LogLevel=LogLevel.DEBUG)

                    SendMessage = DetectTarget.getResponse().getSendMessaget()
                    Refresh = DetectTarget.getResponse().needRefresh
                    
                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                    break

            if not isDetectedTarget:
                self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態 以上是最後兩個畫面')
                sys.exit()
        if ErrCode != ErrorCode.Success:
            return ErrCode, None
        
        UserPageList = self.__ReceiveData[ConnectIndex].split('\n')
        # for i in range(len(UserPageList)):
        #     print('Q', UserPageList[i])
        
        UserPage = '\n'.join(UserPageList[2:6])
        # print(UserPage)
        UserDataList = list(map(int, re.findall(r'\d+', UserPage)))
        # print(UserDataList)
        # print(len(UserDataList)) 19

        LoginTime = UserDataList[0]
        LegalPost = UserDataList[1]
        IllegalPost = UserDataList[2]
        LastIP = str(UserDataList[9]) + '.' + str(UserDataList[10]) + '.' + str(UserDataList[11]) + '.' + str(UserDataList[12])
        FiveChess = UserDataList[13:16]
        Chess = UserDataList[16:19]

        ID = UserPageList[1]
        ID = ID[ID.find('《ＩＤ暱稱》') + len('《ＩＤ暱稱》') : ID.find('《經濟狀況》')]
        while ID.startswith(' '):
            ID = ID[1:]
        while ID.endswith(' '):
            ID = ID[:-1]
        
        Money = UserPageList[1]
        Money = Money[Money.find('《經濟狀況》') + len('《經濟狀況》') :]
        while Money.startswith(' '):
            Money = Money[1:]
        while Money.endswith(' '):
            Money = Money[:-1]

        State = UserPageList[3]
        State = State[State.find('《目前動態》') + len('《目前動態》') : State.find('《私人信箱》')]
        while State.startswith(' '):
            State = State[1:]
        while State.endswith(' '):
            State = State[:-1]
        
        Mail = UserPageList[3]
        Mail = Mail[Mail.find('《私人信箱》') + len('《私人信箱》') :]
        while Mail.startswith(' '):
            Mail = Mail[1:]
        while Mail.endswith(' '):
            Mail = Mail[:-1]

        LastLogin = UserPageList[4]
        LastLogin = LastLogin[LastLogin.find('《上次上站》') + len('《上次上站》') : LastLogin.find('《上次故鄉》')]
        while LastLogin.startswith(' '):
            LastLogin = LastLogin[1:]
        while LastLogin.endswith(' '):
            LastLogin = LastLogin[:-1]

        # print('ID:', ID)
        # print('Money:', Money)
        # print('State:', State)
        # print('Mail:', Mail)
        # print('LastLogin:', LastLogin)

        # print('LoginTime:', LoginTime)
        # print('LegalPost:', LegalPost)
        # print('IllegalPost:', IllegalPost)
        # print('LastIP:', LastIP)
        # print('FiveChess:', FiveChess)
        # print('Chess:', Chess)

        result = Information.UserInformation(ID, Money, LoginTime, LegalPost, IllegalPost, State, Mail, LastLogin, LastIP, FiveChess, Chess)

        return ErrorCode.Success, result
    def getNewestMailIndex(self):

        ConnectIndex = 0
        result = 0

        SendMessage = '\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fDM\rR\r0\r$'
        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '進入信箱',
                '鴻雁往返', 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
        ]
        
        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('超時')
                return ErrCode, None
            elif ErrCode != ErrorCode.Success:
                self.Log('操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                return ErrCode, None
            
            # self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)

            isDetectedTarget = False

            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                    self.Log(DetectTarget.getDisplayMsg(), _LogLevel=LogLevel.DEBUG)

                    SendMessage = DetectTarget.getResponse().getSendMessaget()
                    Refresh = DetectTarget.getResponse().needRefresh
                    
                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                    break

            if not isDetectedTarget:
                self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態 以上是最後兩個畫面')
                sys.exit()
        if ErrCode != ErrorCode.Success:
            return ErrCode, None

        MailBoxLineList = self.__ReceiveData[ConnectIndex].split('\n')

        # for i in range(len(MailBoxLineList)):
        #     print('line', i,MailBoxLineList[i])

        result = list(map(int, re.findall(r'\d+', MailBoxLineList[3])))[0]

        return ErrorCode.Success, result
    def getMail(self, MailIndex):

        result = None
        ConnectIndex = 0

        if MailIndex <= 0:
            self.Log('錯誤的輸入: ' + str(MailIndex))
            return ErrorCode.ErrorInput, result
        ErrCode, NewestMailIndex = self.getNewestMailIndex()
        if ErrCode != ErrorCode.Success:
            self.Log('取得最新信箱編號失敗: ' + str(ErrCode))
            return ErrCode, result
        if MailIndex >= NewestMailIndex:
            self.Log('錯誤的輸入: ' + str(MailIndex))
            return ErrorCode.ErrorInput, result
        
        SendMessage = str(MailIndex) + '\r\r'
        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '讀取信件完畢',
                '(100%)  目前顯示: 第', 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '讀取信件...',
                '目前顯示', 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
        ]
        
        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('超時')
                return ErrCode, None
            elif ErrCode != ErrorCode.Success:
                self.Log('操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                return ErrCode, None
            
            # self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)

            isDetectedTarget = False

            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                    self.Log(DetectTarget.getDisplayMsg(), _LogLevel=LogLevel.DEBUG)

                    SendMessage = DetectTarget.getResponse().getSendMessaget()
                    Refresh = DetectTarget.getResponse().needRefresh
                    
                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                    break

            if not isDetectedTarget:
                self.__showScreen(ErrCode, CatchIndex, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態 以上是最後兩個畫面')
                sys.exit()
        if ErrCode != ErrorCode.Success:
            return ErrCode, None

        MailLineList = self.__ReceiveData[ConnectIndex].split('\n')

        for line in MailLineList:
            print('Q', line)

        return ErrorCode.Success, result
        ###############################################
        try:
            MailIndex = int(inputMailIndex)
        except ValueError:
            self.Log('錯誤的信件編號: ' + str(inputMailIndex), LogLevel.INFO)
            return self.ErrorInput, None

        if MailIndex < 1:
            self.Log('過小的信件編號: ' + str(MailIndex), LogLevel.INFO)
            return self.ErrorInput, None

        ErrCode = self.__gotoTop(ConnectIndex)
        if ErrCode != ErrorCode.Success:
            print('無法移動至主選單: ' + str(ErrorCode))
            return ErrCode, None
        
        ErrCode, NewestMailIndex = self.getNewestMailIndex(ConnectIndex)
        if ErrCode != ErrorCode.Success:
            print('無法移動至主選單: ' + str(ErrorCode))
            return ErrCode, None

        if NewestMailIndex == 0:
            self.Log('信箱中沒有郵件')
            return ErrorCode.Success, None
        else:
            self.Log('信箱中最新郵件編號: ' + str(NewestMailIndex), LogLevel.DEBUG)

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

        return ErrorCode.Success, result
    def crawlBoard(self, Board, PostHandler, StartIndex=0, EndIndex=0, ShowProgressBar=True):
    
        self.__PostHandler = PostHandler
    
        DefaultThreadNumber = 32
        
        self.Log('Into crawlBoard', LogLevel.DEBUG)
        
        self.__ShowProgressBar = ShowProgressBar
        
        if StartIndex == 0 and EndIndex == 0:
            self.Log('爬行 ' + Board + ' 板所有文章')
            
            ErrCode, EndIndex = self.getNewestPostIndex(Board)
            if ErrCode == ErrorCode.Success:
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
                    if self.__connectRemote(i) == ErrorCode.Success:
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
        
        self.setLogLevel(LogLevel.CRITICAL)
        
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
        
        return ErrorCode.Success
        
    def giveMoney(self, ID, Money, YourPassword, ConnectIndex = 0):
        self.__CurrentTimeout[ConnectIndex] = 3
        
        ErrCode = self.__gotoTop(ConnectIndex)
        if ErrCode != ErrorCode.Success:
            print('giveMoney goto top error code 1: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['量販店', '給其他人Ptt幣', '這位幸運兒的id', '請輸入金額', '請輸入您的密碼', '要修改紅包袋嗎', '確定進行交易嗎', '按任意鍵繼續']
        SendMessage = 'P'
        Enter = True
        while True:        
            ErrCode, Index = self.__sendData(ConnectIndex, SendMessage, CaseList, Enter)
            if ErrCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('No such option: ' + SendMessage, LogLevel.DEBUG)
                return self.NoUser
            if ErrCode != ErrorCode.Success:
                self.Log('mail 2 error code: ' + str(ErrorCode), LogLevel.DEBUG)
                return ErrorCode
            if Index == 0:
                SendMessage = 'P'
                Enter = True
                self.Log('giveMoney 量販店', LogLevel.DEBUG)
            if Index == 1:
                SendMessage = '0'
                Enter = True
                self.Log('giveMoney 給其他人Ptt幣', LogLevel.DEBUG)
            if Index == 2:
                SendMessage = ID
                Enter = True
                self.Log('giveMoney 這位幸運兒的id', LogLevel.DEBUG)
            if Index == 3:
                SendMessage = '\t' + str(Money)
                Enter = True
                self.Log('giveMoney 請輸入金額', LogLevel.DEBUG)
            if Index == 4:
                SendMessage = str(YourPassword)
                Enter = True
                self.__CurrentTimeout[ConnectIndex] = 3
                self.Log('giveMoney 請輸入您的密碼', LogLevel.DEBUG)
            if Index == 5:
                SendMessage = 'n'
                Enter = True
                self.__CurrentTimeout[ConnectIndex] = 3
                self.Log('giveMoney 要修改紅包袋嗎', LogLevel.DEBUG)
            if Index == 6:
                SendMessage = 'y'
                Enter = True
                self.__CurrentTimeout[ConnectIndex] = 3
                self.Log('giveMoney 確定進行交易嗎', LogLevel.DEBUG)
            if Index == 7:
                self.Log('giveMoney 按任意鍵繼續', LogLevel.DEBUG)
                break
        return ErrorCode.Success
    
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
            ErrCode = self.__gotoPostByID(Board, PostID, ConnectIndex)
            if ErrCode != ErrorCode.Success:
                self.Log('replyPost 1 移動至文章失敗', LogLevel.DEBUG)
                return ErrorCode
        elif Index != -1:
            #def __gotoPostByIndex(self, Board, PostIndex, ConnectIndex=0):
            ErrCode = self.__gotoPostByIndex(Board, Index, ConnectIndex)
            if ErrCode != ErrorCode.Success:
                self.Log('replyPost 2 移動至文章失敗', LogLevel.DEBUG)
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
            ErrCode, Index = self.__sendData(ConnectIndex, SendMessage, CaseList, Enter)
            if ErrCode == self.WaitTimeout:
                self.__showScreen()
                self.Log('無法回文', LogLevel.DEBUG)
                return self.WaitTimeout
            if ErrCode != ErrorCode.Success:
                self.Log('replyPost 2 error code: ' + str(ErrorCode), LogLevel.DEBUG)
                return ErrorCode
            if Index == 0:
                if ReplyType == self.ReplyPost_Board:
                    SendMessage = 'F'
                    self.Log('replyPost 回應至 (F)看板', LogLevel.DEBUG)
                elif ReplyType == self.ReplyPost_Mail:
                    SendMessage = 'M'
                    self.Log('replyPost 回應至 (M)作者信箱', LogLevel.DEBUG)
                elif ReplyType == (self.ReplyPost_Board + self.ReplyPost_Mail):
                    SendMessage = 'B'
                    self.Log('replyPost 回應至 (B)二者皆是', LogLevel.DEBUG)
                else:
                    self.Log('replyPost 不支援的回文選項: ' + str(ReplyType), LogLevel.DEBUG)
                self.__CurrentTimeout[ConnectIndex] = 10
                Enter = True
            if Index == 1:
                SendMessage = 'Y'
                Enter = True
                self.__CurrentTimeout[ConnectIndex] = 10
                self.Log('replyPost 回信給作者', LogLevel.DEBUG)
            if Index == 2:
                SendMessage = 'Y'
                Enter = True
                self.Log('replyPost 採用原標題', LogLevel.DEBUG)
            if Index == 3:
                SendMessage = 'Y'
                Enter = True
                self.Log('replyPost 引用原文', LogLevel.DEBUG)
            if Index == 4:
                SendMessage = Content + '\r\x18'
                Enter = True
                self.__CurrentTimeout[ConnectIndex] = 10
                self.Log('replyPost 編輯文章', LogLevel.DEBUG)
            if Index == 5:
                SendMessage = 's'
                Enter = True
                self.Log('replyPost 儲存檔案', LogLevel.DEBUG)
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
                self.Log('replyPost 已順利寄出', LogLevel.DEBUG)
        
        return ErrorCode.Success
    
if __name__ == '__main__':

    print('PTT Library v ' + Version)
    print('Developed by PTT CodingMan')