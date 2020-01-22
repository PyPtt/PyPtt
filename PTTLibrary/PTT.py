import sys
import time
import re
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
    from . import Screens
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
    import Screens
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
        Language: int = 0,
        ConnectMode: int = 0,
        LogLevel: int = 0,
        ScreenTimeOut: int = 0,
        ScreenLongTimeOut: int = 0,
        LogHandler=None,
        Host: int = 0,
    ):

        if LogHandler is not None and not callable(LogHandler):
            raise TypeError('[PTT Library] LogHandler is must callable!!')

        if LogHandler is not None:
            hasLogHandler = True
            setLogHandlerResult = True
            try:
                LogHandler(f'PTT Library v {Version}')
                LogHandler('Developed by PTT CodingMan')
            except Exception:
                LogHandler = None
                setLogHandlerResult = False
        else:
            hasLogHandler = False

        print(f'PTT Library v {Version}')
        print('Developed by PTT CodingMan')

        self._LoginStatus = False

        self.Config = Config.Config()

        if not isinstance(Language, int):
            raise TypeError('[PTT Library] Language must be integer')
        if not isinstance(ConnectMode, int):
            raise TypeError('[PTT Library] ConnectMode must be integer')
        if not isinstance(LogLevel, int):
            raise TypeError('[PTT Library] LogLevel must be integer')
        if not isinstance(ScreenTimeOut, int):
            raise TypeError('[PTT Library] ScreenTimeOut must be integer')
        if not isinstance(ScreenLongTimeOut, int):
            raise TypeError('[PTT Library] ScreenLongTimeOut must be integer')
        if not isinstance(Host, int):
            raise TypeError('[PTT Library] Host must be integer')

        if ScreenTimeOut != 0:
            self.Config.ScreenTimeOut = ScreenTimeOut
        if ScreenLongTimeOut != 0:
            self.Config.ScreenLongTimeOut = ScreenLongTimeOut

        if LogLevel == 0:
            LogLevel = self.Config.LogLevel
        elif not Util.checkRange(Log.Level, LogLevel):
            raise ValueError('[PTT Library] Unknow LogLevel', LogLevel)
        else:
            self.Config.LogLevel = LogLevel

        if Language == 0:
            Language = self.Config.Language
        elif not Util.checkRange(i18n.Language, Language):
            raise ValueError('[PTT Library] Unknow language', Language)
        else:
            self.Config.Language = Language
        i18n.load(Language)

        if LogHandler is not None:
            # Log.Handler = LogHandler
            self.Config.LogHandler = LogHandler
            Log.showValue(
                self.Config,
                Log.Level.INFO,
                i18n.LogHandler,
                i18n.Init
            )
        elif hasLogHandler and not setLogHandlerResult:
            Log.showValue(
                self.Config,
                Log.Level.INFO,
                i18n.LogHandler,
                [
                    i18n.Init,
                    i18n.Fail
                ]
            )

        if Language == i18n.Language.Chinese:
            Log.showValue(self.Config, Log.Level.INFO, [
                i18n.ChineseTranditional,
                i18n.LanguageModule
            ],
                i18n.Init
            )
        elif Language == i18n.Language.English:
            Log.showValue(self.Config, Log.Level.INFO, [
                i18n.English,
                i18n.LanguageModule
            ],
                i18n.Init
            )

        if ConnectMode == 0:
            ConnectMode = self.Config.ConnectMode
        elif not Util.checkRange(ConnectCore.ConnectMode, ConnectMode):
            raise ValueError('[PTT Library] Unknow ConnectMode', ConnectMode)
        else:
            self.Config.ConnectMode = ConnectMode

        if Host == 0:
            Host = self.Config.Host
        elif not Util.checkRange(DataType.Host, Host):
            raise ValueError('[PTT Library] Unknow Host', Host)
        self.Config.Host = Host

        if Host == DataType.Host.PTT1:
            Log.showValue(
                self.Config,
                Log.Level.INFO,
                [
                    i18n.Connect,
                    i18n.Host
                ],
                i18n.PTT
            )
        if Host == DataType.Host.PTT2:
            Log.showValue(
                self.Config,
                Log.Level.INFO,
                [
                    i18n.Connect,
                    i18n.Host
                ],
                i18n.PTT2
            )

        self._ConnectCore = ConnectCore.API(self.Config, Host)
        self._ExistBoardList = []
        self._ModeratorList = dict()
        self._LastThroWaterBallTime = 0
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
        CurrentThreadID = threading.get_ident()
        if CurrentThreadID == self._ThreadID:
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
            CurrentThreadID
        )
        raise Exceptions.MultiThreadOperated()

    def getVersion(self) -> str:
        self._OneThread()
        return self.Config.Version

    def _login(
        self,
        ID: str,
        Password: str,
        KickOtherLogin: bool = False
    ):

        if self._LoginStatus:
            self.logout()

        CheckValue.check(self.Config, str, 'ID', ID)
        CheckValue.check(self.Config, str, 'Password', Password)
        CheckValue.check(self.Config, bool, 'KickOtherLogin', KickOtherLogin)

        self.Config.KickOtherLogin = KickOtherLogin

        def KickOtherLoginDisplayMsg():
            if self.Config.KickOtherLogin:
                return i18n.KickOtherLogin
            return i18n.NotKickOtherLogin

        def KickOtherLoginResponse(Screen):
            if self.Config.KickOtherLogin:
                return 'y' + Command.Enter
            return 'n' + Command.Enter

        if len(Password) > 8:
            Password = Password[:8]

        ID = ID.strip()
        Password = Password.strip()

        self._ID = ID
        self._Password = Password

        Log.showValue(
            self.Config,
            Log.Level.INFO,
            [
                i18n.Login,
                i18n.ID
            ],
            ID
        )

        self.Config.KickOtherLogin = KickOtherLogin

        self._ConnectCore.connect()

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.HasNewMailGotoMainMenu,
                '你有新信件',
                Response=Command.GoMainMenu,
            ),
            ConnectCore.TargetUnit(
                i18n.LoginSuccess,
                Screens.Target.MainMenu,
                BreakDetect=True
            ),
            ConnectCore.TargetUnit(
                i18n.GoMainMenu,
                '【看板列表】',
                Response=Command.GoMainMenu,
            ),
            ConnectCore.TargetUnit(
                i18n.ErrorIDPW,
                '密碼不對或無此帳號',
                BreakDetect=True,
                Exceptions=Exceptions.WrongIDorPassword()
            ),
            ConnectCore.TargetUnit(
                i18n.LoginTooOften,
                '登入太頻繁',
                BreakDetect=True,
                Exceptions=Exceptions.LoginTooOften()
            ),
            ConnectCore.TargetUnit(
                i18n.SystemBusyTryLater,
                '系統過載',
                BreakDetect=True,
            ),
            ConnectCore.TargetUnit(
                i18n.DelWrongPWRecord,
                '您要刪除以上錯誤嘗試的記錄嗎',
                Response='y' + Command.Enter,
            ),
            ConnectCore.TargetUnit(
                i18n.MailBoxFull,
                '您保存信件數目',
                Response=Command.GoMainMenu,
            ),
            ConnectCore.TargetUnit(
                i18n.PostNotFinish,
                '請選擇暫存檔 (0-9)[0]',
                Response=Command.Enter,
            ),
            ConnectCore.TargetUnit(
                i18n.PostNotFinish,
                '有一篇文章尚未完成',
                Response='Q' + Command.Enter,
            ),
            ConnectCore.TargetUnit(
                i18n.SigningUnPleaseWait,
                '登入中，請稍候',
            ),
            ConnectCore.TargetUnit(
                KickOtherLoginDisplayMsg,
                '您想刪除其他重複登入的連線嗎',
                Response=KickOtherLoginResponse,
            ),
            ConnectCore.TargetUnit(
                i18n.AnyKeyContinue,
                '任意鍵',
                Response=Command.Enter
            ),
            ConnectCore.TargetUnit(
                i18n.SigningUpdate,
                '正在更新與同步線上使用者及好友名單',
            ),
        ]

        CmdList = []
        CmdList.append(ID)
        CmdList.append(Command.Enter)
        CmdList.append(Password)
        CmdList.append(Command.Enter)

        Cmd = ''.join(CmdList)

        index = self._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=self.Config.ScreenLongTimeOut,
            Refresh=False,
            Secret=True
        )

        if TargetList[index].getDisplayMsg() != i18n.LoginSuccess:
            # OriScreen = self._ConnectCore.getScreenQueue()[-1]
            # print(OriScreen)
            raise Exceptions.LoginError()

        OriScreen = self._ConnectCore.getScreenQueue()[-1]
        if '> (' in OriScreen:
            self._Cursor = DataType.Cursor.New
            Log.log(
                self.Config,
                Log.Level.DEBUG,
                i18n.NewCursor
            )
        else:
            self._Cursor = DataType.Cursor.Old
            Log.log(
                self.Config,
                Log.Level.DEBUG,
                i18n.OldCursor
            )

        if self._Cursor not in Screens.Target.InBoardWithCursor:
            Screens.Target.InBoardWithCursor.append('\n' + self._Cursor)

        self._UnregisteredUser = False
        if '(T)alk' not in OriScreen:
            self._UnregisteredUser = True
        if '(P)lay' not in OriScreen:
            self._UnregisteredUser = True
        if '(N)amelist' not in OriScreen:
            self._UnregisteredUser = True

        if self._UnregisteredUser:
            Log.log(
                self.Config,
                Log.Level.INFO,
                i18n.UnregisteredUserCantUseAllAPI
            )

        self._LoginStatus = True

    def login(
        self,
        ID: str,
        Password: str,
        KickOtherLogin: bool = False
    ):
        self._OneThread()
        try:
            return self._login(
                ID,
                Password,
                KickOtherLogin=KickOtherLogin
            )
        except Exceptions.LoginError:
            return self._login(
                ID,
                Password,
                KickOtherLogin=KickOtherLogin
            )

    def logout(self):
        self._OneThread()

        if not self._LoginStatus:
            return

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('g')
        CmdList.append(Command.Enter)
        CmdList.append('y')
        CmdList.append(Command.Enter)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                [
                    i18n.Logout,
                    i18n.Success,
                ],
                '任意鍵',
                BreakDetect=True,
            ),
        ]

        Log.log(
            self.Config,
            Log.Level.INFO,
            [
                i18n.Start,
                i18n.Logout
            ]
        )

        try:
            self._ConnectCore.send(Cmd, TargetList)
            self._ConnectCore.close()
        except Exceptions.ConnectionClosed:
            pass
        except RuntimeError:
            pass

        self._LoginStatus = False

        Log.showValue(
            self.Config,
            Log.Level.INFO,
            i18n.Logout,
            i18n.Done
        )

    def log(self, Msg):
        self._OneThread()
        Log.log(self.Config, Log.Level.INFO, Msg)

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
        Board: str,
        PostAID: str = None,
        PostIndex: int = 0,
        SearchType: int = 0,
        SearchCondition: str = None,
        Query: bool = False
    ):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'Board', Board)
        if PostAID is not None:
            CheckValue.check(self.Config, str, 'PostAID', PostAID)
        CheckValue.check(self.Config, int, 'PostIndex', PostIndex)
        CheckValue.check(self.Config, int, 'SearchType', SearchType,
                         Class=DataType.PostSearchType)
        if SearchCondition is not None:
            CheckValue.check(self.Config, str,
                             'SearchCondition', SearchCondition)

        if len(Board) == 0:
            raise ValueError(Log.merge([
                i18n.Board,
                i18n.ErrorParameter,
                Board
            ]))

        if PostIndex != 0 and isinstance(PostAID, str):
            raise ValueError(Log.merge([
                'PostIndex',
                'PostAID',
                i18n.ErrorParameter,
                i18n.BothInput
            ]))

        if PostIndex == 0 and PostAID is None:
            raise ValueError(Log.merge([
                'PostIndex',
                'PostAID',
                i18n.ErrorParameter
            ]))

        if SearchCondition is not None and SearchType == 0:
            raise ValueError(Log.merge([
                'SearchType',
                i18n.ErrorParameter,
            ]))

        if SearchType == DataType.PostSearchType.Push:
            try:
                S = int(SearchCondition)
            except ValueError:
                raise ValueError(Log.merge([
                    'SearchCondition',
                    i18n.ErrorParameter,
                ]))

            if not (-100 <= S <= 110):
                raise ValueError(Log.merge([
                    'SearchCondition',
                    i18n.ErrorParameter,
                ]))

        if PostAID is not None and SearchCondition is not None:
            raise ValueError(Log.merge([
                'PostAID',
                'SearchCondition',
                i18n.ErrorParameter,
                i18n.BothInput,
            ]))

        if PostIndex != 0:
            NewestIndex = self._getNewestIndex(
                DataType.IndexType.BBS,
                Board=Board,
                SearchType=SearchType,
                SearchCondition=SearchCondition
            )

            if PostIndex < 1 or NewestIndex < PostIndex:
                raise ValueError(Log.merge([
                    'PostIndex',
                    i18n.ErrorParameter,
                    i18n.OutOfRange,
                ]))

        self._checkBoard(Board)

        for i in range(2):

            NeedContinue = False
            Post = None
            try:
                Post = self._getPost(
                    Board,
                    PostAID,
                    PostIndex,
                    SearchType,
                    SearchCondition,
                    Query
                )
            except Exceptions.ParseError as e:
                if i == 1:
                    raise e
                NeedContinue = True
            except Exceptions.UnknowError as e:
                if i == 1:
                    raise e
                NeedContinue = True
            except Exceptions.NoSuchBoard as e:
                if i == 1:
                    raise e
                NeedContinue = True
            except Exceptions.NoMatchTargetError as e:
                if i == 1:
                    raise e
                NeedContinue = True

            if Post is None:
                NeedContinue = True
            elif not Post.isFormatCheck():
                NeedContinue = True

            if NeedContinue:
                Log.log(
                    self.Config,
                    Log.Level.DEBUG,
                    'Wait for retry repost'
                )
                time.sleep(0.1)
                continue

            break
        return Post

    def _checkBoard(
        self,
        Board,
        CheckModerator: bool = False
    ):
        if Board.lower() not in self._ExistBoardList:
            CmdList = []
            CmdList.append(Command.GoMainMenu)
            CmdList.append('qs')
            CmdList.append(Board)
            CmdList.append(Command.Enter)
            CmdList.append(Command.Ctrl_C * 2)
            CmdList.append(Command.Space)
            CmdList.append('i')
            Cmd = ''.join(CmdList)

            TargetList = [
                ConnectCore.TargetUnit(
                    i18n.AnyKeyContinue,
                    '任意鍵繼續',
                    BreakDetect=True,
                    LogLevel=Log.Level.DEBUG
                ),
                # ConnectCore.TargetUnit(
                #     i18n.NoSuchBoard,
                #     Screens.Target.MainMenu,
                #     BreakDetect=True,
                #     LogLevel=Log.Level.DEBUG
                # ),
            ]

            index = self._ConnectCore.send(Cmd, TargetList)
            if index < 0:
                raise Exceptions.NoSuchBoard(self.Config, Board)

            OriScreen = self._ConnectCore.getScreenQueue()[-1]

            # print(OriScreen)
            # if index == 1:
            #     raise Exceptions.NoSuchBoard(self.Config, Board)

            BoardNameLine = [line.strip() for line in OriScreen.split(
                '\n') if line.strip().startswith('《')]
            if len(BoardNameLine) != 1:
                raise Exceptions.UnknowError(OriScreen)
            BoardNameLine = BoardNameLine[0]
            if '《' not in BoardNameLine or '》' not in BoardNameLine:
                raise Exceptions.UnknowError(BoardNameLine)

            BoardName = BoardNameLine[1:BoardNameLine.find('》')].lower()

            Log.showValue(
                self.Config,
                Log.Level.DEBUG,
                'Find Board Name',
                BoardName
            )

            self._ExistBoardList.append(BoardName)

            if BoardName != Board.lower():
                raise Exceptions.NoSuchBoard(self.Config, Board)

            CheckModeratorLine = [line.strip() for line in OriScreen.split(
                '\n') if line.strip().startswith('板主名單:')]

            if len(CheckModeratorLine) != 1:
                raise Exceptions.UnknowError(OriScreen)

            if BoardName not in self._ModeratorList:

                CheckModeratorLine = CheckModeratorLine[0]
                CheckModeratorLine = CheckModeratorLine[5:].strip()

                CheckModeratorList = CheckModeratorLine.split('/')
                CheckModeratorList = [x.lower() for x in CheckModeratorList]
                Log.showValue(
                    self.Config,
                    Log.Level.DEBUG,
                    'CheckModeratorLine',
                    CheckModeratorLine
                )

                self._ModeratorList[BoardName] = CheckModeratorList

        if CheckModerator:
            if self._ID.lower() not in self._ModeratorList[Board.lower()]:
                raise Exceptions.NeedModeratorPermission(Board)

    def _getPost(
            self,
            Board: str,
            PostAID: str = None,
            PostIndex: int = 0,
            SearchType: int = 0,
            SearchCondition: str = None,
            Query: bool = False):

        try:
            from . import api_getPost
        except ModuleNotFoundError:
            import api_getPost

        return api_getPost.getPost(
            self,
            Board,
            PostAID,
            PostIndex,
            SearchType,
            SearchCondition,
            Query)

    def _getNewestIndex(
            self,
            IndexType: int,
            Board: str = None,
            # BBS
            SearchType: int = 0,
            SearchCondition: str = None):

        CheckValue.check(
            self.Config, int, 'IndexType',
            IndexType, Class=DataType.IndexType)
        CheckValue.check(self.Config, str, 'Board', Board)

        try:
            from . import api_getNewestIndex
        except ModuleNotFoundError:
            import api_getNewestIndex

        return api_getNewestIndex.getNewestIndex(
            self,
            IndexType,
            Board,
            SearchType,
            SearchCondition)

    def getNewestIndex(
            self,
            IndexType: int,
            Board: str = None,
            SearchType: int = 0,
            SearchCondition: str = None):
        self._OneThread()

        if IndexType == DataType.IndexType.BBS:
            if not self._LoginStatus:
                raise Exceptions.RequireLogin(i18n.RequireLogin)

        try:
            return self._getNewestIndex(
                IndexType,
                Board,
                SearchType,
                SearchCondition
            )
        except:
            return self._getNewestIndex(
                IndexType,
                Board,
                SearchType,
                SearchCondition
            )

    def _getPostIndex(
            self,
            Board,
            AID):

        try:
            from . import api_getPostIndex
        except ModuleNotFoundError:
            import api_getPostIndex

        return api_getPostIndex.getPostIndex(
            self,
            Board,
            AID)

    def crawlBoard(
            self,
            PostHandler,
            CrawlType: int,
            Board: str,
            # BBS版本
            StartIndex: int = 0,
            EndIndex: int = 0,
            StartAID: str = None,
            EndAID: str = None,
            SearchType: int = 0,
            SearchCondition: str = None,
            Query: bool = False,
            # 網頁版本
            StartPage: int = 0,
            EndPage: int = 0):

        self._OneThread()

        CheckValue.check(
            self.Config, int, 'CrawlType',
            CrawlType, Class=DataType.CrawlType)
        CheckValue.check(self.Config, str, 'Board', Board)

        if len(Board) == 0:
            raise ValueError(Log.merge([
                i18n.Board,
                i18n.ErrorParameter,
                Board
            ]))

        if CrawlType == DataType.CrawlType.BBS:
            if not self._LoginStatus:
                raise Exceptions.RequireLogin(i18n.RequireLogin)

            CheckValue.check(self.Config, int, 'SearchType', SearchType)
            if SearchCondition is not None:
                CheckValue.check(self.Config, str,
                                 'SearchCondition', SearchCondition)
            if StartAID is not None:
                CheckValue.check(self.Config, str, 'StartAID', StartAID)
            if EndAID is not None:
                CheckValue.check(self.Config, str, 'EndAID', EndAID)

            if (StartAID is not None or EndAID is not None) and \
               (StartIndex != 0 or EndIndex != 0):
                raise ValueError(Log.merge([
                    'AID',
                    'Index',
                    i18n.ErrorParameter,
                    i18n.BothInput
                ]))

            if (StartAID is not None or EndAID is not None) and \
               (SearchCondition is not None):
                raise ValueError(Log.merge([
                    'AID',
                    'SearchCondition',
                    i18n.ErrorParameter,
                    i18n.BothInput
                ]))

            if SearchType == DataType.PostSearchType.Push:
                try:
                    S = int(SearchCondition)
                except ValueError:
                    raise ValueError(Log.merge([
                        'SearchCondition',
                        i18n.ErrorParameter,
                    ]))

                if not (-100 <= S <= 110):
                    raise ValueError(Log.merge([
                        'SearchCondition',
                        i18n.ErrorParameter,
                    ]))

            if StartIndex != 0:
                NewestIndex = self._getNewestIndex(
                    DataType.IndexType.BBS,
                    Board=Board,
                    SearchType=SearchType,
                    SearchCondition=SearchCondition
                )
                CheckValue.checkIndexRange(
                    self.Config,
                    'StartIndex',
                    StartIndex,
                    'EndIndex',
                    EndIndex,
                    MaxValue=NewestIndex
                )
            elif StartAID is not None and EndAID is not None:
                StartIndex = self._getPostIndex(
                    Board,
                    StartAID,
                )
                EndIndex = self._getPostIndex(
                    Board,
                    EndAID,
                )

                CheckValue.checkIndexRange(
                    self.Config,
                    'StartAID',
                    StartIndex,
                    'EndAID',
                    EndIndex
                )
            else:
                raise ValueError(Log.merge([
                    i18n.ErrorParameter,
                    i18n.NoInput
                ]))

            Log.showValue(
                self.Config,
                Log.Level.DEBUG,
                'StartIndex',
                StartIndex
            )

            Log.showValue(
                self.Config,
                Log.Level.DEBUG,
                'EndIndex',
                EndIndex
            )

            ErrorPostList = []
            DelPostList = []
            if self.Config.LogLevel == Log.Level.INFO:
                PB = progressbar.ProgressBar(
                    max_value=EndIndex - StartIndex + 1,
                    redirect_stdout=True
                )
            for index in range(StartIndex, EndIndex + 1):

                for i in range(2):
                    NeedContinue = False
                    Post = None
                    try:
                        Post = self._getPost(
                            Board,
                            PostIndex=index,
                            SearchType=SearchType,
                            SearchCondition=SearchCondition,
                            Query=Query
                        )
                    except Exceptions.ParseError as e:
                        if i == 1:
                            raise e
                        NeedContinue = True
                    except Exceptions.UnknowError as e:
                        if i == 1:
                            raise e
                        NeedContinue = True
                    except Exceptions.NoSuchBoard as e:
                        if i == 1:
                            raise e
                        NeedContinue = True
                    except Exceptions.NoMatchTargetError as e:
                        if i == 1:
                            raise e
                        NeedContinue = True
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
                        NeedContinue = True
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
                        NeedContinue = True

                    if Post is None:
                        NeedContinue = True
                    elif not Post.isFormatCheck():
                        NeedContinue = True

                    if NeedContinue:
                        Log.log(
                            self.Config,
                            Log.Level.DEBUG,
                            'Wait for retry repost'
                        )
                        time.sleep(0.1)
                        continue

                    break

                if self.Config.LogLevel == Log.Level.INFO:
                    PB.update(index - StartIndex)
                if Post is None:
                    ErrorPostList.append(index)
                    continue
                if not Post.isFormatCheck():
                    if Post.getAID() is not None:
                        ErrorPostList.append(Post.getAID())
                    else:
                        ErrorPostList.append(index)
                    continue
                if Post.getDeleteStatus() != DataType.PostDeleteStatus.NotDeleted:
                    DelPostList.append(index)
                PostHandler(Post)
            if self.Config.LogLevel == Log.Level.INFO:
                PB.finish()

            return ErrorPostList, DelPostList

        else:
            if self.Config.Host == DataType.Host.PTT2:
                raise Exceptions.HostNotSupport(Util.getCurrentFuncName())

            # 網頁版本爬蟲
            # https://www.ptt.cc/bbs/index.html

            # 1. 取得總共有幾頁 MaxPage
            NewestIndex = self._getNewestIndex(
                DataType.IndexType.Web,
                Board=Board
            )
            # 2. 檢查 StartPage 跟 EndPage 有沒有在 1 ~ MaxPage 之間

            CheckValue.checkIndexRange(
                self.Config,
                'StartPage',
                StartPage,
                'EndPage',
                EndPage,
                MaxValue=NewestIndex
            )

            # 3. 把每篇文章(包括被刪除文章)欄位解析出來組合成 DataType.PostInfo
            ErrorPostList = []
            DelPostList = []
            # PostAID = ""
            _url = 'https://www.ptt.cc/bbs/'
            index = str(NewestIndex)
            if self.Config.LogLevel == Log.Level.INFO:
                PB = progressbar.ProgressBar(
                    max_value=EndPage - StartPage + 1,
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

            for index in range(StartPage, NewestIndex + 1):
                Log.showValue(
                    self.Config,
                    Log.Level.DEBUG,
                    'CurrentPage',
                    index
                )

                url = _url + Board + '/index' + str(index) + '.html'
                r = requests.get(url, cookies={'over18': '1'})
                if r.status_code != requests.codes.ok:
                    raise Exceptions.NoSuchBoard(self.Config, Board)
                soup = BeautifulSoup(r.text, 'html.parser')

                for div in soup.select('div.r-ent'):
                    web = div.select('div.title a')
                    post = {
                        'author': div.select('div.author')[0].text,
                        'title': div.select('div.title')[0].text.strip('\n').strip(),
                        'web': web[0].get('href') if web else ''
                    }
                    if post['title'].startswith('('):
                        DelPostList.append(post['title'])
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

                    Post = DataType.PostInfo(
                        Board=Board,
                        Author=post['author'],
                        Title=post['title'],
                        WebUrl='https://www.ptt.cc' + post['web'],
                        DeleteStatus=deleted_post(post['title'])
                    )
                    PostHandler(Post)

                if self.Config.LogLevel == Log.Level.INFO:
                    PB.update(index - StartPage)

            Log.showValue(
                self.Config,
                Log.Level.DEBUG,
                'DelPostList',
                DelPostList
            )

            # 4. 把組合出來的 Post 塞給 handler

            # 5. 顯示 progress bar
            if self.Config.LogLevel == Log.Level.INFO:
                PB.finish()

            return ErrorPostList, DelPostList

    def post(
        self,
        Board: str,
        Title: str,
        Content: str,
        PostType: int,
        SignFile
    ):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'Board', Board)
        CheckValue.check(self.Config, str, 'Title', Title)
        CheckValue.check(self.Config, str, 'Content', Content)
        CheckValue.check(self.Config, int, 'PostType', PostType)

        CheckSignFile = False
        for i in range(0, 10):
            if str(i) == SignFile or i == SignFile:
                CheckSignFile = True
                break

        if not CheckSignFile:
            SignFile = SignFile.lower()
            if SignFile != 'x':
                raise ValueError(Log.merge([
                    'SignFile',
                    i18n.ErrorParameter,
                    SignFile
                ]))

        self._checkBoard(Board)

        try:
            from . import api_post
        except ModuleNotFoundError:
            import api_post

        return api_post.post(
            self,
            Board,
            Title,
            Content,
            PostType,
            SignFile)

    def push(
            self,
            Board: str,
            PushType: int,
            PushContent: str,
            PostAID: str = None,
            PostIndex: int = 0):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'Board', Board)
        CheckValue.check(self.Config, int, 'PushType',
                         PushType, Class=DataType.PushType)
        CheckValue.check(self.Config, str, 'PushContent', PushContent)
        if PostAID is not None:
            CheckValue.check(self.Config, str, 'PostAID', PostAID)
        CheckValue.check(self.Config, int, 'PostIndex', PostIndex)

        if len(Board) == 0:
            raise ValueError(Log.merge([
                i18n.Board,
                i18n.ErrorParameter,
                Board
            ]))

        if PostIndex != 0 and isinstance(PostAID, str):
            raise ValueError(Log.merge([
                'PostIndex',
                'PostAID',
                i18n.ErrorParameter,
                i18n.BothInput
            ]))

        if PostIndex == 0 and PostAID is None:
            raise ValueError(Log.merge([
                'PostIndex',
                'PostAID',
                i18n.ErrorParameter,
                i18n.NoInput
            ]))

        if PostIndex != 0:
            NewestIndex = self._getNewestIndex(
                DataType.IndexType.BBS,
                Board=Board
            )
            CheckValue.checkIndex(self.Config, 'PostIndex',
                                  PostIndex, NewestIndex)

        self._checkBoard(Board)

        MaxPushLength = 33
        PushList = []

        TempStartIndex = 0
        TempEndIndex = TempStartIndex + 1

        while TempEndIndex <= len(PushContent):

            Temp = ''
            LastTemp = None
            while len(Temp.encode('big5-uao', 'replace')) < MaxPushLength:
                Temp = PushContent[TempStartIndex:TempEndIndex]

                if not len(Temp.encode('big5-uao', 'replace')) < MaxPushLength:
                    break
                elif PushContent.endswith(Temp):
                    break
                elif Temp.endswith('\n'):
                    break
                elif LastTemp == Temp:
                    break

                TempEndIndex += 1
                LastTemp = Temp

            PushList.append(Temp.strip())

            TempStartIndex = TempEndIndex
            TempEndIndex = TempStartIndex + 1
        PushList = filter(None, PushList)

        for push in PushList:
            Log.showValue(
                self.Config,
                Log.Level.INFO,
                i18n.Push,
                push
            )

            for _ in range(2):
                try:
                    self._push(
                        Board,
                        PushType,
                        push,
                        PostAID=PostAID,
                        PostIndex=PostIndex
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
            Board: str,
            PushType: int,
            PushContent: str,
            PostAID: str = None,
            PostIndex: int = 0):

        try:
            from . import api_push
        except ModuleNotFoundError:
            import api_push

        return api_push.push(
            self,
            Board,
            PushType,
            PushContent,
            PostAID,
            PostIndex)

    def _getUser(self, UserID):

        CheckValue.check(self.Config, str, 'UserID', UserID)
        if len(UserID) < 3:
            raise ValueError(Log.merge([
                'UserID',
                i18n.ErrorParameter,
                UserID
            ]))

        try:
            from . import api_getUser
        except ModuleNotFoundError:
            import api_getUser

        return api_getUser.getUser(self, UserID)

    def getUser(self, UserID):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if self._UnregisteredUser:
            raise Exceptions.UnregisteredUser(Util.getCurrentFuncName())

        return self._getUser(UserID)

    def throwWaterBall(self, TargetID, Content):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if self._UnregisteredUser:
            raise Exceptions.UnregisteredUser(Util.getCurrentFuncName())

        CheckValue.check(self.Config, str, 'TargetID', TargetID)
        CheckValue.check(self.Config, str, 'Content', Content)

        if len(TargetID) <= 2:
            raise ValueError(Log.merge([
                'TargetID',
                i18n.ErrorParameter,
                TargetID
            ]))

        User = self._getUser(TargetID)
        if '不在站上' in User.getState():
            raise Exceptions.UserOffline(TargetID)

        try:
            from . import api_WaterBall
        except ModuleNotFoundError:
            import api_WaterBall

        return api_WaterBall.throwWaterBall(self, TargetID, Content)

    def getWaterBall(self, OperateType):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if self._UnregisteredUser:
            raise Exceptions.UnregisteredUser(Util.getCurrentFuncName())

        CheckValue.check(
            self.Config, int, 'OperateType', OperateType,
            Class=DataType.WaterBallOperateType)

        try:
            from . import api_WaterBall
        except ModuleNotFoundError:
            import api_WaterBall

        return api_WaterBall.getWaterBall(self, OperateType)

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
            inputCallStatus):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, int, 'CallStatus', inputCallStatus,
                         Class=DataType.CallStatus)

        try:
            from . import api_CallStatus
        except ModuleNotFoundError:
            import api_CallStatus

        return api_CallStatus.setCallStatus(self, inputCallStatus)

    def giveMoney(self, ID, Money):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if self._UnregisteredUser:
            raise Exceptions.UnregisteredUser(Util.getCurrentFuncName())

        CheckValue.check(self.Config, str, 'ID', ID)
        CheckValue.check(self.Config, int, 'Money', Money)
        # Check user
        self.getUser(ID)

        try:
            from . import api_giveMoney
        except ModuleNotFoundError:
            import api_giveMoney

        return api_giveMoney.giveMoney(self, ID, Money)

    def mail(
            self,
            ID: str,
            Title: str,
            Content: str,
            SignFile):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'ID', ID)
        CheckValue.check(self.Config, str, 'Title', Title)
        CheckValue.check(self.Config, str, 'Content', Content)

        CheckSignFile = False
        for i in range(0, 10):
            if str(i) == SignFile or i == SignFile:
                CheckSignFile = True
                break

        if not CheckSignFile:
            SignFile = SignFile.lower()
            if SignFile != 'x':
                raise ValueError(Log.merge([
                    'SignFile',
                    i18n.ErrorParameter,
                    SignFile
                ]))

        try:
            from . import api_mail
        except ModuleNotFoundError:
            import api_mail

        return api_mail.mail(
            self,
            ID,
            Title,
            Content,
            SignFile)

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
            inputReplyType: int,
            Board: str,
            Content: str,
            SignFile=0,
            PostAID: str = None,
            PostIndex: int = 0):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, int, 'ReplyType', inputReplyType,
                         Class=DataType.ReplyType)
        CheckValue.check(self.Config, str, 'Board', Board)
        CheckValue.check(self.Config, str, 'Content', Content)
        if PostAID is not None:
            CheckValue.check(self.Config, str, 'PostAID', PostAID)

        if PostIndex != 0:
            NewestIndex = self._getNewestIndex(
                DataType.IndexType.BBS,
                Board=Board)
            CheckValue.checkIndex(
                self.Config, 'PostIndex',
                PostIndex, MaxValue=NewestIndex)

        SignFileList = [str(x) for x in range(0, 10)]
        SignFileList.append('x')

        if str(SignFile) not in SignFileList:
            raise ValueError(Log.merge([
                'SignFile',
                i18n.ErrorParameter
            ]))

        if PostAID is not None and PostIndex != 0:
            raise ValueError(Log.merge([
                'PostIndex',
                'PostAID',
                i18n.ErrorParameter,
                i18n.BothInput
            ]))

        self._checkBoard(Board)

        try:
            from . import api_replyPost
        except ModuleNotFoundError:
            import api_replyPost

        api_replyPost.replyPost(
            self,
            inputReplyType,
            Board,
            Content,
            SignFile,
            PostAID,
            PostIndex)

    def setBoardTitle(
            self,
            Board: str,
            NewTitle: str):
        # 第一支板主專用 API
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'Board', Board)
        CheckValue.check(self.Config, str, 'NewTitle', NewTitle)

        self._checkBoard(
            Board,
            CheckModerator=True
        )

        try:
            from . import api_setBoardTitle
        except ModuleNotFoundError:
            import api_setBoardTitle

        api_setBoardTitle.setBoardTitle(self, Board, NewTitle)

    def markPost(
        self,
        inputMarkType: int,
        Board: str,
        PostAID: str = None,
        PostIndex: int = 0,
        SearchType: int = 0,
        SearchCondition: str = None,
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
            inputMarkType,
            Board,
            PostAID,
            PostIndex,
            SearchType,
            SearchCondition
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

    def bucket(self, Board, BucketDays, Reason, TargetID):

        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'Board', Board)
        CheckValue.check(self.Config, int, 'BucketDays', BucketDays)
        CheckValue.check(self.Config, str, 'Reason', Reason)
        CheckValue.check(self.Config, str, 'TargetID', TargetID)

        self._getUser(TargetID)

        self._checkBoard(
            Board,
            CheckModerator=True
        )

        try:
            from . import api_bucket
        except ModuleNotFoundError:
            import api_bucket

        resultlist = api_bucket.bucket(
            self, Board, BucketDays, Reason, TargetID)

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

    def getBoardInfo(
            self,
            Board,
            setting=True):

        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(self.Config, str, 'Board', Board)
        CheckValue.check(self.Config, bool, 'setting', setting)
        self._checkBoard(Board)

        try:
            from . import api_getBoardInfo
        except ModuleNotFoundError:
            import api_getBoardInfo

        return api_getBoardInfo.getBoardInfo(self, Board, setting)


if __name__ == '__main__':

    print('PTT Library v ' + Version)
    print('Developed by PTT CodingMan')
