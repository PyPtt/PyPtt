try:
    from . import DataType
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Screens
    from . import Command
    from . import CheckValue
except ModuleNotFoundError:
    import DataType
    import i18n
    import ConnectCore
    import Log
    import Screens
    import Command
    import CheckValue


def markPost(
        api,
        mark_type: int,
        board: str,
        post_aid: str,
        post_index: int,
        search_type: int,
        search_condition: str) -> None:

    Log.show_value(
        api.Config,
        Log.Level.INFO,
        [
            i18n.PTT,
            i18n.Msg
        ],
        i18n.MarkPost
    )

    CheckValue.check(api.Config, int, 'MarkType', mark_type,
                     value_class=DataType.MarkType)
    CheckValue.check(api.Config, str, 'Board', board)
    if post_aid is not None:
        CheckValue.check(api.Config, str, 'PostAID', post_aid)
    CheckValue.check(api.Config, int, 'PostIndex', post_index)
    CheckValue.check(api.Config, int, 'SearchType', search_type,
                     value_class=DataType.PostSearchType)
    if search_condition is not None:
        CheckValue.check(api.Config, str,
                         'SearchCondition', search_condition)

    if len(board) == 0:
        raise ValueError(Log.merge([
            i18n.Board,
            i18n.ErrorParameter,
            board
        ]))

    if post_index != 0 and isinstance(post_aid, str):
        raise ValueError(Log.merge([
            'PostIndex',
            'PostAID',
            i18n.ErrorParameter,
            i18n.BothInput
        ]))

    if post_index == 0 and post_aid is None:
        raise ValueError(Log.merge([
            'PostIndex',
            'PostAID',
            i18n.ErrorParameter
        ]))

    if search_condition is not None and search_type == 0:
        raise ValueError(Log.merge([
            'SearchType',
            i18n.ErrorParameter,
        ]))

    if search_type == DataType.PostSearchType.Push:
        try:
            S = int(search_condition)
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

    if post_aid is not None and search_condition is not None:
        raise ValueError(Log.merge([
            'PostAID',
            'SearchCondition',
            i18n.ErrorParameter,
            i18n.BothInput,
        ]))

    if post_index != 0:
        NewestIndex = api._get_newest_index(
            DataType.IndexType.BBS,
            board=board,
            search_type=search_type,
            search_condition=search_condition
        )
        CheckValue.check_index(api.Config, 'PostIndex',
                               post_index, max_value=NewestIndex)

    if mark_type == DataType.MarkType.Unconfirmed:
        # 批踢踢兔沒有待證文章功能 QQ
        if api.Config.Host == DataType.Host.PTT2:
            raise Exceptions.HostNotSupport(Util.get_current_func_name())

    api._check_board(
        board,
        check_moderator=True
    )

    cmd_list = []
    cmd_list.append(Command.GoMainMenu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(Command.Enter)

    cmd = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵',
            response=' ',
        ),
        ConnectCore.TargetUnit(
            [
                '動畫播放中',
            ],
            '互動式動畫播放中',
            response=Command.Ctrl_C,
            log_level=Log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                '進板成功',
            ],
            Screens.Target.InBoard,
            break_detect=True,
            log_level=Log.Level.DEBUG
        ),
    ]

    index = api._ConnectCore.send(cmd, target_list)

    cmd_list = []
    if post_aid is not None:
        cmd_list.append('#' + post_aid)

    elif post_index != 0:
        if search_condition is not None:
            if search_type == DataType.PostSearchType.Keyword:
                cmd_list.append('/')
            elif search_type == DataType.PostSearchType.Author:
                cmd_list.append('a')
            elif search_type == DataType.PostSearchType.Push:
                cmd_list.append('Z')
            elif search_type == DataType.PostSearchType.Mark:
                cmd_list.append('G')
            elif search_type == DataType.PostSearchType.Money:
                cmd_list.append('A')

            cmd_list.append(search_condition)
            cmd_list.append(Command.Enter)

        cmd_list.append(str(post_index))

    cmd_list.append(Command.Enter)

    if mark_type == DataType.MarkType.S:
        cmd_list.append('L')
    elif mark_type == DataType.MarkType.D:
        cmd_list.append('t')
    elif mark_type == DataType.MarkType.DeleteD:
        cmd_list.append(Command.Ctrl_D)
    elif mark_type == DataType.MarkType.M:
        cmd_list.append('m')
    elif mark_type == DataType.MarkType.Unconfirmed:
        cmd_list.append(Command.Ctrl_E + 'S')

    cmd = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            [i18n.DelAllMarkPost],
            '刪除所有標記',
            response='y' + Command.Enter,
            log_level=Log.Level.INFO
        ),
        ConnectCore.TargetUnit(
            [
                i18n.Mark,
                i18n.Success,
            ],
            Screens.Target.InBoard,
            break_detect=True,
            log_level=Log.Level.INFO
        ),
    ]

    index = api._ConnectCore.send(cmd, target_list)
