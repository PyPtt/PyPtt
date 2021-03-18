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


def load(lang):
    if not lib_util.check_range(language, lang):
        raise ValueError('Language', lang)

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
