Search.setIndex({"docnames": ["api/bucket", "api/change_pw", "api/comment", "api/del_mail", "api/del_post", "api/get_aid_from_url", "api/get_all_boards", "api/get_board_info", "api/get_bottom_post_list", "api/get_favourite_boards", "api/get_mail", "api/get_newest_index", "api/get_post", "api/get_time", "api/get_user", "api/give_money", "api/index", "api/init", "api/login_logout", "api/mail", "api/mark_post", "api/post", "api/reply_post", "api/search_user", "api/set_board_title", "changelog", "dev", "docker", "examples", "exceptions", "faq", "index", "install", "roadmap", "service", "type"], "filenames": ["api/bucket.rst", "api/change_pw.rst", "api/comment.rst", "api/del_mail.rst", "api/del_post.rst", "api/get_aid_from_url.rst", "api/get_all_boards.rst", "api/get_board_info.rst", "api/get_bottom_post_list.rst", "api/get_favourite_boards.rst", "api/get_mail.rst", "api/get_newest_index.rst", "api/get_post.rst", "api/get_time.rst", "api/get_user.rst", "api/give_money.rst", "api/index.rst", "api/init.rst", "api/login_logout.rst", "api/mail.rst", "api/mark_post.rst", "api/post.rst", "api/reply_post.rst", "api/search_user.rst", "api/set_board_title.rst", "changelog.rst", "dev.rst", "docker.rst", "examples.rst", "exceptions.rst", "faq.rst", "index.rst", "install.rst", "roadmap.rst", "service.rst", "type.rst"], "titles": ["bucket", "change_pw", "comment", "del_mail", "del_post", "get_aid_from_url", "get_all_boards", "get_board_info", "get_bottom_post_list", "get_favourite_boards", "get_mail", "get_newest_index", "get_post", "get_time", "get_user", "give_money", "APIs", "init", "login, logout", "mail", "mark_post", "post", "reply_post", "search_user", "set_board_title", "\u66f4\u65b0\u65e5\u8a8c", "Development", "Docker Image", "\u4f7f\u7528\u7bc4\u4f8b", "\u4f8b\u5916", "FAQ", "PyPtt", "\u5b89\u88dd PyPtt", "\u958b\u767c", "Service", "\u53c3\u6578\u578b\u614b"], "terms": {"pyptt": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 33, 34, 35], "api": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 27, 28, 30, 31, 32, 33, 34], "self": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 34], "board": [0, 2, 4, 5, 7, 8, 11, 12, 20, 21, 22, 24, 27, 28, 34, 35], "str": [0, 1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 24], "bucket_day": 0, "int": [0, 2, 3, 4, 10, 11, 12, 15, 17, 19, 20, 21, 22, 23], "reason": 0, "ptt_id": [0, 15, 18, 19, 23, 27, 34, 35], "none": [0, 1, 2, 3, 4, 10, 11, 12, 13, 15, 17, 18, 19, 20, 21, 22, 23, 24, 28, 34], "ptt": [0, 5, 13, 15, 17, 18, 19, 23, 28, 30, 31, 33, 34, 35], "id": [0, 14, 15, 18, 19, 23, 34, 35], "requirelogin": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 14, 15, 19, 20, 21, 22, 23, 24, 29], "unregisteredus": [0, 2, 3, 4, 15, 19, 20, 21, 23, 24, 29], "nosuchboard": [0, 2, 4, 7, 8, 11, 12, 20, 21, 22, 24, 29], "nosuchus": [0, 14, 15, 19, 29], "needmoderatorpermiss": [0, 20, 24, 29], "import": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 27, 28, 30, 34], "ptt_bot": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 28, 30], "tri": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 24, 28, 29, 34], "login": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 27, 28, 34], "test": [0, 2, 7, 20, 21, 22, 24, 26, 27, 28], "do": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 24, 28], "someth": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 24, 28], "final": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 24, 28, 34], "logout": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 27, 28, 34], "new_password": 1, "setcontactmailfirst": [1, 29], "wrongpassword": [1, 29], "123456": 1, "comment_typ": 2, "commenttyp": 2, "content": [2, 19, 21, 22, 27, 28, 35], "aid": [2, 4, 5, 12, 20, 22, 35], "index": [2, 3, 4, 10, 11, 12, 20, 22, 26, 28, 35], "nosuchpost": [2, 4, 20, 22, 29], "nopermiss": [2, 4, 7, 10, 21, 22, 29], "nofastcom": [2, 29], "push": [2, 26, 35], "by": 2, "123": [2, 20, 22, 27], "17mrayxf": 2, "mailboxful": [3, 29], "get_newest_index": [3, 10, 16, 27, 28, 34], "python": [4, 5, 8, 11, 12, 26, 28, 30, 31, 34], "1tjh_xy0": [4, 12], "url": [5, 34, 35], "tupl": [5, 11, 12], "https": [5, 27, 34], "www": [5, 34], "cc": [5, 27, 34], "bbs": [5, 34], "1565335521": [5, 34], "880": [5, 34], "html": [5, 26, 27, 34], "list": [6, 8, 9, 10, 11, 12, 23], "board_list": 6, "get_post_typ": 7, "bool": [7, 12, 17, 18, 19], "fals": [7, 12, 18, 28], "dict": [7, 9, 10, 12, 14, 34], "boardfield": 7, "board_info": 7, "post": [8, 16, 27, 28], "postfield": [8, 12, 28], "bottom_post_list": 8, "favouriteboardfield": 9, "favourite_board": 9, "search_typ": [10, 11, 12, 20], "searchtyp": [10, 11, 12, 20], "search_condit": [10, 11, 12, 20], "search_list": [10, 11, 12], "mailfield": 10, "nosuchmail": [10, 29], "mail": [10, 11, 16, 35], "index_typ": [11, 27, 34], "newindex": [11, 27, 34], "ani": 11, "get": [11, 27], "newest": 11, "of": [11, 32], "newest_index": [11, 28], "keyword": [11, 12, 35], "queri": 12, "post_info": [12, 28], "time": [13, 28, 35], "user_id": 14, "user_info": 14, "codingman": [14, 15, 19, 31], "money": [15, 35], "red_bag_titl": 15, "red_bag_cont": 15, "nomoney": [15, 29], "100": 15, "or": [15, 33], "ptt2": [16, 35], "init": 16, "__init__": [16, 17, 34], "get_post": [16, 28], "reply_post": 16, "del_post": 16, "comment": [16, 35], "get_mail": 16, "del_mail": 16, "give_money": 16, "get_us": 16, "search_us": 16, "change_pw": 16, "get_tim": [16, 27, 34], "get_all_board": 16, "get_favourite_board": 16, "get_board_info": 16, "get_aid_from_url": [16, 34], "get_bottom_post_list": 16, "set_board_titl": 16, "mark_post": 16, "bucket": 16, "kwarg": 17, "languag": [17, 34], "mandarin": [17, 35], "log_level": [17, 30], "loglevel": [17, 30], "info": 17, "screen_timeout": 17, "screen_long_timeout": 17, "10": [17, 30, 34], "screen_post_timeout": 17, "60": [17, 28], "connect_mod": 17, "connectmod": 17, "websocket": [17, 32, 33, 35], "logger_callback": 17, "callabl": 17, "callback": 17, "port": 17, "23": 17, "host": [17, 29], "ptt1": [17, 35], "check_upd": 17, "true": [17, 18, 19, 28], "english": [17, 34, 35], "debug": [17, 30], "ptt_pw": [18, 27, 34], "kick_other_sess": [18, 28], "session": 18, "loginerror": [18, 28, 29], "wrongidorpassword": [18, 28, 29], "onlysecureconnect": [18, 29], "resetyourcontactemail": [18, 29], "except": [18, 28, 29], "print": [18, 27, 28, 34], "titl": [19, 21, 27, 28, 35], "sign_fil": [19, 21, 22, 28], "backup": 19, "mark_typ": 20, "marktyp": 20, "title_index": [21, 27, 28], "reply_to": 22, "data_typ": 22, "replyto": 22, "cantrespons": [22, 29], "min_pag": 23, "max_pag": 23, "search_result": 23, "code": 23, "new_titl": 24, "datetim": 24, "now": 24, "2022": [25, 31, 33], "12": [25, 31, 33], "20": 25, "logger": 25, "log": 25, "19": [25, 31, 33], "docker": [25, 31, 33], "imag": [25, 31, 33], "08": [25, 31], "2021": [25, 31], "servic": [25, 31, 33], "01": 25, "roadmap": [25, 31], "09": 25, "furo": 25, "14": 25, "virtualenv": 26, "venv": [26, 32], "sourc": 26, "bin": 26, "activ": [26, 35], "pip": [26, 30, 32], "instal": [26, 30, 32], "requir": 26, "txt": 26, "doc": [26, 27], "bash": 26, "make_doc": 26, "sh": [26, 30], "_build": 26, "python3": 26, "py": 26, "sphinx": [26, 33], "fork": 26, "git": 26, "checkout": 26, "feat": 26, "my": 26, "new": 26, "featur": 26, "commit": 26, "am": 26, "add": 26, "some": 26, "msg": 26, "convent": 26, "origin": 26, "hub": 27, "com": 27, "codingman000": 27, "github": [27, 30, 33], "pyptt_imag": 27, "pull": 27, "latest": 27, "run": 27, "8787": 27, "request": [27, 32], "from": [27, 32, 34], "src": 27, "util": 27, "object_encod": 27, "config": 27, "if": [27, 28, 34], "__name__": [27, 28, 34], "__main__": [27, 28, 34], "param": 27, "arg": [27, 34], "http": [27, 32], "localhost": 27, "json": 27, "gossip": 27, "po": 27, "456": 27, "789": 27, "def": [28, 34], "max_retri": 28, "for": [28, 32, 34], "retry_tim": 28, "in": [28, 32, 34], "rang": [28, 34], "your_id": 28, "your_pw": 28, "els": 28, "break": 28, "sleep": 28, "logintoooften": [28, 29], "rais": 28, "as": 28, "return": 28, "last_newest_index": 28, "while": 28, "connectionclos": [28, 29], "continu": 28, "command": [28, 30], "ctrl_c": 28, "left": 28, "right": 28, "31": 28, "44": 28, "join": [28, 34], "post_status": [28, 35], "poststatus": 28, "exist": [28, 35], "elif": 28, "deleted_by_author": [28, 35], "sys": 28, "exit": 28, "deleted_by_moder": [28, 35], "not": 28, "pass_format_check": [28, 35], "multithreadoper": 29, "thread": [29, 34], "usetoomanyresourc": 29, "hostnotsupport": 29, "cantcom": 29, "connecterror": 29, "cannotusesearchpostcod": 29, "userhaspreviouslybeenban": 29, "nosearchresult": 29, "pr": 30, "issu": [30, 31, 33], "telegram": [30, 31], "asyncio": 30, "jypyt": 30, "nest_asyncio": 30, "appli": 30, "applic": 30, "certif": 30, "colab": 30, "gcp": 30, "azur": 30, "aws": 30, "etc": 30, "librari": [31, 32], "changelog": 31, "cpython": 32, "progressbar2": 32, "is": 32, "text": 32, "progress": 32, "bar": 32, "build": 32, "server": 32, "and": 32, "client": 32, "with": 32, "focus": 32, "on": 32, "correct": 32, "simplic": 32, "robust": 32, "perform": 32, "uao": 32, "pure": 32, "implement": 32, "the": 32, "unicod": 32, "encod": 32, "decod": 32, "releas": 32, "under": 32, "apach": 32, "licens": 32, "autostrenum": 32, "that": 32, "provid": 32, "an": 32, "enum": 32, "class": 32, "automat": 32, "convert": 32, "valu": 32, "to": 32, "string": 32, "pyyaml": 32, "yaml": 32, "parser": 32, "emitt": 32, "virtual": 32, "environ": 32, "packag": 32, "tor": 33, "proxi": 33, "app": 33, "18": [33, 35], "15": 33, "11": 33, "pyptt_init_config": 34, "safe": 34, "api_test": 34, "thread_id": 34, "result": 34, "call": 34, "your_ptt_id": 34, "your_ptt_pw": 34, "pool": 34, "target": 34, "start": 34, "append": 34, "close": 34, "telnet": 35, "author": 35, "mark": 35, "board_mail": 35, "boo": 35, "arrow": 35, "deleted_by_unknown": 35, "delete_d": 35, "unconfirm": 35, "login_count": 35, "account_verifi": 35, "legal_post": 35, "illegal_post": 35, "last_login_d": 35, "last_login_ip": 35, "ip": 35, "five_chess": 35, "chess": 35, "signature_fil": 35, "type": 35, "origin_mail": 35, "date": 35, "locat": 35, "is_red_envelop": 35, "online_us": 35, "chinese_d": 35, "moder": 35, "open_status": 35, "into_top_ten_when_hid": 35, "can_non_board_members_post": 35, "can_reply_post": 35, "self_del_post": 35, "can_comment_post": 35, "can_boo_post": 35, "can_fast_push": 35, "min_interval_between_com": 35, "is_comment_record_ip": 35, "is_comment_align": 35, "can_moderators_del_illegal_cont": 35, "does_tran_post_auto_recorded_and_require_post_permiss": 35, "is_cool_mod": 35, "is_require18": 35, "require_login_tim": 35, "require_illegal_post": 35, "post_kind_list": 35, "1z69g2ts": 35, "906": 35, "list_dat": 35, "has_control_cod": 35, "push_numb": 35, "is_lock": 35, "full_cont": 35, "is_unconfirm": 35}, "objects": {"PyPtt": [[17, 0, 0, "-", "API"], [34, 0, 0, "-", "Service"]], "PyPtt.API": [[17, 1, 1, "", "__init__"]], "PyPtt.BoardField": [[35, 2, 1, "", "board"], [35, 2, 1, "", "can_boo_post"], [35, 2, 1, "", "can_comment_post"], [35, 2, 1, "", "can_fast_push"], [35, 2, 1, "", "can_moderators_del_illegal_content"], [35, 2, 1, "", "can_non_board_members_post"], [35, 2, 1, "", "can_reply_post"], [35, 2, 1, "", "chinese_des"], [35, 2, 1, "", "does_tran_post_auto_recorded_and_require_post_permissions"], [35, 2, 1, "", "into_top_ten_when_hide"], [35, 2, 1, "", "is_comment_aligned"], [35, 2, 1, "", "is_comment_record_ip"], [35, 2, 1, "", "is_cool_mode"], [35, 2, 1, "", "is_require18"], [35, 2, 1, "", "min_interval_between_comments"], [35, 2, 1, "", "moderators"], [35, 2, 1, "", "online_user"], [35, 2, 1, "", "open_status"], [35, 2, 1, "", "post_kind_list"], [35, 2, 1, "", "require_illegal_post"], [35, 2, 1, "", "require_login_time"], [35, 2, 1, "", "self_del_post"]], "PyPtt.CommentField": [[35, 2, 1, "", "author"], [35, 2, 1, "", "content"], [35, 2, 1, "", "ip"], [35, 2, 1, "", "time"], [35, 2, 1, "", "type"]], "PyPtt.CommentType": [[35, 2, 1, "", "ARROW"], [35, 2, 1, "", "BOO"], [35, 2, 1, "", "PUSH"]], "PyPtt.ConnectMode": [[35, 2, 1, "", "TELNET"], [35, 2, 1, "", "WEBSOCKETS"]], "PyPtt.FavouriteBoardField": [[35, 2, 1, "", "board"], [35, 2, 1, "", "title"], [35, 2, 1, "", "type"]], "PyPtt.HOST": [[35, 2, 1, "", "PTT1"], [35, 2, 1, "", "PTT2"]], "PyPtt.Language": [[35, 2, 1, "", "ENGLISH"], [35, 2, 1, "", "MANDARIN"]], "PyPtt.MailField": [[35, 2, 1, "", "author"], [35, 2, 1, "", "content"], [35, 2, 1, "", "date"], [35, 2, 1, "", "ip"], [35, 2, 1, "", "is_red_envelope"], [35, 2, 1, "", "location"], [35, 2, 1, "", "origin_mail"], [35, 2, 1, "", "title"]], "PyPtt.MarkType": [[35, 2, 1, "", "D"], [35, 2, 1, "", "DELETE_D"], [35, 2, 1, "", "M"], [35, 2, 1, "", "S"], [35, 2, 1, "", "UNCONFIRMED"]], "PyPtt.NewIndex": [[35, 2, 1, "", "BOARD"], [35, 2, 1, "", "MAIL"]], "PyPtt.PostField": [[35, 2, 1, "", "aid"], [35, 2, 1, "", "author"], [35, 2, 1, "", "board"], [35, 2, 1, "", "comments"], [35, 2, 1, "", "content"], [35, 2, 1, "", "date"], [35, 2, 1, "", "full_content"], [35, 2, 1, "", "has_control_code"], [35, 2, 1, "", "index"], [35, 2, 1, "", "ip"], [35, 2, 1, "", "is_lock"], [35, 2, 1, "", "is_unconfirmed"], [35, 2, 1, "", "list_date"], [35, 2, 1, "", "location"], [35, 2, 1, "", "money"], [35, 2, 1, "", "pass_format_check"], [35, 2, 1, "", "post_status"], [35, 2, 1, "", "push_number"], [35, 2, 1, "", "title"], [35, 2, 1, "", "url"]], "PyPtt.PostStatus": [[35, 2, 1, "", "DELETED_BY_AUTHOR"], [35, 2, 1, "", "DELETED_BY_MODERATOR"], [35, 2, 1, "", "DELETED_BY_UNKNOWN"], [35, 2, 1, "", "EXISTS"]], "PyPtt.PyPtt.exceptions": [[29, 3, 1, "", "CanNotUseSearchPostCode"], [29, 3, 1, "", "CantComment"], [29, 3, 1, "", "CantResponse"], [29, 3, 1, "", "ConnectError"], [29, 3, 1, "", "ConnectionClosed"], [29, 3, 1, "", "HostNotSupport"], [29, 3, 1, "", "LoginError"], [29, 3, 1, "", "LoginTooOften"], [29, 3, 1, "", "MailboxFull"], [29, 3, 1, "", "MultiThreadOperated"], [29, 3, 1, "", "NeedModeratorPermission"], [29, 3, 1, "", "NoFastComment"], [29, 3, 1, "", "NoMoney"], [29, 3, 1, "", "NoPermission"], [29, 3, 1, "", "NoSearchResult"], [29, 3, 1, "", "NoSuchBoard"], [29, 3, 1, "", "NoSuchMail"], [29, 3, 1, "", "NoSuchPost"], [29, 3, 1, "", "NoSuchUser"], [29, 3, 1, "", "OnlySecureConnection"], [29, 3, 1, "", "RequireLogin"], [29, 3, 1, "", "ResetYourContactEmail"], [29, 3, 1, "", "SetContactMailFirst"], [29, 3, 1, "", "UnregisteredUser"], [29, 3, 1, "", "UseTooManyResources"], [29, 3, 1, "", "UserHasPreviouslyBeenBanned"], [29, 3, 1, "", "WrongIDorPassword"], [29, 3, 1, "", "WrongPassword"]], "PyPtt.ReplyTo": [[35, 2, 1, "", "BOARD"], [35, 2, 1, "", "BOARD_MAIL"], [35, 2, 1, "", "MAIL"]], "PyPtt.SearchType": [[35, 2, 1, "", "AUTHOR"], [35, 2, 1, "", "COMMENT"], [35, 2, 1, "", "KEYWORD"], [35, 2, 1, "", "MARK"], [35, 2, 1, "", "MONEY"]], "PyPtt.Service": [[34, 1, 1, "", "__init__"]], "PyPtt.UserField": [[35, 2, 1, "", "account_verified"], [35, 2, 1, "", "activity"], [35, 2, 1, "", "chess"], [35, 2, 1, "", "five_chess"], [35, 2, 1, "", "illegal_post"], [35, 2, 1, "", "last_login_date"], [35, 2, 1, "", "last_login_ip"], [35, 2, 1, "", "legal_post"], [35, 2, 1, "", "login_count"], [35, 2, 1, "", "mail"], [35, 2, 1, "", "money"], [35, 2, 1, "", "ptt_id"], [35, 2, 1, "", "signature_file"]]}, "objtypes": {"0": "py:module", "1": "py:function", "2": "py:attribute", "3": "py:exception"}, "objnames": {"0": ["py", "module", "Python \u6a21\u7d44"], "1": ["py", "function", "Python \u51fd\u5f0f"], "2": ["py", "attribute", "Python \u5c6c\u6027"], "3": ["py", "exception", "Python \u4f8b\u5916"]}, "titleterms": {"bucket": 0, "change_pw": 1, "comment": 2, "del_mail": 3, "del_post": 4, "get_aid_from_url": 5, "get_all_board": 6, "get_board_info": 7, "get_bottom_post_list": 8, "get_favourite_board": 9, "get_mail": 10, "get_newest_index": 11, "get_post": 12, "get_tim": 13, "get_us": 14, "give_money": 15, "api": 16, "ptt": 16, "init": 17, "login": 18, "logout": 18, "mail": 19, "mark_post": 20, "post": 21, "reply_post": 22, "search_us": 23, "set_board_titl": 24, "develop": 26, "pull": 26, "request": 26, "docker": 27, "imag": 27, "faq": 30, "pyptt": [30, 31, 32], "jupyt": 30, "the": 30, "event": 30, "loop": 30, "is": 30, "alreadi": 30, "run": 30, "mac": 30, "websocket": 30, "ssl": 30, "python": 32, "servic": 34, "host": 35, "languag": 35, "connectmod": 35, "newindex": 35, "searchtyp": 35, "replyto": 35, "commenttyp": 35, "poststatus": 35, "marktyp": 35, "userfield": 35, "commentfield": 35, "favouriteboardfield": 35, "mailfield": 35, "boardfield": 35, "postfield": 35}, "envversion": {"sphinx.domains.c": 3, "sphinx.domains.changeset": 1, "sphinx.domains.citation": 1, "sphinx.domains.cpp": 9, "sphinx.domains.index": 1, "sphinx.domains.javascript": 3, "sphinx.domains.math": 2, "sphinx.domains.python": 4, "sphinx.domains.rst": 2, "sphinx.domains.std": 2, "sphinx": 60}, "alltitles": {"bucket": [[0, "bucket"]], "change_pw": [[1, "change-pw"]], "comment": [[2, "comment"]], "del_mail": [[3, "del-mail"]], "del_post": [[4, "del-post"]], "get_aid_from_url": [[5, "get-aid-from-url"]], "get_all_boards": [[6, "get-all-boards"]], "get_board_info": [[7, "get-board-info"]], "get_bottom_post_list": [[8, "get-bottom-post-list"]], "get_favourite_boards": [[9, "get-favourite-boards"]], "get_mail": [[10, "get-mail"]], "get_newest_index": [[11, "get-newest-index"]], "get_post": [[12, "get-post"]], "get_time": [[13, "get-time"]], "get_user": [[14, "get-user"]], "give_money": [[15, "give-money"]], "APIs": [[16, "apis"]], "\u57fa\u672c\u529f\u80fd": [[16, "id1"]], "\u6587\u7ae0\u76f8\u95dc": [[16, "id2"]], "\u4fe1\u7bb1\u76f8\u95dc": [[16, "id3"]], "\u4f7f\u7528\u8005\u76f8\u95dc": [[16, "id4"]], "\u53d6\u5f97 PTT \u8cc7\u8a0a": [[16, "ptt"]], "\u7248\u4e3b\u76f8\u95dc": [[16, "id5"]], "init": [[17, "init"]], "login, logout": [[18, "login-logout"]], "mail": [[19, "mail"]], "mark_post": [[20, "mark-post"]], "post": [[21, "post"]], "reply_post": [[22, "reply-post"]], "search_user": [[23, "search-user"]], "set_board_title": [[24, "set-board-title"]], "\u66f4\u65b0\u65e5\u8a8c": [[25, "id1"]], "Development": [[26, "development"]], "\u958b\u767c\u74b0\u5883": [[26, "id1"]], "\u5b89\u88dd\u76f8\u4f9d\u5957\u4ef6": [[26, "id2"]], "\u57f7\u884c\u6e2c\u8a66": [[26, "id3"]], "\u64b0\u5beb\u6587\u4ef6": [[26, "id4"]], "\u5efa\u7acb\u4f60\u7684 Pull Request": [[26, "pull-request"]], "Docker Image": [[27, "docker-image"]], "\u5b89\u88dd": [[27, "id1"]], "\u555f\u52d5": [[27, "id2"]], "\u9023\u7dda": [[27, "id3"]], "\u4f7f\u7528\u7bc4\u4f8b": [[28, "id1"]], "\u4fdd\u6301\u767b\u5165": [[28, "id2"]], "\u5e6b\u4f60\u7684\u6587\u7ae0\u4e0a\u8272": [[28, "id3"]], "\u5982\u4f55\u5224\u65b7\u6587\u7ae0\u8cc7\u6599\u662f\u5426\u53ef\u4ee5\u4f7f\u7528": [[28, "check-post-status"]], "\u4f8b\u5916": [[29, "id1"]], "FAQ": [[30, "faq"]], "Q: \u6211\u8a72\u5982\u4f55\u4f7f\u7528 PyPtt\uff1f": [[30, "q-pyptt"]], "Q: \u4f7f\u7528 PyPtt \u6642\uff0c\u9047\u5230\u554f\u984c\u8a72\u5982\u4f55\u89e3\u6c7a\uff1f": [[30, "id1"]], "Q: \u5728 jupyter \u906d\u9047 the event loop is already running \u932f\u8aa4": [[30, "q-jupyter-the-event-loop-is-already-running"]], "Q: \u5728 Mac \u7121\u6cd5\u4f7f\u7528 WebSocket \u9023\u7dda\uff0c\u906d\u9047 SSL \u76f8\u95dc\u932f\u8aa4": [[30, "q-mac-websocket-ssl"]], "Q: \u70ba\u4ec0\u9ebc\u6211\u6c92\u8fa6\u6cd5\u5728\u96f2\u7aef\u74b0\u5883\u4e0a\u4f7f\u7528 PyPtt\uff1f": [[30, "id2"]], "PyPtt": [[31, "pyptt"]], "\u91cd\u8981\u6d88\u606f": [[31, "id3"]], "\u6587\u4ef6": [[31, "id4"]], "\u5b89\u88dd PyPtt": [[32, "pyptt"]], "Python \u7248\u672c": [[32, "python"]], "\u76f8\u4f9d\u5957\u4ef6": [[32, "id1"]], "\u4f7f\u7528\u865b\u64ec\u74b0\u5883\u5b89\u88dd (\u63a8\u85a6)": [[32, "id2"]], "\u5b89\u88dd\u6307\u4ee4": [[32, "id3"]], "\u958b\u767c": [[33, "id1"]], "\u672a\u4f86\u958b\u767c\u8a08\u5283": [[33, "id2"]], "\u958b\u767c\u4e2d": [[33, "id3"]], "\u5df2\u5b8c\u6210": [[33, "id4"]], "Service": [[34, "module-PyPtt.Service"]], "\u53c3\u6578\u578b\u614b": [[35, "id1"]], "HOST": [[35, "host"]], "Language": [[35, "language"]], "ConnectMode": [[35, "connectmode"]], "NewIndex": [[35, "newindex"]], "SearchType": [[35, "searchtype"]], "ReplyTo": [[35, "replyto"]], "CommentType": [[35, "commenttype"]], "PostStatus": [[35, "poststatus"]], "MarkType": [[35, "marktype"]], "UserField": [[35, "userfield"]], "CommentField": [[35, "commentfield"]], "FavouriteBoardField": [[35, "favouriteboardfield"]], "MailField": [[35, "mailfield"]], "BoardField": [[35, "boardfield"]], "PostField": [[35, "postfield"]]}, "indexentries": {"pyptt.api": [[17, "module-PyPtt.API"]], "__init__() (\u65bc pyptt.api \u6a21\u7d44\u4e2d)": [[17, "PyPtt.API.__init__"]], "module": [[17, "module-PyPtt.API"], [34, "module-PyPtt.Service"]], "pyptt.exceptions.cannotusesearchpostcode": [[29, "PyPtt.PyPtt.exceptions.CanNotUseSearchPostCode"]], "pyptt.exceptions.cantcomment": [[29, "PyPtt.PyPtt.exceptions.CantComment"]], "pyptt.exceptions.cantresponse": [[29, "PyPtt.PyPtt.exceptions.CantResponse"]], "pyptt.exceptions.connecterror": [[29, "PyPtt.PyPtt.exceptions.ConnectError"]], "pyptt.exceptions.connectionclosed": [[29, "PyPtt.PyPtt.exceptions.ConnectionClosed"]], "pyptt.exceptions.hostnotsupport": [[29, "PyPtt.PyPtt.exceptions.HostNotSupport"]], "pyptt.exceptions.loginerror": [[29, "PyPtt.PyPtt.exceptions.LoginError"]], "pyptt.exceptions.logintoooften": [[29, "PyPtt.PyPtt.exceptions.LoginTooOften"]], "pyptt.exceptions.mailboxfull": [[29, "PyPtt.PyPtt.exceptions.MailboxFull"]], "pyptt.exceptions.multithreadoperated": [[29, "PyPtt.PyPtt.exceptions.MultiThreadOperated"]], "pyptt.exceptions.needmoderatorpermission": [[29, "PyPtt.PyPtt.exceptions.NeedModeratorPermission"]], "pyptt.exceptions.nofastcomment": [[29, "PyPtt.PyPtt.exceptions.NoFastComment"]], "pyptt.exceptions.nomoney": [[29, "PyPtt.PyPtt.exceptions.NoMoney"]], "pyptt.exceptions.nopermission": [[29, "PyPtt.PyPtt.exceptions.NoPermission"]], "pyptt.exceptions.nosearchresult": [[29, "PyPtt.PyPtt.exceptions.NoSearchResult"]], "pyptt.exceptions.nosuchboard": [[29, "PyPtt.PyPtt.exceptions.NoSuchBoard"]], "pyptt.exceptions.nosuchmail": [[29, "PyPtt.PyPtt.exceptions.NoSuchMail"]], "pyptt.exceptions.nosuchpost": [[29, "PyPtt.PyPtt.exceptions.NoSuchPost"]], "pyptt.exceptions.nosuchuser": [[29, "PyPtt.PyPtt.exceptions.NoSuchUser"]], "pyptt.exceptions.onlysecureconnection": [[29, "PyPtt.PyPtt.exceptions.OnlySecureConnection"]], "pyptt.exceptions.requirelogin": [[29, "PyPtt.PyPtt.exceptions.RequireLogin"]], "pyptt.exceptions.resetyourcontactemail": [[29, "PyPtt.PyPtt.exceptions.ResetYourContactEmail"]], "pyptt.exceptions.setcontactmailfirst": [[29, "PyPtt.PyPtt.exceptions.SetContactMailFirst"]], "pyptt.exceptions.unregistereduser": [[29, "PyPtt.PyPtt.exceptions.UnregisteredUser"]], "pyptt.exceptions.usetoomanyresources": [[29, "PyPtt.PyPtt.exceptions.UseTooManyResources"]], "pyptt.exceptions.userhaspreviouslybeenbanned": [[29, "PyPtt.PyPtt.exceptions.UserHasPreviouslyBeenBanned"]], "pyptt.exceptions.wrongidorpassword": [[29, "PyPtt.PyPtt.exceptions.WrongIDorPassword"]], "pyptt.exceptions.wrongpassword": [[29, "PyPtt.PyPtt.exceptions.WrongPassword"]], "pyptt.service": [[34, "module-PyPtt.Service"]], "__init__() (\u65bc pyptt.service \u6a21\u7d44\u4e2d)": [[34, "PyPtt.Service.__init__"]], "arrow (pyptt.commenttype \u7684\u5c6c\u6027)": [[35, "PyPtt.CommentType.ARROW"]], "author (pyptt.searchtype \u7684\u5c6c\u6027)": [[35, "PyPtt.SearchType.AUTHOR"]], "board (pyptt.newindex \u7684\u5c6c\u6027)": [[35, "PyPtt.NewIndex.BOARD"]], "board (pyptt.replyto \u7684\u5c6c\u6027)": [[35, "PyPtt.ReplyTo.BOARD"]], "board_mail (pyptt.replyto \u7684\u5c6c\u6027)": [[35, "PyPtt.ReplyTo.BOARD_MAIL"]], "boo (pyptt.commenttype \u7684\u5c6c\u6027)": [[35, "PyPtt.CommentType.BOO"]], "comment (pyptt.searchtype \u7684\u5c6c\u6027)": [[35, "PyPtt.SearchType.COMMENT"]], "d (pyptt.marktype \u7684\u5c6c\u6027)": [[35, "PyPtt.MarkType.D"]], "deleted_by_author (pyptt.poststatus \u7684\u5c6c\u6027)": [[35, "PyPtt.PostStatus.DELETED_BY_AUTHOR"]], "deleted_by_moderator (pyptt.poststatus \u7684\u5c6c\u6027)": [[35, "PyPtt.PostStatus.DELETED_BY_MODERATOR"]], "deleted_by_unknown (pyptt.poststatus \u7684\u5c6c\u6027)": [[35, "PyPtt.PostStatus.DELETED_BY_UNKNOWN"]], "delete_d (pyptt.marktype \u7684\u5c6c\u6027)": [[35, "PyPtt.MarkType.DELETE_D"]], "english (pyptt.language \u7684\u5c6c\u6027)": [[35, "PyPtt.Language.ENGLISH"]], "exists (pyptt.poststatus \u7684\u5c6c\u6027)": [[35, "PyPtt.PostStatus.EXISTS"]], "keyword (pyptt.searchtype \u7684\u5c6c\u6027)": [[35, "PyPtt.SearchType.KEYWORD"]], "m (pyptt.marktype \u7684\u5c6c\u6027)": [[35, "PyPtt.MarkType.M"]], "mail (pyptt.newindex \u7684\u5c6c\u6027)": [[35, "PyPtt.NewIndex.MAIL"]], "mail (pyptt.replyto \u7684\u5c6c\u6027)": [[35, "PyPtt.ReplyTo.MAIL"]], "mandarin (pyptt.language \u7684\u5c6c\u6027)": [[35, "PyPtt.Language.MANDARIN"]], "mark (pyptt.searchtype \u7684\u5c6c\u6027)": [[35, "PyPtt.SearchType.MARK"]], "money (pyptt.searchtype \u7684\u5c6c\u6027)": [[35, "PyPtt.SearchType.MONEY"]], "ptt1 (pyptt.host \u7684\u5c6c\u6027)": [[35, "PyPtt.HOST.PTT1"]], "ptt2 (pyptt.host \u7684\u5c6c\u6027)": [[35, "PyPtt.HOST.PTT2"]], "push (pyptt.commenttype \u7684\u5c6c\u6027)": [[35, "PyPtt.CommentType.PUSH"]], "s (pyptt.marktype \u7684\u5c6c\u6027)": [[35, "PyPtt.MarkType.S"]], "telnet (pyptt.connectmode \u7684\u5c6c\u6027)": [[35, "PyPtt.ConnectMode.TELNET"]], "unconfirmed (pyptt.marktype \u7684\u5c6c\u6027)": [[35, "PyPtt.MarkType.UNCONFIRMED"]], "websockets (pyptt.connectmode \u7684\u5c6c\u6027)": [[35, "PyPtt.ConnectMode.WEBSOCKETS"]], "account_verified (pyptt.userfield \u7684\u5c6c\u6027)": [[35, "PyPtt.UserField.account_verified"]], "activity (pyptt.userfield \u7684\u5c6c\u6027)": [[35, "PyPtt.UserField.activity"]], "aid (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.aid"]], "author (pyptt.commentfield \u7684\u5c6c\u6027)": [[35, "PyPtt.CommentField.author"]], "author (pyptt.mailfield \u7684\u5c6c\u6027)": [[35, "PyPtt.MailField.author"]], "author (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.author"]], "board (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.board"]], "board (pyptt.favouriteboardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.FavouriteBoardField.board"]], "board (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.board"]], "can_boo_post (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.can_boo_post"]], "can_comment_post (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.can_comment_post"]], "can_fast_push (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.can_fast_push"]], "can_moderators_del_illegal_content (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.can_moderators_del_illegal_content"]], "can_non_board_members_post (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.can_non_board_members_post"]], "can_reply_post (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.can_reply_post"]], "chess (pyptt.userfield \u7684\u5c6c\u6027)": [[35, "PyPtt.UserField.chess"]], "chinese_des (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.chinese_des"]], "comments (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.comments"]], "content (pyptt.commentfield \u7684\u5c6c\u6027)": [[35, "PyPtt.CommentField.content"]], "content (pyptt.mailfield \u7684\u5c6c\u6027)": [[35, "PyPtt.MailField.content"]], "content (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.content"]], "date (pyptt.mailfield \u7684\u5c6c\u6027)": [[35, "PyPtt.MailField.date"]], "date (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.date"]], "does_tran_post_auto_recorded_and_require_post_permissions (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.does_tran_post_auto_recorded_and_require_post_permissions"]], "five_chess (pyptt.userfield \u7684\u5c6c\u6027)": [[35, "PyPtt.UserField.five_chess"]], "full_content (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.full_content"]], "has_control_code (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.has_control_code"]], "illegal_post (pyptt.userfield \u7684\u5c6c\u6027)": [[35, "PyPtt.UserField.illegal_post"]], "index (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.index"]], "into_top_ten_when_hide (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.into_top_ten_when_hide"]], "ip (pyptt.commentfield \u7684\u5c6c\u6027)": [[35, "PyPtt.CommentField.ip"]], "ip (pyptt.mailfield \u7684\u5c6c\u6027)": [[35, "PyPtt.MailField.ip"]], "ip (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.ip"]], "is_comment_aligned (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.is_comment_aligned"]], "is_comment_record_ip (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.is_comment_record_ip"]], "is_cool_mode (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.is_cool_mode"]], "is_lock (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.is_lock"]], "is_red_envelope (pyptt.mailfield \u7684\u5c6c\u6027)": [[35, "PyPtt.MailField.is_red_envelope"]], "is_require18 (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.is_require18"]], "is_unconfirmed (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.is_unconfirmed"]], "last_login_date (pyptt.userfield \u7684\u5c6c\u6027)": [[35, "PyPtt.UserField.last_login_date"]], "last_login_ip (pyptt.userfield \u7684\u5c6c\u6027)": [[35, "PyPtt.UserField.last_login_ip"]], "legal_post (pyptt.userfield \u7684\u5c6c\u6027)": [[35, "PyPtt.UserField.legal_post"]], "list_date (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.list_date"]], "location (pyptt.mailfield \u7684\u5c6c\u6027)": [[35, "PyPtt.MailField.location"]], "location (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.location"]], "login_count (pyptt.userfield \u7684\u5c6c\u6027)": [[35, "PyPtt.UserField.login_count"]], "mail (pyptt.userfield \u7684\u5c6c\u6027)": [[35, "PyPtt.UserField.mail"]], "min_interval_between_comments (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.min_interval_between_comments"]], "moderators (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.moderators"]], "money (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.money"]], "money (pyptt.userfield \u7684\u5c6c\u6027)": [[35, "PyPtt.UserField.money"]], "online_user (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.online_user"]], "open_status (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.open_status"]], "origin_mail (pyptt.mailfield \u7684\u5c6c\u6027)": [[35, "PyPtt.MailField.origin_mail"]], "pass_format_check (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.pass_format_check"]], "post_kind_list (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.post_kind_list"]], "post_status (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.post_status"]], "ptt_id (pyptt.userfield \u7684\u5c6c\u6027)": [[35, "PyPtt.UserField.ptt_id"]], "push_number (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.push_number"]], "require_illegal_post (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.require_illegal_post"]], "require_login_time (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.require_login_time"]], "self_del_post (pyptt.boardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.BoardField.self_del_post"]], "signature_file (pyptt.userfield \u7684\u5c6c\u6027)": [[35, "PyPtt.UserField.signature_file"]], "time (pyptt.commentfield \u7684\u5c6c\u6027)": [[35, "PyPtt.CommentField.time"]], "title (pyptt.favouriteboardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.FavouriteBoardField.title"]], "title (pyptt.mailfield \u7684\u5c6c\u6027)": [[35, "PyPtt.MailField.title"]], "title (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.title"]], "type (pyptt.commentfield \u7684\u5c6c\u6027)": [[35, "PyPtt.CommentField.type"]], "type (pyptt.favouriteboardfield \u7684\u5c6c\u6027)": [[35, "PyPtt.FavouriteBoardField.type"]], "url (pyptt.postfield \u7684\u5c6c\u6027)": [[35, "PyPtt.PostField.url"]]}})