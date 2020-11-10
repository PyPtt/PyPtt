﻿import time
import progressbar
import threading
import requests
import re
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

try:
    from . import data_type
    from . import config
    from . import lib_util
    from . import i18n
    from . import connect_core
    from . import log
    from . import screens
    from . import exceptions
    from . import command
    from . import check_value
    from . import version
except ModuleNotFoundError:
    import data_type
    import config
    import lib_util
    import i18n
    import connect_core
    import log
    import screens
    import exceptions
    import command
    import check_value
    import version
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class API:
    def __init__(
            self,
            language: int = 0,
            log_level: int = 0,
            screen_time_out: int = 0,
            screen_long_time_out: int = 0,
            screen_post_time_out: int = 0,
            connect_mode: int = 0,
            port: int = 0,
            log_handler=None,
            host: int = 0):

        self._mailbox_full = False
        self._ID = None
        if log_handler is not None and not callable(log_handler):
            raise TypeError('[PyPtt] log_handler is must callable!!')

        if log_handler is not None:
            has_log_handler = True
            set_log_handler_result = True
            try:
                log_handler(f'PyPtt v {version.V}')
                log_handler('Developed by CodingMan')
            except Exception:
                log_handler = None
                set_log_handler_result = False
        else:
            has_log_handler = False

        print(f'PyPtt v {version.V}')
        print('Developed by CodingMan')

        self._login_status = False
        self.unregistered_user = True
        self.registered_user = False
        self.process_picks = 0

        self.config = config.Config()

        if not isinstance(language, int):
            raise TypeError('[PyPtt] language must be integer')
        if not isinstance(log_level, int):
            raise TypeError('[PyPtt] log_level must be integer')
        if not isinstance(screen_time_out, int):
            raise TypeError('[PyPtt] screen_timeout must be integer')
        if not isinstance(screen_long_time_out, int):
            raise TypeError('[PyPtt] screen_long_timeout must be integer')
        if not isinstance(host, int):
            raise TypeError('[PyPtt] host must be integer')

        if screen_time_out != 0:
            self.config.screen_timeout = screen_time_out
        if screen_long_time_out != 0:
            self.config.screen_long_timeout = screen_long_time_out
        if screen_post_time_out != 0:
            self.config.screen_post_timeout = screen_post_time_out

        if log_level == 0:
            log_level = self.config.log_level
        elif not lib_util.check_range(log.level, log_level):
            raise ValueError('[PyPtt] Unknown log_level', log_level)
        else:
            self.config.log_level = log_level

        if language == 0:
            language = self.config.language
        elif not lib_util.check_range(i18n.language, language):
            raise ValueError('[PyPtt] Unknown language', language)
        else:
            self.config.language = language
        i18n.load(self.config.language)

        if log_handler is not None:
            self.config.log_handler = log_handler
            log.show_value(
                self.config,
                log.level.INFO,
                i18n.log_handler,
                i18n.Init
            )
        elif has_log_handler and not set_log_handler_result:
            log.show_value(
                self.config,
                log.level.INFO,
                i18n.log_handler,
                [
                    i18n.Init,
                    i18n.Fail
                ]
            )

        if self.config.language == i18n.language.CHINESE:
            log.show_value(
                self.config, log.level.INFO, [
                    i18n.ChineseTranditional,
                    i18n.languageModule
                ],
                i18n.Init
            )
        elif self.config.language == i18n.language.ENGLISH:
            log.show_value(
                self.config, log.level.INFO, [
                    i18n.English,
                    i18n.languageModule
                ],
                i18n.Init
            )

        if connect_mode == 0:
            connect_mode = self.config.connect_mode
        elif not lib_util.check_range(connect_core.connect_mode, connect_mode):
            raise ValueError('[PyPtt] Unknown connect_mode', connect_mode)
        else:
            self.config.connect_mode = connect_mode

        if port == 0:
            port = self.config.port
        elif not 0 < port < 65535:
            raise ValueError('[PyPtt] Unknown port', port)
        else:
            self.config.port = port

        if host == 0:
            host = self.config.host
        elif not lib_util.check_range(data_type.host_type, host):
            raise ValueError('[PyPtt] Unknown host', host)
        self.config.host = host

        if self.config.host == data_type.host_type.PTT1:
            log.show_value(
                self.config,
                log.level.INFO,
                [
                    i18n.Connect,
                    i18n.host
                ],
                i18n.PTT
            )
        elif self.config.host == data_type.host_type.PTT2:
            log.show_value(
                self.config,
                log.level.INFO,
                [
                    i18n.Connect,
                    i18n.host
                ],
                i18n.PTT2
            )
        elif self.config.host == data_type.host_type.LOCALHOST:
            log.show_value(
                self.config,
                log.level.INFO,
                [
                    i18n.Connect,
                    i18n.host
                ],
                i18n.Localhost
            )

        self.connect_core = connect_core.API(self.config)
        self._exist_board_list = list()
        self._board_info_list = dict()
        self._ModeratorList = dict()
        self._LastThrowWaterBallTime = 0
        self._ThreadID = threading.get_ident()
        self._goto_board_list = list()

        log.show_value(
            self.config,
            log.level.DEBUG,
            'ThreadID',
            self._ThreadID
        )

        log.show_value(
            self.config,
            log.level.INFO,
            [
                i18n.Library,
                ' v ' + version.V,
            ],
            i18n.Init
        )

    def _one_thread(self) -> None:
        current_thread_id = threading.get_ident()
        if current_thread_id == self._ThreadID:
            return
        log.show_value(
            self.config,
            log.level.DEBUG,
            'ThreadID',
            self._ThreadID
        )
        log.show_value(
            self.config,
            log.level.DEBUG,
            'Current thread id',
            current_thread_id
        )
        raise exceptions.MultiThreadOperated()

    def get_version(self) -> str:
        self._one_thread()
        return self.config.Version

    def _login(
            self,
            ptt_id: str,
            password: str,
            kick_other_login: bool = False) -> None:

        try:
            from . import _api_loginout
        except ModuleNotFoundError:
            import _api_loginout

        return _api_loginout.login(
            self,
            ptt_id,
            password,
            kick_other_login)

    def login(
            self,
            ptt_id: str,
            password: str,
            kick_other_login: bool = False) -> None:
        self._one_thread()

        self.config.log_last_value = None

        check_value.check(self.config, str, 'ID', ptt_id)
        check_value.check(self.config, str, 'Password', password)
        check_value.check(self.config, bool, 'kick_other_login', kick_other_login)

        try:
            return self._login(
                ptt_id,
                password,
                kick_other_login=kick_other_login
            )
        except exceptions.LoginError:
            return self._login(
                ptt_id,
                password,
                kick_other_login=kick_other_login
            )

    def logout(self) -> None:
        self._one_thread()

        if not self._login_status:
            return

        self.config.log_last_value = None

        try:
            from . import _api_loginout
        except ModuleNotFoundError:
            import _api_loginout

        return _api_loginout.logout(self)

    def log(self, msg: str) -> None:
        self._one_thread()
        log.log(self.config, log.level.INFO, msg)

    def get_time(self) -> str:
        self._one_thread()
        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        self.config.log_last_value = None

        try:
            from . import _api_get_time
        except ModuleNotFoundError:
            import _api_get_time

        return _api_get_time.get_time(self)

    def get_post(
            self,
            board: str,
            post_aid: str = None,
            post_index: int = 0,
            search_type: int = 0,
            search_condition: str = None,
            search_list: list = None,
            query: bool = False) -> data_type.PostInfo:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        self.config.log_last_value = None

        check_value.check(self.config, str, 'Board', board)
        if post_aid is not None:
            check_value.check(self.config, str, 'PostAID', post_aid)
        check_value.check(self.config, int, 'PostIndex', post_index)
        check_value.check(self.config, int, 'SearchType', search_type,
                          value_class=data_type.post_search_type)
        if search_condition is not None:
            check_value.check(self.config, str,
                              'SearchCondition', search_condition)

        if search_list is not None:
            check_value.check(self.config, list,
                              'search_list', search_condition)

        if len(board) == 0:
            raise ValueError(log.merge(
                self.config,
                [
                    i18n.Board,
                    i18n.ErrorParameter,
                    board
                ]))

        if post_index != 0 and isinstance(post_aid, str):
            raise ValueError(log.merge(
                self.config,
                [
                    'PostIndex',
                    'PostAID',
                    i18n.ErrorParameter,
                    i18n.BothInput
                ]))

        if post_index == 0 and post_aid is None:
            raise ValueError(log.merge(
                self.config,
                [
                    'PostIndex',
                    'PostAID',
                    i18n.ErrorParameter
                ]))

        if search_condition is not None and search_type == 0:
            raise ValueError(log.merge(
                self.config,
                [
                    'SearchType',
                    i18n.ErrorParameter,
                ]))

        if search_type == data_type.post_search_type.PUSH:
            try:
                S = int(search_condition)
            except ValueError:
                raise ValueError(log.merge(
                    self.config,
                    [
                        'SearchCondition',
                        i18n.ErrorParameter,
                    ]))

            if not (-100 <= S <= 110):
                raise ValueError(log.merge(
                    self.config,
                    [
                        'SearchCondition',
                        i18n.ErrorParameter,
                    ]))

        if post_aid is not None and search_condition is not None:
            raise ValueError(log.merge(
                self.config,
                [
                    'PostAID',
                    'SearchCondition',
                    i18n.ErrorParameter,
                    i18n.BothInput,
                ]))

        if post_index != 0:
            newest_index = self._get_newest_index(
                data_type.index_type.BBS,
                board=board,
                search_type=search_type,
                search_condition=search_condition,
                search_list=search_list)

            if post_index < 1 or newest_index < post_index:
                raise ValueError(log.merge(
                    self.config,
                    [
                        'PostIndex',
                        i18n.ErrorParameter,
                        i18n.OutOfRange,
                    ]))

        self._check_board(board)

        for i in range(2):

            need_continue = False
            post = None
            try:
                post = self._get_post(
                    board,
                    post_aid,
                    post_index,
                    search_type,
                    search_condition,
                    search_list,
                    query
                )
            except exceptions.ParseError as e:
                if i == 1:
                    raise e
                need_continue = True
            except exceptions.UnknownError as e:
                if i == 1:
                    raise e
                need_continue = True
            except exceptions.NoSuchBoard as e:
                if i == 1:
                    raise e
                need_continue = True
            except exceptions.NoMatchTargetError as e:
                if i == 1:
                    raise e
                need_continue = True

            if post is None:
                need_continue = True
            elif not post.pass_format_check:
                need_continue = True

            if need_continue:
                log.log(
                    self.config,
                    log.level.DEBUG,
                    'Wait for retry repost'
                )
                time.sleep(0.1)
                continue

            break
        return post

    def _check_board(
            self,
            board: str,
            check_moderator: bool = False) -> None:

        if board.lower() not in self._exist_board_list:
            board_info = self._get_board_info(board, False)
            self._exist_board_list.append(board.lower())
            self._board_info_list[board.lower()] = board_info

            moderators = board_info.moderators
            moderators = [x.lower() for x in moderators]
            self._ModeratorList[board.lower()] = moderators

        if check_moderator:
            if self._ID.lower() not in self._ModeratorList[board.lower()]:
                raise exceptions.NeedModeratorPermission(board)

    def _get_post(
            self,
            board: str,
            post_aid: str = None,
            post_index: int = 0,
            search_type: int = 0,
            search_condition: str = None,
            search_list: list = None,
            query: bool = False) -> data_type.PostInfo:

        try:
            from . import _api_get_post
        except ModuleNotFoundError:
            import _api_get_post

        return _api_get_post.get_post(
            self,
            board,
            post_aid,
            post_index,
            search_type,
            search_condition,
            search_list,
            query)

    def _get_newest_index(
            self,
            index_type: int,
            board: str = None,
            # BBS
            search_type: int = 0,
            search_condition: str = None,
            search_list: list = None) -> int:

        check_value.check(
            self.config, int, 'index_type',
            index_type, value_class=data_type.index_type)

        try:
            from . import _api_get_newest_index
        except ModuleNotFoundError:
            import _api_get_newest_index

        return _api_get_newest_index.get_newest_index(
            self,
            index_type,
            board,
            search_type,
            search_condition,
            search_list)

    def get_newest_index(
            self,
            index_type: int,
            board: str = None,
            search_type: int = 0,
            search_condition: str = None,
            search_list: list = None) -> int:
        self._one_thread()

        if index_type == data_type.index_type.BBS or index_type == data_type.index_type.MAIL:
            if not self._login_status:
                raise exceptions.Requirelogin(i18n.Requirelogin)

        if index_type == data_type.index_type.MAIL:
            if self.unregistered_user:
                raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        try:
            return self._get_newest_index(
                index_type,
                board,
                search_type,
                search_condition,
                search_list)
        except exceptions.NoSearchResult:
            raise exceptions.NoSearchResult

    def crawl_board(
            self,
            crawl_type: int,
            post_handler,
            board: str,
            # BBS版本
            start_index: int = 0,
            end_index: int = 0,
            start_aid: str = None,
            end_aid: str = None,
            search_type: int = 0,
            search_condition: str = None,
            search_list: list = None,
            query: bool = False,
            # 網頁版本
            start_page: int = 0,
            end_page: int = 0) -> list:

        self._one_thread()

        self.config.log_last_value = None

        check_value.check(
            self.config, int, 'crawl_type',
            crawl_type, value_class=data_type.crawl_type)
        check_value.check(self.config, str, 'Board', board)

        if len(board) == 0:
            raise ValueError(log.merge(
                self.config,
                [
                    i18n.Board,
                    i18n.ErrorParameter,
                    board
                ]))

        if crawl_type == data_type.crawl_type.BBS:
            if not self._login_status:
                raise exceptions.Requirelogin(i18n.Requirelogin)

            check_value.check(self.config, int, 'SearchType', search_type)
            if search_condition is not None:
                check_value.check(self.config, str,
                                  'SearchCondition', search_condition)

            if search_list is not None:
                check_value.check(self.config, list,
                                  'search_list', search_list)

            if start_aid is not None:
                check_value.check(self.config, str, 'StartAID', start_aid)
            if end_aid is not None:
                check_value.check(self.config, str, 'EndAID', end_aid)

            if (start_aid is not None or end_aid is not None) and \
                    (start_index != 0 or end_index != 0):
                raise ValueError(log.merge(
                    self.config,
                    [
                        'AID',
                        'Index',
                        i18n.ErrorParameter,
                        i18n.BothInput
                    ]))

            if (start_aid is not None or end_aid is not None) and \
                    (search_condition is not None):
                raise ValueError(log.merge(
                    self.config,
                    [
                        'AID',
                        'SearchCondition',
                        i18n.ErrorParameter,
                        i18n.BothInput
                    ]))

            if search_type == data_type.post_search_type.PUSH:
                try:
                    S = int(search_condition)
                except ValueError:
                    raise ValueError(log.merge(
                        self.config,
                        [
                            'SearchCondition',
                            i18n.ErrorParameter,
                        ]))

                if not (-100 <= S <= 110):
                    raise ValueError(log.merge(
                        self.config,
                        [
                            'SearchCondition',
                            i18n.ErrorParameter,
                        ]))

            if start_index != 0:
                newest_index = self._get_newest_index(
                    data_type.index_type.BBS,
                    board=board,
                    search_type=search_type,
                    search_condition=search_condition
                )

                check_value.check_index_range(
                    self.config,
                    'start_index',
                    start_index,
                    'end_index',
                    end_index,
                    max_value=newest_index
                )
            elif start_aid is not None and end_aid is not None:
                start_index = self.get_post(
                    board,
                    post_aid=start_aid,
                    query=True
                ).index
                end_index = self.get_post(
                    board,
                    post_aid=end_aid,
                    query=True
                ).index

                check_value.check_index_range(
                    self.config,
                    'start_index',
                    start_index,
                    'end_index',
                    end_index
                )
            else:
                raise ValueError(log.merge(
                    self.config,
                    [
                        i18n.ErrorParameter,
                        i18n.NoInput
                    ]))

            log.show_value(
                self.config,
                log.level.DEBUG,
                'StartIndex',
                start_index
            )

            log.show_value(
                self.config,
                log.level.DEBUG,
                'EndIndex',
                end_index
            )

            error_post_list = list()
            del_post_list = list()
            if self.config.log_level == log.level.INFO:
                PB = progressbar.ProgressBar(
                    max_value=end_index - start_index + 1,
                    redirect_stdout=True
                )
            for index in range(start_index, end_index + 1):

                for i in range(2):
                    need_continue = False
                    post = None
                    try:
                        post = self._get_post(
                            board,
                            post_index=index,
                            search_type=search_type,
                            search_condition=search_condition,
                            search_list=search_list,
                            query=query
                        )
                    except exceptions.ParseError as e:
                        if i == 1:
                            raise e
                        need_continue = True
                    except exceptions.UnknownError as e:
                        if i == 1:
                            raise e
                        need_continue = True
                    except exceptions.NoSuchBoard as e:
                        if i == 1:
                            raise e
                        need_continue = True
                    except exceptions.NoMatchTargetError as e:
                        if i == 1:
                            raise e
                        need_continue = True
                    except exceptions.ConnectionClosed as e:
                        if i == 1:
                            raise e
                        log.log(
                            self.config,
                            log.level.INFO,
                            i18n.RestoreConnection
                        )
                        self._login(
                            self._ID,
                            self._Password,
                            self.config.kick_other_login
                        )
                        need_continue = True
                    except exceptions.UseTooManyResources as e:
                        if i == 1:
                            raise e
                        log.log(
                            self.config,
                            log.level.INFO,
                            i18n.RestoreConnection
                        )
                        self._login(
                            self._ID,
                            self._Password,
                            self.config.kick_other_login
                        )
                        need_continue = True

                    if post is None:
                        need_continue = True
                    elif not post.pass_format_check:
                        need_continue = True

                    if need_continue:
                        log.log(
                            self.config,
                            log.level.DEBUG,
                            'Wait for retry repost'
                        )
                        time.sleep(0.1)
                        continue

                    break

                if self.config.log_level == log.level.INFO:
                    PB.update(index - start_index)
                if post is None:
                    error_post_list.append(index)
                    continue
                if not post.pass_format_check:
                    if post.aid is not None:
                        error_post_list.append(post.aid)
                    else:
                        error_post_list.append(index)
                    continue
                if post.delete_status != data_type.post_delete_status.NOT_DELETED:
                    del_post_list.append(index)
                post_handler(post)
            if self.config.log_level == log.level.INFO:
                PB.finish()

            return error_post_list, del_post_list

        else:
            if self.config.host == data_type.host_type.PTT2:
                raise exceptions.HostNotSupport(lib_util.get_current_func_name())

            # 網頁版本爬蟲
            # https://www.ptt.cc/bbs/index.html

            # 1. 取得總共有幾頁 MaxPage
            newest_index = self._get_newest_index(
                data_type.index_type.WEB,
                board=board)
            # 2. 檢查 StartPage 跟 EndPage 有沒有在 1 ~ MaxPage 之間

            check_value.check_index_range(
                self.config,
                'StartPage',
                start_page,
                'EndPage',
                end_page,
                max_value=newest_index
            )

            # 3. 把每篇文章(包括被刪除文章)欄位解析出來組合成 data_type.PostInfo
            error_post_list = list()
            del_post_list = list()
            # PostAID = ""
            _url = 'https://www.ptt.cc/bbs/'
            index = str(newest_index)
            if self.config.log_level == log.level.INFO:
                PB = progressbar.ProgressBar(
                    max_value=end_page - start_page + 1,
                    redirect_stdout=True
                )

            def deleted_post(post_title):
                if post_title.startswith('('):
                    if '本文' in post_title:
                        return data_type.post_delete_status.AUTHOR
                    elif post_title.startswith('(已被'):
                        return data_type.post_delete_status.MODERATOR
                    else:
                        return data_type.post_delete_status.UNKNOWN
                else:
                    return data_type.post_delete_status.NOT_DELETED

            for index in range(start_page, newest_index + 1):
                log.show_value(
                    self.config,
                    log.level.DEBUG,
                    'CurrentPage',
                    index
                )

                url = _url + board + '/index' + str(index) + '.html'
                r = requests.get(url, cookies={'over18': '1'})
                if r.status_code != requests.codes.ok:
                    raise exceptions.NoSuchBoard(self.config, board)
                soup = BeautifulSoup(r.text, 'html.parser')

                for div in soup.select('div.r-ent'):
                    web = div.select('div.title a')
                    post = {
                        'author': div.select('div.author')[0].text,
                        'title': div.select('div.title')[0].text.strip('\n').strip(),
                        'web': web[0].get('href') if web else ''
                    }
                    if post['title'].startswith('('):
                        del_post_list.append(post['title'])
                        if post['title'].startswith('(本文'):
                            if '[' in post['title']:
                                post['author'] = post['title'].split(
                                    '[')[1].split(']')[0]
                            else:
                                post['author'] = post['title'].split('<')[
                                    1].split('>')[0]
                        else:
                            post['author'] = post['title'].split('<')[
                                1].split('>')[0]

                    post = data_type.PostInfo(
                        board=board,
                        author=post['author'],
                        title=post['title'],
                        web_url='https://www.ptt.cc' + post['web'],
                        delete_status=deleted_post(post['title'])
                    )
                    post_handler(post)

                if self.config.log_level == log.level.INFO:
                    PB.update(index - start_page)

            log.show_value(
                self.config,
                log.level.DEBUG,
                'DelPostList',
                del_post_list
            )

            # 4. 把組合出來的 Post 塞給 handler

            # 5. 顯示 progress bar
            if self.config.log_level == log.level.INFO:
                PB.finish()

            return error_post_list, del_post_list

    def post(
            self,
            board: str,
            title: str,
            content: str,
            post_type: int,
            sign_file) -> None:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        self.config.log_last_value = None

        check_value.check(self.config, str, 'Board', board)
        check_value.check(self.config, str, 'Title', title)
        check_value.check(self.config, str, 'Content', content)
        check_value.check(self.config, int, 'PostType', post_type)

        check_sign_file = False
        for i in range(0, 10):
            if str(i) == sign_file or i == sign_file:
                check_sign_file = True
                break

        if not check_sign_file:
            sign_file = sign_file.lower()
            if sign_file != 'x':
                raise ValueError(log.merge(
                    self.config,
                    [
                        'SignFile',
                        i18n.ErrorParameter,
                        sign_file
                    ]))

        self._check_board(board)

        try:
            from . import _api_post
        except ModuleNotFoundError:
            import _api_post

        return _api_post.post(
            self,
            board,
            title,
            content,
            post_type,
            sign_file)

    def push(
            self,
            board: str,
            push_type: int,
            push_content: str,
            post_aid: str = None,
            post_index: int = 0) -> None:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        self.config.log_last_value = None

        check_value.check(self.config, str, 'Board', board)
        check_value.check(self.config, int, 'push_type',
                          push_type, value_class=data_type.push_type)
        check_value.check(self.config, str, 'PushContent', push_content)
        if post_aid is not None:
            check_value.check(self.config, str, 'PostAID', post_aid)
        check_value.check(self.config, int, 'PostIndex', post_index)

        if len(board) == 0:
            raise ValueError(log.merge(
                self.config,
                [
                    i18n.Board,
                    i18n.ErrorParameter,
                    board
                ]))

        if post_index != 0 and isinstance(post_aid, str):
            raise ValueError(log.merge(
                self.config,
                [
                    'PostIndex',
                    'PostAID',
                    i18n.ErrorParameter,
                    i18n.BothInput
                ]))

        if post_index == 0 and post_aid is None:
            raise ValueError(log.merge(
                self.config,
                [
                    'PostIndex',
                    'PostAID',
                    i18n.ErrorParameter,
                    i18n.NoInput
                ]))

        if post_index != 0:
            newest_index = self._get_newest_index(
                data_type.index_type.BBS,
                board=board)
            check_value.check_index(self.config, 'PostIndex',
                                    post_index, newest_index)

        self._check_board(board)

        board_info = self._board_info_list[board.lower()]

        if board_info.is_push_record_ip:
            log.log(
                self.config,
                log.level.INFO,
                i18n.record_ip)
            if board_info.is_push_aligned:
                log.log(
                    self.config,
                    log.level.INFO,
                    i18n.push_aligned)
                max_push_length = 32
            else:
                log.log(
                    self.config,
                    log.level.INFO,
                    i18n.not_push_aligned)
                max_push_length = 43 - len(self._ID)
        else:
            log.log(
                self.config,
                log.level.INFO,
                i18n.not_record_ip)
            #     推文對齊
            if board_info.is_push_aligned:
                log.log(
                    self.config,
                    log.level.INFO,
                    i18n.push_aligned)
                max_push_length = 46
            else:
                log.log(
                    self.config,
                    log.level.INFO,
                    i18n.not_push_aligned)
                max_push_length = 58 - len(self._ID)

        push_content = push_content.strip()

        push_list = list()
        while push_content:
            index = 0
            jump = 0

            while len(push_content[:index].encode('big5-uao', 'replace')) < max_push_length:

                if index == len(push_content):
                    break
                if push_content[index] == '\n':
                    jump = 1
                    break

                index += 1

            push_list.append(push_content[:index])
            push_content = push_content[index + jump:]

        push_list = filter(None, push_list)

        for push in push_list:
            log.show_value(
                self.config,
                log.level.INFO,
                i18n.Push,
                push)

            for _ in range(2):
                try:
                    self._push(
                        board,
                        push_type,
                        push,
                        post_aid=post_aid,
                        post_index=post_index)
                    break
                except exceptions.NoFastPush:
                    # screens.show(self.config, self.connect_core.getScreenQueue())
                    log.log(
                        self.config,
                        log.level.INFO,
                        '等待快速推文')
                    time.sleep(5.2)

    def _push(
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

    def _get_user(self, user_id) -> data_type.UserInfo:

        check_value.check(self.config, str, 'UserID', user_id)
        if len(user_id) < 2:
            raise ValueError(log.merge(
                self.config,
                [
                    'UserID',
                    i18n.ErrorParameter,
                    user_id
                ]))

        try:
            from . import _api_get_user
        except ModuleNotFoundError:
            import _api_get_user

        return _api_get_user.get_user(self, user_id)

    def get_user(self, user_id) -> data_type.UserInfo:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        return self._get_user(user_id)

    def throw_waterball(self, ptt_id, content) -> None:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        check_value.check(self.config, str, 'ptt_id', ptt_id)
        check_value.check(self.config, str, 'content', content)

        if len(ptt_id) <= 2:
            raise ValueError(log.merge(
                self.config,
                [
                    'ptt_id',
                    i18n.ErrorParameter,
                    ptt_id
                ]))

        user = self._get_user(ptt_id)
        if '不在站上' in user.status:
            raise exceptions.UserOffline(ptt_id)

        try:
            from . import _api_waterball
        except ModuleNotFoundError:
            import _api_waterball

        return _api_waterball.throw_waterball(self, ptt_id, content)

    def get_waterball(self, operate_type: int) -> list:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        check_value.check(
            self.config, int, 'OperateType', operate_type,
            value_class=data_type.waterball_operate_type)

        try:
            from . import _api_waterball
        except ModuleNotFoundError:
            import _api_waterball

        return _api_waterball.get_waterball(self, operate_type)

    def get_call_status(self) -> int:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        return self._get_call_status()

    def _get_call_status(self) -> int:

        try:
            from . import _api_call_status
        except ModuleNotFoundError:
            import _api_call_status

        return _api_call_status.get_call_status(self)

    def set_call_status(
            self,
            call_status) -> None:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        check_value.check(
            self.config, int, 'call_status', call_status,
            value_class=data_type.call_status)

        try:
            from . import _api_call_status
        except ModuleNotFoundError:
            import _api_call_status

        return _api_call_status.set_call_status(self, call_status)

    def give_money(self, ptt_id: str, money: int) -> None:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        check_value.check(self.config, str, 'ID', ptt_id)
        check_value.check(self.config, int, 'Money', money)
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
            sign_file) -> None:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        check_value.check(self.config, str, 'ptt_id', ptt_id)
        check_value.check(self.config, str, 'title', title)
        check_value.check(self.config, str, 'content', content)

        self.get_user(ptt_id)

        check_sign_file = False
        for i in range(0, 10):
            if str(i) == sign_file or i == sign_file:
                check_sign_file = True
                break

        if not check_sign_file:
            sign_file = sign_file.lower()
            if sign_file != 'x':
                raise ValueError(log.merge(
                    self.config,
                    [
                        'SignFile',
                        i18n.ErrorParameter,
                        sign_file
                    ]))

        try:
            from . import _api_mail
        except ModuleNotFoundError:
            import _api_mail

        _api_mail.mail(
            self,
            ptt_id,
            title,
            content,
            sign_file)

        if self._mailbox_full:
            self.logout()
            raise exceptions.MailboxFull()

    def has_new_mail(self) -> int:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.get_newest_index(data_type.index_type.MAIL) == 0:
            return 0

        self.config.log_last_value = None

        try:
            from . import _api_has_new_mail
        except ModuleNotFoundError:
            import _api_has_new_mail

        return _api_has_new_mail.has_new_mail(self)

    def get_board_list(self) -> list:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        self.config.log_last_value = None

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
            raise exceptions.Requirelogin(i18n.Requirelogin)

        self.config.log_last_value = None

        check_value.check(
            self.config, int, 'reply_type', reply_type,
            value_class=data_type.reply_type)
        check_value.check(self.config, str, 'Board', board)
        check_value.check(self.config, str, 'Content', content)
        if post_aid is not None:
            check_value.check(self.config, str, 'PostAID', post_aid)

        if post_index != 0:
            newest_index = self._get_newest_index(
                data_type.index_type.BBS,
                board=board)
            check_value.check_index(
                self.config, 'PostIndex',
                post_index, max_value=newest_index)

        sign_file_list = [str(x) for x in range(0, 10)]
        sign_file_list.append('x')

        if str(sign_file) not in sign_file_list:
            raise ValueError(log.merge(
                self.config,
                [
                    'SignFile',
                    i18n.ErrorParameter
                ]))

        if post_aid is not None and post_index != 0:
            raise ValueError(log.merge(
                self.config,
                [
                    'PostIndex',
                    'PostAID',
                    i18n.ErrorParameter,
                    i18n.BothInput
                ]))

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
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        check_value.check(self.config, str, 'board', board)
        check_value.check(self.config, str, 'new_title', new_title)

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
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        try:
            from . import _api_mark_post
        except ModuleNotFoundError:
            import _api_mark_post

        _api_mark_post.markPost(
            self,
            mark_type,
            board,
            post_aid,
            post_index,
            search_type,
            search_condition
        )

    def get_favourite_board(self) -> list:
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        self.config.log_last_value = None

        try:
            from . import _api_get_favourite_board
        except ModuleNotFoundError:
            import _api_get_favourite_board

        return _api_get_favourite_board.get_favourite_board(self)

    def bucket(self, board: str, bucket_days: int, reason: str, ptt_id: str) -> None:

        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        check_value.check(self.config, str, 'board', board)
        check_value.check(self.config, int, 'bucket_days', bucket_days)
        check_value.check(self.config, str, 'reason', reason)
        check_value.check(self.config, str, 'ptt_id', ptt_id)

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
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        check_value.check(self.config, str, 'ptt_id', ptt_id)
        if min_page is not None:
            check_value.check_index(
                self.config,
                'min_page',
                min_page
            )
        if max_page is not None:
            check_value.check_index(
                self.config,
                'max_page',
                max_page
            )
        if min_page is not None and max_page is not None:
            check_value.check_index_range(
                self.config,
                'min_page',
                min_page,
                'max_page',
                max_page
            )

        try:
            from . import _api_search_user
        except ModuleNotFoundError:
            import _api_search_user

        return _api_search_user.search_user(self, ptt_id, min_page, max_page)

    def get_board_info(self, board: str, get_post_kind: bool = False, get_board_limit: bool = False) -> data_type.BoardInfo:

        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        self.config.log_last_value = None

        check_value.check(self.config, str, 'board', board)

        return self._get_board_info(board, get_post_kind, get_board_limit, call_by_others=False)

    def _get_board_info(self, board: str, get_post_kind, get_board_limit, call_by_others: bool = True) -> data_type.BoardInfo:

        try:
            from . import _api_get_board_info
        except ModuleNotFoundError:
            import _api_get_board_info

        return _api_get_board_info.get_board_info(self, board, get_post_kind, get_board_limit, call_by_others)

    def get_mail(self, index):

        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        if index == 0:
            return None
        current_index = self.get_newest_index(data_type.index_type.MAIL)
        check_value.check_index(self.config, 'index', index, current_index)

        try:
            from . import _api_mail
        except ModuleNotFoundError:
            import _api_mail

        return _api_mail.get_mail(self, index)

    def del_mail(self, index):
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        if self.unregistered_user:
            raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

        self.config.log_last_value = None

        current_index = self.get_newest_index(data_type.index_type.MAIL)
        check_value.check_index(self.config, index, current_index)

        try:
            from . import _api_mail
        except ModuleNotFoundError:
            import _api_mail

        return _api_mail.del_mail(self, index)

    def change_pw(self, new_password):
        self._one_thread()

        if not self._login_status:
            raise exceptions.Requirelogin(i18n.Requirelogin)

        new_password = new_password[:8]

        try:
            from . import _api_change_pw
        except ModuleNotFoundError:
            import _api_change_pw

        _api_change_pw.change_pw(self, new_password)

    def get_aid_from_url(self, url: str) -> (str, str):

        # 檢查是否為字串
        check_value.check(self.config, str, 'url', url)

        # 檢查是否符合 PTT BBS 文章網址格式
        pattern = re.compile('https://www.ptt.cc/bbs/[-.\w]+/M.[\d]+.A[.\w]*.html')
        r = pattern.search(url)
        if r is None:
            raise ValueError(log.merge(
                self.config,
                [
                    i18n.ErrorParameter,
                    'url must be www.ptt.cc article url'
                ]))

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

    def _goto_board(self, board: str, refresh: bool = False) -> None:

        cmd_list = list()
        cmd_list.append(command.GoMainMenu)
        cmd_list.append('qs')
        cmd_list.append(board)
        cmd_list.append(command.Enter)
        cmd_list.append(command.Space)

        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit(
                i18n.AnyKeyContinue,
                '任意鍵',
                response=' ',
                log_level=log.level.DEBUG
            ),
            connect_core.TargetUnit(
                [
                    '動畫播放中',
                ],
                '互動式動畫播放中',
                response=command.Ctrl_C,
                log_level=log.level.DEBUG
            ),
            connect_core.TargetUnit(
                [
                    '進板成功',
                ],
                screens.Target.InBoard,
                break_detect=True,
                log_level=log.level.DEBUG
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


if __name__ == '__main__':
    print('PyPtt v ' + version.V)
    print('Developed by CodingMan')
    print('Github: PttCodingMan')
