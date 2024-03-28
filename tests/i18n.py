import os
import sys

sys.path.append(os.getcwd())

import PyPtt


def test():
    PyPtt.i18n.init(PyPtt.Language.ENGLISH)

    print(PyPtt.i18n.goodbye)


if __name__ == '__main__':
    test()
