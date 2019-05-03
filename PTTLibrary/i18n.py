from time import gmtime, strftime

try:
    from . import DataType
    from . import Util
    from . import Exceptions
except:
    import DataType
    import Util
    import Exceptions


class Language(object):

    Chinese = 1
    English = 2

    MinValue = Chinese
    MaxValue = English


LanguageList = [
    Language.Chinese,
    Language.English,
]


def SpecificLoad(inputLanguage, LangList):
    global LanguageList

    if len(LanguageList) != len(LangList):
        raise Exceptions.ParameterError('SpecificLoad LangList legnth error')
    
    if inputLanguage not in LanguageList:
        raise Exceptions.ParameterError('SpecificLoad Unknow language',
                                        inputLanguage)
    return LangList[LanguageList.index(inputLanguage)]


def load(inputLanguage):
    if not Util.checkRange(Language, inputLanguage):
        Log.showValue(Log.Level.INFO, 'Error Language valve', inputLanguage)
        raise Exceptions.ParameterError('Language', inputLanguage)
    
    global Connect
    Connect = SpecificLoad(inputLanguage, [
        '連線',
        'Connect',
    ])

    global Start
    Start = SpecificLoad(inputLanguage, [
        '開始',
        'Start',
    ])

    global ConnectMode
    ConnectMode = SpecificLoad(inputLanguage, [
        Connect + '模式',
        Connect + 'mode',
    ])
    
    global ConnectMode_Telnet
    ConnectMode_Telnet = SpecificLoad(inputLanguage, [
        'Telnet',
        'Telnet',
    ])
    
    global ConnectMode_WebSocket
    ConnectMode_WebSocket = SpecificLoad(inputLanguage, [
        'WebSocket',
        'WebSocket',
    ])

    global Active
    Active = SpecificLoad(inputLanguage, [
        '啟動',
        'Active',
    ])
    
    global ErrorParameter
    ErrorParameter = SpecificLoad(inputLanguage, [
        '參數錯誤',
        'Wrong parameter',
    ])
    
    global ConnectCore
    ConnectCore = SpecificLoad(inputLanguage, [
        '連線核心',
        'Connect Core',
    ])
    
    global PTT
    PTT = SpecificLoad(inputLanguage, [
        '批踢踢',
        'PTT',
    ])
    
    global Init
    Init = SpecificLoad(inputLanguage, [
        '初始化',
        'initialize',
    ])

    global Done
    Done = SpecificLoad(inputLanguage, [
        '完成',
        'Done',
    ])

    global i18n
    i18n = SpecificLoad(inputLanguage, [
        '多國語系',
        'i18n',
    ])
    
    global Library
    Library = SpecificLoad(inputLanguage, [
        '函式庫',
        'Library',
    ])
    
    global Fail
    Fail = SpecificLoad(inputLanguage, [
        '失敗',
        'Fail',
    ])

    global Success
    Success = SpecificLoad(inputLanguage, [
        '成功',
        'Success',
    ])
    
    global Prepare
    Prepare = SpecificLoad(inputLanguage, [
        '準備',
        'Prepare',
    ])
    
    global Info
    Info = SpecificLoad(inputLanguage, [
        '資訊',
        'INFO',
    ])
    
    global Debug
    Debug = SpecificLoad(inputLanguage, [
        '除錯',
        'DBUG',
    ])
    
    global Again
    Again = SpecificLoad(inputLanguage, [
        '重新',
        'Re',
    ])
    
    global ErrorIDPW
    ErrorIDPW = SpecificLoad(inputLanguage, [
        '密碼不對或無此帳號',
        'Wrong password or no such id',
    ])
    
    global ScreenNoMatchTarget
    ScreenNoMatchTarget = SpecificLoad(inputLanguage, [
        '此畫面無法辨識',
        'This screen is not recognized',
    ])

    global SigningUnPleaseWait
    SigningUnPleaseWait = SpecificLoad(inputLanguage, [
        '登入中，請稍候',
        'Signing in, please wait',
    ])

    global Msg
    Msg = SpecificLoad(inputLanguage, [
        '訊息',
        'Message',
    ])

    global SigningUpdate
    SigningUpdate = SpecificLoad(inputLanguage, [
        '更新與同步線上使用者及好友名單',
        'Updating and synchronizing online users and friends list',
    ])

    global SendMsg
    SendMsg = SpecificLoad(inputLanguage, [
        '送出訊息',
        'Send Msg',
    ])

    global KickOtherLogin
    KickOtherLogin = SpecificLoad(inputLanguage, [
        '剔除其他登入',
        'Kick other login',
    ])

    global NotKickOtherLogin
    NotKickOtherLogin = SpecificLoad(inputLanguage, [
        '不剔除其他登入',
        'Not kick other login',
    ])

    global AnyKeyContinue
    AnyKeyContinue = SpecificLoad(inputLanguage, [
        '請按任意鍵繼續',
        'Any key to continue',
    ])

    global Login
    Login = SpecificLoad(inputLanguage, [
        '登入',
        'Login',
    ])

    global LoginSuccess
    LoginSuccess = SpecificLoad(inputLanguage, [
        Login + Success,
        Login + ' ' + Success,
    ])

    global LoginFail
    LoginFail = SpecificLoad(inputLanguage, [
        Login + Fail,
        Login + ' ' + Fail,
    ])

    global MailBoxFull
    MailBoxFull = SpecificLoad(inputLanguage, [
        '郵件已滿',
        'Mail box is full',
    ])

    global PostNotFinish
    PostNotFinish = SpecificLoad(inputLanguage, [
        '文章尚未完成',
        'Post is not finish',
    ])

    global SystemBusyTryLater
    SystemBusyTryLater = SpecificLoad(inputLanguage, [
        '系統負荷過重, 請稍後再試',
        'System is overloaded, please try again later',
    ])

    global DelWrongPWRecord
    DelWrongPWRecord = SpecificLoad(inputLanguage, [
        '刪除以上錯誤嘗試的記錄',
        'Delete the record of the wrong password',
    ])

    global Logout
    Logout = SpecificLoad(inputLanguage, [
        '登出',
        'Logout',
    ])

    # 您要刪除以上錯誤嘗試的記錄嗎

    # Final check
    for k, v in globals().items():
        # System Var
        if k.startswith('__'):
            continue
        # print(k)
        # print(v)
        if v is None:
            raise Exceptions.InitError(
                Util.getFileName(__file__), k + ' is None')

    print('[' + strftime('%m%d %H:%M:%S') + '][' + Info + '] ' + i18n + 
          ' [' + Init + ']')


def _createlist():

    i18nStrList = []

    for k, v in globals().items():
        # System Var
        if k.startswith('_'):
            continue
        if isinstance(k, str) and isinstance(v, str):
            i18nStrList.append(k)

    with open('i18n.txt', 'w') as F:
        F.write('\n'.join(i18nStrList))

if __name__ == '__main__':
    load(Language.Chinese)
    _createlist()
