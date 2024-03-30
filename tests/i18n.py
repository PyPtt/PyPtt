import os
import sys

sys.path.append(os.getcwd())

import PyPtt
from PyPtt import i18n
from PyPtt import log


def test():
    PyPtt.i18n.init(PyPtt.Language.ENGLISH)

    print(PyPtt.i18n.goodbye)

    logger = log.init(PyPtt.LogLevel.INFO, 'test')
    logger.info(
        i18n.replace(i18n.welcome, 'test version'))


if __name__ == '__main__':
    test()
