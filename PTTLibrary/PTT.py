import sys
import time
import re
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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

Version = Config.Version

ErrorCode = ErrorCode.ErrorCode()
Language = i18n.Language
ConnectMode = ConnectCore.ConnectMode
LogLevel = Log.Level
Command = ConnectCore.Command
PushType = DataType.PushType
PostSearchType = DataType.PostSearchType


class Library(Synchronize.SynchronizeAllMethod):
    def __init__(self,
                 Language: int=0,
                 ConnectMode: int=0,
                 LogLevel: int=0,
                 ScreenTimeOut: int=0,
                 ScreenLongTimeOut: int=0,
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

    def _login(self, ID: str, Password: str, KickOtherLogin: bool=False):

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
                return 'y' + ConnectCore.Command.Enter
            return 'n' + ConnectCore.Command.Enter

        if len(Password) > 8:
            Password = Password[:8]

        ID = ID.strip()
        Password = Password.strip()

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
                Response='y' + ConnectCore.Command.Enter,
            ),
            ConnectCore.TargetUnit(
                i18n.MailBoxFull,
                '您保存信件數目',
                Response=ConnectCore.Command.GoMainMenu,
            ),
            ConnectCore.TargetUnit(
                i18n.PostNotFinish,
                '有一篇文章尚未完成',
                Response='q' + ConnectCore.Command.Enter,
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
                Response=ConnectCore.Command.GoMainMenu,
            ),
            ConnectCore.TargetUnit(
                i18n.SigningUpdate,
                '正在更新與同步線上使用者及好友名單',
            ),
        ]

        CmdList = []
        CmdList.append(ID)
        CmdList.append(ConnectCore.Command.Enter)
        CmdList.append(Password)
        CmdList.append(ConnectCore.Command.Enter)

        Cmd = ''.join(CmdList)

        index = self._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=Config.ScreenLongTimeOut
        )
        if index != 0:
            raise ConnectCore.LoginError()

        self._Login = True
        return ErrorCode.Success

    def login(self, ID: str, Password: str, KickOtherLogin: bool=False):
        return self._login(ID, Password, KickOtherLogin=KickOtherLogin)

    def logout(self):

        if not self._Login:
            return ErrorCode.Success
        CmdList = []
        CmdList.append(ConnectCore.Command.GoMainMenu)
        CmdList.append('g')
        CmdList.append(ConnectCore.Command.Enter)
        CmdList.append('y')
        CmdList.append(ConnectCore.Command.Enter)
        CmdList.append(ConnectCore.Command.Enter)

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
        return ErrorCode.Success

    def log(self, Msg):
        Log.log(Log.Level.INFO, Msg)

    def getTime(self) -> str:

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CmdList = []
        CmdList.append(ConnectCore.Command.GoMainMenu)
        CmdList.append('P')
        CmdList.append(ConnectCore.Command.Right)
        CmdList.append(ConnectCore.Command.Left)

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

    def getPost(self, Board: str,
                PostAID: str=None,
                PostIndex: int=0,
                SearchType: int=0,
                SearchCondition: str=None):

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

        return self._getPost(Board,
                             PostAID,
                             PostIndex,
                             SearchType,
                             SearchCondition)

    def _getPost(self, Board: str,
                 PostAID: str=None,
                 PostIndex: int=0,
                 SearchType: int=0,
                 SearchCondition: str=None):

        if not self._Login:
            raise Exceptions.RequireLogin(i18n.RequireLogin)

        CmdList = []
        CmdList.append(ConnectCore.Command.GoMainMenu)
        CmdList.append('qs')
        CmdList.append(Board)
        CmdList.append(ConnectCore.Command.Enter)
        CmdList.append(ConnectCore.Command.Ctrl_C * 2)

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
                CmdList.append(ConnectCore.Command.Enter)

            CmdList.append(str(PostIndex))

        CmdList.append(ConnectCore.Command.Enter)
        CmdList.append(ConnectCore.Command.QueryPost)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                [
                    i18n.CatchPost,
                    i18n.Success,
                ],
                Screens.Target.QueryPost,
                BreakDetect=True,
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

        if index < 0:
            Screens.show(self._ConnectCore.getScreenQueue())
            raise Exceptions.UnknowError(i18n.UnknowError)

        OriScreen = self._ConnectCore.getScreenQueue()[-1]
        # print(self._ConnectCore.getScreenQueue()[-1])

        if index == 1:
            # 文章被刪除
            Log.log(Log.Level.DEBUG, i18n.PostDeled)
            PostDelStatus = 0

            for line in OriScreen.split('\n'):
                if (line.startswith(DataType.Cursor.NewType) or
                   line.startswith(DataType.Cursor.OldType)):
                    # print(f'line: {line}')

                    pattern = re.compile('[\d]+\/[\d]+')
                    PatternResult = pattern.search(line)
                    ListDate = PatternResult.group(0)

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

            return DataType.PostInfo(Board=Board,
                                     Author=PostAuthor,
                                     ListDate=ListDate,
                                     DeleteStatus=PostDelStatus)

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
                if (line.startswith(DataType.Cursor.NewType) or
                   line.startswith(DataType.Cursor.OldType)):

                    pattern = re.compile('[\d]+\/[\d]+')
                    PatternResult = pattern.search(line)
                    ListDate = PatternResult.group(0)

            Log.showValue(Log.Level.DEBUG, 'PostAID', PostAID)
            Log.showValue(Log.Level.DEBUG, 'PostWeb', PostWeb)
            Log.showValue(Log.Level.DEBUG, 'PostMoney', PostMoney)
            Log.showValue(Log.Level.DEBUG, 'ListDate', ListDate)

        Cmd = ConnectCore.Command.Enter * 2
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
        PostAuthorPattern = re.compile('作者  (.+) 看板  ' + Board)
        PostTitle = None
        PostTitlePattern = re.compile('標題  (.+)')
        PostDate = None
        PostDatePattern = re.compile('時間  (.+)')
        PostContent = []

        LineFromTopattern = re.compile('[\d]+~[\d]+')
        NewIPPattern = re.compile('\([\d]+\.[\d]+\.[\d]+\.[\d]+\)')
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

            # print(LastScreen)

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

                PatternResult = PostAuthorPattern.search(LastScreen)
                PostAuthor = PatternResult.group(0)
                PostAuthor = PostAuthor.replace('看板  ' + Board, '')
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

            if (not ContentFinish and
               Screens.isMatch(LastScreen, Screens.Target.PostIP)):
                ContentFinish = True

                pattern = re.compile(
                    '發信站: 批踢踢實業坊\(ptt.cc\), 來自: [\d]+\.[\d]+\.[\d]+\.[\d]+'
                )
                PatternResult = pattern.search(LastScreen)
                IP = PatternResult.group(0)[25:]

                Log.showValue(Log.Level.DEBUG, 'IP', IP)

                PostContent = '\n'.join(PostContent)
                PostContent = PostContent[
                    :PostContent.find('※ 發信站: 批踢踢實業坊(ptt.cc)')
                ].strip()

                Log.showValue(Log.Level.DEBUG, 'PostContent', PostContent)

                LastScreen = LastScreen[
                    LastScreen.find('發信站: 批踢踢實業坊(ptt.cc)'):
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
                    if line.startswith('※ 編輯'):
                        if IP in line:
                            continue
                        PatternResult = NewIPPattern.search(line)
                        IP = PatternResult.group(0)[1:-1]
                        Log.showValue(
                            Log.Level.DEBUG,
                            [
                                i18n.Update,
                                'IP'
                            ],
                            IP
                        )
                    elif line.startswith('推'):
                        PushType = DataType.PushType.Push
                    elif line.startswith('噓'):
                        PushType = DataType.PushType.Boo
                    elif line.startswith('→'):
                        PushType = DataType.PushType.Arrow
                    else:
                        pass

                    if PushType != 0:
                        Result = PushAuthorPattern.search(line)
                        PushAuthor = Result.group(0)[2:-1]
                        Log.showValue(Log.Level.DEBUG, [
                                i18n.Push,
                                i18n.ID,
                            ],
                            PushAuthor
                        )

                        Result = PushDatePattern.search(line)
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
                        PushContent = PushContent[2:].strip()

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
                Cmd = ConnectCore.Command.Down
            elif ContentFinish:
                Cmd = ConnectCore.Command.Right
            else:
                Cmd = ConnectCore.Command.Down

        # res = requests.get(
        #     url=PostWeb,
        #     cookies={'over18': '1'},
        #     timeout=3
        # )

        # PageSource = res.text

        # UnitList = Util.findValues(
        #     PageSource,
        #     '<span class="article-meta-value">',
        #     '</span>'
        # )

        # PostAuthor = UnitList[0]
        # PostTitle = UnitList[2]
        # PostDate = UnitList[3]

        # UnitList = Util.findValues(
        #     PageSource,
        #     PostDate + '</span></div>',
        #     '<span class="f2">※ 發信站'
        # )
        # Content = UnitList[0]

        # ResultList = re.findall(r'<a(.+)</a>', Content)

        # for a in ResultList:
        #     HTML = '<a' + a + '</a>'
        #     Log.showValue(Log.Level.DEBUG, 'HTML', HTML)

        #     UrlPattern = re.compile(
        #         '(https|http):[\S]+<'
        #     )
        #     UrlPatternResult = UrlPattern.search(HTML)
        #     if UrlPatternResult is None:
        #         Content = Content.replace(HTML, '')
        #         continue
        #     URL = UrlPatternResult.group(0)[:-1]

        #     Log.showValue(Log.Level.DEBUG, 'URL', URL)
        #     Content = Content.replace(HTML, URL)

        # ResultList = re.findall(r'<(.+)>', Content)

        # for h in ResultList:
        #     HTML = '<' + h + '>'
        #     Log.showValue(Log.Level.DEBUG, 'HTML', HTML)
        #     Content = Content.replace(HTML, '')

        # Content = Content.strip()

        # Log.showValue(Log.Level.DEBUG, 'PostAuthor', PostAuthor)
        # Log.showValue(Log.Level.DEBUG, 'PostTitle', PostTitle)
        # Log.showValue(Log.Level.DEBUG, 'PostDate', PostDate)
        # Log.showValue(Log.Level.DEBUG, 'PostContent', PostContent)
        # Log.showValue(Log.Level.DEBUG, 'IP', IP)

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

    def post(self,
             Board: str,
             Title: str,
             Content: str,
             PostType: int,
             SignType: int):

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
        CmdList.append(ConnectCore.Command.GoMainMenu)
        CmdList.append('qs')
        CmdList.append(Board)
        CmdList.append(ConnectCore.Command.Enter)
        CmdList.append(ConnectCore.Command.Ctrl_C * 2)
        CmdList.append(ConnectCore.Command.Ctrl_P)

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
        CmdList.append(ConnectCore.Command.Enter)
        CmdList.append(str(Title))
        CmdList.append(ConnectCore.Command.Enter)
        CmdList.append(str(Content))
        CmdList.append(ConnectCore.Command.Ctrl_X)
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
                Response='s' + ConnectCore.Command.Enter,
            ),
            ConnectCore.TargetUnit(
                i18n.SelectSignature,
                'x=隨機',
                Response=str(SignType) + ConnectCore.Command.Enter,
            ),
        ]
        index = self._ConnectCore.send(Cmd, TargetList)

        return ErrorCode.Success

if __name__ == '__main__':

    print('PTT Library v ' + Version)
    print('Developed by PTT CodingMan')
