from __future__ import annotations

import threading
from typing import Dict, Tuple, Callable, List

from SingleLog import LogLevel
from SingleLog import Logger

from . import _api_bucket
from . import _api_change_pw
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
from . import _api_push
from . import _api_reply_post
from . import _api_search_user
from . import _api_set_board_title
from . import check_value
from . import config
from . import connect_core
from . import data_type
from . import i18n
from . import lib_util
from . import version


class API:
    """
    這個 API 類別實作了目前 PyPtt 支援 PTT 與 PTT2 的所有操作
    """

    def __init__(self, language: data_type.Language = data_type.Language.MANDARIN, log_level: LogLevel = LogLevel.INFO,
                 screen_timeout: int = 3.0, screen_long_timeout: int = 10.0, screen_post_timeout: int = 60.0,
                 connect_mode: data_type.ConnectMode = data_type.ConnectMode.WEBSOCKETS, port: int = 23,
                 logger_callback: Callable = None, host=data_type.HOST.PTT1):

        """
        初始化 PyPtt.

        Args:
            language (Language): PyPtt 顯示訊息的語言。預設為 **Language.MANDARIN**。
            log_level: PyPtt 顯示訊息的等級。預設為 **LogLevel.INFO**。
            screen_timeout: 經過 screen_timeout 秒之後， PyPtt 將會判定無法判斷目前畫面的狀況。預設為 **3 秒**。
            screen_long_timeout: 經過 screen_long_timeout 秒之後，PyPtt 將會判定無法判斷目前畫面的狀況，這會用在較長的等待時間，例如踢掉其他連線等等。預設為 **10 秒**。
            screen_post_timeout: 經過 screen_post_timeout 秒之後，PyPtt 將會判定無法判斷目前畫面的狀況，這會用在較長的等待時間，例如發佈文章等等。預設為 **60 秒**。
            connect_mode: PyPtt 連線的模式。預設為 **ConnectMode.WEBSOCKETS**。
            logger_callback: PyPtt 顯示訊息的 callback function。預設為 None。
            host: PyPtt 連線的 PTT 伺服器。預設為 **HOST.PTT1**。

        Returns:
            None

        範例::

            import PyPtt
            ptt_bot = PyPtt.API()

        """

        self.logger = None

        if not isinstance(log_level, LogLevel):
            raise TypeError('[PyPtt] log_level must be LogLevel')

        self.logger = Logger('PyPtt', log_level)

        if logger_callback is not None and not callable(logger_callback):
            raise TypeError('[PyPtt] logger_callback must be callable')

        self.logger = Logger('PyPtt', log_level, callback=logger_callback, **config.LOGGER_CONFIG)

        if not isinstance(language, data_type.Language):
            raise TypeError('[PyPtt] language must be PyPtt.Language')

        self.config = config.Config()
        self.config.log_level = log_level

        self.config.language = language
        i18n.load(self.config.language)

        config.LOGGER_CONFIG['key_word_success'].append(i18n.success)

        config.LOGGER_CONFIG['key_word_fails'].append(i18n.retry)

        self.is_mailbox_full: bool = False
        self.is_registered_user: bool = False
        self.process_picks: int = 0

        self._ptt_id: str = ''
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
        self._ModeratorList = dict()
        # self._last_throw_water_ball_time = 0
        self._thread_id = threading.get_ident()
        self._goto_board_list = []
        self._board_info_list = dict()

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

        version_compare, remote_version = lib_util.sync_version()

        if version_compare is data_type.Compare.SMALLER:
            self.logger.info(i18n.current_version, version)
            self.logger.info(i18n.new_version, remote_version)
        elif version_compare is data_type.Compare.BIGGER:
            self.logger.info(i18n.development_version, version)
        else:
            self.logger.info(i18n.latest_version, version)

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
            PyPtt.LoginError: 登入失敗。
            PyPtt.WrongIDorPassword: 帳號或密碼錯誤。
            PyPtt.LoginTooOften: 登入太頻繁。

        範例::

            from PyPtt import PTT
            ptt_bot = PTT.API()

            try:
                ptt_bot.login(
                    ptt_id='ptt_id', ptt_pw='ptt_pw', kick_other_session=True)
            except PyPtt.LoginError:
                logger.info('登入失敗')
            except PyPtt.WrongIDorPassword:
                logger.info('帳號密碼錯誤')
            except PyPtt.LoginTooOften:
                logger.info('請稍等一下再登入')

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

            ptt_bot.logout()
        """

        _api_loginout.logout(self)

    def get_time(self) -> str:

        """
        取得 PTT 系統時間。

        Returns:
            None
        """

        return _api_get_time.get_time(self)

    def get_post(self, board: str, aid: [str | None] = None, index: int = 0,
                 search_type: data_type.SearchType = data_type.SearchType.NOPE, search_condition: [str | None] = None,
                 search_list: [list | None] = None, query: bool = False) -> Dict:
        """
        取得文章。

        Args:
            board: 看板名稱。
            aid: 文章編號。
            index: 文章編號。
            search_type: 搜尋類型。
            search_condition: 搜尋條件。
            search_list: 搜尋清單。
            query: 是否為查詢模式。

        Returns:
            Dict，文章內容。

        """
        return _api_get_post.get_post(
            self, board, aid=aid, index=index, search_type=search_type, search_condition=search_condition,
            search_list=search_list, query=query)

    def get_newest_index(self, index_type: data_type.NewIndex, board: [str | None] = None,
                         search_type: data_type.SearchType = data_type.SearchType.NOPE,
                         search_list: [list | None] = None, search_condition: [str | None] = None) -> int:

        """
        取得最新文章或信箱編號。

        Args:
            index_type: 編號類型。NewIndex.BOARD 或 NewIndex.MAIL。
            board: 看板名稱。
            search_type: 搜尋類型。
            search_list: 搜尋清單。
            search_condition: 搜尋條件。

        Returns:
            int，最新文章或信箱編號。

        """

        return _api_get_newest_index.get_newest_index(
            self, index_type, board, search_type, search_condition, search_list)

    def post(self, board: str, title_index: int, title: str, content: str, sign_file: [str | int]) -> None:
        """
        發文。

        Args:
            board: 看板名稱。
            title_index: 文章標題編號。
            title: 文章標題。
            content: 文章內容。
            sign_file: 簽名檔名稱或編號。

        Returns:
            None

        """

        _api_post.post(self, board, title, content, title_index, sign_file)

    def comment(self, board: str, comment_type: data_type.CommentType, comment_content: str, aid: [str | None] = None,
                index: int = 0) -> None:
        """
        推文。

        Args:
            board: 看板名稱。
            comment_type: 推文類型。
            comment_content: 推文內容。
            aid: 文章編號。
            index: 文章編號。

        Returns:
            None

        """

        _api_push.push(self, board, comment_type, comment_content, aid, index)

    def get_user(self, user_id) -> Dict:

        """
        取得使用者資訊。

        Args:
            user_id: 使用者 ID。

        Returns:
            Dict，使用者資訊。

        """

        return _api_get_user.get_user(self, user_id)

    def give_money(self, ptt_id: str, money: int, red_bag_title: str = '', red_bag_content: str = '') -> None:

        """
        轉帳。

        Args:
            ptt_id: PTT ID。
            money: 轉帳金額。
            red_bag_title: 紅包標題。
            red_bag_content: 紅包內容。

        Returns:
            None

        """

        _api_give_money.give_money(self, ptt_id, money, red_bag_title, red_bag_content)

    def mail(self, ptt_id: str, title: str, content: str, sign_file, backup: bool = True) -> None:

        """
        寄信。

        Args:
            ptt_id: PTT ID。
            title: 信件標題。
            content: 信件內容。
            sign_file: 簽名檔名稱或編號。
            backup: 是否備份信件。

        Returns:
            None
        """

        _api_mail.mail(self, ptt_id, title, content, sign_file, backup)

    def get_board_list(self) -> List[str]:

        """
        取得看板清單。

        Returns:
            List[str]，看板清單。
        """

        return _api_get_board_list.get_board_list(self)

    def reply_post(self, reply_to: data_type.ReplyTo, board: str, content: str, sign_file=0, aid: [str | None] = None,
                   index: int = 0) -> None:

        """
        回覆文章。

        Args:
            reply_to: 回覆類型。
            board: 看板名稱。
            content: 回覆內容。
            sign_file: 簽名檔名稱或編號。
            aid: 文章編號。
            index: 文章編號。

        Returns:
            None
        """

        _api_reply_post.reply_post(self, reply_to, board, content, sign_file, aid, index)

    def set_board_title(self, board: str, new_title: str) -> None:

        """
        設定看板標題。

        Args:
            board: 看板名稱。
            new_title: 新標題。

        Returns:
            None
        """

        _api_set_board_title.set_board_title(self, board, new_title)

    def mark_post(self, mark_type: int, board: str, aid: [str | None] = None, index: int = 0, search_type: int = 0,
                  search_condition: [str | None] = None) -> None:

        """
        標記文章。

        Args:
            mark_type: 標記類型。
            board: 看板名稱。
            aid: 文章編號。
            index: 文章編號。
            search_type: 搜尋類型。
            search_condition: 搜尋條件。

        Returns:
            None
        """

        _api_mark_post.mark_post(self, mark_type, board, aid, index, search_type, search_condition)

    def get_favourite_boards(self) -> list:
        """
        取得收藏看板清單。

        Returns:
            list，收藏看板清單。
        """

        return _api_get_favourite_board.get_favourite_board(self)

    def bucket(self, board: str, bucket_days: int, reason: str, ptt_id: str) -> None:

        """
        水桶。

        Args:
            board: 看板名稱。
            bucket_days: 水桶天數。
            reason: 水桶原因。
            ptt_id: PTT ID。

        Returns:
            None
        """

        _api_bucket.bucket(self, board, bucket_days, reason, ptt_id)

    def search_user(self, ptt_id: str, min_page: int = None, max_page: int = None) -> List[str]:

        """
        搜尋使用者。

        Args:
            ptt_id: PTT ID。
            min_page: 最小頁數。
            max_page: 最大頁數。

        Returns:
            List[str]，搜尋結果。
        """

        return _api_search_user.search_user(self, ptt_id, min_page, max_page)

    def get_board_info(self, board: str, get_post_types: bool = False) -> Dict:

        """
        取得看板資訊。

        Args:
            board: 看板名稱。
            get_post_types: 是否取得文章類型。

        Returns:
            Dict，看板資訊。
        """

        return _api_get_board_info.get_board_info(self, board, get_post_types, call_by_others=False)

    def get_mail(self, index: int, search_type: int = 0, search_condition: [str | None] = None,
                 search_list: [list | None] = None) -> Dict:

        """
        取得信件。

        Args:
            index: 信件編號。
            search_type: 搜尋類型。
            search_condition: 搜尋條件。
            search_list: 搜尋清單。

        Returns:
            Dict，信件資訊。
        """

        return _api_mail.get_mail(self, index, search_type, search_condition, search_list)

    def del_mail(self, index) -> None:

        """
        刪除信件。

        Args:
            index: 信件編號。

        Returns:
            None
        """

        _api_mail.del_mail(self, index)

    def change_pw(self, new_password) -> None:

        """
        更改密碼。

        Args:
            new_password: 新密碼。

        Returns:
            None
        """

        _api_change_pw.change_pw(self, new_password)

    def get_aid_from_url(self, url: str) -> Tuple[str, str]:

        """
        從網址取得看板名稱與文章編號。

        Args:
            url: 網址。

        Returns:
            Tuple，看板名稱與文章編號。
        """

        return lib_util.get_aid_from_url(url)

    def get_bottom_post_list(self, board: str) -> List[str]:

        """
        取得看板置底文章清單。

        Args:
            board: 看板名稱。

        Returns:
            List[str]，置底文章清單。
        """

        return _api_get_bottom_post_list.get_bottom_post_list(self, board)

    def del_post(self, board, aid: [str | None] = None, index: int = 0) -> None:
        """
        刪除文章。

        Args:
            board: 看板名稱。
            aid: 文章編號。
            index: 文章編號。

        Returns:
            None
        """

        _api_del_post.del_post(self, board, aid, index)

    def fast_post_step0(self, board: str, title: str, content: str, post_type: int) -> None:
        _api_post.fast_post_step0(self, board, title, content, post_type)

    def fast_post_step1(self, sign_file):
        _api_post.fast_post_step1(self, sign_file)


if __name__ == '__main__':
    print('PyPtt v ' + version)
    print('Maintained by CodingMan')
