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
            
            if self.__SleepTime * ReceiveTimes > self.__Timeout:
                print(self.__ReceiveData)
                return PTTTelnetCrawlerLibraryErrorCode.WaitTimeout
        
        self.__SleepTime = self.__SleepTime * (ReceiveTimes / 5.0)
        #print('self.__SleepTime: ' + str(self.__SleepTime))
        return PTTTelnetCrawlerLibraryErrorCode.Success
    def __showScreen(self):
        result = self.__readScreen()
        print(result)
    def __sendData(self, Message, CaseList=[], Enter=True):
        
        if Message == None:
            Message = ''
        if CaseList == None:
            CaseList = []
        
        self.__ReceiveData = ''
        
        ReceiveTimes = 0
        
        for i in range(len(CaseList)):
            if type(CaseList[i]) is str:
                CaseList[i] = CaseList[i].encode('big5')
        
        if self.__isConnected:
            self.__Timeout = 1
        else:
            self.__Timeout = 10
        
        try:
            if Enter:
                self.__telnet.write(str(Message + '\r\n').encode('big5'))
            else:
                self.__telnet.write(str(Message).encode('big5'))
                
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
            
        CaseList = ['密碼不對', '您想刪除其他重複登入', '按任意鍵繼續', '您要刪除以上錯誤嘗試', '您有一篇文章尚未完成', '請輸入您的密碼:', '編特別名單', '正在更新']
        SendMessage = self.__ID
        
        while True:
            ErrorCode, Index = self.__sendData(SendMessage, CaseList)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                return ErrorCode
            if Index == -1:
                SendMessage = ''
                self.Log('Wait..')
                self.__showScreen()
            if Index == 0:
                self.Log('Wrong password')
                return PTTTelnetCrawlerLibraryErrorCode.WrongPassword
            if Index == 1:
                if self.__kickOtherLogin:
                    SendMessage = 'y'
                    self.Log('Detect other login')
                    self.Log('Kick other login success')
                else :
                    SendMessage = 'n'
                    self.Log('Detect other login')
            if Index == 2:
                SendMessage = ''
                self.Log('Press any key continue')
            if Index == 3:
                SendMessage = 'y'
                self.Log('Delete error password log')
            if Index == 4:
                SendMessage = 'q'
                self.Log('Delete the post not finished')    
            if Index == 5:
                SendMessage = self.__Password
                self.Log('Input ID success')
            if Index == 6:
                self.Log('Login success')
                break
            if Index == 7:
                SendMessage = ''
                self.Log('Wait update')
                
        self.__isConnected = True
        return PTTTelnetCrawlerLibraryErrorCode.Success
    def gotoTop(self):
        ErrorCode, Index = self.__sendData('\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D\x1b[D', [], False)
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            return ErrorCode
        
        return PTTTelnetCrawlerLibraryErrorCode.Success
    def logout(self):
        ErrorCode = self.gotoTop()
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            print('Error code 1: ' + str(ErrorCode))
            return ErrorCode
        ErrorCode, Index = self.__sendData('g', ['您確定要離開【 批踢踢實業坊 】嗎(Y/N)？[N]'])
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            print('Error code 2: ' + str(ErrorCode))
            return ErrorCode
        ErrorCode, Index = self.__sendData('y')
        if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
            print('Error code 3: ' + str(ErrorCode))
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
        if Index == -1:
            self.Log('Input board error')
            self.__showScreen()
            return PTTTelnetCrawlerLibraryErrorCode.ErrorInput
        
        SendMessage = Board
        ErrorCode, Index = self.__sendData(SendMessage)
            
if __name__ == '__main__':

    print('PTT Telnet Crawler Library v 0.2.170608')
    print('PTT CodingMan')
