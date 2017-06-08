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
        
        self.__SleepTime =         0.1
        self.__Timeout =             2
        
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

    def __sendData(self, Message, CaseList, Enter=True, ExtraWait=0):
        
        try:
            if Message != '':
                if Enter:
                    self.__telnet.write(str(Message + '\r\n').encode('big5'))
                else:
                    self.__telnet.write(str(Message).encode('big5'))
        except ConnectionResetError:
            PTTTelnetCrawlerLibraryUtil.Log('Remote reset connection...')
            return PTTTelnetCrawlerLibraryErrorCode.ConnectionResetError, -1
        if ExtraWait > 0:
            time.sleep(ExtraWait)
        
        self.__ReceiveData = ''
        
        ReceiveTimes = 0
        
        for i in range(len(CaseList)):
            CaseList[i] = CaseList[i].encode('big5')
        
        ReturnIndex = self.__telnet.expect(CaseList, self.__Timeout)[0]
        
        '''while True:
            time.sleep(self.__SleepTime)
            try:
                self.__ReceiveData += self.__telnet.read_very_eager().decode('big5', 'ignore')
            except EOFError:
                return PTTTelnetCrawlerLibraryErrorCode.EOFError
                
            self.removeColor()
            
            if ReadUtil != '':
                if ReadUtil in self.__ReceiveData:
                    break
            
            ReceiveTimes += 1
            
            if self.__SleepTime * ReceiveTimes > self.__SleepTimeout:
                print(ReceiveTimes)
                return PTTTelnetCrawlerLibraryErrorCode.WaitTimeout
        
        self.__SleepTime = self.__SleepTime * (ReceiveTimes / 5.0)'''
        
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
            
        CaseList = ['密碼不對', '您想刪除其他重複登入', '按任意鍵繼續', '您要刪除以上錯誤嘗試', '您有一篇文章尚未完成', '[呼叫器]']
        SendMessage = self.__ID
        
        while True:
            self.__telnet = telnetlib.Telnet(self.__host)
            ErrorCode, Index = self.__sendData(SendMessage, CaseList)
            if ErrorCode != PTTTelnetCrawlerLibraryErrorCode.Success:
                return ErrorCode
            
            if Index == 0:
                self.Log('Wrong password')
                return PTTTelnetCrawlerLibraryErrorCode.WrongPassword
            if Index == 1:
                if self.__kickOtherLogin:
                    SendMessage = 'y\r\n'
                    self.Log('Detect other login')
                    self.Log('Kick other login success')
                else :
                    SendMessage = 'n'
                    self.Log('Detect other login')
            if Index == 2:
                SendMessage = ''
            if Index == 3:
                SendMessage = 'y'
                self.Log('Delete error password log')
            if Index == 4:
                SendMessage = 'q'
                self.Log('Delete the post not finished')    
            if Index == 5:
                self.Log('Login success!')
                break
        
        self.__isConnected = True
    
    def logout(self):
        pass
if __name__ == '__main__':

    print('PTT Telnet Crawler Library v 0.1.170607')
    print('PTT CodingMan')
