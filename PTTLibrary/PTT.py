import sys
import time
import re
import progressbar
# import requests
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
    import DataType
    import Config
    import Util
    import i18n
    import ConnectCore
    import ErrorCode
    import Log
    import Synchronize
    import Screens
    import Exceptions
    import Command
except ModuleNotFoundError:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import ConnectCore
    from . import ErrorCode
    from . import Log
    from . import Synchronize
    from . import Screens
    from . import Exceptions
    from . import Command


Version = Config.Version

ErrorCode = ErrorCode.ErrorCode()
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


class Library(Synchronize.SynchronizeAllMethod):
    def __init__(
        self,
        Language: int = 0,
        ConnectMode: int = 0,
        LogLevel: int = 0,
        ScreenTimeOut: int = 0,
        ScreenLongTimeOut: int = 0,
    ):
        print(f'PTT Library v {Version}')
        print('Developed by PTT CodingMan')
        self._Login = False

        Config.load()

        if not isinstance(Language, int):
            raise TypeError('Language must be integer')
        if not isinstance(ConnectMode, int):
            raise TypeError('ConnectMode must be integer')
        if not isinstance(LogLevel, int):
            raise TypeError('LogLevel must be integer')
        if not isinstance(ScreenTimeOut, int):
            raise TypeError('ScreenTimeOut must be integer')
        if not isinstance(ScreenLongTimeOut, int):
            raise TypeError('ScreenLongTimeOut must be integer')

        if ScreenTimeOut != 0:
            Config.ScreenTimeOut = ScreenTimeOut
        if ScreenLongTimeOut != 0:
            Config.ScreenLongTimeOut = ScreenLongTimeOut

        if LogLevel == 0:
            LogLevel = Config.LogLevel
        elif not Util.checkRange(Log.Level, LogLevel):
            raise ValueError('Unknow LogLevel', LogLevel)

        else:
            Config.LogLevel = LogLevel

        if Language == 0:
            Language = Config.Language
        elif not Util.checkRange(i18n.Language, Language):
            raise ValueError('Unknow language', Language)
        else:
            Config.Language = Language
        i18n.load(Language)

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
            raise ValueError('Unknow ConnectMode', ConnectMode)
        else:
            Config.ConnectMode = ConnectMode
        self._ConnectCore = ConnectCore.API(ConnectMode)

        Log.showValue(Log.Level.INFO, [
            i18n.PTT,
            i18n.Library,
            ' v ' + Version,
        ],
            i18n.Init
        )

    def getVersion(self) -> str:
        return Config.Version

    def _login(
        self,
        ID: str,
        Password: str,
        KickOtherLogin: bool = False
    ):

        if self._Login:
            self.logout()

        if not isinstance(ID, str):
            raise TypeError(Log.merge([
                i18n.ID,
                i18n.MustBe,
                i18n.String
            ]))
        if not isinstance(Password, str):
            raise TypeError(Log.merge([
                i18n.Password,
                i18n.MustBe,
                i18n.String
            ]))
        if not isinstance(KickOtherLogin, bool):
            raise TypeError(Log.merge([
                'KickOtherLogin',
                i18n.MustBe,
                i18n.Boolean
            ]))

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
                i18n.LoginSuccess,
                Screens.Target.MainMenu,
                BreakDetect=True
            ),
            ConnectCore.TargetUnit(
                i18n.ErrorIDPW,
                '密碼不對或無此帳號',
                BreakDetect=True
            ),
            ConnectCore.TargetUnit(
                i18n.ErrorIDPW,
                '密碼不對或無此帳號',
                BreakDetect=True
            ),
            ConnectCore.TargetUnit(
                i18n.LoginTooOften,
                '登入太頻繁',
                BreakDetect=True,
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
                Response=Command.GoMainMenu,
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
            Refresh=False
        )
        if index != 0:
            raise Exceptions.LoginError()

        self._Login = True

    def login(
        self,
        ID: str,
        Password: str,
        KickOtherLogin: bool = False
    ):
        return self._login(ID, Password, KickOtherLogin=KickOtherLogin)

    def logout(self):

        if not self._Login:
            return ErrorCode.Success
        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('g')
        CmdList.append(Command.Enter)
        CmdList.append('y')
        CmdList.append(Command.Enter)
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
        self._ConnectCore.send(Cmd, TargetList)
        self._ConnectCore.close()
        self._Login = False

        Log.showValue(
            Log.Level.INFO,
            i18n.Logout,
            i18n.Done
        )

    def log(self, Msg):
        Log.log(Log.Level.INFO, Msg)

    def getTime(self) -> str:

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('P')
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

        pattern = re.compile('[\d]+:[\d][\d]')
        Result = pattern.search(OriScreen)

        if Result is not None:
            return Result.group(0)
        return None

    def getPost(
        self,
        Board: str,
        PostAID: str = None,
        PostIndex: int = 0,
        SearchType: int = 0,
        SearchCondition: str = None
    ):

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if not isinstance(Board, str):
            raise TypeError(Log.merge([
                'Board',
                i18n.MustBe,
                i18n.String
            ]))
        if not isinstance(PostAID, str) and PostAID is not None:
            raise TypeError(Log.merge([
                'PostAID',
                i18n.MustBe,
                i18n.String
            ]))
        if not isinstance(PostIndex, int):
            raise TypeError(Log.merge([
                'PostIndex',
                i18n.MustBe,
                i18n.Integer
            ]))

        if not isinstance(SearchType, int):
            raise TypeError(Log.merge([
                'SearchType',
                i18n.MustBe,
                i18n.Integer
            ]))
        if (not isinstance(SearchCondition, str) and
                SearchCondition is not None):
            raise TypeError(Log.merge([
                'SearchCondition',
                i18n.MustBe,
                i18n.String
            ]))

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

        if (SearchType != 0 and
                not Util.checkRange(DataType.PostSearchType, SearchType)):
            raise ValueError(Log.merge([
                'SearchType',
                i18n.ErrorParameter,
            ]))

        if SearchCondition is not None and SearchType == 0:
            raise ValueError(Log.merge([
                'SearchType',
                i18n.ErrorParameter,
            ]))

        if PostAID is not None and SearchCondition is not None:
            raise ValueError(Log.merge([
                'PostAID',
                'SearchCondition',
                i18n.ErrorParameter,
                i18n.BothInput,
            ]))

        if PostIndex > 0:
            NewestIndex = self._getNewestIndex(
                DataType.IndexType.Board,
                Board=Board,
                SearchType=SearchType,
                SearchCondition=SearchCondition
            )

            if PostIndex > NewestIndex:
                raise ValueError(Log.merge([
                    'PostIndex',
                    i18n.ErrorParameter,
                    i18n.OutOfRange,
                ]))
        return self._getPost(
            Board,
            PostAID,
            PostIndex,
            SearchType,
            SearchCondition
        )

    def _getPost(
        self,
        Board: str,
        PostAID: str = None,
        PostIndex: int = 0,
        SearchType: int = 0,
        SearchCondition: str = None
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
                    i18n.CatchPost,
                    i18n.Success,
                ],
                Screens.Target.InBoard,
                BreakDetect=True,
                LogLevel=Log.Level.DEBUG
            ),
        ]

        index = self._ConnectCore.send(Cmd, TargetList)
        OriScreen = self._ConnectCore.getScreenQueue()[-1]
        if index < 0:
            raise Exceptions.UnknowError(OriScreen)

        if index == 1:
            # 文章被刪除
            Log.log(Log.Level.DEBUG, i18n.PostDeled)
            PostDelStatus = 0

            for line in OriScreen.split('\n'):
                if (line.startswith(DataType.Cursor.New) or
                        line.startswith(DataType.Cursor.Old)):
                    # print(f'line: {line}')

                    pattern = re.compile('[\d]+\/[\d]+')
                    PatternResult = pattern.search(line)
                    ListDate = PatternResult.group(0)
                    ListDate = ListDate[-5:]

                    pattern = re.compile('\[[\w]+\]')
                    PatternResult = pattern.search(line)
                    if PatternResult is not None:
                        PostDelStatus = DataType.PostDeleteStatus.ByAuthor
                    else:
                        pattern = re.compile('<[\w]+>')
                        PatternResult = pattern.search(line)
                        PostDelStatus = DataType.PostDeleteStatus.ByModerator

                    PostAuthor = PatternResult.group(0)[1:-1]
                    break

            Log.showValue(Log.Level.DEBUG, 'ListDate', ListDate)
            Log.showValue(Log.Level.DEBUG, 'PostAuthor', PostAuthor)
            Log.showValue(Log.Level.DEBUG, 'PostDelStatus', PostDelStatus)

            return DataType.PostInfo(
                Board=Board,
                Author=PostAuthor,
                ListDate=ListDate,
                DeleteStatus=PostDelStatus
            )

        elif index == 0:

            pattern = re.compile('#[\w]+')
            PatternResult = pattern.search(OriScreen)
            PostAID = PatternResult.group(0)[1:]

            pattern = re.compile('文章網址: https:[\S]+html')
            PatternResult = pattern.search(OriScreen)
            PostWeb = PatternResult.group(0)[6:]

            pattern = re.compile('這一篇文章值 [\d]+ Ptt幣')
            PatternResult = pattern.search(OriScreen)
            if PatternResult is None:
                # 特殊文章無價格
                PostMoney = -1
            else:
                PostMoney = PatternResult.group(0)[7:]
                PostMoney = PostMoney[:PostMoney.find(' ')]
                PostMoney = int(PostMoney)

            for line in OriScreen.split('\n'):
                if (line.startswith(DataType.Cursor.New) or
                        line.startswith(DataType.Cursor.Old)):

                    pattern = re.compile('[\d]+\/[\d]+')
                    PatternResult = pattern.search(line)
                    ListDate = PatternResult.group(0)
                    ListDate = ListDate[-5:]

            Log.showValue(Log.Level.DEBUG, 'PostAID', PostAID)
            Log.showValue(Log.Level.DEBUG, 'PostWeb', PostWeb)
            Log.showValue(Log.Level.DEBUG, 'PostMoney', PostMoney)
            Log.showValue(Log.Level.DEBUG, 'ListDate', ListDate)

        Cmd = Command.Enter * 2
        TargetList = [
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
        ]

        PostAuthor = None
        PostAuthorPattern_New = re.compile('作者  (.+) 看板  ' + Board)
        PostAuthorPattern_Old = re.compile('作者  (.+)')
        PostTitle = None
        PostTitlePattern = re.compile('標題  (.+)')
        PostDate = None
        PostDatePattern = re.compile('時間  (.+)')
        PostContent = []

        LineFromTopattern = re.compile('[\d]+~[\d]+')
        NewIPPattern_New = re.compile('\([\d]+\.[\d]+\.[\d]+\.[\d]+\)')
        NewIPPattern_Old = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')
        PushAuthorPattern = re.compile('[推|噓|→] [\w]+:')
        PushDatePattern = re.compile('[\d]+/[\d]+ [\d]+:[\d]+')
        PushIPPattern = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')

        PushList = []

        HasControlCode = False
        ControlCodeMode = False
        ContentFinish = False
        index = -1
        FirstPage = True
        while True:
            index = self._ConnectCore.send(Cmd, TargetList)
            LastScreen = self._ConnectCore.getScreenQueue()[-1]
            Lines = LastScreen.split('\n')
            LastLine = Lines[-1]
            Lines.pop()
            LastScreen = '\n'.join(Lines)

            PatternResult = LineFromTopattern.search(LastLine)
            if PatternResult is None:
                ControlCodeMode = True
                HasControlCode = True
            else:
                LastReadLineTemp = int(PatternResult.group(0).split('~')[1])
                if ControlCodeMode:
                    LastReadLine = LastReadLineTemp - 1
                ControlCodeMode = False

            if FirstPage:

                if (Screens.isMatch(
                    LastScreen, Screens.Target.Vote_Type1
                ) or Screens.isMatch(
                    LastScreen, Screens.Target.Vote_Type2
                )):
                    Log.log(
                        Log.Level.DEBUG, [
                            i18n.VotePost,
                            i18n.DoNothing,
                        ]
                    )
                    return None

                PatternResult = PostAuthorPattern_New.search(LastScreen)
                if PatternResult is not None:
                    PostAuthor = PatternResult.group(0)
                    PostAuthor = PostAuthor.replace('看板  ' + Board, '')
                else:
                    PatternResult = PostAuthorPattern_Old.search(LastScreen)
                    if PatternResult is None:
                        Log.log(
                            Log.Level.DEBUG, [
                                i18n.SubstandardPost,
                                i18n.DoNothing,
                            ]
                        )
                        return None
                    PostAuthor = PatternResult.group(0)
                    PostAuthor = PostAuthor.replace('站內  ' + Board, '')
                PostAuthor = PostAuthor[4:].strip()

                Log.showValue(Log.Level.DEBUG, i18n.Author, PostAuthor)

                PatternResult = PostTitlePattern.search(LastScreen)
                PostTitle = PatternResult.group(0)
                PostTitle = PostTitle[4:].strip()

                Log.showValue(Log.Level.DEBUG, i18n.Title, PostTitle)

                PatternResult = PostDatePattern.search(LastScreen)
                PostDate = PatternResult.group(0)
                PostDate = PostDate[4:].strip()

                Log.showValue(Log.Level.DEBUG, i18n.Date, PostDate)

                PostContentTemp = LastScreen
                StartTarget = '───────────────────────────────────────'
                PostContentTemp = PostContentTemp[
                    PostContentTemp.find(StartTarget) + len(StartTarget):
                ]

                PostContent.append(PostContentTemp)
                if not ControlCodeMode:
                    LastReadLine = LastReadLineTemp
            else:
                if not ControlCodeMode:
                    GetLine = LastReadLineTemp - LastReadLine
                    if GetLine > 0:
                        NewContentPart = '\n'.join(Lines[-GetLine:])
                    else:
                        NewContentPart = '\n'.join(Lines)
                else:
                    NewContentPart = Lines[-1]
                Log.showValue(
                    Log.Level.DEBUG,
                    'NewContentPart',
                    NewContentPart
                )

                if not ContentFinish:
                    PostContent.append(NewContentPart)
                else:
                    LastScreen = NewContentPart

            if (not ContentFinish and (
                Screens.isMatch(
                    LastScreen, Screens.Target.PostIP_New
                ) or
                Screens.isMatch(
                    LastScreen, Screens.Target.PostIP_Old
                ) or
                Screens.isMatch(
                    LastScreen, Screens.Target.Edit
                )
            )):
                ContentFinish = True

                pattern = re.compile(
                    '發信站: 批踢踢實業坊\(ptt.cc\), 來自: [\d]+\.[\d]+\.[\d]+\.[\d]+'
                )
                PatternResult = pattern.search(LastScreen)
                if PatternResult is not None:
                    IP = PatternResult.group(0)[25:]
                else:
                    pattern = re.compile(
                        '◆ From: [\d]+\.[\d]+\.[\d]+\.[\d]+'
                    )
                    PatternResult = pattern.search(LastScreen)
                    if PatternResult is not None:
                        IP = PatternResult.group(0)[8:]
                    else:
                        PatternResult = NewIPPattern_New.search(LastScreen)
                        if PatternResult is not None:
                            IP = PatternResult.group(0)[1:-1]
                        else:
                            PatternResult = NewIPPattern_Old.search(LastScreen)
                            IP = PatternResult.group(0)
                Log.showValue(Log.Level.DEBUG, 'IP', IP)

                PostContent = '\n'.join(PostContent)
                PostContent = PostContent[
                    :PostContent.rfind('※')
                ].strip()

                Log.showValue(Log.Level.DEBUG, 'PostContent', PostContent)

                LastScreen = LastScreen[
                    LastScreen.rfind('※'):
                ]

            if ContentFinish:
                Lines = LastScreen.split('\n')
                for line in Lines:
                    line = line.strip()

                    Log.showValue(Log.Level.DEBUG, [
                        'line'
                    ],
                        line
                    )

                    PushType = 0
                    # Log.showValue(
                    #     Log.Level.INFO,
                    #     'line',
                    #     line
                    # )
                    if line.startswith('※ 編輯'):
                        if IP in line:
                            continue
                        PatternResult = NewIPPattern_New.search(line)
                        if PatternResult is not None:
                            IP = PatternResult.group(0)[1:-1]
                        else:
                            PatternResult = NewIPPattern_Old.search(line)
                            IP = PatternResult.group(0)
                        Log.showValue(
                            Log.Level.DEBUG,
                            [
                                i18n.Update,
                                'IP'
                            ],
                            IP
                        )
                    elif line.startswith('推 '):
                        PushType = DataType.PushType.Push
                    elif line.startswith('噓 '):
                        PushType = DataType.PushType.Boo
                    elif line.startswith('→ '):
                        PushType = DataType.PushType.Arrow
                    else:
                        pass

                    if PushType != 0:
                        # print(line)

                        Result = PushAuthorPattern.search(line)
                        PushAuthor = Result.group(0)[2:-1]
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
                        PushContent = PushContent.replace(PushDate, '')
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
            if index == 0:
                break

            FirstPage = False
            if not ControlCodeMode:
                LastReadLine = LastReadLineTemp

            if ControlCodeMode:
                Cmd = Command.Down
            elif ContentFinish:
                Cmd = Command.Right
            else:
                Cmd = Command.Down

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
            ControlCode=HasControlCode
        )
        return Post

    def _getNewestIndex(self,
                        IndexType: int,
                        Board: str = None,
                        SearchType: int = 0,
                        SearchCondition: str = None):
        if not Util.checkRange(DataType.IndexType, IndexType):
            raise ValueError('Unknow IndexType', IndexType)
        if not isinstance(Board, str):
            raise TypeError(Log.merge([
                'Board',
                i18n.MustBe,
                i18n.String
            ]))
        if not isinstance(SearchType, int):
            raise TypeError(Log.merge([
                'SearchType',
                i18n.MustBe,
                i18n.Integer
            ]))
        if (SearchCondition is not None and
                not isinstance(SearchCondition, str)):
            raise TypeError(Log.merge([
                'SearchCondition',
                i18n.MustBe,
                i18n.String
            ]))
        if (SearchType != 0 and
                not Util.checkRange(DataType.PostSearchType, SearchType)):
            raise ValueError('Unknow PostSearchType', PostSearchType)

        if IndexType == DataType.IndexType.Board:
            CmdList = []
            CmdList.append(Command.GoMainMenu)
            CmdList.append('qs')
            CmdList.append(Board)
            CmdList.append(Command.Enter)
            CmdList.append(Command.Ctrl_C * 2)
            CmdList.append(Command.Space)

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

            CmdList.append('0')
            CmdList.append(Command.Enter)
            CmdList.append('$')

            Cmd = ''.join(CmdList)

            TargetList = [
                ConnectCore.TargetUnit(
                    i18n.Success,
                    Screens.Target.InBoard,
                    BreakDetect=True,
                    LogLevel=Log.Level.DEBUG
                ),
            ]
            index = self._ConnectCore.send(Cmd, TargetList)
            if index < 0:
                Screens.show(self._ConnectCore.getScreenQueue())
                raise Exceptions.UnknowError(i18n.UnknowError)

            LastScreen = self._ConnectCore.getScreenQueue()[-1]
            AllIndex = re.findall(r' \d+ ', LastScreen)

            if len(AllIndex) == 0:
                Screens.show(self._ConnectCore.getScreenQueue())
                raise Exceptions.UnknowError(i18n.UnknowError)

            AllIndex = list(map(int, AllIndex))
            AllIndex.sort(reverse=True)

            NewestIndex = 0
            for IndexTemp in AllIndex:
                Continue = True
                for i in range(1, 6):
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

            return NewestIndex

    def getNewestIndex(
        self,
        IndexType: int,
        Board: str = None,
        SearchType: int = 0,
        SearchCondition: str = None
    ):

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        return self._getNewestIndex(
            IndexType,
            Board,
            SearchType,
            SearchCondition
        )

    def crawlBoard(
        self,
        PostHandler,
        Board: str,
        StartIndex: int = 0,
        EndIndex: int = 0,
        SearchType: int = 0,
        SearchCondition: str = None
    ):
        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if not isinstance(Board, str):
            raise TypeError(Log.merge([
                'Board',
                i18n.MustBe,
                i18n.String
            ]))
        if not isinstance(StartIndex, int):
            raise TypeError(Log.merge([
                'StartIndex',
                i18n.MustBe,
                i18n.Integer
            ]))
        if not isinstance(EndIndex, int):
            raise TypeError(Log.merge([
                'EndIndex',
                i18n.MustBe,
                i18n.Integer
            ]))
        if not isinstance(SearchType, int):
            raise TypeError(Log.merge([
                'SearchType',
                i18n.MustBe,
                i18n.Integer
            ]))
        if (SearchCondition is not None and
                not isinstance(SearchCondition, str)):
            raise TypeError(Log.merge([
                'SearchCondition',
                i18n.MustBe,
                i18n.String
            ]))

        if StartIndex < 1:
            raise ValueError(Log.merge([
                'StartIndex',
                i18n.ErrorParameter,
                i18n.OutOfRange,
            ]))

        if StartIndex < 1:
            raise ValueError(Log.merge([
                'StartIndex',
                i18n.ErrorParameter,
                i18n.OutOfRange,
            ]))

        if StartIndex > EndIndex:
            raise ValueError(Log.merge([
                'StartIndex',
                i18n.MustSmall,
                'EndIndex',
            ]))

        NewestIndex = self._getNewestIndex(
            DataType.IndexType.Board,
            Board=Board,
            SearchType=SearchType,
            SearchCondition=SearchCondition
        )

        if EndIndex > NewestIndex:
            raise ValueError(Log.merge([
                'EndIndex',
                i18n.ErrorParameter,
                i18n.OutOfRange,
            ]))

        ErrorPostList = []
        DelPostList = []
        if Config.LogLevel == Log.Level.INFO:
            PB = progressbar.ProgressBar(
                max_value=EndIndex - StartIndex + 1,
                redirect_stdout=True
            )
        for index in range(StartIndex, EndIndex + 1):
            Post = self._getPost(
                Board,
                PostIndex=index,
                SearchType=SearchType,
                SearchCondition=SearchCondition
            )
            if Config.LogLevel == Log.Level.INFO:
                PB.update(index - StartIndex)
            if Post is None:
                ErrorPostList.append(index)
                continue
            if Post.getDeleteStatus() != DataType.PostDeleteStatus.NotDeleted:
                DelPostList.append(index)
            PostHandler(Post)
        if Config.LogLevel == Log.Level.INFO:
            PB.finish()
        return ErrorPostList, DelPostList

    def post(
        self,
        Board: str,
        Title: str,
        Content: str,
        PostType: int,
        SignType: int
    ):

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if not isinstance(Board, str):
            raise TypeError(Log.merge([
                'Board',
                i18n.MustBe,
                i18n.String
            ]))

        if not isinstance(Title, str):
            raise TypeError(Log.merge([
                'Title',
                i18n.MustBe,
                i18n.String
            ]))

        if not isinstance(Content, str):
            raise TypeError(Log.merge([
                'Content',
                i18n.MustBe,
                i18n.String
            ]))

        if not isinstance(PostType, int):
            raise TypeError(Log.merge([
                'PostType',
                i18n.MustBe,
                i18n.Integer
            ]))

        if not isinstance(SignType, int):
            raise TypeError(Log.merge([
                'SignType',
                i18n.MustBe,
                i18n.Integer
            ]))

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

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
                Response=str(SignType) + Command.Enter,
            ),
        ]
        index = self._ConnectCore.send(Cmd, TargetList)

    def push(
        self,
        Board: str,
        PushType: int,
        PushContent: str,
        PostAID: str = None,
        PostIndex: int = 0
    ):

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if not isinstance(Board, str):
            raise TypeError(Log.merge([
                'Board',
                i18n.MustBe,
                i18n.String
            ]))
        if not isinstance(PushType, int):
            raise TypeError(Log.merge([
                'PushType',
                i18n.MustBe,
                i18n.Integer
            ]))
        if not isinstance(PushContent, str):
            raise TypeError(Log.merge([
                'PushContent',
                i18n.MustBe,
                i18n.String
            ]))
        if not isinstance(PostAID, str) and PostAID is not None:
            raise TypeError(Log.merge([
                'PostAID',
                i18n.MustBe,
                i18n.String
            ]))
        if not isinstance(PostIndex, int):
            raise TypeError(Log.merge([
                'PostIndex',
                i18n.MustBe,
                i18n.Integer
            ]))
        if len(Board) == 0:
            raise ValueError(Log.merge([
                i18n.Board,
                i18n.ErrorParameter,
                Board
            ]))
        if not Util.checkRange(DataType.PushType, PushType):
            raise ValueError('Unknow PushType', PushType)
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
        if PostIndex > 0:
            NewestIndex = self._getNewestIndex(
                DataType.IndexType.Board,
                Board=Board
            )

            if PostIndex > NewestIndex:
                raise ValueError(Log.merge([
                    'PostIndex',
                    i18n.ErrorParameter,
                    i18n.OutOfRange,
                ]))

        MaxPushLength = 33
        PushList = []

        TempStartIndex = 0
        TempEndIndex = TempStartIndex + 1

        while TempEndIndex <= len(PushContent):

            Temp = ''
            LastTemp = None
            while len(Temp.encode('big5-uao', 'ignore')) < MaxPushLength:
                Temp = PushContent[TempStartIndex:TempEndIndex]

                if not len(Temp.encode('big5-uao', 'ignore')) < MaxPushLength:
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
                Exceptions=Exceptions.Error(i18n.NoPermission)
            )
        ]

        index = self._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=Config.ScreenLongTimeOut,
            # Refresh=False
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
            TargetList,
            ScreenTimeout=Config.ScreenLongTimeOut
        )

    def _getUser(self, UserID):

        if not isinstance(UserID, str):
            raise TypeError(Log.merge([
                'UserID',
                i18n.MustBe,
                i18n.String
            ]))

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
            TargetList,
            ScreenTimeout=Config.ScreenLongTimeOut
        )
        OriScreen = self._ConnectCore.getScreenQueue()[-1]
        Log.showValue(
            Log.Level.DEBUG,
            'OriScreen',
            OriScreen
        )
        if index == 1:
            raise Exceptions.NoSuchUser(UserID)

        Data = Util.getSubStringList(OriScreen, '》', ['《', '\n'])
        if len(Data) != 10:
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
        IllegalPost = int(Temp[1])

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

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        return self._getUser(UserID)

    def throwWaterBall(self, TargetID, Content):

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if not isinstance(TargetID, str):
            raise TypeError(Log.merge([
                'TargetID',
                i18n.MustBe,
                i18n.String
            ]))

        if not isinstance(Content, str):
            raise TypeError(Log.merge([
                'Content',
                i18n.MustBe,
                i18n.String
            ]))

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

            time.sleep(3.2)

    def getWaterBall(self, OperateType):

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if not isinstance(OperateType, int):
            raise TypeError(Log.merge([
                'OperateType',
                i18n.MustBe,
                i18n.Integer
            ]))

        if not Util.checkRange(DataType.WaterBallOperateType, OperateType):
            raise ValueError('Unknow WaterBallOperateType', OperateType)

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
                BreakDetect=True
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

        LastReadLine = 0
        AddTailNextRound = False
        while True:
            index = self._ConnectCore.send(
                Cmd,
                TargetList,
                ScreenTimeout=Config.ScreenTimeOut
            )
            Log.showValue(
                Log.Level.DEBUG,
                'index',
                index
            )
            if index == 0:
                return None

            OriScreen = self._ConnectCore.getScreenQueue()[-1]

            # print(OriScreen)
            # print('=' * 50)
            ScreenTemp = OriScreen
            Log.showValue(
                Log.Level.DEBUG,
                'OriScreen',
                OriScreen
            )

            LastLine = ScreenTemp.split('\n')[-1]
            Log.showValue(
                Log.Level.DEBUG,
                'LastLine',
                LastLine
            )
            if LastLine.startswith('★'):
                continue
            ScreenTemp = '\n'.join(ScreenTemp.split('\n')[:-1])

            ScreenTemp = ScreenTemp.replace(
                ']\n', ']==PTTWaterBallNewLine==')
            ScreenTemp = ScreenTemp.replace('\n', '')
            ScreenTemp = ScreenTemp.replace(
                ']==PTTWaterBallNewLine==', ']\n')

            # print(ScreenTemp)
            # print('=' * 50)

            Lines = ScreenTemp.split('\n')
            PatternResult = LineFromTopattern.search(LastLine)
            LastReadLineTemp = int(PatternResult.group(0).split('~')[1])
            GetLine = LastReadLineTemp - LastReadLine

            # print(LastReadLine)
            # print(GetLine)
            # print('=' * 50)
            if GetLine > 0 and LastReadLine != 0:
                if AddTailNextRound:
                    Log.log(
                        Log.Level.DEBUG,
                        'Add Tail'
                    )
                    AddTailNextRound = False
                    NewContentPart = Lines[-(GetLine + 1):]
                else:
                    NewContentPart = Lines[-GetLine:]
            else:
                NewContentPart = Lines
            NewContentPart = [x.strip() for x in NewContentPart]

            # print('\n'.join(NewContentPart))

            for line in NewContentPart:
                # print(f'line =>{line}<')
                # print(len(line))
                if len(line) == 0:
                    break
                if (not line.startswith('To')) and (not line.startswith('★')):

                    Log.showValue(
                        Log.Level.DEBUG,
                        'Discard waterball',
                        line
                    )
                    AddTailNextRound = True
                    continue

                if not line.endswith(']'):
                    Log.showValue(
                        Log.Level.DEBUG,
                        'Discard waterball',
                        line
                    )
                    AddTailNextRound = True
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
                    Content = Content[:Content.rfind(Date) - 1].strip()
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
                    Content = Content[:Content.rfind(Date) - 1].strip()

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

            if index == 1:
                break
            # elif index == 2:
            #     pass

            Cmd = Command.Down
            LastReadLine = LastReadLineTemp

        return WaterBallList

    def getCallStatus(self):

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        return self._getCallStatus()

    def _getCallStatus(self):

        CmdList = []
        CmdList.append(Command.GoMainMenu)
        CmdList.append('P')
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
        ]

        index = self._ConnectCore.send(Cmd, TargetList)
        if index < 0:
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

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if not isinstance(inputCallStatus, int):
            raise TypeError('CallStatus must be integer')

        if not Util.checkRange(DataType.CallStatus, inputCallStatus):
            raise ValueError('Unknow CallStatus', inputCallStatus)

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

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        if not isinstance(ID, str):
            raise TypeError(Log.merge([
                'ID',
                i18n.MustBe,
                i18n.String
            ]))

        if not isinstance(Money, int):
            raise TypeError(Log.merge([
                'Money',
                i18n.MustBe,
                i18n.Integer
            ]))

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


if __name__ == '__main__':

    print('PTT Library v ' + Version)
    print('Developed by PTT CodingMan')
