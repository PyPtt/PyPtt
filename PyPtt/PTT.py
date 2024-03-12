from __future__ import annotations

import functools
import threading
from typing import Dict, Tuple, Callable, List, Optional, Any

from SingleLog import LogLevel, DefaultLogger

from . import _api_bucket, __version__
from . import _api_change_pw
from . import _api_comment
from . import _api_del_post
from . import _api_get_board_info
from . import _api_get_board_list
from . import _api_get_bottom_post_list
from . import _api_get_favourite_board
from . import _api_get_newest_index
from . import _api_get_post
from . import _api_get_time
from . import _api_get_user
from . import _api_give_money
from . import _api_loginout
from . import _api_mail
from . import _api_mark_post
from . import _api_post
from . import _api_reply_post
from . import _api_search_user
from . import _api_set_board_title
from . import check_value
from . import config
from . import connect_core
from . import data_type
from . import i18n
from . import lib_util


class API:
    def __init__(self, language: data_type.Language = data_type.Language.MANDARIN, log_level: LogLevel = LogLevel.INFO,
                 screen_timeout: int = 3.0, screen_long_timeout: int = 10.0, screen_post_timeout: int = 60.0,
                 connect_mode: data_type.ConnectMode = data_type.ConnectMode.WEBSOCKETS, port: int = 23,
                 logger_callback: Optional[Callable] = None, host=data_type.HOST.PTT1,
                 check_update: bool = True) -> None:

        """

        初始化 PyPtt。

        Args:
            language (:ref:`language`): PyPtt 顯示訊息的語言。預設為 **MANDARIN**。
            log_level (LogLevel_): PyPtt 顯示訊息的等級。預設為 **INFO**。
            screen_timeout (int): 經過 screen_timeout 秒之後， PyPtt 將會判定無法判斷目前畫面的狀況。預設為 **3 秒**。
            screen_long_timeout (int): 經過 screen_long_timeout 秒之後，PyPtt 將會判定無法判斷目前畫面的狀況，這會用在較長的等待時間，例如踢掉其他連線等等。預設為 **10 秒**。
            screen_post_timeout (int): 經過 screen_post_timeout 秒之後，PyPtt 將會判定無法判斷目前畫面的狀況，這會用在較長的等待時間，例如發佈文章等等。預設為 **60 秒**。
            connect_mode (:ref:`connect-mode`): PyPtt 連線的模式。預設為 **WEBSOCKETS**。
            logger_callback (Callable): PyPtt 顯示訊息的 callback。預設為 None。
            port (int): PyPtt 連線的 port。預設為 **23**。
            host (:ref:`host`): PyPtt 連線的 PTT 伺服器。預設為 **PTT1**。
            check_update (bool): 是否檢查 PyPtt 的更新。預設為 **True**。

        Returns:
            None

        範例::

            import PyPtt
            ptt_bot = PyPtt.API()

        參考: :ref:`language`、LogLevel_、:ref:`connect-mode`、:ref:`host`

        .. _LogLevel: https://github.com/PttCodingMan/SingleLog/blob/d7c19a1b848dfb1c9df8201f13def9a31afd035c/SingleLog/SingleLog.py#L22
        """

        self.logger = None

        if not isinstance(log_level, LogLevel):
            raise TypeError('[PyPtt] log_level must be LogLevel')

        if logger_callback is not None and not callable(logger_callback):
            raise TypeError('[PyPtt] logger_callback must be callable')

        self.logger = DefaultLogger('PyPtt', log_level, handler=logger_callback, **config.LOGGER_CONFIG)

        if not isinstance(language, data_type.Language):
            raise TypeError('[PyPtt] language must be PyPtt.Language')

        self.config = config.Config()
        self.config.log_level = log_level

        self.config.language = language
        i18n.load(self.config.language)

        self.is_mailbox_full: bool = False
        self.is_registered_user: bool = False
        self.process_picks: int = 0

        self.ptt_id: str = ''
        self._ptt_pw: str = ''
        self._is_login: bool = False

        check_value.check_type(host, (data_type.HOST, str), 'host')
        check_value.check_type(screen_timeout, float, 'screen_timeout')
        check_value.check_type(screen_long_timeout, float, 'screen_long_timeout')

        if screen_timeout != 0:
            self.config.screen_timeout = screen_timeout
        if screen_long_timeout != 0:
            self.config.screen_long_timeout = screen_long_timeout
        if screen_post_timeout != 0:
            self.config.screen_post_timeout = screen_post_timeout

        self.config.host = host
        self.host = host

        check_value.check_type(port, int, 'port')
        check_value.check_range(port, 1, 65535 - 1, 'port')
        self.config.port = port

        check_value.check_type(connect_mode, data_type.ConnectMode, 'connect_mode')
        if host in [data_type.HOST.PTT1, data_type.HOST.PTT2] and connect_mode is data_type.ConnectMode.TELNET:
            raise ValueError('[PyPtt] TELNET is not available on PTT1 and PTT2')
        self.config.connect_mode = connect_mode

        self.connect_core = connect_core.API(self.config)
        self._exist_board_list = []
        self._board_info_list = dict()
        self._moderators = dict()
        self._thread_id = threading.get_ident()
        self._goto_board_list = []
        self._board_info_list = dict()
        self._newest_index_data = data_type.TimedDict(timeout=3)

        self.logger.debug('ThreadID', self._thread_id)

        self.logger.info(i18n.welcome)

        self.logger.info('PyPtt', i18n.init)

        if self.config.connect_mode == data_type.ConnectMode.TELNET:
            self.logger.info(i18n.set_connect_mode, i18n.connect_mode_TELNET)
        elif self.config.connect_mode == data_type.ConnectMode.WEBSOCKETS:
            self.logger.info(i18n.set_connect_mode, i18n.connect_mode_WEBSOCKET)

        if self.config.language == data_type.Language.MANDARIN:
            self.logger.info(i18n.set_up_lang_module, i18n.mandarin_module)
        elif self.config.language == data_type.Language.ENGLISH:
            self.logger.info(i18n.set_up_lang_module, i18n.english_module)

        if self.config.host == data_type.HOST.PTT1:
            self.logger.info(i18n.set_connect_host, i18n.PTT)
        elif self.config.host == data_type.HOST.PTT2:
            self.logger.info(i18n.set_connect_host, i18n.PTT2)
        elif self.config.host == data_type.HOST.LOCALHOST:
            self.logger.info(i18n.set_connect_host, i18n.localhost)
        else:
            self.logger.info(i18n.set_connect_host, self.config.host)

        if check_update:
            version_compare, remote_version = lib_util.sync_version()

            if version_compare is data_type.Compare.SMALLER:
                self.logger.info(i18n.current_version, __version__)
                self.logger.info(i18n.new_version, remote_version)
            elif version_compare is data_type.Compare.BIGGER:
                self.logger.info(i18n.development_version, __version__)
            else:
                self.logger.info(i18n.latest_version, __version__)
        else:
            self.logger.info(i18n.current_version, __version__)

    def __del__(self):
        if self.logger:
            self.logger.debug(i18n.goodbye)

    def login(self, ptt_id: str, ptt_pw: str, kick_other_session: bool = False) -> None:

        """
        登入 PTT。

        Args:
            ptt_id (str): PTT ID。
            ptt_pw (str): PTT 密碼。
            kick_other_session (bool): 是否踢掉其他登入的 session。預設為 False。

        Returns:
            None

        Raises:
            LoginError: 登入失敗。
            WrongIDorPassword: 帳號或密碼錯誤。
            OnlySecureConnection: 只能使用安全連線。
            ResetYourContactEmail: 請先至信箱設定連絡信箱。

        範例::

            import PyPtt
            ptt_bot = PyPtt.API()

            try:
                ptt_bot.login(
                    ptt_id='ptt_id', ptt_pw='ptt_pw', kick_other_session=True)
            except PyPtt.LoginError:
                print('登入失敗')
            except PyPtt.WrongIDorPassword:
                print('帳號密碼錯誤')
            except PyPtt.OnlySecureConnection:
                print('只能使用安全連線')
            except PyPtt.ResetYourContactEmail:
                print('請先至信箱設定連絡信箱')

        """

        _api_loginout.login(self, ptt_id, ptt_pw, kick_other_session)

    def logout(self) -> None:
        """
        登出 PTT。

        Returns:
            None

        範例::

            import PyPtt
            ptt_bot = PyPtt.API()

            try:
                # .. login ..
                # .. do something ..
            finally:
                ptt_bot.logout()

        """

        _api_loginout.logout(self)

    def get_time(self) -> str:

        """
        取得 PTT 系統時間。

        Returns:
            None

        範例::

            import PyPtt
            ptt_bot = PyPtt.API()

            try:
                # .. login ..
                time = ptt_bot.get_time()
                # .. do something ..
            finally:
                ptt_bot.logout()
        """

        return _api_get_time.get_time(self)

    def get_post(self, board: str, aid: Optional[str] = None, index: Optional[int] = None,
                 search_type: Optional[data_type.SearchType] = None, search_condition: Optional[str] = None,
                 search_list: Optional[List[str]] = None, query: bool = False) -> Dict:
        """
        取得文章。

        Args:
            board (str): 看板名稱。
            aid (str): 文章編號。
            index: 文章編號。
            search_type (:ref:`search-type`): 搜尋類型。
            search_condition (str): 搜尋條件。
            search_list (List[str]): 搜尋清單。
            query (bool): 是否為查詢模式。

        Returns:
            Dict，文章內容。詳見 :ref:`post-field`

        Raises:
            RequireLogin: 需要登入。
            NoSuchBoard: 看板不存在。

        使用 AID 範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                post_info = ptt_bot.get_post('Python', aid='1TJH_XY0')
                # .. do something ..
            finally:
                ptt_bot.logout()

        使用 index 範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                post_info = ptt_bot.get_post('Python', index=1)
                # .. do something ..
            finally:
                ptt_bot.logout()

        | 更多範例參考 :ref:`取得文章 <check_post_status>`
        | 參考 :ref:`取得最新文章編號 <api-get-newest-index>`
        """
        return _api_get_post.get_post(
            self, board, aid=aid, index=index, search_type=search_type, search_condition=search_condition,
            search_list=search_list, query=query)

    def get_newest_index(self, index_type: data_type.NewIndex, board: Optional[str] = None,
                         search_type: Optional[data_type.SearchType] = None, search_condition: Optional[str] = None,
                         search_list: Optional[List[Tuple[Any | str]]] = None, ) -> int:
        """
        取得最新文章或信箱編號。

        Args:
            index_type (:ref:`new-index`): 編號類型。
            board (str): 看板名稱。
            search_list (List[str]): 搜尋清單。

        Returns:
            int，最新文章或信箱編號。

        Raises:
            RequireLogin: 需要登入。
            NoSuchBoard: 看板不存在。

        取得最新看板編號::

            import PyPtt

            ptt_bot = PyPtt.API()

            # get newest index of board
            try:
                # .. login ..
                newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, 'Python')
                # .. do something ..
            finally:
                ptt_bot.logout()


        取得最新文章編號使用搜尋::

            import PyPtt

            ptt_bot = PyPtt.API()

            search_list = [(PyPtt.SearchType.KEYWORD, 'PyPtt')]

            try:
                # .. login ..
                newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, 'Python', search_list=search_list)
                # .. do something ..
            finally:
                ptt_bot.logout()

        取得最新信箱編號::

            import PyPtt

            ptt_bot = PyPtt.API()

            # get newest index of mail
            try:
                # .. login ..
                newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.MAIL)
                # .. do something ..
            finally:
                ptt_bot.logout()

        參考 :ref:`搜尋編號種類 <new-index>`、:ref:`取得文章 <api-get-post>`
        """

        return _api_get_newest_index.get_newest_index(
            self, index_type, board, search_type, search_condition, search_list)

    def post(self, board: str, title_index: int, title: str, content: str, sign_file: [str | int] = 0) -> None:
        """
        發文。

        Args:
            board (str): 看板名稱。
            title_index (int): 文章標題編號。
            title (str): 文章標題。
            content (str): 文章內容。
            sign_file  (str | int): 編號或隨機簽名檔 (x)，預設為 0 (不選)。

        Returns:
            None

        Raises:
            UnregisteredUser: 未註冊使用者。
            RequireLogin: 需要登入。
            NoSuchBoard: 看板不存在。
            NoPermission: 沒有發佈權限。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                ptt_bot.post(board='Test', title_index=1, title='PyPtt 程式貼文測試', content='測試內容', sign_file=0)
                # .. do something ..
            finally:
                ptt_bot.logout()

        """

        _api_post.post(self, board, title, content, title_index, sign_file)

    def comment(self, board: str, comment_type: data_type.CommentType, content: str, aid: Optional[str] = None,
                index: int = 0) -> None:
        """
        推文。

        Args:
            board (str): 看板名稱。
            comment_type (:ref:`comment-type`): 推文類型。
            content (str): 推文內容。
            aid (str): 文章編號。
            index (int): 文章編號。

        Returns:
            None

        Raises:
            UnregisteredUser: 未註冊使用者。
            RequireLogin: 需要登入。
            NoSuchBoard: 看板不存在。
            NoSuchPost: 文章不存在。
            NoPermission: 沒有推文權限。
            NoFastComment: 推文間隔太短。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                ptt_bot.comment(board='Test', comment_type=PyPtt.CommentType.PUSH, content='Comment by index', index=123)
                ptt_bot.comment(board='Test', comment_type=PyPtt.CommentType.PUSH, content='Comment by index', aid='17MrayxF')
                # .. do something ..
            finally:
                ptt_bot.logout()

        參考 :ref:`推文類型 <comment-type>`、:ref:`取得最新文章編號 <api-get-newest-index>`
        """

        _api_comment.comment(self, board, comment_type, content, aid, index)

    def get_user(self, user_id: str) -> Dict:

        """
        取得使用者資訊。

        Args:
            user_id (str): 使用者 ID。

        Returns:
            Dict，使用者資訊。詳見 :ref:`使用者資料欄位 <user-field>`

        Raises:
            RequireLogin: 需要登入。
            NoSuchUser: 使用者不存在。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                user_info = ptt_bot.get_user('CodingMan')
                # .. do something ..
            finally:
                ptt_bot.logout()

        參考 :ref:`使用者資料欄位 <user-field>`

        """

        return _api_get_user.get_user(self, user_id)

    def give_money(self, ptt_id: str, money: int, red_bag_title: Optional[str] = None,
                   red_bag_content: Optional[str] = None) -> None:

        """
        轉帳，詳見 `P 幣`_。

        .. _`P 幣`: https://pttpedia.fandom.com/zh/wiki/P%E5%B9%A3

        Args:
            ptt_id (str): PTT ID。
            money (int): 轉帳金額。
            red_bag_title (str): 紅包標題。
            red_bag_content (str): 紅包內容。

        Returns:
            None

        Raises:
            RequireLogin: 需要登入。
            UnregisteredUser: 未註冊使用者。
            NoSuchUser: 使用者不存在。
            NoMoney: 餘額不足。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                ptt_bot.give_money(ptt_id='CodingMan', money=100)
                # or
                ptt_bot.give_money('CodingMan', 100, red_bag_title='紅包袋標題', red_bag_content='紅包袋內文')
                # .. do something ..
            finally:
                ptt_bot.logout()

        """

        _api_give_money.give_money(self, ptt_id, money, red_bag_title, red_bag_content)

    def mail(self, ptt_id: str, title: str, content: str, sign_file: [int | str] = 0,
             backup: bool = True) -> None:

        """
        寄信。

        Args:
            ptt_id (str): PTT ID。
            title (str): 信件標題。
            content (str): 信件內容。
            sign_file (str | int): 編號或隨機簽名檔 (x)，預設為 0 (不選)。
            backup (bool): 如果是 True 寄信時將會備份信件，預設為 True。

        Returns:
            None

        Raises:
            RequireLogin: 需要登入。
            UnregisteredUser: 未註冊使用者。
            NoSuchUser: 使用者不存在。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                ptt_bot.mail(ptt_id='CodingMan', title='信件標題', content='信件內容')
                # .. do something ..
            finally:
                ptt_bot.logout()
        """

        _api_mail.mail(self, ptt_id, title, content, sign_file, backup)

    def get_all_boards(self) -> List[str]:

        """
        取得全站看板清單。

        Returns:
            List[str]，看板清單。

        Raises:
            RequireLogin: 需要登入。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                board_list = ptt_bot.get_all_boards()
                # .. do something ..
            finally:
                ptt_bot.logout()
        """

        return _api_get_board_list.get_board_list(self)

    def reply_post(self, reply_to: data_type.ReplyTo, board: str, content: str, sign_file: [str | int] = 0,
                   aid: Optional[str] = None, index: int = 0) -> None:

        """
        回覆文章。

        Args:
            reply_to (:ref:`reply-to`): 回覆類型。
            board (str): 看板名稱。
            content (str): 回覆內容。
            sign_file (str | int): 編號或隨機簽名檔 (x)，預設為 **0** (不選)。
            aid: 文章編號。
            index: 文章編號。

        Returns:
            None

        Raises:
            RequireLogin: 需要登入。
            NoSuchBoard: 看板不存在。
            NoSuchPost: 文章不存在。
            NoPermission: 沒有回覆權限。
            CantResponse: 已結案並標記, 不得回應。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                ptt_bot.reply_post(reply_to=PyPtt.ReplyTo.BOARD, board='Test', content='PyPtt 程式回覆測試', index=123)
                # .. do something ..
            finally:
                ptt_bot.logout()

        參考 :ref:`回覆類型 <reply-to>`、:ref:`取得最新文章編號 <api-get-newest-index>`
        """

        _api_reply_post.reply_post(self, reply_to, board, content, sign_file, aid, index)

    def set_board_title(self, board: str, new_title: str) -> None:
        """
        設定看板標題。

        Args:
            board (str): 看板名稱。
            new_title (str): 新標題。

        Returns:
            None

        Raises:
            RequireLogin: 需要登入。
            UnregisteredUser: 未註冊使用者。
            NoSuchBoard: 看板不存在。
            NeedModeratorPermission: 需要看板管理員權限。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                ptt_bot.set_board_title(board='Test', new_title='現在時間 %s' % datetime.datetime.now())
                # .. do something ..
            finally:
                ptt_bot.logout()

        """

        _api_set_board_title.set_board_title(self, board, new_title)

    def mark_post(self, mark_type: int, board: str, aid: Optional[str] = None, index: int = 0, search_type: int = 0,
                  search_condition: Optional[str] = None) -> None:
        """
        標記文章。

        Args:
            mark_type (:ref:`mark-type`): 標記類型。
            board (str): 看板名稱。
            aid (str): 文章編號。
            index (int): 文章編號。
            search_type (:ref:`search-type`): 搜尋類型。
            search_condition (str): 搜尋條件。

        Returns:
            None

        Raises:
            RequireLogin: 需要登入。
            UnregisteredUser: 未註冊使用者。
            NoSuchBoard: 看板不存在。
            NoSuchPost: 文章不存在。
            NeedModeratorPermission: 需要看板管理員權限。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                ptt_bot.mark_post(mark_type=PyPtt.MarkType.M, board='Test', index=123)
                # .. do something ..
            finally:
                ptt_bot.logout()
        """

        _api_mark_post.mark_post(self, mark_type, board, aid, index, search_type, search_condition)

    def get_favourite_boards(self) -> List[dict]:
        """
        取得我的最愛清單。

        Returns:
            List[dict]，收藏看板清單，詳見 :ref:`favorite-board-field`。

        Raises:
            RequireLogin: 需要登入。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()

            try:
                # .. login ..
                favourite_boards = ptt_bot.get_favourite_boards()
                # .. do something ..
            finally:
                ptt_bot.logout()
        """

        return _api_get_favourite_board.get_favourite_board(self)

    def bucket(self, board: str, bucket_days: int, reason: str, ptt_id: str) -> None:
        """
        水桶。

        Args:
            board (str): 看板名稱。
            bucket_days (int): 水桶天數。
            reason (str): 水桶原因。
            ptt_id (str): PTT ID。

        Returns:
            None

        Raises:
            RequireLogin: 需要登入。
            UnregisteredUser: 未註冊使用者。
            NoSuchBoard: 看板不存在。
            NoSuchUser: 使用者不存在。
            NeedModeratorPermission: 需要看板管理員權限。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                ptt_bot.bucket(board='Test', bucket_days=7, reason='PyPtt 程式水桶測試', ptt_id='test')
                # .. do something ..
            finally:
                ptt_bot.logout()

        """

        _api_bucket.bucket(self, board, bucket_days, reason, ptt_id)

    def search_user(self, ptt_id: str, min_page: Optional[int] = None, max_page: Optional[int] = None) -> List[str]:
        """
        搜尋使用者。

        Args:
            ptt_id (str): PTT ID。
            min_page (int): 最小頁數。
            max_page (int): 最大頁數。

        Returns:
            List[str]，搜尋結果。

        Raises:
            RequireLogin: 需要登入。
            UnregisteredUser: 未註冊使用者。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                search_result = ptt_bot.search_user(ptt_id='Coding')
                # .. do something ..
            finally:
                ptt_bot.logout()
        """

        return _api_search_user.search_user(self, ptt_id, min_page, max_page)

    def get_board_info(self, board: str, get_post_types: bool = False) -> Dict:
        """
        取得看板資訊。

        Args:
            board (str): 看板名稱。
            get_post_types (bool): 是否取得文章類型，例如：八卦板的「問卦」。

        Returns:
            Dict，看板資訊，詳見 :ref:`board-field`。

        Raises:
            RequireLogin: 需要登入。
            NoSuchBoard: 看板不存在。
            NoPermission: 沒有權限。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                board_info = ptt_bot.get_board_info(board='Test')
                # .. do something ..
            finally:
                ptt_bot.logout()
        """

        return _api_get_board_info.get_board_info(self, board, get_post_types, call_by_others=False)

    def get_mail(self, index: int, search_type: Optional[data_type.SearchType] = None,
                 search_condition: Optional[str] = None,
                 search_list: Optional[list] = None) -> Dict:
        """
        取得信件。

        Args:
            index (int): 信件編號。
            search_type (:ref:`search-type`): 搜尋類型。
            search_condition: 搜尋條件。
            search_list: 搜尋清單。

        Returns:
            Dict，信件資訊，詳見 :ref:`mail-field`。

        Raises:
            RequireLogin: 需要登入。
            NoSuchMail: 信件不存在。
            NoPermission: 沒有權限。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                mail = ptt_bot.get_mail(index=1)
                # .. do something ..
            finally:
                ptt_bot.logout()

        參考 :doc:`get_newest_index`
        """

        return _api_mail.get_mail(self, index, search_type, search_condition, search_list)

    def del_mail(self, index: int) -> None:
        """
        刪除信件。

        Args:
            index (int): 信件編號。

        Returns:
            None

        Raises:
            RequireLogin: 需要登入。
            UnregisteredUser: 未註冊使用者。
            MailboxFull: 信箱已滿。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                ptt_bot.del_mail(index=1)
                # .. do something ..
            finally:
                ptt_bot.logout()

        參考 :doc:`get_newest_index`
        """

        _api_mail.del_mail(self, index)

    def change_pw(self, new_password: str) -> None:
        """
        更改密碼。
        備註：因批踢踢系統限制，最長密碼為 8 碼。

        Args:
            new_password (str): 新密碼。

        Returns:
            None

        Raises:
            RequireLogin: 需要登入。
            SetContactMailFirst: 需要先設定聯絡信箱。
            WrongPassword: 密碼錯誤。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                ptt_bot.change_pw(new_password='123456')
                # .. do something ..
            finally:
                ptt_bot.logout()
        """

        _api_change_pw.change_pw(self, new_password)

    @functools.lru_cache(maxsize=64)
    def get_aid_from_url(self, url: str) -> Tuple[str, str]:
        """
        從網址取得看板名稱與文章編號。

        Args:
            url: 網址。

        Returns:
            Tuple[str, str]，看板名稱與文章編號。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            url = 'https://www.ptt.cc/bbs/Python/M.1565335521.A.880.html'
            board, aid = ptt_bot.get_aid_from_url(url)
        """

        return lib_util.get_aid_from_url(url)

    def get_bottom_post_list(self, board: str) -> List[str]:
        """
        取得看板置底文章清單。

        Args:
            board (str): 看板名稱。

        Returns:
            List[post]，置底文章清單，詳見 :ref:`post-field`。

        Raises:
            RequireLogin: 需要登入。
            NoSuchBoard: 看板不存在。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()

            try:
                # .. login ..
                bottom_post_list = ptt_bot.get_bottom_post_list(board='Python')
                # .. do something ..
            finally:
                ptt_bot.logout()
        """

        return _api_get_bottom_post_list.get_bottom_post_list(self, board)

    def del_post(self, board: str, aid: Optional[str] = None, index: int = 0) -> None:
        """
        刪除文章。

        Args:
            board (str): 看板名稱。
            aid (str): 文章編號。
            index (int): 文章編號。

        Returns:
            None

        Raises:
            RequireLogin: 需要登入。
            UnregisteredUser: 未註冊使用者。
            NoSuchBoard: 看板不存在。
            NoSuchPost: 文章不存在。
            NoPermission: 沒有權限。

        範例::

            import PyPtt

            ptt_bot = PyPtt.API()
            try:
                # .. login ..
                ptt_bot.del_post(board='Python', aid='1TJH_XY0')
                # .. do something ..
            finally:
                ptt_bot.logout()
        """

        _api_del_post.del_post(self, board, aid, index)

    def fast_post_step0(self, board: str, title: str, content: str, post_type: int) -> None:
        _api_post.fast_post_step0(self, board, title, content, post_type)

    def fast_post_step1(self, sign_file):
        _api_post.fast_post_step1(self, sign_file)


if __name__ == '__main__':
    print('PyPtt v ' + __version__)
    print('Maintained by CodingMan')
