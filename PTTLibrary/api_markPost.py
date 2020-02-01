try:
    from . import data_type
    from . import i18n
    from . import ConnectCore
    from . import log
    from . import screens
    from . import Command
    from . import CheckValue
except ModuleNotFoundError:
    import data_type
    import i18n
    import ConnectCore
    import log
    import screens
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

    log.show_value(
        api.config,
        log.Level.INFO,
        [
            i18n.PTT,
            i18n.Msg
        ],
        i18n.MarkPost
    )

    CheckValue.check(api.config, int, 'MarkType', mark_type,
                     value_class=data_type.MarkType)
    CheckValue.check(api.config, str, 'Board', board)
    if post_aid is not None:
        CheckValue.check(api.config, str, 'PostAID', post_aid)
    CheckValue.check(api.config, int, 'PostIndex', post_index)
    CheckValue.check(api.config, int, 'SearchType', search_type,
                     value_class=data_type.PostSearchType)
    if search_condition is not None:
        CheckValue.check(api.config, str,
                         'SearchCondition', search_condition)

    if len(board) == 0:
        raise ValueError(log.merge([
            i18n.Board,
            i18n.ErrorParameter,
            board
        ]))

    if post_index != 0 and isinstance(post_aid, str):
        raise ValueError(log.merge([
            'PostIndex',
            'PostAID',
            i18n.ErrorParameter,
            i18n.BothInput
        ]))

    if post_index == 0 and post_aid is None:
        raise ValueError(log.merge([
            'PostIndex',
            'PostAID',
            i18n.ErrorParameter
        ]))

    if search_condition is not None and search_type == 0:
        raise ValueError(log.merge([
            'SearchType',
            i18n.ErrorParameter,
        ]))

    if search_type == data_type.PostSearchType.Push:
        try:
            S = int(search_condition)
        except ValueError:
            raise ValueError(log.merge([
                'SearchCondition',
                i18n.ErrorParameter,
            ]))

        if not (-100 <= S <= 110):
            raise ValueError(log.merge([
                'SearchCondition',
                i18n.ErrorParameter,
            ]))

    if post_aid is not None and search_condition is not None:
        raise ValueError(log.merge([
            'PostAID',
            'SearchCondition',
            i18n.ErrorParameter,
            i18n.BothInput,
        ]))

    if post_index != 0:
        NewestIndex = api._get_newest_index(
            data_type.IndexType.BBS,
            board=board,
            search_type=search_type,
            search_condition=search_condition
        )
        CheckValue.check_index(api.config, 'PostIndex',
                               post_index, max_value=NewestIndex)

    if mark_type == data_type.MarkType.Unconfirmed:
        # 批踢踢兔沒有待證文章功能 QQ
        if api.config.host == data_type.host.PTT2:
            raise exceptions.hostNotSupport(lib_util.get_current_func_name())

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
            log_level=log.Level.DEBUG
        ),
        ConnectCore.TargetUnit(
            [
                '進板成功',
            ],
            screens.Target.InBoard,
            break_detect=True,
            log_level=log.Level.DEBUG
        ),
    ]

    index = api.connect_core.send(cmd, target_list)

    cmd_list = []
    if post_aid is not None:
        cmd_list.append('#' + post_aid)

    elif post_index != 0:
        if search_condition is not None:
            if search_type == data_type.PostSearchType.Keyword:
                cmd_list.append('/')
            elif search_type == data_type.PostSearchType.Author:
                cmd_list.append('a')
            elif search_type == data_type.PostSearchType.Push:
                cmd_list.append('Z')
            elif search_type == data_type.PostSearchType.Mark:
                cmd_list.append('G')
            elif search_type == data_type.PostSearchType.Money:
                cmd_list.append('A')

            cmd_list.append(search_condition)
            cmd_list.append(Command.Enter)

        cmd_list.append(str(post_index))

    cmd_list.append(Command.Enter)

    if mark_type == data_type.MarkType.S:
        cmd_list.append('L')
    elif mark_type == data_type.MarkType.D:
        cmd_list.append('t')
    elif mark_type == data_type.MarkType.DeleteD:
        cmd_list.append(Command.Ctrl_D)
    elif mark_type == data_type.MarkType.M:
        cmd_list.append('m')
    elif mark_type == data_type.MarkType.Unconfirmed:
        cmd_list.append(Command.Ctrl_E + 'S')

    cmd = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            [i18n.DelAllMarkPost],
            '刪除所有標記',
            response='y' + Command.Enter,
            log_level=log.Level.INFO
        ),
        ConnectCore.TargetUnit(
            [
                i18n.Mark,
                i18n.Success,
            ],
            screens.Target.InBoard,
            break_detect=True,
            log_level=log.Level.INFO
        ),
    ]

    index = api.connect_core.send(cmd, target_list)
