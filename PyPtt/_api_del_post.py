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

# pttbbs input fields cap length in bytes (Big5: 2 bytes per Chinese
# character), not in Python characters.
_BAD_POST_REASON_MAX_BYTES = 50

# --- del_post's `reason` field (annotates the title shown after a
# moderator deletes another user's post) ---
#
# pttbbs pre-fills this prompt with "(已被<moderator id>刪除) <author id>"
# (pttbbs mbbsd/bbs.c, del_post()'s SAFE_ARTICLE_DELETE branch) in a
# `char reason[PROPER_TITLE_LEN]` buffer; PROPER_TITLE_LEN is 42
# (pttbbs include/common.h), so the whole title -- prefix *and* PyPtt's
# reason together -- is capped at 41 Big5 bytes, not python characters.
# PyPtt answers the prompt with Ctrl-E (jump to the end of the prefilled
# text) plus a leading space plus `reason`, so the byte budget actually
# left for `reason` depends on how long the moderator's and the post
# author's PTT IDs are -- there is no single safe constant independent of
# who is deleting what, unlike bad_post_reason above.
#
# Verified live against a local pttbbs (bbsdocker/imageptt rebuilt with
# SAFE_ARTICLE_DELETE enabled -- the stock image ships with that feature
# #define'd out and never offers this prompt at all):
#   - exactly at the budget: reason is accepted in full, title not
#     truncated.
#   - 1 byte over budget, ASCII-only overflow: pttbbs silently truncates
#     to fit (title is just missing the last character).
#   - 1 byte over budget, where the overflow splits a double-byte Big5
#     glyph in half: pttbbs's line editor corrupts and del_post() hangs
#     until connect_core's screen_timeout, returning neither success nor
#     a clean failure -- this is the "刪文失敗" a caller with a too-long
#     reason actually experiences.
# PyPtt must reject before sending in both cases.
_REASON_TITLE_BUFFER_BYTES = 41  # PROPER_TITLE_LEN(42) - 1 byte reserved for the NUL terminator
_REASON_PREFIX_FIXED_BYTES = 13  # Big5 bytes of "(已被刪除) <>", the literal part of "(已被%s刪除) <%s>"
# A rough, moderator/author-id-independent ceiling: the most bytes `reason`
# could ever fit under, i.e. the budget if both PTT ids were the shortest
# possible (1 byte each). Real ids can only be longer than that, which only
# shrinks the true budget further -- so a reason within this ceiling is not
# guaranteed to fit any *particular* id pair, but a reason over it can never
# fit *any* id pair. That asymmetry is what makes it safe to use as an
# early, id-independent guard: it will never reject a reason that might be
# legal once we know the real ids (checked later by _check_reason_budget).
_REASON_MAX_POSSIBLE_BYTES = _REASON_TITLE_BUFFER_BYTES - _REASON_PREFIX_FIXED_BYTES - 1 - 1 - 1


def _check_no_control_chars(name: str, value: str) -> None:
    """Terminal command injection guard: none of PyPtt's del_post text
    parameters may contain control characters (they get typed directly
    into the remote terminal via connect_core.send())."""
    for c in value:
        if ord(c) < 0x20 or ord(c) == 0x7f:
            raise exceptions.ParameterError(
                f'{name} must not contain control characters (found {c!r})')


def _check_bad_post_reason(bad_post_reason: str) -> None:
    _check_no_control_chars('bad_post_reason', bad_post_reason)
    try:
        encoded = bad_post_reason.encode('big5uao')
    except UnicodeEncodeError as e:
        raise exceptions.ParameterError(
            f'bad_post_reason contains a character that cannot be encoded in Big5: {e}') from e
    if len(encoded) > _BAD_POST_REASON_MAX_BYTES:
        raise exceptions.ParameterError(
            f'bad_post_reason must not exceed {_BAD_POST_REASON_MAX_BYTES} bytes')


def _check_reason(reason: str) -> None:
    """Early, post_info-independent guard for `reason`: control chars,
    Big5-encodability, and a rough length ceiling that can never fit any
    moderator/author id pair (_REASON_MAX_POSSIBLE_BYTES). This alone does
    NOT guarantee `reason` fits the *actual* ids involved -- that exact,
    id-dependent budget is enforced later by _check_reason_budget, once
    post_info is available. Keeping this one id-independent lets del_post()
    reject an obviously-broken reason (control chars, non-Big5, absurdly
    long) the same way regardless of whether the target post still exists."""
    _check_no_control_chars('reason', reason)
    try:
        encoded = reason.encode('big5uao')
    except UnicodeEncodeError as e:
        raise exceptions.ParameterError(
            f'reason contains a character that cannot be encoded in Big5: {e}') from e
    if len(encoded) > _REASON_MAX_POSSIBLE_BYTES:
        raise exceptions.ParameterError(
            f'reason must not exceed {_REASON_MAX_POSSIBLE_BYTES} bytes '
            f'(pttbbs caps the deleted-post title at {_REASON_TITLE_BUFFER_BYTES} bytes total; '
            f'{_REASON_MAX_POSSIBLE_BYTES} bytes is the most any reason could ever fit, for the '
            f'shortest possible moderator/author PTT ids -- the actual limit for this delete may '
            f'be smaller)')


def _check_reason_budget(reason: str, moderator_id: str, author_id: str) -> None:
    """Exact, post_info-dependent guard for `reason`: pttbbs pre-fills the
    delete-title prompt with "(已被<moderator_id>刪除) <author_id>" inside the
    fixed-size buffer described above, so the byte budget actually left for
    `reason` depends on the two real PTT IDs involved in this delete --
    unlike _check_bad_post_reason, this can't be a plain module-level
    constant. Call this once post_info is available (see del_post());
    _check_reason above already covers the id-independent checks (control
    chars, Big5-encodability) so this only needs to re-derive the byte
    count for the length comparison."""
    try:
        encoded = reason.encode('big5uao')
    except UnicodeEncodeError as e:
        raise exceptions.ParameterError(
            f'reason contains a character that cannot be encoded in Big5: {e}') from e
    prefix_bytes = _REASON_PREFIX_FIXED_BYTES + len(moderator_id) + len(author_id)
    # -1 for the leading space PyPtt sends before reason (see del_post()).
    max_reason_bytes = max(0, _REASON_TITLE_BUFFER_BYTES - prefix_bytes - 1)
    if len(encoded) > max_reason_bytes:
        raise exceptions.ParameterError(
            f'reason must not exceed {max_reason_bytes} bytes for this moderator/author pair '
            f'(pttbbs caps the deleted-post title at {_REASON_TITLE_BUFFER_BYTES} bytes total, '
            f'and the prefix "(已被{moderator_id}刪除) <{author_id}>" already uses {prefix_bytes} of them)')


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

    # --- Pure parameter validation (doesn't need post_info) happens here,
    # before the "already deleted" early-return below -- an invalid
    # combination of parameters must always fail the same way, regardless of
    # whether the post happens to already be gone. `reason` is checked in
    # two stages for this reason: _check_reason here covers everything that
    # doesn't depend on state (control chars, Big5-encodability, and a
    # rough ceiling no id pair could ever exceed), so those failures are
    # always reported the same way; the *exact* budget depends on the
    # moderator's and the post author's real PTT IDs, so that part
    # (_check_reason_budget) has to wait until post_info is available below
    # -- alongside the other post_info-dependent reason check ("reason is
    # only valid when...") a few lines down. ---
    if reason is not None:
        _check_reason(reason)

    if bad_post_type == data_type.BadPostType.OTHER:
        if not bad_post_reason:
            raise exceptions.ParameterError(
                'bad_post_reason is required when bad_post_type is BadPostType.OTHER')
        _check_bad_post_reason(bad_post_reason)
    elif bad_post_reason is not None:
        raise exceptions.ParameterError(
            'bad_post_reason is only valid when bad_post_type is BadPostType.OTHER')

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

    if check_author:
        if api.ptt_id.lower() != post_info[data_type.PostField.author].lower():
            log.logger.info(i18n.delete_post, '...', i18n.fail)
            raise exceptions.NoPermission(i18n.no_permission)

    # Reaching here with reason still set means: not self-authored (checked
    # above) and permitted (the check_author gate above didn't raise) --
    # i.e. exactly the "moderator deleting someone else's post" case where
    # PTT will actually offer the R加註理由 prompt. Validate reason's exact
    # byte budget now, using the real moderator/author id pair, before any
    # of the interactive delete flow below is sent.
    if reason:
        _check_reason_budget(reason, api.ptt_id, post_info[data_type.PostField.author])

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
    #
    # menu_shown / reason_prompted track whether PTT actually walked us
    # through the bad-post flow: PTT silently skips straight past the "0.取消
    # 退文" menu (e.g. for a post too old to badpost) without any error, so
    # the only way to know whether a bad-post record was actually made is to
    # have observed each step's screen ourselves, rather than assuming the
    # scripted response was consumed.
    menu_shown = False
    reason_prompted = False

    if not check_author:
        def bad_post_menu_handler(screen):
            nonlocal menu_shown
            menu_shown = True

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
                def reason_prompt_handler(screen):
                    nonlocal reason_prompted
                    reason_prompted = True

                target_list.append(
                    connect_core.TargetUnit(
                        '請輸入原因',
                        response=bad_post_reason + command.enter,
                        handler=reason_prompt_handler,
                        max_match=1))

    target_list.append(
        connect_core.TargetUnit(screens.Target.InBoard, break_detect=True))

    result = api.connect_core.send(cmd, target_list)

    if not api.confirm:
        log.logger.info(i18n.delete_post, '...', i18n.fail)
        raise exceptions.NoPermission(i18n.no_permission)

    # api.confirm being True means PTT already accepted the delete
    # confirmation ('y' to "請確定刪除(Y/N)") -- the post itself is gone at
    # this point in PTT's flow regardless of what happens afterwards (the
    # bad-post menu, or simply returning to the board screen). A timeout
    # (-1) after that point means send() never reached screens.Target.InBoard,
    # so we can't blindly log success as before -- but we *can* say the
    # delete succeeded and, if a bad-post record was requested, that it
    # wasn't confirmed.
    timed_out = result == -1

    log.logger.info(i18n.delete_post, '...', i18n.success)

    if bad_post_type is not None:
        reason_ok = bad_post_type != data_type.BadPostType.OTHER or reason_prompted
        api.bad_post_done = bool(menu_shown and reason_ok and not timed_out)
        if not api.bad_post_done:
            raise exceptions.BadPostNotRecorded(i18n.bad_post_not_recorded)
    elif timed_out:
        raise exceptions.UnknownError(
            'delete succeeded, but PTT never returned to the board screen '
            'afterwards (timeout)')
