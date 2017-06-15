# -*- coding: utf8 -*-
import sys
import telnetlib
import time
import re
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import PTTUtil

Success =                         0
UnknowError =                   0.1
ConnectError =                    1
EOFError =                        2
ConnectionResetError =            3
WaitTimeout =                     4
WrongPassword =                   5
ErrorInput =                      6
PostNotFound =                    7
ParseError =                      8
PostDeleted =                     9
WebFormatError =                 10
NoPermission =                   11
NoUser =                         12

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
    
class Crawler(object):
    def __init__(self, ID, Password, kickOtherLogin):
 
        PTTUtil.Log('ID: ' + ID)

        TempPW = ''

        for i in range(len(Password)):
            TempPW += '*'
        
        PTTUtil.Log('Password: ' + TempPW)
        if kickOtherLogin:
            PTTUtil.Log('This connection will kick other login')
        else :
            PTTUtil.Log('This connection will NOT kick other login')

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
        PTTUtil.Log(Message)
    def isLoginSuccess(self):
        return self.__isConnected
    def __readScreen(self, Message='', ExpectTarget=[]):
        
        result = -1
        ErrorCode = UnknowError
        try:
            self.__telnet.write(str(Message + '\x0C').encode('big5'))
        except ConnectionResetError:
            PTTUtil.Log('Remote reset connection...')
            self.__connectRemote()
            return ConnectionResetError, result
        
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
                PTTUtil.Log('Remote kick connection...')
                self.__connectRemote()
                self.__CurrentTimeout = 0
                return EOFError, result
            
            DataMacthed = False
            
            for i in range(len(ExpectTarget)):
                #print(ExpectTarget[i])
                if ExpectTarget[i] in self.__ReceiveData:
                    result = i
                    DataMacthed = True
                    break
            
            if DataMacthed:
                ErrorCode = Success
                break
            
            NowTime = time.time()
            
            if NowTime - StartTime > self.__Timeout:
                self.__Timeouted = True
                #print(str(len(self.__ReceiveData)))
                #print('ReadScreen timeouted')
                ErrorCode = WaitTimeout
                break
        
        self.__SleepTime = self.__SleepTime * (ReceiveTimes / 5.0)
        self.__CurrentTimeout = 0
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
            PTTUtil.Log('Remote kick connection...')
            self.__connectRemote()
            self.__CurrentTimeout = 0
            return EOFError, -1
        except ConnectionResetError:
            PTTUtil.Log('Remote reset connection...')
            self.__connectRemote()
            self.__CurrentTimeout = 0
            return ConnectionResetError, -1
        
        if ReturnIndex == -1:
            print('SendData timeouted')
            self.__CurrentTimeout = 0
            return WaitTimeout, ReturnIndex
        self.__CurrentTimeout = 0
        return Success, ReturnIndex
    def __connectRemote(self):
        self.__isConnected = False
        
        while True:
            self.__telnet = telnetlib.Telnet(self.__host)
            ErrorCode, Index = self.__sendData('', ['請輸入代號', '系統過載'], False)
            if ErrorCode != Success:
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
            if ErrorCode != Success:
                return ErrorCode
            if Index == 0:
                self.Log('Wrong password')
                return WrongPassword
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
        '''
        BoardList = ['Wanted', 'Gossiping', 'Test', 'Python']
        
        i = 0
        
        for Board in BoardList:
            ErrorCode, NewestIndex = self.getNewestPostIndex(Board)
            if ErrorCode == Success:
                self.Log('Detect network environment: ' + str(int(((i + 1) * 100) / len(BoardList))) + ' % ')
            else:
                self.Log('Detect network environment: ' + str(int(((i + 1) * 100) / len(BoardList))) + ' % ' + ' fail')
                return False
            i+=1
        '''
        return Success
        
    def __gotoTop(self):
        for i in range(3):
            ErrorCode = self.___gotoTop()
            if ErrorCode == Success:
                break
        return ErrorCode
    def ___gotoTop(self):
    
        ErrorCode, Index = self.__sendData('q\x1b[D\x1b[D\x1b[D\x1b[D', ['[呼叫器]', '編特別名單', '娛樂與休閒', '系統資訊區', '主功能表', '私人信件區'], False, True)
        if ErrorCode != Success:
            return ErrorCode
        return Success
    def logout(self):
        ErrorCode = self.__gotoTop()
        if ErrorCode != Success:
            print('Error code 1: ' + str(ErrorCode))
            return ErrorCode
        
        try:
            ErrorCode, Index = self.__sendData('g\r\ny', ['此次停留時間'])
        except TypeError:
            pass
        
        self.__telnet.close()
        PTTUtil.Log('Logout success')
        
        return Success
    def __gotoBoard(self, Board):
        for i in range(5):
            ErrorCode = self.___gotoBoard(Board)
            if ErrorCode == Success:
                break
                
        return ErrorCode
    def ___gotoBoard(self, Board):
        ErrorCode = self.__gotoTop()
        if ErrorCode != Success:
            print('Error code __gotoBoard 1: ' + str(ErrorCode))
            return ErrorCode
        CaseList = ['請輸入看板名稱']
        SendMessage = 's'
        
        self.__CurrentTimeout = 5
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, False)
        if ErrorCode != Success:
            print('Error code __gotoBoard 2: ' + str(ErrorCode))
            return ErrorCode
        
        #self.__showScreen()
        CaseList = ['請按任意鍵繼續', '其他任意鍵停止', '動畫播放中', '看板《' + Board + '》']
        SendMessage = Board
        Enter = True
        while True:            
            ErrorCode, Index = self.__sendData(SendMessage, CaseList, Enter)
            if ErrorCode != Success:
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
                
        return Success
    
    def post(self, board, title, content, PostType, SignType):
    
        self.__CurrentTimeout = 10
        
        ErrorCode = self.__gotoBoard(board)
        if ErrorCode != Success:
            self.Log('post 1 Go to ' + board + ' fail')
            return ErrorCode
        
        CaseList = ['1-8或不選', '使用者不可發言']
        SendMessage = '\x10'
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, False)
        if ErrorCode != Success:
            self.Log('post 2 error code: ' + str(ErrorCode))
            return ErrorCode
        
        if Index == 1:
            self.Log('You are in the bucket QQ')
            return NoPermission
        
        CaseList = ['標題']
        SendMessage = str(PostType)
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList)
        if ErrorCode != Success:
            self.Log('post 3 error code: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['編輯文章']
        SendMessage = title
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList)
        if ErrorCode != Success:
            
            self.Log('post 4 error code: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['確定要儲存檔案嗎']
        SendMessage = content + '\x18'
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, False)
        if ErrorCode != Success:
            self.Log('post 5 error code: ' + str(ErrorCode))
            return ErrorCode
        
        self.__CurrentTimeout = 10
        
        CaseList = ['x=隨機', '請按任意鍵繼續', '看板《' + board + '》']
        SendMessage = 's'
        Enter = True
        Refresh = False
        while True:        
            ErrorCode, Index = self.__sendData(SendMessage, CaseList, Enter, Refresh)
            if ErrorCode != Success:
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
                
        return Success
    
    def getNewestPostIndex(self, Board):
        
        TryTime = 0
        
        for i in range(10):
            ErrorCode, Index = self.__getNewestPostIndex(Board)
            TryTime += 1
            if ErrorCode == Success:
                break
            elif ErrorCode == ParseError:
                #self.Log('getNewestPostIndex parse error retry..')
                pass
            elif ErrorCode == WaitTimeout:
                #self.Log('getNewestPostIndex time out retry..')
                pass
            else:
                self.Log('ErrorCode: ' + str(ErrorCode))
                return ErrorCode, Index
            time.sleep(self.__SleepTime)
        
        #self.Log('TryTime: ' + str(TryTime))
        return ErrorCode, Index
    def __getNewestPostIndex(self, Board):
        ReturnIndex = -1
    
        ErrorCode = self.__gotoBoard(Board)
        if ErrorCode != Success:
            self.Log('getNewestPostIndex 1 Go to ' + Board + ' fail')
            return ErrorCode, -1
        
        self.__readScreen('0\r\n$', ['★'])
        if ErrorCode == WaitTimeout:
            #self.Log('getNewestPostIndex 2.1 error code: ' + str(ErrorCode))
            print(self.__ReceiveData)
            return ErrorCode, -1

        AllIndex = re.findall(r'\d+ ', self.__ReceiveData)
        
        AllIndex = list(set(map(int, AllIndex)))
        AllIndex.sort()
        
        if len(AllIndex) == 0:
            return ParseError, -1
        
        AllIndexTemp = list(AllIndex)
        while True:
            
            ReturnIndexTemp = AllIndex.pop()
            
            if len(str(ReturnIndexTemp)) <= 6:

                HasFront = True
                HasBack = True
                '''
                print(AllIndexTemp)
                print(str(ReturnIndexTemp))
                '''
                for i in range(5):
                    if not (ReturnIndexTemp - i) in AllIndexTemp:
                        HasFront = False
                        break
                
                for i in range(5):
                    if not (ReturnIndexTemp + i) in AllIndexTemp:
                        HasBack = False
                        break
                
                if HasFront or HasBack:
                    ReturnIndex = ReturnIndexTemp
                    break
            if len(AllIndex) == 0:
                #print(self.__ReceiveData)
                #print(AllIndexTemp)
                #self.Log('Parse error!!!')
                return ParseError, -1
        return Success, int(ReturnIndex)
    
    def __gotoPostByIndex(self, Board, PostIndex):
        for i in range(3):
            ErrorCode = self.___gotoPostByIndex(Board, PostIndex)
            if ErrorCode == Success:
                break
        return ErrorCode
    def ___gotoPostByIndex(self, Board, PostIndex):
    
        ErrorCode = self.__gotoBoard(Board)
        if ErrorCode != Success:
            self.Log('__gotoPostByIndex 1 Go to ' + Board + ' fail')
            self.__showScreen()
            return ErrorCode

        IndexTarget = '>{0: >6}'.format(str(PostIndex))
        
        self.__CurrentTimeout = 5
        
        self.__readScreen(str(PostIndex) + '\r\n', [IndexTarget])
        
        if IndexTarget in self.__ReceiveData:
            return Success
        else:
            #print(self.__ReceiveData)
            return PostNotFound
    def __gotoPostByID(self, Board, PostID):
        ErrorCode = self.__gotoBoard(Board)
        if ErrorCode != Success:
            self.Log('__gotoPostByID 1 Go to ' + Board + ' fail')
            return ErrorCode
        
        self.__readScreen('#' + PostID + '\r\n', '文章選讀')
        
        if '找不到這個文章代碼' in self.__ReceiveData:
            return PostNotFound
        
        return Success
        
    def getPostInfoByID(self, Board, PostID, Index=-1):
        for i in range(5):
            ErrorCode, Post = self.__getPostInfoByID(Board, PostID, Index)
            if ErrorCode == Success:
                break
            if ErrorCode == WebFormatError:
                break
            if ErrorCode == PostDeleted:
                break
        return ErrorCode, Post
    def __getPostInfoByID(self, Board, PostID, Index=-1):
        
        if Index != -1:
            ErrorCode = self.__gotoPostByIndex(Board, Index)
            if ErrorCode != Success:
                self.Log('getPostInfoByIndex 1 goto post fail')
                return ErrorCode, None
        else:
        
            if len(PostID) != 8:
                self.Log('Error input: ' + PostID)
                return ErrorInput, None
        
            ErrorCode = self.__gotoPostByID(Board, PostID)
            if ErrorCode != Success:
                self.Log('getPostInfoByID 1 goto post fail')
                return ErrorCode, None
        
        ErrorCode, Index = self.__readScreen('Q', ['請按任意鍵繼續'])
        if ErrorCode == WaitTimeout:
            return PostDeleted, None
        if ErrorCode != Success:
            self.Log('getPostInfoByID 3 read screen time out')
            return ErrorCode, None
        
        if Index == 0:
            #Get query screen success
            pass
        if Index == 1:
            print(self.__ReceiveData)
            print('Post has beeb deleted')
            return PostDeleted, None
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
                return ParseError, None
        
        if 'https' in self.__ReceiveData:
            RealWebUrl = self.__ReceiveData[self.__ReceiveData.find('https'):self.__ReceiveData.find('.html') + 5]
        else:
            self.Log('Find weburl fail')
            return ParseError, None
        
        if '這一篇文章值' in self.__ReceiveData:
            RealMoneyTemp = self.__ReceiveData[self.__ReceiveData.find('這一篇文章值') + len('這一篇文章值') : self.__ReceiveData.find('Ptt幣')]
            RealMoney = int(re.search(r'\d+', RealMoneyTemp).group())
        else:
            self.Log('Find post money fail')
            return ParseError, None
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
            #self.Log('div.article-metaline is not exist')
            return WebFormatError, None
            
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
        
        return Success, result

    def getPostInfoByIndex(self, Board, Index):
        
        ErrorCode, Post = self.getPostInfoByID(Board, '', Index)
        
        return ErrorCode, Post
    
    def getNewPostIndexList(self, Board, LastPostIndex):
        
        result = []
        ErrorCode, LastIndex = self.getNewestPostIndex(Board)

        if ErrorCode != Success:
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
            if ErrorCode == Success:
                break
            if ErrorCode == NoPermission:
                break
        return ErrorCode
    def __pushByID(self, Board, PushType, PushContent, PostID, PostIndex=-1):
        self.__CurrentTimeout = 3
    
        if PostIndex != -1:
            ErrorCode = self.__gotoPostByIndex(Board, PostIndex)
            if ErrorCode != Success:
                self.Log('pushByIndex 1 goto post fail')
                return ErrorCode
        else:
        
            if len(PostID) != 8:
                self.Log('pushByID Error input: ' + PostID)
                return ErrorInput
        
            ErrorCode = self.__gotoPostByID(Board, PostID)
            if ErrorCode != Success:
                self.Log('pushByID 1 goto post fail')
                return ErrorCode
        
        #CaseList = ['您覺得這篇文章', '加註方式', '禁止快速連續推文']
        
        Message = 'X'
        
        while True:
        
            ErrorCode, Index = self.__readScreen(Message, ['您覺得這篇文章', '加註方式', '禁止快速連續推文', '禁止短時間內大量推文', '使用者不可發言'])
            if ErrorCode == WaitTimeout:
                print(self.__ReceiveData)
                self.Log('No push option')
                return NoPermission
            if ErrorCode != Success:
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
                PTTUtil.Log('No fast push, wait...')
                Message = 'qX'
                time.sleep(1)
            if Index == 3:
                PTTUtil.Log('System abort many push, wait...')
                Message = 'qX'
                time.sleep(2)
            if Index == 4:
                PTTUtil.Log('You are in the bucket QQ')
                return NoPermission
                
        if not AllowPushTypeList[self.PushType_Boo] and PushType == self.PushType_Boo:
            PushType = self.PushType_Arrow
        
        CaseList = ['']
        
        if ArrowOnly:
            SendMessage = PushContent + '\r\ny'
        else:
            SendMessage = str(PushType) + PushContent + '\r\ny'
        
        ErrorCode, Index = self.__sendData(SendMessage, CaseList, True, True)
        if ErrorCode != Success:
            self.Log('pushByID 3 error code: ' + str(ErrorCode))
            return ErrorCode

        return Success
    def pushByIndex(self, Board, PushType, PushContent, PostIndex):
        ErrorCode = self.pushByID(Board, PushType, PushContent, '', PostIndex)
        return ErrorCode
    def mail(self, UserID, MailTitle, MailContent, SignType):
    
        self.__CurrentTimeout = 3
        
        ErrorCode = self.__gotoTop()
        if ErrorCode != Success:
            print('mail goto top error code 1: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['主題：', '請選擇簽名檔', '已順利寄出，是否自存底稿', '任意鍵繼續', '電子郵件']
        SendMessage = 'M\r\nS\r\n' + UserID
        Enter = True
        while True:        
            ErrorCode, Index = self.__sendData(SendMessage, CaseList, Enter)
            if ErrorCode == WaitTimeout:
                self.__showScreen()
                self.Log('No such user: ' + UserID)
                return NoUser
            if ErrorCode != Success:
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
        
        return Success
        
    def giveMoney(self, ID, Money, YourPassword):
        self.__CurrentTimeout = 3
        
        ErrorCode = self.__gotoTop()
        if ErrorCode != Success:
            print('giveMoney goto top error code 1: ' + str(ErrorCode))
            return ErrorCode
        
        CaseList = ['量販店', '給其他人Ptt幣', '這位幸運兒的id', '請輸入金額', '請輸入您的密碼', '要修改紅包袋嗎', '確定進行交易嗎', '按任意鍵繼續']
        SendMessage = 'P'
        Enter = True
        while True:        
            ErrorCode, Index = self.__sendData(SendMessage, CaseList, Enter)
            if ErrorCode == WaitTimeout:
                self.__showScreen()
                self.Log('No such option: ' + SendMessage)
                return NoUser
            if ErrorCode != Success:
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
        return Success
        
    def getTime(self):
        for i in range(5):
            ErrorCode, Time = self.__getTime()
            if ErrorCode == Success:
                break
        return ErrorCode, Time
    def __getTime(self):
        self.__CurrentTimeout = 2
        
        #Thanks for ervery one in Python
        
        ErrorCode = self.__gotoTop()
        if ErrorCode != Success:
            print('getTime goto top error code 2: ' + str(ErrorCode))
            return ErrorCode, ''
            
        self.__CurrentTimeout = 1
        ErrorCode, Index = self.__readScreen('A\r\nqA\r\nq', ['呼叫器', '離開，再見…'])
        if ErrorCode == WaitTimeout:
            #self.__showScreen()
            #self.Log('getTime 2.1')
            return ErrorCode, ''
        if ErrorCode != Success:
            self.Log('getTime 3 read screen error code: ' + str(ErrorCode))
            return ErrorCode, ''
        
        if not '離開，再見…' in self.__ReceiveData or not '[呼叫器]' in self.__ReceiveData:
            #self.Log('Not in user menu 1')
            return ParseError, ''
        
        result = self.__ReceiveData[self.__ReceiveData.find('離開，再見…') + len('離開，再見…'):self.__ReceiveData.find('[呼叫器]')]
        
        if not '星期' in result:
            #self.Log('Not in user menu 2')
            return ParseError, ''
        
        result = result[result.find('星期') + len('星期'):]
        result = result[result.find(' ') + 1:result.find(']')]

        return Success, result
    
    def getUserInfo(self, ID):
        ErrorCode = self.__gotoTop()
        if ErrorCode != Success:
            print('getUserInfo goto top error code 1: ' + str(ErrorCode))
            return ErrorCode, None
        CaseList = ['請輸入使用者代號', '請按任意鍵繼續', '顯示上幾次熱訊']
        SendMessage = 'T\r\nQ\r\n'
        Enter = False
        while True:        
            ErrorCode, Index = self.__sendData(SendMessage, CaseList, Enter)
            if ErrorCode == WaitTimeout:
                self.__showScreen()
                self.Log('No such option: ' + SendMessage)
                return ErrorCode, None
            if ErrorCode != Success:
                self.Log('getUserInfo 2 error code: ' + str(ErrorCode))
                return ErrorCode, None
            if Index == 0:
                #self.Log('Input user ID')
                SendMessage = str(ID)
                Enter = True
            if Index == 1:
                break
            if Index == 2:
                #self.Log('No such user')
                return NoUser, None
        
                
        self.__CurrentTimeout = 3
        
        ErrorCode, Index = self.__readScreen('', ['請按任意鍵繼續'])
        
        if ErrorCode == WaitTimeout:
            return WaitTimeout, None
        if ErrorCode != Success:
            self.Log('getUserInfo 3 read screen time out')
            return ErrorCode, None
        
        if not '《ＩＤ暱稱》' in self.__ReceiveData or not '《經濟狀況》' in self.__ReceiveData or not '《登入次數》' in self.__ReceiveData or not '《有效文章》' in self.__ReceiveData or not '《目前動態》' in self.__ReceiveData or not '《私人信箱》' in self.__ReceiveData or not '《上次上站》' in self.__ReceiveData or not '《上次故鄉》' in self.__ReceiveData or not '《 五子棋 》' in self.__ReceiveData or not '《象棋戰績》' in self.__ReceiveData:
            self.Log('User info not complete')
            return WaitTimeout, None
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
        
        return Success, result
if __name__ == '__main__':

    print('PTT Crawler Library v 0.2.170615 beta')
    print('PTT CodingMan')
