import array


def ParseParameter(type, input):
    if input is None:
        return None
    result = type(input)
    if isinstance(result, str):
        result = result.rstrip()
    return result


class PostSearchType(object):
    # 搜尋關鍵字    / ?
    # 搜尋作者      a
    # 搜尋推文數    Z
    # 搜尋標記      G
    # 搜尋稿酬      A
    Unknow =                                0
    Keyword =                               1
    Author =                                2
    Push =                                  3
    Mark =                                  4
    Money =                                 5

    MinValue = Unknow
    MaxValue = Money

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
        self.__Author = ParseParameter(str, Author)
        self.__Title = ParseParameter(str, Title)
        self.__Date = ParseParameter(str, Date)
        self.__Content = ParseParameter(str, Content)
        self.__IP = ParseParameter(str, IP)
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
        self.__ID = ParseParameter(str, ID)
        self.__Money = ParseParameter(str, Money)
        self.__LoginTime = ParseParameter(int, LoginTime)
        self.__LegalPost = ParseParameter(int, LegalPost)
        self.__IllegalPost = ParseParameter(int, IllegalPost)
        self.__State = ParseParameter(str, State)
        self.__Mail = ParseParameter(str, Mail)
        self.__LastLogin = ParseParameter(str, LastLogin)
        self.__LastIP = ParseParameter(str, LastIP)
        self.__FiveChess = ParseParameter(str, FiveChess)
        self.__Chess = ParseParameter(str, Chess)
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
    def __init__(self, PushType, Author, PushContent, PushIP, PushTime):
        self.__Type = ParseParameter(int, PushType)
        self.__Author = ParseParameter(str, Author)
        self.__Content = ParseParameter(str, PushContent)
        self.__IP = ParseParameter(str, PushIP)
        self.__Time = ParseParameter(str, PushTime)

    def getType(self):
        return self.__Type
    def getAuthor(self):
        return self.__Author
    def getContent(self):
        return self.__Content
    def getIP(self):
        return self.__IP
    def getTime(self):
        return self.__Time

class PostDeleteStatus(object):
    NotDeleted =                            0
    ByAuthor =                              1
    ByModerator =                           2
    ByUnknow =                              3

    MinValue = NotDeleted
    MaxValue = ByUnknow


class PostInformation(object):
    def __init__(self, Board=None, PostID=None, Author=None, Date=None, Title=None, WebUrl=None, Money=None, PostContent=None, IP=None, PushList=None, RawData=None, ListDate=None, DeleteStatus=0):
        self.__Board = ParseParameter(str, Board)        
        self.__PostID = ParseParameter(str, PostID)
        self.__Author = ParseParameter(str, Author)
        self.__Date = ParseParameter(str, Date)
        self.__Title = ParseParameter(str, Title)
        self.__PostContent = ParseParameter(str, PostContent)
        self.__Money = ParseParameter(int, Money)
        self.__WebUrl = ParseParameter(str, WebUrl)
        self.__IP = ParseParameter(str, IP)
        self.__PushList = PushList
        self.__RawData = ParseParameter(str, RawData)
        self.__DeleteStatus = DeleteStatus
        self.__ListDate = ParseParameter(str, ListDate)
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
    def getDeleteStatus(self):
        return self.__DeleteStatus
    def getListDate(self):
        return self.__ListDate

class WaterBallInformation(object):
    def __init__(self, Type, Author, PushContent, Date=''):
        self.__Type = ParseParameter(int, Type)
        self.__Author = ParseParameter(str, Author)
        self.__Content = ParseParameter(str, PushContent)
        self.__Date = ParseParameter(str, Date)
    def getAuthor(self):
        return self.__Author
    def getContent(self):
        return self.__Content
    def getDate(self):
        return self.__Date
    def getType(self):
        return self.__Type
