import re

try:
    from . import data_type
    from . import i18n
    from . import connect_core
    from . import log
    from . import screens
    from . import exceptions
    from . import command
except ModuleNotFoundError:
    import data_type
    import i18n
    import connect_core
    import log
    import screens
    import exceptions
    import command


def get_bottom_post_list(api, board):
    api._goto_board(board)

    last_screen = api.connect_core.get_screen_queue()[-1]

    print(last_screen)

    bottom_screen = [line for line in last_screen.split('\n') if '★' in line[:8]]
    bottom_length = len(bottom_screen)
    # bottom_screen = '\n'.join(bottom_screen)
    # print(bottom_screen)

    cmd_list = list()
    cmd_list.append(command.QueryPost)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            [
                i18n.CatchPost,
                i18n.Success,
            ],
            screens.Target.QueryPost,
            break_detect=True,
            refresh=False,
            log_level=log.level.DEBUG
        ),
        connect_core.TargetUnit(
            [
                i18n.PostDeleted,
                i18n.Success,
            ],
            screens.Target.InBoard,
            break_detect=True,
            log_level=log.level.DEBUG
        ),
        connect_core.TargetUnit(
            i18n.NoSuchBoard,
            screens.Target.MainMenu_Exiting,
            exceptions_=exceptions.NoSuchBoard(api.config, board)
        ),
    ]

    index = api.connect_core.send(cmd, target_list)
    last_screen = api.connect_core.get_screen_queue()[-1]

    print(last_screen)
