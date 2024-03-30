from . import command, _api_util
from . import connect_core
from . import exceptions
from . import i18n
from . import log


def change_pw(api, new_password: str) -> None:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    log.logger.info(i18n.change_pw)

    new_password = new_password[:8]

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append('U')
    cmd_list.append(command.enter)
    cmd_list.append('I')
    cmd_list.append(command.enter)
    cmd_list.append('2')
    cmd_list.append(command.enter)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('設定聯絡信箱後才能修改密碼', exceptions_=exceptions.SetContactMailFirst()),
        connect_core.TargetUnit('您輸入的密碼不正確', exceptions_=exceptions.WrongPassword()),
        connect_core.TargetUnit('請您確定(Y/N)？', response='Y' + command.enter),
        connect_core.TargetUnit('檢查新密碼', response=new_password + command.enter, max_match=1),
        connect_core.TargetUnit('設定新密碼', response=new_password + command.enter, max_match=1),
        connect_core.TargetUnit('輸入原密碼', response=api._ptt_pw + command.enter, max_match=1),
        connect_core.TargetUnit('設定個人資料與密碼', break_detect=True)
    ]

    index = api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout)
    if index < 0:
        ori_screen = api.connect_core.get_screen_queue()[-1]
        raise exceptions.UnknownError(ori_screen)

    api._ptt_pw = new_password

    log.logger.info(i18n.change_pw, '...', i18n.success)
