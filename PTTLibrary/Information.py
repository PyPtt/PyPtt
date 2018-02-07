
class ReplyPostType(object):
    def __init__(self):
        self.Board =                        1
        self.Mail =                         2

class LogLevel(object):
    def __init__(self):
        self.DEBUG =                        1
        self.WARNING =                      2
        self.INFO =                         3
        self.CRITICAL =                     4
        self.SLIENT =                       5

class PushType(object):
    def __init__(self):
        self.Push =                         1
        self.Boo =                          2
        self.Arrow =                        3

class MailInformation(object):
    def __init__(self, Author, Title, Date, Content, IP):
        self.__Author = str(Author)
        self.__Title = str(Title)
        self.__Date = str(Date)
        self.__Content = str(Content)
        self.__IP = str(IP)
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
    def __init__(self, Board, PostID, Author, Date, Title, WebUrl, Money, PostContent, PushList):
        self.__Board = str(Board)
        self.__PostID = str(PostID)
        self.__Author = str(Author)
        self.__Date = str(Date)
        self.__Title = str(Title)
        self.__PostContent = str(PostContent)
        self.__Money = Money
        self.__WebUrl = str(WebUrl)
        self.__PushList = PushList
    def getPostBoard(self):
        return self.__Board
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