import inspect
import sys
from enum import auto

from AutoStrEnum import AutoStrEnum


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


class SearchType(AutoStrEnum):
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


class ReplyTo(AutoStrEnum):
    # 回文類型

    BOARD = auto()
    MAIL = auto()
    BOARD_MAIL = auto()


class CommentType(AutoStrEnum):
    PUSH = auto()
    BOO = auto()
    ARROW = auto()


class UserField(AutoStrEnum):
    ptt_id = auto()
    money = auto()
    login_time = auto()
    legal_post = auto()
    illegal_post = auto()
    status = auto()
    mail = auto()
    last_login = auto()
    last_ip = auto()
    five_chess = auto()
    chess = auto()
    signature_file = auto()


class CommentField(AutoStrEnum):
    type = auto()
    author = auto()
    content = auto()
    ip = auto()
    time = auto()


class PostStatus(AutoStrEnum):
    exist = auto()
    deleted_by_author = auto()
    deleted_by_moderator = auto()
    deleted_by_unknown = auto()


class PostField(AutoStrEnum):
    board = auto()
    aid = auto()
    index = auto()
    author = auto()
    date = auto()
    title = auto()
    content = auto()
    money = auto()
    url = auto()
    ip = auto()
    push_list = auto()
    delete_status = auto()
    list_date = auto()
    has_control_code = auto()
    pass_format_check = auto()
    location = auto()
    push_number = auto()
    is_lock = auto()
    full_content = auto()
    is_unconfirmed = auto()


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


class NewIndex(AutoStrEnum):
    # 看板
    BBS = auto()
    # 信箱
    MAIL = auto()
    # 網頁，尚不支援
    # WEB = auto()


class HOST(AutoStrEnum):
    # 批踢踢萬
    PTT1 = auto()
    # 批踢踢兔
    PTT2 = auto()
    # 本機測試用
    LOCALHOST = auto()


class MarkType(AutoStrEnum):
    # s 文章
    S = auto()
    # 標記文章
    D = auto()
    # 刪除標記文章
    DeleteD = auto()
    # M 起來
    M = auto()
    # 待證實文章
    UNCONFIRMED = auto()


class FavouriteBoard:
    def __init__(self, board, board_type, board_title):
        self.board: str = parse_para(str, board)
        self.type: str = parse_para(str, board_type)
        self.title: str = parse_para(str, board_title)


class BoardField(AutoStrEnum):
    board = auto()
    online_user = auto()
    chinese_des = auto()
    moderators = auto()
    open_status = auto()
    into_top_ten_when_hide = auto()
    non_board_members_post = auto()
    reply_post = auto()
    self_del_post = auto()
    push_post = auto()
    boo_post = auto()
    fast_push = auto()
    min_interval = auto()
    push_record_ip = auto()
    push_aligned = auto()
    moderator_can_del_illegal_content = auto()
    tran_post_auto_recorded_and_require_post_permissions = auto()
    cool_mode = auto()
    require18 = auto()
    require_login_time = auto()
    require_illegal_post = auto()
    post_kind = auto()
    kind_list = auto()


class Compare(AutoStrEnum):
    BIGGER = auto()
    SAME = auto()
    SMALLER = auto()
    UNKNOWN = auto()


class_list = inspect.getmembers(sys.modules['PyPtt.data_type'], inspect.isclass)
class_list = set([name[0] for name in class_list])