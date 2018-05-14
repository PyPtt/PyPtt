
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
    def __init__(self, Board, PostID, Author, Date, Title, WebUrl, Money, PostContent, IP, PushList):
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

class WaterBallInformation(object):
    def __init__(self, Author, PushContent):
        self.__Author = str(Author)
        self.__Content = str(PushContent)

    def getAuthor(self):
        return self.__Author
    def getContent(self):
        return self.__Content
