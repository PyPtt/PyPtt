import re
import time
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


def getWaterBall(api, OperateType):

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
        index = api._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=1
        )
        Log.showValue(
            api.Config,
            Log.Level.DEBUG,
            'index',
            index
        )
        if index == 0:
            return WaterBallList

        OriScreen = api._ConnectCore.getScreenQueue()[-1]
        Lines = OriScreen.split('\n')
        LastLine = Lines[-1]
        Lines.pop()
        Lines = list(filter(None, Lines))
        OriScreen = '\n'.join(Lines)

        # print('=' * 50)
        # print(OriScreen)
        # print('=' * 50)
        # ScreenTemp = OriScreen
        Log.showValue(
            api.Config,
            Log.Level.DEBUG,
            'OriScreen',
            OriScreen
        )

        Log.showValue(
            api.Config,
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
                api.Config,
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

    if api.Config.Host == DataType.Host.PTT1:
        AllWaterball = AllWaterball.replace(
            ']\n', ']==PTTWaterBallNewLine==')
        AllWaterball = AllWaterball.replace('\n', '')
        AllWaterball = AllWaterball.replace(
            ']==PTTWaterBallNewLine==', ']\n')
    else:
        AllWaterball = AllWaterball.replace('\\\n', '')
    Log.showValue(
        api.Config,
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
                api.Config,
                Log.Level.DEBUG,
                'Discard waterball',
                line
            )
            continue
        Log.showValue(
            api.Config,
            Log.Level.DEBUG,
            'Ready to parse waterball',
            line
        )

        if line.startswith('To'):
            Log.showValue(
                api.Config,
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
                api.Config,
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
            api.Config,
            Log.Level.DEBUG,
            'Waterball Target',
            Target
        )
        Log.showValue(
            api.Config,
            Log.Level.DEBUG,
            'Waterball Content',
            Content
        )
        Log.showValue(
            api.Config,
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


def throwWaterBall(api, TargetID, Content):
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

        if api._LastThroWaterBallTime != 0:
            CurrentTime = time.time()
            while (CurrentTime - api._LastThroWaterBallTime) < 3.2:
                time.sleep(0.1)
                CurrentTime = time.time()

        Log.showValue(
            api.Config,
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
        if '【好友列表】' in api._ConnectCore.getScreenQueue()[-1]:
            CmdList.append('f')
        CmdList.append('s')
        CmdList.append(TargetID)
        CmdList.append(Command.Enter)
        CmdList.append('w')

        Cmd = ''.join(CmdList)

        api._ConnectCore.send(
            Cmd,
            TargetList,
            ScreenTimeout=api.Config.ScreenLongTimeOut
        )

        api._LastThroWaterBallTime = time.time()
