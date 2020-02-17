try:
    from . import i18n
    from . import connect_core
    from . import command
except ModuleNotFoundError:
    import i18n
    import connect_core
    import command


def set_board_title(
        api,
        board: str,
        new_title: str) ->None:

    # log.showValue(
    #     api.config,
    #     log.level.INFO,
    #     [
    #         i18n.PTT,
    #         i18n.Msg
    #     ],
    #     i18n.MarkPost
    # )

    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(command.Enter)
    cmd_list.append(command.Ctrl_C * 2)
    cmd_list.append(command.Space)
    cmd_list.append('I')
    cmd_list.append(command.Ctrl_P)
    cmd_list.append('b')
    cmd_list.append(command.Enter)
    cmd_list.append(command.Backspace * 31)
    cmd_list.append(new_title)
    cmd_list.append(command.Enter * 2)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.NewSettingsHaveBeenSaved,
            '◆ 已儲存新設定',
            break_detect=True,
        ),
        connect_core.TargetUnit(
            i18n.NoChanges,
            '◆ 未改變任何設定',
            break_detect=True,
        ),
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout
    )
