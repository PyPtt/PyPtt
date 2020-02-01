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


class Config:
    Version = Ver.V

    # retry_wait_time 秒後重新連線
    retry_wait_time = 3

    # screen_long_timeout 秒後判定此畫面沒有可辨識的目標
    # 適用於需要特別等待的情況，例如: 剔除其他登入、發文等等
    # 建議不要低於 10 秒，剔除其他登入最長可能會花費約六到七秒
    screen_long_timeout = 10.0

    # screen_post_timeout 秒後判定此畫面沒有可辨識的目標
    # 適用於貼文等待的情況，建議不要低於 10 秒
    screen_post_timeout = 60.0

    # ScreenLTimeOut 秒後判定此畫面沒有可辨識的目標
    screen_timeout = 3.0

    # 預設語言
    language = i18n.language.Chinese

    # 預設 Log 等級
    log_level = Log.Level.INFO

    # 預設不剔除其他登入
    kick_other_login = False

    # 預設登入 PTT1
    host = DataType.host.PTT1

    log_handler = None
