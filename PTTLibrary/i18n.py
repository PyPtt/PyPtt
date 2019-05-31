from time import gmtime, strftime

try:
    import DataType
    import Util
    import Config
except ModuleNotFoundError:
    from . import DataType
    from . import Util
    from . import Config


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
        raise ValueError('SpecificLoad LangList legnth error')

    if inputLanguage not in LanguageList:
        raise ValueError('SpecificLoad Unknow language', inputLanguage)
    return LangList[LanguageList.index(inputLanguage)]


def load(inputLanguage):
    if not Util.checkRange(Language, inputLanguage):
        raise ValueError('Language', inputLanguage)

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
        '畫面無法辨識',
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

    global SpendTime
    SpendTime = SpecificLoad(inputLanguage, [
        '花費時間',
        'Spend time',
    ])

    global GetPTTTime
    GetPTTTime = SpecificLoad(inputLanguage, [
        '取得批踢踢時間',
        'Get PTT time',
    ])

    global LoginTooOften
    LoginTooOften = SpecificLoad(inputLanguage, [
        '登入太頻繁',
        'Login too often',
    ])

    global MustBe
    MustBe = SpecificLoad(inputLanguage, [
        '必須是',
        'must be',
    ])

    global String
    String = SpecificLoad(inputLanguage, [
        '字串',
        'String',
    ])

    global Integer
    Integer = SpecificLoad(inputLanguage, [
        '整數',
        'Integer',
    ])

    global Boolean
    Boolean = SpecificLoad(inputLanguage, [
        '布林值',
        'Boolean',
    ])

    global ID
    ID = SpecificLoad(inputLanguage, [
        '帳號',
        'ID',
    ])

    global Password
    Password = SpecificLoad(inputLanguage, [
        '密碼',
        'Password',
    ])

    global Board
    Board = SpecificLoad(inputLanguage, [
        '看板',
        'Board',
    ])

    global BothInput
    BothInput = SpecificLoad(inputLanguage, [
        '同時輸入',
        'Both input',
    ])

    global NoInput
    NoInput = SpecificLoad(inputLanguage, [
        '沒有輸入',
        'No input',
    ])

    global CatchPost
    CatchPost = SpecificLoad(inputLanguage, [
        '取得文章',
        'Catch post',
    ])

    global PostDeled
    PostDeled = SpecificLoad(inputLanguage, [
        '文章已經被刪除',
        'Post has been deleted',
    ])

    global BrowsePost
    BrowsePost = SpecificLoad(inputLanguage, [
        '瀏覽文章',
        'Browse post',
    ])

    global CatchIP
    CatchIP = SpecificLoad(inputLanguage, [
        '取得 IP',
        'Catch IP',
    ])

    global GetPush
    GetPush = SpecificLoad(inputLanguage, [
        '取得推文',
        'Get push',
    ])

    global Update
    Update = SpecificLoad(inputLanguage, [
        '更新',
        'Update',
    ])

    global Push
    Push = SpecificLoad(inputLanguage, [
        '推文',
        'Push',
    ])

    global Date
    Date = SpecificLoad(inputLanguage, [
        '日期',
        'Date',
    ])

    global Content
    Content = SpecificLoad(inputLanguage, [
        '內文',
        'Content',
    ])

    global Author
    Author = SpecificLoad(inputLanguage, [
        '作者',
        'Author',
    ])

    global Title
    Title = SpecificLoad(inputLanguage, [
        '標題',
        'Title',
    ])

    global UnknowError
    UnknowError = SpecificLoad(inputLanguage, [
        '未知錯誤',
        'Unknow Error',
    ])

    global RequireLogin
    RequireLogin = SpecificLoad(inputLanguage, [
        '請先' + Login,
        'Please ' + Login + ' first',
    ])

    global HasPostPermission
    HasPostPermission = SpecificLoad(inputLanguage, [
        '使用者擁有貼文權限',
        'User Has Post Permission',
    ])

    global NoPermission
    NoPermission = SpecificLoad(inputLanguage, [
        '使用者沒有貼文權限',
        'User Has No Permission',
    ])

    global SaveFile
    SaveFile = SpecificLoad(inputLanguage, [
        '儲存檔案',
        'Save File',
    ])

    global SelectSignature
    SelectSignature = SpecificLoad(inputLanguage, [
        '選擇簽名檔',
        'Select Signature',
    ])

    global FindNewestIndex
    FindNewestIndex = SpecificLoad(inputLanguage, [
        '找到最新編號',
        'Find Newest Index',
    ])

    global OutOfRange
    OutOfRange = SpecificLoad(inputLanguage, [
        '超出範圍',
        'Out Of Range',
    ])

    global MustSmall
    MustSmall = SpecificLoad(inputLanguage, [
        '必須小於',
        'Must Small than',
    ])

    global VotePost
    VotePost = SpecificLoad(inputLanguage, [
        '投票文章',
        'Vote Post',
    ])

    global DoNothing
    DoNothing = SpecificLoad(inputLanguage, [
        '不處理',
        'Do Nothing',
    ])

    # global List
    # List = []

    # for k, v in globals().items():
    #     # System Var
    #     if k.startswith('_'):
    #         continue

    #     print(f'k {k}')
    #     print(f'v {v}')
    #     if isinstance(k, str) and isinstance(v, str):
    #         List.append(k)


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

