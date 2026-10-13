import re

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import log
from . import screens


def logout(api) -> None:
    _api_util.one_thread(api)

    log.logger.info(i18n.logout)
    if not api._is_login:
        _abort_pending_otp(api)
        log.logger.info(i18n.logout, '...', i18n.success)
        return

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append('g')
    cmd_list.append(command.enter)
    cmd_list.append('y')
    cmd_list.append(command.enter)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('任意鍵', break_detect=True),
    ]

    try:
        api.connect_core.send(cmd, target_list)
        api.connect_core.close()
    except exceptions.ConnectionClosed:
        pass
    except RuntimeError:
        pass

    api._is_login = False

    log.logger.info(i18n.logout, '...', i18n.success)


# PTT 兩階段驗證畫面, 字串取自 pttbbs daemon/logind/logind.c 與 mbbsd/mbbsd.c。
# logind 與 mbbsd 的提示字串在「或」後面差一個空白, 只比對共同前綴。
_otp_prompt = '請輸入兩階段(2FA)驗證碼'
# logind: 「驗證碼錯誤！請確認後重新輸入。」; mbbsd: 「驗證碼錯誤。請確定在時限前輸入完畢。」
_otp_wrong_code = '驗證碼錯誤'
# mbbsd 錯 5 次後的訊息; logind 錯滿 LOGINATTEMPTS 次則直接送 goodbye 畫面並斷線。
_otp_too_many_failures = '兩階段驗證失敗次數過多'

_otp_pattern = re.compile(r'\d{6}|\d{8}')


def _abort_pending_otp(api) -> None:
    if not api._pending_otp:
        return
    api._pending_otp = False
    try:
        api.connect_core.close()
    except (exceptions.ConnectionClosed, RuntimeError):
        pass


def _login_target_list(api, otp_targets: list) -> list:
    def kick_other_login_response(screen):
        return ('y' if api.config.kick_other_session else 'n') + command.enter

    def register_processing(screen):
        pattern = re.compile(r'[\d]+')
        api.process_picks = int(pattern.search(screen).group(0))

    return [
        connect_core.TargetUnit(screens.Target.InMailBox,
                                response=command.go_main_menu + 'A' + command.right + command.left, break_detect=True),
        connect_core.TargetUnit(screens.Target.InMailMenu, response=command.go_main_menu),
        connect_core.TargetUnit(screens.Target.MainMenu, break_detect=True),
        connect_core.TargetUnit('【看板列表】', response=command.go_main_menu),
        connect_core.TargetUnit('密碼不對', break_detect=True, exceptions_=exceptions.WrongIDorPassword()),
        connect_core.TargetUnit('請重新輸入', break_detect=True, exceptions_=exceptions.WrongIDorPassword()),
        connect_core.TargetUnit('登入太頻繁', response=' '),
        connect_core.TargetUnit('系統過載', break_detect=True),
        connect_core.TargetUnit('您要刪除以上錯誤嘗試的記錄嗎', response='y' + command.enter),
        connect_core.TargetUnit('請選擇暫存檔 (0-9)[0]', response=command.enter),
        connect_core.TargetUnit('有一篇文章尚未完成', response='Q' + command.enter),
        connect_core.TargetUnit(
            '請重新設定您的聯絡信箱', break_detect=True, exceptions_=exceptions.ResetYourContactEmail()),
        connect_core.TargetUnit('密碼正確'),
        connect_core.TargetUnit('您想刪除其他重複登入的連線嗎', response=kick_other_login_response),
        connect_core.TargetUnit('◆ 您的註冊申請單尚在處理中', response=command.enter, handler=register_processing),
        # 需排在「任意鍵」等泛用 catch-all 之前, 否則會被搶先命中而吃不到這幾條。
        *otp_targets,
        connect_core.TargetUnit('任意鍵', response=' '),
        connect_core.TargetUnit('正在更新與同步線上使用者及好友名單'),
        connect_core.TargetUnit('【分類看板】', response=command.go_main_menu),
        connect_core.TargetUnit([
            '大富翁',
            '排行榜',
            '名次',
            '代號',
            '暱稱',
            '數目'
        ], response=command.go_main_menu),
        connect_core.TargetUnit([
            '熱門話題'
        ], response=command.go_main_menu),
        connect_core.TargetUnit('您確定要填寫註冊單嗎', response=command.enter * 3),
        connect_core.TargetUnit('以上資料是否正確', response='y' + command.enter),
        connect_core.TargetUnit('另外若輸入後發生認證碼錯誤請先確認輸入是否為最後一封', response='x' + command.enter),
        connect_core.TargetUnit('此帳號已設定為只能使用安全連線', exceptions_=exceptions.OnlySecureConnection())
    ]


def login(api, ptt_id: str, ptt_pw: str, kick_other_session: bool) -> None:
    _api_util.one_thread(api)

    check_value.check_type(ptt_id, str, 'ptt_id')
    check_value.check_type(ptt_pw, str, 'password')
    check_value.check_type(kick_other_session, bool, 'kick_other_session')

    if api._is_login:
        api.logout()
        api._is_login = False
    # 上一次 login() 停在兩階段驗證畫面卻沒有 submit_otp(), 放棄那條連線重新來過。
    _abort_pending_otp(api)

    api.config.kick_other_session = kick_other_session

    api.is_mailbox_full = False

    ptt_id = ptt_id[:12].strip()
    # 不截斷密碼: 舊版 PTT 由 server 端忽略第 8 字之後的部分, 新版 (pttbbs #112, bcrypt)
    # 則支援 72 字元, 兩邊都必須送出完整密碼才會正確。
    ptt_pw = ptt_pw.strip()

    api.ptt_id = ptt_id
    api._ptt_pw = ptt_pw

    api.connect_core.connect()

    log.logger.info(i18n.login_id, ptt_id)

    otp_prompt_target = connect_core.TargetUnit(_otp_prompt, break_detect=True)
    target_list = _login_target_list(api, [otp_prompt_target])

    # IAC = '\xff'
    # WILL = '\xfb'
    # NAWS = '\x1f'

    cmd_list = []
    # cmd_list.append(IAC + WILL + NAWS)
    cmd_list.append(ptt_id + ',')
    cmd_list.append(command.enter)
    cmd_list.append(ptt_pw)
    cmd_list.append(command.enter)

    cmd = ''.join(cmd_list)

    index = api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout,
        refresh=False,
        secret=True)

    if index == target_list.index(otp_prompt_target):
        # 連線保留在驗證碼輸入畫面, 交給 app 取得驗證碼後呼叫 submit_otp()。
        api._pending_otp = True
        raise exceptions.TwoFactorAuthRequired(ptt_id, data_type.TwoFactorAuthReason.FIRST)

    _finish_login(api, index)


def submit_otp(api, otp: str) -> None:
    _api_util.one_thread(api)

    # 不用 check_value.check_type: 它會把值印進錯誤訊息, 驗證碼不該出現在 log 或例外裡。
    if not isinstance(otp, str):
        raise TypeError(f'[PyPtt] otp {i18n.must_be_a_string}')
    otp = otp.strip()
    if not _otp_pattern.fullmatch(otp):
        raise exceptions.ParameterError(i18n.otp_format_error)

    if not api._pending_otp:
        raise exceptions.RequireLogin(i18n.no_pending_two_factor_auth)

    otp_targets = [
        # 驗證碼錯誤時 PTT 會在錯誤訊息下方重畫輸入提示, 所以這裡只認錯誤訊息,
        # 不放輸入提示本身, 否則重畫的提示會被誤判成第一次要求。
        connect_core.TargetUnit(_otp_too_many_failures, break_detect=True,
                                exceptions_=exceptions.TwoFactorAuthFailed()),
        connect_core.TargetUnit(_otp_wrong_code, break_detect=True,
                                exceptions_=exceptions.TwoFactorAuthRequired(
                                    api.ptt_id, data_type.TwoFactorAuthReason.WRONG_CODE)),
    ]
    target_list = _login_target_list(api, otp_targets)

    try:
        index = api.connect_core.send(
            otp + command.enter,
            target_list,
            screen_timeout=api.config.screen_long_timeout,
            refresh=False,
            secret=True)
    except exceptions.TwoFactorAuthRequired:
        # 驗證碼錯誤: 連線仍停在輸入畫面, 讓 app 再呼叫一次 submit_otp()。
        raise
    except exceptions.ConnectionClosed as e:
        # logind 錯滿 LOGINATTEMPTS 次會送 goodbye 畫面並直接斷線。
        api._pending_otp = False
        raise exceptions.TwoFactorAuthFailed() from e
    except Exception:
        _abort_pending_otp(api)
        raise

    api._pending_otp = False
    _finish_login(api, index)


def _finish_login(api, index: int) -> None:
    if index == 0:

        current_capacity, max_capacity = _api_util.get_mailbox_capacity(api)

        log.logger.info(i18n.has_new_mail_goto_main_menu)

        if current_capacity > max_capacity:
            api.is_mailbox_full = True
            log.logger.info(i18n.mail_box_full)

        if api.is_mailbox_full:
            log.logger.info(i18n.use_mailbox_api_will_logout_after_execution)

        target_list = [
            connect_core.TargetUnit(screens.Target.MainMenu, break_detect=True)
        ]

        cmd = command.go_main_menu + 'A' + command.right + command.left

        index = api.connect_core.send(
            cmd,
            target_list,
            screen_timeout=api.config.screen_long_timeout,
            secret=True)

    ori_screen = api.connect_core.get_screen_queue()[-1]

    is_login = all(t in ori_screen for t in screens.Target.MainMenu)

    if not is_login:
        raise exceptions.LoginError()

    if '> (' in ori_screen:
        api.cursor = data_type.Cursor.NEW
        log.logger.debug(i18n.new_cursor)
    elif '●(' in ori_screen:
        api.cursor = data_type.Cursor.OLD
        log.logger.debug(i18n.old_cursor)
    else:
        raise exceptions.UnknownError()

    screens.Target.InBoardWithCursor = screens.Target.InBoardWithCursor[:screens.Target.InBoardWithCursorLen]
    screens.Target.InBoardWithCursor.append(api.cursor)

    screens.Target.InMailBoxWithCursor = screens.Target.InMailBoxWithCursor[:screens.Target.InMailBoxWithCursorLen]
    screens.Target.InMailBoxWithCursor.append(api.cursor)

    screens.Target.CursorToGoodbye = screens.Target.CursorToGoodbye[:len(screens.Target.MainMenu)]
    if api.cursor == '>':
        screens.Target.CursorToGoodbye.append('> (G)oodbye')
    else:
        screens.Target.CursorToGoodbye.append('●(G)oodbye')

    unregistered_user = True
    if '(T)alk' in ori_screen:
        unregistered_user = False
    if '(P)lay' in ori_screen:
        unregistered_user = False
    if '(N)amelist' in ori_screen:
        unregistered_user = False

    if unregistered_user:
        log.logger.info(i18n.unregistered_user_cant_use_all_api)

    api.is_registered_user = not unregistered_user

    if api.process_picks != 0:
        log.logger.info(i18n.picks_in_register, api.process_picks)

    api._is_login = True
    log.logger.info(i18n.login_success)
