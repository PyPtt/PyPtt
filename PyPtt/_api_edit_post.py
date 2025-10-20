from . import _api_util
from . import check_value
from . import command
from . import data_type
from . import exceptions
from . import i18n
from . import lib_util
from . import log


def edit_post(api, board: str, post_aid: str, post_index: int, new_content: str, new_title: str) -> None:
    _api_util.one_thread(api)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    check_value.check_type(board, str, 'board')
    if post_aid is not None:
        check_value.check_type(post_aid, str, 'PostAID')
    check_value.check_type(post_index, int, 'PostIndex')

    if new_content is not None:
        check_value.check_type(new_content, str, 'NewContent')
    if new_title is not None:
        check_value.check_type(new_title, str, 'NewTitle')

    if len(board) == 0:
        raise exceptions.ParameterError(f'board error parameter: {board}')

    if post_index != 0 and isinstance(post_aid, str):
        raise exceptions.ParameterError('wrong parameter index and aid can\'t both input')

    if post_index == 0 and post_aid is None:
        raise exceptions.ParameterError('wrong parameter index or aid must input')

    if post_index != 0:
        newest_index = api.get_newest_index(
            data_type.NewIndex.BOARD,
            board=board)
        check_value.check_index(
            'PostIndex',
            post_index,
            newest_index)

    log.logger.info(i18n.edit_post)

    post_info = api.get_post(board, aid=post_aid, index=post_index, query=True)
    if api.ptt_id.lower() != post_info[data_type.PostField.author].lower():
        log.logger.info(i18n.edit_post, '...', i18n.fail)
        raise exceptions.NoPermission(i18n.no_permission)

    print(post_info)


