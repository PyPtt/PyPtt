try:
    from . import i18n
    from . import connect_core
    from . import screens
    from . import exceptions
    from . import command
except ModuleNotFoundError:
    import i18n
    import connect_core
    import screens
    import exceptions
    import command


def bucket(api: object, board: str, bucket_days: int, reason: str, ptt_id: str) -> None:

    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(command.Enter)
    cmd_list.append(command.Ctrl_C * 2)
    cmd_list.append(command.Space)
    cmd_list.append('i')
    cmd_list.append(command.Ctrl_P)
    cmd_list.append('w')
    cmd_list.append(command.Enter)
    cmd_list.append('a')
    cmd_list.append(command.Enter)
    cmd_list.append(ptt_id)
    cmd_list.append(command.Enter)
    cmd = ''.join(cmd_list)

    cmd_list = []
    cmd_list.append(str(bucket_days))
    cmd_list.append(command.Enter)
    cmd_list.append(reason)
    cmd_list.append(command.Enter)
    cmd_list.append('y')
    cmd_list.append(command.Enter)
    cmd_part2 = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            [
                i18n.bucket,
                i18n.Fail,
            ],
            '◆ 使用者之前已被禁言',
            exceptions_=exceptions.UserHasPreviouslyBeenBanned()
        ),
        connect_core.TargetUnit(
            i18n.InputBucketDays_Reason,
            '請以數字跟單位(預設為天)輸入期限',
            response=cmd_part2,
        ),
        connect_core.TargetUnit(
            [
                i18n.bucket,
                i18n.Success,
            ],
            '其它鍵結束',
            response=command.Enter,
        ),
        connect_core.TargetUnit(
            [
                i18n.bucket,
                i18n.Success,
            ],
            '權限設定系統',
            response=command.Enter,
        ),
        connect_core.TargetUnit(
            [
                i18n.bucket,
                i18n.Success,
            ],
            '任意鍵',
            response=command.Space,
        ),
        connect_core.TargetUnit(
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
