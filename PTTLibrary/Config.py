try:
    from . import Ver
    from . import DataType
    from . import Log
    from . import i18n
    from . import ConnectCore
except ModuleNotFoundError:
    import Ver
    import DataType
    import Log
    import i18n
    import ConnectCore


Version = Ver.V

RetryWaitTime = 3
ScreenLongTimeOut = 10.0
ScreenPostTimeOut = 60.0
ScreenTimeOut = 3.0
Language = i18n.Language.Chinese
ConnectMode = ConnectCore.ConnectMode.WebSocket
LogLevel = Log.Level.INFO
KickOtherLogin = False
Host = DataType.Host.PTT1


def load():
    # RetryWaitTime 秒後重新連線
    global RetryWaitTime
    RetryWaitTime = 3

    # ScreenLongTimeOut 秒後判定此畫面沒有可辨識的目標
    # 適用於需要特別等待的情況，例如: 剔除其他登入、發文等等
    # 建議不要低於 10 秒，剔除其他登入最長可能會花費約六到七秒
    global ScreenLongTimeOut
    ScreenLongTimeOut = 10.0

    # ScreenPostTimeOut 秒後判定此畫面沒有可辨識的目標
    # 適用於貼文等待的情況，建議不要低於 10 秒
    global ScreenPostTimeOut
    ScreenPostTimeOut = 60.0

    # ScreenLTimeOut 秒後判定此畫面沒有可辨識的目標
    global ScreenTimeOut
    ScreenTimeOut = 3.0

    # 預設語言
    global Language
    Language = i18n.Language.Chinese

    # 預設連線模式
    global ConnectMode
    ConnectMode = ConnectCore.ConnectMode.WebSocket

    # 預設 Log 等級
    global LogLevel
    LogLevel = Log.Level.INFO

    # 預設不剔除其他登入
    global KickOtherLogin
    KickOtherLogin = False

    # 預設登入 PTT1
    global Host
    Host = DataType.Host.PTT1
