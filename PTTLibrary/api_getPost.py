import re
try:
    from . import DataType
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Screens
    from . import Exceptions
    from . import Command
except ModuleNotFoundError:
    import DataType
    import i18n
    import ConnectCore
    import Log
    import Screens
    import Exceptions
    import Command


def getPost(
        api,
        Board: str,
        PostAID: str = None,
        PostIndex: int = 0,
        SearchType: int = 0,
        SearchCondition: str = None,
        Query: bool = False):

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
            Exceptions=Exceptions.NoSuchBoard(api.Config, Board)
        ),
    ]

    index = api._ConnectCore.send(Cmd, TargetList)
    OriScreen = api._ConnectCore.getScreenQueue()[-1]

    PostAuthor = None
    PostTitle = None
    if index < 0 or index == 1:
        # 文章被刪除
        Log.log(api.Config, Log.Level.DEBUG, i18n.PostDeleted)
        PostDelStatus = 0

        Log.showValue(
            api.Config,
            Log.Level.DEBUG,
            'OriScreen',
            OriScreen
        )

        CursorLine = [line for line in OriScreen.split(
            '\n') if line.startswith(api._Cursor)]

        if len(CursorLine) != 1:
            raise Exceptions.UnknownError(OriScreen)

        CursorLine = CursorLine[0]
        Log.showValue(
            api.Config,
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
            PostDelStatus = DataType.PostDeleteStatus.ByUnknown

        Log.showValue(api.Config, Log.Level.DEBUG, 'ListDate', ListDate)
        Log.showValue(api.Config, Log.Level.DEBUG,
                      'PostAuthor', PostAuthor)
        Log.showValue(api.Config, Log.Level.DEBUG,
                      'PostDelStatus', PostDelStatus)

        return DataType.PostInfo(
            board=Board,
            author=PostAuthor,
            list_date=ListDate,
            delete_status=PostDelStatus,
            format_check=True
        )

    elif index == 0:

        LockPost = False
        CursorLine = [line for line in OriScreen.split(
            '\n') if line.startswith(api._Cursor)][0]
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
        Log.showValue(api.Config, Log.Level.DEBUG,
                      'PostAuthor', PostAuthor)
        Log.showValue(api.Config, Log.Level.DEBUG, 'PostTitle', PostTitle)
        Log.showValue(api.Config, Log.Level.DEBUG, 'PostAID', PostAID)
        Log.showValue(api.Config, Log.Level.DEBUG, 'PostWeb', PostWeb)
        Log.showValue(api.Config, Log.Level.DEBUG, 'PostMoney', PostMoney)
        Log.showValue(api.Config, Log.Level.DEBUG, 'ListDate', ListDate)
        Log.showValue(api.Config, Log.Level.DEBUG,
                      'PushNumber', PushNumber)

        if LockPost:
            Post = DataType.PostInfo(
                board=Board,
                aid=PostAID,
                author=PostAuthor,
                title=PostTitle,
                web_url=PostWeb,
                money=PostMoney,
                list_date=ListDate,
                format_check=True,
                push_number=PushNumber,
                lock=True,
            )
            return Post

    if Query:
        Post = DataType.PostInfo(
            board=Board,
            aid=PostAID,
            author=PostAuthor,
            title=PostTitle,
            web_url=PostWeb,
            money=PostMoney,
            list_date=ListDate,
            format_check=True,
            push_number=PushNumber,
        )
        return Post

    api.Unconfirmed = False

    def isUnconfirmedHandler():
        api.Unconfirmed = True

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
    StopDict = dict()

    while True:
        index = api._ConnectCore.send(Cmd, TargetList)

        if index == 3 or index == 4:
            Post = DataType.PostInfo(
                board=Board,
                aid=PostAID,
                author=PostAuthor,
                # Date=PostDate,
                title=PostTitle,
                web_url=PostWeb,
                money=PostMoney,
                # Content=PostContent,
                # PushList=PushList,
                list_date=ListDate,
                control_code=HasControlCode,
                format_check=False,
                push_number=PushNumber,
                unconfirmed=api.Unconfirmed,
            )
            return Post

        LastScreen = api._ConnectCore.getScreenQueue()[-1]
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
            # print(LastScreen)
            # print(f'LastReadLineATemp [{LastReadLineATemp}]')
            # print(f'LastReadLineBTemp [{LastReadLineBTemp}]')
            # print(f'Dis [{23 - (LastReadLineBTemp - LastReadLineATemp)}]')
            # print(f'ContentStartJump {ContentStartJump}')
            # print(f'GetLineB {LastReadLineBTemp - LastReadLineB}')
            # print(f'GetLineA {LastReadLineATemp - LastReadLineA}')
            if not ControlCodeMode:

                if LastReadLineATemp in StopDict:
                    NewContentPart = '\n'.join(
                        Lines[-StopDict[LastReadLineATemp]:])
                else:
                    GetLineB = LastReadLineBTemp - LastReadLineB
                    if GetLineB > 0:
                        # print('Type 1')
                        # print(f'GetLineB [{GetLineB}]')
                        NewContentPart = '\n'.join(Lines[-GetLineB:])
                    else:
                        # 駐足現象，LastReadLineB跟上一次相比並沒有改變
                        if (LastReadLineBTemp + 1) not in StopDict:
                            StopDict[LastReadLineBTemp + 1] = 1
                        StopDict[LastReadLineBTemp + 1] += 1

                        GetLineA = LastReadLineATemp - LastReadLineA

                        if GetLineA > 0:
                            NewContentPart = '\n'.join(Lines[-GetLineA:])
                        else:
                            NewContentPart = '\n'.join(Lines)

            else:
                NewContentPart = Lines[-1]

            OriginPost.append(NewContentPart)
            Log.showValue(
                api.Config,
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

    # print(api.Unconfirmed)
    OriginPost = '\n'.join(OriginPost)
    # OriginPost = [line.strip() for line in OriginPost.split('\n')]
    # OriginPost = '\n'.join(OriginPost)

    Log.showValue(
        api.Config,
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
                    api.Config,
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
                api.Config,
                Log.Level.DEBUG,
                i18n.SubstandardPost,
                i18n.Author
            )
            Post = DataType.PostInfo(
                board=Board,
                aid=PostAID,
                author=PostAuthor,
                date=PostDate,
                title=PostTitle,
                web_url=PostWeb,
                money=PostMoney,
                content=PostContent,
                ip=IP,
                push_list=PushList,
                list_date=ListDate,
                control_code=HasControlCode,
                format_check=False,
                location=Location,
                push_number=PushNumber,
                origin_post=OriginPost,
                unconfirmed=api.Unconfirmed,
            )
            return Post
        PostAuthor = PatternResult.group(0)
        PostAuthor = PostAuthor[:PostAuthor.rfind(')') + 1]
    PostAuthor = PostAuthor[4:].strip()

    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        i18n.Author,
        PostAuthor
    )

    PostTitlePattern = re.compile('標題  (.+)')

    TitleLine = OriginPostLines[1]
    PatternResult = PostTitlePattern.search(TitleLine)
    if PatternResult is None:
        Log.showValue(
            api.Config,
            Log.Level.DEBUG,
            i18n.SubstandardPost,
            i18n.Title
        )
        Post = DataType.PostInfo(
            board=Board,
            aid=PostAID,
            author=PostAuthor,
            date=PostDate,
            title=PostTitle,
            web_url=PostWeb,
            money=PostMoney,
            content=PostContent,
            ip=IP,
            push_list=PushList,
            list_date=ListDate,
            control_code=HasControlCode,
            format_check=False,
            location=Location,
            push_number=PushNumber,
            origin_post=OriginPost,
            unconfirmed=api.Unconfirmed,
        )
        return Post
    PostTitle = PatternResult.group(0)
    PostTitle = PostTitle[4:].strip()

    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        i18n.Title,
        PostTitle
    )

    PostDatePattern = re.compile('時間  (.+)')
    DateLine = OriginPostLines[2]
    PatternResult = PostDatePattern.search(DateLine)
    if PatternResult is None:
        Log.showValue(
            api.Config,
            Log.Level.DEBUG,
            i18n.SubstandardPost,
            i18n.Date
        )
        Post = DataType.PostInfo(
            board=Board,
            aid=PostAID,
            author=PostAuthor,
            date=PostDate,
            title=PostTitle,
            web_url=PostWeb,
            money=PostMoney,
            content=PostContent,
            ip=IP,
            push_list=PushList,
            list_date=ListDate,
            control_code=HasControlCode,
            format_check=False,
            location=Location,
            push_number=PushNumber,
            origin_post=OriginPost,
            unconfirmed=api.Unconfirmed,
        )
        return Post
    PostDate = PatternResult.group(0)
    PostDate = PostDate[4:].strip()

    Log.showValue(
        api.Config,
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
            api.Config,
            Log.Level.DEBUG,
            i18n.SubstandardPost,
            i18n.Content
        )
        Post = DataType.PostInfo(
            board=Board,
            aid=PostAID,
            author=PostAuthor,
            date=PostDate,
            title=PostTitle,
            web_url=PostWeb,
            money=PostMoney,
            content=PostContent,
            ip=IP,
            push_list=PushList,
            list_date=ListDate,
            control_code=HasControlCode,
            format_check=False,
            location=Location,
            push_number=PushNumber,
            origin_post=OriginPost,
            unconfirmed=api.Unconfirmed,
        )
        return Post

    Log.showValue(
        api.Config,
        Log.Level.DEBUG,
        i18n.Content,
        PostContent
    )

    InfoLines = [
        line for line in OriginPostLines if line.startswith('※') or
        line.startswith('◆')
    ]

    pattern = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')
    pattern_p2 = re.compile('[\d]+-[\d]+-[\d]+-[\d]+')
    for line in reversed(InfoLines):
        Log.showValue(
            api.Config,
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
                Log.showValue(api.Config, Log.Level.DEBUG,
                              'Location', Location)
            break

        PatternResult = pattern_p2.search(line)
        if PatternResult is not None:
            IP = PatternResult.group(0)
            IP = IP.replace('-', '.')
            # print(f'IP -> [{IP}]')
            break
    if api.Config.Host == DataType.Host.PTT1:
        if IP is None:
            Log.showValue(
                api.Config,
                Log.Level.DEBUG,
                i18n.SubstandardPost,
                'IP'
            )
            Post = DataType.PostInfo(
                board=Board,
                aid=PostAID,
                author=PostAuthor,
                date=PostDate,
                title=PostTitle,
                web_url=PostWeb,
                money=PostMoney,
                content=PostContent,
                ip=IP,
                push_list=PushList,
                list_date=ListDate,
                control_code=HasControlCode,
                format_check=False,
                location=Location,
                push_number=PushNumber,
                origin_post=OriginPost,
                unconfirmed=api.Unconfirmed,
            )
            return Post
    Log.showValue(api.Config, Log.Level.DEBUG, 'IP', IP)

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
        Log.showValue(api.Config, Log.Level.DEBUG, [
            i18n.Push,
            i18n.ID,
        ],
            PushAuthor
        )

        Result = PushDatePattern.search(line)
        if Result is None:
            continue
        PushDate = Result.group(0)
        Log.showValue(api.Config, Log.Level.DEBUG, [
            i18n.Push,
            i18n.Date,
        ],
            PushDate
        )

        PushIP = None
        Result = PushIPPattern.search(line)
        if Result is not None:
            PushIP = Result.group(0)
            Log.showValue(api.Config, Log.Level.DEBUG, [
                i18n.Push,
                'IP',
            ],
                PushIP
            )

        PushContent = line[
            line.find(PushAuthor) + len(PushAuthor):
        ]
        # PushContent = PushContent.replace(PushDate, '')

        if api.Config.Host == DataType.Host.PTT1:
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
        Log.showValue(api.Config, Log.Level.DEBUG, [
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
        board=Board,
        aid=PostAID,
        author=PostAuthor,
        date=PostDate,
        title=PostTitle,
        web_url=PostWeb,
        money=PostMoney,
        content=PostContent,
        ip=IP,
        push_list=PushList,
        list_date=ListDate,
        control_code=HasControlCode,
        format_check=True,
        location=Location,
        push_number=PushNumber,
        origin_post=OriginPost,
        unconfirmed=api.Unconfirmed,
    )
    return Post
