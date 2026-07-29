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
        # 只比對「新密碼」/「原密碼」, 不含前後綴與冒號: 正式站目前是「請設定新密碼：」
        # 「請檢查新密碼：」「請輸入原密碼：」(全形冒號), pttbbs #112 之後上游改成兩步同名的
        # 「新密碼:」(半形), 兩種寫法都涵蓋。新密碼要吃設定與確認兩次, 故 max_match=2。
        # 「新密碼」必須排在「原密碼」前面: 新版輸入完原密碼後該行仍留在畫面上, 兩者會同時出現。
        connect_core.TargetUnit('新密碼', response=new_password + command.enter, max_match=2, secret=True),
        connect_core.TargetUnit('原密碼', response=api._ptt_pw + command.enter, max_match=1, secret=True),
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
