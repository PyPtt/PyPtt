from . import data_type
from . import log


class Config:
    # retry_wait_time 秒後重新連線
    retry_wait_time = 3

    # ScreenLTimeOut 秒後判定此畫面沒有可辨識的目標
    screen_timeout = 3.0

    # screen_long_timeout 秒後判定此畫面沒有可辨識的目標
    # 適用於需要特別等待的情況，例如: 剔除其他登入等等
    # 建議不要低於 10 秒，剔除其他登入最長可能會花費約六到七秒
    screen_long_timeout = 10.0

    # screen_post_timeout 秒後判定此畫面沒有可辨識的目標
    # 適用於貼文等待的情況，建議不要低於 60 秒
    screen_post_timeout = 60.0

    # 預設語言
    language = data_type.Language.MANDARIN

    # 預設 log 等級
    log_level = log.INFO

    # 預設不剔除其他登入
    kick_other_session = False

    # 預設登入 PTT1
    host = data_type.HOST.PTT1

    # 預設採用 websockets
    connect_mode = None

    # 預設使用 23
    port = 23

    # 終端機高度（行數，含狀態列），透過 Telnet NAWS 告知 PTT
    # 越大每頁能看到更多行，大幅減少 get_post 的網路來回次數
    # 實測：高度 24 → 58 次 send；高度 100 → 2 次（~97% 改善）
    # PTT 伺服器端硬性上限為 100，傳入更大的值不會有額外效果
    screen_height = 100

    # 預設驗證 server 端 TLS 憑證；設為 False 可在 SSL 攔截 proxy 環境下使用
    verify_ssl = True

    logger_callback = None


LOGGER_CONFIG = {

}
