
try:
    from . import Util
except ModuleNotFoundError:
    import Util


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


def replace(String, *args):
    for i in range(len(args)):
        Target = str(args[i])
        String = String.replace('{Target' + str(i) + '}', Target)
    return String


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

    global PTT2
    PTT2 = SpecificLoad(inputLanguage, [
        '批踢踢兔',
        'PTT2',
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

    global PostDeleted
    PostDeleted = SpecificLoad(inputLanguage, [
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

    global HasPushPermission
    HasPushPermission = SpecificLoad(inputLanguage, [
        '使用者擁有推文權限',
        'User Has Push Permission',
    ])

    global HasPostPermission
    HasPostPermission = SpecificLoad(inputLanguage, [
        '使用者擁有貼文權限',
        'User Has Post Permission',
    ])

    global NoPermission
    NoPermission = SpecificLoad(inputLanguage, [
        '使用者沒有權限',
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

    global MustSmallOrEqual
    MustSmallOrEqual = SpecificLoad(inputLanguage, [
        '必須小於等於',
        'Must be less than or equal',
    ])

    global VotePost
    VotePost = SpecificLoad(inputLanguage, [
        '投票文章',
        'Vote Post',
    ])

    global SubstandardPost
    SubstandardPost = SpecificLoad(inputLanguage, [
        '不合規範文章',
        'Substandard Post',
    ])

    global DoNothing
    DoNothing = SpecificLoad(inputLanguage, [
        '不處理',
        'Do Nothing',
    ])

    global NoFastPush
    NoFastPush = SpecificLoad(inputLanguage, [
        '禁止快速連續推文',
        'No Fast Push',
    ])

    global OnlyArrow
    OnlyArrow = SpecificLoad(inputLanguage, [
        '使用加註方式',
        'Arrow Only in Push',
    ])

    global GetUser
    GetUser = SpecificLoad(inputLanguage, [
        '取得使用者',
        'Get User',
    ])

    global NoSuchUser
    NoSuchUser = SpecificLoad(inputLanguage, [
        '無該使用者',
        'No such user',
    ])

    global WaterBall
    WaterBall = SpecificLoad(inputLanguage, [
        '水球',
        'Water Ball',
    ])

    global UserOffline
    UserOffline = SpecificLoad(inputLanguage, [
        '使用者離線',
        'User Offline',
    ])

    global SetCallStatus
    SetCallStatus = SpecificLoad(inputLanguage, [
        '設定呼叫器狀態',
        'Set Call Status',
    ])

    global Throw
    Throw = SpecificLoad(inputLanguage, [
        '丟',
        'Throw',
    ])

    global NoWaterball
    NoWaterball = SpecificLoad(inputLanguage, [
        '無訊息記錄',
        'No Waterball',
    ])

    global BrowseWaterball
    BrowseWaterball = SpecificLoad(inputLanguage, [
        '瀏覽水球紀錄',
        'Browse Waterball',
    ])

    global LanguageModule
    LanguageModule = SpecificLoad(inputLanguage, [
        '語言模組',
        'Language Module',
    ])

    global English
    English = SpecificLoad(inputLanguage, [
        '英文',
        'English',
    ])

    global ChineseTranditional
    ChineseTranditional = SpecificLoad(inputLanguage, [
        '繁體中文',
        'Chinese Tranditional',
    ])

    global GetCallStatus
    GetCallStatus = SpecificLoad(inputLanguage, [
        '取得呼叫器狀態',
        'Get BBCall Status',
    ])

    global NoMoney
    NoMoney = SpecificLoad(inputLanguage, [
        'P 幣不足',
        'No Money',
    ])

    global InputID
    InputID = SpecificLoad(inputLanguage, [
        '輸入帳號',
        'Input ID',
    ])

    global InputMoney
    InputMoney = SpecificLoad(inputLanguage, [
        '輸入金額',
        'Input Money',
    ])

    global AuthenticationHasNotExpired
    AuthenticationHasNotExpired = SpecificLoad(inputLanguage, [
        '認證尚未過期',
        'Authentication has not expired',
    ])

    global VerifyID
    VerifyID = SpecificLoad(inputLanguage, [
        '確認身分',
        'Verify ID',
    ])

    global TradingInProgress
    TradingInProgress = SpecificLoad(inputLanguage, [
        '交易正在進行中',
        'Trading is in progress',
    ])

    global Transaction
    Transaction = SpecificLoad(inputLanguage, [
        '交易',
        'Transaction',
    ])

    global MoneyTooFew
    MoneyTooFew = SpecificLoad(inputLanguage, [
        '金額過少，交易取消!',
        'The amount is too small, the transaction is cancelled!',
    ])

    global ConstantRedBag
    ConstantRedBag = SpecificLoad(inputLanguage, [
        '不修改紅包袋',
        'Constant the red bag',
    ])

    global SendMail
    SendMail = SpecificLoad(inputLanguage, [
        '寄信',
        'Send Mail',
    ])

    global Select
    Select = SpecificLoad(inputLanguage, [
        '選擇',
        'Select',
    ])

    global SignatureFile
    SignatureFile = SpecificLoad(inputLanguage, [
        '簽名檔',
        'Signature File',
    ])

    global NoSignatureFile
    NoSignatureFile = SpecificLoad(inputLanguage, [
        '不加簽名檔',
        'No Signature File',
    ])

    global SelfSaveDraft
    SelfSaveDraft = SpecificLoad(inputLanguage, [
        '自存底稿',
        'Self-Save Draft',
    ])

    global MailBox
    MailBox = SpecificLoad(inputLanguage, [
        '郵件選單',
        'Mail Box',
    ])

    global NoSuchBoard
    NoSuchBoard = SpecificLoad(inputLanguage, [
        '無該板面',
        'No Such Board',
    ])

    global HideSensitiveInfor
    HideSensitiveInfor = SpecificLoad(inputLanguage, [
        '隱藏敏感資訊',
        'Hide Sensitive Information',
    ])

    global PostFormatError
    PostFormatError = SpecificLoad(inputLanguage, [
        '文章格式錯誤',
        'Post Format Error',
    ])

    global LogHandler
    LogHandler = SpecificLoad(inputLanguage, [
        '紀錄額取器',
        'Log Handler',
    ])

    global NewCursor
    NewCursor = SpecificLoad(inputLanguage, [
        '新式游標',
        'New Type Cursor',
    ])

    global OldCursor
    OldCursor = SpecificLoad(inputLanguage, [
        '舊式游標',
        'Old Type Cursor',
    ])

    global PostNoContent
    PostNoContent = SpecificLoad(inputLanguage, [
        '此文章無內容',
        'Post has no content',
    ])

    global ConnectionClosed
    ConnectionClosed = SpecificLoad(inputLanguage, [
        '連線已經被關閉',
        'Connection Closed',
    ])

    global BoardList
    BoardList = SpecificLoad(inputLanguage, [
        '看板列表',
        'Board List',
    ])

    global UnregisteredUserCantUseAllAPI
    UnregisteredUserCantUseAllAPI = SpecificLoad(inputLanguage, [
        '未註冊使用者，將無法使用全部功能',
        'Unregistered User Can\'t Use All API',
    ])

    global UnregisteredUserCantUseThisAPI
    UnregisteredUserCantUseThisAPI = SpecificLoad(inputLanguage, [
        '未註冊使用者，無法使用此功能',
        'Unregistered User Can\'t Use This API',
    ])

    global MultiThreadOperate
    MultiThreadOperate = SpecificLoad(inputLanguage, [
        '請勿使用多線程同時操作一個 PTT Library 物件',
        'Do not use a multi-thread to operate a PTT Library object',
    ])

    global HasNewMailGotoMainMenu
    HasNewMailGotoMainMenu = SpecificLoad(inputLanguage, [
        '有新信，回到主選單',
        'Have a new letter, return to the main menu',
    ])

    global UseTooManyResources
    UseTooManyResources = SpecificLoad(inputLanguage, [
        '耗用太多資源',
        'Use too many resources of PTT',
    ])

    global Host
    Host = SpecificLoad(inputLanguage, [
        '主機',
        'Host',
    ])

    global PTT2NotSupport
    PTT2NotSupport = SpecificLoad(inputLanguage, [
        f'{PTT2}不支援',
        f'{PTT2} Not Support',
    ])

    # Animation
    global AnimationPost
    AnimationPost = SpecificLoad(inputLanguage, [
        '動畫文章',
        'Animation Post',
    ])

    global RestoreConnection
    RestoreConnection = SpecificLoad(inputLanguage, [
        '恢復連線',
        'Restore Connection',
    ])

    global NoPush
    NoPush = SpecificLoad(inputLanguage, [
        '禁止推薦',
        'No Push',
    ])

    global NoResponse
    NoResponse = SpecificLoad(inputLanguage, [
        '很抱歉, 此文章已結案並標記, 不得回應',
        'This Post has been closed and marked, no response',
    ])

    global ReplyBoard
    ReplyBoard = SpecificLoad(inputLanguage, [
        '回應至看板',
        'Respond to the Board',
    ])

    global ReplyMail
    ReplyMail = SpecificLoad(inputLanguage, [
        '回應至作者信箱',
        'Respond to the mailbox of author',
    ])

    global ReplyBoard_Mail
    ReplyBoard_Mail = SpecificLoad(inputLanguage, [
        '回應至看板與作者信箱',
        'Respond to the Board and the mailbox of author',
    ])

    global UseTheOriginalTitle
    UseTheOriginalTitle = SpecificLoad(inputLanguage, [
        '採用原標題',
        'Use the original title',
    ])

    global QuoteOriginal
    QuoteOriginal = SpecificLoad(inputLanguage, [
        '引用原文',
        'Quote original',
    ])

    global EditPost
    EditPost = SpecificLoad(inputLanguage, [
        '編輯文章',
        'Edit Post',
    ])

    global RespondSuccess
    RespondSuccess = SpecificLoad(inputLanguage, [
        '回應成功',
        'Respond Success',
    ])

    global ForcedWrite
    ForcedWrite = SpecificLoad(inputLanguage, [
        '強制寫入',
        'Forced Write',
    ])

    global NoPost
    NoPost = SpecificLoad(inputLanguage, [
        '沒有文章',
        'No Post',
    ])

    global NeedModeratorPermission
    NeedModeratorPermission = SpecificLoad(inputLanguage, [
        '需要板主權限',
        'Need Moderator Permission',
    ])

    global NewSettingsHaveBeenSaved
    NewSettingsHaveBeenSaved = SpecificLoad(inputLanguage, [
        '已儲存新設定',
        'New settings have been saved',
    ])

    global NoChanges
    NoChanges = SpecificLoad(inputLanguage, [
        '未改變任何設定',
        'No changes have been made to any settings',
    ])

    global Mark
    Mark = SpecificLoad(inputLanguage, [
        '標記',
        'Mark',
    ])

    global DelAllMarkPost
    DelAllMarkPost = SpecificLoad(inputLanguage, [
        '刪除所有標記文章',
        'Del All Mark Post',
    ])

    global NoSuchPost
    NoSuchPost = SpecificLoad(inputLanguage, [
        '{Target0} 板找不到這個文章代碼 {Target1}',
        'In {Target0}, the post code is not exist {Target1}',
    ])

    global GoMainMenu
    GoMainMenu = SpecificLoad(inputLanguage, [
        '回到主選單',
        'Back to main memu',
    ])

    global CanNotUseSearchPostCodeF
    CanNotUseSearchPostCodeF = SpecificLoad(inputLanguage, [
        '此狀態下無法使用搜尋文章代碼(AID)功能',
        'This state can not use the search Post code function',
    ])

    global FavouriteBoardList
    FavouriteBoardList = SpecificLoad(inputLanguage, [
        '我的最愛',
        'Favourite Board List',
    ])

    global bucket
    bucket = SpecificLoad(inputLanguage, [
        '水桶',
        'Bucket',
    ])

    global UserHasPreviouslyBeenBanned
    UserHasPreviouslyBeenBanned = SpecificLoad(inputLanguage, [
        '使用者之前已被禁言',
        'User has previously been banned',
    ])

    global InputBucketDays_Reason
    InputBucketDays_Reason = SpecificLoad(inputLanguage, [
        '輸入水桶天數與理由',
        'Input bucket days and reason',
    ])

    global UnconfirmedPost
    UnconfirmedPost = SpecificLoad(inputLanguage, [
        '待證實文章',
        'Post To Be Confirmed',
    ])

    global Reading
    Reading = SpecificLoad(inputLanguage, [
        '讀取中',
        'Reading',
    ])

    global ReadComplete
    ReadComplete = SpecificLoad(inputLanguage, [
        f'讀取{Done}',
        f'Read {Done}',
    ])

    global QuitUserProfile
    QuitUserProfile = SpecificLoad(inputLanguage, [
        f'退出使用者檔案',
        f'Quit User Profile',
    ])

    # No changes have been made to any settings

    # Quote original

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
