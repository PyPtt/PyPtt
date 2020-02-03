

def parse_para(value_type, parameter):
    if parameter is None:
        return None
    result = value_type(parameter)
    if isinstance(result, str):
        result = result.rstrip()
    return result


class CallStatus:
    # 呼叫器狀態

    # 打開
    ON: int = 0
    # 拔掉
    UNPLUG: int = 1
    # 防水
    WATERPROOF: int = 2
    # 好友
    FRIEND: int = 3
    # 關掉
    OFF: int = 4

    MinValue = ON
    MaxValue = OFF


class PostSearchType:
    # 文章搜尋類型

    NOPE: int = 0
    # 搜尋關鍵字    / ?
    KEYWORD: int = 1
    # 搜尋作者      a
    AUTHOR: int = 2
    # 搜尋推文數    Z
    PUSH: int = 3
    # 搜尋標記      G
    MARK: int = 4
    # 搜尋稿酬      A
    MONEY: int = 5

    MinValue = NOPE
    MaxValue = MONEY


class WaterBallType:
    # 水球接收狀態

    # 收到水球
    CATCH: int = 1
    # 收到水球
    SEND: int = 2

    MinValue = CATCH
    MaxValue = SEND


class WaterBallOperateType:
    # 清除水球類型

    CLEAR: int = 1
    MAIL: int = 2
    NOTHING: int = 3

    MinValue = CLEAR
    MaxValue = NOTHING


class FriendListType:
    # 名單類型

    GoodFriend = 1
    BadGuy = 2
    SuperFriend = 3
    loginNotification = 4
    OtherSpecial = 5

    MinValue = GoodFriend
    MaxValue = OtherSpecial


class ReplyType:
    # 回文類型

    BOARD: int = 1
    MAIL: int = 2
    BOARD_MAIL: int = 3

    MinValue = BOARD
    MaxValue = BOARD_MAIL


class PushType:
    PUSH: int = 1
    BOO: int = 2
    ARROW: int = 3

    MinValue = PUSH
    MaxValue = ARROW


class MailInformation:
    def __init__(self, author, title, date, content, ip):
        self.author = parse_para(str, author)
        self.title = parse_para(str, title)
        self.date = parse_para(str, date)
        self.content = parse_para(str, content)
        self.ip = parse_para(str, ip)


class UserInfo:
    def __init__(
            self,
            pttid,
            money,
            login_time,
            legal_post,
            illegal_post,
            state,
            mail,
            last_login,
            last_ip,
            five_chess,
            chess,
            signature_file):
        self.ID = parse_para(str, pttid)
        self.Money = parse_para(str, money)
        self.loginTime = parse_para(int, login_time)
        self.LegalPost = parse_para(int, legal_post)
        self.IllegalPost = parse_para(int, illegal_post)
        self.State = parse_para(str, state)
        self.Mail = parse_para(str, mail)
        self.Lastlogin = parse_para(str, last_login)
        self.LastIP = parse_para(str, last_ip)
        self.FiveChess = parse_para(str, five_chess)
        self.Chess = parse_para(str, chess)
        self.SignatureFile = parse_para(str, signature_file)


class PushInfo:
    def __init__(self, push_type, author, push_content, push_ip, push_time):
        self.Type = parse_para(int, push_type)
        self.Author = parse_para(str, author)
        self.Content = parse_para(str, push_content)
        self.IP = parse_para(str, push_ip)
        self.Time = parse_para(str, push_time)

    def get_type(self):
        return self.Type

    def get_author(self):
        return self.Author

    def get_content(self):
        return self.Content

    def get_ip(self):
        return self.IP

    def get_time(self):
        return self.Time


class PostDeleteStatus:
    NotDeleted = 0
    ByAuthor = 1
    ByModerator = 2
    ByUnknown = 3

    MinValue = NotDeleted
    MaxValue = ByUnknown


class PostInfo:
    def __init__(
            self,
            board=None,
            aid=None,
            author=None,
            date=None,
            title=None,
            web_url=None,
            money=None,
            content=None,
            ip=None,
            push_list=None,
            list_date=None,
            delete_status=0,
            control_code=False,
            format_check=False,
            location=None,
            push_number=None,
            lock=False,
            origin_post=None,
            unconfirmed=False):
        self.Board = parse_para(str, board)
        self.AID = parse_para(str, aid)
        self.Author = parse_para(str, author)
        self.Date = parse_para(str, date)
        self.Title = parse_para(str, title)
        self.Content = parse_para(str, content)
        self.Money = parse_para(int, money)
        self.WebUrl = parse_para(str, web_url)
        self.IP = parse_para(str, ip)
        self.PushList = push_list
        self.DeleteStatus = delete_status
        self.ListDate = parse_para(str, list_date)
        self.ControlCode = control_code
        self.FormatCheck = format_check
        self.Location = parse_para(str, location)
        self.PushNumber = parse_para(str, push_number)
        self.Lock = lock
        self.OriginPost = parse_para(str, origin_post)
        self.Unconfirmed = parse_para(bool, unconfirmed)

    def get_board(self):
        return self.Board

    def get_aid(self):
        return self.AID

    def get_author(self):
        return self.Author

    def get_date(self):
        return self.Date

    def get_title(self):
        return self.Title

    def get_content(self):
        return self.Content

    def get_money(self):
        return self.Money

    def get_web_url(self):
        return self.WebUrl

    def get_ip(self):
        return self.IP

    def get_push_list(self):
        return self.PushList

    def get_delete_status(self):
        return self.DeleteStatus

    def get_list_date(self):
        return self.ListDate

    def has_control_code(self):
        return self.ControlCode

    def is_format_check(self):
        return self.FormatCheck

    def get_location(self):
        return self.Location

    def get_push_number(self):
        return self.PushNumber

    def is_lock(self):
        return self.Lock

    def get_origin_post(self):
        return self.OriginPost

    def is_unconfirmed(self):
        return self.Unconfirmed


class WaterBallInfo:
    def __init__(self, waterball_type, target, content, date):
        self.Type = parse_para(int, waterball_type)
        self.Target = parse_para(str, target)
        self.Content = parse_para(str, content)
        self.Date = parse_para(str, date)

    def get_target(self):
        return self.Target

    def get_content(self):
        return self.Content

    def get_date(self):
        return self.Date

    def get_type(self):
        return self.Type


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


class host:
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
    def __init__(self, board, board_type, board_title):
        self.Board = parse_para(str, board)
        self.Type = parse_para(str, board_type)
        self.BoardTitle = parse_para(str, board_title)

    def get_board(self):
        return self.Board

    def get_type(self):
        return self.Type

    def get_board_title(self):
        return self.BoardTitle


class BoardInfo:
    def __init__(
            self,
            board,
            online_user,
            chinese_des=None,
            moderators=None,
            open_state=None,
            into_top_ten_when_hide=None,
            non_board_members_post=None,
            reply_post=None,
            self_del_post=None,
            push_post=None,
            boo_post=None,
            fast_push=None,
            min_interval=None,
            push_record_ip=None,
            push_aligned=None,
            moderator_can_del_illegal_content=None,
            tran_post_auto_recorded_and_require_post_permissions=None,
            cool_mode=None,
            require18=None,
            require_login_time=None,
            require_illegal_post=None):
        self.Board = parse_para(str, board)
        self.OnlineUser = parse_para(int, online_user)
        self.ChineseDes = parse_para(str, chinese_des)
        self.Moderators = parse_para(list, moderators)
        self.OpenState = parse_para(bool, open_state)
        self.IntoTopTenWhenHide = parse_para(bool, into_top_ten_when_hide)
        self.NonBoardMembersPost = parse_para(bool, non_board_members_post)
        self.ReplyPost = parse_para(bool, reply_post)
        self.SelfDelPost = parse_para(bool, self_del_post)
        self.PushPost = parse_para(bool, push_post)
        self.BooPost = parse_para(bool, boo_post)
        self.FastPush = parse_para(bool, fast_push)
        self.MinInterval = parse_para(int, min_interval)
        self.PushRecordIP = parse_para(bool, push_record_ip)
        self.PushAligned = parse_para(bool, push_aligned)
        self.ModeratorCanDelIllegalContent = parse_para(
            bool, moderator_can_del_illegal_content)
        self.TranPostAutoRecordedAndRequirePostPermissions = parse_para(
            bool, tran_post_auto_recorded_and_require_post_permissions)
        self.CoolMode = parse_para(bool, cool_mode)
        self.Require18 = parse_para(bool, require18)
        self.RequireloginTime = parse_para(int, require_login_time)
        self.RequireIllegalPost = parse_para(int, require_illegal_post)

    def get_board(self):
        return self.Board

    def get_online_user(self):
        return self.OnlineUser

    def get_chinese_des(self):
        return self.ChineseDes

    def get_moderators(self):
        return self.Moderators

    def is_open(self):
        return self.OpenState

    def can_into_top_ten_when_hide(self):
        return self.IntoTopTenWhenHide

    def can_non_board_members_post(self):
        return self.NonBoardMembersPost

    def can_reply_post(self):
        return self.ReplyPost

    def can_self_del_post(self):
        return self.SelfDelPost

    def can_push_post(self):
        return self.PushPost

    def can_boo_post(self):
        return self.BooPost

    def can_fast_push(self):
        return self.FastPush

    def get_min_interval(self):
        return self.MinInterval

    def is_push_record_ip(self):
        return self.PushRecordIP

    def is_push_aligned(self):
        return self.PushAligned

    def can_moderator_can_del_illegal_content(self):
        return self.ModeratorCanDelIllegalContent

    def is_tran_post_auto_recorded_and_require_post_permissions(self):
        return self.TranPostAutoRecordedAndRequirePostPermissions

    def is_cool_mode(self):
        return self.CoolMode

    def is_require18(self):
        return self.Require18

    def get_require_login_time(self):
        return self.RequireloginTime

    def get_require_illegal_post(self):
        return self.RequireIllegalPost
