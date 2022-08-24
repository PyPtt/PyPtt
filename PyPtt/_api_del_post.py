import PyPtt
from . import command, lib_util, check_value, NewIndex, _api_util
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import screens


def del_post(api: PyPtt.API, board: str, post_aid: str = None, post_index: int = 0) -> None:
    _api_util.one_thread(api)

    if api.unregistered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    if not api._login_status:
        raise exceptions.Requirelogin(i18n.require_login)

    check_value.check_type(str, 'board', board)
    if post_aid is not None:
        check_value.check_type(str, 'PostAID', post_aid)
    check_value.check_type(int, 'PostIndex', post_index)

    if len(board) == 0:
        raise ValueError(f'board error parameter: {board}')

    if post_index != 0 and isinstance(post_aid, str):
        raise ValueError('wrong parameter post_index and post_aid can\'t both input')

    if post_index == 0 and post_aid is None:
        raise ValueError('wrong parameter post_index or post_aid must input')

    if post_index != 0:
        newest_index = api.get_newest_index(
            NewIndex.BBS,
            board=board)
        check_value.check_index(
            'PostIndex',
            post_index,
            newest_index)

    board_info = _api_util._check_board(api, board)

    check_author = True
    for moderator in board_info.moderators:
        if api._ID.lower() == moderator.lower():
            check_author = False
            break

    post_info = api.get_post(board, aid=post_aid, index=post_index, query=True)
    if post_info['delete_status'] != data_type.PostDelStatus.exist:
        if post_aid is not None:
            raise exceptions.DeletedPost(board, post_aid)
        else:
            raise exceptions.DeletedPost(board, post_index)

    if check_author:
        if api._ID.lower() != post_info['author'].lower():
            raise exceptions.NoPermission(i18n.no_permission)

    _api_util.goto_board(api, board)

    cmd_list = list()

    if post_aid is not None:
        cmd_list.append('#' + post_aid)
    elif post_index != 0:
        cmd_list.append(str(post_index))
    cmd_list.append(command.enter)
    cmd_list.append('d')

    cmd = ''.join(cmd_list)

    api.confirm = False

    def confirm_delete_handler(screen):
        api.confirm = True

    target_list = [
        connect_core.TargetUnit(
            i18n.any_key_continue,
            '請按任意鍵繼續',
            response=' '),
        connect_core.TargetUnit(
            i18n.confirm_delete,
            '請確定刪除(Y/N)?[N]',
            response='y' + command.enter,
            max_match=1,
            handler=confirm_delete_handler),
        connect_core.TargetUnit(
            i18n.delete_success,
            screens.Target.InBoard,
            break_detect=True),
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
            raise exceptions.NoPermission(i18n.no_permission)

    if index == -1:
        if post_aid is not None:
            raise exceptions.NoSuchPost(board, post_aid)
        else:
            raise exceptions.NoSuchPost(board, post_index)
