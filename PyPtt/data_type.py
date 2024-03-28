import time
from enum import auto

from AutoStrEnum import AutoStrEnum


class Language:
    MANDARIN = 'zh_TW'
    ENGLISH = 'en_US'


class ConnectMode(AutoStrEnum):
    TELNET = auto()
    WEBSOCKETS = auto()


class SearchType(AutoStrEnum):
    """文章搜尋類型"""

    NOPE = auto()
    # 搜尋關鍵字    / ?
    KEYWORD = auto()
    # 搜尋作者      a
    AUTHOR = auto()
    # 搜尋推文數    Z
    COMMENT = auto()
    # 搜尋標記      G
    MARK = auto()
    # 搜尋稿酬      A
    MONEY = auto()


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
    login_count = auto()
    account_verified = auto()
    legal_post = auto()
    illegal_post = auto()
    activity = auto()
    mail = auto()
    last_login_date = auto()
    last_login_ip = auto()
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
    EXISTS = auto()
    DELETED_BY_AUTHOR = auto()
    DELETED_BY_MODERATOR = auto()
    DELETED_BY_UNKNOWN = auto()


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
    comments = auto()
    post_status = auto()
    list_date = auto()
    has_control_code = auto()
    pass_format_check = auto()
    location = auto()
    push_number = auto()
    is_lock = auto()
    full_content = auto()
    is_unconfirmed = auto()


# class WaterballInfo:
#     def __init__(self, waterball_type, target, content, date):
#         self.type: int = parse_para(int, waterball_type)
#         self.target: str = parse_para(str, target)
#         self.content: str = parse_para(str, content)
#         self.date: str = parse_para(str, date)


class Cursor:
    # 舊式游標
    OLD: str = '●'
    # 新式游標
    NEW: str = '>'


class NewIndex(AutoStrEnum):
    # 看板
    BOARD = auto()
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
    DELETE_D = auto()
    # M 起來
    M = auto()
    # 待證實文章
    UNCONFIRMED = auto()


class FavouriteBoardField(AutoStrEnum):
    board = auto()
    type = auto()
    title = auto()


class MailField(AutoStrEnum):
    origin_mail = auto()
    author = auto()
    title = auto()
    date = auto()
    content = auto()
    ip = auto()
    location = auto()
    is_red_envelope = auto()


class BoardField(AutoStrEnum):
    board = auto()
    online_user = auto()
    mandarin_des = auto()
    moderators = auto()
    open_status = auto()
    into_top_ten_when_hide = auto()
    can_non_board_members_post = auto()
    can_reply_post = auto()
    self_del_post = auto()
    can_comment_post = auto()
    can_boo_post = auto()
    can_fast_push = auto()
    min_interval_between_comments = auto()
    is_comment_record_ip = auto()
    is_comment_aligned = auto()
    can_moderators_del_illegal_content = auto()
    does_tran_post_auto_recorded_and_require_post_permissions = auto()
    is_cool_mode = auto()
    is_require18 = auto()
    require_login_time = auto()
    require_illegal_post = auto()
    # post_kind = auto()
    post_kind_list = auto()


class Compare(AutoStrEnum):
    BIGGER = auto()
    SAME = auto()
    SMALLER = auto()
    UNKNOWN = auto()


class TimedDict:
    def __init__(self, timeout: int = 0):
        self.timeout = timeout
        self.data = {}
        self.timestamps = {}

    def __setitem__(self, key, value):
        self.data[key] = value
        self.timestamps[key] = time.time()

    def __getitem__(self, key):
        if key not in self.data:
            raise KeyError(key)
        timestamp = self.timestamps[key]
        if time.time() - timestamp > self.timeout > 0:
            del self.data[key]
            del self.timestamps[key]
            raise KeyError(key)
        return self.data[key]

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True

    def __len__(self):
        self.cleanup()
        return len(self.data)

    def cleanup(self):
        if self.timeout == 0:
            return

        now = time.time()
        to_remove = [key for key, timestamp in self.timestamps.items()
                     if now - timestamp > self.timeout > 0]
        for key in to_remove:
            del self.data[key]
            del self.timestamps[key]
