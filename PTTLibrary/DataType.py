
import array
from uao import register_uao
register_uao()


def ParseParameter(type, input):
    if input is None:
        return None
    result = type(input)
    if isinstance(result, str):
        result = result.rstrip()
    return result


class CallStatus:
    # 呼叫器狀態

    # 打開
    On = 0
    # 拔掉
    Unplug = 1
    # 防水
    Waterproof = 2
    # 好友
    Friend = 3
    # 關掉
    Off = 4

    MinValue = On
    MaxValue = Off


class PostSearchType:
    # 文章搜尋類型

    Nope = 0
    # 搜尋關鍵字    / ?
    Keyword = 1
    # 搜尋作者      a
    Author = 2
    # 搜尋推文數    Z
    Push = 3
    # 搜尋標記      G
    Mark = 4
    # 搜尋稿酬      A
    Money = 5

    MinValue = Nope
    MaxValue = Money


class WaterBallType:
    # 水球接收狀態

    # 收到水球
    Catch = 1
    # 收到水球
    Send = 2

    MinValue = Catch
    MaxValue = Send


class WaterBallOperateType:
    # 清除水球類型

    Clear = 1
    Mail = 2
    DoNothing = 3

    MinValue = Clear
    MaxValue = DoNothing


class OperateType:
    # 操作類型

    Add = 1
    Del = 2
    Query = 3

    MinValue = Add
    MaxValue = Query


class FriendListType:
    # 名單類型

    GoodFriend = 1
    BadGuy = 2
    SuperFriend = 3
    LoginNotification = 4
    OtherSpecial = 5

    MinValue = GoodFriend
    MaxValue = OtherSpecial


class ReplyType:
    # 回文類型

    Board = 1
    Mail = 2
    Board_Mail = 3

    MinValue = Board
    MaxValue = Board_Mail


class PushType:
    Push = 1
    Boo = 2
    Arrow = 3

    MinValue = Push
    MaxValue = Arrow


class MailInformation:
    def __init__(self, Author, Title, Date, Content, IP, RawData):
        self._Author = ParseParameter(str, Author)
        self._Title = ParseParameter(str, Title)
        self._Date = ParseParameter(str, Date)
        self._Content = ParseParameter(str, Content)
        self._IP = ParseParameter(str, IP)
        self._RawData = array.array('B', RawData).tostring()

    def getAuthor(self):
        return self._Author

    def getTitle(self):
        return self._Title

    def getDate(self):
        return self._Date

    def getContent(self):
        return self._Content

    def getIP(self):
        return self._IP

    def getRawData(self):
        return self._RawData


class UserInfo:
    def __init__(
        self,
        ID,
        Money,
        LoginTime,
        LegalPost,
        IllegalPost,
        State,
        Mail,
        LastLogin,
        LastIP,
        FiveChess,
        Chess,
        SignatureFile
    ):
        self._ID = ParseParameter(str, ID)
        self._Money = ParseParameter(str, Money)
        self._LoginTime = ParseParameter(int, LoginTime)
        self._LegalPost = ParseParameter(int, LegalPost)
        self._IllegalPost = ParseParameter(int, IllegalPost)
        self._State = ParseParameter(str, State)
        self._Mail = ParseParameter(str, Mail)
        self._LastLogin = ParseParameter(str, LastLogin)
        self._LastIP = ParseParameter(str, LastIP)
        self._FiveChess = ParseParameter(str, FiveChess)
        self._Chess = ParseParameter(str, Chess)
        self._SignatureFile = ParseParameter(str, SignatureFile)

    def getID(self):
        return self._ID

    def getMoney(self):
        return self._Money

    def getLoginTime(self):
        return self._LoginTime

    def getLegalPost(self):
        return self._LegalPost

    def getIllegalPost(self):
        return self._IllegalPost

    def getState(self):
        return self._State

    def getMail(self):
        return self._Mail

    def getLastLogin(self):
        return self._LastLogin

    def getLastIP(self):
        return self._LastIP

    def getFiveChess(self):
        return self._FiveChess

    def getChess(self):
        return self._Chess

    def getSignatureFile(self):
        return self._SignatureFile


class PushInfo:
    def __init__(self, PushType, Author, PushContent, PushIP, PushTime):
        self._Type = ParseParameter(int, PushType)
        self._Author = ParseParameter(str, Author)
        self._Content = ParseParameter(str, PushContent)
        self._IP = ParseParameter(str, PushIP)
        self._Time = ParseParameter(str, PushTime)

    def getType(self):
        return self._Type

    def getAuthor(self):
        return self._Author

    def getContent(self):
        return self._Content

    def getIP(self):
        return self._IP

    def getTime(self):
        return self._Time


class PostDeleteStatus:
    NotDeleted = 0
    ByAuthor = 1
    ByModerator = 2
    ByUnknow = 3

    MinValue = NotDeleted
    MaxValue = ByUnknow


class PostInfo:
    def __init__(
        self,
        Board=None,
        AID=None,
        Author=None,
        Date=None,
        Title=None,
        WebUrl=None,
        Money=None,
        Content=None,
        IP=None,
        PushList=None,
        ListDate=None,
        DeleteStatus=0,
        ControlCode=False,
        FormatCheck=False,
        Location=None,
        PushNumber=None,
        Lock=False,
        OriginPost=None,
        Unconfirmed=False
    ):
        self._Board = ParseParameter(str, Board)
        self._AID = ParseParameter(str, AID)
        self._Author = ParseParameter(str, Author)
        self._Date = ParseParameter(str, Date)
        self._Title = ParseParameter(str, Title)
        self._Content = ParseParameter(str, Content)
        self._Money = ParseParameter(int, Money)
        self._WebUrl = ParseParameter(str, WebUrl)
        self._IP = ParseParameter(str, IP)
        self._PushList = PushList
        self._DeleteStatus = DeleteStatus
        self._ListDate = ParseParameter(str, ListDate)
        self._ControlCode = ControlCode
        self._FormatCheck = FormatCheck
        self._Location = ParseParameter(str, Location)
        self._PushNumber = ParseParameter(str, PushNumber)
        self._Lock = Lock
        self._OriginPost = ParseParameter(str, OriginPost)
        self._Unconfirmed = ParseParameter(bool, Unconfirmed)

    def getBoard(self):
        return self._Board

    def getAID(self):
        return self._AID

    def getAuthor(self):
        return self._Author

    def getDate(self):
        return self._Date

    def getTitle(self):
        return self._Title

    def getContent(self):
        return self._Content

    def getMoney(self):
        return self._Money

    def getWebUrl(self):
        return self._WebUrl

    def getIP(self):
        return self._IP

    def getPushList(self):
        return self._PushList

    def getDeleteStatus(self):
        return self._DeleteStatus

    def getListDate(self):
        return self._ListDate

    def hasControlCode(self):
        return self._ControlCode

    def isFormatCheck(self):
        return self._FormatCheck

    def getLocation(self):
        return self._Location

    def getPushNumber(self):
        return self._PushNumber

    def isLock(self):
        return self._Lock

    def getOriginPost(self):
        return self._OriginPost

    def isUnconfirmed(self):
        return self._Unconfirmed


class WaterBallInfo:
    def __init__(self, Type, Target, Content, Date):
        self._Type = ParseParameter(int, Type)
        self._Target = ParseParameter(str, Target)
        self._Content = ParseParameter(str, Content)
        self._Date = ParseParameter(str, Date)

    def getTarget(self):
        return self._Target

    def getContent(self):
        return self._Content

    def getDate(self):
        return self._Date

    def getType(self):
        return self._Type


class Cursor:
    # 舊式游標
    Old = '●'
    # 新式游標
    New = '>'


class IndexType:
    # 板
    BBS = 1
    # 信箱
    Mail = 2
    #
    Web = 3

    MinValue = BBS
    MaxValue = Web


class CrawlType:
    # BBS版本
    BBS = 1
    # 網頁版本
    Web = 2

    MinValue = BBS
    MaxValue = Web


class Host:
    # 批踢踢萬
    PTT1 = 1
    # 批踢踢兔
    PTT2 = 2

    MinValue = PTT1
    MaxValue = PTT2


class MarkType:
    # s 文章
    S = 1
    # 標記文章
    D = 2
    # 刪除標記文章
    DeleteD = 3
    # M 起來
    M = 4
    # 待證實文章
    Unconfirmed = 5

    MinValue = S
    MaxValue = Unconfirmed


class FavouriteBoard:
    def __init__(self, Board, Type, BoardTitle):
        self.Board = ParseParameter(str, Board)
        self.Type = ParseParameter(str, Type)
        self.BoardTitle = ParseParameter(str, BoardTitle)

    def getBoard(self):
        return self.Board

    def getType(self):
        return self.Type

    def getBoardTitle(self):
        return self.BoardTitle


class BoardInfo:
    def __init__(
        self,
        Board,
        OnlineUser,
        ChineseDes=None,
        Moderators=None,
        OpenState=None,
        IntoTopTenWhenHide=None,
        NonBoardMembersPost=None,
        ReplyPost=None,
        SelfDelPost=None,
        PushPost=None,
        BooPost=None,
        FastPush=None,
        MinInterval=None,
        PushRecordIP=None,
        PushAligned=None,
        ModeratorCanDelIllegalContent=None,
        TranPostAutoRecordedAndRequirePostPermissions=None,
        CoolMode=None,
        Require18=None,
        RequireLoginTime=None,
        RequireIllegalPost=None,
    ):
        self.Board = ParseParameter(str, Board)
        self.OnlineUser = ParseParameter(int, OnlineUser)
        self.ChineseDes = ParseParameter(str, ChineseDes)
        self.Moderators = ParseParameter(list, Moderators)
        self.OpenState = ParseParameter(bool, OpenState)
        self.IntoTopTenWhenHide = ParseParameter(bool, IntoTopTenWhenHide)
        self.NonBoardMembersPost = ParseParameter(bool, NonBoardMembersPost)
        self.ReplyPost = ParseParameter(bool, ReplyPost)
        self.SelfDelPost = ParseParameter(bool, SelfDelPost)
        self.PushPost = ParseParameter(bool, PushPost)
        self.BooPost = ParseParameter(bool, BooPost)
        self.FastPush = ParseParameter(bool, FastPush)
        self.MinInterval = ParseParameter(int, MinInterval)
        self.PushRecordIP = ParseParameter(bool, PushRecordIP)
        self.PushAligned = ParseParameter(bool, PushAligned)
        self.ModeratorCanDelIllegalContent = ParseParameter(
            bool, ModeratorCanDelIllegalContent)
        self.TranPostAutoRecordedAndRequirePostPermissions = ParseParameter(
            bool, TranPostAutoRecordedAndRequirePostPermissions)
        self.CoolMode = ParseParameter(bool, CoolMode)
        self.Require18 = ParseParameter(bool, Require18)
        self.RequireLoginTime = ParseParameter(int, RequireLoginTime)
        self.RequireIllegalPost = ParseParameter(int, RequireIllegalPost)

    def getBoard(self):
        return self.Board

    def getOnlineUser(self):
        return self.OnlineUser

    def getChineseDes(self):
        return self.ChineseDes

    def getModerators(self):
        return self.Moderators

    def isOpen(self):
        return self.OpenState

    def canIntoTopTenWhenHide(self):
        return self.IntoTopTenWhenHide

    def canNonBoardMembersPost(self):
        return self.NonBoardMembersPost

    def canReplyPost(self):
        return self.ReplyPost

    def canSelfDelPost(self):
        return self.SelfDelPost

    def canPushPost(self):
        return self.PushPost

    def canBooPost(self):
        return self.BooPost

    def canFastPush(self):
        return self.FastPush

    def getMinInterval(self):
        return self.MinInterval

    def isPushRecordIP(self):
        return self.PushRecordIP

    def isPushAligned(self):
        return self.PushAligned

    def canModeratorCanDelIllegalContent(self):
        return self.ModeratorCanDelIllegalContent

    def isTranPostAutoRecordedAndRequirePostPermissions(self):
        return self.TranPostAutoRecordedAndRequirePostPermissions

    def isCoolMode(self):
        return self.CoolMode

    def isRequire18(self):
        return self.Require18

    def getRequireLoginTime(self):
        return self.RequireLoginTime

    def getRequireIllegalPost(self):
        return self.RequireIllegalPost
