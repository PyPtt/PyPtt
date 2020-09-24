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


def del_post(
        api,
        board,
        post_aid: str = None,
        post_index: int = 0) -> None:
    post_info = api.get_post(board, post_aid=post_aid, post_index=post_index)
    if post_info.delete_status != data_type.post_delete_status.NOT_DELETED:
        if post_aid is not None:
            raise exceptions.DeletedPost(board, post_aid)
        else:
            raise exceptions.DeletedPost(board, post_index)

    api._goto_board(board)

    cmd_list = list()

    if post_aid is not None:
        cmd_list.append('#' + post_aid)
    elif post_index != 0:
        cmd_list.append(str(post_index))
    cmd_list.append(command.Enter)
    cmd_list.append('d')

    cmd = ''.join(cmd_list)

    api.confirm = False

    def confirm_delete_handler(screen):
        api.confirm = True

    target_list = [
        connect_core.TargetUnit(
            i18n.ConfirmDelete,
            '請確定刪除(Y/N)?[N]',
            response='y' + command.Enter,
            handler=confirm_delete_handler
        ),
        connect_core.TargetUnit(
            i18n.DeleteSuccess,
            screens.Target.InBoard,
            break_detect=True
        ),
    ]

    index = api.connect_core.send(
        cmd,
        target_list)

    # last_screen = api.connect_core.get_screen_queue()[-1]
    # print(api.confirm)
    # print(last_screen)
    # print(index)

    if index == 1:
        if not api.confirm:
            raise exceptions.NoPermission(i18n.NoPermission)

    if index == -1:
        if post_aid is not None:
            raise exceptions.NoSuchPost(board, post_aid)
        else:
            raise exceptions.NoSuchPost(board, post_index)
