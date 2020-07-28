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

Connect = None
Start = None
ConnectMode = None
ConnectMode_Telnet = None
ConnectMode_WebSocket = None
Active = None
ErrorParameter = None
connect_core = None
PTT = None
PTT2 = None
Localhost = None
Init = None
Done = None
i18n = None
Library = None
Fail = None
Success = None
Prepare = None
Info = None
Debug = None
Again = None
ErrorIDPW = None
ErrorPW = None
ScreenNoMatchTarget = None
SigningUnPleaseWait = None
Msg = None
SigningUpdate = None
SendMsg = None
kick_other_login = None
Notkick_other_login = None
AnyKeyContinue = None
login = None
loginSuccess = None
loginFail = None
MailBoxFull = None
PostNotFinish = None
SystemBusyTryLater = None
DelWrongPWRecord = None
logout = None
SpendTime = None
GetPTTTime = None
LoginTooOften = None
MustBe = None
String = None
Integer = None
Boolean = None
ID = None
Password = None
InputOriginPassword = None
InputNewPassword = None
CheckNewPassword = None
Board = None
IntoBoard = None
BothInput = None
NoInput = None
CatchPost = None
PostDeleted = None
BrowsePost = None
CatchIP = None
GetPush = None
Update = None
Push = None
Date = None
Content = None
Author = None
Title = None
UnknownError = None
Requirelogin = None
HasPushPermission = None
HasPostPermission = None
NoPermission = None
SaveFile = None
SelectSignature = None
FindNewestIndex = None
OutOfRange = None
MustSmallOrEqual = None
VotePost = None
SubstandardPost = None
DoNothing = None
NoFastPush = None
OnlyArrow = None
GetUser = None
NoSuchUser = None
WaterBall = None
UserOffline = None
SetCallStatus = None
Throw = None
NoWaterball = None
BrowseWaterball = None
languageModule = None
English = None
ChineseTranditional = None
GetCallStatus = None
NoMoney = None
InputID = None
InputMoney = None
AuthenticationHasNotExpired = None
VerifyID = None
TradingInProgress = None
Transaction = None
MoneyTooFew = None
TransactionCancelled = None
ConstantRedBag = None
SendMail = None
Select = None
SignatureFile = None
NoSignatureFile = None
SelfSaveDraft = None
MailBox = None
NoSuchBoard = None
HideSensitiveInfor = None
PostFormatError = None
log_handler = None
NewCursor = None
OldCursor = None
PostNoContent = None
ConnectionClosed = None
BoardList = None
UnregisteredUserCantUseAllAPI = None
UnregisteredUserCantUseThisAPI = None
MultiThreadOperate = None
HasNewMailGotoMainMenu = None
UseTooManyResources = None
host = None
PTT2NotSupport = None
AnimationPost = None
RestoreConnection = None
NoPush = None
NoResponse = None
ReplyBoard = None
ReplyMail = None
ReplyBoard_Mail = None
UseTheOriginalTitle = None
QuoteOriginal = None
EditPost = None
RespondSuccess = None
ForcedWrite = None
NoPost = None
NeedModeratorPermission = None
NewSettingsHaveBeenSaved = None
NoChanges = None
Mark = None
MarkPost = None
DelAllMarkPost = None
NoSuchPost = None
GoMainMenu = None
ErrorLoginRichPeopleGoMainMenu = None
CanNotUseSearchPostCodeF = None
FavouriteBoardList = None
bucket = None
UserHasPreviouslyBeenBanned = None
InputBucketDays_Reason = None
UnconfirmedPost = None
Reading = None
ReadComplete = None
QuitUserProfile = None
NoMail = None
UseMailboxAPIWillLogoutAfterExecution = None
PicksInRegister = None
RegisterInProcessing = None
record_ip = None
not_record_ip = None
push_aligned = None
not_push_aligned = None
confirm = None
timeout = None
NoSearchResult = None
SkipRegistrationForm = None
url = None
OnlySecureConnection = None


def specific_load(input_language, lang_list):
    global languageList

    if len(languageList) != len(lang_list):
        raise ValueError('SpecificLoad LangList legnth error')

    if input_language not in languageList:
        raise ValueError('SpecificLoad Unknow language', input_language)
    return lang_list[languageList.index(input_language)]


def replace(string, *args):
    # for i in range(len(args)):
    for i, _ in enumerate(args):
        target = str(args[i])
        string = string.replace('{Target' + str(i) + '}', target)
    return string


def load(input_lang):
    if not lib_util.check_range(language, input_lang):
        raise ValueError('Language', input_lang)

    global Connect
    Connect = specific_load(input_lang, [
        '連線',
        'Connect',
    ])

    global Start
    Start = specific_load(input_lang, [
        '開始',
        'Start',
    ])

    global ConnectMode
    ConnectMode = specific_load(input_lang, [
        Connect + '模式',
        Connect + 'mode',
    ])

    global ConnectMode_Telnet
    ConnectMode_Telnet = specific_load(input_lang, [
        'Telnet',
        'Telnet',
    ])

    global ConnectMode_WebSocket
    ConnectMode_WebSocket = specific_load(input_lang, [
        'WebSocket',
        'WebSocket',
    ])

    global Active
    Active = specific_load(input_lang, [
        '啟動',
        'Active',
    ])

    global ErrorParameter
    ErrorParameter = specific_load(input_lang, [
        '參數錯誤',
        'Wrong parameter',
    ])

    global connect_core
    connect_core = specific_load(input_lang, [
        '連線核心',
        'Connect Core',
    ])

    global PTT
    PTT = specific_load(input_lang, [
        '批踢踢',
        'PTT',
    ])

    global PTT2
    PTT2 = specific_load(input_lang, [
        '批踢踢兔',
        'PTT2',
    ])

    global Localhost
    Localhost = specific_load(input_lang, [
        '本機',
        'localhost',
    ])

    global Init
    Init = specific_load(input_lang, [
        '初始化',
        'initialize',
    ])

    global Done
    Done = specific_load(input_lang, [
        '完成',
        'Done',
    ])

    global i18n
    i18n = specific_load(input_lang, [
        '多國語系',
        'i18n',
    ])

    global Library
    Library = specific_load(input_lang, [
        'PyPtt',
        'PyPtt',
    ])

    global Fail
    Fail = specific_load(input_lang, [
        '失敗',
        'Fail',
    ])

    global Success
    Success = specific_load(input_lang, [
        '成功',
        'Success',
    ])

    global Prepare
    Prepare = specific_load(input_lang, [
        '準備',
        'Prepare',
    ])

    global Info
    Info = specific_load(input_lang, [
        '資訊',
        'INFO',
    ])

    global Debug
    Debug = specific_load(input_lang, [
        '除錯',
        'DBUG',
    ])

    global Again
    Again = specific_load(input_lang, [
        '重新',
        'Re',
    ])

    global ErrorIDPW
    ErrorIDPW = specific_load(input_lang, [
        '密碼不對或無此帳號',
        'Wrong password or no such id',
    ])

    global ErrorPW
    ErrorPW = specific_load(input_lang, [
        '密碼不正確',
        'Wrong password',
    ])

    global ScreenNoMatchTarget
    ScreenNoMatchTarget = specific_load(input_lang, [
        '畫面無法辨識',
        'This screen is not recognized',
    ])

    global SigningUnPleaseWait
    SigningUnPleaseWait = specific_load(input_lang, [
        '登入中，請稍候',
        'Signing in, please wait',
    ])

    global Msg
    Msg = specific_load(input_lang, [
        '訊息',
        'Message',
    ])

    global SigningUpdate
    SigningUpdate = specific_load(input_lang, [
        '更新與同步線上使用者及好友名單',
        'Updating and synchronizing online users and friends list',
    ])

    global SendMsg
    SendMsg = specific_load(input_lang, [
        '送出訊息',
        'Send Msg',
    ])

    global kick_other_login
    kick_other_login = specific_load(input_lang, [
        '剔除其他登入',
        'Kick other login',
    ])

    global Notkick_other_login
    Notkick_other_login = specific_load(input_lang, [
        '不剔除其他登入',
        'Not kick other login',
    ])

    global AnyKeyContinue
    AnyKeyContinue = specific_load(input_lang, [
        '請按任意鍵繼續',
        'Any key to continue',
    ])

    global login
    login = specific_load(input_lang, [
        '登入',
        'login',
    ])

    global loginSuccess
    loginSuccess = specific_load(input_lang, [
        '登入成功',
        'login Success',
    ])

    global loginFail
    loginFail = specific_load(input_lang, [
        login + Fail,
        login + ' ' + Fail,
    ])

    global MailBoxFull
    MailBoxFull = specific_load(input_lang, [
        '郵件已滿',
        'Mail box is full',
    ])

    global PostNotFinish
    PostNotFinish = specific_load(input_lang, [
        '文章尚未完成',
        'Post is not finish',
    ])

    global SystemBusyTryLater
    SystemBusyTryLater = specific_load(input_lang, [
        '系統負荷過重, 請稍後再試',
        'System is overloaded, please try again later',
    ])

    global DelWrongPWRecord
    DelWrongPWRecord = specific_load(input_lang, [
        '刪除以上錯誤嘗試的記錄',
        'Delete the record of the wrong password',
    ])

    global logout
    logout = specific_load(input_lang, [
        '登出',
        'logout',
    ])

    global SpendTime
    SpendTime = specific_load(input_lang, [
        '花費時間',
        'Spend time',
    ])

    global GetPTTTime
    GetPTTTime = specific_load(input_lang, [
        '取得批踢踢時間',
        'Get PTT time',
    ])

    global LoginTooOften
    LoginTooOften = specific_load(input_lang, [
        '登入太頻繁',
        'login too often',
    ])

    global MustBe
    MustBe = specific_load(input_lang, [
        '必須是',
        'must be',
    ])

    global String
    String = specific_load(input_lang, [
        '字串',
        'String',
    ])

    global Integer
    Integer = specific_load(input_lang, [
        '整數',
        'Integer',
    ])

    global Boolean
    Boolean = specific_load(input_lang, [
        '布林值',
        'Boolean',
    ])

    global ID
    ID = specific_load(input_lang, [
        '帳號',
        'ID',
    ])

    global Password
    Password = specific_load(input_lang, [
        '密碼',
        'Password',
    ])

    global InputOriginPassword
    InputOriginPassword = specific_load(input_lang, [
        '輸入原密碼',
        'Input Origin Password',
    ])

    global InputNewPassword
    InputNewPassword = specific_load(input_lang, [
        '設定新密碼',
        'Input New Password',
    ])

    global CheckNewPassword
    CheckNewPassword = specific_load(input_lang, [
        '檢查新密碼',
        'CheckNewPassword',
    ])

    global Board
    Board = specific_load(input_lang, [
        '看板',
        'Board',
    ])

    global IntoBoard
    IntoBoard = specific_load(input_lang, [
        '進入看板',
        'Into Board',
    ])

    global ReadingBoardInfo
    ReadingBoardInfo = specific_load(input_lang, [
        '讀取看板資訊',
        'Reading Board Info',
    ])

    global BothInput
    BothInput = specific_load(input_lang, [
        '同時輸入',
        'Both input',
    ])

    global NoInput
    NoInput = specific_load(input_lang, [
        '沒有輸入',
        'No input',
    ])

    global CatchPost
    CatchPost = specific_load(input_lang, [
        '取得文章',
        'Catch post',
    ])

    global PostDeleted
    PostDeleted = specific_load(input_lang, [
        '文章已經被刪除',
        'Post has been deleted',
    ])

    global BrowsePost
    BrowsePost = specific_load(input_lang, [
        '瀏覽文章',
        'Browse post',
    ])

    global CatchIP
    CatchIP = specific_load(input_lang, [
        '取得 IP',
        'Catch IP',
    ])

    global GetPush
    GetPush = specific_load(input_lang, [
        '取得推文',
        'Get push',
    ])

    global Update
    Update = specific_load(input_lang, [
        '更新',
        'Update',
    ])

    global Push
    Push = specific_load(input_lang, [
        '推文',
        'Push',
    ])

    global Date
    Date = specific_load(input_lang, [
        '日期',
        'Date',
    ])

    global Content
    Content = specific_load(input_lang, [
        '內文',
        'Content',
    ])

    global Author
    Author = specific_load(input_lang, [
        '作者',
        'Author',
    ])

    global Title
    Title = specific_load(input_lang, [
        '標題',
        'Title',
    ])

    global UnknownError
    UnknownError = specific_load(input_lang, [
        '未知錯誤',
        'Unknow Error',
    ])

    global Requirelogin
    Requirelogin = specific_load(input_lang, [
        '請先' + login,
        'Please ' + login + ' first',
    ])

    global HasPushPermission
    HasPushPermission = specific_load(input_lang, [
        '使用者擁有推文權限',
        'User Has Push Permission',
    ])

    global HasPostPermission
    HasPostPermission = specific_load(input_lang, [
        '使用者擁有貼文權限',
        'User Has Post Permission',
    ])

    global NoPermission
    NoPermission = specific_load(input_lang, [
        '使用者沒有權限',
        'User Has No Permission',
    ])

    global SaveFile
    SaveFile = specific_load(input_lang, [
        '儲存檔案',
        'Save File',
    ])

    global SelectSignature
    SelectSignature = specific_load(input_lang, [
        '選擇簽名檔',
        'Select Signature',
    ])

    global FindNewestIndex
    FindNewestIndex = specific_load(input_lang, [
        '找到最新編號',
        'Find Newest Index',
    ])

    global OutOfRange
    OutOfRange = specific_load(input_lang, [
        '超出範圍',
        'Out Of Range',
    ])

    global MustSmallOrEqual
    MustSmallOrEqual = specific_load(input_lang, [
        '必須小於等於',
        'Must be less than or equal',
    ])

    global VotePost
    VotePost = specific_load(input_lang, [
        '投票文章',
        'Vote Post',
    ])

    global SubstandardPost
    SubstandardPost = specific_load(input_lang, [
        '不合規範文章',
        'Substandard Post',
    ])

    global DoNothing
    DoNothing = specific_load(input_lang, [
        '不處理',
        'Do Nothing',
    ])

    global NoFastPush
    NoFastPush = specific_load(input_lang, [
        '禁止快速連續推文',
        'No Fast Push',
    ])

    global OnlyArrow
    OnlyArrow = specific_load(input_lang, [
        '使用加註方式',
        'Arrow Only in Push',
    ])

    global GetUser
    GetUser = specific_load(input_lang, [
        '取得使用者',
        'Get User',
    ])

    global NoSuchUser
    NoSuchUser = specific_load(input_lang, [
        '無該使用者',
        'No such user',
    ])

    global WaterBall
    WaterBall = specific_load(input_lang, [
        '水球',
        'Water Ball',
    ])

    global UserOffline
    UserOffline = specific_load(input_lang, [
        '使用者離線',
        'User Offline',
    ])

    global SetCallStatus
    SetCallStatus = specific_load(input_lang, [
        '設定呼叫器狀態',
        'Set Call Status',
    ])

    global Throw
    Throw = specific_load(input_lang, [
        '丟',
        'Throw',
    ])

    global NoWaterball
    NoWaterball = specific_load(input_lang, [
        '無訊息記錄',
        'No Waterball',
    ])

    global BrowseWaterball
    BrowseWaterball = specific_load(input_lang, [
        '瀏覽水球紀錄',
        'Browse Waterball',
    ])

    global languageModule
    languageModule = specific_load(input_lang, [
        '語言模組',
        'language Module',
    ])

    global English
    English = specific_load(input_lang, [
        '英文',
        'English',
    ])

    global ChineseTranditional
    ChineseTranditional = specific_load(input_lang, [
        '繁體中文',
        'Chinese Tranditional',
    ])

    global GetCallStatus
    GetCallStatus = specific_load(input_lang, [
        '取得呼叫器狀態',
        'Get BBCall Status',
    ])

    global NoMoney
    NoMoney = specific_load(input_lang, [
        'P 幣不足',
        'No Money',
    ])

    global InputID
    InputID = specific_load(input_lang, [
        '輸入帳號',
        'Input ID',
    ])

    global InputMoney
    InputMoney = specific_load(input_lang, [
        '輸入金額',
        'Input Money',
    ])

    global AuthenticationHasNotExpired
    AuthenticationHasNotExpired = specific_load(input_lang, [
        '認證尚未過期',
        'Authentication has not expired',
    ])

    global VerifyID
    VerifyID = specific_load(input_lang, [
        '確認身分',
        'Verify ID',
    ])

    global TradingInProgress
    TradingInProgress = specific_load(input_lang, [
        '交易正在進行中',
        'Trading is in progress',
    ])

    global Transaction
    Transaction = specific_load(input_lang, [
        '交易',
        'Transaction',
    ])

    global MoneyTooFew
    MoneyTooFew = specific_load(input_lang, [
        '金額過少，交易取消!',
        'The amount is too small, the transaction is cancelled!',
    ])

    global TransactionCancelled
    TransactionCancelled = specific_load(input_lang, [
        '交易取消!',
        'The transaction is cancelled!',
    ])

    global ConstantRedBag
    ConstantRedBag = specific_load(input_lang, [
        '不修改紅包袋',
        'Constant the red bag',
    ])

    global SendMail
    SendMail = specific_load(input_lang, [
        '寄信',
        'Send Mail',
    ])

    global Select
    Select = specific_load(input_lang, [
        '選擇',
        'Select',
    ])

    global SignatureFile
    SignatureFile = specific_load(input_lang, [
        '簽名檔',
        'Signature File',
    ])

    global NoSignatureFile
    NoSignatureFile = specific_load(input_lang, [
        '不加簽名檔',
        'No Signature File',
    ])

    global SelfSaveDraft
    SelfSaveDraft = specific_load(input_lang, [
        '自存底稿',
        'Self-Save Draft',
    ])

    global MailBox
    MailBox = specific_load(input_lang, [
        '郵件選單',
        'Mail Box',
    ])

    global NoSuchBoard
    NoSuchBoard = specific_load(input_lang, [
        '無該板面',
        'No Such Board',
    ])

    global HideSensitiveInfor
    HideSensitiveInfor = specific_load(input_lang, [
        '隱藏敏感資訊',
        'Hide Sensitive Information',
    ])

    global PostFormatError
    PostFormatError = specific_load(input_lang, [
        '文章格式錯誤',
        'Post Format Error',
    ])

    global log_handler
    log_handler = specific_load(input_lang, [
        '紀錄額取器',
        'log Handler',
    ])

    global NewCursor
    NewCursor = specific_load(input_lang, [
        '新式游標',
        'New Type Cursor',
    ])

    global OldCursor
    OldCursor = specific_load(input_lang, [
        '舊式游標',
        'Old Type Cursor',
    ])

    global PostNoContent
    PostNoContent = specific_load(input_lang, [
        '此文章無內容',
        'Post has no content',
    ])

    global ConnectionClosed
    ConnectionClosed = specific_load(input_lang, [
        '連線已經被關閉',
        'Connection Closed',
    ])

    global BoardList
    BoardList = specific_load(input_lang, [
        '看板列表',
        'Board List',
    ])

    global UnregisteredUserCantUseAllAPI
    UnregisteredUserCantUseAllAPI = specific_load(input_lang, [
        '未註冊使用者，將無法使用全部功能',
        'Unregistered User Can\'t Use All API',
    ])

    global UnregisteredUserCantUseThisAPI
    UnregisteredUserCantUseThisAPI = specific_load(input_lang, [
        '未註冊使用者，無法使用此功能',
        'Unregistered User Can\'t Use This API',
    ])

    global MultiThreadOperate
    MultiThreadOperate = specific_load(input_lang, [
        '請勿使用多線程同時操作一個 PyPtt 物件',
        'Do not use a multi-thread to operate a PyPtt object',
    ])

    global HasNewMailGotoMainMenu
    HasNewMailGotoMainMenu = specific_load(input_lang, [
        '有新信，回到主選單',
        'Have a new letter, return to the main menu',
    ])

    global UseTooManyResources
    UseTooManyResources = specific_load(input_lang, [
        '耗用太多資源',
        'Use too many resources of PTT',
    ])

    global host
    host = specific_load(input_lang, [
        '主機',
        'host',
    ])

    global PTT2NotSupport
    PTT2NotSupport = specific_load(input_lang, [
        f'{PTT2}不支援',
        f'{PTT2} Not Support',
    ])

    global AnimationPost
    AnimationPost = specific_load(input_lang, [
        '動畫文章',
        'Animation Post',
    ])

    global RestoreConnection
    RestoreConnection = specific_load(input_lang, [
        '恢復連線',
        'Restore Connection',
    ])

    global NoPush
    NoPush = specific_load(input_lang, [
        '禁止推薦',
        'No Push',
    ])

    global NoResponse
    NoResponse = specific_load(input_lang, [
        '很抱歉, 此文章已結案並標記, 不得回應',
        'This Post has been closed and marked, no response',
    ])

    global ReplyBoard
    ReplyBoard = specific_load(input_lang, [
        '回應至看板',
        'Respond to the Board',
    ])

    global ReplyMail
    ReplyMail = specific_load(input_lang, [
        '回應至作者信箱',
        'Respond to the mailbox of author',
    ])

    global ReplyBoard_Mail
    ReplyBoard_Mail = specific_load(input_lang, [
        '回應至看板與作者信箱',
        'Respond to the Board and the mailbox of author',
    ])

    global UseTheOriginalTitle
    UseTheOriginalTitle = specific_load(input_lang, [
        '採用原標題',
        'Use the original title',
    ])

    global QuoteOriginal
    QuoteOriginal = specific_load(input_lang, [
        '引用原文',
        'Quote original',
    ])

    global EditPost
    EditPost = specific_load(input_lang, [
        '編輯文章',
        'Edit Post',
    ])

    global RespondSuccess
    RespondSuccess = specific_load(input_lang, [
        '回應成功',
        'Respond Success',
    ])

    global ForcedWrite
    ForcedWrite = specific_load(input_lang, [
        '強制寫入',
        'Forced Write',
    ])

    global NoPost
    NoPost = specific_load(input_lang, [
        '沒有文章',
        'No Post',
    ])

    global NeedModeratorPermission
    NeedModeratorPermission = specific_load(input_lang, [
        '需要板主權限',
        'Need Moderator Permission',
    ])

    global NewSettingsHaveBeenSaved
    NewSettingsHaveBeenSaved = specific_load(input_lang, [
        '已儲存新設定',
        'New settings have been saved',
    ])

    global NoChanges
    NoChanges = specific_load(input_lang, [
        '未改變任何設定',
        'No changes have been made to any settings',
    ])

    global Mark
    Mark = specific_load(input_lang, [
        '標記',
        'Mark',
    ])

    global MarkPost
    MarkPost = specific_load(input_lang, [
        '標記文章',
        'Mark Post',
    ])

    global DelAllMarkPost
    DelAllMarkPost = specific_load(input_lang, [
        '刪除所有標記文章',
        'Del All Mark Post',
    ])

    global NoSuchPost
    NoSuchPost = specific_load(input_lang, [
        '{Target0} 板找不到這個文章代碼 {Target1}',
        'In {Target0}, the post code is not exist {Target1}',
    ])

    global GoMainMenu
    GoMainMenu = specific_load(input_lang, [
        '回到主選單',
        'Back to main memu',
    ])

    global ErrorLoginRichPeopleGoMainMenu
    ErrorLoginRichPeopleGoMainMenu = specific_load(input_lang, [
        '誤入大富翁區，回到主選單',
        'Stray into the Monopoly area and return to the main menu',
    ])

    global CanNotUseSearchPostCodeF
    CanNotUseSearchPostCodeF = specific_load(input_lang, [
        '此狀態下無法使用搜尋文章代碼(AID)功能',
        'This status can not use the search Post code function',
    ])

    global FavouriteBoardList
    FavouriteBoardList = specific_load(input_lang, [
        '我的最愛',
        'Favourite Board List',
    ])

    global bucket
    bucket = specific_load(input_lang, [
        '水桶',
        'Bucket',
    ])

    global UserHasPreviouslyBeenBanned
    UserHasPreviouslyBeenBanned = specific_load(input_lang, [
        '使用者之前已被禁言',
        'User has previously been banned',
    ])

    global InputBucketDays_Reason
    InputBucketDays_Reason = specific_load(input_lang, [
        '輸入水桶天數與理由',
        'Input bucket days and reason',
    ])

    global UnconfirmedPost
    UnconfirmedPost = specific_load(input_lang, [
        '待證實文章',
        'Post To Be Confirmed',
    ])

    global Reading
    Reading = specific_load(input_lang, [
        '讀取中',
        'Reading',
    ])

    global ReadComplete
    ReadComplete = specific_load(input_lang, [
        f'讀取{Done}',
        f'Read {Done}',
    ])

    global QuitUserProfile
    QuitUserProfile = specific_load(input_lang, [
        f'退出使用者檔案',
        f'Quit User Profile',
    ])

    global NoMail
    NoMail = specific_load(input_lang, [
        f'沒有信件',
        f'You have no mail',
    ])

    global UseMailboxAPIWillLogoutAfterExecution
    UseMailboxAPIWillLogoutAfterExecution = specific_load(input_lang, [
        f'如果使用信箱相關功能，將執行後自動登出',
        f'If you use mailbox related functions, you will be logged out automatically after execution',
    ])

    global PicksInRegister
    PicksInRegister = specific_load(input_lang, [
        '註冊申請單處理順位',
        'Registration application processing order',
    ])

    global RegisterInProcessing
    RegisterInProcessing = specific_load(input_lang, [
        '註冊申請單尚在處理中',
        'Register is in processing',
    ])

    global record_ip
    record_ip = specific_load(input_lang, [
        '紀錄 IP',
        'Record ip',
    ])

    global not_record_ip
    not_record_ip = specific_load(input_lang, [
        '不紀錄 IP',
        'Not record ip',
    ])

    global push_aligned
    push_aligned = specific_load(input_lang, [
        '推文對齊',
        'Push aligned',
    ])

    global not_push_aligned
    not_push_aligned = specific_load(input_lang, [
        '無推文對齊',
        'No push aligned',
    ])

    global confirm
    confirm = specific_load(input_lang, [
        '確認',
        'Confirm',
    ])

    global timeout
    timeout = specific_load(input_lang, [
        '超時',
        'Timeout',
    ])

    global NoSearchResult
    NoSearchResult = specific_load(input_lang, [
        '沒有搜尋結果',
        'No Search Result',
    ])

    global SkipRegistrationForm
    SkipRegistrationForm = specific_load(input_lang, [
        '跳過填寫註冊單',
        'Skip Registration Form',
    ])

    global url
    url = specific_load(input_lang, [
        '網址',
        'url',
    ])

    global OnlySecureConnection
    OnlySecureConnection = specific_load(input_lang, [
        '已設定為只能使用安全連線',
        'Secure connections only',
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
    load(language.CHINESE)
    _createlist()
