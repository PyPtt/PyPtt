import PyPtt
from tests import util


def test(ptt_bot: PyPtt.API):

    ptt_bot.give_money('janice001', 10)


def func():
    host_list = [
        PyPtt.HOST.PTT1,
        # PyPtt.HOST.PTT2
    ]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LogLevel.TRACE,
        )
        util.login(ptt_bot)

        test(ptt_bot)

        ptt_bot.logout()


if __name__ == '__main__':
    func()
