Search.setIndex({"docnames": ["api/bucket", "api/change_pw", "api/comment", "api/del_mail", "api/del_post", "api/get_aid_from_url", "api/get_board_info", "api/get_board_list", "api/get_bottom_post_list", "api/get_favourite_boards", "api/get_mail", "api/get_newest_index", "api/get_post", "api/get_time", "api/get_user", "api/give_money", "api/index", "api/init", "api/login_logout", "api/mail", "api/mark_post", "api/post", "api/reply_post", "api/search_user", "api/set_board_title", "changelog", "develop", "examples", "exceptions", "faq", "index", "install", "type"], "filenames": ["api/bucket.rst", "api/change_pw.rst", "api/comment.rst", "api/del_mail.rst", "api/del_post.rst", "api/get_aid_from_url.rst", "api/get_board_info.rst", "api/get_board_list.rst", "api/get_bottom_post_list.rst", "api/get_favourite_boards.rst", "api/get_mail.rst", "api/get_newest_index.rst", "api/get_post.rst", "api/get_time.rst", "api/get_user.rst", "api/give_money.rst", "api/index.rst", "api/init.rst", "api/login_logout.rst", "api/mail.rst", "api/mark_post.rst", "api/post.rst", "api/reply_post.rst", "api/search_user.rst", "api/set_board_title.rst", "changelog.rst", "develop.rst", "examples.rst", "exceptions.rst", "faq.rst", "index.rst", "install.rst", "type.rst"], "titles": ["bucket", "change_pw", "comment", "del_mail", "del_post", "get_aid_from_url", "get_board_info", "get_board_list", "get_bottom_post_list", "get_favourite_boards", "get_mail", "get_newest_index", "get_post", "get_time", "get_user", "give_money", "APIs", "init", "login, logout", "mail", "mark_post", "post", "reply_post", "search_user", "set_board_title", "\u66f4\u65b0\u65e5\u8a8c", "\u958b\u767c", "\u4f7f\u7528\u7bc4\u4f8b", "\u4f8b\u5916", "FAQ", "PyPtt", "\u5b89\u88dd PyPtt", "\u53c3\u6578\u578b\u614b"], "terms": {"pyptt": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 32], "api": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 29, 30, 31], "self": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24], "board": [0, 2, 4, 5, 6, 8, 11, 12, 20, 21, 22, 24, 27, 32], "str": [0, 1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 24], "bucket_day": 0, "int": [0, 2, 3, 4, 10, 11, 12, 15, 17, 19, 20, 21, 22, 23], "reason": 0, "ptt_id": [0, 15, 18, 19, 23, 32], "none": [0, 1, 2, 3, 4, 10, 11, 12, 13, 15, 17, 18, 19, 20, 21, 22, 23, 24, 27], "ptt": [0, 5, 13, 15, 17, 18, 19, 23, 26, 27, 30, 32], "id": [0, 14, 15, 18, 19, 23, 32], "requirelogin": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 14, 15, 19, 20, 21, 22, 23, 24, 28], "unregisteredus": [0, 2, 3, 4, 15, 19, 20, 21, 23, 24, 28], "nosuchboard": [0, 2, 4, 6, 8, 11, 12, 20, 21, 22, 24, 28], "nosuchus": [0, 14, 15, 19, 28], "needmoderatorpermiss": [0, 20, 24, 28], "import": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 27, 29], "ptt_bot": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 27, 29], "tri": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 24, 27, 28], "login": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 27], "test": [0, 2, 6, 20, 21, 22, 24, 27], "do": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 20, 21, 22, 23, 24, 27], "someth": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 20, 21, 22, 23, 24, 27], "final": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 24, 27], "logout": [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 27], "new_password": 1, "setconnectmailfirst": [1, 28], "wrongpassword": [1, 28], "123456": 1, "comment_typ": 2, "commenttyp": 2, "content": [2, 19, 21, 22, 27, 32], "aid": [2, 4, 5, 12, 20, 22, 32], "option": [2, 4, 10, 11, 12, 15, 17, 20, 22, 23], "index": [2, 3, 4, 10, 11, 12, 20, 22, 27, 32], "nosuchpost": [2, 4, 20, 22, 28], "nopermiss": [2, 4, 6, 10, 21, 22, 28], "nofastcom": [2, 28], "push": [2, 32], "comment_cont": 2, "123": [2, 20, 22], "mailboxful": [3, 28], "get_newest_index": [3, 10, 16, 27], "python": [4, 5, 8, 11, 12, 27, 29], "1tjh_xy0": [4, 12], "url": [5, 32], "tupl": 5, "https": 5, "www": 5, "cc": 5, "bbs": 5, "1565335521": 5, "880": 5, "html": 5, "get_post_typ": 6, "bool": [6, 12, 17, 18, 19], "fals": [6, 12, 18, 27], "dict": [6, 9, 10, 12, 14], "boardfield": 6, "board_info": 6, "list": [7, 8, 9, 10, 11, 12, 23], "board_list": 7, "post": [8, 16, 27], "postfield": [8, 12, 27], "bottom_post_list": 8, "favouriteboardfield": 9, "favourite_board": 9, "search_typ": [10, 11, 12, 20], "searchtyp": [10, 11, 12, 20], "search_condit": [10, 11, 12, 20], "search_list": [10, 11, 12], "mailfield": 10, "nosuchmail": 10, "mail": [10, 11, 16, 32], "index_typ": 11, "newindex": 11, "get": 11, "newest": 11, "of": [11, 31], "newest_index": [11, 27], "nope": 12, "queri": 12, "post_info": [12, 27], "time": [13, 27, 32], "user_id": 14, "user_info": 14, "codingman": [14, 15, 19, 30], "money": [15, 32], "red_bag_titl": 15, "red_bag_cont": 15, "nomoney": [15, 28], "100": 15, "or": [15, 26], "ptt2": [16, 32], "init": 16, "get_post": [16, 27], "reply_post": 16, "del_post": 16, "comment": [16, 32], "get_mail": 16, "del_mail": 16, "give_money": 16, "get_us": 16, "search_us": 16, "change_pw": 16, "get_tim": 16, "get_board_list": 16, "get_favourite_board": 16, "get_board_info": 16, "get_aid_from_url": 16, "get_bottom_post_list": 16, "set_board_titl": 16, "mark_post": 16, "bucket": 16, "__init__": 17, "languag": 17, "mandarin": [17, 32], "log_level": 17, "loglevel": [17, 29], "info": [17, 18], "screen_timeout": 17, "screen_long_timeout": 17, "10": [17, 29], "screen_post_timeout": 17, "60": [17, 27], "connect_mod": 17, "connectmod": 17, "websocket": [17, 26, 31, 32], "port": 17, "23": 17, "logger_callback": 17, "callabl": 17, "host": [17, 28], "ptt1": [17, 32], "check_upd": 17, "true": [17, 18, 19, 27], "callback": 17, "ptt_pw": 18, "kick_other_sess": [18, 27], "session": 18, "loginerror": [18, 27, 28], "wrongidorpassword": [18, 27, 28], "onlysecureconnect": [18, 28], "from": [18, 29, 31], "except": [18, 27, 28], "logger": 18, "logintoooften": [18, 27, 28], "titl": [19, 21, 27, 32], "sign_fil": [19, 21, 22, 27], "backup": 19, "mark_typ": 20, "marktyp": 20, "title_index": [21, 27], "reply_to": 22, "data_typ": 22, "replyto": 22, "cantrespons": [22, 28], "min_pag": 23, "max_pag": 23, "search_result": 23, "code": 23, "new_titl": 24, "datetim": 24, "now": 24, "2022": [25, 30], "09": [25, 30], "14": [25, 30], "github": 26, "issu": [26, 30], "tor": 26, "proxi": 26, "servic": 26, "imag": 26, "sphinx": 26, "def": 27, "max_retri": 27, "for": [27, 31], "retry_tim": 27, "in": [27, 31], "rang": 27, "your_id": 27, "your_pw": 27, "if": 27, "els": 27, "break": 27, "print": 27, "sleep": 27, "rais": 27, "as": 27, "return": 27, "__name__": 27, "__main__": 27, "last_newest_index": 27, "while": 27, "connectionclos": [27, 28], "continu": 27, "command": [27, 29], "ctrl_c": 27, "left": 27, "right": 27, "31": 27, "44": 27, "join": 27, "post_status": [27, 32], "poststatus": 27, "exist": [27, 32], "elif": 27, "deleted_by_author": [27, 32], "sys": 27, "exit": 27, "deleted_by_moder": [27, 32], "not": 27, "pass_format_check": [27, 32], "multithreadoper": 28, "thread": 28, "usetoomanyresourc": 28, "hostnotsupport": 28, "cantcom": 28, "connecterror": 28, "cannotusesearchpostcod": 28, "userhaspreviouslybeenban": 28, "nosearchresult": 28, "trace": 29, "asyncio": 29, "jypyt": 29, "nest_asyncio": 29, "pip": [29, 31], "instal": [29, 31], "appli": 29, "sh": 29, "applic": 29, "certif": 29, "telegram": 30, "cpython": 31, "is": 31, "librari": 31, "build": 31, "server": 31, "and": 31, "client": 31, "with": 31, "focus": 31, "on": 31, "correct": 31, "simplic": 31, "robust": 31, "perform": 31, "uao": 31, "pure": 31, "implement": 31, "the": 31, "unicod": 31, "encod": 31, "decod": 31, "singlelog": 31, "simpl": 31, "log": 31, "request": 31, "http": 31, "releas": 31, "under": 31, "apach": 31, "licens": 31, "autostrenum": 31, "that": 31, "provid": 31, "an": 31, "enum": 31, "class": 31, "automat": 31, "convert": 31, "valu": 31, "to": 31, "string": 31, "venv": 31, "virtual": 31, "environ": 31, "packag": 31, "english": 32, "telnet": 32, "keyword": 32, "author": 32, "mark": 32, "board_mail": 32, "boo": 32, "arrow": 32, "deleted_by_unknown": 32, "delete_d": 32, "unconfirm": 32, "login_count": 32, "account_verifi": 32, "legal_post": 32, "illegal_post": 32, "activ": 32, "last_login_d": 32, "last_login_ip": 32, "ip": 32, "five_chess": 32, "chess": 32, "signature_fil": 32, "type": 32, "origin_mail": 32, "date": 32, "locat": 32, "is_red_envelop": 32, "online_us": 32, "chinese_d": 32, "moder": 32, "open_status": 32, "into_top_ten_when_hid": 32, "can_non_board_members_post": 32, "can_reply_post": 32, "self_del_post": 32, "can_comment_post": 32, "can_boo_post": 32, "can_fast_push": 32, "min_interval_between_com": 32, "is_comment_record_ip": 32, "is_comment_align": 32, "can_moderators_del_illegal_cont": 32, "does_tran_post_auto_recorded_and_require_post_permiss": 32, "is_cool_mod": 32, "is_require18": 32, "18": 32, "require_login_tim": 32, "require_illegal_post": 32, "post_kind_list": 32, "1z69g2ts": 32, "906": 32, "list_dat": 32, "has_control_cod": 32, "push_numb": 32, "is_lock": 32, "full_cont": 32, "is_unconfirm": 32}, "objects": {"PyPtt": [[17, 0, 0, "-", "API"]], "PyPtt.API": [[17, 1, 1, "", "__init__"]], "PyPtt.BoardField": [[32, 2, 1, "", "board"], [32, 2, 1, "", "can_boo_post"], [32, 2, 1, "", "can_comment_post"], [32, 2, 1, "", "can_fast_push"], [32, 2, 1, "", "can_moderators_del_illegal_content"], [32, 2, 1, "", "can_non_board_members_post"], [32, 2, 1, "", "can_reply_post"], [32, 2, 1, "", "chinese_des"], [32, 2, 1, "", "does_tran_post_auto_recorded_and_require_post_permissions"], [32, 2, 1, "", "into_top_ten_when_hide"], [32, 2, 1, "", "is_comment_aligned"], [32, 2, 1, "", "is_comment_record_ip"], [32, 2, 1, "", "is_cool_mode"], [32, 2, 1, "", "is_require18"], [32, 2, 1, "", "min_interval_between_comments"], [32, 2, 1, "", "moderators"], [32, 2, 1, "", "online_user"], [32, 2, 1, "", "open_status"], [32, 2, 1, "", "post_kind_list"], [32, 2, 1, "", "require_illegal_post"], [32, 2, 1, "", "require_login_time"], [32, 2, 1, "", "self_del_post"]], "PyPtt.CommentField": [[32, 2, 1, "", "author"], [32, 2, 1, "", "content"], [32, 2, 1, "", "ip"], [32, 2, 1, "", "time"], [32, 2, 1, "", "type"]], "PyPtt.CommentType": [[32, 2, 1, "", "ARROW"], [32, 2, 1, "", "BOO"], [32, 2, 1, "", "PUSH"]], "PyPtt.ConnectMode": [[32, 2, 1, "", "TELNET"], [32, 2, 1, "", "WEBSOCKETS"]], "PyPtt.FavouriteBoardField": [[32, 2, 1, "", "board"], [32, 2, 1, "", "title"], [32, 2, 1, "", "type"]], "PyPtt.HOST": [[32, 2, 1, "", "PTT1"], [32, 2, 1, "", "PTT2"]], "PyPtt.Language": [[32, 2, 1, "", "ENGLISH"], [32, 2, 1, "", "MANDARIN"]], "PyPtt.MailField": [[32, 2, 1, "", "author"], [32, 2, 1, "", "content"], [32, 2, 1, "", "date"], [32, 2, 1, "", "ip"], [32, 2, 1, "", "is_red_envelope"], [32, 2, 1, "", "location"], [32, 2, 1, "", "origin_mail"], [32, 2, 1, "", "title"]], "PyPtt.MarkType": [[32, 2, 1, "", "D"], [32, 2, 1, "", "DELETE_D"], [32, 2, 1, "", "M"], [32, 2, 1, "", "S"], [32, 2, 1, "", "UNCONFIRMED"]], "PyPtt.NewIndex": [[32, 2, 1, "", "BOARD"], [32, 2, 1, "", "MAIL"]], "PyPtt.PostField": [[32, 2, 1, "", "aid"], [32, 2, 1, "", "author"], [32, 2, 1, "", "board"], [32, 2, 1, "", "comments"], [32, 2, 1, "", "content"], [32, 2, 1, "", "date"], [32, 2, 1, "", "full_content"], [32, 2, 1, "", "has_control_code"], [32, 2, 1, "", "index"], [32, 2, 1, "", "ip"], [32, 2, 1, "", "is_lock"], [32, 2, 1, "", "is_unconfirmed"], [32, 2, 1, "", "list_date"], [32, 2, 1, "", "location"], [32, 2, 1, "", "money"], [32, 2, 1, "", "pass_format_check"], [32, 2, 1, "", "post_status"], [32, 2, 1, "", "push_number"], [32, 2, 1, "", "title"], [32, 2, 1, "", "url"]], "PyPtt.PostStatus": [[32, 2, 1, "", "DELETED_BY_AUTHOR"], [32, 2, 1, "", "DELETED_BY_MODERATOR"], [32, 2, 1, "", "DELETED_BY_UNKNOWN"], [32, 2, 1, "", "EXISTS"]], "PyPtt.PyPtt.exceptions": [[28, 3, 1, "", "CanNotUseSearchPostCode"], [28, 3, 1, "", "CantComment"], [28, 3, 1, "", "CantResponse"], [28, 3, 1, "", "ConnectError"], [28, 3, 1, "", "ConnectionClosed"], [28, 3, 1, "", "HostNotSupport"], [28, 3, 1, "", "LoginError"], [28, 3, 1, "", "LoginTooOften"], [28, 3, 1, "", "MailboxFull"], [28, 3, 1, "", "MultiThreadOperated"], [28, 3, 1, "", "NeedModeratorPermission"], [28, 3, 1, "", "NoFastComment"], [28, 3, 1, "", "NoMoney"], [28, 3, 1, "", "NoPermission"], [28, 3, 1, "", "NoSearchResult"], [28, 3, 1, "", "NoSuchBoard"], [28, 3, 1, "", "NoSuchPost"], [28, 3, 1, "", "NoSuchUser"], [28, 3, 1, "", "OnlySecureConnection"], [28, 3, 1, "", "RequireLogin"], [28, 3, 1, "", "SetConnectMailFirst"], [28, 3, 1, "", "UnregisteredUser"], [28, 3, 1, "", "UseTooManyResources"], [28, 3, 1, "", "UserHasPreviouslyBeenBanned"], [28, 3, 1, "", "WrongIDorPassword"], [28, 3, 1, "", "WrongPassword"]], "PyPtt.ReplyTo": [[32, 2, 1, "", "BOARD"], [32, 2, 1, "", "BOARD_MAIL"], [32, 2, 1, "", "MAIL"]], "PyPtt.SearchType": [[32, 2, 1, "", "AUTHOR"], [32, 2, 1, "", "COMMENT"], [32, 2, 1, "", "KEYWORD"], [32, 2, 1, "", "MARK"], [32, 2, 1, "", "MONEY"]], "PyPtt.UserField": [[32, 2, 1, "", "account_verified"], [32, 2, 1, "", "activity"], [32, 2, 1, "", "chess"], [32, 2, 1, "", "five_chess"], [32, 2, 1, "", "illegal_post"], [32, 2, 1, "", "last_login_date"], [32, 2, 1, "", "last_login_ip"], [32, 2, 1, "", "legal_post"], [32, 2, 1, "", "login_count"], [32, 2, 1, "", "mail"], [32, 2, 1, "", "money"], [32, 2, 1, "", "ptt_id"], [32, 2, 1, "", "signature_file"]]}, "objtypes": {"0": "py:module", "1": "py:function", "2": "py:attribute", "3": "py:exception"}, "objnames": {"0": ["py", "module", "Python \u6a21\u7d44"], "1": ["py", "function", "Python \u51fd\u5f0f"], "2": ["py", "attribute", "Python \u5c6c\u6027"], "3": ["py", "exception", "Python \u4f8b\u5916"]}, "titleterms": {"bucket": 0, "change_pw": 1, "comment": 2, "del_mail": 3, "del_post": 4, "get_aid_from_url": 5, "get_board_info": 6, "get_board_list": 7, "get_bottom_post_list": 8, "get_favourite_board": 9, "get_mail": 10, "get_newest_index": 11, "get_post": 12, "get_tim": 13, "get_us": 14, "give_money": 15, "api": 16, "ptt": 16, "init": 17, "login": 18, "logout": 18, "mail": 19, "mark_post": 20, "post": 21, "reply_post": 22, "search_us": 23, "set_board_titl": 24, "faq": 29, "jupyt": 29, "the": 29, "event": 29, "loop": 29, "is": 29, "alreadi": 29, "run": 29, "mac": 29, "websocket": 29, "ssl": 29, "pyptt": [30, 31], "pypi": 30, "python": 31, "host": 32, "languag": 32, "connectmod": 32, "newindex": 32, "searchtyp": 32, "replyto": 32, "commenttyp": 32, "poststatus": 32, "marktyp": 32, "userfield": 32, "commentfield": 32, "favouriteboardfield": 32, "mailfield": 32, "boardfield": 32, "postfield": 32}, "envversion": {"sphinx.domains.c": 2, "sphinx.domains.changeset": 1, "sphinx.domains.citation": 1, "sphinx.domains.cpp": 6, "sphinx.domains.index": 1, "sphinx.domains.javascript": 2, "sphinx.domains.math": 2, "sphinx.domains.python": 3, "sphinx.domains.rst": 2, "sphinx.domains.std": 2, "sphinx": 56}})