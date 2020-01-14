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
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Version = Config.Version

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

        # Config.load()

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
            Config.ScreenTimeOut = ScreenTimeOut
        if ScreenLongTimeOut != 0:
            Config.ScreenLongTimeOut = ScreenLongTimeOut

        if LogLevel == 0:
            LogLevel = Config.LogLevel
        elif not Util.checkRange(Log.Level, LogLevel):
            raise ValueError('[PTT Library] Unknow LogLevel', LogLevel)
        else:
            Config.LogLevel = LogLevel

        if Language == 0:
            Language = Config.Language
        elif not Util.checkRange(i18n.Language, Language):
            raise ValueError('[PTT Library] Unknow language', Language)
        else:
            Config.Language = Language
        i18n.load(Language)

        if LogHandler is not None:
            Log.Handler = LogHandler
            Log.showValue(
                Log.Level.INFO,
                i18n.LogHandler,
                i18n.Init
            )
        elif hasLogHandler and not setLogHandlerResult:
            Log.showValue(
                Log.Level.INFO,
                i18n.LogHandler,
                [
                    i18n.Init,
                    i18n.Fail
                ]
            )

        if Language == i18n.Language.Chinese:
            Log.showValue(Log.Level.INFO, [
                i18n.ChineseTranditional,
                i18n.LanguageModule
            ],
                i18n.Init
            )
        elif Language == i18n.Language.English:
            Log.showValue(Log.Level.INFO, [
                i18n.English,
                i18n.LanguageModule
            ],
                i18n.Init
            )

        if ConnectMode == 0:
            ConnectMode = Config.ConnectMode
        elif not Util.checkRange(ConnectCore.ConnectMode, ConnectMode):
            raise ValueError('[PTT Library] Unknow ConnectMode', ConnectMode)
        else:
            Config.ConnectMode = ConnectMode

        if Host == 0:
            Host = Config.Host
        elif not Util.checkRange(DataType.Host, Host):
            raise ValueError('[PTT Library] Unknow Host', Host)
        Config.Host = Host

        if Host == DataType.Host.PTT1:
            Log.showValue(
                Log.Level.INFO,
                [
                    i18n.Connect,
                    i18n.Host
                ],
                i18n.PTT
            )
        if Host == DataType.Host.PTT2:
            Log.showValue(
                Log.Level.INFO,
                [
                    i18n.Connect,
                    i18n.Host
                ],
                i18n.PTT2
            )

        self._ConnectCore = ConnectCore.API(Host)
        self._ExistBoardList = []
        self._ModeratorList = dict()
        self._LastThroWaterBallTime = 0
        self._ThreadID = threading.get_ident()

        Log.showValue(
            Log.Level.DEBUG,
            'ThreadID',
            self._ThreadID
        )

        Log.showValue(
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
            Log.Level.DEBUG,
            'ThreadID',
            self._ThreadID
        )
        Log.showValue(
            Log.Level.DEBUG,
            'Current thread id',
            CurrentThreadID
        )
        raise Exceptions.MultiThreadOperated()

    def getVersion(self) -> str:
        self._OneThread()
        return Config.Version

    def _login(
        self,
        ID: str,
        Password: str,
        KickOtherLogin: bool = False
    ):

        if self._LoginStatus:
            self.logout()

        CheckValue.check(str, 'ID', ID)
        CheckValue.check(str, 'Password', Password)
        CheckValue.check(bool, 'KickOtherLogin', KickOtherLogin)

        Config.KickOtherLogin = KickOtherLogin

        def KickOtherLoginDisplayMsg():
            if Config.KickOtherLogin:
                return i18n.KickOtherLogin
            return i18n.NotKickOtherLogin

        def KickOtherLoginResponse(Screen):
            if Config.KickOtherLogin:
                return 'y' + Command.Enter
            return 'n' + Command.Enter

        if len(Password) > 8:
            Password = Password[:8]

        ID = ID.strip()
        Password = Password.strip()

        self._ID = ID
        self._Password = Password

        Log.showValue(
            Log.Level.INFO,
            [
                i18n.Login,
                i18n.ID
            ],
            ID
        )

        Config.KickOtherLogin = KickOtherLogin

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
            ScreenTimeout=Config.ScreenLongTimeOut,
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
                Log.Level.DEBUG,
                i18n.NewCursor
            )
        else:
            self._Cursor = DataType.Cursor.Old
            Log.log(
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
            Log.Level.INFO,
            i18n.Logout,
            i18n.Done
        )

    def log(self, Msg):
        self._OneThread()
        Log.log(Log.Level.INFO, Msg)

    def getTime(self) -> str:
        self._OneThread()
        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('A')
        CmdList.append(Command.Right)
        CmdList.append(Command.Left)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                [
                    i18n.GetPTTTime,
                    i18n.Success,
                ],
                Screens.Target.MainMenu,
                BreakDetect=True
            ),
        ]

        index = self._ConnectCore.send(Cmd, TargetList)
        if index != 0:
            return None

        OriScreen = self._ConnectCore.getScreenQueue()[-1]
        LineList = OriScreen.split('\n')
        pattern = re.compile('[\d]+:[\d][\d]')

        LineList = LineList[-3:]

        # 0:00

        for line in LineList:
            if '星期' in line and '線上' in line and '我是' in line:
                Result = pattern.search(line)
                if Result is not None:
                    return Result.group(0)
        return None

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

        CheckValue.check(str, 'Board', Board)
        if PostAID is not None:
            CheckValue.check(str, 'PostAID', PostAID)
        CheckValue.check(int, 'PostIndex', PostIndex)
        CheckValue.check(int, 'SearchType', SearchType,
                         Class=DataType.PostSearchType)
        if SearchCondition is not None:
            CheckValue.check(str, 'SearchCondition', SearchCondition)

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
                raise Exceptions.NoSuchBoard(Board)

            OriScreen = self._ConnectCore.getScreenQueue()[-1]

            # print(OriScreen)
            # if index == 1:
            #     raise Exceptions.NoSuchBoard(Board)

            BoardNameLine = [line.strip() for line in OriScreen.split(
                '\n') if line.strip().startswith('《')]
            if len(BoardNameLine) != 1:
                raise Exceptions.UnknowError(OriScreen)
            BoardNameLine = BoardNameLine[0]
            if '《' not in BoardNameLine or '》' not in BoardNameLine:
                raise Exceptions.UnknowError(BoardNameLine)

            BoardName = BoardNameLine[1:BoardNameLine.find('》')].lower()

            Log.showValue(
                Log.Level.DEBUG,
                'Find Board Name',
                BoardName
            )

            self._ExistBoardList.append(BoardName)

            if BoardName != Board.lower():
                raise Exceptions.NoSuchBoard(Board)

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
        Query: bool = False,
    ):

        self._checkBoard(Board)

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('qs')
        CmdList.append(Board)
        CmdList.append(Command.Enter)
        CmdList.append(Command.Ctrl_C * 2)
        CmdList.append(Command.Space)

        if PostAID is not None:
            CmdList.append('#' + PostAID)

        elif PostIndex != 0:
            if SearchCondition is not None:
                if SearchType == DataType.PostSearchType.Keyword:
                    CmdList.append('/')
                elif SearchType == DataType.PostSearchType.Author:
                    CmdList.append('a')
                elif SearchType == DataType.PostSearchType.Push:
                    CmdList.append('Z')
                elif SearchType == DataType.PostSearchType.Mark:
                    CmdList.append('G')
                elif SearchType == DataType.PostSearchType.Money:
                    CmdList.append('A')

                CmdList.append(SearchCondition)
                CmdList.append(Command.Enter)

            CmdList.append(str(PostIndex))

        CmdList.append(Command.Enter)
        CmdList.append(Command.QueryPost)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                [
                    i18n.CatchPost,
                    i18n.Success,
                ],
                Screens.Target.QueryPost,
                BreakDetect=True,
                Refresh=False,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.PostDeleted,
                    i18n.Success,
                ],
                Screens.Target.InBoard,
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                i18n.NoSuchBoard,
                Screens.Target.MainMenu_Exiting,
                Exceptions=Exceptions.NoSuchBoard(Board)
            ),
        ]

        index = self._ConnectCore.send(Cmd, TargetList)
        OriScreen = self._ConnectCore.getScreenQueue()[-1]

        PostAuthor = None
        PostTitle = None
        if index < 0 or index == 1:
            # 文章被刪除
            Log.log(Log.Level.DEBUG, i18n.PostDeleted)
            PostDelStatus = 0

            Log.showValue(
                Log.Level.DEBUG,
                'OriScreen',
                OriScreen
            )

            CursorLine = [line for line in OriScreen.split(
                '\n') if line.startswith(self._Cursor)]

            if len(CursorLine) != 1:
                raise Exceptions.UnknowError(OriScreen)

            CursorLine = CursorLine[0]
            Log.showValue(
                Log.Level.DEBUG,
                'CursorLine',
                CursorLine
            )

            pattern = re.compile('[\d]+\/[\d]+')
            PatternResult = pattern.search(CursorLine)
            if PatternResult is None:
                ListDate = None
            else:
                ListDate = PatternResult.group(0)
                ListDate = ListDate[-5:]

            pattern = re.compile('\[[\w]+\]')
            PatternResult = pattern.search(CursorLine)
            if PatternResult is not None:
                PostDelStatus = DataType.PostDeleteStatus.ByAuthor
            else:
                pattern = re.compile('<[\w]+>')
                PatternResult = pattern.search(CursorLine)
                PostDelStatus = DataType.PostDeleteStatus.ByModerator

            # > 79843     9/11 -             □ (本文已被吃掉)<
            # > 76060     8/28 -             □ (本文已被刪除) [weida7332]
            # print(f'O=>{CursorLine}<')
            if PatternResult is not None:
                PostAuthor = PatternResult.group(0)[1:-1]
            else:
                PostAuthor = None
                PostDelStatus = DataType.PostDeleteStatus.ByUnknow

            Log.showValue(Log.Level.DEBUG, 'ListDate', ListDate)
            Log.showValue(Log.Level.DEBUG, 'PostAuthor', PostAuthor)
            Log.showValue(Log.Level.DEBUG, 'PostDelStatus', PostDelStatus)

            return DataType.PostInfo(
                Board=Board,
                Author=PostAuthor,
                ListDate=ListDate,
                DeleteStatus=PostDelStatus,
                FormatCheck=True
            )

        elif index == 0:

            LockPost = False
            CursorLine = [line for line in OriScreen.split(
                '\n') if line.startswith(self._Cursor)][0]
            PostAuthor = CursorLine
            if '□' in PostAuthor:
                PostAuthor = PostAuthor[:PostAuthor.find('□')].strip()
            elif 'R:' in PostAuthor:
                PostAuthor = PostAuthor[:PostAuthor.find('R:')].strip()
            elif ' 轉 ' in PostAuthor:
                PostAuthor = PostAuthor[:PostAuthor.find('轉')].strip()
            elif ' 鎖 ' in PostAuthor:
                PostAuthor = PostAuthor[:PostAuthor.find('鎖')].strip()
                LockPost = True
            PostAuthor = PostAuthor[PostAuthor.rfind(' '):].strip()

            PostTitle = CursorLine
            if ' □ ' in PostTitle:
                PostTitle = PostTitle[PostTitle.find('□') + 1:].strip()
            elif ' R:' in PostTitle:
                PostTitle = PostTitle[PostTitle.find('R:'):].strip()
            elif ' 轉 ' in PostTitle:
                # print(f'[{PostTitle}]=========>')
                PostTitle = PostTitle[PostTitle.find('轉') + 1:].strip()
                PostTitle = f'Fw: {PostTitle}'
                # print(f'=========>[{PostTitle}]')
            elif ' 鎖 ' in PostTitle:
                PostTitle = PostTitle[PostTitle.find('鎖') + 1:].strip()

            OriScreenTemp = OriScreen[OriScreen.find('┌──────────'):]
            OriScreenTemp = OriScreenTemp[:OriScreenTemp.find(
                '└─────────────')
            ]

            AIDLine = [line for line in OriScreen.split(
                '\n') if line.startswith('│ 文章代碼(AID)')]

            if len(AIDLine) == 1:
                AIDLine = AIDLine[0]
                pattern = re.compile('#[\w|-]+')
                PatternResult = pattern.search(AIDLine)
                PostAID = PatternResult.group(0)[1:]

            pattern = re.compile('文章網址: https:[\S]+html')
            PatternResult = pattern.search(OriScreenTemp)
            if PatternResult is None:
                PostWeb = None
            else:
                PostWeb = PatternResult.group(0)[6:]

            pattern = re.compile('這一篇文章值 [\d]+ Ptt幣')
            PatternResult = pattern.search(OriScreenTemp)
            if PatternResult is None:
                # 特殊文章無價格
                PostMoney = -1
            else:
                PostMoney = PatternResult.group(0)[7:]
                PostMoney = PostMoney[:PostMoney.find(' ')]
                PostMoney = int(PostMoney)

            pattern = re.compile('[\d]+\/[\d]+')
            PatternResult = pattern.search(CursorLine)
            if PatternResult is None:
                ListDate = None
            else:
                ListDate = PatternResult.group(0)
                ListDate = ListDate[-5:]

            # >  7485   9 8/09 CodingMan    □ [閒聊] PTT Library 更新
            # > 79189 M 1 9/17 LittleCalf   □ [公告] 禁言退文公告
            # >781508 +爆 9/17 jodojeda     □ [新聞] 國人吃魚少 學者：應把吃魚當成輕鬆愉快
            # >781406 +X1 9/17 kingofage111 R: [申請] ReDmango 請辭Gossiping板主職務

            PushNumber = CursorLine
            # print(PushNumber)
            PushNumber = PushNumber[:PushNumber.find(ListDate)]
            # print(PushNumber)
            PushNumber = PushNumber[7:]
            # print(PushNumber)
            PushNumber = PushNumber.split(' ')
            # print(PushNumber)
            PushNumber = list(filter(None, PushNumber))
            # print(PushNumber)

            if len(PushNumber) == 0:
                PushNumber = None
            else:
                PushNumber = PushNumber[-1]
                # print(PushNumber)

                if PushNumber.startswith('+') or PushNumber.startswith('~'):
                    PushNumber = PushNumber[1:]
                    # print(PushNumber)
                if PushNumber.lower().startswith('m'):
                    PushNumber = PushNumber[1:]
                    # print(PushNumber)
                if PushNumber.lower().startswith('!'):
                    PushNumber = PushNumber[1:]

                if PushNumber.lower().startswith('s'):
                    PushNumber = PushNumber[1:]

                if PushNumber.lower().startswith('='):
                    PushNumber = PushNumber[1:]

                if len(PushNumber) == 0:
                    PushNumber = None

            # print(PushNumber)
            Log.showValue(Log.Level.DEBUG, 'PostAuthor', PostAuthor)
            Log.showValue(Log.Level.DEBUG, 'PostTitle', PostTitle)
            Log.showValue(Log.Level.DEBUG, 'PostAID', PostAID)
            Log.showValue(Log.Level.DEBUG, 'PostWeb', PostWeb)
            Log.showValue(Log.Level.DEBUG, 'PostMoney', PostMoney)
            Log.showValue(Log.Level.DEBUG, 'ListDate', ListDate)
            Log.showValue(Log.Level.DEBUG, 'PushNumber', PushNumber)

            if LockPost:
                Post = DataType.PostInfo(
                    Board=Board,
                    AID=PostAID,
                    Author=PostAuthor,
                    Title=PostTitle,
                    WebUrl=PostWeb,
                    Money=PostMoney,
                    ListDate=ListDate,
                    FormatCheck=True,
                    PushNumber=PushNumber,
                    Lock=True,
                )
                return Post

        if Query:
            Post = DataType.PostInfo(
                Board=Board,
                AID=PostAID,
                Author=PostAuthor,
                Title=PostTitle,
                WebUrl=PostWeb,
                Money=PostMoney,
                ListDate=ListDate,
                FormatCheck=True,
                PushNumber=PushNumber,
            )
            return Post

        self.Unconfirmed = False

        def isUnconfirmedHandler():
            self.Unconfirmed = True

        Cmd = Command.Enter * 2
        TargetList = [
            # 待證實文章
            ConnectCore.TargetUnit(
                i18n.UnconfirmedPost,
                '本篇文章內容經站方授權之板務管理人員判斷有尚待證實之處',
                Response=' ',
                Handler=isUnconfirmedHandler
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.BrowsePost,
                    i18n.Done,
                ],
                Screens.Target.PostEnd,
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.BrowsePost,
                ],
                Screens.Target.InPost,
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.PostNoContent,
                ],
                Screens.Target.PostNoContent,
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            # 動畫文章
            ConnectCore.TargetUnit(
                [
                    i18n.AnimationPost,
                ],
                Screens.Target.Animation,
                Response=Command.GoMainMenu_TypeQ,
                BreakDetectAfterSend=True
            ),
        ]

        LineFromTopattern = re.compile('[\d]+~[\d]+')

        ContentStart = '───────────────────────────────────────'
        ContentEnd = []
        ContentEnd.append('--\n※ 發信站: 批踢踢實業坊(ptt.cc)')
        ContentEnd.append('--\n※ 發信站: 批踢踢兔(ptt2.cc)')
        ContentEnd.append('--\n※ 發信站: 新批踢踢(ptt2.twbbs.org.tw)')

        # '※ 發信站: 批踢踢實業坊(ptt.cc)'

        HasControlCode = False
        ControlCodeMode = False
        PushStart = False
        ContentStartExist = False
        ContentStartJump = False
        ContentStartJumpSet = False

        FirstPage = True
        OriginPost = []
        while True:
            index = self._ConnectCore.send(Cmd, TargetList)

            if index == 3 or index == 4:
                Post = DataType.PostInfo(
                    Board=Board,
                    AID=PostAID,
                    Author=PostAuthor,
                    # Date=PostDate,
                    Title=PostTitle,
                    WebUrl=PostWeb,
                    Money=PostMoney,
                    # Content=PostContent,
                    # PushList=PushList,
                    ListDate=ListDate,
                    ControlCode=HasControlCode,
                    FormatCheck=False,
                    PushNumber=PushNumber,
                    Unconfirmed=self.Unconfirmed,
                )
                return Post

            LastScreen = self._ConnectCore.getScreenQueue()[-1]
            Lines = LastScreen.split('\n')
            LastLine = Lines[-1]
            Lines.pop()
            LastScreen = '\n'.join(Lines)

            if ContentStart in LastScreen and not ContentStartExist:
                ContentStartExist = True

            if ContentStartExist:
                if not ContentStartJumpSet:
                    if ContentStart not in LastScreen:
                        ContentStartJump = True
                        ContentStartJumpSet = True
                else:
                    ContentStartJump = False

            PatternResult = LineFromTopattern.search(LastLine)
            if PatternResult is None:
                ControlCodeMode = True
                HasControlCode = True
            else:
                LastReadLineList = PatternResult.group(0).split('~')
                LastReadLineATemp = int(LastReadLineList[0])
                LastReadLineBTemp = int(LastReadLineList[1])
                if ControlCodeMode:
                    LastReadLineA = LastReadLineATemp - 1
                    LastReadLineB = LastReadLineBTemp - 1
                ControlCodeMode = False

            if FirstPage:
                FirstPage = False
                OriginPost.append(LastScreen)
            else:
                # print(f'LastReadLineATemp [{LastReadLineATemp}]')
                # print(f'LastReadLineBTemp [{LastReadLineBTemp}]')
                # print(f'ContentStartJump {ContentStartJump}')
                if not ControlCodeMode:
                    GetLineB = LastReadLineBTemp - LastReadLineB
                    if GetLineB > 0:
                        # print('Type 1')
                        # print(f'GetLineB [{GetLineB}]')
                        NewContentPart = '\n'.join(Lines[-GetLineB:])
                    else:
                        GetLineA = LastReadLineATemp - LastReadLineA
                        # print('Type 2')
                        # print(f'GetLineA [{GetLineA}]')
                        if GetLineA > 0:
                            NewContentPart = '\n'.join(Lines[-GetLineA:])
                        else:
                            NewContentPart = '\n'.join(Lines)
                else:
                    NewContentPart = Lines[-1]

                OriginPost.append(NewContentPart)
                Log.showValue(
                    Log.Level.DEBUG,
                    'NewContentPart',
                    NewContentPart
                )

            if index == 1:
                if ContentStartJump and len(NewContentPart) == 0:
                    # print(f'!!!GetLineB {GetLineB}')
                    GetLineB += 1
                    NewContentPart = '\n'.join(Lines[-GetLineB:])
                    # print(f'!!!NewContentPart {NewContentPart}')
                    OriginPost.pop()
                    OriginPost.append(NewContentPart)
                break

            if not ControlCodeMode:
                LastReadLineA = LastReadLineATemp
                LastReadLineB = LastReadLineBTemp

            for EC in ContentEnd:
                if EC in LastScreen:
                    PushStart = True
                    break

            if not PushStart:
                Cmd = Command.Down
            else:
                Cmd = Command.Right

        # print(self.Unconfirmed)
        OriginPost = '\n'.join(OriginPost)
        # OriginPost = [line.strip() for line in OriginPost.split('\n')]
        # OriginPost = '\n'.join(OriginPost)

        Log.showValue(
            Log.Level.DEBUG,
            'OriginPost',
            OriginPost
        )

        # print('=' * 20)
        # print()
        # print('=' * 20)

        PostAuthorPattern_New = re.compile('作者  (.+) 看板')
        PostAuthorPattern_Old = re.compile('作者  (.+)')
        BoardPattern = re.compile('看板  (.+)')

        PostDate = None
        PostContent = []
        IP = None
        Location = None
        PushList = []

        # 格式確認，亂改的我也沒辦法Q_Q
        OriginPostLines = OriginPost.split('\n')

        AuthorLine = OriginPostLines[0]

        if Board.lower() == 'allpost':
            BoardLine = AuthorLine[AuthorLine.find(')') + 1:]
            PatternResult = BoardPattern.search(BoardLine)
            if PatternResult is not None:
                BoardTemp = PostAuthor = PatternResult.group(0)
                BoardTemp = BoardTemp[2:].strip()
                if len(BoardTemp) > 0:
                    Board = BoardTemp
                    Log.showValue(
                        Log.Level.DEBUG,
                        i18n.Board,
                        Board
                    )
        PatternResult = PostAuthorPattern_New.search(AuthorLine)
        if PatternResult is not None:
            PostAuthor = PatternResult.group(0)
            PostAuthor = PostAuthor[:PostAuthor.rfind(')') + 1]
        else:
            PatternResult = PostAuthorPattern_Old.search(AuthorLine)
            if PatternResult is None:
                Log.showValue(
                    Log.Level.DEBUG,
                    i18n.SubstandardPost,
                    i18n.Author
                )
                Post = DataType.PostInfo(
                    Board=Board,
                    AID=PostAID,
                    Author=PostAuthor,
                    Date=PostDate,
                    Title=PostTitle,
                    WebUrl=PostWeb,
                    Money=PostMoney,
                    Content=PostContent,
                    IP=IP,
                    PushList=PushList,
                    ListDate=ListDate,
                    ControlCode=HasControlCode,
                    FormatCheck=False,
                    Location=Location,
                    PushNumber=PushNumber,
                    OriginPost=OriginPost,
                    Unconfirmed=self.Unconfirmed,
                )
                return Post
            PostAuthor = PatternResult.group(0)
            PostAuthor = PostAuthor[:PostAuthor.rfind(')') + 1]
        PostAuthor = PostAuthor[4:].strip()

        Log.showValue(
            Log.Level.DEBUG,
            i18n.Author,
            PostAuthor
        )

        PostTitlePattern = re.compile('標題  (.+)')

        TitleLine = OriginPostLines[1]
        PatternResult = PostTitlePattern.search(TitleLine)
        if PatternResult is None:
            Log.showValue(
                Log.Level.DEBUG,
                i18n.SubstandardPost,
                i18n.Title
            )
            Post = DataType.PostInfo(
                Board=Board,
                AID=PostAID,
                Author=PostAuthor,
                Date=PostDate,
                Title=PostTitle,
                WebUrl=PostWeb,
                Money=PostMoney,
                Content=PostContent,
                IP=IP,
                PushList=PushList,
                ListDate=ListDate,
                ControlCode=HasControlCode,
                FormatCheck=False,
                Location=Location,
                PushNumber=PushNumber,
                OriginPost=OriginPost,
                Unconfirmed=self.Unconfirmed,
            )
            return Post
        PostTitle = PatternResult.group(0)
        PostTitle = PostTitle[4:].strip()

        Log.showValue(
            Log.Level.DEBUG,
            i18n.Title,
            PostTitle
        )

        PostDatePattern = re.compile('時間  (.+)')
        DateLine = OriginPostLines[2]
        PatternResult = PostDatePattern.search(DateLine)
        if PatternResult is None:
            Log.showValue(
                Log.Level.DEBUG,
                i18n.SubstandardPost,
                i18n.Date
            )
            Post = DataType.PostInfo(
                Board=Board,
                AID=PostAID,
                Author=PostAuthor,
                Date=PostDate,
                Title=PostTitle,
                WebUrl=PostWeb,
                Money=PostMoney,
                Content=PostContent,
                IP=IP,
                PushList=PushList,
                ListDate=ListDate,
                ControlCode=HasControlCode,
                FormatCheck=False,
                Location=Location,
                PushNumber=PushNumber,
                OriginPost=OriginPost,
                Unconfirmed=self.Unconfirmed,
            )
            return Post
        PostDate = PatternResult.group(0)
        PostDate = PostDate[4:].strip()

        Log.showValue(
            Log.Level.DEBUG,
            i18n.Date,
            PostDate
        )

        ContentFail = True
        if ContentStart not in OriginPost:
            # print('Type 1')
            ContentFail = True
        else:
            PostContent = OriginPost
            PostContent = PostContent[
                PostContent.find(ContentStart) +
                len(ContentStart):
            ]
            # print('Type 2')
            # print(f'PostContent [{PostContent}]')
            for EC in ContentEnd:
                # + 3 = 把 --\n 拿掉
                # print(f'EC [{EC}]')
                if EC in PostContent:
                    ContentFail = False

                    PostContent = PostContent[
                        :PostContent.rfind(EC) + 3
                    ]
                    OriginPostLines = OriginPost[OriginPost.find(EC):]
                    PostContent = PostContent.strip()
                    OriginPostLines = OriginPostLines.split('\n')
                    break

        if ContentFail:
            Log.showValue(
                Log.Level.DEBUG,
                i18n.SubstandardPost,
                i18n.Content
            )
            Post = DataType.PostInfo(
                Board=Board,
                AID=PostAID,
                Author=PostAuthor,
                Date=PostDate,
                Title=PostTitle,
                WebUrl=PostWeb,
                Money=PostMoney,
                Content=PostContent,
                IP=IP,
                PushList=PushList,
                ListDate=ListDate,
                ControlCode=HasControlCode,
                FormatCheck=False,
                Location=Location,
                PushNumber=PushNumber,
                OriginPost=OriginPost,
                Unconfirmed=self.Unconfirmed,
            )
            return Post

        Log.showValue(
            Log.Level.DEBUG,
            i18n.Content,
            PostContent
        )

        InfoLines = [
            line for line in OriginPostLines if line.startswith('※') or line.startswith('◆')
        ]

        pattern = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')
        pattern_p2 = re.compile('[\d]+-[\d]+-[\d]+-[\d]+')
        for line in reversed(InfoLines):
            Log.showValue(
                Log.Level.DEBUG,
                'IP Line',
                line
            )

            # type 1
            # ※ 編輯: CodingMan (111.243.146.98 臺灣)
            # ※ 發信站: 批踢踢實業坊(ptt.cc), 來自: 111.243.146.98 (臺灣)

            # type 2
            # ※ 發信站: 批踢踢實業坊(ptt.cc), 來自: 116.241.32.178
            # ※ 編輯: kill77845 (114.136.55.237), 12/08/2018 16:47:59

            # type 3
            # ※ 發信站: 批踢踢實業坊(ptt.cc)
            # ◆ From: 211.20.78.69
            # ※ 編輯: JCC             來自: 211.20.78.69         (06/20 10:22)
            # ※ 編輯: JCC (118.163.28.150), 12/03/2015 14:25:35

            PatternResult = pattern.search(line)
            if PatternResult is not None:
                IP = PatternResult.group(0)
                LocationTemp = line[line.find(IP) + len(IP):].strip()
                LocationTemp = LocationTemp.replace('(', '')
                LocationTemp = LocationTemp[:LocationTemp.rfind(')')]
                LocationTemp = LocationTemp.strip()
                # print(f'=>[{LocationTemp}]')
                if ' ' not in LocationTemp and len(LocationTemp) > 0:
                    Location = LocationTemp
                    Log.showValue(Log.Level.DEBUG, 'Location', Location)
                break

            PatternResult = pattern_p2.search(line)
            if PatternResult is not None:
                IP = PatternResult.group(0)
                IP = IP.replace('-', '.')
                # print(f'IP -> [{IP}]')
                break
        if Config.Host == DataType.Host.PTT1:
            if IP is None:
                Log.showValue(
                    Log.Level.DEBUG,
                    i18n.SubstandardPost,
                    'IP'
                )
                Post = DataType.PostInfo(
                    Board=Board,
                    AID=PostAID,
                    Author=PostAuthor,
                    Date=PostDate,
                    Title=PostTitle,
                    WebUrl=PostWeb,
                    Money=PostMoney,
                    Content=PostContent,
                    IP=IP,
                    PushList=PushList,
                    ListDate=ListDate,
                    ControlCode=HasControlCode,
                    FormatCheck=False,
                    Location=Location,
                    PushNumber=PushNumber,
                    OriginPost=OriginPost,
                    Unconfirmed=self.Unconfirmed,
                )
                return Post
        Log.showValue(Log.Level.DEBUG, 'IP', IP)

        PushAuthorPattern = re.compile('[推|噓|→] [\w| ]+:')
        PushDatePattern = re.compile('[\d]+/[\d]+ [\d]+:[\d]+')
        PushIPPattern = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')

        PushList = []

        for line in OriginPostLines:
            PushType = 0
            if line.startswith('推'):
                PushType = DataType.PushType.Push
            elif line.startswith('噓 '):
                PushType = DataType.PushType.Boo
            elif line.startswith('→ '):
                PushType = DataType.PushType.Arrow
            else:
                continue

            Result = PushAuthorPattern.search(line)
            if Result is None:
                # 不符合推文格式
                continue
            PushAuthor = Result.group(0)[2:-1].strip()
            Log.showValue(Log.Level.DEBUG, [
                i18n.Push,
                i18n.ID,
            ],
                PushAuthor
            )

            Result = PushDatePattern.search(line)
            if Result is None:
                continue
            PushDate = Result.group(0)
            Log.showValue(Log.Level.DEBUG, [
                i18n.Push,
                i18n.Date,
            ],
                PushDate
            )

            PushIP = None
            Result = PushIPPattern.search(line)
            if Result is not None:
                PushIP = Result.group(0)
                Log.showValue(Log.Level.DEBUG, [
                    i18n.Push,
                    'IP',
                ],
                    PushIP
                )

            PushContent = line[
                line.find(PushAuthor) + len(PushAuthor):
            ]
            # PushContent = PushContent.replace(PushDate, '')

            if Config.Host == DataType.Host.PTT1:
                PushContent = PushContent[
                    :PushContent.rfind(PushDate)
                ]
            else:
                # → CodingMan:What is Ptt?                                       推 10/04 13:25
                PushContent = PushContent[
                    :PushContent.rfind(PushDate) - 2
                ]
            if PushIP is not None:
                PushContent = PushContent.replace(PushIP, '')
            PushContent = PushContent[
                PushContent.find(':') + 1:
            ].strip()
            Log.showValue(Log.Level.DEBUG, [
                i18n.Push,
                i18n.Content,
            ],
                PushContent
            )

            CurrentPush = DataType.PushInfo(
                PushType,
                PushAuthor,
                PushContent,
                PushIP,
                PushDate
            )
            PushList.append(CurrentPush)

        Post = DataType.PostInfo(
            Board=Board,
            AID=PostAID,
            Author=PostAuthor,
            Date=PostDate,
            Title=PostTitle,
            WebUrl=PostWeb,
            Money=PostMoney,
            Content=PostContent,
            IP=IP,
            PushList=PushList,
            ListDate=ListDate,
            ControlCode=HasControlCode,
            FormatCheck=True,
            Location=Location,
            PushNumber=PushNumber,
            OriginPost=OriginPost,
            Unconfirmed=self.Unconfirmed,
        )
        return Post

    def _getNewestIndex(
        self,
        IndexType: int,
        Board: str = None,
        # BBS
        SearchType: int = 0,
        SearchCondition: str = None
    ):
        CheckValue.check(int, 'IndexType', IndexType, Class=DataType.IndexType)
        CheckValue.check(str, 'Board', Board)

        if IndexType == DataType.IndexType.BBS:

            self._checkBoard(Board)

            CheckValue.check(int, 'SearchType', SearchType,
                             Class=DataType.PostSearchType)
            if SearchCondition is not None:
                CheckValue.check(str, 'SearchCondition', SearchCondition)
            CheckValue.check(int, 'SearchType', SearchType)

            CmdList = []
            CmdList.append(Command.GoMainMenu)
            CmdList.append('qs')
            CmdList.append(Board)
            CmdList.append(Command.Enter)

            Cmd = ''.join(CmdList)

            TargetList = [
                ConnectCore.TargetUnit(
                    i18n.AnyKeyContinue,
                    '任意鍵',
                    Response=' ',
                ),
                ConnectCore.TargetUnit(
                    [
                        '動畫播放中',
                    ],
                    '互動式動畫播放中',
                    Response=Command.Ctrl_C,
                    LogLevel=Log.Level.DEBUG
                ),
                ConnectCore.TargetUnit(
                    [
                        i18n.Mark,
                        i18n.Success,
                    ],
                    Screens.Target.InBoard,
                    BreakDetect=True,
                    LogLevel=Log.Level.DEBUG
                ),
            ]

            if SearchCondition is not None:
                if SearchType == DataType.PostSearchType.Keyword:
                    CmdList.append('/')
                elif SearchType == DataType.PostSearchType.Author:
                    CmdList.append('a')
                elif SearchType == DataType.PostSearchType.Push:
                    CmdList.append('Z')
                elif SearchType == DataType.PostSearchType.Mark:
                    CmdList.append('G')
                elif SearchType == DataType.PostSearchType.Money:
                    CmdList.append('A')

                CmdList.append(SearchCondition)
                CmdList.append(Command.Enter)

            CmdList.append('1')
            CmdList.append(Command.Enter)
            CmdList.append('$')

            Cmd = ''.join(CmdList)

            TargetList = [
                ConnectCore.TargetUnit(
                    i18n.NoPost,
                    '沒有文章...',
                    BreakDetect=True,
                    LogLevel=Log.Level.DEBUG
                ),
                ConnectCore.TargetUnit(
                    i18n.Success,
                    Screens.Target.InBoard,
                    BreakDetect=True,
                    LogLevel=Log.Level.DEBUG
                ),
                ConnectCore.TargetUnit(
                    i18n.Success,
                    Screens.Target.InBoardWithCursor,
                    BreakDetect=True,
                    LogLevel=Log.Level.DEBUG
                ),
                ConnectCore.TargetUnit(
                    i18n.NoSuchBoard,
                    Screens.Target.MainMenu_Exiting,
                    Exceptions=Exceptions.NoSuchBoard(Board)
                ),
            ]
            index = self._ConnectCore.send(Cmd, TargetList)
            if index < 0:
                # OriScreen = self._ConnectCore.getScreenQueue()[-1]
                raise Exceptions.NoSuchBoard(Board)

            if index == 0:
                return 0

            LastScreen = self._ConnectCore.getScreenQueue()[-1]
            AllIndex = re.findall(r'\d+ ', LastScreen)

            if len(AllIndex) == 0:
                print(LastScreen)
                raise Exceptions.UnknowError(i18n.UnknowError)

            AllIndex = list(map(int, AllIndex))
            AllIndex.sort(reverse=True)

            MaxCheckRange = 6
            NewestIndex = 0
            for IndexTemp in AllIndex:
                Continue = True
                if IndexTemp > MaxCheckRange:
                    CheckRange = MaxCheckRange
                else:
                    CheckRange = IndexTemp
                for i in range(1, CheckRange):
                    if str(IndexTemp - i) not in LastScreen:
                        Continue = False
                        break
                if Continue:
                    Log.showValue(
                        Log.Level.DEBUG,
                        i18n.FindNewestIndex,
                        IndexTemp
                    )
                    NewestIndex = IndexTemp
                    break

            if NewestIndex == 0:
                Screens.show(self._ConnectCore.getScreenQueue())
                raise Exceptions.UnknowError(i18n.UnknowError)

        elif DataType.IndexType.Web:
            # web
            _NewestIndex = None
            NewestIndex = 0
            _url = 'https://www.ptt.cc/bbs/'
            url = _url + Board
            r = requests.get(url, cookies={'over18': '1'})

            if r.status_code != requests.codes.ok:
                raise Exceptions.NoSuchBoard(Board)
            soup = BeautifulSoup(r.text, 'html.parser')

            for index, data in enumerate(soup.select('div.btn-group.btn-group-paging a')):
                text = data.text
                herf = data.get('href')
                if '上頁' in text:
                    _NewestIndex = herf.split('index')[1].split('.')[0]
                    # print("_NewestIndex: " + _NewestIndex)
                    _NewestIndex = int(_NewestIndex)

            if _NewestIndex is None:
                raise Exceptions.UnknowError('')
            NewestIndex = (_NewestIndex) + 1
        return NewestIndex

    def getNewestIndex(
        self,
        IndexType: int,
        Board: str = None,
        SearchType: int = 0,
        SearchCondition: str = None
    ):
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
        AID,
    ):
        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('qs')
        CmdList.append(Board)
        CmdList.append(Command.Enter)
        CmdList.append(Command.Ctrl_C * 2)
        CmdList.append(Command.Space)

        CmdList.append('#')
        CmdList.append(AID)
        CmdList.append(Command.Enter)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.NoPost,
                '找不到這個文章代碼(AID)',
                Exceptions=Exceptions.NoSuchPost(Board, AID)
            ),
            # 此狀態下無法使用搜尋文章代碼(AID)功能
            ConnectCore.TargetUnit(
                i18n.CanNotUseSearchPostCodeF,
                '此狀態下無法使用搜尋文章代碼(AID)功能',
                Exceptions=Exceptions.CanNotUseSearchPostCode()
            ),
            ConnectCore.TargetUnit(
                i18n.NoPost,
                '沒有文章...',
                Exceptions=Exceptions.NoSuchPost(Board, AID)
            ),
            ConnectCore.TargetUnit(
                i18n.Success,
                Screens.Target.InBoard,
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                i18n.Success,
                Screens.Target.InBoardWithCursor,
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                i18n.NoSuchBoard,
                Screens.Target.MainMenu_Exiting,
                Exceptions=Exceptions.NoSuchBoard(Board)
            ),
        ]
        index = self._ConnectCore.send(
            Cmd,
            TargetList
        )
        OriScreen = self._ConnectCore.getScreenQueue()[-1]
        if index < 0:
            print(OriScreen)
            raise Exceptions.NoSuchBoard(Board)

        # print(index)
        # print(OriScreen)
        ScreenList = OriScreen.split('\n')

        line = [x for x in ScreenList if x.startswith(self._Cursor)]
        line = line[0]
        LastLine = ScreenList[ScreenList.index(line) - 1]
        # print(LastLine)
        # print(line)

        if '編號' in LastLine and '人氣:' in LastLine:
            Index = line[1:].strip()
            IndexFix = False
        else:
            Index = LastLine.strip()
            IndexFix = True
        while '  ' in Index:
            Index = Index.replace('  ', ' ')
        IndexList = Index.split(' ')
        Index = IndexList[0]
        Index = int(Index)
        if IndexFix:
            Index += 1
        # print(Index)
        return Index

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
        EndPage: int = 0,
    ):

        self._OneThread()

        CheckValue.check(int, 'CrawlType', CrawlType, Class=DataType.CrawlType)
        CheckValue.check(str, 'Board', Board)

        if len(Board) == 0:
            raise ValueError(Log.merge([
                i18n.Board,
                i18n.ErrorParameter,
                Board
            ]))

        if CrawlType == DataType.CrawlType.BBS:
            if not self._LoginStatus:
                raise Exceptions.RequireLogin(i18n.RequireLogin)

            CheckValue.check(int, 'SearchType', SearchType)
            if SearchCondition is not None:
                CheckValue.check(str, 'SearchCondition', SearchCondition)
            if StartAID is not None:
                CheckValue.check(str, 'StartAID', StartAID)
            if EndAID is not None:
                CheckValue.check(str, 'EndAID', EndAID)

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
                Log.Level.DEBUG,
                'StartIndex',
                StartIndex
            )

            Log.showValue(
                Log.Level.DEBUG,
                'EndIndex',
                EndIndex
            )

            ErrorPostList = []
            DelPostList = []
            if Config.LogLevel == Log.Level.INFO:
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
                            Log.Level.INFO,
                            i18n.RestoreConnection
                        )
                        self._login(
                            self._ID,
                            self._Password,
                            Config.KickOtherLogin
                        )
                        NeedContinue = True
                    except Exceptions.UseTooManyResources as e:
                        if i == 1:
                            raise e
                        Log.log(
                            Log.Level.INFO,
                            i18n.RestoreConnection
                        )
                        self._login(
                            self._ID,
                            self._Password,
                            Config.KickOtherLogin
                        )
                        NeedContinue = True

                    if Post is None:
                        NeedContinue = True
                    elif not Post.isFormatCheck():
                        NeedContinue = True

                    if NeedContinue:
                        Log.log(
                            Log.Level.DEBUG,
                            'Wait for retry repost'
                        )
                        time.sleep(0.1)
                        continue

                    break

                if Config.LogLevel == Log.Level.INFO:
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
            if Config.LogLevel == Log.Level.INFO:
                PB.finish()

            return ErrorPostList, DelPostList

        else:
            if Config.Host == DataType.Host.PTT2:
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
            if Config.LogLevel == Log.Level.INFO:
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
                    Log.Level.DEBUG,
                    'CurrentPage',
                    index
                )

                url = _url + Board + '/index' + str(index) + '.html'
                r = requests.get(url, cookies={'over18': '1'})
                if r.status_code != requests.codes.ok:
                    raise Exceptions.NoSuchBoard(Board)
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

                if Config.LogLevel == Log.Level.INFO:
                    PB.update(index - StartPage)

            Log.showValue(
                Log.Level.DEBUG,
                'DelPostList',
                DelPostList
            )

            # 4. 把組合出來的 Post 塞給 handler

            # 5. 顯示 progress bar
            if Config.LogLevel == Log.Level.INFO:
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

        CheckValue.check(str, 'Board', Board)
        CheckValue.check(str, 'Title', Title)
        CheckValue.check(str, 'Content', Content)
        CheckValue.check(int, 'PostType', PostType)

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

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('qs')
        CmdList.append(Board)
        CmdList.append(Command.Enter)
        CmdList.append(Command.Ctrl_C * 2)
        CmdList.append(Command.Space)
        CmdList.append(Command.Ctrl_P)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.HasPostPermission,
                '發表文章於【',
                BreakDetect=True,
            ),
            ConnectCore.TargetUnit(
                i18n.NoPermission,
                '使用者不可發言',
                BreakDetect=True,
            )
        ]
        index = self._ConnectCore.send(Cmd, TargetList)
        if index < 0:
            Screens.show(self._ConnectCore.getScreenQueue())
            raise Exceptions.UnknowError(i18n.UnknowError)
        if index == 1:
            raise Exceptions.NoPermission(i18n.NoPermission)

        Screens.show(self._ConnectCore.getScreenQueue())

        CmdList = []
        CmdList.append(str(PostType))
        CmdList.append(Command.Enter)
        CmdList.append(str(Title))
        CmdList.append(Command.Enter)
        CmdList.append(Command.Ctrl_Y * 30)
        CmdList.append(str(Content))
        CmdList.append(Command.Ctrl_X)
        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.AnyKeyContinue,
                '任意鍵繼續',
                BreakDetect=True,
            ),
            ConnectCore.TargetUnit(
                i18n.SaveFile,
                '確定要儲存檔案嗎',
                Response='s' + Command.Enter,
            ),
            ConnectCore.TargetUnit(
                i18n.SelectSignature,
                'x=隨機',
                Response=str(SignFile) + Command.Enter,
            ),
        ]
        index = self._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=Config.ScreenPostTimeOut
        )

    def push(
        self,
        Board: str,
        PushType: int,
        PushContent: str,
        PostAID: str = None,
        PostIndex: int = 0
    ):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(str, 'Board', Board)
        CheckValue.check(int, 'PushType', PushType, Class=DataType.PushType)
        CheckValue.check(str, 'PushContent', PushContent)
        if PostAID is not None:
            CheckValue.check(str, 'PostAID', PostAID)
        CheckValue.check(int, 'PostIndex', PostIndex)

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
            CheckValue.checkIndex('PostIndex', PostIndex, NewestIndex)

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
                    # Screens.show(self._ConnectCore.getScreenQueue())
                    Log.log(
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
        PostIndex: int = 0
    ):
        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('qs')
        CmdList.append(Board)
        CmdList.append(Command.Enter)
        CmdList.append(Command.Ctrl_C * 2)
        CmdList.append(Command.Space)

        if PostAID is not None:
            CmdList.append('#' + PostAID)
        elif PostIndex != 0:
            CmdList.append(str(PostIndex))
        CmdList.append(Command.Enter)
        CmdList.append(Command.Push)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.HasPushPermission,
                '您覺得這篇',
                LogLevel=Log.Level.DEBUG,
                BreakDetect=True
            ),
            ConnectCore.TargetUnit(
                i18n.OnlyArrow,
                '加註方式',
                LogLevel=Log.Level.DEBUG,
                BreakDetect=True
            ),
            ConnectCore.TargetUnit(
                i18n.NoFastPush,
                '禁止快速連續推文',
                LogLevel=Log.Level.INFO,
                BreakDetect=True,
                Exceptions=Exceptions.NoFastPush()
            ),
            ConnectCore.TargetUnit(
                i18n.NoFastPush,
                '禁止短時間內大量推文',
                LogLevel=Log.Level.INFO,
                BreakDetect=True,
                Exceptions=Exceptions.NoFastPush()
            ),
            ConnectCore.TargetUnit(
                i18n.NoPermission,
                '使用者不可發言',
                LogLevel=Log.Level.INFO,
                BreakDetect=True,
                Exceptions=Exceptions.NoPermission(i18n.NoPermission)
            ),
            ConnectCore.TargetUnit(
                i18n.NoPush,
                '◆ 抱歉, 禁止推薦',
                LogLevel=Log.Level.INFO,
                BreakDetect=True,
                Exceptions=Exceptions.NoPush()
            ),
        ]

        index = self._ConnectCore.send(
            Cmd,
            TargetList
        )

        # print(index)
        # print(self._ConnectCore.getScreenQueue()[-1].split('\n')[-1])

        EnablePush = False
        EnableBoo = False
        EnableArrow = False

        CmdList = []

        if index == 0:
            PushOptionLine = self._ConnectCore.getScreenQueue()[-1]
            PushOptionLine = PushOptionLine.split('\n')[-1]
            Log.showValue(Log.Level.DEBUG, 'Push option line', PushOptionLine)

            EnablePush = '值得推薦' in PushOptionLine
            EnableBoo = '給它噓聲' in PushOptionLine
            EnableArrow = '只加→註解' in PushOptionLine

            Log.showValue(Log.Level.DEBUG, 'Push', EnablePush)
            Log.showValue(Log.Level.DEBUG, 'Boo', EnableBoo)
            Log.showValue(Log.Level.DEBUG, 'Arrow', EnableArrow)

            if PushType == DataType.PushType.Push and not EnablePush:
                PushType = DataType.PushType.Arrow
            elif PushType == DataType.PushType.Boo and not EnableBoo:
                PushType = DataType.PushType.Arrow
            elif PushType == DataType.PushType.Arrow and not EnableArrow:
                PushType = DataType.PushType.Push

            CmdList.append(str(PushType))
        elif index == 1:
            PushType = DataType.PushType.Arrow

        CmdList.append(PushContent)
        CmdList.append(Command.Enter)
        CmdList.append('y')
        CmdList.append(Command.Enter)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                [
                    i18n.Push,
                    i18n.Success,
                ],
                Screens.Target.InBoard,
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
        ]

        index = self._ConnectCore.send(
            Cmd,
            TargetList
        )

    def _getUser(self, UserID):

        CheckValue.check(str, 'UserID', UserID)
        if len(UserID) < 3:
            raise ValueError(Log.merge([
                'UserID',
                i18n.ErrorParameter,
                UserID
            ]))

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('T')
        CmdList.append(Command.Enter)
        CmdList.append('Q')
        CmdList.append(Command.Enter)
        CmdList.append(UserID)
        CmdList.append(Command.Enter)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                [
                    i18n.GetUser,
                    i18n.Success,
                ],
                Screens.Target.AnyKey,
                BreakDetect=True,
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.GetUser,
                    i18n.Fail,
                ],
                Screens.Target.InTalk,
                BreakDetect=True,
            ),
        ]

        index = self._ConnectCore.send(
            Cmd,
            TargetList
        )
        OriScreen = self._ConnectCore.getScreenQueue()[-1]
        Log.showValue(
            Log.Level.DEBUG,
            'OriScreen',
            OriScreen
        )
        if index == 1:
            raise Exceptions.NoSuchUser(UserID)
        # PTT1
        # 《ＩＤ暱稱》CodingMan (專業程式 BUG 製造機)《經濟狀況》小康 ($73866)
        # 《登入次數》1118 次 (同天內只計一次) 《有效文章》15 篇 (退:0)
        # 《目前動態》閱讀文章     《私人信箱》最近無新信件
        # 《上次上站》10/06/2019 17:29:49 Sun  《上次故鄉》111.251.231.184
        # 《 五子棋 》 0 勝  0 敗  0 和 《象棋戰績》 0 勝  0 敗  0 和

        # https://github.com/Truth0906/PTTLibrary

        # 強大的 PTT 函式庫
        # 提供您 快速 穩定 完整 的 PTT API

        # 提供專業的 PTT 機器人諮詢服務

        # PTT2
        # 《ＩＤ暱稱》CodingMan (專業程式 BUG 製造機)《經濟狀況》家徒四壁 ($0)
        # 《登入次數》8 次 (同天內只計一次)  《有效文章》0 篇
        # 《目前動態》看板列表     《私人信箱》最近無新信件
        # 《上次上站》10/06/2019 17:27:55 Sun  《上次故鄉》111.251.231.184
        # 《 五子棋 》 0 勝  0 敗  0 和 《象棋戰績》 0 勝  0 敗  0 和

        # 《個人名片》CodingMan 目前沒有名片

        Data = Util.getSubStringList(OriScreen, '》', ['《', '\n'])
        if len(Data) < 10:
            print('\n'.join(Data))
            print(len(Data))
            raise Exceptions.ParseError(OriScreen)

        ID = Data[0]
        Money = Data[1]
        LoginTime = Data[2]
        LoginTime = LoginTime[:LoginTime.find(' ')]
        LoginTime = int(LoginTime)

        Temp = re.findall(r'\d+', Data[3])
        LegalPost = int(Temp[0])

        # PTT2 沒有退文
        if Config.Host == DataType.Host.PTT1:
            IllegalPost = int(Temp[1])
        else:
            IllegalPost = -1

        State = Data[4]
        Mail = Data[5]
        LastLogin = Data[6]
        LastIP = Data[7]
        FiveChess = Data[8]
        Chess = Data[9]

        SignatureFile = '\n'.join(OriScreen.split('\n')[6:-1]).strip()

        Log.showValue(Log.Level.DEBUG, 'ID', ID)
        Log.showValue(Log.Level.DEBUG, 'Money', Money)
        Log.showValue(Log.Level.DEBUG, 'LoginTime', LoginTime)
        Log.showValue(Log.Level.DEBUG, 'LegalPost', LegalPost)
        Log.showValue(Log.Level.DEBUG, 'IllegalPost', IllegalPost)
        Log.showValue(Log.Level.DEBUG, 'State', State)
        Log.showValue(Log.Level.DEBUG, 'Mail', Mail)
        Log.showValue(Log.Level.DEBUG, 'LastLogin', LastLogin)
        Log.showValue(Log.Level.DEBUG, 'LastIP', LastIP)
        Log.showValue(Log.Level.DEBUG, 'FiveChess', FiveChess)
        Log.showValue(Log.Level.DEBUG, 'Chess', Chess)
        Log.showValue(Log.Level.DEBUG, 'SignatureFile', SignatureFile)

        User = DataType.UserInfo(
            ID,
            Money,
            LoginTime,
            LegalPost,
            IllegalPost,
            State,
            Mail,
            LastLogin,
            LastIP,
            FiveChess,
            Chess,
            SignatureFile
        )
        return User

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

        CheckValue.check(str, 'TargetID', TargetID)
        CheckValue.check(str, 'Content', Content)

        if len(TargetID) <= 2:
            raise ValueError(Log.merge([
                'TargetID',
                i18n.ErrorParameter,
                TargetID
            ]))

        User = self._getUser(TargetID)
        if '不在站上' in User.getState():
            raise Exceptions.UserOffline(TargetID)

        MaxLength = 50

        WaterBallList = []

        TempStartIndex = 0
        TempEndIndex = TempStartIndex + 1

        while TempEndIndex <= len(Content):
            Temp = ''
            LastTemp = None
            while len(Temp.encode('big5-uao', 'ignore')) < MaxLength:
                Temp = Content[TempStartIndex:TempEndIndex]

                if not len(Temp.encode('big5-uao', 'ignore')) < MaxLength:
                    break
                elif Content.endswith(Temp) and TempStartIndex != 0:
                    break
                elif Temp.endswith('\n'):
                    break
                elif LastTemp == Temp:
                    break

                TempEndIndex += 1
                LastTemp = Temp

            WaterBallList.append(Temp.strip())

            TempStartIndex = TempEndIndex
            TempEndIndex = TempStartIndex + 1
        WaterBallList = filter(None, WaterBallList)

        for waterball in WaterBallList:

            if self._LastThroWaterBallTime != 0:
                CurrentTime = time.time()
                while (CurrentTime - self._LastThroWaterBallTime) < 3.2:
                    time.sleep(0.1)
                    CurrentTime = time.time()

            Log.showValue(
                Log.Level.INFO,
                i18n.WaterBall,
                waterball
            )

            TargetList = [
                ConnectCore.TargetUnit(
                    i18n.SetCallStatus,
                    '您的呼叫器目前設定為關閉',
                    Response='y' + Command.Enter,
                ),
                # 對方已落跑了
                ConnectCore.TargetUnit(
                    i18n.SetCallStatus,
                    '◆ 糟糕! 對方已落跑了',
                    Exceptions=Exceptions.UserOffline(TargetID)
                ),
                ConnectCore.TargetUnit(
                    [
                        i18n.Throw,
                        TargetID,
                        i18n.WaterBall
                    ],
                    '丟 ' + TargetID + ' 水球:',
                    Response=waterball + Command.Enter * 2 +
                    Command.GoMainMenu,
                ),
                ConnectCore.TargetUnit(
                    [
                        i18n.Throw,
                        i18n.WaterBall,
                        i18n.Success
                    ],
                    Screens.Target.MainMenu,
                    BreakDetect=True
                )
            ]

            CmdList = []
            CmdList.append(Command.GoMainMenu)
            CmdList.append('T')
            CmdList.append(Command.Enter)
            CmdList.append('U')
            CmdList.append(Command.Enter)
            if '【好友列表】' in self._ConnectCore.getScreenQueue()[-1]:
                CmdList.append('f')
            CmdList.append('s')
            CmdList.append(TargetID)
            CmdList.append(Command.Enter)
            CmdList.append('w')

            Cmd = ''.join(CmdList)

            index = self._ConnectCore.send(
                Cmd,
                TargetList,
                ScreenTimeout=Config.ScreenLongTimeOut
            )

            self._LastThroWaterBallTime = time.time()

    def getWaterBall(self, OperateType):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if self._UnregisteredUser:
            raise Exceptions.UnregisteredUser(Util.getCurrentFuncName())

        CheckValue.check(int, 'OperateType', OperateType,
                         Class=DataType.WaterBallOperateType)

        if OperateType == DataType.WaterBallOperateType.DoNothing:
            WaterBallOperateType = 'R'
        elif OperateType == DataType.WaterBallOperateType.Clear:
            WaterBallOperateType = 'C' + Command.Enter + 'Y'
        elif OperateType == DataType.WaterBallOperateType.Mail:
            WaterBallOperateType = 'M'

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.NoWaterball,
                '◆ 暫無訊息記錄',
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.BrowseWaterball,
                    i18n.Done,
                ],
                Screens.Target.WaterBallListEnd,
                Response=Command.Left + WaterBallOperateType +
                Command.Enter + Command.GoMainMenu,
                BreakDetectAfterSend=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.BrowseWaterball,
                ],
                Screens.Target.InWaterBallList,
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
        ]

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('T')
        CmdList.append(Command.Enter)
        CmdList.append('D')
        CmdList.append(Command.Enter)

        Cmd = ''.join(CmdList)

        WaterBallList = []

        LineFromTopattern = re.compile('[\d]+~[\d]+')
        ToWaterBallTargetPattern = re.compile('To [\w]+:')
        FromWaterBallTargetPattern = re.compile('★[\w]+ ')
        WaterBallDatePattern = re.compile(
            '\[[\d]+/[\d]+/[\d]+ [\d]+:[\d]+:[\d]+\]')

        AllWaterball = []
        FirstPage = True
        while True:
            index = self._ConnectCore.send(
                Cmd,
                TargetList,
                ScreenTimeout=1
            )
            Log.showValue(
                Log.Level.DEBUG,
                'index',
                index
            )
            if index == 0:
                return WaterBallList

            OriScreen = self._ConnectCore.getScreenQueue()[-1]
            Lines = OriScreen.split('\n')
            LastLine = Lines[-1]
            Lines.pop()
            Lines = list(filter(None, Lines))
            OriScreen = '\n'.join(Lines)

            # print('=' * 50)
            # print(OriScreen)
            # print('=' * 50)
            ScreenTemp = OriScreen
            Log.showValue(
                Log.Level.DEBUG,
                'OriScreen',
                OriScreen
            )

            Log.showValue(
                Log.Level.DEBUG,
                'LastLine',
                LastLine
            )
            if LastLine.startswith('★'):
                continue

            # 整理水球換行格式
            # ScreenTemp = ScreenTemp.replace(
            #     ']\n', ']==PTTWaterBallNewLine==')
            # ScreenTemp = ScreenTemp.replace('\\\n', '')
            # ScreenTemp = ScreenTemp.replace('\n', '')
            # ScreenTemp = ScreenTemp.replace(
            #     ']==PTTWaterBallNewLine==', ']\n')

            # print('=' * 50)
            # print(LastLine)
            # print('=' * 50)

            PatternResult = LineFromTopattern.search(LastLine)
            LastReadLineList = PatternResult.group(0).split('~')
            LastReadLineATemp = int(LastReadLineList[0])
            LastReadLineBTemp = int(LastReadLineList[1])
            # LastReadLineA = LastReadLineATemp - 1
            # LastReadLineB = LastReadLineBTemp - 1

            if FirstPage:
                FirstPage = False
                AllWaterball.append(OriScreen)
                LastReadLineA = LastReadLineATemp - 1
                LastReadLineB = LastReadLineBTemp - 1
            else:
                GetLineA = LastReadLineATemp - LastReadLineA
                GetLineB = LastReadLineBTemp - LastReadLineB

                # print(f'LastReadLineA [{LastReadLineA}]')
                # print(f'LastReadLineB [{LastReadLineB}]')
                # print(f'LastReadLineATemp [{LastReadLineATemp}]')
                # print(f'LastReadLineBTemp [{LastReadLineBTemp}]')
                # print(f'GetLineA [{GetLineA}]')
                # print(f'GetLineB [{GetLineB}]')
                if GetLineB > 0:
                    # print('Type 1')

                    if not AllWaterball[-1].endswith(']'):
                        GetLineB += 1

                    NewContentPart = '\n'.join(Lines[-GetLineB:])
                else:
                    # print('Type 2')
                    if GetLineA > 0:
                        # print('Type 2 - 1')

                        if len(Lines[-GetLineA]) == 0:
                            # print('!!!!!!!!!')
                            GetLineA += 1

                        NewContentPart = '\n'.join(Lines[-GetLineA:])
                    else:
                        # print('Type 2 - 2')
                        NewContentPart = '\n'.join(Lines)

                AllWaterball.append(NewContentPart)
                Log.showValue(
                    Log.Level.DEBUG,
                    'NewContentPart',
                    NewContentPart
                )

            if index == 1:
                break

            LastReadLineA = LastReadLineATemp
            LastReadLineB = LastReadLineBTemp

            Cmd = Command.Down

        AllWaterball = '\n'.join(AllWaterball)

        if Config.Host == DataType.Host.PTT1:
            AllWaterball = AllWaterball.replace(
                ']\n', ']==PTTWaterBallNewLine==')
            AllWaterball = AllWaterball.replace('\n', '')
            AllWaterball = AllWaterball.replace(
                ']==PTTWaterBallNewLine==', ']\n')
        else:
            AllWaterball = AllWaterball.replace('\\\n', '')
        Log.showValue(
            Log.Level.DEBUG,
            'AllWaterball',
            AllWaterball
        )
        # print('=' * 20)
        # print(AllWaterball)
        # print('=' * 20)

        WaterBallList = []
        for line in AllWaterball.split('\n'):

            if (not line.startswith('To')) and (not line.startswith('★')):
                Log.showValue(
                    Log.Level.DEBUG,
                    'Discard waterball',
                    line
                )
                continue
            Log.showValue(
                Log.Level.DEBUG,
                'Ready to parse waterball',
                line
            )

            if line.startswith('To'):
                Log.showValue(
                    Log.Level.DEBUG,
                    'Waterball Type',
                    'Send'
                )
                Type = DataType.WaterBallType.Send

                PatternResult = ToWaterBallTargetPattern.search(line)
                Target = PatternResult.group(0)[3:-1]

                PatternResult = WaterBallDatePattern.search(line)
                Date = PatternResult.group(0)[1:-1]

                Content = line
                Content = Content[Content.find(
                    Target + ':') + len(Target + ':'):]
                Content = Content[:Content.rfind(Date) - 1]
                Content = Content.strip()

            elif line.startswith('★'):
                Log.showValue(
                    Log.Level.DEBUG,
                    'Waterball Type',
                    'Catch'
                )
                Type = DataType.WaterBallType.Catch

                PatternResult = FromWaterBallTargetPattern.search(line)
                Target = PatternResult.group(0)[1:-1]

                PatternResult = WaterBallDatePattern.search(line)
                Date = PatternResult.group(0)[1:-1]

                Content = line
                Content = Content[Content.find(
                    Target + ' ') + len(Target + ' '):]
                Content = Content[:Content.rfind(Date) - 1]
                Content = Content.strip()

            Log.showValue(
                Log.Level.DEBUG,
                'Waterball Target',
                Target
            )
            Log.showValue(
                Log.Level.DEBUG,
                'Waterball Content',
                Content
            )
            Log.showValue(
                Log.Level.DEBUG,
                'Waterball Date',
                Date
            )

            CurrentWaterBall = DataType.WaterBallInfo(
                Type,
                Target,
                Content,
                Date
            )

            WaterBallList.append(CurrentWaterBall)

        return WaterBallList

    def getCallStatus(self):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        return self._getCallStatus()

    def _getCallStatus(self):

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('A')
        CmdList.append(Command.Right)
        CmdList.append(Command.Left)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                [
                    i18n.GetCallStatus,
                    i18n.Success,
                ],
                '[呼叫器]打開',
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.GetCallStatus,
                    i18n.Success,
                ],
                '[呼叫器]拔掉',
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.GetCallStatus,
                    i18n.Success,
                ],
                '[呼叫器]防水',
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.GetCallStatus,
                    i18n.Success,
                ],
                '[呼叫器]好友',
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.GetCallStatus,
                    i18n.Success,
                ],
                '[呼叫器]關閉',
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.GetCallStatus,
                ],
                '★',
                Response=Cmd,
                LogLevel=Log.Level.DEBUG
            ),
        ]

        for i in range(2):
            index = self._ConnectCore.send(Cmd, TargetList)
            if index < 0:
                if i == 0:
                    continue
                OriScreen = self._ConnectCore.getScreenQueue()[-1]
                raise Exceptions.UnknowError(OriScreen)

        if index == 0:
            return DataType.CallStatus.On
        if index == 1:
            return DataType.CallStatus.Unplug
        if index == 2:
            return DataType.CallStatus.Waterproof
        if index == 3:
            return DataType.CallStatus.Friend
        if index == 4:
            return DataType.CallStatus.Off

        OriScreen = self._ConnectCore.getScreenQueue()[-1]
        raise Exceptions.UnknowError(OriScreen)

    def setCallStatus(
        self,
        inputCallStatus
    ):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(int, 'CallStatus', inputCallStatus,
                         Class=DataType.CallStatus)

        # 打開 -> 拔掉 -> 防水 -> 好友 -> 關閉

        CurrentCallStatus = self._getCallStatus()

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append(Command.Ctrl_U)
        CmdList.append('p')

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                [
                    i18n.SetCallStatus,
                    i18n.Success
                ],
                Screens.Target.InUserList,
                BreakDetect=True
            )
        ]

        while CurrentCallStatus != inputCallStatus:
            self._ConnectCore.send(
                Cmd,
                TargetList,
                ScreenTimeout=Config.ScreenLongTimeOut
            )

            CurrentCallStatus = self._getCallStatus()

    def giveMoney(self, ID, Money):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if self._UnregisteredUser:
            raise Exceptions.UnregisteredUser(Util.getCurrentFuncName())

        CheckValue.check(str, 'ID', ID)
        CheckValue.check(int, 'Money', Money)

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('P')
        CmdList.append(Command.Enter)
        CmdList.append('P')
        CmdList.append(Command.Enter)
        CmdList.append('O')
        CmdList.append(Command.Enter)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.NoMoney,
                '你沒有那麼多Ptt幣喔!',
                BreakDetect=True,
                Exceptions=Exceptions.NoMoney
            ),
            ConnectCore.TargetUnit(
                i18n.NoMoney,
                '金額過少，交易取消!',
                BreakDetect=True,
                Exceptions=Exceptions.MoneyTooFew
            ),
            ConnectCore.TargetUnit(
                i18n.NoMoney,
                '交易取消!',
                BreakDetect=True,
                Exceptions=Exceptions.UnknowError
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.Transaction,
                    i18n.Success
                ],
                '按任意鍵繼續',
                BreakDetect=True
            ),
            ConnectCore.TargetUnit(
                i18n.ConstantRedBag,
                '要修改紅包袋嗎',
                Response=Command.Enter
            ),
            ConnectCore.TargetUnit(
                i18n.VerifyID,
                '完成交易前要重新確認您的身份',
                Response=self._Password + Command.Enter
            ),
            ConnectCore.TargetUnit(
                i18n.InputMoney,
                '要給他多少Ptt幣呢?',
                Response=Command.Tab + str(Money) + Command.Enter
            ),
            ConnectCore.TargetUnit(
                i18n.InputID,
                '這位幸運兒的id',
                Response=ID + Command.Enter
            ),
            ConnectCore.TargetUnit(
                i18n.AuthenticationHasNotExpired,
                '認證尚未過期',
                Response='y' + Command.Enter
            ),
            ConnectCore.TargetUnit(
                i18n.TradingInProgress,
                '交易正在進行中',
                Response=Command.Space
            )
        ]

        self._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=Config.ScreenLongTimeOut
        )

    def mail(
        self,
        ID: str,
        Title: str,
        Content: str,
        SignFile
    ):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(str, 'ID', ID)
        CheckValue.check(str, 'Title', Title)
        CheckValue.check(str, 'Content', Content)

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

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('M')
        CmdList.append(Command.Enter)
        CmdList.append('S')
        CmdList.append(Command.Enter)
        CmdList.append(ID)
        CmdList.append(Command.Enter)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                [
                    i18n.Start,
                    i18n.SendMail
                ],
                '主題：',
                BreakDetect=True
            ),
            ConnectCore.TargetUnit(
                i18n.NoSuchUser,
                '【電子郵件】',
                Exceptions=Exceptions.NoSuchUser(ID)
            ),
        ]

        self._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=Config.ScreenLongTimeOut
        )

        CmdList = []
        CmdList.append(Title)
        CmdList.append(Command.Enter)
        CmdList.append(Content)
        CmdList.append(Command.Ctrl_X)

        Cmd = ''.join(CmdList)

        if SignFile == 0:
            SingFileSelection = i18n.NoSignatureFile
        else:
            SingFileSelection = i18n.Select + ' ' + \
                str(SignFile) + 'th ' + i18n.SignatureFile

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.AnyKeyContinue,
                '任意鍵',
                BreakDetect=True
            ),
            ConnectCore.TargetUnit(
                i18n.SaveFile,
                '確定要儲存檔案嗎',
                Response='s' + Command.Enter,
                # Refresh=False,
            ),
            ConnectCore.TargetUnit(
                i18n.SelfSaveDraft,
                '是否自存底稿',
                Response='y' + Command.Enter
            ),
            ConnectCore.TargetUnit(
                SingFileSelection,
                '選擇簽名檔',
                Response=str(SignFile) + Command.Enter
            ),
            ConnectCore.TargetUnit(
                SingFileSelection,
                'x=隨機',
                Response=str(SignFile) + Command.Enter
            ),
        ]

        self._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=Config.ScreenPostTimeOut
        )

        Log.showValue(
            Log.Level.INFO,
            i18n.SendMail,
            i18n.Success
        )

    def hasNewMail(self):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('M')
        CmdList.append(Command.Enter)
        CmdList.append('R')
        CmdList.append(Command.Enter)
        CmdList.append('1')
        CmdList.append(Command.Enter)
        CmdList.append('$')
        Cmd = ''.join(CmdList)

        #
        TargetList = [
            ConnectCore.TargetUnit(
                i18n.MailBox,
                Screens.Target.InMailBox,
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            )
        ]

        self._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=Config.ScreenLongTimeOut
        )

        OriScreen = self._ConnectCore.getScreenQueue()[-1]

        pattern = re.findall('[\s]+[\d]+ (\+)[\s]+', OriScreen)
        return len(pattern)

    def getBoardList(self):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('F')
        CmdList.append(Command.Enter)
        CmdList.append('y')
        CmdList.append('$')
        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.BoardList,
                Screens.Target.InBoardList,
                BreakDetect=True
            )
        ]

        self._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=Config.ScreenLongTimeOut
        )
        OriScreen = self._ConnectCore.getScreenQueue()[-1]

        MaxNo = 0

        for line in OriScreen.split('\n'):
            if '◎' not in line:
                continue

            if line.startswith(self._Cursor):
                line = line[len(self._Cursor):]

            # print(f'->{line}<')

            FrontPart = line[:line.find('◎')]
            FrontPartList = [x for x in FrontPart.split(' ')]
            FrontPartList = list(filter(None, FrontPartList))
            # print(f'FrontPartList =>{FrontPartList}<=')
            MaxNo = int(FrontPartList[0])

        Log.showValue(
            Log.Level.DEBUG,
            'MaxNo',
            MaxNo
        )

        if Config.LogLevel == Log.Level.INFO:
            PB = progressbar.ProgressBar(
                max_value=MaxNo,
                redirect_stdout=True
            )

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('F')
        CmdList.append(Command.Enter)
        CmdList.append('y')
        CmdList.append('0')
        Cmd = ''.join(CmdList)

        BoardList = []
        while True:

            self._ConnectCore.send(
                Cmd,
                TargetList,
                ScreenTimeout=Config.ScreenLongTimeOut
            )

            OriScreen = self._ConnectCore.getScreenQueue()[-1]
            # print(OriScreen)
            for line in OriScreen.split('\n'):
                if '◎' not in line and '●' not in line:
                    continue

                if line.startswith(self._Cursor):
                    line = line[len(self._Cursor):]

                # print(f'->{line}<')

                if '◎' in line:
                    FrontPart = line[:line.find('◎')]
                else:
                    FrontPart = line[:line.find('●')]
                FrontPartList = [x for x in FrontPart.split(' ')]
                FrontPartList = list(filter(None, FrontPartList))
                # print(f'FrontPartList =>{FrontPartList}<=')
                No = int(FrontPartList[0])
                # print(f'No  =>{No}<=')
                # print(f'LastNo =>{LastNo}<=')

                Log.showValue(
                    Log.Level.DEBUG,
                    'Board NO',
                    No
                )

                BoardName = FrontPartList[1]
                if BoardName.startswith('ˇ'):
                    BoardName = BoardName[1:]

                Log.showValue(
                    Log.Level.DEBUG,
                    'Board Name',
                    BoardName
                )
                # 版名重複
                # > 10609   BR_Joseyen   苦甜 ◎Josey的異想世界                    1 joseyen
                #   10610   BR_Joseyen   苦甜 ◎Josey的異想世界                      joseyen

                BoardList.append(BoardName)

                if Config.LogLevel == Log.Level.INFO:
                    PB.update(No)

            if No == MaxNo:
                break
            Cmd = Command.Ctrl_F

        if Config.LogLevel == Log.Level.INFO:
            PB.finish()

        return BoardList

    def replyPost(
        self,
        inputReplyType: int,
        Board: str,
        Content: str,
        SignFile=0,
        PostAID: str = None,
        PostIndex: int = 0
    ):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(int, 'ReplyType', inputReplyType,
                         Class=DataType.ReplyType)
        CheckValue.check(str, 'Board', Board)
        CheckValue.check(str, 'Content', Content)
        if PostAID is not None:
            CheckValue.check(str, 'PostAID', PostAID)

        if PostIndex != 0:

            NewestIndex = self._getNewestIndex(
                DataType.IndexType.BBS,
                Board=Board,
            )
            CheckValue.checkIndex('PostIndex', PostIndex, MaxValue=NewestIndex)

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

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('qs')
        CmdList.append(Board)
        CmdList.append(Command.Enter)
        CmdList.append(Command.Ctrl_C * 2)
        CmdList.append(Command.Space)

        if PostAID is not None:
            CmdList.append('#' + PostAID)
        elif PostIndex != 0:
            CmdList.append(str(PostIndex))
        CmdList.append(Command.Enter * 2)
        CmdList.append('r')

        if inputReplyType == DataType.ReplyType.Board:
            ReplyTargetUnit = ConnectCore.TargetUnit(
                i18n.ReplyBoard,
                '▲ 回應至',
                LogLevel=Log.Level.INFO,
                Response='F' + Command.Enter
            )
        elif inputReplyType == DataType.ReplyType.Mail:
            ReplyTargetUnit = ConnectCore.TargetUnit(
                i18n.ReplyMail,
                '▲ 回應至',
                LogLevel=Log.Level.INFO,
                Response='M' + Command.Enter
            )
        elif inputReplyType == DataType.ReplyType.Board_Mail:
            ReplyTargetUnit = ConnectCore.TargetUnit(
                i18n.ReplyBoard_Mail,
                '▲ 回應至',
                LogLevel=Log.Level.INFO,
                Response='B' + Command.Enter
            )

        Cmd = ''.join(CmdList)
        TargetList = [
            ConnectCore.TargetUnit(
                i18n.AnyKeyContinue,
                '任意鍵繼續',
                BreakDetect=True,
            ),
            ConnectCore.TargetUnit(
                i18n.NoResponse,
                '◆ 很抱歉, 此文章已結案並標記, 不得回應',
                LogLevel=Log.Level.INFO,
                Exceptions=Exceptions.NoResponse()
            ),
            ConnectCore.TargetUnit(
                i18n.ForcedWrite,
                '(E)繼續編輯 (W)強制寫入',
                LogLevel=Log.Level.INFO,
                Response='W' + Command.Enter
            ),
            ConnectCore.TargetUnit(
                i18n.SelectSignature,
                '請選擇簽名檔',
                Response=str(SignFile) + Command.Enter,
            ),
            ConnectCore.TargetUnit(
                i18n.SaveFile,
                '確定要儲存檔案嗎',
                Response='s' + Command.Enter,
            ),
            ConnectCore.TargetUnit(
                i18n.EditPost,
                '編輯文章',
                LogLevel=Log.Level.INFO,
                Response=str(Content) + Command.Enter + Command.Ctrl_X
            ),
            ConnectCore.TargetUnit(
                i18n.QuoteOriginal,
                '請問要引用原文嗎',
                LogLevel=Log.Level.DEBUG,
                Response='Y' + Command.Enter
            ),
            ConnectCore.TargetUnit(
                i18n.UseTheOriginalTitle,
                '採用原標題[Y/n]?',
                LogLevel=Log.Level.DEBUG,
                Response='Y' + Command.Enter
            ),
            ReplyTargetUnit,
            ConnectCore.TargetUnit(
                i18n.SelfSaveDraft,
                '已順利寄出，是否自存底稿',
                LogLevel=Log.Level.DEBUG,
                Response='Y' + Command.Enter
            ),
        ]

        self._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=Config.ScreenLongTimeOut
        )

        Log.log(
            Log.Level.INFO,
            i18n.RespondSuccess
        )

    def setBoardTitle(
        self,
        Board: str,
        NewTitle: str
    ):
        # 第一支板主專用 API
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(str, 'Board', Board)
        CheckValue.check(str, 'NewTitle', NewTitle)

        self._checkBoard(
            Board,
            CheckModerator=True
        )

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('qs')
        CmdList.append(Board)
        CmdList.append(Command.Enter)
        CmdList.append(Command.Ctrl_C * 2)
        CmdList.append(Command.Space)
        CmdList.append('I')
        CmdList.append(Command.Ctrl_P)
        CmdList.append('b')
        CmdList.append(Command.Enter)
        CmdList.append(Command.Backspace * 31)
        CmdList.append(NewTitle)
        CmdList.append(Command.Enter * 2)
        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.NewSettingsHaveBeenSaved,
                '◆ 已儲存新設定',
                BreakDetect=True,
            ),
            ConnectCore.TargetUnit(
                i18n.NoChanges,
                '◆ 未改變任何設定',
                BreakDetect=True,
            ),
        ]

        self._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=Config.ScreenLongTimeOut
        )

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

        CheckValue.check(int, 'MarkType', inputMarkType,
                         Class=DataType.MarkType)
        CheckValue.check(str, 'Board', Board)
        if PostAID is not None:
            CheckValue.check(str, 'PostAID', PostAID)
        CheckValue.check(int, 'PostIndex', PostIndex)
        CheckValue.check(int, 'SearchType', SearchType,
                         Class=DataType.PostSearchType)
        if SearchCondition is not None:
            CheckValue.check(str, 'SearchCondition', SearchCondition)

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
            CheckValue.checkIndex('PostIndex', PostIndex, MaxValue=NewestIndex)

        if inputMarkType == DataType.MarkType.Unconfirmed:
            # 批踢踢兔沒有待證文章功能 QQ
            if Config.Host == DataType.Host.PTT2:
                raise Exceptions.HostNotSupport(Util.getCurrentFuncName())

        self._checkBoard(
            Board,
            CheckModerator=True
        )

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('qs')
        CmdList.append(Board)
        CmdList.append(Command.Enter)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.AnyKeyContinue,
                '任意鍵',
                Response=' ',
            ),
            ConnectCore.TargetUnit(
                [
                    '動畫播放中',
                ],
                '互動式動畫播放中',
                Response=Command.Ctrl_C,
                LogLevel=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                [
                    '進板成功',
                ],
                Screens.Target.InBoard,
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
        ]

        index = self._ConnectCore.send(Cmd, TargetList)

        CmdList = []
        if PostAID is not None:
            CmdList.append('#' + PostAID)

        elif PostIndex != 0:
            if SearchCondition is not None:
                if SearchType == DataType.PostSearchType.Keyword:
                    CmdList.append('/')
                elif SearchType == DataType.PostSearchType.Author:
                    CmdList.append('a')
                elif SearchType == DataType.PostSearchType.Push:
                    CmdList.append('Z')
                elif SearchType == DataType.PostSearchType.Mark:
                    CmdList.append('G')
                elif SearchType == DataType.PostSearchType.Money:
                    CmdList.append('A')

                CmdList.append(SearchCondition)
                CmdList.append(Command.Enter)

            CmdList.append(str(PostIndex))

        CmdList.append(Command.Enter)

        if inputMarkType == DataType.MarkType.S:
            CmdList.append('L')
        elif inputMarkType == DataType.MarkType.D:
            CmdList.append('t')
        elif inputMarkType == DataType.MarkType.DeleteD:
            CmdList.append(Command.Ctrl_D)
        elif inputMarkType == DataType.MarkType.M:
            CmdList.append('m')
        elif inputMarkType == DataType.MarkType.Unconfirmed:
            CmdList.append(Command.Ctrl_E + 'S')

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                [i18n.DelAllMarkPost],
                '刪除所有標記',
                Response='y' + Command.Enter,
                LogLevel=Log.Level.INFO
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.Mark,
                    i18n.Success,
                ],
                Screens.Target.InBoard,
                BreakDetect=True,
                LogLevel=Log.Level.INFO
            ),
        ]

        index = self._ConnectCore.send(Cmd, TargetList)

    def getFavouriteBoard(self):
        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('F')
        CmdList.append(Command.Enter)
        CmdList.append('0')
        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.FavouriteBoardList,
                '選擇看板',
                BreakDetect=True
            )
        ]

        FavouriteBoardList = []
        while True:

            self._ConnectCore.send(
                Cmd,
                TargetList
            )

            OriScreen = self._ConnectCore.getScreenQueue()[-1]
            # print(OriScreen)
            ScreenBuf = OriScreen
            ScreenBuf = [x for x in ScreenBuf.split('\n')][3:][:-1]
            ScreenBuf[0] = '  ' + ScreenBuf[0][1:]
            ScreenBuf = [x for x in ScreenBuf]

            MinLen = 47

            # for line in ScreenBuf:
            #     print(line[:MinLen - len(line)])
            #     print(len(line))
            for i, line in enumerate(ScreenBuf):
                if len(ScreenBuf[i]) == 0:
                    continue
                if len(ScreenBuf[i]) <= MinLen:
                    # print(f'[{ScreenBuf[i]}]')
                    ScreenBuf[i] = ScreenBuf[i] + \
                        (' ' * ((MinLen + 1) - len(ScreenBuf[i])))
            ScreenBuf = [x[10:MinLen - len(x)].strip() for x in ScreenBuf]
            ScreenBuf = list(filter(None, ScreenBuf))

            for i, line in enumerate(ScreenBuf):
                # print(i)
                # 16 = line.find('◎')
                linebuff = line[:16].strip()

                Type = linebuff[-2:]
                Board = linebuff[:-2].strip()

                BoardTitle = line[17:].strip()
                # print(line)
                # print('\t' + Type)
                # print('\t' + Board)
                # print('\t' + BoardTitle)

                FBoard = DataType.FavouriteBoard(
                    Board,
                    Type,
                    BoardTitle
                )

                FavouriteBoardList.append(FBoard)

            # print(len(FavouriteBoardList))
            # print(len(ScreenBuf))
            if len(ScreenBuf) < 20:
                break

            Cmd = Command.Ctrl_F

        # ScreenBuf = '\n'.join(ScreenBuf)
        # print(ScreenBuf)
        # print(len(FavouriteBoardList))
        return FavouriteBoardList

    def bucket(self, Board, BucketDays, Reason, TargetID):

        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(str, 'Board', Board)
        CheckValue.check(int, 'BucketDays', BucketDays)
        CheckValue.check(str, 'Reason', Reason)
        CheckValue.check(str, 'TargetID', TargetID)

        self._checkBoard(
            Board,
            CheckModerator=True
        )

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('qs')
        CmdList.append(Board)
        CmdList.append(Command.Enter)
        CmdList.append(Command.Ctrl_C * 2)
        CmdList.append(Command.Space)
        CmdList.append('i')
        CmdList.append(Command.Ctrl_P)
        CmdList.append('w')
        CmdList.append(Command.Enter)
        CmdList.append('a')
        CmdList.append(Command.Enter)
        CmdList.append(TargetID)
        CmdList.append(Command.Enter)
        Cmd = ''.join(CmdList)

        CmdList = []
        CmdList.append(str(BucketDays))
        CmdList.append(Command.Enter)
        CmdList.append(Reason)
        CmdList.append(Command.Enter)
        CmdList.append('y')
        CmdList.append(Command.Enter)
        CmdPart2 = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                [
                    i18n.bucket,
                    i18n.Fail,
                ],
                '◆ 使用者之前已被禁言',
                Exceptions=Exceptions.UserHasPreviouslyBeenBanned()
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.bucket,
                    i18n.Success,
                ],
                '任意鍵',
                BreakDetect=True,
            ),
            ConnectCore.TargetUnit(
                i18n.InputBucketDays_Reason,
                '請以數字跟單位(預設為天)輸入期限',
                Response=CmdPart2,
            ),
        ]

        self._ConnectCore.send(
            Cmd,
            TargetList
        )

        OriScreen = self._ConnectCore.getScreenQueue()[-1]

    def searchUser(self, target, minpage=None, maxpage=None):

        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(str, 'target', target)
        if minpage is not None:
            CheckValue.checkIndex(
                'minpage',
                minpage
            )

        if maxpage is not None:
            CheckValue.checkIndex(
                'maxpage',
                maxpage
            )

        if minpage is not None and maxpage is not None:
            CheckValue.checkIndexRange(
                'minpage',
                minpage,
                'maxpage',
                maxpage
            )

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('T')
        CmdList.append(Command.Enter)
        CmdList.append('Q')
        CmdList.append(Command.Enter)
        CmdList.append(target)
        Cmd = ''.join(CmdList)

        if minpage is not None:
            temppage = minpage
        else:
            temppage = 1

        appendstr = ' ' * temppage
        cmdtemp = Cmd + appendstr

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.AnyKeyContinue,
                '任意鍵',
                BreakDetect=True,
            ),
        ]

        resultlist = []

        while True:

            self._ConnectCore.send(
                cmdtemp,
                TargetList
            )
            OriScreen = self._ConnectCore.getScreenQueue()[-1]
            Log.log(
                Log.Level.INFO,
                i18n.Reading
            )
            # print(OriScreen)
            # print(len(OriScreen.split('\n')))

            if len(OriScreen.split('\n')) == 2:
                resultid = OriScreen.split('\n')[1]
                resultid = resultid[resultid.find(' ') + 1:].strip()
                # print(resultid)

                resultlist.append(resultid)
                break
            else:

                OriScreen = OriScreen.split('\n')[3:-1]
                OriScreen = '\n'.join(OriScreen)

                templist = OriScreen.replace('\n', ' ')

                while '  ' in templist:
                    templist = templist.replace('  ', ' ')

                templist = templist.split(' ')
                resultlist.extend(templist)

                # print(templist)
                # print(len(templist))

                if len(templist) != 100 and len(templist) != 120:
                    break

                temppage += 1
                if maxpage is not None:
                    if temppage > maxpage:
                        break

                cmdtemp = ' '

        Log.log(
            Log.Level.INFO,
            i18n.ReadComplete
        )

        self._ConnectCore.send(
            Command.Enter,
            [
                # 《ＩＤ暱稱》
                ConnectCore.TargetUnit(
                    i18n.QuitUserProfile,
                    '《ＩＤ暱稱》',
                    Response=Command.Enter,
                    # LogLevel=Log.Level.DEBUG
                ),
                ConnectCore.TargetUnit(
                    i18n.Done,
                    '查詢網友',
                    BreakDetect=True,
                    # LogLevel=Log.Level.DEBUG
                )
            ]
        )

        resultlist = list(filter(None, resultlist))

        return resultlist

    def getBoardInfo(
        self,
        Board,
        setting=True
    ):

        self._OneThread()

        if not self._LoginStatus:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CheckValue.check(str, 'Board', Board)
        CheckValue.check(bool, 'setting', setting)
        self._checkBoard(Board)

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('qs')
        CmdList.append(Board)
        CmdList.append(Command.Enter)
        CmdList.append(Command.Ctrl_C * 2)
        CmdList.append(Command.Space)
        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.LoginSuccess,
                [
                    '文章選讀',
                    '進板畫面'
                ],
                BreakDetect=True
            ),
        ]

        index = self._ConnectCore.send(
            Cmd,
            TargetList
        )

        OriScreen = self._ConnectCore.getScreenQueue()[-1]
        # print(OriScreen)
        Nuser = OriScreen.split('\n')[2]
        # print(Nuser)
        if '[靜]' in Nuser:
            OnlineUser = 0
        else:
            pattern = re.compile('[\d]+')
            OnlineUser = pattern.search(Nuser).group(0)
            Log.showValue(
                Log.Level.DEBUG,
                '人氣',
                OnlineUser
            )

        if not setting:
            return DataType.BoardInfo(Board, OnlineUser)

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.AnyKeyContinue,
                '任意鍵繼續',
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
        ]

        index = self._ConnectCore.send(
            'i',
            TargetList
        )

        OriScreen = self._ConnectCore.getScreenQueue()[-1]
        # print(OriScreen)

        p = re.compile('中文敘述: (.+)')
        r = p.search(OriScreen)
        if r is not None:
            ChineseDes = r.group(0)[5:].strip()
        Log.showValue(
            Log.Level.DEBUG,
            '中文敘述',
            ChineseDes
        )

        p = re.compile('板主名單: (.+)')
        r = p.search(OriScreen)
        if r is not None:
            ModeratorLine = r.group(0)[5:].strip()
            Moderators = ModeratorLine.split('/')
        Log.showValue(
            Log.Level.DEBUG,
            '板主名單',
            Moderators
        )

        OpenState = ('公開狀態(是否隱形): 公開' in OriScreen)
        Log.showValue(
            Log.Level.DEBUG,
            '公開狀態',
            OpenState
        )

        IntoTopTenWhenHide = (
            '隱板時 可以 進入十大排行榜' in OriScreen
        )
        Log.showValue(
            Log.Level.DEBUG,
            '隱板時可以進入十大排行榜',
            IntoTopTenWhenHide
        )

        NonBoardMembersPost = ('開放 非看板會員發文' in OriScreen)
        Log.showValue(
            Log.Level.DEBUG,
            '非看板會員發文',
            NonBoardMembersPost
        )

        ReplyPost = ('開放 回應文章' in OriScreen)
        Log.showValue(
            Log.Level.DEBUG,
            '回應文章',
            ReplyPost
        )

        SelfDelPost = ('開放 自刪文章' in OriScreen)
        Log.showValue(
            Log.Level.DEBUG,
            '自刪文章',
            SelfDelPost
        )

        PushPost = ('開放 推薦文章' in OriScreen)
        Log.showValue(
            Log.Level.DEBUG,
            '推薦文章',
            PushPost
        )

        BooPost = ('開放 噓文' in OriScreen)
        Log.showValue(
            Log.Level.DEBUG,
            '噓文',
            BooPost
        )

        # 限制 快速連推文章, 最低間隔時間: 5 秒
        # 開放 快速連推文章

        FastPush = ('開放 快速連推文章' in OriScreen)
        Log.showValue(
            Log.Level.DEBUG,
            '快速連推文章',
            FastPush
        )

        if not FastPush:
            p = re.compile('最低間隔時間: [\d]+')
            r = p.search(OriScreen)
            if r is not None:
                MinInterval = r.group(0)[7:].strip()
                MinInterval = int(MinInterval)
            else:
                MinInterval = 0
            Log.showValue(
                Log.Level.DEBUG,
                '最低間隔時間',
                MinInterval
            )
        else:
            MinInterval = 0

        # 推文時 自動 記錄來源 IP
        # 推文時 不會 記錄來源 IP
        PushRecordIP = ('推文時 自動 記錄來源 IP' in OriScreen)
        Log.showValue(
            Log.Level.DEBUG,
            '記錄來源 IP',
            PushRecordIP
        )

        # 推文時 對齊 開頭
        # 推文時 不用對齊 開頭
        PushAligned = ('推文時 對齊 開頭' in OriScreen)
        Log.showValue(
            Log.Level.DEBUG,
            '對齊開頭',
            PushAligned
        )

        # 板主 可 刪除部份違規文字
        ModeratorCanDelIllegalContent = (
            '板主 可 刪除部份違規文字' in OriScreen
        )
        Log.showValue(
            Log.Level.DEBUG,
            '板主可刪除部份違規文字',
            ModeratorCanDelIllegalContent
        )

        # 轉錄文章 會 自動記錄，且 需要 發文權限
        TranPostAutoRecordedAndRequirePostPermissions = (
            '轉錄文章 會 自動記錄，且 需要 發文權限' in OriScreen
        )
        Log.showValue(
            Log.Level.DEBUG,
            '轉錄文章 會 自動記錄，且 需要 發文權限',
            TranPostAutoRecordedAndRequirePostPermissions
        )

        CoolMode = (
            '未 設為冷靜模式' not in OriScreen
        )
        Log.showValue(
            Log.Level.DEBUG,
            '冷靜模式',
            CoolMode
        )

        Require18 = (
            '禁止 未滿十八歲進入' in OriScreen
        )

        Log.showValue(
            Log.Level.DEBUG,
            '禁止未滿十八歲進入',
            Require18
        )

        p = re.compile('登入次數 [\d]+ 次以上')
        r = p.search(OriScreen)
        if r is not None:
            RequireLoginTime = r.group(0).split(' ')[1]
            RequireLoginTime = int(RequireLoginTime)
        else:
            RequireLoginTime = 0
        Log.showValue(
            Log.Level.DEBUG,
            '發文限制登入次數',
            RequireLoginTime
        )

        p = re.compile('退文篇數 [\d]+ 篇以下')
        r = p.search(OriScreen)
        if r is not None:
            RequireIllegalPost = r.group(0).split(' ')[1]
            RequireIllegalPost = int(RequireIllegalPost)
        else:
            RequireIllegalPost = 0
        Log.showValue(
            Log.Level.DEBUG,
            '發文限制退文篇數',
            RequireIllegalPost
        )

        BoardInfo = DataType.BoardInfo(
            Board,
            OnlineUser,
            ChineseDes,
            Moderators,
            OpenState,
            IntoTopTenWhenHide,
            NonBoardMembersPost,
            ReplyPost,
            SelfDelPost,
            PushPost,
            BooPost,
            FastPush,
            MinInterval,
            PushRecordIP,
            PushAligned,
            ModeratorCanDelIllegalContent,
            TranPostAutoRecordedAndRequirePostPermissions,
            CoolMode,
            Require18,
            RequireLoginTime,
            RequireIllegalPost,
        )
        return BoardInfo


if __name__ == '__main__':

    print('PTT Library v ' + Version)
    print('Developed by PTT CodingMan')
