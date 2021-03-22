try:
    from . import lib_util
except ModuleNotFoundError:
    import lib_util


class language(object):
    CHINESE: int = 1
    ENGLISH: int = 2

    min_value = CHINESE
    max_value = ENGLISH


languageList = [
    language.CHINESE,
    language.ENGLISH,
]


def specific_load(input_language, lang_list):
    global languageList

    if len(languageList) != len(lang_list):
        raise ValueError('SpecificLoad LangList length error')

    if input_language not in languageList:
        raise ValueError('SpecificLoad unknown language', input_language)
    return lang_list[languageList.index(input_language)]


def replace(string, *args):
    # for i in range(len(args)):
    for i, _ in enumerate(args):
        target = str(args[i])
        string = string.replace('{Target' + str(i) + '}', target)
    return string


chinese_traditional_module = None
english_module = None
init = None
connect_host = None
PTT = None
PTT2 = None
localhost = None
must_be_a_string = None
must_be_a_integer = None
must_be_a_boolean = None
unknown = None
must_bigger_than = None
must_small_than = None
must_between = None
connect_core = None
use_too_many_resources = None
prepare_connect_again = None
active = None
connect_mode = None
connect_mode_TELNET = None
connect_mode_WEBSOCKET = None
fail = None
connect = None
hide_sensitive_info = None
send_msg = None
ptt_msg = None
spend_time = None
kick_other_login = None
not_kick_other_login = None
login_id = None
mail_box = None
login_success = None
go_main_menu = None
wrong_id_pw = None
login_too_often = None
system_busy_try_later = None
del_wrong_pw_record = None
post_not_finish = None
in_login_process_please_wait = None
any_key_continue = None
update_sync_online_user_friend_list = None
error_login_rich_people_go_main_menu = None
skip_registration_form = None
only_secure_connection = None
debug = None
info = None
out_side = None
new_cursor = None
old_cursor = None
logout_success = None
logout = None
complete = None
query_ptt_time_success = None


def load(lang):
    if not lib_util.check_range(language, lang):
        raise ValueError('Language', lang)

    global query_ptt_time_success
    query_ptt_time_success = specific_load(lang, [
        '取得批踢踢時間成功',
        'query ptt time success',
    ])

    global complete
    complete = specific_load(lang, [
        '完成',
        'complete',
    ])

    global logout
    logout = specific_load(lang, [
        '登出',
        'logout',
    ])

    global logout_success
    logout_success = specific_load(lang, [
        '登出成功',
        'logout success',
    ])

    global new_cursor
    new_cursor = specific_load(lang, [
        '新式游標',
        'new cursor',
    ])

    global old_cursor
    old_cursor = specific_load(lang, [
        '舊式游標',
        'old cursor',
    ])

    global debug
    debug = specific_load(lang, [
        '除錯',
        'dbug',
    ])

    global info
    info = specific_load(lang, [
        '資訊',
        'Info',
    ])

    global out_side
    out_side = specific_load(lang, [
        '外部',
        'out',
    ])

    global only_secure_connection
    only_secure_connection = specific_load(lang, [
        '跳過填寫註冊單',
        'skip registration form',
    ])

    global skip_registration_form
    skip_registration_form = specific_load(lang, [
        '跳過填寫註冊單',
        'skip registration form',
    ])

    global error_login_rich_people_go_main_menu
    error_login_rich_people_go_main_menu = specific_load(lang, [
        '錯誤登入到大富翁排行榜，回到主選單',
        'error login rich people, go main menu',
    ])

    global update_sync_online_user_friend_list
    update_sync_online_user_friend_list = specific_load(lang, [
        '正在更新與同步線上使用者及好友名單',
        'update sync online user friend list',
    ])

    global any_key_continue
    any_key_continue = specific_load(lang, [
        '任意鍵繼續',
        'any key to continue',
    ])

    global in_login_process_please_wait
    in_login_process_please_wait = specific_load(lang, [
        '登入中，請稍候',
        'in login process, please wait',
    ])

    global post_not_finish
    post_not_finish = specific_load(lang, [
        '文章尚未完成',
        'post is not finish',
    ])

    global del_wrong_pw_record
    del_wrong_pw_record = specific_load(lang, [
        '刪除錯誤密碼嘗試紀錄',
        'delete error password record',
    ])

    global system_busy_try_later
    system_busy_try_later = specific_load(lang, [
        '系統繁忙，請稍後再試',
        'system busy, try later',
    ])

    global login_too_often
    login_too_often = specific_load(lang, [
        '登入太頻繁',
        'login too often',
    ])

    global wrong_id_pw
    wrong_id_pw = specific_load(lang, [
        '帳號密碼錯誤',
        'wrong id or pw',
    ])

    global go_main_menu
    go_main_menu = specific_load(lang, [
        '回到主選單',
        'go to main menu',
    ])

    global login_success
    login_success = specific_load(lang, [
        '登入成功',
        'login success',
    ])

    global mail_box
    mail_box = specific_load(lang, [
        '郵件信箱',
        'mail box',
    ])

    global login_id
    login_id = specific_load(lang, [
        '登入帳號',
        'login id',
    ])

    global not_kick_other_login
    not_kick_other_login = specific_load(lang, [
        '不剔除其他登入',
        'not kick other login',
    ])

    global kick_other_login
    kick_other_login = specific_load(lang, [
        '剔除其他登入',
        'kick other login',
    ])

    global spend_time
    spend_time = specific_load(lang, [
        '花費時間',
        'spend time',
    ])

    global ptt_msg
    ptt_msg = specific_load(lang, [
        '批踢踢訊息',
        'ptt msg',
    ])

    global send_msg
    send_msg = specific_load(lang, [
        '送出訊息',
        'send msg',
    ])

    global hide_sensitive_info
    hide_sensitive_info = specific_load(lang, [
        '隱藏敏感資訊',
        'hide sensitive info'])

    global connect
    connect = specific_load(lang, [
        '連線',
        'connect'])

    global fail
    fail = specific_load(lang, [
        '失敗',
        'fail'])

    global connect_mode_WEBSOCKET
    connect_mode_WEBSOCKET = specific_load(lang, [
        'WebSocket',
        'WebSocket'])

    global connect_mode_TELNET
    connect_mode_TELNET = specific_load(lang, [
        'Telnet',
        'Telnet'])

    global connect_mode
    connect_mode = specific_load(lang, [
        '連線模式',
        'connect mode'])

    global active
    active = specific_load(lang, [
        '啟動',
        'active'])

    global prepare_connect_again
    prepare_connect_again = specific_load(lang, [
        '準備再次連線',
        'prepare connect again'])

    global use_too_many_resources
    use_too_many_resources = specific_load(lang, [
        '耗用過多資源',
        'use too many resources'])

    global connect_core
    connect_core = specific_load(lang, [
        '連線核心',
        'connect core'])

    global must_small_than
    must_small_than = specific_load(lang, [
        '必須小於',
        'must smaller than'])

    global must_between
    must_between = specific_load(lang, [
        '必須介於',
        'must between'])

    global must_bigger_than
    must_bigger_than = specific_load(lang, [
        '必須大於',
        'must bigger than'])

    global unknown
    unknown = specific_load(lang, [
        '不明的',
        'unknown'])

    global must_be_a_boolean
    must_be_a_boolean = specific_load(lang, [
        '必須為布林值',
        'must be a boolean'])

    global must_be_a_integer
    must_be_a_integer = specific_load(lang, [
        '必須為數字',
        'must be a integer'])

    global must_be_a_string
    must_be_a_string = specific_load(lang, [
        '必須為字串',
        'must be a string'])

    global chinese_traditional_module
    chinese_traditional_module = specific_load(lang, [
        '繁體中文語言模組',
        'Traditional Chinese language module'])

    global english_module
    english_module = specific_load(lang, [
        '英文語言模組',
        'English language module'])

    global init
    init = specific_load(lang, [
        '初始化',
        'Init'])

    global connect_host
    connect_host = specific_load(lang, [
        '連線主機',
        'Connect host'])

    global PTT
    PTT = specific_load(lang, [
        '批踢踢',
        'PTT'])

    global PTT2
    PTT2 = specific_load(lang, [
        '批踢踢兔',
        'PTT2'])

    global localhost
    localhost = specific_load(lang, [
        '本機',
        'Localhost'])

    ##############################################

    # No changes have been made to any settings

    # Quote original

    # global List
    # List = list()

    # for k, v in globals().items():
    #     # System Var
    #     if k.startswith('_'):
    #         continue

    #     print(f'k {k}')
    #     print(f'v {v}')
    #     if isinstance(k, str) and isinstance(v, str):
    #         List.append(k)


def _createlist():
    i18nStrList = list()

    for k, v in globals().items():
        # System Var
        if k.startswith('_'):
            continue
        if isinstance(k, str) and isinstance(v, str):
            i18nStrList.append(k)

    with open('i18n.txt', 'w') as F:
        F.write('\n'.join(i18nStrList))


if __name__ == '__main__':
    load(language.CHINESE)
    _createlist()
