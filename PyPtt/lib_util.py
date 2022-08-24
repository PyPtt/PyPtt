import os
import random
import re
import string
import traceback
from enum import Enum
from typing import Tuple

from PyPtt import check_value


def check_range(define_obj, value) -> bool:
    if value < define_obj.min_value or define_obj.max_value < value:
        return False
    return True


def get_file_name(path_str: str) -> str:
    result = os.path.basename(path_str)
    result = result[:result.find('.')]
    return result


def get_current_func_name() -> str:
    return traceback.extract_stack(None, 2)[0][2]


def findnth(haystack, needle, n) -> int:
    parts = haystack.split(needle, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(haystack) - len(parts[-1]) - len(needle)


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


def get_random_str(length) -> str:
    return ''.join(random.choices(string.hexdigits, k=length))


def get_aid_from_url(url: str) -> Tuple[str, str]:
    # 檢查是否為字串
    check_value.check_type(str, 'url', url)

    # 檢查是否符合 PTT BBS 文章網址格式
    pattern = re.compile('https://www.ptt.cc/bbs/[-.\w]+/M.[\d]+.A[.\w]*.html')
    r = pattern.search(url)
    if r is None:
        raise ValueError('wrong parameter url must be www.ptt.cc post url')

    # 演算法參考 https://www.ptt.cc/man/C_Chat/DE98/DFF5/DB61/M.1419434423.A.DF0.html
    # aid 字元表
    aid_table = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'

    board = url[23:]
    board = board[:board.find('/')]

    temp = url[url.rfind('/') + 1:].split('.')
    # print(temp)

    id_0 = int(temp[1])  # dec

    aid_0 = ''
    for _ in range(6):
        index = id_0 % 64
        aid_0 = f'{aid_table[index]}{aid_0}'
        id_0 = int(id_0 / 64)

    if temp[3] != 'html':
        id_1 = int(temp[3], 16)  # hex
        aid_1 = ''
        for _ in range(2):
            index = id_1 % 64
            aid_1 = f'{aid_table[index]}{aid_1}'
            id_1 = int(id_1 / 64)
    else:
        aid_1 = '00'

    aid = f'{aid_0}{aid_1}'

    return board, aid


if __name__ == '__main__':
    for _ in range(5):
        print(get_random_str(10))
