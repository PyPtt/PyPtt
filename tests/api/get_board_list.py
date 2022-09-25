import json

import PyPtt
from tests import util


def test(ptt_bot: PyPtt.API):
    board_list = ptt_bot.get_all_boards()

    with open('board_list.json', 'w') as f:
        json.dump(board_list, f, indent=4, ensure_ascii=False)


def func():
    host_list = [
        PyPtt.HOST.PTT1,
        PyPtt.HOST.PTT2
    ]

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
