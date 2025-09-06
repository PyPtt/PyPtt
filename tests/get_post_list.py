import json
import os
import sys

sys.path.append(os.getcwd())

import PyPtt
from tests import util


def test(ptt_bot: PyPtt.API):

    def _test(board: str):
        offset = 0
        limit = 5

        check_rounds = 5

        post_list = []

        for _ in range(check_rounds):

            cur_post_list = ptt_bot.get_post_list(board, limit=limit, offset=offset)
            offset += limit

            post_list.extend(cur_post_list)

        # assert if no duplicate indexes
        index_set = set()
        for post in post_list:
            index = post[PyPtt.PostField.index]
            assert index not in index_set, f'Duplicate index: {index}'
            index_set.add(index)

        # assert if indexes are continuous
        sorted_indexes = sorted(index_set)
        for i in range(len(sorted_indexes) - 1):
            assert sorted_indexes[i] + 1 == sorted_indexes[i + 1], f'Indexes are not continuous: {sorted_indexes[i]} and {sorted_indexes[i + 1]}'

        # assert if the length of post_list is correct
        assert len(post_list) == check_rounds * limit, f'Length of post_list is not correct: {len(post_list)}'

        post_list.sort(key=lambda x: x[PyPtt.PostField.index])
        print(json.dumps(post_list, indent=4, ensure_ascii=False))
        print(f'Total posts: {len(post_list)}')

    test_boards = [
        'Gossiping',
        'Stock',
        'Baseball',
        'NBA',
        'LoL',
        'Soft_Job',
        'Tech_Job',
        'Python',
        'xxxxx' # non-existent board
    ]

    for board in test_boards:
        print(f'Testing board: {board}')

        try:
            _test(board)
        except PyPtt.exceptions.NoSuchBoard:
            print(f'Board {board} does not exist, skipping...')
            assert board == 'xxxxx'
        except Exception as e:
            raise e



def func():
    host_list = [
        PyPtt.HOST.PTT1,
        # PyPtt.HOST.PTT2
    ]

    for host in host_list:
        ptt_bot = PyPtt.API(
            host=host,
            # log_level=PyPtt.LogLevel.DEBUG,
        )

        try:
            util.login(ptt_bot)
            test(ptt_bot)
        finally:
            ptt_bot.logout()


if __name__ == '__main__':
    func()
