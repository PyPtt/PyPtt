try:
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Command
except ModuleNotFoundError:
    import i18n
    import ConnectCore
    import Log
    import Command


def bucket(api, Board, BucketDays, Reason, TargetID):

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

    api._ConnectCore.send(
        Cmd,
        TargetList
    )

    # OriScreen = api._ConnectCore.getScreenQueue()[-1]
