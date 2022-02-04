import time

import PyPtt
import util


def test(ptt_bot: PyPtt.API):
    content = '''
此為 PyPtt 貼文測試內容，如有打擾請告知。
github: https://github.com/PttCodingMan/PyPtt

開發手冊: https://github.com/PttCodingMan/PyPtt/tree/master/doc
ポ
ポポ
ポポポ
☂
☂☂
☂☂☂
'''

    for _ in range(3):
        ptt_bot.post(
            # 看板
            'Test',
            # 標題分類
            1,
            # 標題
            'PyPtt 程式貼文測試',
            # 內文
            content,
            # 簽名檔
            0)


def func():
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LOG_LEVEL.TRACE,
        )
        util.login(ptt_bot)

        test(ptt_bot)

        ptt_bot.logout()


if __name__ == '__main__':
    func()
