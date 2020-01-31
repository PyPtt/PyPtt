import time
import progressbar
import threading
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

try:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import ConnectCore
    from . import Log
    # from . import Screens
    from . import Exceptions
    from . import Command
    from . import CheckValue
    from . import Ver
except ModuleNotFoundError:
    import DataType
    import Config
    import Util
    import i18n
    import ConnectCore
    import Log
    # import Screens
    import Exceptions
    import Command
    import CheckValue
    import Ver
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Version = Ver.V

Language = i18n.Language
ConnectMode = ConnectCore.ConnectMode
LogLevel = Log.Level
Command = Command
PushType = DataType.PushType
PostSearchType = DataType.PostSearchType
IndexType = DataType.IndexType
WaterBallOperateType = DataType.WaterBallOperateType
WaterBallType = DataType.WaterBallType
CallStatus = DataType.CallStatus
PostDeleteStatus = DataType.PostDeleteStatus
CrawlType = DataType.CrawlType
Host = DataType.Host
ReplyType = DataType.ReplyType
MarkType = DataType.MarkType


class Library:
    def __init__(
            self,
            language: int = 0,
            connect_mode: int = 0,
            log_level: int = 0,
            screen_time_out: int = 0,
            screen_long_time_out: int = 0,
            log_handler=None,
            host: int = 0,
    ):

        self._ID = None
        if log_handler is not None and not callable(log_handler):
            raise TypeError('[PTT Library] LogHandler is must callable!!')

        if log_handler is not None:
            has_log_handler = True
            set_log_handler_result = True
            try:
                log_handler(f'PTT Library v {Version}')
                log_handler('Developed by PTT CodingMan')
            except Exception:
                log_handler = None
                set_log_handler_result = False
        else:
            has_log_handler = False

        print(f'PTT Library v {Version}')
        print('Developed by PTT CodingMan')

        self._LoginStatus = False

        self.Config = Config.Config()

        if not isinstance(language, int):
            raise TypeError('[PTT Library] Language must be integer')
        if not isinstance(connect_mode, int):
            raise TypeError('[PTT Library] ConnectMode must be integer')
        if not isinstance(log_level, int):
            raise TypeError('[PTT Library] LogLevel must be integer')
        if not isinstance(screen_time_out, int):
            raise TypeError('[PTT Library] ScreenTimeOut must be integer')
        if not isinstance(screen_long_time_out, int):
            raise TypeError('[PTT Library] ScreenLongTimeOut must be integer')
        if not isinstance(host, int):
            raise TypeError('[PTT Library] Host must be integer')

        if screen_time_out != 0:
            self.Config.ScreenTimeOut = screen_time_out
        if screen_long_time_out != 0:
            self.Config.ScreenLongTimeOut = screen_long_time_out

        if log_level == 0:
            log_level = self.Config.LogLevel
        elif not Util.checkRange(Log.Level, log_level):
            raise ValueError('[PTT Library] Unknown LogLevel', log_level)
        else:
            self.Config.LogLevel = log_level

        if language == 0:
            language = self.Config.Language
        elif not Util.checkRange(i18n.Language, language):
            raise ValueError('[PTT Library] Unknown language', language)
        else:
            self.Config.Language = language
        i18n.load(language)

        if log_handler is not None:
            # Log.Handler = LogHandler
            self.Config.LogHandler = log_handler
            Log.showValue(
                self.Config,
                Log.Level.INFO,
                i18n.LogHandler,
                i18n.Init
            )
        elif has_log_handler and not set_log_handler_result:
            Log.showValue(
                self.Config,
                Log.Level.INFO,
                i18n.LogHandler,
                [
                    i18n.Init,
                    i18n.Fail
                ]
            )

        if language == i18n.Language.Chinese:
            Log.showValue(
                self.Config, Log.Level.INFO, [
                    i18n.ChineseTranditional,
                    i18n.LanguageModule
                ],
                i18n.Init
            )
        elif language == i18n.Language.English:
            Log.showValue(
                self.Config, Log.Level.INFO, [
                    i18n.English,
                    i18n.LanguageModule
                ],
                i18n.Init
            )

        if connect_mode == 0:
            connect_mode = self.Config.ConnectMode
        elif not Util.checkRange(ConnectCore.ConnectMode, connect_mode):
            raise ValueError('[PTT Library] Unknown ConnectMode', connect_mode)
        else:
            self.Config.ConnectMode = connect_mode

        if host == 0:
            host = self.Config.Host
        elif not Util.checkRange(DataType.Host, host):
            raise ValueError('[PTT Library] Unknown Host', host)
        self.Config.Host = host

        if host == DataType.Host.PTT1:
            Log.showValue(
                self.Config,
                Log.Level.INFO,
                [
                    i18n.Connect,
                    i18n.Host
                ],
                i18n.PTT
            )
        if host == DataType.Host.PTT2:
            Log.showValue(
                self.Config,
                Log.Level.INFO,
                [
                    i18n.Connect,
                    i18n.Host
                ],
                i18n.PTT2
            )

        self._ConnectCore = ConnectCore.API(self.Config, host)
        self._ExistBoardList = []
        self._ModeratorList = dict()
        self._LastThrowWaterBallTime = 0
        self._ThreadID = threading.get_ident()

        Log.showValue(
            self.Config,
            Log.Level.DEBUG,
            'ThreadID',
            self._ThreadID
        )

        Log.showValue(
            self.Config,
            Log.Level.INFO, [
                i18n.PTT,
                i18n.Library,
                ' v ' + Version,
            ],
            i18n.Init
        )

    def _OneThread(self):
        current_thread_id = threading.get_ident()
        if current_thread_id == self._ThreadID:
            return
        Log.showValue(
            self.Config,
            Log.Level.DEBUG,
            'ThreadID',
            self._ThreadID
        )
        Log.showValue(
            self.Config,
            Log.Level.DEBUG,
            'Current thread id',
            current_thread_id
        )
        raise Exceptions.MultiThreadOperated()

    def getVersion(self) -> str:
        self._OneThread()
        return self.Config.Version

    def _login(
            self,
            id: str,
            password: str,
            kick_other_login: bool = False
    ):

        try:
            from . import api_loginout
        except ModuleNotFoundError:
            import api_loginout

        return api_loginout.login(
            self,
            id,
            password,
            kick_other_login)

    def login(
            self,
            id: str,
            password: str,
            kick_other_login: bool = False
    ):
        self._OneThread()

        CheckValue.check(self.Config, str, 'ID', id)
        CheckValue.check(self.Config, str, 'Password', password)
        CheckValue.check(self.Config, bool, 'KickOtherLogin', kick_other_login)

        try:
            return self._login(
                id,
                password,
                kick_other_login=kick_other_login
            )
        except Exceptions.LoginError:
            return self._login(
                id,
                password,
                kick_other_login=kick_other_login
            )

    def logout(self):
        self._OneThread()

        if not self._LoginStatus:
            return

        try:
            from . import api_loginout
        except ModuleNotFoundError:
            import api_loginout

        return api_loginout.logout(self)

    def log(self, msg):
        self._OneThread()
        Log.log(self.Config, Log.Level.INFO, msg)

    def getTime(self) -> str:
        self._OneThread()
        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        try:
            from . import api_getTime
        except ModuleNotFoundError:
            import api_getTime

        return api_getTime.getTime(self)

    def getPost(
            self,
            board: str,
            post_aid: str = None,
            post_index: int = 0,
            search_type: int = 0,
            search_condition: str = None,
            query: bool = False
    ):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'Board', board)
        if post_aid is not None:
            CheckValue.check(self.Config, str, 'PostAID', post_aid)
        CheckValue.check(self.Config, int, 'PostIndex', post_index)
        CheckValue.check(self.Config, int, 'SearchType', search_type,
                         Class=DataType.PostSearchType)
        if search_condition is not None:
            CheckValue.check(self.Config, str,
                             'SearchCondition', search_condition)

        if len(board) == 0:
            raise ValueError(Log.merge(
                self.Config,
                [
                    i18n.Board,
                    i18n.ErrorParameter,
                    board
                ]))

        if post_index != 0 and isinstance(post_aid, str):
            raise ValueError(Log.merge(
                self.Config,
                [
                    'PostIndex',
                    'PostAID',
                    i18n.ErrorParameter,
                    i18n.BothInput
                ]))

        if post_index == 0 and post_aid is None:
            raise ValueError(Log.merge(
                self.Config,
                [
                    'PostIndex',
                    'PostAID',
                    i18n.ErrorParameter
                ]))

        if search_condition is not None and search_type == 0:
            raise ValueError(Log.merge(
                self.Config,
                [
                    'SearchType',
                    i18n.ErrorParameter,
                ]))

        if search_type == DataType.PostSearchType.Push:
            try:
                S = int(search_condition)
            except ValueError:
                raise ValueError(Log.merge(
                    self.Config,
                    [
                        'SearchCondition',
                        i18n.ErrorParameter,
                    ]))

            if not (-100 <= S <= 110):
                raise ValueError(Log.merge(
                    self.Config,
                    [
                        'SearchCondition',
                        i18n.ErrorParameter,
                    ]))

        if post_aid is not None and search_condition is not None:
            raise ValueError(Log.merge(
                self.Config,
                [
                    'PostAID',
                    'SearchCondition',
                    i18n.ErrorParameter,
                    i18n.BothInput,
                ]))

        if post_index != 0:
            newest_index = self._getNewestIndex(
                DataType.IndexType.BBS,
                board=board,
                search_type=search_type,
                search_condition=search_condition
            )

            if post_index < 1 or newest_index < post_index:
                raise ValueError(Log.merge(
                    self.Config,
                    [
                        'PostIndex',
                        i18n.ErrorParameter,
                        i18n.OutOfRange,
                    ]))

        self._checkBoard(board)

        for i in range(2):

            need_continue = False
            post = None
            try:
                post = self._getPost(
                    board,
                    post_aid,
                    post_index,
                    search_type,
                    search_condition,
                    query
                )
            except Exceptions.ParseError as e:
                if i == 1:
                    raise e
                need_continue = True
            except Exceptions.UnknownError as e:
                if i == 1:
                    raise e
                need_continue = True
            except Exceptions.NoSuchBoard as e:
                if i == 1:
                    raise e
                need_continue = True
            except Exceptions.NoMatchTargetError as e:
                if i == 1:
                    raise e
                need_continue = True

            if post is None:
                need_continue = True
            elif not post.isFormatCheck():
                need_continue = True

            if need_continue:
                Log.log(
                    self.Config,
                    Log.Level.DEBUG,
                    'Wait for retry repost'
                )
                time.sleep(0.1)
                continue

            break
        return post

    def _checkBoard(
            self,
            board,
            check_moderator: bool = False
    ):
        if board.lower() not in self._ExistBoardList:
            boardinfo = self._getBoardInfo(board)
            self._ExistBoardList.append(board.lower())

            moderators = boardinfo.getModerators()
            moderators = [x.lower() for x in moderators]
            self._ModeratorList[board.lower()] = moderators

        if check_moderator:
            if self._ID.lower() not in self._ModeratorList[board.lower()]:
                raise Exceptions.NeedModeratorPermission(board)

    def _getPost(
            self,
            board: str,
            post_aid: str = None,
            post_index: int = 0,
            search_type: int = 0,
            search_condition: str = None,
            query: bool = False):

        try:
            from . import api_getPost
        except ModuleNotFoundError:
            import api_getPost

        return api_getPost.getPost(
            self,
            board,
            post_aid,
            post_index,
            search_type,
            search_condition,
            query)

    def _getNewestIndex(
            self,
            index_type: int,
            board: object = None,
            # BBS
            search_type: object = 0,
            search_condition: object = None) -> object:

        CheckValue.check(
            self.Config, int, 'IndexType',
            index_type, Class=DataType.IndexType)
        CheckValue.check(self.Config, str, 'Board', board)

        try:
            from . import api_getNewestIndex
        except ModuleNotFoundError:
            import api_getNewestIndex

        return api_getNewestIndex.getNewestIndex(
            self,
            index_type,
            board,
            search_type,
            search_condition)

    def getNewestIndex(
            self,
            index_type: int,
            board: str = None,
            search_type: int = 0,
            search_condition: str = None):
        self._OneThread()

        if index_type == DataType.IndexType.BBS:
            if not self._LoginStatus:
                raise Exceptions.RequireLogin(i18n.RequireLogin)

        try:
            return self._getNewestIndex(
                index_type,
                board,
                search_type,
                search_condition
            )
        except Exception:
            return self._getNewestIndex(
                index_type,
                board,
                search_type,
                search_condition
            )

    def _getPostIndex(
            self,
            board,
            aid):

        try:
            from . import api_getPostIndex
        except ModuleNotFoundError:
            import api_getPostIndex

        return api_getPostIndex.getPostIndex(
            self,
            board,
            aid)

    def crawlBoard(
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
            query: bool = False,
            # 網頁版本
            start_page: int = 0,
            end_page: int = 0):

        self._OneThread()

        CheckValue.check(
            self.Config, int, 'CrawlType',
            crawl_type, Class=DataType.CrawlType)
        CheckValue.check(self.Config, str, 'Board', board)

        if len(board) == 0:
            raise ValueError(Log.merge(
                self.Config,
                [
                    i18n.Board,
                    i18n.ErrorParameter,
                    board
                ]))

        if crawl_type == DataType.CrawlType.BBS:
            if not self._LoginStatus:
                raise Exceptions.RequireLogin(i18n.RequireLogin)

            CheckValue.check(self.Config, int, 'SearchType', search_type)
            if search_condition is not None:
                CheckValue.check(self.Config, str,
                                 'SearchCondition', search_condition)
            if start_aid is not None:
                CheckValue.check(self.Config, str, 'StartAID', start_aid)
            if end_aid is not None:
                CheckValue.check(self.Config, str, 'EndAID', end_aid)

            if (start_aid is not None or end_aid is not None) and \
                    (start_index != 0 or end_index != 0):
                raise ValueError(Log.merge(
                    self.Config,
                    [
                        'AID',
                        'Index',
                        i18n.ErrorParameter,
                        i18n.BothInput
                    ]))

            if (start_aid is not None or end_aid is not None) and \
                    (search_condition is not None):
                raise ValueError(Log.merge(
                    self.Config,
                    [
                        'AID',
                        'SearchCondition',
                        i18n.ErrorParameter,
                        i18n.BothInput
                    ]))

            if search_type == DataType.PostSearchType.Push:
                try:
                    S = int(search_condition)
                except ValueError:
                    raise ValueError(Log.merge(
                        self.Config,
                        [
                            'SearchCondition',
                            i18n.ErrorParameter,
                        ]))

                if not (-100 <= S <= 110):
                    raise ValueError(Log.merge(
                        self.Config,
                        [
                            'SearchCondition',
                            i18n.ErrorParameter,
                        ]))

            if start_index != 0:
                newest_index = self._getNewestIndex(
                    DataType.IndexType.BBS,
                    board=board,
                    search_type=search_type,
                    search_condition=search_condition
                )
                CheckValue.checkIndexRange(
                    self.Config,
                    'StartIndex',
                    start_index,
                    'EndIndex',
                    end_index,
                    MaxValue=newest_index
                )
            elif start_aid is not None and end_aid is not None:
                start_index = self._getPostIndex(
                    board,
                    start_aid,
                )
                end_index = self._getPostIndex(
                    board,
                    end_aid,
                )
                CheckValue.checkIndexRange(
                    self.Config,
                    'StartAID',
                    start_index,
                    'EndAID',
                    end_index
                )
            else:
                raise ValueError(Log.merge(
                    self.Config,
                    [
                        i18n.ErrorParameter,
                        i18n.NoInput
                    ]))

            Log.showValue(
                self.Config,
                Log.Level.DEBUG,
                'StartIndex',
                start_index
            )

            Log.showValue(
                self.Config,
                Log.Level.DEBUG,
                'EndIndex',
                end_index
            )

            error_post_list = []
            del_post_list = []
            if self.Config.LogLevel == Log.Level.INFO:
                PB = progressbar.ProgressBar(
                    max_value=end_index - start_index + 1,
                    redirect_stdout=True
                )
            for index in range(start_index, end_index + 1):

                for i in range(2):
                    need_continue = False
                    post = None
                    try:
                        post = self._getPost(
                            board,
                            post_index=index,
                            search_type=search_type,
                            search_condition=search_condition,
                            query=query
                        )
                    except Exceptions.ParseError as e:
                        if i == 1:
                            raise e
                        need_continue = True
                    except Exceptions.UnknownError as e:
                        if i == 1:
                            raise e
                        need_continue = True
                    except Exceptions.NoSuchBoard as e:
                        if i == 1:
                            raise e
                        need_continue = True
                    except Exceptions.NoMatchTargetError as e:
                        if i == 1:
                            raise e
                        need_continue = True
                    except Exceptions.ConnectionClosed as e:
                        if i == 1:
                            raise e
                        Log.log(
                            self.Config,
                            Log.Level.INFO,
                            i18n.RestoreConnection
                        )
                        self._login(
                            self._ID,
                            self._Password,
                            self.Config.KickOtherLogin
                        )
                        need_continue = True
                    except Exceptions.UseTooManyResources as e:
                        if i == 1:
                            raise e
                        Log.log(
                            self.Config,
                            Log.Level.INFO,
                            i18n.RestoreConnection
                        )
                        self._login(
                            self._ID,
                            self._Password,
                            self.Config.KickOtherLogin
                        )
                        need_continue = True

                    if post is None:
                        need_continue = True
                    elif not post.isFormatCheck():
                        need_continue = True

                    if need_continue:
                        Log.log(
                            self.Config,
                            Log.Level.DEBUG,
                            'Wait for retry repost'
                        )
                        time.sleep(0.1)
                        continue

                    break

                if self.Config.LogLevel == Log.Level.INFO:
                    PB.update(index - start_index)
                if post is None:
                    error_post_list.append(index)
                    continue
                if not post.isFormatCheck():
                    if post.getAID() is not None:
                        error_post_list.append(post.getAID())
                    else:
                        error_post_list.append(index)
                    continue
                if post.getDeleteStatus() != DataType.PostDeleteStatus.NotDeleted:
                    del_post_list.append(index)
                post_handler(post)
            if self.Config.LogLevel == Log.Level.INFO:
                PB.finish()

            return error_post_list, del_post_list

        else:
            if self.Config.Host == DataType.Host.PTT2:
                raise Exceptions.HostNotSupport(Util.getCurrentFuncName())

            # 網頁版本爬蟲
            # https://www.ptt.cc/bbs/index.html

            # 1. 取得總共有幾頁 MaxPage
            newest_index = self._getNewestIndex(
                DataType.IndexType.Web,
                board=board
            )
            # 2. 檢查 StartPage 跟 EndPage 有沒有在 1 ~ MaxPage 之間

            CheckValue.checkIndexRange(
                self.Config,
                'StartPage',
                start_page,
                'EndPage',
                end_page,
                MaxValue=newest_index
            )

            # 3. 把每篇文章(包括被刪除文章)欄位解析出來組合成 DataType.PostInfo
            error_post_list = []
            del_post_list = []
            # PostAID = ""
            _url = 'https://www.ptt.cc/bbs/'
            index = str(newest_index)
            if self.Config.LogLevel == Log.Level.INFO:
                PB = progressbar.ProgressBar(
                    max_value=end_page - start_page + 1,
                    redirect_stdout=True
                )

            def deleted_post(post_title):
                if post_title.startswith('('):
                    if '本文' in post_title:
                        return DataType.PostDeleteStatus.ByAuthor
                    elif post_title.startswith('(已被'):
                        return DataType.PostDeleteStatus.ByModerator
                    else:
                        return DataType.PostDeleteStatus.ByUnknow
                else:
                    return DataType.PostDeleteStatus.NotDeleted

            for index in range(start_page, newest_index + 1):
                Log.showValue(
                    self.Config,
                    Log.Level.DEBUG,
                    'CurrentPage',
                    index
                )

                url = _url + board + '/index' + str(index) + '.html'
                r = requests.get(url, cookies={'over18': '1'})
                if r.status_code != requests.codes.ok:
                    raise Exceptions.NoSuchBoard(self.Config, board)
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

                    post = DataType.PostInfo(
                        Board=board,
                        Author=post['author'],
                        Title=post['title'],
                        WebUrl='https://www.ptt.cc' + post['web'],
                        DeleteStatus=deleted_post(post['title'])
                    )
                    post_handler(post)

                if self.Config.LogLevel == Log.Level.INFO:
                    PB.update(index - start_page)

            Log.showValue(
                self.Config,
                Log.Level.DEBUG,
                'DelPostList',
                del_post_list
            )

            # 4. 把組合出來的 Post 塞給 handler

            # 5. 顯示 progress bar
            if self.Config.LogLevel == Log.Level.INFO:
                PB.finish()

            return error_post_list, del_post_list

    def post(
            self,
            board: str,
            title: str,
            content: str,
            post_type: int,
            sign_file
    ):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'Board', board)
        CheckValue.check(self.Config, str, 'Title', title)
        CheckValue.check(self.Config, str, 'Content', content)
        CheckValue.check(self.Config, int, 'PostType', post_type)

        check_sign_file = False
        for i in range(0, 10):
            if str(i) == sign_file or i == sign_file:
                check_sign_file = True
                break

        if not check_sign_file:
            sign_file = sign_file.lower()
            if sign_file != 'x':
                raise ValueError(Log.merge(
                    self.Config,
                    [
                        'SignFile',
                        i18n.ErrorParameter,
                        sign_file
                    ]))

        self._checkBoard(board)

        try:
            from . import api_post
        except ModuleNotFoundError:
            import api_post

        return api_post.post(
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
            post_index: int = 0):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'Board', board)
        CheckValue.check(self.Config, int, 'PushType',
                         push_type, Class=DataType.PushType)
        CheckValue.check(self.Config, str, 'PushContent', push_content)
        if post_aid is not None:
            CheckValue.check(self.Config, str, 'PostAID', post_aid)
        CheckValue.check(self.Config, int, 'PostIndex', post_index)

        if len(board) == 0:
            raise ValueError(Log.merge(
                self.Config,
                [
                    i18n.Board,
                    i18n.ErrorParameter,
                    board
                ]))

        if post_index != 0 and isinstance(post_aid, str):
            raise ValueError(Log.merge(
                self.Config,
                [
                    'PostIndex',
                    'PostAID',
                    i18n.ErrorParameter,
                    i18n.BothInput
                ]))

        if post_index == 0 and post_aid is None:
            raise ValueError(Log.merge(
                self.Config,
                [
                    'PostIndex',
                    'PostAID',
                    i18n.ErrorParameter,
                    i18n.NoInput
                ]))

        if post_index != 0:
            newest_index = self._getNewestIndex(
                DataType.IndexType.BBS,
                board=board
            )
            CheckValue.checkIndex(self.Config, 'PostIndex',
                                  post_index, newest_index)

        self._checkBoard(board)

        max_push_length = 33
        push_list = []

        temp_start_index = 0
        temp_end_index = temp_start_index + 1

        while temp_end_index <= len(push_content):

            temp = ''
            last_temp = None
            while len(temp.encode('big5-uao', 'replace')) < max_push_length:
                temp = push_content[temp_start_index:temp_end_index]

                if not len(temp.encode('big5-uao', 'replace')) < max_push_length:
                    break
                elif push_content.endswith(temp):
                    break
                elif temp.endswith('\n'):
                    break
                elif last_temp == temp:
                    break

                temp_end_index += 1
                last_temp = temp

            push_list.append(temp.strip())

            temp_start_index = temp_end_index
            temp_end_index = temp_start_index + 1
        push_list = filter(None, push_list)

        for push in push_list:
            Log.showValue(
                self.Config,
                Log.Level.INFO,
                i18n.Push,
                push
            )

            for _ in range(2):
                try:
                    self._push(
                        board,
                        push_type,
                        push,
                        post_aid=post_aid,
                        post_index=post_index
                    )
                    break
                except Exceptions.NoFastPush:
                    # Screens.show(self.Config, self._ConnectCore.getScreenQueue())
                    Log.log(
                        self.Config,
                        Log.Level.INFO,
                        '等待快速推文'
                    )
                    time.sleep(5.2)

    def _push(
            self,
            board: str,
            push_type: int,
            push_content: str,
            post_aid: str = None,
            post_index: int = 0):

        try:
            from . import api_push
        except ModuleNotFoundError:
            import api_push

        return api_push.push(
            self,
            board,
            push_type,
            push_content,
            post_aid,
            post_index)

    def _getUser(self, user_id):

        CheckValue.check(self.Config, str, 'UserID', user_id)
        if len(user_id) < 3:
            raise ValueError(Log.merge(
                self.Config,
                [
                    'UserID',
                    i18n.ErrorParameter,
                    user_id
                ]))

        try:
            from . import api_getUser
        except ModuleNotFoundError:
            import api_getUser

        return api_getUser.getUser(self, user_id)

    def getUser(self, user_id):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if self._UnregisteredUser:
            raise Exceptions.UnregisteredUser(Util.getCurrentFuncName())

        return self._getUser(user_id)

    def throwWaterBall(self, pttid, content):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if self._UnregisteredUser:
            raise Exceptions.UnregisteredUser(Util.getCurrentFuncName())

        CheckValue.check(self.Config, str, 'TargetID', pttid)
        CheckValue.check(self.Config, str, 'Content', content)

        if len(pttid) <= 2:
            raise ValueError(Log.merge(
                self.Config,
                [
                    'TargetID',
                    i18n.ErrorParameter,
                    pttid
                ]))

        User = self._getUser(pttid)
        if '不在站上' in User.getState():
            raise Exceptions.UserOffline(pttid)

        try:
            from . import api_WaterBall
        except ModuleNotFoundError:
            import api_WaterBall

        return api_WaterBall.throwWaterBall(self, pttid, content)

    def getWaterBall(self, operate_type):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if self._UnregisteredUser:
            raise Exceptions.UnregisteredUser(Util.getCurrentFuncName())

        CheckValue.check(
            self.Config, int, 'OperateType', operate_type,
            Class=DataType.WaterBallOperateType)

        try:
            from . import api_WaterBall
        except ModuleNotFoundError:
            import api_WaterBall

        return api_WaterBall.get_waterball(self, operate_type)

    def getCallStatus(self):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        return self._getCallStatus()

    def _getCallStatus(self):

        try:
            from . import api_CallStatus
        except ModuleNotFoundError:
            import api_CallStatus

        return api_CallStatus.getCallStatus(self)

    def setCallStatus(
            self,
            call_status):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, int, 'CallStatus', call_status,
                         Class=DataType.CallStatus)

        try:
            from . import api_CallStatus
        except ModuleNotFoundError:
            import api_CallStatus

        return api_CallStatus.setCallStatus(self, call_status)

    def giveMoney(self, pttid, money):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if self._UnregisteredUser:
            raise Exceptions.UnregisteredUser(Util.getCurrentFuncName())

        CheckValue.check(self.Config, str, 'ID', pttid)
        CheckValue.check(self.Config, int, 'Money', money)
        # Check user
        self.getUser(pttid)

        try:
            from . import api_giveMoney
        except ModuleNotFoundError:
            import api_giveMoney

        return api_giveMoney.giveMoney(self, pttid, money)

    def mail(
            self,
            pttid: str,
            title: str,
            content: str,
            sign_file):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'ID', pttid)
        CheckValue.check(self.Config, str, 'Title', title)
        CheckValue.check(self.Config, str, 'Content', content)

        check_sign_file = False
        for i in range(0, 10):
            if str(i) == sign_file or i == sign_file:
                check_sign_file = True
                break

        if not check_sign_file:
            sign_file = sign_file.lower()
            if sign_file != 'x':
                raise ValueError(Log.merge(
                    self.Config,
                    [
                        'SignFile',
                        i18n.ErrorParameter,
                        sign_file
                    ]))

        try:
            from . import api_mail
        except ModuleNotFoundError:
            import api_mail

        return api_mail.mail(
            self,
            pttid,
            title,
            content,
            sign_file)

    def hasNewMail(self):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        try:
            from . import api_hasNewMail
        except ModuleNotFoundError:
            import api_hasNewMail

        return api_hasNewMail.hasNewMail(self)

    def getBoardList(self):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        try:
            from . import api_getBoardList
        except ModuleNotFoundError:
            import api_getBoardList

        return api_getBoardList.getBoardList(self)

    def replyPost(
            self,
            reply_type: int,
            board: str,
            content: str,
            sign_file=0,
            post_aid: str = None,
            post_index: int = 0):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, int, 'ReplyType', reply_type,
                         Class=DataType.ReplyType)
        CheckValue.check(self.Config, str, 'Board', board)
        CheckValue.check(self.Config, str, 'Content', content)
        if post_aid is not None:
            CheckValue.check(self.Config, str, 'PostAID', post_aid)

        if post_index != 0:
            newest_index = self._getNewestIndex(
                DataType.IndexType.BBS,
                board=board)
            CheckValue.checkIndex(
                self.Config, 'PostIndex',
                post_index, MaxValue=newest_index)

        sign_file_list = [str(x) for x in range(0, 10)]
        sign_file_list.append('x')

        if str(sign_file) not in sign_file_list:
            raise ValueError(Log.merge(
                self.Config,
                [
                    'SignFile',
                    i18n.ErrorParameter
                ]))

        if post_aid is not None and post_index != 0:
            raise ValueError(Log.merge(
                self.Config,
                [
                    'PostIndex',
                    'PostAID',
                    i18n.ErrorParameter,
                    i18n.BothInput
                ]))

        self._checkBoard(board)

        try:
            from . import api_replyPost
        except ModuleNotFoundError:
            import api_replyPost

        api_replyPost.replyPost(
            self,
            reply_type,
            board,
            content,
            sign_file,
            post_aid,
            post_index)

    def setBoardTitle(
            self,
            board: str,
            new_title: str):
        # 第一支板主專用 API
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'Board', board)
        CheckValue.check(self.Config, str, 'NewTitle', new_title)

        self._checkBoard(
            board,
            check_moderator=True
        )

        try:
            from . import api_setBoardTitle
        except ModuleNotFoundError:
            import api_setBoardTitle

        api_setBoardTitle.setBoardTitle(self, board, new_title)

    def markPost(
            self,
            mark_type: int,
            board: str,
            post_aid: str = None,
            post_index: int = 0,
            search_type: int = 0,
            search_condition: str = None,
    ):
        # 標記文章
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        try:
            from . import api_markPost
        except ModuleNotFoundError:
            import api_markPost

        api_markPost.markPost(
            self,
            mark_type,
            board,
            post_aid,
            post_index,
            search_type,
            search_condition
        )

    def getFavouriteBoard(self):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        try:
            from . import api_getFavouriteBoard
        except ModuleNotFoundError:
            import api_getFavouriteBoard

        return api_getFavouriteBoard.getFavouriteBoard(self)

    def bucket(self, board: str, bucket_days: int, reason: str, pttid: str):

        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'Board', board)
        CheckValue.check(self.Config, int, 'BucketDays', bucket_days)
        CheckValue.check(self.Config, str, 'Reason', reason)
        CheckValue.check(self.Config, str, 'TargetID', pttid)

        self._getUser(pttid)

        self._checkBoard(
            board,
            check_moderator=True
        )

        try:
            from . import api_bucket
        except ModuleNotFoundError:
            import api_bucket

        api_bucket.bucket(
            self, board, bucket_days, reason, pttid)

    def searchUser(
            self,
            target: str,
            minpage: int = None,
            maxpage: int = None):

        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'target', target)
        if minpage is not None:
            CheckValue.checkIndex(
                self.Config,
                'minpage',
                minpage
            )
        if maxpage is not None:
            CheckValue.checkIndex(
                self.Config,
                'maxpage',
                maxpage
            )
        if minpage is not None and maxpage is not None:
            CheckValue.checkIndexRange(
                self.Config,
                'minpage',
                minpage,
                'maxpage',
                maxpage
            )

        try:
            from . import api_searchuser
        except ModuleNotFoundError:
            import api_searchuser

        return api_searchuser.searchuser(self, target, minpage, maxpage)

    def getBoardInfo(self, board):

        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'Board', board)

        return self._getBoardInfo(board)

    def _getBoardInfo(self, board):

        try:
            from . import api_getBoardInfo
        except ModuleNotFoundError:
            import api_getBoardInfo

        return api_getBoardInfo.getBoardInfo(self, board)


if __name__ == '__main__':
    print('PTT Library v ' + Version)
    print('Developed by PTT CodingMan')
