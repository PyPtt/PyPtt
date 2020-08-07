try:
    from . import data_type
    from . import i18n
    from . import connect_core
    from . import log
    from . import screens
    from . import command
    from . import check_value
    from . import exceptions
    from . import lib_util
except ModuleNotFoundError:
    import data_type
    import i18n
    import connect_core
    import log
    import screens
    import command
    import check_value
    import exceptions
    import lib_util


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
        log.level.INFO,
        [
            i18n.PTT,
            i18n.Msg
        ],
        i18n.MarkPost
    )

    check_value.check(api.config, int, 'mark_type', mark_type,
                      value_class=data_type.mark_type)
    check_value.check(api.config, str, 'Board', board)
    if post_aid is not None:
        check_value.check(api.config, str, 'PostAID', post_aid)
    check_value.check(api.config, int, 'PostIndex', post_index)
    check_value.check(api.config, int, 'SearchType', search_type,
                      value_class=data_type.post_search_type)
    if search_condition is not None:
        check_value.check(api.config, str,
                          'SearchCondition', search_condition)

    if len(board) == 0:
        raise ValueError(log.merge([
            i18n.Board,
            i18n.ErrorParameter,
            board
        ]))

    if mark_type != data_type.mark_type.DeleteD:
        if post_index != 0 and isinstance(post_aid, str):
            raise ValueError(log.merge(
                api.config,
                [
                    'PostIndex',
                    'PostAID',
                    i18n.ErrorParameter,
                    i18n.BothInput
                ]))

        if post_index == 0 and post_aid is None:
            raise ValueError(log.merge(
                api.config,
                [
                    'PostIndex',
                    'PostAID',
                    i18n.ErrorParameter
                ]))

    if search_condition is not None and search_type == 0:
        raise ValueError(log.merge(
            api.config,
            [
                'SearchType',
                i18n.ErrorParameter,
            ]))

    if search_type == data_type.post_search_type.PUSH:
        try:
            S = int(search_condition)
        except ValueError:
            raise ValueError(log.merge(
                api.config,
                [
                    'SearchCondition',
                    i18n.ErrorParameter,
                ]))

        if not (-100 <= S <= 110):
            raise ValueError(log.merge(
                api.config,
                [
                    'SearchCondition',
                    i18n.ErrorParameter,
                ]))

    if post_aid is not None and search_condition is not None:
        raise ValueError(log.merge(
            api.config, [
                'PostAID',
                'SearchCondition',
                i18n.ErrorParameter,
                i18n.BothInput,
            ]))

    if post_index != 0:
        newest_index = api._get_newest_index(
            data_type.index_type.BBS,
            board=board,
            search_type=search_type,
            search_condition=search_condition
        )
        check_value.check_index(api.config, 'PostIndex',
                                post_index, max_value=newest_index)

    if mark_type == data_type.mark_type.UNCONFIRMED:
        # 批踢踢兔沒有待證文章功能 QQ
        if api.config.host == data_type.host_type.PTT2:
            raise exceptions.HostNotSupport(lib_util.get_current_func_name())

    api._check_board(
        board,
        check_moderator=True
    )

    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(command.Enter)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵',
            response=' ',
        ),
        connect_core.TargetUnit(
            [
                '動畫播放中',
            ],
            '互動式動畫播放中',
            response=command.Ctrl_C,
            log_level=log.level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                '進板成功',
            ],
            screens.Target.InBoard,
            break_detect=True,
            log_level=log.level.DEBUG
        ),
    ]

    index = api.connect_core.send(cmd, target_list)

    cmd_list = []
    if post_aid is not None:
        cmd_list.append('#' + post_aid)

        cmd_list.append(command.Enter)

    elif post_index != 0:
        if search_condition is not None:
            if search_type == data_type.post_search_type.KEYWORD:
                cmd_list.append('/')
            elif search_type == data_type.post_search_type.AUTHOR:
                cmd_list.append('a')
            elif search_type == data_type.post_search_type.PUSH:
                cmd_list.append('Z')
            elif search_type == data_type.post_search_type.MARK:
                cmd_list.append('G')
            elif search_type == data_type.post_search_type.MONEY:
                cmd_list.append('A')

            cmd_list.append(search_condition)
            cmd_list.append(command.Enter)

        cmd_list.append(str(post_index))

        cmd_list.append(command.Enter)

    if mark_type == data_type.mark_type.S:
        cmd_list.append('L')
    elif mark_type == data_type.mark_type.D:
        cmd_list.append('t')
    elif mark_type == data_type.mark_type.DeleteD:
        cmd_list.append(command.Ctrl_D)
    elif mark_type == data_type.mark_type.M:
        cmd_list.append('m')
    elif mark_type == data_type.mark_type.UNCONFIRMED:
        cmd_list.append(command.Ctrl_E + 'S')

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            [i18n.DelAllMarkPost],
            '刪除所有標記',
            response='y' + command.Enter,
            log_level=log.level.INFO
        ),
        connect_core.TargetUnit(
            [
                i18n.Mark,
                i18n.Success,
            ],
            screens.Target.InBoard,
            break_detect=True,
            log_level=log.level.INFO
        ),
    ]

    index = api.connect_core.send(cmd, target_list)
