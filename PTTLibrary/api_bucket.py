try:
    from . import i18n
    from . import ConnectCore
    from . import Screens
    from . import Exceptions
    from . import Command
except ModuleNotFoundError:
    import i18n
    import ConnectCore
    import Screens
    import Exceptions
    import Command


def bucket(api, board, bucket_days, reason, pttid):

    cmd_list = []
    cmd_list.append(Command.GoMainMenu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(Command.Enter)
    cmd_list.append(Command.Ctrl_C * 2)
    cmd_list.append(Command.Space)
    cmd_list.append('i')
    cmd_list.append(Command.Ctrl_P)
    cmd_list.append('w')
    cmd_list.append(Command.Enter)
    cmd_list.append('a')
    cmd_list.append(Command.Enter)
    cmd_list.append(pttid)
    cmd_list.append(Command.Enter)
    cmd = ''.join(cmd_list)

    cmd_list = []
    cmd_list.append(str(bucket_days))
    cmd_list.append(Command.Enter)
    cmd_list.append(reason)
    cmd_list.append(Command.Enter)
    cmd_list.append('y')
    cmd_list.append(Command.Enter)
    cmd_part2 = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            [
                i18n.bucket,
                i18n.Fail,
            ],
            '◆ 使用者之前已被禁言',
            Exceptions=Exceptions.UserHasPreviouslyBeenBanned()
        ),
        ConnectCore.TargetUnit(
            i18n.InputBucketDays_Reason,
            '請以數字跟單位(預設為天)輸入期限',
            Response=cmd_part2,
        ),
        ConnectCore.TargetUnit(
            [
                i18n.bucket,
                i18n.Success,
            ],
            '其它鍵結束',
            Response=Command.Enter,
        ),
        ConnectCore.TargetUnit(
            [
                i18n.bucket,
                i18n.Success,
            ],
            '權限設定系統',
            Response=Command.Enter,
        ),
        ConnectCore.TargetUnit(
            [
                i18n.bucket,
                i18n.Success,
            ],
            '任意鍵',
            Response=Command.Space,
        ),
        ConnectCore.TargetUnit(
            [
                i18n.bucket,
                i18n.Success,
            ],
            Screens.Target.InBoard,
            BreakDetect=True
        ),
    ]

    api._ConnectCore.send(
        cmd,
        target_list
    )

    # OriScreen = api._ConnectCore.getScreenQueue()[-1]
