try:
    from . import i18n
    from . import ConnectCore
    from . import screens
    from . import exceptions
    from . import Command
except ModuleNotFoundError:
    import i18n
    import ConnectCore
    import screens
    import exceptions
    import Command


def bucket(api: object, board: str, bucket_days: int, reason: str, pttid: str) -> None:

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
            exceptions=exceptions.UserHasPreviouslyBeenBanned()
        ),
        ConnectCore.TargetUnit(
            i18n.InputBucketDays_Reason,
            '請以數字跟單位(預設為天)輸入期限',
            response=cmd_part2,
        ),
        ConnectCore.TargetUnit(
            [
                i18n.bucket,
                i18n.Success,
            ],
            '其它鍵結束',
            response=Command.Enter,
        ),
        ConnectCore.TargetUnit(
            [
                i18n.bucket,
                i18n.Success,
            ],
            '權限設定系統',
            response=Command.Enter,
        ),
        ConnectCore.TargetUnit(
            [
                i18n.bucket,
                i18n.Success,
            ],
            '任意鍵',
            response=Command.Space,
        ),
        ConnectCore.TargetUnit(
            [
                i18n.bucket,
                i18n.Success,
            ],
            screens.Target.InBoard,
            break_detect=True
        ),
    ]

    api.connect_core.send(
        cmd,
        target_list
    )

    # OriScreen = api.connect_core.getScreenQueue()[-1]
