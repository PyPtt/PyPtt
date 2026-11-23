import re

from . import _api_set_board_title
from . import _api_util
from . import check_value
from . import command
from . import exceptions
from . import i18n
from . import lib_util
from . import log
from . import screens
from ._api_set_board_title import step

# 看板設定 (編輯模式) →「[管理] 文章類別設定」的流程 (PTT1 2026-11 實錄)：
#
#   c → 類別編輯器 (每行一個類別)             Ctrl-X → 確定要儲存檔案嗎？
#     → (A)放棄：類別不動                      → 要編輯現有類別的範本嗎？(y/N)
#     → y → 文章類別範本設定 (類別｜有/無｜範本內容預覽)
#     → 游標移到類別，Enter → 範本編輯器 (預載目前範本)
#     → Ctrl-Y 清空、打入新範本，Ctrl-X → 確定要儲存檔案嗎？ → s 存檔
#     → 回到範本設定 → q 回到編輯選單
#
# 類別清單本身一律「放棄」不存：這支 API 只換範本，不改類別。
_CATEGORY_EDITOR = '每一行代表一個類別'
_SAVE_PROMPT = '確定要儲存檔案嗎'
_ASK_TEMPLATE = '要編輯現有類別的範本嗎'
_TEMPLATE_LIST = '文章類別範本設定'
_EDITOR = '編輯文章'

# 「>  贈送    有    1.贈送前請詳看板規…」
_ROW = re.compile(r'^([> ])\s+(\S+)\s+(有|無)(?:\s+(.*))?$')

# 清空編輯器時每批送出的 Ctrl-Y 數；送完檢查畫面，還有內容就再送一批
_CLEAR_BATCH = 50
_CLEAR_MAX_BATCHES = 20


def _template_rows(screen: str) -> list:
    """範本設定畫面上的 [(是否游標所在, 類別, 有無範本, 預覽), ...]。"""
    rows = []
    for line in screen.split('\n'):
        match = _ROW.match(line.rstrip())
        if match:
            rows.append((match.group(1) == '>', match.group(2), match.group(3), match.group(4) or ''))
    return rows


def _editor_is_empty(screen: str) -> bool:
    """編輯器畫面除了頁尾之外只剩空行與「~」。"""
    lines = screen.split('\n')
    body = [line for line in lines if _EDITOR not in line]
    return all(line.strip() in ('', '~') for line in body)


def _check_content(content: str) -> None:
    for c in content:
        if c in '\r\n':
            continue
        if ord(c) < 0x20 or ord(c) == 0x7f:
            raise exceptions.ParameterError(f'content must not contain control characters (found {c!r})')
    try:
        content.encode('big5uao')
    except UnicodeEncodeError as e:
        raise exceptions.ParameterError(f'content contains a character that cannot be encoded in Big5: {e}') from e


def set_post_template(api, board: str, post_type: str, content: str) -> None:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(board, str, 'board')
    check_value.check_type(post_type, str, 'post_type')
    check_value.check_type(content, str, 'content')
    _api_util.check_no_control_chars(post_type, 'post_type')
    _check_content(content)
    if not post_type:
        raise exceptions.ParameterError('post_type must not be empty')

    _api_util.check_board(api, board, check_moderator=True)
    _api_util.goto_board(api, board)

    log.logger.info(i18n.set_post_template)
    content = lib_util.uniform_new_line(content)
    _api_util.run_in_board_setting(api, lambda: _set_template_in_board_setting(api, board, post_type, content))
    log.logger.info(i18n.set_post_template, '...', i18n.success)


def _set_template_in_board_setting(api, board: str, post_type: str, content: str) -> None:
    mode = _api_set_board_title.open_board_setting(api, board, 'i')
    if mode != 'new':
        raise exceptions.UnknownError('set_post_template only supports the new (2026-10) board setting menu')

    # 類別編輯器：不改類別，直接放棄，接著 PTT 會問要不要編輯範本
    step(api, 'c', [('categories', _CATEGORY_EDITOR)])
    step(api, command.ctrl_x, [('save', _SAVE_PROMPT)])
    step(api, 'a' + command.enter, [('ask', _ASK_TEMPLATE)])
    step(api, 'y' + command.enter, [('list', _TEMPLATE_LIST)])

    rows = _template_rows(_api_util.last_screen(api))
    names = [name for _, name, _, _ in rows]
    if post_type not in names:
        raise exceptions.ParameterError(f'board {board} has no post type {post_type!r} (has: {names})')
    current = next((i for i, (is_cursor, _, _, _) in enumerate(rows) if is_cursor), None)
    if current is None:
        raise exceptions.UnknownError(f'cursor not found on the template list:\n{_api_util.last_screen(api)}')
    target = names.index(post_type)
    if target != current:
        key = command.down * (target - current) if target > current else command.up * (current - target)
        step(api, key, [('list', _TEMPLATE_LIST)])
        rows = _template_rows(_api_util.last_screen(api))
        if not any(is_cursor and name == post_type for is_cursor, name, _, _ in rows):
            raise exceptions.UnknownError(f'cursor did not reach {post_type}:\n{_api_util.last_screen(api)}')

    # 範本編輯器會預載目前的範本：清空到畫面上只剩「~」才打入新內容
    step(api, command.enter, [('editor', _EDITOR)])
    # 至少先清一批：剛開啟時畫面可能還沒畫完，不能憑第一張畫面判斷已經是空的
    for _ in range(_CLEAR_MAX_BATCHES):
        step(api, command.ctrl_y * _CLEAR_BATCH, [('editor', _EDITOR)])
        if _editor_is_empty(_api_util.last_screen(api)):
            break
    else:
        raise exceptions.UnknownError('could not clear the existing template')

    step(api, content + command.ctrl_x, [('save', _SAVE_PROMPT)], screen_timeout=api.config.screen_long_timeout)
    step(api, 's' + command.enter, [('list', _TEMPLATE_LIST)], screen_timeout=api.config.screen_long_timeout)

    rows = _template_rows(_api_util.last_screen(api))
    if not any(name == post_type and has == '有' for _, name, has, _ in rows):
        raise exceptions.UnknownError(f'template for {post_type} was not saved:\n{_api_util.last_screen(api)}')

    step(api, 'q', [('edit', screens.Target.BoardSettingEdit)])
    _api_set_board_title.close_board_setting(api, mode)
