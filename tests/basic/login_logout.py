import PyPtt
from tests import util


def test(ptt_bot: PyPtt.API):
    util.login(ptt_bot)
    ptt_bot.logout()

    util.login(ptt_bot)
    ptt_bot.logout()


def func():
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LOG_LEVEL.TRACE,
        )
        test(ptt_bot)

    util.logger.info('login logout test ok')


if __name__ == '__main__':
    func()
