from enum import auto, IntEnum

from PyPtt.lib_util import AutoName


def parse_para(value_type, parameter):
    if parameter is None:
        if value_type is list:
            return []
        return None
    result = value_type(parameter)
    if isinstance(result, str):
        result = result.rstrip()
    return result


class call_status:
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

    min_value = ON
    max_value = OFF


class SearchType(IntEnum):
    """文章搜尋類型"""

    NOPE = auto()
    # 搜尋關鍵字    / ?
    KEYWORD = auto()
    # 搜尋作者      a
    AUTHOR = auto()
    # 搜尋推文數    Z
    PUSH = auto()
    # 搜尋標記      G
    MARK = auto()
    # 搜尋稿酬      A
    MONEY = auto()


# class MailSearchType(IntEnum):
#     """信件搜尋類型"""
#
#     NOPE = auto()
#     # 搜尋關鍵字    / ?
#     KEYWORD = auto()
#     # 搜尋作者      a
#     AUTHOR = auto()
#     # 搜尋標記      G
#     MARK = auto()


class waterball_type:
    # 水球接收狀態

    # 收到水球
    CATCH: int = 1
    # 收到水球
    SEND: int = 2

    min_value = CATCH
    max_value = SEND


class waterball_operate_type:
    # 清除水球類型

    CLEAR: int = 1
    MAIL: int = 2
    NOTHING: int = 3

    min_value = CLEAR
    max_value = NOTHING


# class FriendListType:
#     # 名單類型
#
#     GoodFriend = 1
#     BadGuy = 2
#     SuperFriend = 3
#     loginNotification = 4
#     OtherSpecial = 5
#
#     min_value = GoodFriend
#     max_value = OtherSpecial


class reply_type:
    # 回文類型

    BOARD: int = 1
    MAIL: int = 2
    BOARD_MAIL: int = 3

    min_value = BOARD
    max_value = BOARD_MAIL


class push_type:
    PUSH: int = 1
    BOO: int = 2
    ARROW: int = 3

    min_value = PUSH
    max_value = ARROW


class MailInfo:
    def __init__(
            self,
            origin_mail: str = None,
            author: str = None,
            title: str = None,
            date: str = None,
            content: str = None,
            ip: str = None,
            location: str = None,
            is_red_envelope: bool = False):
        self.origin_mail: str = parse_para(str, origin_mail)
        self.author: str = parse_para(str, author)
        self.title: str = parse_para(str, title)
        self.date: str = parse_para(str, date)
        self.content: str = parse_para(str, content)
        self.ip: str = parse_para(str, ip)
        self.location: str = parse_para(str, location)
        self.is_red_envelope = parse_para(bool, is_red_envelope)


class UserInfo:
    def __init__(
            self,
            ptt_id,
            money,
            login_time,
            legal_post,
            illegal_post,
            status,
            mail,
            last_login,
            last_ip,
            five_chess,
            chess,
            signature_file):
        self.id: str = parse_para(str, ptt_id)
        self.money: str = parse_para(str, money)
        self.login_time: int = parse_para(int, login_time)
        self.legal_post: int = parse_para(int, legal_post)
        self.illegal_post: int = parse_para(int, illegal_post)
        self.status: str = parse_para(str, status)
        self.mail_status: str = parse_para(str, mail)
        self.last_login: str = parse_para(str, last_login)
        self.last_ip: str = parse_para(str, last_ip)
        self.five_chess: str = parse_para(str, five_chess)
        self.chess: str = parse_para(str, chess)
        self.signature_file: str = parse_para(str, signature_file)


class User:
    ptt_id = 'ptt_id',
    money = 'money',
    login_time = 'login_time',
    legal_post = 'legal_post',
    illegal_post = 'illegal_post',
    status = 'status',
    mail = 'mail',
    last_login = 'last_login',
    last_ip = 'last_ip',
    five_chess = 'five_chess',
    chess = 'chess',
    signature_file = 'signature_file'


class Comment:
    type = 'type'
    author = 'author'
    content = 'content'
    ip = 'ip'
    time = 'time'


class ArticleDelStatus:
    exist = 'exist'
    deleted_by_author = 'deleted_by_author'
    deleted_by_moderator = 'deleted_by_moderator'
    deleted_by_unknown = 'deleted_by_unknown'


class Article:
    board = 'board'
    aid = 'aid'
    index = 'index'
    author = 'author'
    date = 'date'
    title = 'title'
    content = 'content'
    money = 'money'
    url = 'url'
    ip = 'ip'
    push_list = 'push_list'
    delete_status = 'delete_status'
    list_date = 'list_date'
    has_control_code = 'has_control_code'
    pass_format_check = 'pass_format_check'
    location = 'location'
    push_number = 'push_number'
    is_lock = 'is_lock'
    full_content = 'full_content'
    is_unconfirmed = 'is_unconfirmed'


class WaterballInfo:
    def __init__(self, waterball_type, target, content, date):
        self.type: int = parse_para(int, waterball_type)
        self.target: str = parse_para(str, target)
        self.content: str = parse_para(str, content)
        self.date: str = parse_para(str, date)


class Cursor:
    # 舊式游標
    OLD: str = '●'
    # 新式游標
    NEW: str = '>'


class NewIndex(IntEnum):
    # 看板
    BBS = auto()
    # 信箱
    MAIL = auto()
    # 網頁，尚不支援
    # WEB = auto()


class crawl_type:
    # BBS版本
    BBS: int = 1
    # 網頁版本
    WEB: int = 2

    min_value = BBS
    max_value = BBS


class HOST(AutoName):
    # 批踢踢萬
    PTT1 = auto()
    # 批踢踢兔
    PTT2 = auto()
    # 本機測試用
    LOCALHOST = auto()


class mark_type:
    # s 文章
    S: int = 1
    # 標記文章
    D: int = 2
    # 刪除標記文章
    DeleteD: int = 3
    # M 起來
    M: int = 4
    # 待證實文章
    UNCONFIRMED: int = 5

    min_value = S
    max_value = UNCONFIRMED


class FavouriteBoard:
    def __init__(self, board, board_type, board_title):
        self.board: str = parse_para(str, board)
        self.type: str = parse_para(str, board_type)
        self.title: str = parse_para(str, board_title)


class Board:
    board = 'board'
    online_user = 'online_user'
    chinese_des = 'chinese_des'
    moderators = 'moderators'
    open_status = 'open_status'
    into_top_ten_when_hide = 'into_top_ten_when_hide'
    non_board_members_post = 'non_board_members_post'
    reply_post = 'reply_post'
    self_del_post = 'self_del_post'
    push_post = 'push_post'
    boo_post = 'boo_post'
    fast_push = 'fast_push'
    min_interval = 'min_interval'
    push_record_ip = 'push_record_ip'
    push_aligned = 'push_aligned'
    moderator_can_del_illegal_content = 'moderator_can_del_illegal_content'
    tran_post_auto_recorded_and_require_post_permissions = 'tran_post_auto_recorded_and_require_post_permissions'
    cool_mode = 'cool_mode'
    require18 = 'require18'
    require_login_time = 'require_login_time'
    require_illegal_post = 'require_illegal_post'
    post_kind = 'post_kind'
    kind_list = 'kind_list'