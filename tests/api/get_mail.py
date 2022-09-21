import PyPtt
from tests import util


def test(ptt_bot: PyPtt.API):
    result = []
    for _ in range(3):
        mail_index = ptt_bot.get_newest_index(PyPtt.NewIndex.MAIL)
        mail_info = ptt_bot.get_mail(mail_index)

        util.logger.info('mail result', mail_info)


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
