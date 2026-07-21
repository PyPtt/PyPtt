from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import lib_util
from . import log


def set_signature_file(api, content: str) -> None:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    check_value.check_type(content, str, 'content')

    log.logger.info(i18n.set_signature_file)

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append('U')
    cmd_list.append(command.enter)
    cmd_list.append('M')
    cmd_list.append(command.enter)
    cmd_list.append('Q')
    cmd_list.append(command.enter)
    cmd = ''.join(cmd_list)

    target_list = [
        # Existing signature file -> getans asks Delete/Edit/Cancel first.
        # max_match=1: the echoed prompt text can linger on the next
        # screen refresh while waiting for the editor to draw (same
        # quirk documented for '確定要儲存檔案嗎' in _api_post.py); without
        # it this would re-fire 'E' + Enter into the editor buffer.
        connect_core.TargetUnit('名片 (D)刪除', response='E' + command.enter, max_match=1),
        # Empty signature file skips the getans prompt and opens the
        # editor directly.
        connect_core.TargetUnit('編輯文章', break_detect=True),
    ]
    index = api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout)
    if index < 0:
        ori_screen = api.connect_core.get_screen_queue()[-1]
        raise exceptions.UnknownError(ori_screen)

    content = lib_util.uniform_new_line(content)

    cmd_list = []
    # ponytail: unlike post's blank template, the card-file editor preloads
    # the account's existing signature file, so it has to be cleared line by
    # line before writing the new content. ctrl_y*60 is a "clear up to 60
    # pre-loaded lines" ceiling -- bump it if a real card file ever runs
    # longer than that.
    cmd_list.append(command.ctrl_y * 60)
    cmd_list.append(content)
    cmd_list.append(command.ctrl_x)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('確定要儲存檔案嗎', response='s' + command.enter, max_match=1),
        connect_core.TargetUnit('名片更新完畢', break_detect=True),
    ]
    index = api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout)
    if index < 0:
        ori_screen = api.connect_core.get_screen_queue()[-1]
        raise exceptions.UnknownError(ori_screen)

    # The leading space in go_main_menu dismisses the "請按任意鍵繼續" banner
    # left by the save; the trailing left-arrows walk back out of the
    # 個人設定/個人檔案 submenus to the main menu.
    target_list = [
        connect_core.TargetUnit('主功能表', break_detect=True),
    ]
    api.connect_core.send(
        command.go_main_menu,
        target_list,
        screen_timeout=api.config.screen_long_timeout)

    log.logger.info(i18n.set_signature_file, '...', i18n.success)
