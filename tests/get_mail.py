import os
import sys

sys.path.append(os.getcwd())

import PyPtt
from PyPtt import log
from tests import util


def test(ptt_bot: PyPtt.API):
    for _ in range(3):
        mail_index = ptt_bot.get_newest_index(PyPtt.NewIndex.MAIL)
        mail_info = ptt_bot.get_mail(mail_index)

        log.logger.info('mail result', mail_info)


def test_2(ptt_bot: PyPtt.API):
    mail_index = ptt_bot.get_newest_index(PyPtt.NewIndex.MAIL)

    test_range = 100

    for i in range(test_range):
        if mail_index - i <= 0:
            break
        mail_info = ptt_bot.get_mail(mail_index - i)
        log.logger.info(f'{mail_index - i} mail result', f"[{mail_info[PyPtt.MailField.title]}]")


def func():
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LogLevel.DEBUG,
        )

        try:
            util.login(ptt_bot)
            test(ptt_bot)
            test_2(ptt_bot)
        finally:
            ptt_bot.logout()


if __name__ == '__main__':
    func()
