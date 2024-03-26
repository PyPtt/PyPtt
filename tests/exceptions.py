import os
import sys

sys.path.append(os.getcwd())
import PyPtt

if __name__ == '__main__':
    try:
        raise PyPtt.NoPermission('test')

    except PyPtt.Error as e:
        print(e.__class__.__name__)
