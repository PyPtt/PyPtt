import functools
import os
import random
import re
import string
import time
import traceback
from typing import Tuple

import requests

from . import __version__
from . import check_value
from . import data_type
from . import i18n
from . import log


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


def get_random_str(length) -> str:
    return ''.join(random.choices(string.hexdigits, k=length))


# 演算法參考 https://www.ptt.cc/man/C_Chat/DE98/DFF5/DB61/M.1419434423.A.DF0.html
# aid 字元表
aid_table = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'


def get_aid_from_url(url: str) -> Tuple[str, str]:
    # 檢查是否為字串
    check_value.check_type(url, str, 'url')

    # 檢查是否符合 PTT BOARD 文章網址格式
    pattern = re.compile(r'https://www.ptt.cc/bbs/[-.\w]+/M.[\d]+.A[.\w]*.html')
    r = pattern.search(url)
    if r is None:
        raise ValueError('wrong parameter url must be www.ptt.cc post url')

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


sync_version_compare: data_type.Compare = data_type.Compare.UNKNOWN
sync_version_result: str = ''


def sync_version() -> Tuple[data_type.Compare, str]:
    global sync_version_compare
    global sync_version_result

    if sync_version_compare is not data_type.Compare.UNKNOWN:
        return sync_version_compare, sync_version_result

    log.logger.info(i18n.update_remote_version)

    r = None
    for i in range(3):
        try:
            r = requests.get(
                'https://raw.githubusercontent.com/PyPtt/PyPtt/master/PyPtt/__init__.py',
                timeout=3)
            break
        except requests.exceptions.ReadTimeout:
            log.logger.info(i18n.retry)
            time.sleep(0.5)

    if r is None:
        log.logger.info(i18n.update_remote_version, '...', i18n.fail)
        return data_type.Compare.SAME, ''

    log.logger.info(i18n.update_remote_version, '...', i18n.success)

    text = r.text

    remote_version = [line for line in text.split('\n') if line.startswith('__version__')][0]
    remote_version = remote_version[remote_version.find("'") + 1:]
    remote_version = remote_version[:remote_version.find("'")]

    current_version = __version__
    if 'dev' in current_version:
        current_version = current_version[:current_version.find('dev') - 1]

    version_list = [int(v) for v in current_version.split('.')]
    remote_version_list = [int(v) for v in remote_version.split('.')]

    sync_version_compare = data_type.Compare.SAME
    for i in range(len(version_list)):
        if remote_version_list[i] < version_list[i]:
            sync_version_compare = data_type.Compare.BIGGER
            break
        if version_list[i] < remote_version_list[i]:
            sync_version_compare = data_type.Compare.SMALLER
            break
    return sync_version_compare, remote_version


def uniform_new_line(text: str) -> str:
    random_tag = get_random_str(10)

    text = text.replace('\r\n', random_tag)
    text = text.replace('\n', '\r\n')
    text = text.replace(random_tag, '\r\n')

    return text


@functools.lru_cache(maxsize=64)
def check_aid(aid: str) -> str:
    if aid is None:
        raise ValueError('aid is None')

    if not isinstance(aid, str):
        raise TypeError('aid is not str')

    if aid.startswith('#'):
        aid = aid[1:]

    if len(aid) != 8:
        raise ValueError('aid is not valid')

    # check the char of aid is in aid_table or not
    for char in aid:
        if char not in aid_table:
            raise ValueError('aid is not valid')

    return f'#{aid}'


if __name__ == '__main__':
    check_aid('#1aBzRW4z')
