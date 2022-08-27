import threading
from typing import Dict, Tuple

from SingleLog.log import Logger
from SingleLog.log import LoggerLevel

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
    def __init__(self, language: i18n.Lang = i18n.Lang.MANDARIN, log_level: LoggerLevel = Logger.INFO,
                 screen_timeout: int = 0, screen_long_timeout: int = 0, screen_post_timeout: int = 0,
                 connect_mode: data_type.ConnectMode = data_type.ConnectMode.WEBSOCKETS, port: int = 23,
                 log_handler=None, host=data_type.HOST.PTT1):

        if not isinstance(log_level, LoggerLevel):
            raise TypeError('[PyPtt] log_level must be integer')

        self.logger = Logger('PyPtt', log_level, handler=log_handler)

        if not isinstance(language, i18n.Lang):
            raise TypeError('[PyPtt] language must be i18n.Lang')

        self.config = config.Config()
        self.config.log_level = log_level

        self.config.language = language
        i18n.load(self.config.language)

        self.is_mailbox_full: bool = False
        self.is_registered_user: bool = False
        self.process_picks: int = 0

        self._ptt_id: str = ''
        self._ptt_pw: str = ''
        self._is_login: bool = False

        if (not isinstance(host, data_type.HOST)) and (not isinstance(host, str)):
            raise TypeError('[PyPtt] host must be HOST or a string')

        check_value.check_type(screen_timeout, int, 'screen_timeout')
        check_value.check_type(screen_long_timeout, int, 'screen_long_timeout')

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

        if self.config.language == i18n.Lang.MANDARIN:
            self.logger.info(i18n.set_up_lang_module, i18n.mandarin_module)
        elif self.config.language == i18n.Lang.ENGLISH:
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
        self.logger.debug(i18n.goodbye)

    def login(self, ptt_id: str, ptt_pw: str, kick_other_session: bool = False) -> None:

        """
        Login PTT.

        :param ptt_id: PTT id.
        :param ptt_pw: PTT password.
        :param kick_other_session: kick other session or not while login.
        :return: None
        """

        _api_loginout.login(self, ptt_id, ptt_pw, kick_other_session)

    def logout(self) -> None:
        """
        Logout PTT.

        :return: None
        """

        _api_loginout.logout(self)

    def get_time(self) -> str:

        """
        Get time of PTT.

        :return: None
        """

        return _api_get_time.get_time(self)

    def get_post(self, board: str, aid: str = None, index: int = 0,
                 search_type: data_type.SearchType = data_type.SearchType.NOPE, search_condition: str = None,
                 search_list: list = None, query: bool = False) -> Dict:
        """
        Get the post of PTT.

        :param board: The board name.
        :param aid: (Choose between aid and index) the aid of the PTT post.
        :param index: (Choose between aid and index) the index of the PTT post.
        :param search_type: (Optional) the search type. Check data_type.SearchType.
        :param search_condition: (Optional) the search condition.
        :param search_list: (Optional) the search list including search type and search condition.
        :param query: (Optional) Enable query or not.
        :return: The dict of post.
        """
        return _api_get_post.get_post(self, board, aid, index, search_type, search_condition, search_list, query)

    def get_newest_index(self, index_type: data_type.NewIndex, board: str = None,
                         search_type: data_type.SearchType = data_type.SearchType.NOPE, search_condition: str = None,
                         search_list: list = None) -> int:

        """
        Get the newest index from board or mailbox.

        :param index_type: The index type. Check data_type.NewIndex.
        :param board: The board name.
        :param search_type: (Optional) the search type. Check data_type.SearchType.
        :param search_condition: (Optional) the search condition.
        :param search_list: (Optional) the search list including search type and search condition.
        :return the index:
        """

        return _api_get_newest_index.get_newest_index(
            self, index_type, board, search_type, search_condition, search_list)

    def post(self, board: str, title_index: int, title: str, content: str, sign_file) -> None:
        """
        Post on PTT.

        :param board: The board name.
        :param title_index:
        :param title:
        :param content:
        :param sign_file:
        :return:
        """

        _api_post.post(self, board, title, content, title_index, sign_file)

    def comment(self, board: str, comment_type: data_type.CommentType, comment_content: str, aid: str = None,
                index: int = 0) -> None:
        """
        Comment the post.

        :param board: The name of PTT board.
        :param comment_type: The comment type. Check data_type.CommentType.
        :param comment_content: The comment content.
        :param aid: (Choose between aid and index) the aid of the PTT post.
        :param index: (Choose between aid and index) the index of the PTT post.
        :return: None
        """

        _api_push.push(self, board, comment_type, comment_content, aid, index)

    def get_user(self, user_id) -> Dict:

        """
        Get the information of The PTT user id.

        :param user_id: The PTT user id.
        :return: the user info in dict.
        """

        return _api_get_user.get_user(self, user_id)

    def give_money(self, ptt_id: str, money: int) -> None:

        """
        Give money to The PTT user id.

        :param ptt_id: The PTT user id.
        :param money: The number of money.
        :return: None
        """

        _api_give_money.give_money(self, ptt_id, money)

    def mail(self, ptt_id: str, title: str, content: str, sign_file, backup: bool = True) -> None:

        """
        Mail to The PTT user id.

        :param ptt_id: The PTT user id.
        :param title: The title of mail.
        :param content: The content of mail.
        :param sign_file: The sign file of mail.
        :param backup: If true the mail will store in your mailbox.
        :return: None
        """

        _api_mail.mail(self, ptt_id, title, content, sign_file, backup)

    def get_board_list(self) -> list:

        """
        Get the board list.
        :return: The board list.
        """

        return _api_get_board_list.get_board_list(self)

    def reply_post(self, reply_to: data_type.ReplyTo, board: str, content: str, sign_file=0, aid: str = None,
                   index: int = 0) -> None:

        """
        Replay the post.

        :param reply_to: The place you want to reply to. (Check data_type.ReplyTo)
        :param board: The board name.
        :param content: The reply content.
        :param sign_file: The sign file.
        :param aid: (Choose between aid and index) the aid of the PTT post.
        :param index: (Choose between aid and index) the index of the PTT post.
        :return: None
        """

        _api_reply_post.reply_post(self, reply_to, board, content, sign_file, aid, index)

    def set_board_title(self, board: str, new_title: str) -> None:

        """
        Set the title of the board.
        :param board: The board name.
        :param new_title: The new title of the board.
        :return: None
        """

        _api_set_board_title.set_board_title(self, board, new_title)

    def mark_post(self, mark_type: int, board: str, aid: str = None, index: int = 0, search_type: int = 0,
                  search_condition: str = None) -> None:

        """
        Mark the post.

        :param mark_type: The mark type. (Check data_type.MarkType)
        :param board: The board name.
        :param aid: (Choose between aid and index) the aid of the PTT post.
        :param index: (Choose between aid and index) the index of the PTT post.
        :param search_type: (Optional) the search type. Check data_type.SearchType.
        :param search_condition: (Optional) the search condition.
        :return: None
        """

        _api_mark_post.mark_post(self, mark_type, board, aid, index, search_type, search_condition)

    def get_favourite_boards(self) -> list:
        """
        Get the favourite boards.
        :return: the list of favourite boards.
        """

        return _api_get_favourite_board.get_favourite_board(self)

    def bucket(self, board: str, bucket_days: int, reason: str, ptt_id: str) -> None:

        """
        Bucket The PTT user id.

        :param board: The board name.
        :param bucket_days: The days of bucket.
        :param reason: The reason of bucket.
        :param ptt_id: The bucket PTT user.
        :return: None
        """

        _api_bucket.bucket(self, board, bucket_days, reason, ptt_id)

    def search_user(self, ptt_id: str, min_page: int = None, max_page: int = None) -> list:

        """
        Search the PTT users.

        :param ptt_id: All or part of the PTT user id.
        :param min_page: The min page of searching.
        :param max_page: The max page of searching.
        :return: The list of PTT users.
        """

        return _api_search_user.search_user(self, ptt_id, min_page, max_page)

    def get_board_info(self, board: str, get_post_types: bool = False) -> Dict:

        """
        Get the board information.

        :param board: The board name.
        :param get_post_types: If ture this api will return all the post types.
        :return: The dict of board information.
        """

        return _api_get_board_info.get_board_info(self, board, get_post_types, call_by_others=False)

    def get_mail(self, index: int, search_type: int = 0, search_condition: str = None,
                 search_list: list = None) -> Dict:

        """
        Get the mail.

        :param index: The index of mail.
        :param search_type: (Optional) the search type. Check data_type.SearchType.
        :param search_condition: (Optional) the search condition.
        :param search_list: (Optional) the search list including search type and search condition.
        :return: The dict of mail.
        """

        return _api_mail.get_mail(self, index, search_type, search_condition, search_list)

    def del_mail(self, index) -> None:

        """
        Del the mail.

        :param index: The index of mail.
        :return:
        """

        _api_mail.del_mail(self, index)

    def change_pw(self, new_password) -> None:

        """
        Change password!

        :param new_password: The new password.
        :return: None
        """

        _api_change_pw.change_pw(self, new_password)

    def get_aid_from_url(self, url: str) -> Tuple[str, str]:

        """
        Extract the board name and aid from the ptt url.

        :param url: The ptt url.
        :return: Tuple[board, aid]
        """

        return lib_util.get_aid_from_url(url)

    def get_bottom_post_list(self, board: str) -> list:

        """
        Get the bottom post list.

        :param board: The board name.
        :return: The list of the bottom posts.
        """

        return _api_get_bottom_post_list.get_bottom_post_list(self, board)

    def del_post(self, board, aid: str = None, index: int = 0) -> None:
        """
        Delete the post.
        :param board: The board name.
        :param aid: (Choose between aid and index) the aid of the PTT post.
        :param index: (Choose between aid and index) the index of the PTT post.
        :return: None
        """

        _api_del_post.del_post(self, board, aid, index)

    def fast_post_step0(self, board: str, title: str, content: str, post_type: int) -> None:
        _api_post.fast_post_step0(self, board, title, content, post_type)

    def fast_post_step1(self, sign_file):
        _api_post.fast_post_step1(self, sign_file)


if __name__ == '__main__':
    print('PyPtt v ' + version)
    print('Developed by CodingMan')
