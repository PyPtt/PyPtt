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
except ModuleNotFoundError:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import ConnectCore
    from . import ErrorCode
    from . import Log
    from . import Synchronize

Version = Config.Version

ErrorCode = ErrorCode.ErrorCode()
Language = i18n.Language
ConnectMode = ConnectCore.ConnectMode
LogLevel = Log.Level
Command = ConnectCore.Command


class Library(Synchronize.SynchronizeAllMethod):
    def __init__(self,
                 Language: int=0,
                 ConnectMode: int=0,
                 LogLevel: int=0,
                 ):
        Config.load()

        if not isinstance(Language, int):
            raise TypeError('Language must be integer')
        if not isinstance(ConnectMode, int):
            raise TypeError('ConnectMode must be integer')
        if not isinstance(LogLevel, int):
            raise TypeError('LogLevel must be integer')

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

    def login(self, ID: str, Password: str, KickOtherLogin: bool=False):

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
                ConnectCore.ScreenTarget.MainMenu,
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
        CmdList.append(',')
        CmdList.append(ConnectCore.Command.Enter)
        CmdList.append(Password)
        CmdList.append(ConnectCore.Command.Enter)

        Cmd = ''.join(CmdList)

        index = self._ConnectCore.send(Cmd, TargetList)
        if index != 0:
            raise ConnectCore.LoginError()
        return ErrorCode.Success

    def logout(self):

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

        index = self._ConnectCore.send(Cmd, TargetList)
        self._ConnectCore.close()
        return ErrorCode.Success

    def log(self, Msg):
        Log.log(Log.Level.INFO, Msg)

    def getTime(self) -> str:

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
                ConnectCore.ScreenTarget.MainMenu,
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
           not Util.checkRange(DataType.SearchType, SearchType)):
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
        CmdList = []
        CmdList.append(ConnectCore.Command.GoMainMenu)
        CmdList.append('qs')
        CmdList.append(Board)
        CmdList.append(ConnectCore.Command.Enter)
        CmdList.append(ConnectCore.Command.Ctrl_C * 2)

        if SearchCondition is not None:
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
                ConnectCore.ScreenTarget.QueryPost,
                BreakDetect=True,
            ),
            ConnectCore.TargetUnit(
                [
                    i18n.CatchPost,
                    i18n.Success,
                ],
                ConnectCore.ScreenTarget.InBoard,
                BreakDetect=True,
            ),
        ]

        index = self._ConnectCore.send(Cmd, TargetList)

        if index < 0:
            return None

        OriScreen = self._ConnectCore.getScreenQueue()[-1]
        print(self._ConnectCore.getScreenQueue()[-1])

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

            Log.showValue(Log.Level.INFO, 'ListDate', ListDate)
            Log.showValue(Log.Level.INFO, 'PostAuthor', PostAuthor)
            Log.showValue(Log.Level.INFO, 'PostDelStatus', PostDelStatus)

            return DataType.PostInfo(Board=Board,
                                     Author=PostAuthor,
                                     ListDate=ListDate,
                                     DeleteStatus=PostDelStatus)

        elif index == 0:

            pattern = re.compile('#[\w]+')
            PatternResult = pattern.search(OriScreen)
            AID = PatternResult.group(0)[1:]

            pattern = re.compile('https:[\S]+html')
            PatternResult = pattern.search(OriScreen)
            PostWeb = PatternResult.group(0)

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

            Log.showValue(Log.Level.INFO, 'AID', AID)
            Log.showValue(Log.Level.INFO, 'PostWeb', PostWeb)
            Log.showValue(Log.Level.INFO, 'PoPostMoneystWeb', PostMoney)
            Log.showValue(Log.Level.INFO, 'ListDate', ListDate)

        res = requests.get(
            url=PostWeb,
            cookies={'over18': '1'},
            timeout=3
        )

        PageSource = res.text

        UnitList = Util.findValues(
            PageSource,
            '<span class="article-meta-value">',
            '</span>'
        )

        PostAuthor = UnitList[0]
        PostTitle = UnitList[2]
        PostDate = UnitList[3]

        UnitList = Util.findValues(
            PageSource,
            PostDate + '</span></div>',
            '<span class="f2">※ 發信站'
        )
        # print('\n'.join(UnitList))
        Content = UnitList[0]

        pattern = re.compile('<a(..)+a>')
        while pattern.search(Content) is not None:
            PatternResult = pattern.search(Content)
            HTML = PatternResult.group(0)

            UrlPattern = re.compile(
                '(https|http):[\S]+(html|htm|jpg|png|jpeg)'
            )
            UrlPatternResult = UrlPattern.search(HTML)
            URL = UrlPatternResult.group(0)
            Content = Content.replace(HTML, URL)

        pattern = re.compile('<d(..)+v>')
        while pattern.search(Content) is not None:
            PatternResult = pattern.search(Content)
            HTML = PatternResult.group(0)

            Content = Content.replace(HTML, '')

        UnitList = Util.findValues(
            Content,
            '<',
            '>'
        )

        # print('\n'.join(UnitList))

        for Element in UnitList:
            Remove = False
            if 'div' in Element:
                Remove = True
            elif 'span' in Element:
                Remove = True
            elif 'src=' in Element:
                Remove = True
            elif 'class' in Element:
                Remove = True
            
            if Remove:
                Content = Content.replace('<' + Element + '>', '')
        Content = Content.strip()

        Log.showValue(Log.Level.INFO, 'PostAuthor', PostAuthor)
        Log.showValue(Log.Level.INFO, 'PostTitle', PostTitle)
        Log.showValue(Log.Level.INFO, 'PostDate', PostDate)
        Log.showValue(Log.Level.INFO, 'Content', Content)

        
        
if __name__ == '__main__':

    print('PTT Library v ' + Version)
    print('Developed by PTT CodingMan')
