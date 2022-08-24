import threading
from typing import Dict, Tuple

import requests
from SingleLog.log import Logger
from SingleLog.log import LoggerLevel

from . import _api_get_newest_index, _api_give_money, _api_mail, _api_get_board_list, _api_reply_post, \
    _api_set_board_title, _api_mark_post, _api_get_favourite_board, _api_bucket, _api_search_user, _api_get_board_info, \
    _api_change_pw, _api_get_bottom_post_list, _api_del_post
from . import _api_get_post
from . import _api_get_time
from . import _api_get_user
from . import _api_loginout
from . import _api_post
from . import _api_push
from . import check_value
from . import config
from . import connect_core
from . import i18n
from . import lib_util
from . import version
from .connect_core import ConnectMode
from .data_type import HOST, NewIndex, SearchType, ReplyTo


class API:
    def __init__(self, language: i18n.Lang = i18n.Lang.MANDARIN, log_level: LoggerLevel = Logger.INFO,
                 screen_timeout: int = 0, screen_long_timeout: int = 0, screen_post_timeout: int = 0,
                 connect_mode=ConnectMode.WEBSOCKETS, port: int = 0, log_handler=None, host=HOST.PTT1):

        if not isinstance(log_level, LoggerLevel):
            raise TypeError('[PyPtt] log_level must be integer')

        self.logger = Logger('PyPtt', log_level, handler=log_handler)

        self.logger.info(f'PyPtt v {version} developed by CoidngMan')

        self._mailbox_full = False
        self._ID = None
        self._login_status = False
        self.unregistered_user = True
        self.registered_user = False
        self.process_picks = 0

        self.config = config.Config()

        if not isinstance(language, i18n.Lang):
            raise TypeError('[PyPtt] language must be i18n.Lang')
        if not isinstance(screen_timeout, int):
            raise TypeError('[PyPtt] screen_timeout must be integer')
        if not isinstance(screen_long_timeout, int):
            raise TypeError('[PyPtt] screen_long_timeout must be integer')
        if (not isinstance(host, HOST)) and (not isinstance(host, str)):
            raise TypeError('[PyPtt] host must be HOST or a string')

        if screen_timeout != 0:
            self.config.screen_timeout = screen_timeout
        if screen_long_timeout != 0:
            self.config.screen_long_timeout = screen_long_timeout
        if screen_post_timeout != 0:
            self.config.screen_post_timeout = screen_post_timeout

        self.config.log_level = log_level

        self.config.language = language
        i18n.load(self.config.language)

        if self.config.language == i18n.Lang.MANDARIN:
            self.logger.info(i18n.chinese_traditional_module, i18n.init)
        elif self.config.language == i18n.Lang.ENGLISH:
            self.logger.info(i18n.english_module, i18n.init)

        self.config.host = host
        self.host = host

        if self.config.host == HOST.PTT1:
            self.logger.info(i18n.set_connect_host, i18n.PTT)
        elif self.config.host == HOST.PTT2:
            self.logger.info(i18n.set_connect_host, i18n.PTT2)
        elif self.config.host == HOST.LOCALHOST:
            self.logger.info(i18n.set_connect_host, i18n.localhost)
        else:
            self.logger.info(i18n.set_connect_host, self.config.host)

        if isinstance(connect_mode, ConnectMode):
            self.config.connect_mode = connect_mode
        else:
            raise ValueError('[PyPtt] Unknown connect_mode', connect_mode)

        check_value.check_type(int, 'port', port)
        if port == 0:
            port = self.config.port
        elif not 0 < port < 65535:
            raise ValueError('[PyPtt] Unknown port', port)
        else:
            self.config.port = port

        if self.config.connect_mode == ConnectMode.TELNET:
            self.logger.info(i18n.set_connect_mode, i18n.connect_mode_TELNET)
        elif self.config.connect_mode == ConnectMode.WEBSOCKETS:
            self.logger.info(i18n.set_connect_mode, i18n.connect_mode_WEBSOCKET)

        self.connect_core = connect_core.API(self.config)
        self._exist_board_list = list()
        self._board_info_list = dict()
        self._ModeratorList = dict()
        self._LastThrowWaterBallTime = 0
        self._thread_id = threading.get_ident()
        self._goto_board_list = list()
        self._board_info_list = dict()

        self.logger.debug('ThreadID', self._thread_id)
        self.logger.info('PyPtt', i18n.init)

        r = requests.get('https://raw.githubusercontent.com/PttCodingMan/PyPtt/master/PyPtt/version.py', timeout=3)
        remote_version = r.text
        remote_version = remote_version[remote_version.find("'") + 1:]
        remote_version = remote_version[:remote_version.find("'")]

        self.logger.debug('new version', remote_version)

        version_list = version.split('.')
        new_version_list = remote_version.split('.')

        update = False
        develop_version = False
        for i in range(len(remote_version)):
            if new_version_list[i] < version_list[i]:
                develop_version = True
                break
            if new_version_list[i] > version_list[i]:
                update = True
                break

        if update:
            self.logger.info(i18n.new_version, remote_version)
        elif develop_version:
            self.logger.info(i18n.development_version, version)
        else:
            self.logger.info(i18n.latest_version, version)

    def login(self, ptt_id: str, ptt_pw: str, kick_other_login: bool = False) -> None:

        """
        Login PTT.

        :param ptt_id: PTT id.
        :param ptt_pw: PTT password.
        :param kick_other_login: kick other session or not while login.
        :return: None
        """

        _api_loginout.login(self, ptt_id, ptt_pw, kick_other_login)

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

    def get_post(self, board: str, aid: str = None, index: int = 0, search_type: SearchType = SearchType.NOPE,
                 search_condition: str = None, search_list: list = None, query: bool = False) -> Dict:
        """
        Get the post of PTT.

        :param board: the board name of PTT.
        :param aid: (Choose between aid and index) the aid of the PTT post.
        :param index: (Choose between aid and index) the index of the PTT post.
        :param search_type: (Optional) the search type. Check data_type.SearchType.
        :param search_condition: (Optional) the search condition.
        :param search_list: (Optional) the search list including search type and search condition.
        :param query: (Optional) Enable query or not.
        :return: the dict of post.
        """
        return _api_get_post.get_post(self, board, aid, index, search_type, search_condition, search_list, query)

    def get_newest_index(
            self,
            index_type: NewIndex,
            board: str = None,
            search_type: SearchType = SearchType.NOPE,
            search_condition: str = None,
            search_list: list = None) -> int:

        """
        Get the index from board or mailbox.

        :param index_type:
        :param board:
        :param search_type:
        :param search_condition:
        :param search_list:
        :return the index:
        """

        return _api_get_newest_index.get_newest_index(self, index_type, search_type, search_condition, search_list,
                                                      board)

    def post(self, board: str, title_index: int, title: str, content: str, sign_file) -> None:
        """
        Post on PTT.

        :param board: The name of PTT board.
        :param title_index:
        :param title:
        :param content:
        :param sign_file:
        :return:
        """

        return _api_post.post(self, board, title, content, title_index, sign_file)

    def comment(self, board: str, comment_type: int, comment_content: str, post_aid: str = None,
                post_index: int = 0) -> None:
        """
        Comment.

        :param board: The name of PTT board.
        :param comment_type: The comment type. Check data_type.CommentType.
        :param comment_content: The comment content.
        :param post_aid: The aid of post. Choose one between post_index.
        :param post_index: The index of post. Choose one between post_aid.
        :return: None
        """

        _api_push.push(self, board, comment_type, comment_content, post_aid, post_index)

    def get_user(self, user_id) -> Dict:

        """
        Get the information of the PTT user.

        :param user_id:
        :return: the user info in dict.
        """

        return _api_get_user.get_user(self, user_id)

    def give_money(self, ptt_id: str, money: int) -> None:

        """
        Give money to ptt user.

        :param ptt_id: The PTT user.
        :param money: The number of money.
        :return: None
        """

        return _api_give_money.give_money(self, ptt_id, money)

    def mail(self, ptt_id: str, title: str, content: str, sign_file, backup: bool = True) -> None:

        """
        Mail to the PTT user.

        :param ptt_id: The PTT user.
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

    def reply_post(self, reply_to: ReplyTo, board: str, content: str, sign_file=0, post_aid: str = None,
                   post_index: int = 0) -> None:

        """
        Replay the post.

        :param reply_to: The place you want to reply to. (Check data_type.ReplyTo)
        :param board: The board name.
        :param content: The reply content.
        :param sign_file: The sign file.
        :param post_aid: The aid of the post.
        :param post_index: The index of the post.
        :return: None
        """

        _api_reply_post.reply_post(self, reply_to, board, content, sign_file, post_aid, post_index)

    def set_board_title(self, board: str, new_title: str) -> None:

        """
        Set the title of the board.
        :param board: The board name.
        :param new_title: The new title of the board.
        :return: None
        """

        _api_set_board_title.set_board_title(self, board, new_title)

    def mark_post(self, mark_type: int, board: str, post_aid: str = None, post_index: int = 0, search_type: int = 0,
                  search_condition: str = None) -> None:

        """
        Mark the post.

        :param mark_type: The mark type. (Check data_type.MarkType)
        :param board: The board name.
        :param post_aid: The aid of the post.
        :param post_index: The index of the post.
        :param search_type: (Optional) the search type. Check data_type.SearchType.
        :param search_condition: (Optional) the search condition.
        :return: None
        """

        _api_mark_post.mark_post(self, mark_type, board, post_aid, post_index, search_type, search_condition)

    def get_favourite_boards(self) -> list:
        """
        Get the favourite boards.
        :return: the list of favourite boards.
        """

        return _api_get_favourite_board.get_favourite_board(self)

    def bucket(self, board: str, bucket_days: int, reason: str, ptt_id: str) -> None:

        """
        Bucket the PTT user.

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

        :param ptt_id: All or part of the PTT id.
        :param min_page:
        :param max_page:
        :return:
        """

        return _api_search_user.search_user(self, ptt_id, min_page, max_page)

    def get_board_info(self, board: str, get_post_kind: bool = False) -> Dict:

        return _api_get_board_info.get_board_info(self, board, get_post_kind, call_by_others=False)

    def get_mail(self, index: int, search_type: int = 0, search_condition: str = None, search_list: list = None):

        return _api_mail.get_mail(self, index, search_type, search_condition, search_list)

    def del_mail(self, index) -> None:

        _api_mail.del_mail(self, index)

    def change_pw(self, new_password) -> None:

        _api_change_pw.change_pw(self, new_password)

    def get_aid_from_url(self, url: str) -> Tuple[str, str]:

        return lib_util.get_aid_from_url(url)

    def get_bottom_post_list(self, board: str) -> list:

        return _api_get_bottom_post_list.get_bottom_post_list(self, board)

    def del_post(self, board, post_aid: str = None, post_index: int = 0) -> None:

        _api_del_post.del_post(self, board, post_aid, post_index)

    def fast_post_step0(self, board: str, title: str, content: str, post_type: int) -> None:
        _api_post.fast_post_step0(self, board, title, content, post_type)

    def fast_post_step1(self, sign_file):
        _api_post.fast_post_step1(self, sign_file)


if __name__ == '__main__':
    print('PyPtt v ' + version)
    print('Developed by CodingMan')
    print('Github: @PttCodingMan')
