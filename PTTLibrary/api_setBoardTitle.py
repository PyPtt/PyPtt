try:
    from . import i18n
    from . import ConnectCore
    from . import Command
except ModuleNotFoundError:
    import i18n
    import ConnectCore
    import Command


def set_board_title(
        api,
        board: str,
        new_title: str) ->None:

    # log.showValue(
    #     api.config,
    #     log.Level.INFO,
    #     [
    #         i18n.PTT,
    #         i18n.Msg
    #     ],
    #     i18n.MarkPost
    # )

    cmd_list = []
    cmd_list.append(Command.GoMainMenu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(Command.Enter)
    cmd_list.append(Command.Ctrl_C * 2)
    cmd_list.append(Command.Space)
    cmd_list.append('I')
    cmd_list.append(Command.Ctrl_P)
    cmd_list.append('b')
    cmd_list.append(Command.Enter)
    cmd_list.append(Command.Backspace * 31)
    cmd_list.append(new_title)
    cmd_list.append(Command.Enter * 2)
    cmd = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            i18n.NewSettingsHaveBeenSaved,
            '◆ 已儲存新設定',
            break_detect=True,
        ),
        ConnectCore.TargetUnit(
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
