import re
import threading
import time

import requests
from SingleLog.log import Logger
from SingleLog.log import LoggerLevel

from . import _api_get_time, _api_get_post, version, _api_get_newest_index, _api_loginout, _api_get_user
from . import _api_post
from . import check_value
from . import command
from . import config
from . import connect_core
from . import exceptions
from . import i18n
from . import lib_util
from . import screens
from .connect_core import ConnectMode
from .data_type import HOST, Board, NewIndex, SearchType


class API:
    def __init__(
            self,
            language: i18n.Lang = i18n.Lang.CHINESE,
            log_level: LoggerLevel = Logger.INFO,
            screen_timeout: int = 0,
            screen_long_timeout: int = 0,
            screen_post_timeout: int = 0,
            connect_mode=ConnectMode.WEBSOCKETS,
            port: int = 0,
            log_handler=None,
            host=HOST.PTT1):

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

        if self.config.language == i18n.Lang.CHINESE:
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

        r = requests.get('https://raw.githubusercontent.com/PttCodingMan/PyPtt/master/PyPtt/version.py')
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

    def get_post(
            self,
            board: str,
            aid: str = None,
            index: int = 0,
            search_type: SearchType = SearchType.NOPE,
            search_condition: str = None,
            search_list: list = None,
            query: bool = False) -> dict:
        """
        Get the post of PTT.
        :param board: the board name of PTT.
        :param aid: (Choose between aid and index) the aid of the PTT post.
        :param index: (Choose between aid and index) the index of the PTT post.
        :param search_type: (Optional) the search type. Check SearchType
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
        :return: the index from board or mailbox.
        """

        return _api_get_newest_index.get_newest_index(
            self,
            index_type,
            search_type,
            search_condition,
            search_list,
            board)

    def post(
            self,
            board: str,
            title_index: int,
            title: str,
            content: str,
            sign_file) -> None:
        """

        :param board:
        :param title_index:
        :param title:
        :param content:
        :param sign_file:
        :return:
        """

        return _api_post.post(
            self,
            board,
            title,
            content,
            title_index,
            sign_file)

    def comment(
            self,
            board: str,
            push_type: int,
            push_content: str,
            post_aid: str = None,
            post_index: int = 0) -> None:
        self._one_thread()

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        check_value.check_type(str, 'board', board)
        check_value.check_type(int, 'push_type',
                               push_type, value_class=push_type)
        check_value.check_type(str, 'push_content', push_content)
        if post_aid is not None:
            check_value.check_type(str, 'post_aid', post_aid)
        check_value.check_type(int, 'post_index', post_index)

        if len(board) == 0:
            raise ValueError(f'wrong parameter board: {board}')

        if post_index != 0 and isinstance(post_aid, str):
            raise ValueError('wrong parameter post_index and post_aid can\'t both input')

        if post_index == 0 and post_aid is None:
            raise ValueError('wrong parameter post_index or post_aid must input')

        if post_index != 0:
            newest_index = self.get_newest_index(
                NewIndex.BBS,
                board=board)
            check_value.check_index('post_index', post_index, newest_index)

        self._check_board(board)

        board_info = self._board_info_list[board.lower()]

        if board_info.is_push_record_ip:
            self.logger.info(i18n.record_ip)
            if board_info.is_push_aligned:
                self.logger.info(i18n.push_aligned)
                max_push_length = 32
            else:
                self.logger.info(i18n.not_push_aligned)
                max_push_length = 43 - len(self._ID)
        else:
            self.logger.info(i18n.not_record_ip)
            #     推文對齊
            if board_info.is_push_aligned:
                self.logger.info(i18n.push_aligned)
                max_push_length = 46
            else:
                self.logger.info(i18n.not_push_aligned)
                max_push_length = 58 - len(self._ID)

        push_content = push_content.strip()

        push_list = list()
        while push_content:
            index = 0
            jump = 0

            while len(push_content[:index].encode('big5uao', 'replace')) < max_push_length:

                if index == len(push_content):
                    break
                if push_content[index] == '\n':
                    jump = 1
                    break

                index += 1

            push_list.append(push_content[:index])
            push_content = push_content[index + jump:]

        push_list = filter(None, push_list)

        for comment in push_list:

            self.logger.info(i18n.comment, comment)

            for _ in range(2):
                try:
                    self._comment(
                        board,
                        push_type,
                        comment,
                        post_aid=post_aid,
                        post_index=post_index)
                    break
                except exceptions.NoFastComment:
                    # screens.show(self.config, self.connect_core.getScreenQueue())
                    self.logger.info(i18n.wait_for_no_fast_comment)
                    time.sleep(5.2)

    def _comment(
            self,
            board: str,
            push_type: int,
            push_content: str,
            post_aid: str = None,
            post_index: int = 0) -> None:

        try:
            from . import _api_push
        except ModuleNotFoundError:
            import _api_push

        return _api_push.push(
            self,
            board,
            push_type,
            push_content,
            post_aid,
            post_index)

    def get_user(self, user_id) -> dict:

        """
        Get the information of the PTT user.
        :param user_id:
        :return: the user info in dict.
        """

        return _api_get_user.get_user(self, user_id)

    # def throw_waterball(self, ptt_id, content) -> None:
    #     self._one_thread()
    #
    #     if not self._login_status:
    #         raise exceptions.Requirelogin(i18n.require_login)
    #
    #     if self.unregistered_user:
    #         raise exceptions.UnregisteredUser(lib_util.get_current_func_name())
    #
    #     check_value.check_type(str, 'ptt_id', ptt_id)
    #     check_value.check_type(str, 'content', content)
    #
    #     if len(ptt_id) <= 2:
    #         raise ValueError(f'wrong parameter ptt_id: {ptt_id}')
    #
    #     user = self._get_user(ptt_id)
    #     if '不在站上' in user.status:
    #         raise exceptions.UserOffline(ptt_id)
    #
    #     try:
    #         from . import _api_waterball
    #     except ModuleNotFoundError:
    #         import _api_waterball
    #
    #     return _api_waterball.throw_waterball(self, ptt_id, content)
    #
    # def get_waterball(self, operate_type: int) -> list:
    #     self._one_thread()
    #
    #     if not self._login_status:
    #         raise exceptions.Requirelogin(i18n.require_login)
    #
    #     if self.unregistered_user:
    #         raise exceptions.UnregisteredUser(lib_util.get_current_func_name())
    #
    #     check_value.check_type(int, 'OperateType', operate_type, value_class=waterball_operate_type)
    #
    #     try:
    #         from . import _api_waterball
    #     except ModuleNotFoundError:
    #         import _api_waterball
    #
    #     return _api_waterball.get_waterball(self, operate_type)
    #
    # def get_call_status(self) -> int:
    #     self._one_thread()
    #
    #     if not self._login_status:
    #         raise exceptions.Requirelogin(i18n.require_login)
    #
    #     if self.unregistered_user:
    #         raise exceptions.UnregisteredUser(lib_util.get_current_func_name())
    #
    #     return self._get_call_status()
    #
    # def _get_call_status(self) -> int:
    #
    #     try:
    #         from . import _api_call_status
    #     except ModuleNotFoundError:
    #         import _api_call_status
    #
    #     return _api_call_status.get_call_status(self)
    #
    # def set_call_status(
    #         self,
    #         call_status) -> None:
    #     self._one_thread()
    #
    #     if not self._login_status:
    #         raise exceptions.Requirelogin(i18n.require_login)
    #
    #     if self.unregistered_user:
    #         raise exceptions.UnregisteredUser(lib_util.get_current_func_name())
    #
    #     check_value.check_type(int, 'call_status', call_status, value_class=call_status)
    #
    #     try:
    #         from . import _api_call_status
    #     except ModuleNotFoundError:
    #         import _api_call_status
    #
    #     return _api_call_status.set_call_status(self, call_status)

    def give_money(self, ptt_id: str, money: int) -> None:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        check_value.check_type(str, 'ptt_id', ptt_id)
        check_value.check_type(int, 'money', money)
        # Check user
        self.get_user(ptt_id)

        try:
            from . import _api_give_money
        except ModuleNotFoundError:
            import _api_give_money

        return _api_give_money.give_money(self, ptt_id, money)

    def mail(
            self,
            ptt_id: str,
            title: str,
            content: str,
            sign_file,
            backup: bool = True) -> None:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        check_value.check_type(str, 'ptt_id', ptt_id)
        check_value.check_type(str, 'title', title)
        check_value.check_type(str, 'content', content)

        self.get_user(ptt_id)

        check_sign_file = False
        for i in range(0, 10):
            if str(i) == sign_file or i == sign_file:
                check_sign_file = True
                break

        if not check_sign_file:
            if sign_file.lower() != 'x':
                raise ValueError(f'wrong parameter sign_file: {sign_file}')

        try:
            from . import _api_mail
        except ModuleNotFoundError:
            import _api_mail

        _api_mail.mail(
            self,
            ptt_id,
            title,
            content,
            sign_file,
            backup)

        if self._mailbox_full:
            self.logout()
            raise exceptions.MailboxFull()

    def has_new_mail(self) -> int:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        if self.get_newest_index(NewIndex.MAIL) == 0:
            return 0

        try:
            from . import _api_has_new_mail
        except ModuleNotFoundError:
            import _api_has_new_mail

        return _api_has_new_mail.has_new_mail(self)

    def get_board_list(self) -> list:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        try:
            from . import _api_get_board_list
        except ModuleNotFoundError:
            import _api_get_board_list

        return _api_get_board_list.get_board_list(self)

    def reply_post(
            self,
            reply_type: int,
            board: str,
            content: str,
            sign_file=0,
            post_aid: str = None,
            post_index: int = 0) -> None:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        check_value.check_type(int, 'reply_type', reply_type, value_class=reply_type)
        check_value.check_type(str, 'board', board)
        check_value.check_type(str, 'content', content)
        if post_aid is not None:
            check_value.check_type(str, 'PostAID', post_aid)

        if post_index != 0:
            newest_index = self.get_newest_index(
                NewIndex.BBS,
                board=board)
            check_value.check_index(
                'post_index',
                post_index,
                max_value=newest_index)

        sign_file_list = [str(x) for x in range(0, 10)].append('x')
        if str(sign_file).lower() not in sign_file_list:
            raise ValueError(f'wrong parameter sign_file: {sign_file}')

        if post_aid is not None and post_index != 0:
            raise ValueError('wrong parameter post_aid and post_index can\'t both input')

        self._check_board(board)

        try:
            from . import _api_reply_post
        except ModuleNotFoundError:
            import _api_reply_post

        _api_reply_post.reply_post(
            self,
            reply_type,
            board,
            content,
            sign_file,
            post_aid,
            post_index)

    def set_board_title(
            self,
            board: str,
            new_title: str) -> None:
        # 第一支板主專用 API
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        check_value.check_type(str, 'board', board)
        check_value.check_type(str, 'new_title', new_title)

        self._check_board(
            board,
            check_moderator=True)

        try:
            from . import _api_set_board_title
        except ModuleNotFoundError:
            import _api_set_board_title

        _api_set_board_title.set_board_title(self, board, new_title)

    def mark_post(
            self,
            mark_type: int,
            board: str,
            post_aid: str = None,
            post_index: int = 0,
            search_type: int = 0,
            search_condition: str = None) -> None:
        # 標記文章
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        try:
            from . import _api_mark_post
        except ModuleNotFoundError:
            import _api_mark_post

        _api_mark_post.mark_post(
            self,
            mark_type,
            board,
            post_aid,
            post_index,
            search_type,
            search_condition)

    def get_favourite_board(self) -> list:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        try:
            from . import _api_get_favourite_board
        except ModuleNotFoundError:
            import _api_get_favourite_board

        return _api_get_favourite_board.get_favourite_board(self)

    def bucket(self, board: str, bucket_days: int, reason: str, ptt_id: str) -> None:

        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        check_value.check_type(str, 'board', board)
        check_value.check_type(int, 'bucket_days', bucket_days)
        check_value.check_type(str, 'reason', reason)
        check_value.check_type(str, 'ptt_id', ptt_id)

        self._get_user(ptt_id)

        self._check_board(
            board,
            check_moderator=True)

        try:
            from . import _api_bucket
        except ModuleNotFoundError:
            import _api_bucket

        _api_bucket.bucket(
            self, board, bucket_days, reason, ptt_id)

    def search_user(
            self,
            ptt_id: str,
            min_page: int = None,
            max_page: int = None) -> list:

        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        check_value.check_type(str, 'ptt_id', ptt_id)
        if min_page is not None:
            check_value.check_index(
                'min_page',
                min_page)
        if max_page is not None:
            check_value.check_index(
                'max_page',
                max_page)
        if min_page is not None and max_page is not None:
            check_value.check_index_range(
                'min_page',
                min_page,
                'max_page',
                max_page)

        try:
            from . import _api_search_user
        except ModuleNotFoundError:
            import _api_search_user

        return _api_search_user.search_user(self, ptt_id, min_page, max_page)

    def get_board_info(self, board: str, get_post_kind: bool = False) -> dict:

        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        check_value.check_type(str, 'board', board)

        return self._get_board_info(board, get_post_kind, call_by_others=False)

    def _get_board_info(self, board: str, get_post_kind, call_by_others: bool = True) -> dict:

        try:
            from . import _api_get_board_info
        except ModuleNotFoundError:
            import _api_get_board_info

        return _api_get_board_info.get_board_info(self, board, get_post_kind, call_by_others)

    def get_mail(
            self,
            index: int,
            search_type: int = 0,
            search_condition: str = None,
            search_list: list = None):

        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        if index == 0:
            return None
        current_index = self.get_newest_index(NewIndex.MAIL)
        self.logger.info('current_index', current_index)
        check_value.check_index('index', index, current_index)

        try:
            from . import _api_mail
        except ModuleNotFoundError:
            import _api_mail

        return _api_mail.get_mail(
            self,
            index,
            search_type,
            search_condition,
            search_list)

    def del_mail(self, index):
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        current_index = self.get_newest_index(NewIndex.MAIL)
        check_value.check_index(index, current_index)

        try:
            from . import _api_mail
        except ModuleNotFoundError:
            import _api_mail

        return _api_mail.del_mail(self, index)

    def change_pw(self, new_password) -> None:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        new_password = new_password[:8]

        try:
            from . import _api_change_pw
        except ModuleNotFoundError:
            import _api_change_pw

        _api_change_pw.change_pw(self, new_password)

    def get_aid_from_url(self, url: str) -> (str, str):

        # 檢查是否為字串
        check_value.check_type(str, 'url', url)

        # 檢查是否符合 PTT BBS 文章網址格式
        pattern = re.compile('https://www.ptt.cc/bbs/[-.\w]+/M.[\d]+.A[.\w]*.html')
        r = pattern.search(url)
        if r is None:
            raise ValueError('wrong parameter url must be www.ptt.cc post url')

        # 演算法參考 https://www.ptt.cc/man/C_Chat/DE98/DFF5/DB61/M.1419434423.A.DF0.html
        # aid 字元表
        aid_table = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'

        board = url[23:]
        board = board[:board.find('/')]

        temp = url[url.rfind('/') + 1:].split('.')
        # print(temp)

        id_0 = int(temp[1])  # dec

        aid_0 = ''
        for _ in range(6):
            index = id_0 % 64
            aid_0 = f'{aid_table[index]}{aid_0}'
            id_0 = int(id_0 / 64)

        if temp[3] != 'html':
            id_1 = int(temp[3], 16)  # hex
            aid_1 = ''
            for _ in range(2):
                index = id_1 % 64
                aid_1 = f'{aid_table[index]}{aid_1}'
                id_1 = int(id_1 / 64)
        else:
            aid_1 = '00'

        aid = f'{aid_0}{aid_1}'

        return board, aid

    def get_bottom_post_list(self, board) -> list:

        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        check_value.check_type(str, 'board', board)
        self._check_board(board)

        try:
            from . import _api_get_bottom_post_list
        except ModuleNotFoundError:
            import _api_get_bottom_post_list

        return _api_get_bottom_post_list.get_bottom_post_list(self, board)

    def del_post(
            self,
            board,
            post_aid: str = None,
            post_index: int = 0) -> None:
        self._one_thread()

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.require_login)

        check_value.check_type(str, 'board', board)
        if post_aid is not None:
            check_value.check_type(str, 'PostAID', post_aid)
        check_value.check_type(int, 'PostIndex', post_index)

        if len(board) == 0:
            raise ValueError(f'board error parameter: {board}')

        if post_index != 0 and isinstance(post_aid, str):
            raise ValueError('wrong parameter post_index and post_aid can\'t both input')

        if post_index == 0 and post_aid is None:
            raise ValueError('wrong parameter post_index or post_aid must input')

        if post_index != 0:
            newest_index = self.get_newest_index(
                NewIndex.BBS,
                board=board)
            check_value.check_index(
                'PostIndex',
                post_index,
                newest_index)

        board_info = self._check_board(board)

        try:
            from . import _api_del_post
        except ModuleNotFoundError:
            import _api_del_post

        return _api_del_post.del_post(
            self,
            board_info,
            board,
            post_aid,
            post_index)

    def _goto_board(self, board: str, refresh: bool = False, end: bool = False) -> None:

        cmd_list = list()
        cmd_list.append(command.go_main_menu)
        cmd_list.append('qs')
        cmd_list.append(board)
        cmd_list.append(command.enter)
        cmd_list.append(command.space)

        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit(
                i18n.any_key_continue,
                '任意鍵',
                response=' ',
                log_level=Logger.DEBUG
            ),
            connect_core.TargetUnit(
                [
                    '動畫播放中',
                ],
                '互動式動畫播放中',
                response=command.ctrl_c,
                log_level=Logger.DEBUG
            ),
            connect_core.TargetUnit(
                [
                    '進板成功',
                ],
                screens.Target.InBoard,
                break_detect=True,
                log_level=Logger.DEBUG
            ),
        ]

        if refresh:
            current_refresh = True
        else:
            if board.lower() in self._goto_board_list:
                current_refresh = True
            else:
                current_refresh = False
        self._goto_board_list.append(board.lower())
        self.connect_core.send(cmd, target_list, refresh=current_refresh)

        if end:
            cmd_list = list()
            cmd_list.append('1')
            cmd_list.append(command.enter)
            cmd_list.append('$')
            cmd = ''.join(cmd_list)

            target_list = [
                connect_core.TargetUnit(
                    '',
                    screens.Target.InBoard,
                    break_detect=True,
                    log_level=Logger.DEBUG
                ),
            ]

            self.connect_core.send(cmd, target_list)

    def fast_post_step0(
            self,
            board: str,
            title: str,
            content: str,
            post_type: int):
        _api_post.fast_post_step0(
            self,
            board,
            title,
            content,
            post_type)

    def fast_post_step1(
            self,
            sign_file):
        _api_post.fast_post_step1(self, sign_file)

    def _one_thread(self) -> None:
        current_thread_id = threading.get_ident()
        if current_thread_id == self._thread_id:
            return

        self.logger.debug('thread id', self._thread_id)
        self.logger.debug('current_thread_id', current_thread_id)

        raise exceptions.MultiThreadOperated()

    def _check_board(
            self,
            board: str,
            check_moderator: bool = False) -> Board:

        if board.lower() not in self._exist_board_list:
            board_info = self._get_board_info(board, False, False)
            self._exist_board_list.append(board.lower())
            self._board_info_list[board.lower()] = board_info

            moderators = board_info[Board.moderators]
            moderators = [x.lower() for x in moderators]
            self._ModeratorList[board.lower()] = moderators
            self._board_info_list[board.lower()] = board_info

        if check_moderator:
            if self._ID.lower() not in self._ModeratorList[board.lower()]:
                raise exceptions.NeedModeratorPermission(board)

        return self._board_info_list[board.lower()]


if __name__ == '__main__':
    print('PyPtt v ' + version)
    print('Developed by CodingMan')
    print('Github: PttCodingMan')
