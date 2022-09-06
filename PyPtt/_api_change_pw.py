from SingleLog import Logger

from . import command, _api_util
from . import connect_core
from . import exceptions
from . import i18n


def change_pw(api, new_password: str) -> None:
    _api_util.one_thread(api)

    logger = Logger('api', api.config.log_level)

    if not api._is_login:
        raise exceptions.Requirelogin(i18n.require_login)

    logger.info(i18n.change_pw)

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
        connect_core.TargetUnit(
            i18n.set_connect_mail_first,
            '設定聯絡信箱後才能修改密碼',
            exceptions_=exceptions.SetConnectMailFirst()),
        connect_core.TargetUnit(
            i18n.error_pw,
            '您輸入的密碼不正確',
            exceptions_=exceptions.WrongPassword()),
        connect_core.TargetUnit(
            i18n.confirm,
            '請您確定(Y/N)？',
            response='Y' + command.enter),
        connect_core.TargetUnit(
            i18n.check_new_password,
            '檢查新密碼',
            response=new_password + command.enter,
            max_match=1),
        connect_core.TargetUnit(
            i18n.input_new_password,
            '設定新密碼',
            response=new_password + command.enter,
            max_match=1),
        connect_core.TargetUnit(
            i18n.input_origin_password,
            '輸入原密碼',
            response=api._ptt_pw + command.enter,
            max_match=1),
        connect_core.TargetUnit(
            i18n.done,
            '設定個人資料與密碼',
            break_detect=True)
    ]

    index = api.connect_core.send(
        cmd,
        target_list,
    )
    if index < 0:
        raise exceptions.Timeout

    api._ptt_pw = new_password

    logger.stage(i18n.success)
