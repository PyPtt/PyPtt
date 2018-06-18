import array

class WaterBallType(object):
    Catch =                                 1
    Send =                                  2

    MinValue = Catch
    MaxValue = Send

class WaterBallOperateType(object):
    Clear =                                 1
    Mail =                                  2
    DoNothing =                             3

    MinValue = Clear
    MaxValue = DoNothing

class OperateType(object):
    Add =                                   1
    Del =                                   2
    Query =                                 3

    MinValue = Add
    MaxValue = Query

class FriendListType(object):
    GoodFriend =                            1
    BadGuy =                                2
    SuperFriend =                           3
    LoginNotification =                     4
    OtherSpecial =                          5

    MinValue = GoodFriend
    MaxValue = OtherSpecial

class ReplyPostType(object):
    def __init__(self):
        self.Board =                        1
        self.Mail =                         2
        self.Board_Mail =                   3
        
class LogLevel(object):
    def __init__(self):
        self.DEBUG =                        1
        self.WARNING =                      2
        self.INFO =                         3
        self.CRITICAL =                     4
        self.SLIENT =                       5

        self.MaxValue = self.SLIENT
        self.MinValue = self.DEBUG

class PushType(object):
    def __init__(self):
        self.Unknow =                       0
        self.Push =                         1
        self.Boo =                          2
        self.Arrow =                        3

class MailInformation(object):
    def __init__(self, Author, Title, Date, Content, IP, RawData):
        self.__Author = str(Author)
        self.__Title = str(Title)
        self.__Date = str(Date)
        self.__Content = str(Content)
        self.__IP = str(IP)
        self.__RawData = array.array('B', RawData).tostring()
    def getAuthor(self):
        return self.__Author
    def getTitle(self):
        return self.__Title
    def getDate(self):
        return self.__Date
    def getContent(self):
        return self.__Content
    def getIP(self):
        return self.__IP
    def getRawData(self):
        return self.__RawData

class UserInformation(object):
    def __init__(self, ID, Money, LoginTime, LegalPost, IllegalPost, State, Mail, LastLogin, LastIP, FiveChess, Chess):
        self.__ID = str(ID)
        self.__Money = str(Money)
        self.__LoginTime = int(LoginTime)
        self.__LegalPost = int(LegalPost)
        self.__IllegalPost = int(IllegalPost)
        self.__State = str(State)
        self.__Mail = str(Mail)
        self.__LastLogin = str(LastLogin)
        self.__LastIP = str(LastIP)
        self.__FiveChess = FiveChess
        self.__Chess = Chess
    def getID(self):
        return self.__ID
    def getMoney(self):
        return self.__Money
    def getLoginTime(self):
        return self.__LoginTime
    def getLegalPost(self):
        return self.__LegalPost
    def getIllegalPost(self):
        return self.__IllegalPost
    def getState(self):
        return self.__State
    def getMail(self):
        return self.__Mail
    def getLastLogin(self):
        return self.__LastLogin
    def getLastIP(self):
        return self.__LastIP
    def getFiveChess(self):
        return self.__FiveChess
    def getChess(self):
        return self.__Chess
        
class PushInformation(object):
    def __init__(self, PushType, Author, PushContent, PushTime):
        self.__Type = int(PushType)
        self.__Author = str(Author)
        self.__Content = str(PushContent)
        self.__Time = str(PushTime)

    def getType(self):
        return self.__Type
    def getAuthor(self):
        return self.__Author
    def getContent(self):
        return self.__Content
    def getTime(self):
        return self.__Time
        
class PostInformation(object):
    def __init__(self, Board, PostID, Author, Date, Title, WebUrl, Money, PostContent, IP, PushList, RawData):
        self.__Board = str(Board)
        self.__PostID = str(PostID)
        self.__Author = str(Author)
        self.__Date = str(Date)
        self.__Title = str(Title)
        self.__PostContent = str(PostContent)
        self.__Money = int(Money)
        self.__WebUrl = str(WebUrl)
        self.__IP = str(IP)
        self.__PushList = PushList
        self.__RawData = array.array('B', RawData).tostring()

        

    def getBoard(self):
        return self.__Board
    def getID(self):
        return self.__PostID
    def getAuthor(self):
        return self.__Author
    def getDate(self):
        return self.__Date
    def getTitle(self):
        return self.__Title
    def getContent(self):
        return self.__PostContent
    def getMoney(self):
        return self.__Money
    def getWebUrl(self):
        return self.__WebUrl
    def getIP(self):
        return self.__IP
    def getPushList(self):
        return self.__PushList
    def getRawData(self):
        return self.__RawData

class WaterBallInformation(object):
    def __init__(self, Type, Author, PushContent, Date=''):
        self.__Type = int(Type)
        self.__Author = str(Author)
        self.__Content = str(PushContent)
        self.__Date = str(Date)
    def getAuthor(self):
        return self.__Author
    def getContent(self):
        return self.__Content
    def getDate(self):
        return self.__Date
    def getType(self):
        return self.__Type
