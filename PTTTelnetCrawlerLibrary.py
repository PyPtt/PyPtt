# -*- coding: utf8 -*-
import sys
import telnetlib
import time
import re
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import PTTTelnetCrawlerLibraryUtil
import PTTTelnetCrawlerLibraryErrorCode

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
        self.__Board = Board + ''
        self.__PostID = PostID + ''
        self.__Author = Author + ''
        self.__Date = Date + ''
        self.__Title = Title + ''
        self.__PostContent = PostContent + ''
        self.__Money = Money
        self.__WebUrl = WebUrl + ''
        self.__PushList = PushList
        self.__OriginalData = OriginalData + ''

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
    def __init__(self, ID, Password, kickOtherLogin):
 
        PTTTelnetCrawlerLibraryUtil.Log('ID: ' + ID)

        TempPW = ''

        for i in range(len(Password)):
            TempPW += '*'
        
        PTTTelnetCrawlerLibraryUtil.Log('Password: ' + TempPW)
        if kickOtherLogin:
            PTTTelnetCrawlerLibraryUtil.Log('This connection will kick other login')
        else :
            PTTTelnetCrawlerLibraryUtil.Log('This connection will NOT kick other login')

        self.__host = 'ptt.cc'
        self.__ID = ID
        self.__Password = Password
        self.__kickOtherLogin = kickOtherLogin
        self.__ReceiveData = ''
        self.__isConnected = False
        
        self.PushType_Push =         1
        self.PushType_Boo =          2
        self.PushType_Arrow =        3
        
        self.__SleepTime =         0.5
        self.__DefaultTimeout =      1
        self.__Timeout =            10
        self.__CurrentTimeout =      0
        
        self.__connectRemote()
    def Log(self, Message):
        PTTTelnetCrawlerLibraryUtil.Log(Message)
    def isLoginSuccess(self):
        return self.__isConnected
    def removeColor(self):
        return None
        #Can someone write perfect re code for this?
        self.__ReceiveData = self.__ReceiveData.replace('\x1b', '')
        self.__ReceiveData = self.__ReceiveData.replace('[K', '')
        self.__ReceiveData = self.__ReceiveData.replace('[m', '')
        self.__ReceiveData = self.__ReceiveData.replace('[H', '')
        self.__ReceiveData = self.__ReceiveData.replace('[2J', '')
        
        self.__ReceiveData = self.__ReceiveData.replace('[0;1;37;44m', '')
                    
        ColorList = ['H', 'm']
        
        for i in range(0, 48):
            self.__ReceiveData = self.__ReceiveData.replace('[' + str(i) + 'm', '')
            for ii in range(1, 48):
                for Color in ColorList:
                    self.__ReceiveData = self.__ReceiveData.replace('[' + str(i) + ';' + str(ii) + Color, '')
        
        for i in range(0, 38):
            for ii in range(0, 2):
                for iii in range(30, 48):
                    self.__ReceiveData = self.__ReceiveData.replace('[' + str(ii) + ';' + str(i) + ';' + str(iii) + 'm', '')
        
        for i in range(0, 2):
            for ii in range(0, 2):
                for iii in range(37, 48):
                    for iiii in range(37, 48):
                        self.__ReceiveData = self.__ReceiveData.replace('[' + str(i) + ';' + str(ii) + ';' + str(iii) + ';' + str(iiii) + 'm', '')
    
    def __readScreen(self, Message='', ExpectTarget=[]):
        
        result = -1
        ErrorCode = PTTTelnetCrawlerLibraryErrorCode.UnknowError
        try:
            self.__telnet.write(str(Message + '\x0C').encode('big5'))
        except ConnectionResetError:
            PTTTelnetCrawlerLibraryUtil.Log('Remote reset connection...')
            self.__connectRemote()
            return PTTTelnetCrawlerLibraryErrorCode.ConnectionResetError, result
        
        ReceiveTimes = 0
        self.__Timeouted = False
        self.__ReceiveData = ''
        self.__telnet.read_very_eager()
        
        StartTime = time.time()
        
        if self.__CurrentTimeout == 0:
            self.__Timeout = self.__DefaultTimeout
        else:
            self.__Timeout = self.__CurrentTimeout
        
        while True:
            time.sleep(self.__SleepTime)
            ReceiveTimes += 1
            
            try:
                self.__ReceiveData += self.__telnet.read_very_eager().decode('big5', 'ignore')
            except EOFError:
                PTTTelnetCrawlerLibraryUtil.Log('Remote kick connection...')
                self.__connectRemote()
                self.__Timeout = self.__DefaultTimeout
                return PTTTelnetCrawlerLibraryErrorCode.EOFError, result
            
            if len(ExpectTarget) != 0:
                self.removeColor()
            
            DataMacthed = False
            
            for i in range(len(ExpectTarget)):
                #print(ExpectTarget[i])
                if ExpectTarget[i] in self.__ReceiveData:
                    result = i
                    DataMacthed = True
                    break
            
            if DataMacthed:
                ErrorCode = PTTTelnetCrawlerLibraryErrorCode.Success
                break
            
            NowTime = time.time()
            
            if NowTime - StartTime > self.__Timeout:
                self.__Timeouted = True
                #print(str(len(self.__ReceiveData)))
                #print('ReadScreen timeouted')
                ErrorCode = PTTTelnetCrawlerLibraryErrorCode.WaitTimeout
                break
        
        self.__SleepTime = self.__SleepTime * (ReceiveTimes / 5.0)
        self.__Timeout = self.__DefaultTimeout
        return ErrorCode, result
    def __showScreen(self, ExpectTarget=[]):
        self.__readScreen('', ExpectTarget)
        print(self.__ReceiveData)
    def __sendData(self, Message, CaseList=[''], Enter=True, Refresh=False):
        
        if Message == None:
            Message = ''
        if CaseList == None:
            CaseList = ['']
        
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
            #self.__telnet.read_very_eager()
            #self.__telnet.read_until(b'')
            SendMessage = str(Message) + PostFix
            self.__telnet.read_very_eager()
            self.__telnet.write(SendMessage.encode('big5'))
            ReturnIndex = self.__telnet.expect(CaseList, timeout=self.__Timeout)[0]
            
        except EOFError:
            #QQ why kick me
            PTTTelnetCrawlerLibraryUtil.Log('Remote kick connection...')
            self.__connectRemote()
            self.__Timeout = self.__DefaultTimeout
            return PTTTelnetCrawlerLibraryErrorCode.EOFError, -1
        except ConnectionResetError:
            PTTTelnetCrawlerLibraryUtil.Log('Remote reset connection...')
            self.__connectRemote()
            self.__Timeout = self.__DefaultTimeout
            return PTTTelnetCrawlerLibraryErrorCode.ConnectionResetError, -1
        
        if ReturnIndex == -1:
            print('SendData timeouted')
            self.__Timeout = self.__DefaultTimeout
            return PTTTelnetCrawlerLibraryErrorCode.WaitTimeout, ReturnIndex
        self.__Timeout = self.__DefaultTimeout
        return PTTTelnetCrawlerLibraryErrorCode.Success, ReturnIndex
    def __connectRemote(self):
        self.__isConnected = False
        
        while True:
            self.__telnet = telnetlib.Telnet(self.__host)
            ErrorCode, Index = self.__sendData('', ['請輸入代號', '系統過載'], False)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                return ErrorCode
            if Index == 0:
                self.Log('Connect success')
                break
            if Index == 1:
                self.Log('System overload')
                time.sleep(2)
            
        CaseList = ['密碼不對', '您想刪除其他重複登入', '按任意鍵繼續', '您要刪除以上錯誤嘗試', '您有一篇文章尚未完成', '請輸入您的密碼', '編特別名單', '正在更新']
        SendMessage = self.__ID
        Enter = True
        
        while True:
            ErrorCode, Index = self.__sendData(SendMessage, CaseList, Enter)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                return ErrorCode
            if Index == 0:
                self.Log('Wrong password')
                return PTTTelnetCrawlerLibraryErrorCode.WrongPassword
            if Index == 1:
                if self.__kickOtherLogin:
                    SendMessage = 'y'
                    Enter = True
                    self.Log('Detect other login')
                    self.Log('Kick other login success')
                else :
                    SendMessage = 'n'
                    Enter = True
                    self.Log('Detect other login')
            if Index == 2:
                SendMessage = 'q'
                Enter = False
                self.Log('Press any key to continue')
            if Index == 3:
                SendMessage = 'Y'
                Enter = True
                self.Log('Delete error password log')
            if Index == 4:
                SendMessage = 'q'
                Enter = True
                self.Log('Delete the post not finished')    
            if Index == 5:
                SendMessage = self.__Password
                Enter = True
                self.Log('Input ID success')
            if Index == 6:
                self.Log('Login success')
                break
            if Index == 7:
                SendMessage = ''
                Enter = True
                self.Log('Wait update')
                time.sleep(1)
                
        self.__isConnected = True
        return PTTTelnetCrawlerLibraryErrorCode.Success
    def __gotoTop(self):
        self.__CurrentTimeout = 3
        
        ErrorCode, Index = self.__sendData('\x1b[D\x1b[D\x1b[D\x1b[D\x1b[Dq', ['[呼叫器]', '編特別名單', '娛樂與休閒', '系統資訊區', '主功能表'], False, True)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.__CurrentTimeout = 0
            self.__showScreen()
            return ErrorCode
        self.__CurrentTimeout = 0
        return PTTTelnetCrawlerLibraryErrorCode.Success
    def logout(self):
        ErrorCode = self.__gotoTop()
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            print('Error code 1: ' + str(ErrorCode))
            return ErrorCode
        ErrorCode, Index = self.__sendData('g\r\ny', ['此次停留時間'])
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            #self.__showScreen()
            print('Error code 2: ' + str(ErrorCode))
            return ErrorCode
        
        self.__telnet.close()
        PTTTelnetCrawlerLibraryUtil.Log('Logout success')
        
        return PTTTelnetCrawlerLibraryErrorCode.Success
    def __gotoBoard(self, Board):
        for i in range(5):
            ErrorCode = self.___gotoBoard(Board)
            if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.Success:
                break
                
        return ErrorCode
    def ___gotoBoard(self, Board):
        ErrorCode = self.__gotoTop()
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            print('Error code __gotoBoard 1: ' + str(ErrorCode))
            return ErrorCode
        CaseList = ['請輸入看板名稱']
        SendMessage = 's'
        
        self.__CurrentTimeout = 5
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, False)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            print('Error code __gotoBoard 2: ' + str(ErrorCode))
            return ErrorCode
        
        #self.__showScreen()
        CaseList = ['請按任意鍵繼續', '其他任意鍵停止', '動畫播放中', '看板《' + Board + '》']
        SendMessage = Board
        Enter = True
        while True:            
            ErrorCode, Index = self.__sendData(SendMessage, CaseList, Enter)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.__showScreen()
                print('Error code __gotoBoard 3: ' + str(ErrorCode))
                return ErrorCode
            if Index == 0 or Index == 1:
                SendMessage = ''
                Enter = True
                #self.Log('Press any key to continue')
            if Index == 2:
                SendMessage = 'q'
                Enter = False
                #self.Log('動畫播放中')
            if Index == 3:
                #self.Log('Into ' + Board)
                break
                
        return PTTTelnetCrawlerLibraryErrorCode.Success
    
    def post(self, board, title, content, PostType, SignType):
    
        self.__CurrentTimeout = 10
        
        ErrorCode = self.__gotoBoard(board)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('post 1 Go to ' + board + ' fail')
            return ErrorCode
        
        CaseList = ['1-8或不選', '使用者不可發言']
        SendMessage = '\x10'
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, False)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('post 2 error code: ' + str(ErrorCode))
            return ErrorCode
        
        if Index == 1:
            self.Log('You are in the bucket QQ')
            return PTTTelnetCrawlerLibraryErrorCode.NoPermission
        
        CaseList = ['標題']
        SendMessage = str(PostType)
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('post 3 error code: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['編輯文章']
        SendMessage = title
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            
            self.Log('post 4 error code: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['確定要儲存檔案嗎']
        SendMessage = content + '\x18'
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, False)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('post 5 error code: ' + str(ErrorCode))
            return ErrorCode
        
        self.__CurrentTimeout = 10
        
        CaseList = ['x=隨機', '請按任意鍵繼續', '看板《' + board + '》']
        SendMessage = 's'
        Enter = True
        Refresh = False
        while True:        
            ErrorCode, Index = self.__sendData(SendMessage, CaseList, Enter, Refresh)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.__showScreen()
                self.Log('post 6 error code: ' + str(ErrorCode))
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
                #self.Log('Post success')
                break
                
        self.__CurrentTimeout = 0
        return PTTTelnetCrawlerLibraryErrorCode.Success
    
    def getNewestPostIndex(self, Board):
        
        TryTime = 0
        
        for i in range(10):
            ErrorCode, Index = self.__getNewestPostIndex(Board)
            TryTime += 1
            if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.Success:
                break
            elif ErrorCode == PTTTelnetCrawlerLibraryErrorCode.ParseError:
                #self.Log('getNewestPostIndex parse error retry..')
                pass
            elif ErrorCode == PTTTelnetCrawlerLibraryErrorCode.WaitTimeout:
                #self.Log('getNewestPostIndex time out retry..')
                pass
            else:
                self.Log('ErrorCode: ' + str(ErrorCode))
                return ErrorCode, Index
            #time.sleep(0.1)
        
        #self.Log('TryTime: ' + str(TryTime))
        return ErrorCode, Index
    def __getNewestPostIndex(self, Board):
        ReturnIndex = -1
    
        ErrorCode = self.__gotoBoard(Board)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('getNewestPostIndex 1 Go to ' + Board + ' fail')
            return ErrorCode, -1
        
        self.__readScreen('0\r\n$', ['★'])
        if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.WaitTimeout:
            #self.Log('getNewestPostIndex 2.1 error code: ' + str(ErrorCode))
            print(self.__ReceiveData)
            return ErrorCode, -1

        AllIndex = re.findall(r'\d+ ', self.__ReceiveData)
        
        AllIndex = list(set(map(int, AllIndex)))
        AllIndex.sort()
        
        if len(AllIndex) == 0:
            return PTTTelnetCrawlerLibraryErrorCode.ParseError, -1
        
        AllIndexTemp = list(AllIndex)
        while True:
            
            ReturnIndexTemp = AllIndex.pop()
            
            if len(str(ReturnIndexTemp)) <= 6:
                
                TargetA = '{0: >6}'.format(str(ReturnIndexTemp))
                TargetACount = 0
                
                #計算畫面中 所有數字的同質性，文章編號最長六碼，前三碼會相同，避免一樣是六碼但卻不是文章編號的數字混進來
                for TargetBTemp in AllIndexTemp:
                    TargetB = '{0: >6}'.format(str(TargetBTemp))
                    if TargetA[:3] == TargetB[:3] and len(str(ReturnIndexTemp)) == len(str(TargetBTemp)):
                        TargetACount += 1
                    
                if 10 <= TargetACount and TargetACount <= 20 and (ReturnIndexTemp + 1 in AllIndexTemp or ReturnIndexTemp - 1 in AllIndexTemp):
                    
                    #檢驗是否刪除的邏輯，移動至取得文章資訊時檢查
                    
                    '''
                    #通過同質性測試後，檢驗文章是否已經被刪除
                    CurrentData = self.__ReceiveData[:]
                    
                    while CurrentData.find(str(ReturnIndexTemp)) != -1:
                        CurrentData = CurrentData[CurrentData.find(str(ReturnIndexTemp)) + len(str(ReturnIndexTemp)):]
                    
                    while CurrentData.find('★') != -1:
                        CurrentData = CurrentData[:CurrentData.find('★')]
                    
                    if CurrentData.find('(') != -1 and CurrentData.find('-') < CurrentData.find('('):
                        continue
                    else:
                        ReturnIndex = ReturnIndexTemp
                        break
                    '''    
                    
                    ReturnIndex = ReturnIndexTemp
                    break
                    
                else:
                    pass
                    '''
                    print(str(20 - StartCount - 1))
                    print(str(TargetACount))
                    print(TargetA)
                    print(TargetA[:3])
                    '''
            if len(AllIndex) == 0:
                #print(self.__ReceiveData)
                #print(AllIndexTemp)
                #self.Log('Parse error!!!')
                return PTTTelnetCrawlerLibraryErrorCode.ParseError, -1
        return PTTTelnetCrawlerLibraryErrorCode.Success, int(ReturnIndex)
    
    def __gotoPostByIndex(self, Board, PostIndex):
    
        ErrorCode = self.__gotoBoard(Board)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('__gotoPostByIndex 1 Go to ' + Board + ' fail')
            self.__showScreen()
            return ErrorCode

        IndexTarget = '>{0: >6}'.format(str(PostIndex))
        
        self.__CurrentTimeout = 5
        
        self.__readScreen(str(PostIndex) + '\r\n', [IndexTarget])
        
        if IndexTarget in self.__ReceiveData:
            return PTTTelnetCrawlerLibraryErrorCode.Success
        else:
            print(self.__ReceiveData)
            return PTTTelnetCrawlerLibraryErrorCode.PostNotFound
    def __gotoPostByID(self, Board, PostID):
        ErrorCode = self.__gotoBoard(Board)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('__gotoPostByID 1 Go to ' + Board + ' fail')
            return ErrorCode
        
        self.__readScreen('#' + PostID + '\r\n', '文章選讀')
        
        if '找不到這個文章代碼' in self.__ReceiveData:
            return PTTTelnetCrawlerLibraryErrorCode.PostNotFound
        
        return PTTTelnetCrawlerLibraryErrorCode.Success
        
    def getPostInfoByID(self, Board, PostID, Index=-1):
        for i in range(5):
            ErrorCode = self.__getPostInfoByID(Board, PostID, Index)
            if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.Success:
                break
            if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.WebFormatError:
                break
        return ErrorCode
    def __getPostInfoByID(self, Board, PostID, Index=-1):
        
        if Index != -1:
            ErrorCode = self.__gotoPostByIndex(Board, Index)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.Log('getPostInfoByIndex 1 goto post fail')
                return ErrorCode, None
        else:
        
            if len(PostID) != 8:
                self.Log('Error input: ' + PostID)
                return PTTTelnetCrawlerLibraryErrorCode.ErrorInput, None
        
            ErrorCode = self.__gotoPostByID(Board, PostID)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.Log('getPostInfoByID 1 goto post fail')
                return ErrorCode, None
        
        ErrorCode, Index = self.__readScreen('Q', ['請按任意鍵繼續'])
        if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.WaitTimeout:
            
            return PTTTelnetCrawlerLibraryErrorCode.PostDeleted, None
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('getPostInfoByID 3 read screen time out')
            return ErrorCode, None
        
        if Index == 0:
            #Get query screen success
            pass
        if Index == 1:
            print(self.__ReceiveData)
            print('Post has beeb deleted')
            return PTTTelnetCrawlerLibraryErrorCode.PostDeleted, None
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
                return PTTTelnetCrawlerLibraryErrorCode.ParseError, None
        
        if 'https' in self.__ReceiveData:
            RealWebUrl = self.__ReceiveData[self.__ReceiveData.find('https'):self.__ReceiveData.find('.html') + 5]
        else:
            self.Log('Find weburl fail')
            return PTTTelnetCrawlerLibraryErrorCode.ParseError, None
        
        if '這一篇文章值' in self.__ReceiveData:
            RealMoneyTemp = self.__ReceiveData[self.__ReceiveData.find('這一篇文章值') + len('這一篇文章值') : self.__ReceiveData.find('Ptt幣')]
            RealMoney = int(re.search(r'\d+', RealMoneyTemp).group())
        else:
            self.Log('Find post money fail')
            return PTTTelnetCrawlerLibraryErrorCode.ParseError, None
        '''
        print('RealWebUrl ' + RealWebUrl)
        print('RealPostID ' + RealPostID)
        print('RealMoney ' + str(RealMoney))
        '''
        
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        res = requests.get(
            url = RealWebUrl,
            cookies={'over18': '1'}
        )
        
        soup =  BeautifulSoup(res.text,'html.parser')
        main_content = soup.find(id='main-content')
        
        metas = main_content.select('div.article-metaline')
        filtered = [ v for v in main_content.stripped_strings if v[0] not in ['※', '◆'] and  v[:2] not in ['--'] ]
        
        content = ' '.join(filtered)
        content = re.sub(r'(\s)+', '', content )
        if len(metas) == 0:
            self.Log('div.article-metaline is not exist')
            return PTTTelnetCrawlerLibraryErrorCode.WebFormatError, None
            
        author = metas[0].select('span.article-meta-value')[0].string
        title = metas[1].select('span.article-meta-value')[0].string
        date = metas[2].select('span.article-meta-value')[0].string
        
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
                    RealPushList.append(PushInformation(PushType, PushID, PushContent, PushDate))
            if date == ContentLine:
                PostContentArea = True
                continue
            if RealWebUrl in ContentLine or '推' in ContentLine or '噓' in ContentLine or '→' in ContentLine:
                PostContentArea = False
            if PostContentArea:
                RealPostContent += ContentLine + '\r\n'
        
        '''
        print('RealPostTitle ' + RealPostTitle)
        print('RealPostAuthor ' + RealPostAuthor)
        print('RealPostDate ' + RealPostDate)
        print('RealPostContent ' + RealPostContent)
        '''
        
        result = PostInformation(Board, RealPostID, RealPostAuthor, RealPostDate, RealPostTitle, RealWebUrl, RealMoney, RealPostContent, RealPushList, res.text)
        
        return PTTTelnetCrawlerLibraryErrorCode.Success, result

    def getPostInfoByIndex(self, Board, Index):
        
        ErrorCode, Post = self.getPostInfoByID(Board, '', Index)
        
        return ErrorCode, Post
    
    def getNewPostIndexList(self, Board, LastPostIndex):
        
        result = []
        ErrorCode, LastIndex = self.getNewestPostIndex(Board)

        if LastIndex == -1:
            return result
        
        if LastPostIndex <= 0 or LastIndex < LastPostIndex:
            result.append(LastIndex)
        else:
            for IndexTemp in range(LastPostIndex + 1, LastIndex + 1):
                result.append(IndexTemp)
        return ErrorCode, result
    
    def pushByID(self, Board, PushType, PushContent, PostID, PostIndex=-1):
        for i in range(5):
            ErrorCode = self.__pushByID(Board, PushType, PushContent, PostID, PostIndex)
            if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.Success:
                break
            if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.NoPermission:
                break
        return ErrorCode
    def __pushByID(self, Board, PushType, PushContent, PostID, PostIndex=-1):
        self.__CurrentTimeout = 3
    
        if PostIndex != -1:
            ErrorCode = self.__gotoPostByIndex(Board, PostIndex)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.Log('pushByIndex 1 goto post fail')
                return ErrorCode
        else:
        
            if len(PostID) != 8:
                self.Log('pushByID Error input: ' + PostID)
                return PTTTelnetCrawlerLibraryErrorCode.ErrorInput
        
            ErrorCode = self.__gotoPostByID(Board, PostID)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.Log('pushByID 1 goto post fail')
                return ErrorCode
        
        #CaseList = ['您覺得這篇文章', '加註方式', '禁止快速連續推文']
        
        Message = 'X'
        
        while True:
        
            ErrorCode, Index = self.__readScreen(Message, ['您覺得這篇文章', '加註方式', '禁止快速連續推文', '禁止短時間內大量推文', '使用者不可發言'])
            if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.WaitTimeout:
                print(self.__ReceiveData)
                self.Log('No push option')
                return PTTTelnetCrawlerLibraryErrorCode.NoPermission
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.Log('pushByID 2 error code: ' + str(ErrorCode))
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
                PTTTelnetCrawlerLibraryUtil.Log('No fast push, wait...')
                Message = 'qX'
                time.sleep(1)
            if Index == 3:
                PTTTelnetCrawlerLibraryUtil.Log('System abort many push, wait...')
                Message = 'qX'
                time.sleep(2)
            if Index == 4:
                PTTTelnetCrawlerLibraryUtil.Log('You are in the bucket QQ')
                return PTTTelnetCrawlerLibraryErrorCode.NoPermission
                
        if not AllowPushTypeList[self.PushType_Boo] and PushType == self.PushType_Boo:
            PushType = self.PushType_Arrow
        
        CaseList = ['']
        
        if ArrowOnly:
            SendMessage = PushContent + '\r\ny'
        else:
            SendMessage = str(PushType) + PushContent + '\r\ny'
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, True, True)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('pushByID 3 error code: ' + str(ErrorCode))
            return ErrorCode
        
        self.__CurrentTimeout = 0
        return PTTTelnetCrawlerLibraryErrorCode.Success
    def pushByIndex(self, Board, PushType, PushContent, PostIndex):
        ErrorCode = self.pushByID(Board, PushType, PushContent, '', PostIndex)
        return ErrorCode
    def mail(self, UserID, MailTitle, MailContent, SignType):
    
        self.__CurrentTimeout = 3
        
        ErrorCode = self.__gotoTop()
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            print('mail goto top error code 1: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['主題：', '請選擇簽名檔', '已順利寄出，是否自存底稿', '任意鍵繼續', '電子郵件']
        SendMessage = 'M\r\nS\r\n' + UserID
        Enter = True
        while True:        
            ErrorCode, Index = self.__sendData(SendMessage, CaseList, Enter)
            if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.WaitTimeout:
                self.__showScreen()
                self.Log('No such user: ' + UserID)
                return PTTTelnetCrawlerLibraryErrorCode.NoUser
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.Log('mail 2 error code: ' + str(ErrorCode))
                return ErrorCode
            if Index == 0:
                SendMessage = MailTitle + '\r\n' + MailContent + '\x18s'
                Enter = True
            if Index == 1:
                SendMessage = str(SignType)
                Enter = True
            if Index == 2:
                SendMessage = 'Y'
                Enter = True
            if Index == 3:
                SendMessage = 'q'
                Enter = False
            if Index == 4:
                break
        
        self.__CurrentTimeout = 0
        return PTTTelnetCrawlerLibraryErrorCode.Success
        
    def giveMoney(self, ID, Money, YourPassword):
        self.__CurrentTimeout = 3
        
        ErrorCode = self.__gotoTop()
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            print('giveMoney goto top error code 1: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['量販店', '給其他人Ptt幣', '這位幸運兒的id', '請輸入金額', '請輸入您的密碼', '要修改紅包袋嗎', '確定進行交易嗎', '按任意鍵繼續']
        SendMessage = 'P'
        Enter = True
        while True:        
            ErrorCode, Index = self.__sendData(SendMessage, CaseList, Enter)
            if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.WaitTimeout:
                self.__showScreen()
                self.Log('No such option: ' + SendMessage)
                return PTTTelnetCrawlerLibraryErrorCode.NoUser
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.Log('mail 2 error code: ' + str(ErrorCode))
                return ErrorCode
            if Index == 0:
                SendMessage = 'P'
                Enter = True
            if Index == 1:
                SendMessage = '0'
                Enter = True
            if Index == 2:
                SendMessage = ID
                Enter = True
            if Index == 3:
                SendMessage = '\t' + str(Money)
                Enter = True
            if Index == 4:
                SendMessage = str(YourPassword)
                Enter = True
            if Index == 5:
                SendMessage = 'n'
                Enter = True
            if Index == 6:
                SendMessage = 'y'
                Enter = True
            if Index == 7:
                break
        self.__CurrentTimeout = 0
        return PTTTelnetCrawlerLibraryErrorCode.Success
        
    def getTime(self):
        for i in range(5):
            ErrorCode, Time = self.__getTime()
            if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.Success:
                break
        return ErrorCode, Time
    def __getTime(self):
        self.__CurrentTimeout = 3
        
        #Thanks for ervery one in Python
        
        ErrorCode = self.__gotoTop()
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            print('getTime goto top error code 2: ' + str(ErrorCode))
            return ErrorCode, ''
            
        self.__CurrentTimeout = 1
        ErrorCode, Index = self.__readScreen('A\r\nqA\r\nq', ['呼叫器', '離開，再見…'])
        #ErrorCode, Index = self.__readScreen('', ['[呼叫器]', '離開，再見…'])
        if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.WaitTimeout:
            #self.__showScreen()
            #self.Log('getTime 2.1')
            return ErrorCode, ''
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('getTime 3 read screen error code: ' + str(ErrorCode))
            return ErrorCode, ''
        
        if not '離開，再見…' in self.__ReceiveData or not '[呼叫器]' in self.__ReceiveData:
            #self.Log('Not in user menu 1')
            return PTTTelnetCrawlerLibraryErrorCode.ParseError, ''
        
        result = self.__ReceiveData[self.__ReceiveData.find('離開，再見…') + len('離開，再見…'):self.__ReceiveData.find('[呼叫器]')]
        
        if not '星期' in result:
            #self.Log('Not in user menu 2')
            return PTTTelnetCrawlerLibraryErrorCode.ParseError, ''
        
        result = result[result.find('星期') + len('星期'):]
        result = result[result.find(' ') + 1:result.find(']')]
        
        self.__CurrentTimeout = 0
        
        return PTTTelnetCrawlerLibraryErrorCode.Success, result
if __name__ == '__main__':

    print('PTT Telnet Crawler Library v 0.2.170612 beta')
    print('PTT CodingMan')
