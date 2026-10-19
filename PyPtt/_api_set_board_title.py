import re

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import lib_util
from . import log
from . import screens


# mbbsd/board.c:641 vgetstr(genbuf, BTLEN-16, ...) with BTLEN=48 gives len=32;
# vkey_purge() clears the input queue one byte early, so the safe limit is 30 Big5 bytes.
_TITLE_MAX_BYTES = 30


def step(api, key: str, targets: list, screen_timeout: float = 0) -> str:
    """送出 key，等到 targets [(name, anchor), ...] 其中之一出現並回傳其 name。

    等不到 (未知畫面) 就退出看板設定並丟 UnknownError，不會再盲送任何鍵。"""
    target_list = [connect_core.TargetUnit(anchor, log_level=log.DEBUG, break_detect=True) for _, anchor in targets]
    index = api.connect_core.send(
        key,
        target_list,
        screen_timeout=screen_timeout or api.config.screen_timeout)
    if 0 <= index < len(targets):
        return targets[index][0]

    # 退出由呼叫端的 _api_util.run_in_board_setting 負責 (含逾時時先重繪)
    raise exceptions.UnknownError(f'unexpected screen after sending {key!r}:\n{_api_util.last_screen(api)}')


def open_board_setting(api, board: str, key: str) -> str:
    """從文章列表打開看板設定並切到可修改狀態。

    新版回傳 'new' (停在編輯模式選單)，舊版回傳 'old' (停在「請輸入要改變的設定」)。"""
    mode = step(api, key, [
        ('new', screens.Target.BoardSettingReadOnly),
        ('view_only', screens.Target.BoardSettingViewOnly),
        ('old', screens.Target.BoardSettingOld),
    ])
    if mode == 'view_only':
        raise exceptions.NeedModeratorPermission(board)

    if mode == 'new':
        step(api, command.ctrl_p, [('edit', screens.Target.BoardSettingEdit)])
    else:
        step(api, command.ctrl_p, [('prompt', screens.Target.BoardSettingOldPrompt)])
    return mode


def close_board_setting(api, mode: str) -> None:
    """從編輯選單 (新版) / 「請輸入要改變的設定」(舊版) 離開並回到文章列表。"""
    step(api, command.left if mode == 'new' else command.enter, [
        ('saved', '◆ 已儲存新設定'),
        ('unchanged', '◆ 未改變任何設定'),
    ], screen_timeout=api.config.screen_long_timeout)
    step(api, command.left, [('board', screens.Target.InBoard)])
    # 中文敘述是板主可設的內容，可能含 InBoard 的子字串；再確認不是設定畫面
    screen = _api_util.last_screen(api)
    if not _api_util.is_article_list(api, screen):
        raise exceptions.UnknownError(f'did not return to the article list:\n{screen}')


def set_board_title(api, board: str, new_title: str) -> None:
    # 第一支板主專用 api
    _api_util.one_thread(api)

    check_value.check_type(board, str, 'board')
    check_value.check_type(new_title, str, 'new_title')
    _api_util.check_no_control_chars(new_title, 'new_title')

    _api_util.goto_board(api, board)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    # mbbsd/board.c:641 vgetstr(genbuf, BTLEN-16, ...) with BTLEN=48 gives
    # len=32; vtuikit.c:1409-1415's vkey_purge() clears the input queue one
    # byte early, so the safe limit is 32-2=30 Big5 bytes, not 31.
    try:
        encoded_new_title = new_title.encode('big5uao')
    except UnicodeEncodeError as e:
        raise exceptions.ParameterError(
            f'new_title contains a character that cannot be encoded in Big5: {e}') from e
    if len(encoded_new_title) > _TITLE_MAX_BYTES:
        raise exceptions.ParameterError(f'new_title must not exceed {_TITLE_MAX_BYTES} bytes')

    _api_util.check_board(
        api,
        board,
        check_moderator=True)

    # check_board() above calls get_board_info(get_post_kind=False) (to look
    # up the moderator list) whenever the board isn't already cached, and
    # that helper reads the board's "《board》看板設定" info screen but never
    # dismisses its trailing "[按任意鍵繼續]" prompt. Left alone, the 'I'
    # below lands on that prompt instead of the board's article-list screen:
    # it gets consumed as the "any key" dismissal, so the following ctrl_p
    # is read as the article-list's own "[Ctrl-P]發表文章" shortcut and the
    # whole command ends up composing a new post instead of opening board
    # settings. Verified live against a moderated board: without this
    # re-navigation the send always lands in the article editor; with it,
    # the confirmation targets below match every time (8/8 in local testing).
    _api_util.goto_board(api, board)

    # 從這裡起進入看板設定；任何結束路徑都由 run_in_board_setting 退回文章列表
    _api_util.run_in_board_setting(api, lambda: _set_title_in_board_setting(api, board, new_title))


def _set_title_in_board_setting(api, board: str, new_title: str) -> None:
    mode = open_board_setting(api, board, 'I')

    prompt = screens.Target.BoardTitlePrompt
    if mode == 'new':
        # 新版預填的是畫面上整串 (含「[類別] 」)；new_title 不含類別，
        # 所以清掉預填後要把類別前綴補回去，否則類別會被洗掉。
        # 2026-10-19 起編輯模式每列多了熱鍵標示: '>  1. (b)中文敘述   [贈送] ...'
        m = re.search(r'^>\s*1\.\s+(?:\(\w\))?中文敘述\s+(.+?)\s*$', _api_util.last_screen(api), re.M)
        if m is None:
            raise exceptions.UnknownError(f'cursor is not on 中文敘述:\n{_api_util.last_screen(api)}')
        current = m.group(1)
        prefix = re.match(r'\[[^\]]+\] ', current)
        text = (prefix.group(0) if prefix else '') + new_title
        # 新版輸入列含類別前綴；欄寬未實測，上限連前綴一起算 (超過就不送任何字)
        if len(text.encode('big5uao', 'replace')) > _TITLE_MAX_BYTES:
            raise exceptions.ParameterError(
                f'category prefix {prefix.group(0)!r} + new_title must not exceed {_TITLE_MAX_BYTES} bytes')
        backspace_count = max(31, len(current) * 2 + 2)
        step(api, command.enter, [('input', f'{prompt} {current}')])
    else:
        # 舊版預填只有 title+7 (不含類別)，最多 30 bytes
        text = new_title
        backspace_count = 31
        step(api, 'b' + command.enter, [('input', prompt)])

    # 清掉預填並輸入新標題 (先不送 Enter)，確認輸入列與預期完全一致才送出
    step(api, command.backspace * backspace_count + text, [('typed', f'{prompt} {text}')])
    m = re.search(re.escape(prompt) + r' (.*)$', _api_util.last_screen(api), re.M)
    if m is None or m.group(1).rstrip() != text.rstrip():
        raise exceptions.UnknownError(f'title input line mismatch:\n{_api_util.last_screen(api)}')

    if mode == 'new':
        step(api, command.enter, [('edit', screens.Target.BoardSettingEdit)])
    else:
        step(api, command.enter, [('prompt', screens.Target.BoardSettingOldPrompt)])

    close_board_setting(api, mode)
