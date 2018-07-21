﻿import sys
import time
import re
import threading
import progressbar
import socket
import array
import paramiko
from paramiko import ECDSAKey
from uao import Big5UAOCodec
uao = Big5UAOCodec()

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

Version = Version.Ver
LogLevel = Information.LogLevel()
PushType = Information.PushType()
ErrorCode = ErrorCode.ErrorCode()
ReplyPostType = Information.ReplyPostType()
FriendListType = Information.FriendListType()
OperateType = Information.OperateType()
WaterBallOperateType = Information.WaterBallOperateType
WaterBallType = Information.WaterBallType

class _ResponseUnit(object):
    def __init__(self, SendMessage, Refresh):
        self.__SendMessage = SendMessage
        self.__Refresh = Refresh
    def getSendMessage(self):
        return self.__SendMessage
    def needRefresh(self):
        return self.__Refresh

class _DetectUnit(object):
    def __init__(self, DisplayMsg, DetectTarget, Response, BreakDetect=False, ErrCode=0, LogLV=0):
        self.__DisplayMsg = DisplayMsg
        self.__DetectTarget = DetectTarget
        self.__Response = Response
        self.__BreakDetect = BreakDetect
        self.__ErrCode = ErrCode
        if LogLV == 0:
            self.__LogLevel = LogLevel.INFO
        else:
            self.__LogLevel = LogLV
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
    def getLogLevel(self):
        return self.__LogLevel

class Library(object):
    def __init__(self, ID='', Password='', kickOtherLogin=True, MaxIdleTime=20, _LogLevel=-1, WaterBallHandler=None, LogHandler=None):
    
        self.__host = 'ptt.cc'
        self.__ID = ID
        self.__Password = Password
        self.__kickOtherLogin = kickOtherLogin
        
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

        self.__LogHandler = LogHandler
        self.__LogLevel = LogLevel.INFO

        if _LogLevel != -1:
            if _LogLevel < LogLevel.MinValue or LogLevel.MaxValue < _LogLevel:
                self.Log('LogLevel error: ' + str(_LogLevel))
                return None
            else:
                self.__LogLevel = _LogLevel
        
        self.__isMailBoxFull = False
        self.__MailFullAPILock = False
        self.__DefaultTimeout =                 5
        self.__Cursor =                       '>'
        self.__MaxMultiLogin =                  5

        self.__ConnectList = [None] * self.__MaxMultiLogin
        self.__ReceiveData = [''] * self.__MaxMultiLogin
        self.__ReceiveRawData = [''] * self.__MaxMultiLogin
        
        self.__PreReceiveData = [''] * self.__MaxMultiLogin
        self.__isConnected = [False] * self.__MaxMultiLogin

        self.__isBackground = False

        self.__gotoMainMenu = '\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD'
        self.__delAllWord = '\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08'

        self.__ShowProgressBar =             True

        self.__IdleTime =                       0
        self.__MaxIdleTime =                    MaxIdleTime
        try:
            self.Log('偵測到前景執行使用編碼: ' + sys.stdin.encoding)
            self.__isBackground = False
        except Exception:
            self.Log('偵測到背景執行')
            self.__isBackground = True
        
        if ID != '':
            self.Log('使用者帳號: ' + ID)
        
        if Password != '':
            TempPW = ''

            for i in range(len(Password)):
                TempPW += '*'
            
            self.Log('密碼: ' + TempPW)
        
        self.__SSHKey = ECDSAKey.generate()
        self.Log('產生 SSH 金鑰完成')

        self.__IdleThread =                 None
        self.__RunIdleThread =              False
        
        self.__WaterBallHandler = WaterBallHandler
        if self.__WaterBallHandler != None:
            self.__MaxIdleTime = 2
        
        self.__WaterBallList = []

        self.__APILock = [threading.Lock()] * self.__MaxMultiLogin

        self.__PTTBUGDetectUnit = _DetectUnit(
            '遇到 PTT BUG!!',
            'PttBug', 
            _ResponseUnit(' ', False),
            BreakDetect=True,
            ErrCode = ErrorCode.PttBug
        )

        self.__ErrorCode =                      ErrorCode.Success
    def __AntiLogout(self):
        
        self.__RunIdleThread = True

        while self.__RunIdleThread and threading.main_thread().is_alive():
            self.__IdleTime += 1
            time.sleep(1)
            if self.__IdleTime < self.__MaxIdleTime:
                continue
            ErrCode, result = self.getTime()
            self.__IdleTime = 0

        return
    def __WaterBallProceeor(self):
        
        if self.__WaterBallHandler == None:
            return
        
        while len(self.__WaterBallList) != 0:
            CurrentWaterBall = self.__WaterBallList.pop(0)
            try:
                self.__WaterBallHandler(CurrentWaterBall)
            except TypeError:
                self.Log('WaterBallHandler 介面錯誤', LogLevel.WARNING)
            except:
                self.Log('WaterBallHandler 未知錯誤', LogLevel.WARNING)
    def __APICheck(self):
        if self.__MailFullAPILock:
            self.Log('機器人已被卡在信箱區，僅能取得信件與最新信件編號與寄信', LogLevel.CRITICAL)
            self.Log('請清理信箱並重新登入機器人', LogLevel.CRITICAL)
            self.__ErrorCode = ErrorCode.MailBoxFull
            return False
        self.__ErrorCode = ErrorCode.Success
        return True
    def __showScreen(self, ErrCode, FunctionName, ConnectIndex=0, _LogLevel=-1):
        
        if _LogLevel == -1:
            _LogLevel = self.__LogLevel
        
        if _LogLevel >= self.__LogLevel:
            print('-' * 50)
            try:
                print(self.__PreReceiveData[ConnectIndex].encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding))
            except Exception:
                print(self.__PreReceiveData[ConnectIndex].encode('utf-8', "replace").decode('utf-8'))
            print('頻道 ' + str(ConnectIndex) + ' 畫面長度為: ' + str(len(self.__ReceiveData[ConnectIndex])) + ' ' + str(len(self.__PreReceiveData[ConnectIndex])))
            print('-' * 50)
            try:
                print(self.__ReceiveData[ConnectIndex].encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding))
            except Exception:
                print(self.__ReceiveData[ConnectIndex].encode('utf-8', "replace").decode('utf-8'))
            print('錯誤在 ' + FunctionName + ' 函式發生')
            print('-' * 50)
    
    def Log(self, Message, _LogLevel=-1):
        if _LogLevel == -1:
            _LogLevel = LogLevel.INFO
        if _LogLevel < LogLevel.MinValue or LogLevel.MaxValue < _LogLevel:
            print('[錯誤] MinValue error: ' + str(LogLevel.MinValue))
            print('[錯誤] MaxValue error: ' + str(LogLevel.MaxValue))
            print('[錯誤] LogLevel error: ' + str(_LogLevel))
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
            
            Message = str(Message)
            if len(Message) > 0:
                Util.Log(Prefix + Message)
                if self.__LogHandler != None:
                    try:
                        self.__LogHandler(Message)
                    except TypeError:
                        self.Log('LogHandler 介面錯誤', LogLevel.WARNING)
                    except:
                        self.Log('LogHandler 未知錯誤', LogLevel.WARNING)
                    
        return ErrorCode.Success
    def __operatePTT(self, ConnectIndex, SendMessage='', CatchTargetList=[], Refresh=False, ExtraWait=0):
        
        SendMessageTimeout = 10.0
        PreWait = 0.01
        EveryWait = 0.01

        MaxEveryWait = 0.1
        MinEveryWait = 0.01

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
                time.sleep(PreWait)
                while not self.__ConnectList[ConnectIndex].channel.send_ready():
                    time.sleep(EveryWait)

                    if TimeCout >= 100:
                        TimeCout = 0
                        NowTime = time.time()
                        if (NowTime - StartTime) >= SendMessageTimeout:
                            self.Log('超時斷線，重新連線')
                            self.__connectRemote(ConnectIndex)
                            return self.__operatePTT(ConnectIndex, SendMessage, CatchTargetList, Refresh, ExtraWait)
                    TimeCout += 1
                
                EncodeMessage, Len = uao.encode(SendMessage)
                self.__ConnectList[ConnectIndex].channel.send(EncodeMessage)
            
            TimeCout = 0
            StartTime = time.time()
            time.sleep(PreWait)
            while not self.__ConnectList[ConnectIndex].channel.recv_ready():
                time.sleep(EveryWait)

                if TimeCout >= 100:
                    TimeCout = 0
                    NowTime = time.time()
                    if (NowTime - StartTime) >= SendMessageTimeout:
                        self.Log('超時斷線，重新連線')
                        self.__connectRemote(ConnectIndex)
                        return self.__operatePTT(ConnectIndex, SendMessage, CatchTargetList, Refresh, ExtraWait)
                TimeCout += 1

            self.__ReceiveData[ConnectIndex] = self.__wait_str(ConnectIndex)
            while self.__ConnectList[ConnectIndex].channel.recv_ready():
                time.sleep(EveryWait)
                self.__ReceiveData[ConnectIndex] += self.__recv_str(ConnectIndex)

            
            DelateDetect = [False] * 5
            while DelateDetect.count(True) == 5:
                DelateDetect = [False] * 5
                for i in range(5):
                    time.sleep(PreWait)
                    while self.__ConnectList[ConnectIndex].channel.recv_ready():
                        DelateDetect[i] = True
                        time.sleep(EveryWait)
                        self.__ReceiveData[ConnectIndex] += self.__recv_str(ConnectIndex)
            
            DelateDetectCount = DelateDetect.count(True)

            if DelateDetectCount > 3:
                EveryWait += 0.01
                if EveryWait > MaxEveryWait:
                    EveryWait = MaxEveryWait
            elif DelateDetectCount == 0:
                EveryWait -= 0.01
                if EveryWait < MinEveryWait:
                    EveryWait = MinEveryWait
                
        except socket.timeout:
            self.Log('超時斷線，重新連線')
            self.__connectRemote(ConnectIndex)
            return self.__operatePTT(ConnectIndex, SendMessage, CatchTargetList, Refresh, ExtraWait)
        except OSError:
            self.Log('作業系統錯誤斷線，重新連線')
            self.__connectRemote(ConnectIndex)
            return self.__operatePTT(ConnectIndex, SendMessage, CatchTargetList, Refresh, ExtraWait)
        except KeyboardInterrupt:
            self.Log('使用者中斷')
            self.__ErrorCode = ErrorCode.UserInterrupt
            return self.__ErrorCode, -1
        except:
            self.Log('斷線，重新連線')
            self.__connectRemote(ConnectIndex)
            return self.__operatePTT(ConnectIndex, SendMessage, CatchTargetList, Refresh, ExtraWait)

        # self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex].decode(encoding='big5',errors='ignore')
        self.__ReceiveRawData[ConnectIndex] = self.__ReceiveData[ConnectIndex]
        self.__ReceiveData[ConnectIndex], Len = uao.decode(self.__ReceiveData[ConnectIndex])
        self.__ReceiveData[ConnectIndex] = self.__cleanScreen(self.__ReceiveData[ConnectIndex])

        if self.__WaterBallHandler != None:
            line = self.__ReceiveData[ConnectIndex].split('\n').pop()
                # if '★' in line:
            if line.startswith('  ★'):
                line = line[3:]
                WaterBallAuthor = line[:line.find(' ')]
                WaterBallContent = line[line.find(' ') + 1:line.find(' [K')]
                # print('WaterBallAuthor: =' + WaterBallAuthor + '=')
                # print('WaterBallContent: =' + WaterBallContent + '=')
                CurrentWaterBall = Information.WaterBallInformation(WaterBallType.Catch, WaterBallAuthor, WaterBallContent)
                self.__WaterBallList.append(CurrentWaterBall)
                
        for i in range(len(CatchTargetList)):
            if CatchTargetList[i] in self.__ReceiveData[ConnectIndex]:
                self.__ConnectList[ConnectIndex].channel.settimeout(self.__DefaultTimeout)
                return ErrorCode.Success, i

        self.__ConnectList[ConnectIndex].channel.settimeout(self.__DefaultTimeout)

        self.__ErrorCode = ErrCode
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
        # return self.__dec_bytes(ch)
        return ch
    def __recv_str(self, ConnectIndex):
        # return self.__dec_bytes(self.__ConnectList[ConnectIndex].channel.recv(self.buf_size))
        return self.__ConnectList[ConnectIndex].channel.recv(self.buf_size)
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
                    self.__ErrorCode = ErrCode
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

                self.__ConnectList[ConnectIndex] = paramiko.SSHClient()
                # self.__ConnectList[ConnectIndex].load_system_host_keys()
                # self.__ConnectList[ConnectIndex].set_missing_host_key_policy(paramiko.WarningPolicy())
                self.__ConnectList[ConnectIndex].set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.__ConnectList[ConnectIndex].connect('ptt.cc', username = 'bbs', password = '', pkey = self.__SSHKey)
                
                self.__ConnectList[ConnectIndex].channel = self.__ConnectList[ConnectIndex].invoke_shell(width = self.width, height = self.height)
            except paramiko.AuthenticationException:
                # print('... Authentication failed')
                self.Log('連接至 ' + self.__host + ' SSH 認證失敗')
                self.__ErrorCode = ErrorCode.SSHFail
                return ErrorCode.SSHFail
            except Exception as e:
                # print('... Connection failed:', str(e))
                self.Log('連接至 ' + self.__host + ' 連線失敗')
                self.__ErrorCode = ErrorCode.RemoteHostDown
                return ErrorCode.RemoteHostDown
            except paramiko.SSHException:
                self.Log('建立 SSH 通道失敗')
                self.__ErrorCode = ErrorCode.SSHFail
                return ErrorCode.SSHFail
            except KeyboardInterrupt:
                self.Log('使用者中斷')
                self.__ErrorCode = ErrorCode.UserInterrupt
                return ErrorCode.UserInterrupt
            except:
                self.Log('主機沒有回應')
                Retry = True
                self.__ErrorCode = ErrorCode.UnknowError
                ErrCode = ErrorCode.UnknowError
                continue

            self.Log('頻道 ' + str(ConnectIndex) + ' 建立互動通道成功')
            
            self.__ConnectList[ConnectIndex].channel.settimeout(self.__DefaultTimeout)

            if ConnectIndex == 0:
                KickMsg = '頻道 ' + str(ConnectIndex) + ' 刪除重複登入的連線' if self.__kickOtherLogin else '不刪除重複登入的連線'
                KickResponse = 'y\r' if self.__kickOtherLogin else 'n\r'
            else:
                KickMsg = '副頻道不刪除重複登入的連線'
                KickResponse = 'n\r'

            SendMessage = ''
            Refresh = True
            isBreakDetect = False
            # 先後順序代表偵測的優先順序
            DetectTargetList = [
                _DetectUnit(
                    '頻道 ' + str(ConnectIndex) + ' 郵件已滿',
                    '您保存信件數目', 
                    _ResponseUnit(self.__gotoMainMenu, True),
                ),
                _DetectUnit(
                    '任意鍵繼續',
                    '任意鍵', 
                    _ResponseUnit(' ', True)
                ),
                _DetectUnit(
                    '頻道 ' + str(ConnectIndex) + ' 放棄未完成文章',
                    '有一篇文章尚未完成', 
                    _ResponseUnit('q\r', False)
                ),
                _DetectUnit(
                    '頻道 ' + str(ConnectIndex) + ' 密碼錯誤',
                    '請檢查帳號及密碼大小寫有無輸入錯誤', 
                    _ResponseUnit(' ', False),
                    BreakDetect=True,
                    ErrCode = ErrorCode.WrongPassword
                ),
                _DetectUnit(
                    '頻道 ' + str(ConnectIndex) + ' 系統負荷過重，重新執行連線',
                    '為避免系統負荷過重, 請稍後再試', 
                    _ResponseUnit(' ', False),
                    BreakDetect=True,
                    ErrCode = ErrorCode.WaitTimeout
                ),
                _DetectUnit(
                    '頻道 ' + str(ConnectIndex) + ' 更新與同步線上使用者及好友名單',
                    '更新與同步線上使用者及好友名單', 
                    _ResponseUnit('\x1b\x4fD\x1b\x4fD', False)
                ),
                _DetectUnit(
                    KickMsg,
                    '刪除其他重複登入的連線', 
                    _ResponseUnit(KickResponse, True)
                ),
                _DetectUnit(
                    '頻道 ' + str(ConnectIndex) + ' 刪除錯誤嘗試紀錄',
                    '您要刪除以上錯誤嘗試的記錄嗎', 
                    _ResponseUnit('y\r', False)
                ),
                _DetectUnit(
                    '頻道 ' + str(ConnectIndex) + ' 登入成功',
                    '我是' + self.__ID, 
                    _ResponseUnit(' ', False),
                    BreakDetect=True,
                ),
                _DetectUnit(
                    '頻道 ' + str(ConnectIndex) + ' 輸入密碼',
                    '請輸入您的密碼:', 
                    _ResponseUnit(self.__Password + '\r', False)
                ),
                _DetectUnit(
                    '頻道 ' + str(ConnectIndex) + ' 輸入帳號',
                    '請輸入代號，或以 guest 參觀，或以 new 註冊', 
                    _ResponseUnit(self.__ID + '\r', False)
                ),
                self.__PTTBUGDetectUnit
            ]
            
            LoginFailCount = 0
            MaxLoginFail = 2

            while not isBreakDetect:
                ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
                if ErrCode == ErrorCode.WaitTimeout:
                    self.Log('登入超時重新嘗試')
                    break
                elif ErrCode != ErrorCode.Success:
                    self.Log('登入操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                    self.__ErrorCode = ErrCode
                    return ErrCode
                
                # self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)

                isDetectedTarget = False

                for DetectTarget in DetectTargetList:
                    if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):

                        LoginFailCount = 0
                        self.Log(DetectTarget.getDisplayMsg())

                        if '郵件已滿' in DetectTarget.getDisplayMsg():
                            self.__isMailBoxFull = True

                        SendMessage = DetectTarget.getResponse().getSendMessage()
                        Refresh = DetectTarget.getResponse().needRefresh()
                        
                        isDetectedTarget = True
                        if DetectTarget.isBreakDetect():
                            isBreakDetect = True
                            ErrCode = DetectTarget.getErrorCode()
                        break

                if not isDetectedTarget:

                    if LoginFailCount < MaxLoginFail:
                        self.Log('頻道 ' + str(ConnectIndex) + ' 讀取 PTT 畫面..')
                        Refresh = True
                        LoginFailCount += 1
                        SendMessage = ''
                        continue

                    self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)
                    self.Log('無法解析的狀態! PTT Library 緊急停止')
                    self.logout()
                    sys.exit()
            if ErrCode == ErrorCode.WaitTimeout:
                Retry = True
            elif ErrCode != ErrorCode.Success:
                self.__ErrorCode = ErrCode
                return ErrCode
            
            if '> (' in self.__ReceiveData[ConnectIndex]:
                self.Log('新式游標模式', LogLevel.DEBUG)
                self.__Cursor = '>'
                self.__isConnected[ConnectIndex] = True
                
            elif '●(' in self.__ReceiveData[ConnectIndex]:
                self.Log('舊式游標模式', LogLevel.DEBUG)
                self.__Cursor = '●'
                self.__isConnected[ConnectIndex] = True
            else:
                self.Log('頻道 ' + str(ConnectIndex) + ' 無法偵測游標。重新執行連線')
                # return ErrorCode.UnknowError
        return ErrorCode.Success
    
    def login(self, ID='', Password=''):
        
        self.__IdleTime = 0

        if ID != '':
            self.__ID = ID
            self.Log('使用者帳號: ' + ID)
        if Password != '':
            self.__Password = Password
            TempPW = ''

            for i in range(len(Password)):
                TempPW += '*'
            
            self.Log('密碼: ' + TempPW)
        
        ErrCode = self.__connectRemote(0)
        
        if ErrCode == ErrorCode.Success:
            self.__IdleThread = threading.Thread(target=self.__AntiLogout)
            self.__IdleThread.start()
        
        self.__ErrorCode = ErrCode
        return ErrCode
    def logout(self):
        
        ConnectIndex = -1
        
        self.__IdleTime = 0
        self.__RunIdleThread = False
        
        if ConnectIndex == -1:
            
            self.Log('準備登出所有頻道')
            
            for index in range(self.__MaxMultiLogin):
                self.__isConnected[index] = False
            
            for index in range(self.__MaxMultiLogin):
                if self.__ConnectList[index] == None:
                    continue
                self.Log('頻道 ' + str(index) + ' 登出', LogLevel.DEBUG)
                
                SendMessage = self.__gotoMainMenu + ' g\ry\r'

                ErrCode, CatchIndex = self.__operatePTT(index, SendMessage=SendMessage)
                self.Log('頻道 ' + str(index) + ' 登出成功')
        
        ErrCode = ErrorCode.Success
        self.__ErrorCode = ErrCode
        return ErrCode
    def __getNewestPostIndex(self, Board, ConnectIndex=0, Search='', Author=''):
        result = 0
        
        CatchList = [
            # 0
            '文章選讀',
        ]

        # SendMessage = '\x1b\x4fD\x1b\x4fD\x1b\x4fDqs' + Board + '\r\x03\x03 0\r$'
        
        SendMessage = self.__gotoMainMenu + 'qs' + Board + '\r\x03\x03 '
        if Author != '':
            SendMessage += 'a' + Author + '\r'
        if Search != '':
            SendMessage += '/' + Search + '\r'
        SendMessage += '0\r$'
        Refresh = True
        ExtraWait = 0

        ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=Refresh, ExtraWait=ExtraWait)
        if ErrCode != ErrorCode.Success:
            self.__ErrorCode = ErrCode
            return ErrCode, result

        # print(self.__ReceiveData[ConnectIndex])

        ReceiveDataLines = self.__ReceiveData[ConnectIndex].split('\n')
        ReceiveDataLines = ReceiveDataLines[2:-1]
        self.__ReceiveData[ConnectIndex] = '\n'.join(ReceiveDataLines)
        self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex][:self.__ReceiveData[ConnectIndex].find('★  ')]

        AllIndex = re.findall(r'\d+ ', self.__ReceiveData[ConnectIndex])
        
        if len(AllIndex) == 0:
            ErrCode = ErrorCode.UnknowError
            self.__ErrorCode = ErrCode
            return ErrCode, result

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
            ErrCode = ErrorCode.ParseError
            self.__ErrorCode = ErrCode
            return ErrCode, result
        
        # 確認是否有因為上篇文章是數字結尾導致判斷錯誤的情況
        for i in range(1, 20):
            if str(result + 1) in self.__ReceiveData[ConnectIndex]:
                result += 1
            else: 
                break
        
        SendMessage = self.__gotoMainMenu + 'qs' + Board + '\r\x03\x03 ' + str(result) + '\rQ'
        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '取得可閱讀文章',
                '文章代碼', 
                _ResponseUnit('\x1b\x4fD\x1b\x4fD\x1b\x4fD', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '取得可閱讀文章',
                '文章網址', 
                _ResponseUnit('\x1b\x4fD\x1b\x4fD\x1b\x4fD', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '取得可閱讀文章',
                '這一篇文章值', 
                _ResponseUnit('\x1b\x4fD\x1b\x4fD\x1b\x4fD', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '',
                '請按任意鍵繼續', 
                _ResponseUnit('\x1b\x4fD\x1b\x4fD\x1b\x4fD', False),
                BreakDetect=True,
                ErrCode = ErrorCode.UnknowError
            ),
            self.__PTTBUGDetectUnit
        ]

        ShowFixResult = False

        for TryResult in range(result, result - 100, -1):
            
            FindResult = False

            #self.Log('Try: ' + Board + ' ' + str(TryResult))
            SendMessage = '\x1b\x4fD\x1b\x4fD\x1b\x4fDqs' + Board + '\r\x03\x03 ' + str(TryResult) + '\rQ'

            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('登入超時重新嘗試')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('登入操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                
                self.__ErrorCode = ErrCode
                return ErrCode

            isDetectedTarget = False

            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                    
                    if ShowFixResult:
                        self.Log(DetectTarget.getDisplayMsg())

                    SendMessage = DetectTarget.getResponse().getSendMessage()
                    Refresh = DetectTarget.getResponse().needRefresh()
                    
                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():
                        self.__isConnected[ConnectIndex] = True
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()

                        if result != TryResult:
                            if ShowFixResult:
                                self.Log('修正結果為 ' + str(TryResult), LogLevel.DEBUG)
                            result = TryResult
                        FindResult = True
                    else:
                        ShowFixResult = True
                        break
            if not isDetectedTarget:
                continue
                # self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)
                # self.Log('無法解析的狀態! PTT Library 緊急停止')
                # sys.exit()
            if FindResult:
                break
        ErrCode = ErrorCode.Success
        self.__ErrorCode = ErrCode
        return ErrCode, result
    def post(self, Board, Title, Content, PostType, SignType):
        
        ConnectIndex = 0
        self.__IdleTime = 0

        if not self.__APICheck():
            return self.__ErrorCode

        try:
            Board = str(Board)
            Title = str(Title)
            Content = str(Content)
            PostType = int(PostType)
            SignType = int(SignType)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode
        
        # 前進至板面

        self.__APILock[ConnectIndex].acquire()

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
                self.__APILock[ConnectIndex].release()
                self.__ErrorCode = ErrCode
                return ErrCode

            if CatchIndex == -1:
                self.Log('前進至 ' + Board + '板失敗')
                print(self.__ReceiveData[ConnectIndex])
                self.__APILock[ConnectIndex].release()

                ErrCode = ErrorCode.UnknowError
                self.__ErrorCode = ErrCode
                return ErrCode

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
                    self.__APILock[ConnectIndex].release()
                    self.__ErrorCode = ErrCode
                    return ErrCode
            else:
                RetryCount = 0

            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=Refresh, ExtraWait=ExtraWait)
            if ErrCode != ErrorCode.Success:
                self.__APILock[ConnectIndex].release()
                
                self.__ErrorCode = ErrCode
                return ErrCode

            SendMessage = ' '
            Refresh = False
            ExtraWait = 0

            if CatchIndex == 0:
                self.Log('具備發文權限', LogLevel.DEBUG)
                break
            elif CatchIndex == 1:
                self.Log('你被水桶惹 QQ')
                self.__APILock[ConnectIndex].release()
                ErrCode = ErrorCode.NoPermission
                self.__ErrorCode = ErrCode
                return ErrCode
            else:
                self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex, _LogLevel=LogLevel.DEBUG)
                self.__APILock[ConnectIndex].release()
                ErrCode = ErrorCode.UnknowError
                self.__ErrorCode = ErrCode
                return ErrCode

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
            self.__APILock[ConnectIndex].release()
            self.__ErrorCode = ErrCode
            return ErrCode

        if CatchIndex == 0:
            self.Log('儲存檔案', LogLevel.DEBUG)
            SendMessage = 's\r'
        else:
            self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex, _LogLevel=LogLevel.DEBUG)
            self.__APILock[ConnectIndex].release()
            ErrCode = ErrorCode.UnknowError
            self.__ErrorCode = ErrCode
            return ErrCode

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
                self.__APILock[ConnectIndex].release()

                self.__ErrorCode = ErrCode
                return ErrCode

            if CatchIndex == 0:
                break
            elif CatchIndex == 1:
                self.Log('選擇簽名檔: ' + str(SignType), LogLevel.DEBUG)
                SendMessage = str(SignType) + '\r'
            elif CatchIndex == 2:
                break
            else:
                self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex, _LogLevel=LogLevel.DEBUG)
                self.__APILock[ConnectIndex].release()

                ErrCode = ErrorCode.UnknowError
                self.__ErrorCode = ErrCode
                return ErrCode
        
        self.__WaterBallProceeor()
        self.__APILock[ConnectIndex].release()
        
        ErrCode = ErrorCode.Success
        self.__ErrorCode = ErrCode
        return ErrCode
    def push(self, Board, inputPushType, PushContent, PostID='', PostIndex=0):
        
        self.__IdleTime = 0
        ConnectIndex = 0
        
        if not self.__APICheck():
            return self.__ErrorCode

        try:
            Board = str(Board)
            inputPushType = int(inputPushType)
            PushContent = str(PushContent)
            PostID = str(PostID)
            PostIndex = int(PostIndex)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode
        
        if len(Board) == 0:
            self.Log('看板名稱輸入錯誤: ' + str(Board))
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode

        if PostIndex != 0 and PostID != '':
            self.Log('文章編號與代碼輸入錯誤: 同時輸入')
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode

        if PostIndex == 0 and PostID == '':
            self.Log('文章編號與代碼輸入錯誤: 皆無輸入')
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode

        MaxPushLength = 45

        self.__PushShow = False
        PushList = []
        Temp = ''

        TempStartIndex = 0
        TempEndIndex = TempStartIndex + 1

        while TempEndIndex <= len(PushContent):

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
        
        self.__APILock[ConnectIndex].acquire()
        
        for Push in PushList:
            # print('Push:', Push)
            ErrCode = self.__push(Board, inputPushType, Push, PostID=PostID, PostIndex=PostIndex)

            if ErrCode != ErrorCode.Success:
                self.__ErrorCode = ErrCode
                return ErrCode

        
        self.__WaterBallProceeor()
        self.__APILock[ConnectIndex].release()

        self.__ErrorCode = ErrCode
        return ErrCode
    def __push(self, Board, inputPushType, PushContent, PostID='', PostIndex=0):
        
        ConnectIndex = 0
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
            self.__ErrorCode = ErrCode
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
                ErrCode = ErrorCode.ErrorInput
                self.__ErrorCode = ErrCode
                return ErrCode
                
            self.Log('準備推文')
            SendMessage = str(inputPushType) + str(PushContent) + '\ry\r'

        elif CatchIndex == 1:
            self.Log('禁止快速推文')
            ErrCode = ErrorCode.NoFastPush
            self.__ErrorCode = ErrCode
            return ErrCode
        elif CatchIndex == 2:
            self.Log('禁止機器人快速推文')
            ErrCode = ErrorCode.NoFastPush
            self.__ErrorCode = ErrCode
            return ErrCode
        elif CatchIndex == 3:
            self.Log('你被水桶惹 QQ')
            ErrCode = ErrorCode.NoPermission
            self.__ErrorCode = ErrCode
            return ErrCode

        elif CatchIndex == 4:
            if not self.__PushShow:
                self.Log('作者本人使用箭頭')
                self.__PushShow = True
            SendMessage = str(PushContent) + '\ry\r'
        elif CatchIndex == 5:
            self.Log('文章已經被刪除')
            ErrCode = ErrorCode.PostDeleted
            self.__ErrorCode = ErrCode
            return ErrCode
        else:
            self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex, _LogLevel=LogLevel.DEBUG)
            ErrCode = ErrorCode.UnknowError
            self.__ErrorCode = ErrCode
            return ErrCode
        
        CatchList = []

        ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, CatchTargetList=CatchList, Refresh=True)
        if ErrCode != ErrorCode.Success:
            self.__ErrorCode = ErrCode
            return ErrCode

        # print(self.__ReceiveData[ConnectIndex])
        ErrCode = ErrorCode.Success
        self.__ErrorCode = ErrCode
        return ErrCode

    def getPost(self, Board, PostID='', PostIndex=0, _ConnectIndex=0, Search=''):
        self.__IdleTime = 0
        
        ConnectIndex = _ConnectIndex
        result = None

        if not self.__APICheck():
            return self.__ErrorCode, result
        try:
            Board = str(Board)
            PostID = str(PostID)
            PostIndex = int(PostIndex)
            Search = str(Search)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, result
        
        if len(Board) == 0:
            self.Log('看板名稱輸入錯誤: ' + str(Board))
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, result

        if PostIndex != 0 and PostID != '':
            self.Log('文章編號與代碼輸入錯誤: 同時輸入')
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, result

        if PostIndex == 0 and PostID == '':
            self.Log('文章編號與代碼輸入錯誤: 皆無輸入')
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, result

        if PostID != '' and Search != '':
            self.Log('使用文章代碼取得文章 搜尋條件失效', LogLevel.WARNING)

        self.__APILock[ConnectIndex].acquire()

        for i in range(3):
            ErrCode, Post = self.__getPost(Board, PostID, PostIndex, _ConnectIndex, Search)
            if ErrCode != ErrorCode.Success:
                continue
            
            self.__APILock[ConnectIndex].release()
            self.__ErrorCode = ErrCode
            return ErrCode, Post

        self.__WaterBallProceeor()
        self.__APILock[ConnectIndex].release()

        self.__ErrorCode = ErrCode
        return ErrCode, Post
    def __getPost(self, Board, PostID='', PostIndex=0, _ConnectIndex=0, Search=''):
        
        ConnectIndex = _ConnectIndex
        result = None

        SendMessage = self.__gotoMainMenu + 'qs' + Board + '\r\x03\x03 '
        # 前進至文章
        if PostID != '':
            SendMessage += '#' + PostID + '\rQ'
        elif PostIndex != -1:
            if Search != '':
                SendMessage += '/' + Search + '\r'
            SendMessage += str(PostIndex) + '\rQ'
        
        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '取得文章',
                '請按任意鍵繼續', 
                _ResponseUnit('\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '取得文章',
                '這一篇文章值', 
                _ResponseUnit('\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '取得文章',
                '文章代碼(AID):', 
                _ResponseUnit('\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '含有控制碼',
                '此頁內容會依閱讀者不同', 
                _ResponseUnit('\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD', False),
                BreakDetect=True,
                ErrCode = ErrorCode.HasControlCode
            ),
            _DetectUnit(
                '含有控制碼',
                '原文未必有您的資料', 
                _ResponseUnit('\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD', False),
                BreakDetect=True,
                ErrCode = ErrorCode.HasControlCode
            ),
            _DetectUnit(
                '遇到 PTT BUG!!',
                'PttBug', 
                _ResponseUnit(' ', False),
                BreakDetect=True,
                ErrCode = ErrorCode.PttBug
            ),
        ]

        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('操作超時重新嘗試')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('操作操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
            
                self.__ErrorCode = ErrCode
                return ErrCode, None

            isDetectedTarget = False

            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):

                    self.Log(DetectTarget.getDisplayMsg(), LogLevel.DEBUG)

                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():
                        self.__isConnected[ConnectIndex] = True
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()

                        if ErrCode == ErrorCode.PttBug:
                            self.__connectRemote(ConnectIndex)
                            self.__ErrorCode = ErrCode
                            return ErrCode, None

                        break

                    SendMessage = DetectTarget.getResponse().getSendMessage()
                    Refresh = DetectTarget.getResponse().needRefresh()

                    break

            if not isDetectedTarget:
                
                for line in self.__ReceiveData[ConnectIndex].split('\n'):
                    if line.startswith(self.__Cursor):
                        if '本文已被' in line[:line.find('[')]:
                            ErrCode = ErrorCode.PostDeleted
                            self.__ErrorCode = ErrCode
                            return ErrCode, result
                        if '已被' in line[:line.find('<')] or '刪除' in line[:line.find('<')]:
                            ErrCode = ErrorCode.PostDeleted
                            self.__ErrorCode = ErrCode
                            return ErrCode, result
                        # print('line: ' + line[:line.find('[')])
                
                self.__showScreen(ErrCode, sys._getframe().f_code.co_name + ' part 1', ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態! PTT Library 緊急停止')
                self.logout()
                sys.exit()
        
        Lines = self.__ReceiveData[ConnectIndex].split('\n')
        InfoLines = []
        for Line in Lines:
            # print('line: ' + Line)
            if Line.startswith('│'):
                # print('InfoLines: ' + Line)
                InfoLines.append(Line)
        if len(InfoLines) != 3:
            ErrCode = ErrorCode.ParseError
            self.__ErrorCode = ErrCode
            return ErrCode, result

        Target = '#'
        PostID = InfoLines[0]
        PostID = PostID[PostID.find(Target) + len(Target):]
        PostID = PostID[:PostID.find(' ')]
        while PostID.endswith(' '):
            PostID = PostID[:-1]
        
        Target = '文章網址: '
        PostWeb = InfoLines[1]
        PostWeb = PostWeb[PostWeb.find(Target) + len(Target):]
        PostWeb = PostWeb[:PostWeb.find(' ')]
        while PostWeb.endswith(' '):
            PostWeb = PostWeb[:-1]
        try:
            if '特殊文章，無價格記錄' in InfoLines[2]:
                PostMoney = -1
            else:
                PostMoney = int(re.search(r'\d+', InfoLines[2]).group())
        except:
            PostMoney = -1
            self.Log('取得文章價錢失敗: ' + InfoLines[2], LogLevel.DEBUG)
        
        # self.Log('PostID: =' + PostID + '=')
        # self.Log('PostTitle: =' + PostTitle + '=')
        # self.Log('PostWeb: =' + PostWeb + '=')
        # self.Log('PostMoney: =' + str(PostMoney) + '=')

        SendMessage = '\r\r'
        
        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '文章讀取完成',
                '(100%)  目前', 
                _ResponseUnit('', True),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '文章讀取完成',
                '頁 (100%)', 
                _ResponseUnit('', True),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '',
                '目前顯示: 第', 
                _ResponseUnit('', True),
            ),
            _DetectUnit(
                '',
                '瀏覽 第', 
                _ResponseUnit('', True),
            ),
            _DetectUnit(
                '運作出錯',
                '我是' + self.__ID, 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.ParseError
            ),
            _DetectUnit(
                '運作出錯',
                '任意鍵', 
                _ResponseUnit('', True),
                BreakDetect=True,
                ErrCode = ErrorCode.ParseError
            ),
            self.__PTTBUGDetectUnit
        ]

        FirstPage = ''
        PageIndex = 2
        # 預設先把第一頁的前五行拿掉 分別為 作者 標題 時間 分隔線與一行空白
        LastPageIndex = 5
        PostContentListTemp = []
        PostRawContentListTemp = []
        isFirstPage = True
        PostIP = ''

        NewLine, _ = uao.encode('\n')
        NewLineByte = NewLine[0]

        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode != ErrorCode.Success:
                self.Log('操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                self.__ErrorCode = ErrCode
                return ErrCode, None
            
            # self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)

            isDetectedTarget = False

            if FirstPage == '':
                FirstPage = self.__ReceiveData[ConnectIndex]
                        
            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                    self.Log(DetectTarget.getDisplayMsg(), _LogLevel=LogLevel.DEBUG)
                                        
                    if len(PostIP) == 0:
                        PostIP = re.findall( r'[0-9]+(?:\.[0-9]+){3}', self.__ReceiveData[ConnectIndex])
                        if len(PostIP) > 0:
                            PostIP = PostIP[0]
                 
                    CurrentPage = self.__ReceiveData[ConnectIndex]
                    CurrentRawPage = list(self.__ReceiveRawData[ConnectIndex])

                    if CurrentPage.startswith('[2J'):
                        CurrentPage = CurrentPage[3:]
                        CurrentRawPage = CurrentRawPage[7:]
                    CurrentPageList = CurrentPage.split('\n')

                    PageLineRangeTemp = CurrentPageList.pop()
                    # CurrentRawPageList.pop()
                    # 自幹一個 list pop
                    LastIndex = 0
                    for i in range(len(CurrentRawPage)):
                        if CurrentRawPage[i] == NewLineByte:
                            LastIndex = i
                    if LastIndex != 0:
                        CurrentRawPage = CurrentRawPage[:LastIndex]

                    PageLineRange = re.findall(r'\d+', PageLineRangeTemp)
                    if len(PageLineRange) <= 3:
                        ErrCode = ErrorCode.HasControlCode
                        self.__ErrorCode = ErrCode
                        return ErrCode, None

                    PageLineRange = list(map(int, PageLineRange))[-2:]
                    
                    OverlapLine = LastPageIndex - PageLineRange[0] + 1

                    # 處理分隔線造成的行數計算錯誤
                    if PageLineRange[0] > 1 and PageLineRange[0] < 5:
                        OverlapLine += 1

                    if OverlapLine >= 1 and LastPageIndex != 0:
                        # print('重疊', OverlapLine, '行')
                        CurrentPageList = CurrentPageList[OverlapLine:]
                        # CurrentRawPageList = CurrentRawPageList[OverlapLine:]
                        if not isFirstPage:
                            for i in range(OverlapLine):
                                for ii in range(len(CurrentRawPage)):
                                    if CurrentRawPage[ii] == NewLineByte:
                                        CurrentRawPage = CurrentRawPage[ii + 1:]
                                        break
                    
                    LastPageIndex = PageLineRange[1]

                    PostContentListTemp.extend(CurrentPageList)
                    if not isFirstPage:
                        PostRawContentListTemp.extend([NewLineByte])
                    PostRawContentListTemp.extend(CurrentRawPage)

                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                        break

                    SendMessage = str(PageIndex) + '\r'
                    PageIndex += 1
                    Refresh = True
                    isFirstPage = False
                    break

            if not isDetectedTarget:
                
                if len(self.__ReceiveData[ConnectIndex]) < 500:
                    pass

                self.__showScreen(ErrCode, sys._getframe().f_code.co_name + ' part 2', ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態! PTT Library 緊急停止')
                self.logout()
                sys.exit()
        
        FirstPage = FirstPage[FirstPage.find('[2J 作者'):]
        PostLineList = FirstPage.split('\n')

        if len(PostLineList) < 3:
            ErrCode = ErrorCode.ParseError
            self.__ErrorCode = ErrCode
            return ErrCode, None
        # for line in PostLineList:
        #     print('Q', line)

        Target = '作者  '
        PostAuthor = PostLineList[0]
        PostAuthor = PostAuthor[PostAuthor.find(Target) + len(Target):]
        PostAuthor = PostAuthor[:PostAuthor.find(')') + 1]
        while PostAuthor.endswith(' '):
            PostAuthor = PostAuthor[:-1]
        
        Target = '標題  '
        PostTitle = PostLineList[1]
        PostTitle = PostTitle[PostTitle.find(Target) + len(Target):]
        PostTitle = PostTitle[:PostTitle.find('\r')]
        while PostTitle.endswith(' '):
            PostTitle = PostTitle[:-1]

        Target = '時間  '
        PostDate = PostLineList[2]
        PostDate = PostDate[PostDate.find(Target) + len(Target):]
        PostDate = PostDate[:PostDate.find('\r')]
        while PostDate.endswith(' '):
            PostDate = PostDate[:-1]

        PostContentList = []
        PostPushList = []
        for line in PostContentListTemp:
            # print('! ' + line)
            if len(PostContentList) == 0:
                # print('QQ: ' + str(PostIP))
                if str(PostIP) in line:
                    PostContentList = PostContentListTemp[:PostContentListTemp.index(line)]
            else:
                while line.startswith(' '):
                    line = line[1:]
                
                CurrentPushType = PushType.Unknow

                if line.startswith('推'):
                    CurrentPushType = PushType.Push
                elif line.startswith('噓'):
                    CurrentPushType = PushType.Boo
                elif line.startswith('→'):
                    CurrentPushType = PushType.Arrow
                
                if CurrentPushType != PushType.Unknow:
                    # print(line)

                    PushAuthor = line
                    PushAuthor = PushAuthor[2:]
                    PushAuthor = PushAuthor[:PushAuthor.find(':')]
                    while PushAuthor.endswith(' '):
                        PushAuthor = PushAuthor[:-1]
                    
                    Target = ': '
                    PushContent = line[:-11]
                    PushContent = PushContent[PushContent.find(Target) + len(Target):]
                    # PushContent = PushContent[:PushContent.find(' ')]
                    while PushContent.endswith(' '):
                        PushContent = PushContent[:-1]

                    PushTime = line[-11:]
                    # print('PushAuthor: =' + PushAuthor + '=')
                    # print('PushContent: =' + PushContent + '=')
                    # print('PushTime: =' + PushTime + '=')

                    CurrentPush = Information.PushInformation(CurrentPushType, PushAuthor, PushContent, PushTime)
                    PostPushList.append(CurrentPush)

        PostContent = '\n'.join(PostContentList)
        PosRawData = PostRawContentListTemp

        # self.Log('PostContent: =' + PostContent + '=')
        # self.Log('PostIP: =' + PostIP + '=')

        result = Information.PostInformation(Board, PostID, PostAuthor,PostDate, PostTitle, PostWeb, PostMoney,PostContent, PostIP, PostPushList, PosRawData)

        self.__WaterBallProceeor()
        self.__ErrorCode = ErrCode
        return ErrCode, result

    def mail(self, UserID, MailTitle, MailContent, SignType):
        self.__IdleTime = 0
        ConnectIndex = 0
        if self.__isMailBoxFull:
            self.__MailFullAPILock = True
            self.Log('信箱已滿，已鎖定其他 API，請盡速清理信箱')

        ErrCode = ErrorCode.Success
        try:
            UserID = str(UserID)
            MailTitle = str(MailTitle)
            MailContent = str(MailContent)
            SignType = int(SignType)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode

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
        MailContentList.append('')

        if self.__MailFullAPILock:
            SendMessage = self.__gotoMainMenu + ' S\r' + UserID + '\r' + MailTitle + '\r'
        else:
            SendMessage = self.__gotoMainMenu + 'M\rS\r' + UserID + '\r' + MailTitle + '\r'

        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '編輯文章 ' + str(int((MailContentListIndex + 1) * 100 / len(MailContentList))) + ' %',
                '編輯文章', 
                _ResponseUnit(MailContentList[MailContentListIndex], True),
            ),
            self.__PTTBUGDetectUnit
        ]
        
        self.__APILock[ConnectIndex].acquire()
        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('超時')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                self.__APILock[ConnectIndex].release()
                self.__ErrorCode = ErrCode
                return ErrCode
            
            isDetectedTarget = False

            for i in range(len(DetectTargetList)):
                if DetectTargetList[i].isMatch(self.__ReceiveData[ConnectIndex]):
                    self.Log(DetectTargetList[i].getDisplayMsg())

                    SendMessage = DetectTargetList[i].getResponse().getSendMessage()
                    Refresh = DetectTargetList[i].getResponse().needRefresh()
                    
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

            if not isDetectedTarget:
                self.__showScreen(ErrCode, sys._getframe().f_code.co_name + ' part 1', ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態! PTT Library 緊急停止')
                self.logout()
                sys.exit()
        if ErrCode != ErrorCode.Success:
            self.__APILock[ConnectIndex].release()
            self.__ErrorCode = ErrCode
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
            # 選擇簽名檔
            _DetectUnit(
                '選擇第 ' + str(SignType) + ' 簽名檔',
                '選擇簽名檔', 
                _ResponseUnit(str(SignType) + '\r', True),
            ),
            _DetectUnit(
                '選擇第 ' + str(SignType) + ' 簽名檔',
                'x=隨機', 
                _ResponseUnit(str(SignType) + '\r', True),
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
            self.__PTTBUGDetectUnit
        ]
        
        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('超時')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                self.__APILock[ConnectIndex].release()
                self.__ErrorCode = ErrCode
                return ErrCode
            
            # self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)

            isDetectedTarget = False

            for i in range(len(DetectTargetList)):
                if DetectTargetList[i].isMatch(self.__ReceiveData[ConnectIndex]):
                    self.Log(DetectTargetList[i].getDisplayMsg())

                    SendMessage = DetectTargetList[i].getResponse().getSendMessage()
                    Refresh = DetectTargetList[i].getResponse().needRefresh()
                    
                    isDetectedTarget = True
                    if DetectTargetList[i].isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTargetList[i].getErrorCode()

                    break

            if not isDetectedTarget:
                self.__showScreen(ErrCode, sys._getframe().f_code.co_name + ' part 2', ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態! PTT Library 緊急停止')
                self.logout()
                sys.exit()
        
        self.__APILock[ConnectIndex].release()
        self.__WaterBallProceeor()

        self.__ErrorCode = ErrCode
        return ErrCode
    def getTime(self):
        
        ConnectIndex = 0
        result = None

        if not self.__APICheck():
            return self.__ErrorCode, result

        self.__APILock[ConnectIndex].acquire()

        for i in range(3):
            ErrCode, result = self.__getTime()
            if ErrCode == ErrorCode.WaitTimeout or ErrCode == ErrorCode.Success:
                break
        
        self.__APILock[ConnectIndex].release()
        self.__WaterBallProceeor()

        self.__ErrorCode = ErrCode
        return ErrCode, result

    def __getTime(self):
        self.__IdleTime = 0
        ConnectIndex = 0

        result = None
        # \x1b\x4fA (上, 下右左 BCD)
        SendMessage = self.__gotoMainMenu + 'P\x1b\x4fC\x1b\x4fD'
        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '',
                '我是' + self.__ID, 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            self.__PTTBUGDetectUnit
        ]
        
        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('超時')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                self.__ErrorCode = ErrCode
                return ErrCode, result
            
            # self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)

            isDetectedTarget = False

            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                    self.Log(DetectTarget.getDisplayMsg(), _LogLevel=LogLevel.DEBUG)

                    SendMessage = DetectTarget.getResponse().getSendMessage()
                    Refresh = DetectTarget.getResponse().needRefresh()
                    
                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                    break

            if not isDetectedTarget:
                # self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)
                # self.Log('無法解析的狀態! PTT Library 緊急停止')
                # sys.exit()
                ErrCode = ErrorCode.ParseError
                self.__ErrorCode = ErrCode
                return ErrCode, result
        if ErrCode != ErrorCode.Success:
            self.__ErrorCode = ErrCode
            return ErrCode, result
        
        LastLine = self.__ReceiveData[ConnectIndex].split('\n').pop()
        LastLineList = list(map(int, re.findall(r'\d+', LastLine)))
        if len(LastLineList) < 3:
            ErrCode = ErrorCode.ParseError
            self.__ErrorCode = ErrCode
            return ErrCode, result
        
        Hour = str(LastLineList[2])
        Min = str(LastLineList[3])

        if len(Hour) == 1:
            Hour = '0' + Hour
        if len(Min) == 1:
            Min = '0' + Min
        result = Hour + ':' + Min

        ErrCode = ErrorCode.Success
        self.__ErrorCode = ErrCode
        return ErrCode, result
    
    def getUser(self, UserID):
        self.__IdleTime = 0
        ConnectIndex = 0

        result = None

        if not self.__APICheck():
            return self.__ErrorCode, result

        try:
            UserID = str(UserID)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, result
        
        self.__APILock[ConnectIndex].acquire()

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
            self.__PTTBUGDetectUnit
        ]
        
        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('超時')
                self.__APILock[ConnectIndex].release()
                self.__ErrorCode = ErrCode
                return ErrCode, result
            elif ErrCode != ErrorCode.Success:
                self.Log('操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                self.__APILock[ConnectIndex].release()
                self.__ErrorCode = ErrCode
                return ErrCode, result
            
            # self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)

            isDetectedTarget = False

            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                    self.Log(DetectTarget.getDisplayMsg(), _LogLevel=LogLevel.DEBUG)

                    SendMessage = DetectTarget.getResponse().getSendMessage()
                    Refresh = DetectTarget.getResponse().needRefresh()
                    
                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                    break

            if not isDetectedTarget:
                self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態! PTT Library 緊急停止')
                self.logout()
                sys.exit()
        if ErrCode != ErrorCode.Success:
            self.__APILock[ConnectIndex].release()
            self.__ErrorCode = ErrCode
            return ErrCode, result
        
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
        
        self.__APILock[ConnectIndex].release()
        self.__WaterBallProceeor()

        ErrCode = ErrorCode.Success
        self.__ErrorCode = ErrCode
        return ErrCode, result
    def getNewestIndex(self, Board='', Search=''):
        self.__IdleTime = 0
        ConnectIndex = 0
        result = 0
        
        Board = str(Board)
        Search = str(Search)

        if Board == '' and Search != '':
            self.Log('郵件模式下無法使用搜尋條件', LogLevel.WARNING)

        self.__APILock[ConnectIndex].acquire()
        if Board == '':

            SendMessage = self.__gotoMainMenu + ' \x1aM0\r$'
            Refresh = True
            isBreakDetect = False
            # 先後順序代表偵測的優先順序
            DetectTargetList = [
                _DetectUnit(
                    '進入信箱',
                    '郵件選單', 
                    _ResponseUnit('', False),
                    BreakDetect=True,
                    ErrCode = ErrorCode.Success
                ),
                # 
                self.__PTTBUGDetectUnit
            ]
            
            while not isBreakDetect:
                ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
                if ErrCode == ErrorCode.WaitTimeout:
                    self.Log('超時')
                    self.__APILock[ConnectIndex].release()
                    
                    self.__ErrorCode = ErrCode
                    return ErrCode, result
                elif ErrCode != ErrorCode.Success:
                    self.Log('操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                    self.__APILock[ConnectIndex].release()
                    
                    self.__ErrorCode = ErrCode
                    return ErrCode, result
                
                # self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)

                isDetectedTarget = False

                for DetectTarget in DetectTargetList:
                    if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                        self.Log(DetectTarget.getDisplayMsg(), _LogLevel=LogLevel.DEBUG)

                        SendMessage = DetectTarget.getResponse().getSendMessage()
                        Refresh = DetectTarget.getResponse().needRefresh()
                        
                        isDetectedTarget = True
                        if DetectTarget.isBreakDetect():
                            isBreakDetect = True
                            ErrCode = DetectTarget.getErrorCode()
                        break

                if not isDetectedTarget:
                    self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)
                    self.Log('無法解析的狀態! PTT Library 緊急停止')
                    self.logout()
                    sys.exit()
            if ErrCode != ErrorCode.Success:
                self.__APILock[ConnectIndex].release()
                self.__ErrorCode = ErrCode
                return ErrCode, result

            MailBoxLineList = self.__ReceiveData[ConnectIndex].split('\n')

            # for i in range(len(MailBoxLineList)):
            #     print('line', i,MailBoxLineList[i])

            result = list(map(int, re.findall(r'\d+', MailBoxLineList[3])))[0]
            
        else:
            
            if not self.__APICheck():
                self.__APILock[ConnectIndex].release()
                return self.__ErrorCode, result

            for i in range(3):
                ErrCode, result = self.__getNewestPostIndex(Board=Board, Search=Search)
                if ErrCode == ErrorCode.Success:
                    self.__APILock[ConnectIndex].release()
                    self.__ErrorCode = ErrCode
                    return ErrCode, result
        
        self.__APILock[ConnectIndex].release()
        self.__WaterBallProceeor()

        ErrCode = ErrorCode.Success
        self.__ErrorCode = ErrCode
        return ErrCode, result
    def getMail(self, MailIndex):
        self.__IdleTime = 0
        ConnectIndex = 0
        result = None

        # 此 api 不受 MailFulllock 影響

        try:
            MailIndex = int(MailIndex)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, result
        
        if MailIndex <= 0:
            self.Log('錯誤的輸入: ' + str(MailIndex))
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, result

        ErrCode, NewestMailIndex = self.getNewestIndex()
        if ErrCode != ErrorCode.Success:
            self.Log('取得最新信箱編號失敗: ' + str(ErrCode))
            self.__ErrorCode = ErrCode
            return ErrCode, result
        if MailIndex > NewestMailIndex:
            self.Log('錯誤的輸入: ' + str(MailIndex))

            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, result
        
        if NewestMailIndex == 0:
            self.Log('信箱中沒有郵件')

            ErrCode = ErrorCode.Success
            self.__ErrorCode = ErrCode
            return ErrCode, result
        else:
            self.Log('信箱中最新郵件編號: ' + str(NewestMailIndex), LogLevel.DEBUG)

        self.__APILock[ConnectIndex].acquire()

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
                '',
                '目前顯示', 
                _ResponseUnit('', False),
            ),
            self.__PTTBUGDetectUnit
        ]
        
        FirstPage = ''
        PageIndex = 2
        # 預設先把第一頁的前五行拿掉 分別為 作者 標題 時間 分隔線與一行空白
        LastPageIndex = 5
        MailContentList = []
        MailRawContentList = []
        isFirstPage = True
        IPLine = ''

        NewLine, _ = uao.encode('\n')
        NewLineByte = NewLine[0]

        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('超時')
                self.__APILock[ConnectIndex].release()

                self.__ErrorCode = ErrCode
                return ErrCode, result
            elif ErrCode != ErrorCode.Success:
                self.Log('操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                self.__APILock[ConnectIndex].release()
                
                self.__ErrorCode = ErrCode
                return ErrCode, result
            
            # self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)

            isDetectedTarget = False

            if FirstPage == '':
                FirstPage = self.__ReceiveData[ConnectIndex]
            
            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                    self.Log(DetectTarget.getDisplayMsg(), _LogLevel=LogLevel.DEBUG)
                    
                    # self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)
                    
                    CurrentPage = self.__ReceiveData[ConnectIndex]
                    CurrentRawPage = list(self.__ReceiveRawData[ConnectIndex])

                    if CurrentPage.startswith('[2J'):
                        CurrentPage = CurrentPage[3:]
                        CurrentRawPage = CurrentRawPage[7:]
                    CurrentPageList = CurrentPage.split('\n')


                    PageLineRange = CurrentPageList.pop()
                    # CurrentRawPage.pop()
                    LastIndex = 0
                    for i in range(len(CurrentRawPage)):
                        if CurrentRawPage[i] == NewLineByte:
                            LastIndex = i
                    if LastIndex != 0:
                        CurrentRawPage = CurrentRawPage[:LastIndex]
                    
                    PageLineRangeTemp = re.findall(r'\d+', PageLineRange)
                    PageLineRangeTemp = list(map(int, PageLineRangeTemp))[-2:]
                    
                    OverlapLine = LastPageIndex - PageLineRangeTemp[0] + 1

                    # 處理分隔線造成的行數計算錯誤
                    if PageLineRange[0] > 1 and PageLineRange[0] < 5:
                        OverlapLine += 1

                    if OverlapLine >= 1 and LastPageIndex != 0:
                        print('重疊', OverlapLine, '行')
                        CurrentPageList = CurrentPageList[OverlapLine:]

                        if not isFirstPage:
                            for i in range(OverlapLine):
                                for ii in range(len(CurrentRawPage)):
                                    if CurrentRawPage[ii] == NewLineByte:
                                        CurrentRawPage = CurrentRawPage[ii + 1:]
                                        break
                    
                    LastPageIndex = PageLineRangeTemp[1]

                    CurrentPage = '\n'.join(CurrentPageList)
                    
                    MailContentList.append(CurrentPage)
                    if not isFirstPage:
                        MailRawContentList.extend([NewLineByte])
                    MailRawContentList.extend(CurrentRawPage)

                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():

                        IPLine = CurrentPageList.pop()

                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                        break
                    
                    SendMessage = str(PageIndex) + '\r'
                    Refresh = True
                    isFirstPage = False
                    PageIndex += 1

            if not isDetectedTarget:
                self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態! PTT Library 緊急停止')
                self.logout()
                sys.exit()
        if ErrCode != ErrorCode.Success:
            self.__APILock[ConnectIndex].release()
            self.__ErrorCode = ErrCode
            return ErrCode, result

        MailLineList = FirstPage.split('\n')

        # for line in MailLineList:
        #     print('Q', line)

        Target = '作者  '
        MailAuthor = MailLineList[0]
        MailAuthor = MailAuthor[MailAuthor.find(Target) + len(Target):]
        MailAuthor = MailAuthor[:MailAuthor.find('\r')]
        while MailAuthor.endswith(' '):
            MailAuthor = MailAuthor[:-1]
        
        Target = '標題  '
        MailTitle = MailLineList[1]
        MailTitle = MailTitle[MailTitle.find(Target) + len(Target):]
        MailTitle = MailTitle[:MailTitle.find('\r')]
        while MailTitle.endswith(' '):
            MailTitle = MailTitle[:-1]
        
        Target = '時間  '
        MailDate = MailLineList[2]
        MailDate = MailDate[MailDate.find(Target) + len(Target):]
        MailDate = MailDate[:MailDate.find('\r')]
        while MailDate.endswith(' '):
            MailDate = MailDate[:-1]
        
        # self.Log('MailAuthor: =' + MailAuthor + '=', LogLevel.DEBUG)
        # self.Log('MailTitle: =' + MailTitle + '=', LogLevel.DEBUG)
        # self.Log('MailDate: =' + MailDate + '=', LogLevel.DEBUG)

        MailContent = '\n'.join(MailContentList)
        MailRawContent = MailRawContentList
        # self.Log('MailContent: =' + MailContent + '=', LogLevel.DEBUG)

        if len(IPLine) < 7:
            # 如果只有一頁的情況，IP 會顯示在第一頁
            IPLine = MailLineList.pop()
            IPLine = IPLine[:IPLine.find('瀏覽')]
        MailIPList = list(map(str, re.findall(r'\d+', IPLine)))
        MailIP = '.'.join(MailIPList)

        # self.Log('MailIP: =' + MailIP + '=', LogLevel.DEBUG)

        result = Information.MailInformation(MailAuthor, MailTitle, MailDate, MailContent, MailIP, MailRawContent)

        self.__APILock[ConnectIndex].release()
        self.__WaterBallProceeor()

        ErrCode = ErrorCode.Success
        self.__ErrorCode = ErrCode
        return ErrCode, result
        
    def giveMoney(self, ID, Money, YourPassword):
        self.__IdleTime = 0
        ConnectIndex = 0

        if not self.__APICheck():
            return self.__ErrorCode

        try:
            ID = str(ID)
            Money = int(Money)
            YourPassword = str(YourPassword)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode
            
        self.__APILock[ConnectIndex].acquire()

        # 前進至主頁面
        SendMessage = '\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD'
        # 前進至發錢的地方
        SendMessage += 'P\rP\rO\r'
        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            #
            _DetectUnit(
                'P 幣不足',
                '你沒有那麼多Ptt幣喔!', 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.NoEnoughP
            ),
            _DetectUnit(
                '輸入幸運兒帳號',
                '這位幸運兒的id', 
                _ResponseUnit(ID + '\r', False),
            ),
            _DetectUnit(
                '輸入金額',
                '要給他多少Ptt幣呢?', 
                _ResponseUnit('\t' + str(Money) + '\r', False),
            ),
            _DetectUnit(
                '確認身分',
                '完成交易前要重新確認您的身份', 
                _ResponseUnit(YourPassword + '\r', False),
            ),
            _DetectUnit(
                '等待交易進行中',
                '交易正在進行中', 
                _ResponseUnit('', False),
            ),
            _DetectUnit(
                '',
                '要修改紅包袋嗎？', 
                _ResponseUnit('\r', False),
            ),
            _DetectUnit(
                '交易成功',
                '按任意鍵繼續', 
                _ResponseUnit('\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD', False),
            ),
            _DetectUnit(
                '',
                '主功能表', 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            self.__PTTBUGDetectUnit
        ]

        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('登入超時重新嘗試')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('登入操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                self.__APILock[ConnectIndex].release()

                self.__ErrorCode = ErrCode
                return ErrCode

            isDetectedTarget = False

            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):

                    self.Log(DetectTarget.getDisplayMsg())

                    SendMessage = DetectTarget.getResponse().getSendMessage()
                    Refresh = DetectTarget.getResponse().needRefresh()
                    
                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():
                        self.__isConnected[ConnectIndex] = True
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                        break
            if not isDetectedTarget:
                self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態! PTT Library 緊急停止')
                self.logout()
                sys.exit()
        
        self.__APILock[ConnectIndex].release()
        self.__WaterBallProceeor()

        self.__ErrorCode = ErrCode
        return ErrCode
    def changePassword(self, OldPassword, NewPassword):
        self.__IdleTime = 0
        ConnectIndex = 0

        ErrCode = ErrorCode.Success

        if not self.__APICheck():
            return self.__ErrorCode

        try:
            OldPassword = str(OldPassword)
            NewPassword = str(NewPassword)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)

            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode

        if len(NewPassword) > 8:
            self.Log('新密碼超過八位後將被系統省略', LogLevel.WARNING)

            while len(NewPassword) > 8:
                NewPassword = NewPassword[:-1]
        
        self.__APILock[ConnectIndex].acquire()

        # 前進至主頁面
        SendMessage = '\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD'
        # 前進至修改密碼的地方
        SendMessage += 'U\rI\r2\r'
        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '輸入舊密碼',
                '請輸入原密碼', 
                _ResponseUnit(OldPassword + '\r', False),
                LogLV = LogLevel.DEBUG,
            ),
            _DetectUnit(
                '輸入新密碼',
                '請設定新密碼', 
                _ResponseUnit(NewPassword + '\r', False),
                LogLV = LogLevel.DEBUG,
            ),
            _DetectUnit(
                '確認新密碼',
                '請檢查新密碼', 
                _ResponseUnit(NewPassword + '\r', False),
                LogLV = LogLevel.DEBUG,
            ),
            _DetectUnit(
                '確認',
                '您確定(Y/N)', 
                _ResponseUnit('y\r', True),
                LogLV = LogLevel.DEBUG,
            ),
            _DetectUnit(
                '注意！您已將舊密碼更換為新密碼(' + NewPassword + ')',
                '我是' + self.__ID, 
                _ResponseUnit('\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fD', False),
            ),
            _DetectUnit(
                '密碼不正確',
                '您輸入的密碼不正確', 
                _ResponseUnit('y\r', True),
                BreakDetect=True,
                ErrCode = ErrorCode.WrongPassword
            ),
            _DetectUnit(
                '',
                '主功能表', 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            self.__PTTBUGDetectUnit
        ]

        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('操作超時重新嘗試')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('操作操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                self.__APILock[ConnectIndex].release()

                self.__ErrorCode = ErrCode
                return ErrCode

            isDetectedTarget = False

            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):

                    self.Log(DetectTarget.getDisplayMsg(), DetectTarget.getLogLevel())

                    SendMessage = DetectTarget.getResponse().getSendMessage()
                    Refresh = DetectTarget.getResponse().needRefresh()
                    
                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():
                        self.__isConnected[ConnectIndex] = True
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                        break
                        
                    break
            if not isDetectedTarget:

                self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態! PTT Library 緊急停止')
                self.logout()
                sys.exit()
        
        self.__APILock[ConnectIndex].release()
        self.__WaterBallProceeor()

        self.__ErrorCode = ErrCode
        return ErrCode

    def replyPost(self, Board, Content, ReplyType, PostID='', Index=-1):
        self.__IdleTime = 0
        ConnectIndex = 0
        ErrCode = ErrorCode.Success

        if not self.__APICheck():
            return self.__ErrorCode

        try:
            Board = str(Board)
            Content = str(Content)
            ReplyType = int(ReplyType)
            PostID = str(PostID)
            Index = int(Index)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode

        ReplyResponse = ''
        if ReplyType == ReplyPostType.Board:
            ReplyResponse = 'F'
        elif ReplyType == ReplyPostType.Mail:
            ReplyResponse = 'M'
        elif ReplyType == ReplyPostType.Board_Mail:
            ReplyResponse = 'B'
        else:
            self.Log('回文種類輸入錯誤', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode

        if PostID == '' and Index == -1:
            self.Log('輸入參數錯誤')
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode
        
        self.__APILock[ConnectIndex].acquire()

        Board = str(Board)
        Content = str(Content)
        PostID = str(PostID)
        Index = int(Index)

        # 前進至主頁面
        SendMessage = self.__gotoMainMenu + 'qs' + Board + '\r\x03\x03 '
        # 前進至文章
        if PostID != '':
            SendMessage += '#' + PostID + '\r\rr'
        elif Index != -1:
            SendMessage += str(Index) + '\r\rr'
        
        SendMessage += ReplyResponse + '\r'
        SendMessage += 'y\ry\r'
        
        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '編輯文章',
                '編輯文章', 
                _ResponseUnit(Content + '\r\x18s\r', True),
                # 
            ),
            _DetectUnit(
                '不加簽名檔',
                'x=隨機', 
                _ResponseUnit('0\r', False),
            ),
            _DetectUnit(
                '送出回文',
                '請按任意鍵繼續', 
                _ResponseUnit(self.__gotoMainMenu, False),
            ),
            _DetectUnit(
                '自存底稿',
                '是否自存底稿', 
                _ResponseUnit('y\r', False),
            ),
            _DetectUnit(
                '',
                '我是' + self.__ID, 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            self.__PTTBUGDetectUnit
        ]

        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('操作超時重新嘗試')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('操作操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                self.__APILock[ConnectIndex].release()

                self.__ErrorCode = ErrCode
                return ErrCode

            isDetectedTarget = False

            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):

                    self.Log(DetectTarget.getDisplayMsg())

                    SendMessage = DetectTarget.getResponse().getSendMessage()
                    Refresh = DetectTarget.getResponse().needRefresh()
                    
                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():
                        self.__isConnected[ConnectIndex] = True
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                        break
            if not isDetectedTarget:

                self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態! PTT Library 緊急停止')
                self.logout()
                sys.exit()
        
        self.__APILock[ConnectIndex].release()
        self.__WaterBallProceeor()

        self.__ErrorCode = ErrCode
        return ErrCode
    def __crawlBoardThread(self, ConnectIndex, Board, PostHandler, StartIndex, EndIndex, Search):
        self.Log(str(ConnectIndex) + ' ' + Board + ' ' + str(StartIndex) + ' ' + str(EndIndex) + ' ' + Search)

        if not self.__isConnected[ConnectIndex] and ConnectIndex > 0:
            # self.__CrawLock.acquire()
            self.__connectRemote(ConnectIndex)
            self.__EnableLoginCount += 1
            # self.__CrawLock.release()
        
        while self.__EnableLoginCount < self.__EnableLogin:
            time.sleep(1)

        for PostIndex in range(StartIndex, EndIndex):
            self.__IdleTime = 0

            ErrCode, Post = self.getPost(Board, PostIndex=PostIndex, _ConnectIndex=ConnectIndex, Search=Search)

            if not self.__isBackground:
                self.__ProgressBarCount += 1
                self.__ProgressBar.update(self.__ProgressBarCount)
            
            if ErrCode == ErrorCode.PostDeleted:
                self.__DeleteCrawCount += 1
                continue
            elif ErrCode != ErrorCode.Success:
                self.__ErrorGetPostList.append([ErrCode, Board, PostIndex])
                continue
            
            self.__SuccessCrawCount += 1
            
            self.__CrawLock.acquire()
            # self.Log(Post.getTitle())
            try:
                PostHandler(Post)
            except TypeError:
                self.Log('PostHandler 介面錯誤', LogLevel.WARNING)
            except:
                self.Log('PostHandler 未知錯誤', LogLevel.WARNING)

            self.__CrawLock.release()
        
        self.Log('頻道 ' + str(ConnectIndex) + ' 爬行完畢', LogLevel.DEBUG)
        return
    def crawlBoard(self, Board, PostHandler, MaxMultiLogin=2, StartIndex=0, EndIndex=0, Search=''):
        ErrCode = ErrorCode.Success

        if not self.__APICheck():
            return self.__ErrorCode, 0, 0

        try:
            Board = str(Board)
            StartIndex = int(StartIndex)
            EndIndex = int(EndIndex)
            MaxMultiLogin = int(MaxMultiLogin)
            Search = str(Search)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)

            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, 0, 0

        if MaxMultiLogin < 1 or 5 < MaxMultiLogin:
            self.Log('多重登入設定錯誤', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, 0, 0
        
        self.__MaxMultiLogin = MaxMultiLogin

        ErrCode, NewestIndex = self.getNewestIndex(Board=Board, Search=Search)
        if ErrCode != ErrorCode.Success:
            self.__ErrorCode = ErrCode
            return ErrCode, 0, 0
        
        if StartIndex == 0 and EndIndex == 0:
            StartIndex = 1
            EndIndex = NewestIndex
        elif StartIndex < 1 or NewestIndex < StartIndex:
            self.Log('文章編號區間輸入錯誤: 開始標記不在 ' + Board + ' 板範圍中', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, 0, 0
        elif EndIndex < 1 or NewestIndex < EndIndex:
            self.Log('文章編號區間輸入錯誤: 結束標記不在 ' + Board + ' 板範圍中', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, 0, 0
        elif EndIndex < StartIndex:
            self.Log('文章編號區間輸入錯誤: 開始標記比結束標記大', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, 0, 0

        self.__CrawLock = threading.Lock()
        self.__TotalPost = EndIndex - StartIndex + 1
        self.__EnableLogin = 1
        self.__SuccessCrawCount = 0
        self.__DeleteCrawCount = 0
        self.__ErrorGetPostList = []

        if not self.__isBackground:
            self.__ProgressBar = progressbar.ProgressBar(max_value=self.__TotalPost)
            self.__ProgressBarCount = 0

        self.Log('總爬行文章: ' + str(self.__TotalPost) + ' 篇')
        
        MaxThreadPost = 100
        TempStr = '啟動連線頻道 '
        for i in range(self.__MaxMultiLogin):
            if (i + 1) * MaxThreadPost <= self.__TotalPost:
                self.__EnableLogin += 1
                TempStr += str(i) + ' '
        self.Log(TempStr)

        self.__CrawPoolList = []
        CrawThreadList = []
        Basic = int(self.__TotalPost / self.__EnableLogin)
        LastEndIndexTemp = StartIndex
        for i in range(0, self.__EnableLogin):
            StartIndexTemp = LastEndIndexTemp
            EndIndexTemp = (i + 1) * Basic + StartIndex
            if self.__TotalPost % self.__EnableLogin > i:
                EndIndexTemp += 1
            LastEndIndexTemp = EndIndexTemp

            # self.Log(str(StartIndexTemp) + ' ' + str(EndIndexTemp) + ':' + str(EndIndexTemp - StartIndexTemp))
            # self.__CrawPoolList.append([StartIndexTemp, EndIndexTemp])
            CrawThreadList.append(threading.Thread(target=self.__crawlBoardThread, args=(i, Board, PostHandler, StartIndexTemp, EndIndexTemp, Search)))
        
        self.__EnableLoginCount = 1

        for SubThread in CrawThreadList:
            SubThread.start()
        for SubThread in CrawThreadList:
            SubThread.join()
        
        if not self.__isBackground:
            self.__ProgressBar.update(self.__TotalPost)
            self.__ProgressBar.finish()
        
        for ErrorEvent in self.__ErrorGetPostList:
            self.Log('-----------------', LogLevel.DEBUG)
            self.Log(ErrorEvent[0], LogLevel.DEBUG)
            self.Log(ErrorEvent[1], LogLevel.DEBUG)
            self.Log(ErrorEvent[2], LogLevel.DEBUG)
        
        if len(self.__ErrorGetPostList) != 0:
            self.Log('-----------------', LogLevel.DEBUG)
        
        self.__WaterBallProceeor()

        self.__ErrorCode = ErrCode
        return ErrCode, self.__SuccessCrawCount, self.__DeleteCrawCount
    
    def throwWaterBall(self, WaterBallTarget, WaterBallContent):
        self.__IdleTime = 0
        ConnectIndex = 0
        ErrCode = ErrorCode.Success

        if not self.__APICheck():
            return self.__ErrorCode

        try:
            WaterBallTarget = str(WaterBallTarget)
            WaterBallContent = str(WaterBallContent)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode

        ErrCode, User = self.getUser(WaterBallTarget)
        
        if ErrCode != ErrorCode.Success:
            self.__ErrorCode = ErrCode
            return ErrCode

        # print(WaterBallTarget + ': ' + User.getState())
        
        if '不在站上' in User.getState():
            ErrCode = ErrorCode.UserNotOnline
            self.__ErrorCode = ErrCode
            return ErrCode
        
        self.__APILock[ConnectIndex].acquire()

        # 前進至主頁面
        SendMessage = self.__gotoMainMenu
        SendMessage += 'T\rU\rs' + WaterBallTarget + '\rw'

        Refresh = True
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '打開呼叫器',
                '您的呼叫器目前設定為關閉', 
                _ResponseUnit('y', True),
            ),
            _DetectUnit(
                '丟 ' + WaterBallTarget + ' 水球',
                '丟 ' + WaterBallTarget + ' 水球', 
                _ResponseUnit(WaterBallContent + '\r\r', True),
            ),
            _DetectUnit(
                '',
                '', 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            self.__PTTBUGDetectUnit
        ]

        while not isBreakDetect:
            # self.Log('SendMessage: \n' + SendMessage )
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('操作超時重新嘗試')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('操作操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                self.__APILock[ConnectIndex].release()

                self.__ErrorCode = ErrCode
                return ErrCode
            # self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)

            isDetectedTarget = False

            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):

                    self.Log(DetectTarget.getDisplayMsg())

                    isDetectedTarget = True
                    if DetectTarget.isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                    
                    SendMessage = DetectTarget.getResponse().getSendMessage()
                    Refresh = DetectTarget.getResponse().needRefresh()

                    break
            if not isDetectedTarget:

                self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態! PTT Library 緊急停止')
                self.logout()
                sys.exit()
        
        self.__APILock[ConnectIndex].release()
        self.__WaterBallProceeor()
        
        self.__ErrorCode = ErrCode
        return ErrCode
    
    def delPost(self, Board, PostID='', PostIndex=0):
        self.__IdleTime = 0
        ConnectIndex = 0
        ErrCode = ErrorCode.Success

        if not self.__APICheck():
            return self.__ErrorCode

        try:
            Board = str(Board)
            PostID = str(PostID)
            PostIndex = int(PostIndex)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)
            
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode

        if len(Board) == 0:
            self.Log('看板名稱輸入錯誤: ' + str(Board))
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode

        if PostIndex != 0 and PostID != '':
            self.Log('文章編號與代碼輸入錯誤: 同時輸入')
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode

        if PostIndex == 0 and PostID == '':
            self.Log('文章編號與代碼輸入錯誤: 皆無輸入')
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode
        
        if PostID != '':
            ErrCode, Post = self.getPost(Board, PostID=PostID)
        if PostIndex != 0:
            ErrCode, Post = self.getPost(Board, PostIndex=PostIndex)
        
        if ErrCode != ErrorCode.Success:
            self.__ErrorCode = ErrCode
            return ErrCode
        if not Post.getAuthor().startswith(self.__ID):
            ErrCode = ErrorCode.NoPermission
            self.__ErrorCode = ErrCode
            return ErrCode
        
        self.__APILock[ConnectIndex].acquire()

        SendMessage = '\x1b\x4fD\x1b\x4fD\x1b\x4fD\x1b\x4fDqs' + Board + '\r\x03\x03 '
        # 前進至文章
        if PostID != '':
            SendMessage += '#' + PostID + '\rd'
        elif PostIndex != -1:
            SendMessage += str(PostIndex) + '\rd'
        
        Refresh = False
        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '確定刪除文章',
                '請確定刪除(Y/N)?', 
                _ResponseUnit('y\r', False),
            ),
            _DetectUnit(
                '正在刪除文章',
                '請按任意鍵繼續', 
                _ResponseUnit(' ', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '',
                '', 
                _ResponseUnit('', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            self.__PTTBUGDetectUnit
        ]

        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('操作超時重新嘗試')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('操作操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                self.__APILock[ConnectIndex].release()

                self.__ErrorCode = ErrCode
                return ErrCode

            isDetectedTarget = False
            
            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                    isDetectedTarget = True
                    
                    self.Log(DetectTarget.getDisplayMsg())

                    if DetectTarget.isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                        break

                    SendMessage = DetectTarget.getResponse().getSendMessage()
                    Refresh = DetectTarget.getResponse().needRefresh()

                    break

            if not isDetectedTarget:

                self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態! PTT Library 緊急停止')
                self.logout()
                sys.exit()

        self.__WaterBallProceeor()
        self.__APILock[ConnectIndex].release()

        self.__ErrorCode = ErrCode
        return ErrCode
    def operateFriendList(self, inputOperateType, inputFriendListType, SpecialListIndex=-1, ID='' , SpecialListName=''):
        self.__IdleTime = 0
        ErrCode = ErrorCode.Success
        result = None
        ConnectIndex = 0

        if not self.__APICheck():
            return self.__ErrorCode

        try:
            inputOperateType = int(inputOperateType)
            inputFriendListType = int(inputFriendListType)
            SpecialListIndex = int(SpecialListIndex)
            ID = str(ID)
            SpecialListName = str(SpecialListName)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)

            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, result

        if inputFriendListType < FriendListType.MinValue or FriendListType.MaxValue < inputFriendListType:
            self.Log('輸入錯誤: FriendListType 錯誤', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, result
        
        if inputFriendListType == FriendListType.OtherSpecial:
            if SpecialListIndex < 0 or 9 < SpecialListIndex:
                self.Log('輸入錯誤: SpecialListIndex 錯誤', LogLevel.WARNING)
                ErrCode = ErrorCode.ErrorInput
                self.__ErrorCode = ErrCode
                return ErrCode, result
        
        if inputOperateType < OperateType.MinValue or OperateType.MaxValue < inputOperateType:
            self.Log('輸入錯誤: OperateType 錯誤', LogLevel.WARNING)
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, result
        if inputOperateType == OperateType.Add or inputOperateType == OperateType.Del:
            if ID == '':
                self.Log('輸入錯誤: 新增或刪除模式下，需要輸入 ID', LogLevel.WARNING)
                ErrCode = ErrorCode.ErrorInput
                self.__ErrorCode = ErrCode
                return ErrCode, result
        
        if inputOperateType == OperateType.Add:
            ErrCode, User = self.getUser(ID)
            if ErrCode == ErrorCode.NoUser:
                self.Log('沒有此使用者', LogLevel.WARNING)

                self.__ErrorCode = ErrCode
                return ErrCode, result
            elif ErrCode != ErrorCode.Success:
                self.Log('取得使用者資訊錯誤 錯誤碼:' + str(ErrCode))
                self.__ErrorCode = ErrCode
                return ErrCode, result

        self.__APILock[ConnectIndex].acquire()

        SendMessage = self.__gotoMainMenu + 'N\r'

        # 前進至個別選單
        if inputFriendListType == FriendListType.GoodFriend:
            SendMessage += 'O\r'
        elif inputFriendListType == FriendListType.BadGuy:
            SendMessage += 'B\r'
        elif inputFriendListType == FriendListType.LoginNotification:
            SendMessage += 'A\r'
        elif inputFriendListType == FriendListType.OtherSpecial:
            SendMessage += 'S\r' + str(SpecialListIndex) + '\r'

        Refresh = True
        isBreakDetect = False
        if inputOperateType == OperateType.Add:
            DetectTargetList = [
                _DetectUnit(
                    '系統正在更新清單...',
                    '正在更新與同步線上使用者及好友名單', 
                    _ResponseUnit(' ', False),
                ),
                _DetectUnit(
                    '',
                    '請為此特別名單取一個簡短名稱:' + SpecialListName, 
                    _ResponseUnit('\r', False),
                ),
                _DetectUnit(
                    '',
                    '請為此特別名單取一個簡短名稱', 
                    _ResponseUnit(self.__delAllWord + SpecialListName + '\r', False),
                ),
                _DetectUnit(
                    '新增名單',
                    '(A)增加', 
                    _ResponseUnit('A\r' + ID + '\r\r', True),
                ),
                _DetectUnit(
                    '退出名單',
                    '【名單編輯】', 
                    _ResponseUnit('\r', False),
                    BreakDetect=True,
                    ErrCode = ErrorCode.Success
                ),
                self.__PTTBUGDetectUnit
            ]
        elif inputOperateType == OperateType.Del:
            DetectTargetList = [
                _DetectUnit(
                    '系統正在更新清單...',
                    '正在更新與同步線上使用者及好友名單', 
                    _ResponseUnit(' ', False),
                ),
                _DetectUnit(
                    '',
                    '請為此特別名單取一個簡短名稱:' + SpecialListName, 
                    _ResponseUnit('\r', False),
                ),
                _DetectUnit(
                    '',
                    '請為此特別名單取一個簡短名稱', 
                    _ResponseUnit(self.__delAllWord + SpecialListName + '\r', False),
                ),
                _DetectUnit(
                    '刪除名單',
                    '(D)刪除', 
                    _ResponseUnit('D\r' + ID + '\r\r', True),
                ),
                _DetectUnit(
                    '退出名單',
                    '【名單編輯】', 
                    _ResponseUnit('\r', False),
                    BreakDetect=True,
                    ErrCode = ErrorCode.Success
                ),
                self.__PTTBUGDetectUnit
            ]
        elif inputOperateType == OperateType.Query:
            DetectTargetList = [
                _DetectUnit(
                    '解析名單',
                    '名單上限', 
                    _ResponseUnit('Q\r', False),
                ),
                _DetectUnit(
                    '退出名單',
                    '【名單編輯】', 
                    _ResponseUnit('\r', False),
                    BreakDetect=True,
                    ErrCode = ErrorCode.Success
                ),
                self.__PTTBUGDetectUnit
            ]

        ListPage = ''

        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=Refresh)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('操作超時重新嘗試')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('操作操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                self.__APILock[ConnectIndex].release()

                self.__ErrorCode = ErrCode
                return ErrCode, result

            isDetectedTarget = False
            
            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                    isDetectedTarget = True
                    
                    self.Log(DetectTarget.getDisplayMsg())

                    if '解析名單' == DetectTarget.getDisplayMsg():
                        ListPage = self.__ReceiveData[ConnectIndex]

                    if DetectTarget.isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                        break

                    SendMessage = DetectTarget.getResponse().getSendMessage()
                    Refresh = DetectTarget.getResponse().needRefresh()

                    break

            if not isDetectedTarget:

                self.__showScreen(ErrCode, sys._getframe().f_code.co_name, ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態! PTT Library 緊急停止')
                self.logout()
                sys.exit()
        
        if inputOperateType == OperateType.Query:
            result = []
            List = ListPage.split('\n')[2:]

            for Line in List:
                if Line.startswith('[K'):
                    Line = Line[2:]
                TempList = Line.split(' ')
                TempList = list(filter(None, TempList))
                result.extend(TempList)

        self.__WaterBallProceeor()
        self.__APILock[ConnectIndex].release()

        self.__ErrorCode = ErrCode
        return ErrCode, result

    def getHistoricalWaterBall(self, WaterBallOperateType=0):
        self.__IdleTime = 0
        ErrCode = ErrorCode.Success
        result = []
        ConnectIndex = 0

        if not self.__APICheck():
            return self.__ErrorCode, result

        try:
            WaterBallOperateType = int(WaterBallOperateType)
        except:
            self.Log('輸入錯誤', LogLevel.WARNING)

            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, result

        if WaterBallOperateType == 0:
            WaterBallOperateType = Information.WaterBallOperateType.DoNothing
        elif WaterBallOperateType < Information.WaterBallOperateType.MinValue or Information.WaterBallOperateType.MaxValue < WaterBallOperateType:
            self.Log('錯誤的輸入: OperateType 輸入錯誤', LogLevel.WARNING)
            
            ErrCode = ErrorCode.ErrorInput
            self.__ErrorCode = ErrCode
            return ErrCode, result

        self.__APILock[ConnectIndex].acquire()

        SendMessage = self.__gotoMainMenu + 'T\rD\r'

        isBreakDetect = False
        # 先後順序代表偵測的優先順序
        DetectTargetList = [
            _DetectUnit(
                '水球頁面讀取完成',
                '(100%)  目前', 
                _ResponseUnit('qC\rY\r', True),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '水球頁面讀取完成',
                '頁 (100%)', 
                _ResponseUnit('\x1b\x4fDC\rY\r', True),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '',
                '目前顯示: 第', 
                _ResponseUnit('', True),
            ),
            _DetectUnit(
                '',
                '瀏覽 第', 
                _ResponseUnit('', True),
            ),
            _DetectUnit(
                '無訊息記錄',
                '◆ 暫無訊息記錄', 
                _ResponseUnit('y\r', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            _DetectUnit(
                '',
                '按任意鍵繼續', 
                _ResponseUnit(' ', False),
                BreakDetect=True,
                ErrCode = ErrorCode.Success
            ),
            self.__PTTBUGDetectUnit
        ]
        NoMsg = False
        PageIndex = 2
        # 預設先把第一頁的前五行拿掉 分別為 作者 標題 時間 分隔線與一行空白
        LastPageIndex = 0
        WaterBallListTemp = []

        while not isBreakDetect:
            ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=True)
            if ErrCode == ErrorCode.WaitTimeout:
                self.Log('操作超時重新嘗試')
                break
            elif ErrCode != ErrorCode.Success:
                self.Log('操作操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                self.__APILock[ConnectIndex].release()

                self.__ErrorCode = ErrCode
                return ErrCode, result

            isDetectedTarget = False

            for DetectTarget in DetectTargetList:
                if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                    isDetectedTarget = True
                    
                    self.Log(DetectTarget.getDisplayMsg())
                    
                    if '無訊息記錄' in DetectTarget.getDisplayMsg():
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                        NoMsg = True
                        break

                    CurrentPage = self.__ReceiveData[ConnectIndex]
                    if CurrentPage.startswith('[2J'):
                        CurrentPage = CurrentPage[3:]

                    CurrentPageList = CurrentPage.split('\n')
                    
                    PageLineRangeTemp = CurrentPageList[-1][CurrentPageList[-1].find('  瀏覽 第'):]
                    
                    PageLineRange = re.findall(r'\d+', PageLineRangeTemp)
                    PageLineRange = list(map(int, PageLineRange))[3:]

                    OverlapLine = LastPageIndex - PageLineRange[0] + 1

                    if OverlapLine >= 1 and LastPageIndex != 0:
                        # print('重疊', OverlapLine, '行')
                        CurrentPageList = CurrentPageList[OverlapLine:]

                    LastPageIndex = PageLineRange[1]
                    CurrentPageList[-1] = CurrentPageList[-1][:CurrentPageList[-1].rfind(']') + 1]

                    WaterBallListTemp.extend(CurrentPageList)

                    if DetectTarget.isBreakDetect():
                        isBreakDetect = True
                        ErrCode = DetectTarget.getErrorCode()
                        break

                    SendMessage = str(PageIndex) + '\r'
                    PageIndex += 1

                    break

            if not isDetectedTarget:

                self.__showScreen(ErrCode, sys._getframe().f_code.co_name + 'Part 1', ConnectIndex=ConnectIndex)
                self.Log('無法解析的狀態! PTT Library 緊急停止')
                self.logout()
                sys.exit()
        
        if not NoMsg:
            for i in range(len(WaterBallListTemp)):
                while WaterBallListTemp[i].startswith(' '):
                    WaterBallListTemp[i] = WaterBallListTemp[i][1:]

            for line in WaterBallListTemp:
                Type = 0
                if line.startswith('To'):
                    # print('Send water ball: ' + line)
                    Type = WaterBallType.Send
                    WaterBallAuthor = line[3 : line.find(':')]
                elif line.startswith('★'):
                    # print('Catch water ball: ' + line)
                    Type = WaterBallType.Catch
                    WaterBallAuthor = line[1 : line.find(' ')]

                if Type != 0:
                    
                    WaterBallContent = line[line.find(' ') + 1 : line.rfind('[') - 1]
                    WaterBallDate = line[line.rfind('[') + 1 : line.rfind(']')]

                    CurrentWaterBall = Information.WaterBallInformation(Type, WaterBallAuthor, WaterBallContent, WaterBallDate)
                    result.append(CurrentWaterBall)
            
            isBreakDetect = False
            # 先後順序代表偵測的優先順序
            if WaterBallOperateType == Information.WaterBallOperateType.Clear:
                SendMessage = 'qC\rY\r' + self.__gotoMainMenu
                DetectTargetList = [
                    _DetectUnit(
                        '清除水球歷史紀錄完成',
                        '我是' + self.__ID, 
                        _ResponseUnit(' ', False),
                        BreakDetect=True,
                    ),
                    self.__PTTBUGDetectUnit,
                ]
            elif WaterBallOperateType == Information.WaterBallOperateType.Mail:
                SendMessage = 'qM\r' + self.__gotoMainMenu
                DetectTargetList = [
                    _DetectUnit(
                        '水球歷史紀錄寄回信箱完成',
                        '我是' + self.__ID, 
                        _ResponseUnit(' ', False),
                        BreakDetect=True,
                    ),
                    self.__PTTBUGDetectUnit,
                ]
            else:
                SendMessage = 'qR\r' + self.__gotoMainMenu
                DetectTargetList = [
                    _DetectUnit(
                        '保存水球歷史紀錄',
                        '我是' + self.__ID, 
                        _ResponseUnit(' ', False),
                        BreakDetect=True,
                    ),
                    self.__PTTBUGDetectUnit,
                ]

            while not isBreakDetect:
                ErrCode, CatchIndex = self.__operatePTT(ConnectIndex, SendMessage=SendMessage, Refresh=True)
                if ErrCode == ErrorCode.WaitTimeout:
                    self.Log('操作超時重新嘗試')
                    break
                elif ErrCode != ErrorCode.Success:
                    self.Log('操作操作失敗 錯誤碼: ' + str(ErrCode), LogLevel.DEBUG)
                    self.__APILock[ConnectIndex].release()

                    self.__ErrorCode = ErrCode
                    return ErrCode, result

                isDetectedTarget = False
                
                for DetectTarget in DetectTargetList:
                    if DetectTarget.isMatch(self.__ReceiveData[ConnectIndex]):
                        isDetectedTarget = True
                        
                        self.Log(DetectTarget.getDisplayMsg())

                        if DetectTarget.isBreakDetect():
                            isBreakDetect = True
                            ErrCode = DetectTarget.getErrorCode()
                            break

                        SendMessage = DetectTarget.getResponse().getSendMessage()
                        
                        break

                if not isDetectedTarget:

                    self.__showScreen(ErrCode, sys._getframe().f_code.co_name + 'Part 2', ConnectIndex=ConnectIndex)
                    self.Log('無法解析的狀態! PTT Library 緊急停止')
                    self.logout()
                    sys.exit()

        self.__WaterBallProceeor()
        self.__APILock[ConnectIndex].release()

        self.__ErrorCode = ErrCode
        return ErrCode, result
    def getErrorCode(self):
        return self.__ErrorCode
    def readPostFile(self, FileName):
        self.__IdleTime = 0
        return Util.readPostFile(FileName)
    def getVersion(self):
        self.__IdleTime = 0
        return Version
        
if __name__ == '__main__':

    print('PTT Library v ' + Version)
    print('Developed by PTT CodingMan')