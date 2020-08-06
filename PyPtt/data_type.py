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


class post_search_type:
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

    min_value = NOPE
    max_value = MONEY


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


class PushInfo:
    def __init__(self, push_type, author, push_content, push_ip, push_time):
        self.type = parse_para(int, push_type)
        self.author = parse_para(str, author)
        self.content = parse_para(str, push_content)
        self.ip = parse_para(str, push_ip)
        self.time = parse_para(str, push_time)


class post_delete_status:
    NOT_DELETED: int = 0
    AUTHOR: int = 1
    MODERATOR: int = 2
    UNKNOWN: int = 3

    min_value = NOT_DELETED
    max_value = UNKNOWN


class PostInfo:
    def __init__(
            self,
            board=None,
            aid=None,
            index=None,
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
        self.board: str = parse_para(str, board)
        self.aid: str = parse_para(str, aid)
        self.index: int = parse_para(int, index)
        self.author: str = parse_para(str, author)
        self.date: str = parse_para(str, date)
        self.title: str = parse_para(str, title)
        self.content: str = parse_para(str, content)
        self.money: int = parse_para(int, money)
        self.web_url: str = parse_para(str, web_url)
        self.ip: str = parse_para(str, ip)
        self.push_list: list = parse_para(list, push_list)
        self.delete_status: int = parse_para(int, delete_status)
        self.list_date: str = parse_para(str, list_date)
        self.is_control_code: bool = parse_para(bool, control_code)
        self.pass_format_check: bool = parse_para(bool, format_check)
        self.location: str = parse_para(str, location)
        self.push_number: str = parse_para(str, push_number)
        self.is_lock: bool = parse_para(bool, lock)
        self.origin_post: str = parse_para(str, origin_post)
        self.is_unconfirmed: bool = parse_para(bool, unconfirmed)


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


class index_type:
    # 板
    BBS: int = 1
    # 信箱
    MAIL: int = 2
    #
    WEB: int = 3

    min_value = BBS
    max_value = WEB


class crawl_type:
    # BBS版本
    BBS: int = 1
    # 網頁版本
    WEB: int = 2

    min_value = BBS
    max_value = WEB


class host_type:
    # 批踢踢萬
    PTT1: int = 1
    # 批踢踢兔
    PTT2: int = 2
    # 本機測試用
    LOCALHOST: int = 3

    min_value = PTT1
    max_value = LOCALHOST


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


class BoardInfo:
    def __init__(
            self,
            board,
            online_user,
            chinese_des=None,
            moderators=None,
            open_status=None,
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
            require_illegal_post=None,
            post_kind=None):
        self.board: str = parse_para(str, board)
        self.online_user: int = parse_para(int, online_user)
        self.chinese_des: str = parse_para(str, chinese_des)
        self.moderators: list = parse_para(list, moderators)
        self.is_open: bool = parse_para(bool, open_status)
        self.is_into_top_ten_when_hide: bool = parse_para(bool, into_top_ten_when_hide)
        self.can_non_board_members_post: bool = parse_para(bool, non_board_members_post)
        self.can_reply_post: bool = parse_para(bool, reply_post)
        self.can_self_del_post: bool = parse_para(bool, self_del_post)
        self.can_push_post: bool = parse_para(bool, push_post)
        self.can_boo_post: bool = parse_para(bool, boo_post)
        self.can_fast_push: bool = parse_para(bool, fast_push)
        self.min_interval: int = parse_para(int, min_interval)
        self.is_push_record_ip: bool = parse_para(bool, push_record_ip)
        self.is_push_aligned: bool = parse_para(bool, push_aligned)
        self.can_moderator_del_illegal_content: bool = parse_para(
            bool, moderator_can_del_illegal_content)
        self.is_tran_post_auto_recorded_and_require_post_permissions: bool = parse_para(
            bool, tran_post_auto_recorded_and_require_post_permissions)
        self.is_cool_mode: bool = parse_para(bool, cool_mode)
        self.is_require18: bool = parse_para(bool, require18)
        self.require_login_time: int = parse_para(int, require_login_time)
        self.require_illegal_post: int = parse_para(int, require_illegal_post)
        self.post_kind: list = parse_para(list, post_kind)
