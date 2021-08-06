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
        new_title: str) -> None:
    api._goto_board(board)

    cmd_list = list()
    cmd_list.append('I')
    cmd_list.append(command.ctrl_p)
    cmd_list.append('b')
    cmd_list.append(command.enter)
    cmd_list.append(command.backspace * 31)
    cmd_list.append(new_title)
    cmd_list.append(command.enter * 2)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.new_settings_have_been_saved,
            '◆ 已儲存新設定',
            break_detect=True,
        ),
        connect_core.TargetUnit(
            i18n.no_changes,
            '◆ 未改變任何設定',
            break_detect=True,
        ),
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout)
