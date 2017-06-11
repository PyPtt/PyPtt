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
        self.__Timeout =             5
        
        self.__connectRemote()
    def Log(self, Message):
        PTTTelnetCrawlerLibraryUtil.Log(Message)
    def isLoginSuccess(self):
        return self.__isConnected
    def removeColor(self):
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
    
    def __readScreen(self, ExpectTarget=[]):
        
        result = -1
        ErrorCode = PTTTelnetCrawlerLibraryErrorCode.UnknowError
        try:
            self.__telnet.write(b'\x0C')
        except ConnectionResetError:
            PTTTelnetCrawlerLibraryUtil.Log('Remote reset connection...')
            self.__connectRemote()
            return PTTTelnetCrawlerLibraryErrorCode.ConnectionResetError, result
        
        ReceiveTimes = 0
        self.__Timeouted = False
        self.__ReceiveData = ''
        self.__telnet.read_very_eager()
        
        StartTime = time.time()
        
        while True:
            time.sleep(self.__SleepTime)
            ReceiveTimes += 1
            
            try:
                self.__ReceiveData += self.__telnet.read_very_eager().decode('big5', 'ignore')
            except EOFError:
                PTTTelnetCrawlerLibraryUtil.Log('Remote kick connection...')
                self.__connectRemote()
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
                print('ReadScreen timeouted')
                ErrorCode = PTTTelnetCrawlerLibraryErrorCode.WaitTimeout
                break
        
        self.__SleepTime = self.__SleepTime * (ReceiveTimes / 5.0)
        return ErrorCode, result
    def __showScreen(self, ExpectTarget=[]):
        self.__readScreen(ExpectTarget)
        print(self.__ReceiveData)
    def __sendData(self, Message, CaseList=[], Enter=True, Refresh=False):
        
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
            self.__Timeout = 1
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
            return PTTTelnetCrawlerLibraryErrorCode.EOFError, -1
        except ConnectionResetError:
            PTTTelnetCrawlerLibraryUtil.Log('Remote reset connection...')
            self.__connectRemote()
            return PTTTelnetCrawlerLibraryErrorCode.ConnectionResetError, -1
        
        if ReturnIndex == -1:
            print('SendData timeouted')
            return PTTTelnetCrawlerLibraryErrorCode.WaitTimeout, ReturnIndex
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
    def gotoTop(self):
        ErrorCode, Index = self.__sendData('\x1b[D\x1b[D\x1b[D\x1b[D', ['[呼叫器]'], False, True)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            return ErrorCode
        
        return PTTTelnetCrawlerLibraryErrorCode.Success
    def logout(self):
        ErrorCode = self.gotoTop()
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            print('Error code 1: ' + str(ErrorCode))
            return ErrorCode
        ErrorCode, Index = self.__sendData('g\r\ny', ['此次停留時間'])
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.__showScreen()
            print('Error code 2: ' + str(ErrorCode))
            return ErrorCode
        
        self.__telnet.close()
        PTTTelnetCrawlerLibraryUtil.Log('Logout success')
        
        return PTTTelnetCrawlerLibraryErrorCode.Success
    def gotoBoard(self, Board):
        ErrorCode = self.gotoTop()
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            print('Error code gotoBoard 1: ' + str(ErrorCode))
            return ErrorCode
        CaseList = ['請輸入看板名稱']
        SendMessage = 's'
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, False)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            print('Error code gotoBoard 2: ' + str(ErrorCode))
            return ErrorCode
        
        #self.__showScreen()
        CaseList = ['請按任意鍵繼續', '其他任意鍵停止', '動畫播放中', '看板《' + Board + '》']
        SendMessage = Board
        Enter = True
        while True:            
            ErrorCode, Index = self.__sendData(SendMessage, CaseList, Enter)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.__showScreen()
                print('Error code gotoBoard 3: ' + str(ErrorCode))
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
        ErrorCode = self.gotoBoard(board)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('post 1 Go to ' + board + ' fail')
            return ErrorCode
        
        CaseList = ['1-8或不選']
        SendMessage = '\x10'
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, False)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('post 2 error code: ' + str(ErrorCode))
            return ErrorCode
        
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
        
        CaseList = ['請選擇簽名檔', '請按任意鍵繼續', '看板《' + board + '》']
        SendMessage = 's'
        
        while True:        
            ErrorCode, Index = self.__sendData(SendMessage, CaseList)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.Log('post 5 error code: ' + str(ErrorCode))
                return ErrorCode
            if Index == 0:
                SendMessage = str(SignType)
            if Index == 1:
                SendMessage = ''
            if Index == 2:
                #self.Log('Post success')
                break
        return PTTTelnetCrawlerLibraryErrorCode.Success
    
    def getNewestPostIndex(self, Board):
        
        for i in range(3):
            ErrorCode, Index = self.__getNewestPostIndex(Board)
            
            if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.Success:
                break
            if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.ParseError:
                pass
            else:
                return ErrorCode, Index
        return ErrorCode, Index
    def __getNewestPostIndex(self, Board):
        ReturnIndex = -1
    
        ErrorCode = self.gotoBoard(Board)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('getNewestPostIndex 1 Go to ' + Board + ' fail')
            return ErrorCode, -1
        
        CaseList = ['']
        SendMessage = '0\r\n$'
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, False, True)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('getNewestPostIndex 2 error code: ' + str(ErrorCode))
            return ErrorCode, -1
        
        self.__readScreen(['文章選讀'])
        #print(self.__ReceiveData)
        AllIndex = re.findall(r'\d+ ', self.__ReceiveData)
        
        AllIndex = list(set(map(int, AllIndex)))
        AllIndex.sort()
        
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
                    
                if 10 <= TargetACount and TargetACount <= 20:
                    
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
                print(AllIndexTemp)
                #self.Log('Parse error!!!')
                return PTTTelnetCrawlerLibraryErrorCode.ParseError, -1
        return PTTTelnetCrawlerLibraryErrorCode.Success, int(ReturnIndex)
    
    def gotoPostByIndex(self, Board, PostIndex):
        ErrorCode = self.gotoBoard(Board)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('gotoPostByIndex 1 Go to ' + Board + ' fail')
            self.__showScreen()
            return ErrorCode
        
        IndexTarget = '>{0: >6}'.format(str(PostIndex))
        
        CaseList = ['']
        SendMessage = str(PostIndex)
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, True, True)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('gotoPostByIndex 3 error code: ' + str(ErrorCode))
            return ErrorCode
        
        self.__readScreen(['板主'])
        
        if IndexTarget in self.__ReceiveData:
            return PTTTelnetCrawlerLibraryErrorCode.Success
        else:
            print(self.__ReceiveData)
            return PTTTelnetCrawlerLibraryErrorCode.PostNotFound
    def gotoPostByID(self, Board, PostID):
        ErrorCode = self.gotoBoard(Board)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('gotoPostByID 1 Go to ' + Board + ' fail')
            return ErrorCode
        
        CaseList = ['']
        SendMessage = '#' + PostID
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, True, True)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('gotoPostByIndex 2 error code: ' + str(ErrorCode))
            return ErrorCode
        
        self.__readScreen('文章選讀')
        
        if '找不到這個文章代碼' in self.__ReceiveData:
            return PTTTelnetCrawlerLibraryErrorCode.PostNotFound
        
        return PTTTelnetCrawlerLibraryErrorCode.Success
        
    def getPostInfoByID(self, Board, PostID, Index=-1):
        
        if Index != -1:
            ErrorCode = self.gotoPostByIndex(Board, Index)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.Log('getPostInfoByIndex 1 goto post fail')
                return ErrorCode, None
        else:
        
            if len(PostID) != 8:
                self.Log('Error input: ' + PostID)
                return PTTTelnetCrawlerLibraryErrorCode.ErrorInput, None
        
            ErrorCode = self.gotoPostByID(Board, PostID)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.Log('getPostInfoByID 1 goto post fail')
                return ErrorCode, None
        
        CaseList = ['請按任意鍵繼續']
        SendMessage = 'Q'
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, False, True)
        if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.WaitTimeout:
            return PTTTelnetCrawlerLibraryErrorCode.PostDeleted, None
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('getPostInfoByID 2 error code: ' + str(ErrorCode))
            return ErrorCode, None
        
        ErrorCode, Index = self.__readScreen(['請按任意鍵繼續'])
        if ErrorCode == PTTTelnetCrawlerLibraryErrorCode.WaitTimeout:
            if Index == -1:
                self.__showScreen()
                print('getPostInfoByID 2.1')
            return ErrorCode, None
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
if __name__ == '__main__':

    print('PTT Telnet Crawler Library v 0.2.170609')
    print('PTT CodingMan')
