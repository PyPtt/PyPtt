from __future__ import annotations

from typing import Optional

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import lib_util
from . import log
from . import screens


def del_post(api, board: str, post_aid: Optional[str] = None, post_index: int = 0, reason: Optional[str] = None,
             bad_post_type: Optional[data_type.BadPostType] = None,
             bad_post_reason: Optional[str] = None) -> None:
    _api_util.one_thread(api)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    check_value.check_type(board, str, 'board')
    if post_aid is not None:
        check_value.check_type(post_aid, str, 'PostAID')
    check_value.check_type(post_index, int, 'PostIndex')
    if reason is not None:
        check_value.check_type(reason, str, 'reason')
    if bad_post_type is not None:
        check_value.check_type(bad_post_type, data_type.BadPostType, 'bad_post_type')
    if bad_post_reason is not None:
        check_value.check_type(bad_post_reason, str, 'bad_post_reason')

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

    log.logger.info(i18n.delete_post)

    board_info = _api_util.check_board(api, board)

    check_author = True
    for moderator in board_info[data_type.BoardField.moderators]:
        if api.ptt_id.lower() == moderator.lower():
            check_author = False
            break

    log.logger.info(i18n.delete_post)

    post_info = api.get_post(board, aid=post_aid, index=post_index, query=True)
    if post_info[data_type.PostField.post_status] != data_type.PostStatus.EXISTS:
        # delete success
        log.logger.info(i18n.delete_post, '...', i18n.success)
        return

    # PTT only offers the "R加註理由" annotation when a moderator deletes
    # another user's post. On your own post the reason can never be applied,
    # so reject it rather than silently dropping it.
    if reason and api.ptt_id.lower() == post_info[data_type.PostField.author].lower():
        raise exceptions.ParameterError(
            'reason is only valid when a moderator deletes another user\'s post')

    # 惡退（劣文）跟 R 加註理由一樣，只有「板主刪除他人文章」時才有意義。
    if bad_post_type is not None and (
            check_author or api.ptt_id.lower() == post_info[data_type.PostField.author].lower()):
        raise exceptions.ParameterError(
            'bad_post_type is only valid when a moderator deletes another user\'s post')

    if bad_post_type == data_type.BadPostType.OTHER:
        if not bad_post_reason:
            raise exceptions.ParameterError(
                'bad_post_reason is required when bad_post_type is BadPostType.OTHER')
        if len(bad_post_reason) > 50:
            raise exceptions.ParameterError('bad_post_reason must not exceed 50 characters')
    elif bad_post_reason is not None:
        raise exceptions.ParameterError(
            'bad_post_reason is only valid when bad_post_type is BadPostType.OTHER')

    if check_author:
        if api.ptt_id.lower() != post_info[data_type.PostField.author].lower():
            log.logger.info(i18n.delete_post, '...', i18n.fail)
            raise exceptions.NoPermission(i18n.no_permission)

    _api_util.goto_board(api, board)

    cmd_list = []

    if post_aid is not None:
        cmd_list.append(lib_util.check_aid(post_aid))
    elif post_index != 0:
        cmd_list.append(str(post_index))
    else:
        raise exceptions.ParameterError('post_aid and post_index cannot be None at the same time')

    cmd_list.append(command.enter)
    cmd_list.append('d')

    cmd = ''.join(cmd_list)

    api.confirm = False
    api.bad_post_done = False

    def confirm_delete_handler(screen):
        api.confirm = True

    # A board moderator deleting another user's post gets an extra
    # "R加註理由" option that lets us annotate the title shown after deletion.
    use_reason = bool(reason) and not check_author

    def confirm_delete_response(screen):
        if use_reason and '加註理由' in screen:
            return 'r' + command.enter
        return 'y' + command.enter

    target_list = [
        connect_core.TargetUnit('請按任意鍵繼續', response=' '),
        connect_core.TargetUnit('請確定刪除(Y/N', response=confirm_delete_response,
                                handler=confirm_delete_handler, max_match=1),
    ]

    if use_reason:
        target_list.append(
            connect_core.TargetUnit(
                '請輸入刪除後要顯示的標題',
                response=command.ctrl_e + ' ' + reason + command.enter,
                max_match=1))
        target_list.append(
            connect_core.TargetUnit(
                '請再次確定是否要用上述理由刪除(Y/N',
                response='y' + command.enter,
                max_match=1))

    # A moderator deleting another user's post always gets asked
    # "惡退文章?(y/N)" (record a bad-post strike against the author). Answering
    # 'n' when bad_post_type wasn't requested is what fixes send() timing out
    # for 3 seconds and returning -1 on every moderator delete.
    if not check_author:
        def bad_post_menu_handler(screen):
            api.bad_post_done = True

        target_list.append(
            connect_core.TargetUnit(
                '惡退文章?(y/N',
                response=('y' if bad_post_type else 'n') + command.enter,
                max_match=1))

        if bad_post_type is not None:
            target_list.append(
                connect_core.TargetUnit(
                    '0.取消退文',
                    response=str(int(bad_post_type)) + command.enter,
                    handler=bad_post_menu_handler,
                    max_match=1))

            if bad_post_type == data_type.BadPostType.OTHER:
                target_list.append(
                    connect_core.TargetUnit(
                        '請輸入原因',
                        response=bad_post_reason + command.enter,
                        max_match=1))

    target_list.append(
        connect_core.TargetUnit(screens.Target.InBoard, break_detect=True))

    api.connect_core.send(cmd, target_list)

    if not api.confirm:
        log.logger.info(i18n.delete_post, '...', i18n.fail)
        raise exceptions.NoPermission(i18n.no_permission)

    if bad_post_type is not None and not api.bad_post_done:
        log.logger.warning(
            i18n.bad_post,
            'the post was deleted but PTT did not present the bad-post '
            'menu (it may be too old to badpost); no bad-post record was made')

    log.logger.info(i18n.delete_post, '...', i18n.success)
