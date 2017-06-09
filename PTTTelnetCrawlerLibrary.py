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
    
    def __readScreen(self, ExpectTarget=None):
        
        try:
            self.__telnet.write(b'\x0C')
        except ConnectionResetError:
            PTTTelnetCrawlerLibraryUtil.Log('Remote reset connection...')
            self.__connectRemote()
            return PTTTelnetCrawlerLibraryErrorCode.ConnectionResetError
        
        ReceiveTimes = 0
        self.__ReceiveData = ''
        while True:
            time.sleep(self.__SleepTime)
            ReceiveTimes += 1
            
            try:
                self.__ReceiveData += self.__telnet.read_very_eager().decode('big5', 'ignore')
            except EOFError:
                PTTTelnetCrawlerLibraryUtil.Log('Remote kick connection...')
                self.__connectRemote()
                return PTTTelnetCrawlerLibraryErrorCode.EOFError
            
            self.removeColor()
            
            if ExpectTarget != '' and ExpectTarget != None:
                if ExpectTarget in self.__ReceiveData:
                    break
            
            if ExpectTarget == None and ReceiveTimes > 10:
                return PTTTelnetCrawlerLibraryErrorCode.WaitTimeout
            if self.__SleepTime * ReceiveTimes > self.__Timeout:
                
                return PTTTelnetCrawlerLibraryErrorCode.WaitTimeout
        
        self.__SleepTime = self.__SleepTime * (ReceiveTimes / 3.0)
        #print('self.__SleepTime: ' + str(self.__SleepTime))
        return PTTTelnetCrawlerLibraryErrorCode.Success
    def __showScreen(self, ExpectTarget=None):
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
            self.__Timeout = 3
        else:
            self.__Timeout = 10
        
        try:
            #self.__telnet.read_very_eager()
            #self.__telnet.read_until(b'')
            SendMessage = str(Message) + PostFix
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
            print('Error code gotoBoard 1: ' + str(ErrorCode))
            return ErrorCode
        
        #self.__showScreen()
        CaseList = ['請按任意鍵繼續', '其他任意鍵停止', '動畫播放中', '看板《' + Board + '》']
        SendMessage = Board
        Enter = True
        while True:            
            ErrorCode, Index = self.__sendData(SendMessage, CaseList, Enter)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.__showScreen()
                print('Error code gotoBoard 2: ' + str(ErrorCode))
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
        
        ReturnIndex = -1
    
        ErrorCode = self.gotoBoard(Board)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('getNewestPostIndex 1 Go to ' + Board + ' fail')
            return ErrorCode, -1
        
        CaseList = ['文章選讀']
        SendMessage = '0\r$'
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, False, True)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('getNewestPostIndex 3 error code: ' + str(ErrorCode))
            return ErrorCode, -1
        
        self.__readScreen('文章選讀')
        
        AllIndex = re.findall(r'\d+ ', self.__ReceiveData)
        
        ScreenCount = self.__ReceiveData.count('看板《' + Board + '》')
        StartCount = int(self.__ReceiveData.count('★') / ScreenCount)

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
                #print(AllIndexTemp)
                #self.Log('Parse error!!!')
                return PTTTelnetCrawlerLibraryErrorCode.UnknowError, -1
        return PTTTelnetCrawlerLibraryErrorCode.Success, int(ReturnIndex)
    
    def gotoPostByIndex(self, Board, PostIndex):
        ErrorCode = self.gotoBoard(Board)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('gotoPostByIndex 1 Go to ' + Board + ' fail')
            return ErrorCode
        
        CaseList = ['文章選讀']
        SendMessage = '0'
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, True, True)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('gotoPostByIndex 2 error code: ' + str(ErrorCode))
            return ErrorCode
        
        IndexTarget = '>{0: >6}'.format(str(PostIndex))
        
        CaseList = [IndexTarget, '★']
        SendMessage = str(PostIndex)
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, True, True)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('gotoPostByIndex 3 error code: ' + str(ErrorCode))
            return ErrorCode
        
        if Index == 0:
            #print('0')
            return PTTTelnetCrawlerLibraryErrorCode.Success
        if Index == 1:
            #print('1')
            return PTTTelnetCrawlerLibraryErrorCode.PostNotFound
    def gotoPostByID(self, Board, PostID):
        ErrorCode = self.gotoBoard(Board)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('gotoPostByID 1 Go to ' + Board + ' fail')
            return ErrorCode
        
        CaseList = ['進板畫面', '請按任意鍵繼續']
        SendMessage = '#' + PostID
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, True, True)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('gotoPostByIndex 2 error code: ' + str(ErrorCode))
            return ErrorCode
        if Index == 0:
            return PTTTelnetCrawlerLibraryErrorCode.Success
        if Index == 1:
            return PTTTelnetCrawlerLibraryErrorCode.PostNotFound
            
    def getPostInfoByID(self, Board, PostID, Index=-1):
        
        if Index != -1:
            ErrorCode = self.gotoPostByIndex(Board, Index)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.Log('gotoPostByIndex 1 goto post fail')
                return ErrorCode, None
        else:
            ErrorCode = self.gotoPostByID(Board, PostID)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                self.Log('gotoPostByID 1 goto post fail')
                return ErrorCode, None
        
        print('Works success')
        
        CaseList = ['請按任意鍵繼續', '文章選讀']
        SendMessage = 'Q'
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, False, True)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            self.Log('gotoPostByID 2 error code: ' + str(ErrorCode))
            return ErrorCode
        
        self.__readScreen()
        
        
        RealPostID = ''
        RealWebUrl = ''
        
        if 'https' in self.__ReceiveData:
            RealWebUrl = self.__ReceiveData[self.__ReceiveData.find('https'):self.__ReceiveData.find('.html') + 5]
        else:
            self.Log('Find weburl fail')
                
        if Index == -1:
            RealPostID = PostID
            
        else:
            if '#' in self.__ReceiveData:
                RealPostID = self.__ReceiveData[self.__ReceiveData.find('#') + 1:]
                RealPostID = RealPostID[:RealPostID.find(' ')]
            else:
                self.Log('Find PostID fail')
                
        print('RealWebUrl ' + RealWebUrl)
        print('RealPostID ' + RealPostID)
        result = None
        
        return PTTTelnetCrawlerLibraryErrorCode.Success, result

    def getPostInfoByIndex(self, Board, Index):
        
        ErrorCode, Post = self.getPostInfoByID(Board, '', Index)
        
        return ErrorCode, Post
if __name__ == '__main__':

    print('PTT Telnet Crawler Library v 0.2.170609')
    print('PTT CodingMan')
