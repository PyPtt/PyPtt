try:
    import DataType
    import Log
    import i18n
    import ConnectCore
except ModuleNotFoundError:
    from . import DataType
    from . import Log
    from . import i18n
    from . import ConnectCore

Version = '0.8.0 beta'
Host = 'ptt.cc'
Port = '23'


def load():

    # RetryWaitTime 秒後重新連線
    global RetryWaitTime
    RetryWaitTime = 3

    # ScreenTimeOut 秒後判定此畫面沒有可辨識的目標
    # 建議不要低於 10 秒，剔除其他登入最長可能會花費約六到七秒
    global ScreenTimeOut
    ScreenTimeOut = 10.0

    # 預設語言
    global Language
    Language = i18n.Language.Chinese

    # 預設連線模式
    global ConnectMode
    ConnectMode = ConnectCore.ConnectMode.WebSocket

    # 預設 Log 等級
    global LogLevel
    LogLevel = Log.Level.INFO

    # 預設是否剔除其他登入
    global KickOtherLogin
    KickOtherLogin = False
