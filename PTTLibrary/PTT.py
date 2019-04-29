import sys
import time
import types

try:
    from . import Util
    from . import DataType
    from . import Config
    from . import i18n
except:
    import Util
    import DataType
    import Config
    import i18n

Version = Config.Version


class Library(object):

    def __init__(self):
        pass

    def login(self):
        pass

    def logout(self):
        pass

if __name__ == '__main__':

    print('PTT Library v ' + Version)
    print('Developed by PTT CodingMan')

    print(i18n.load(DataType.Language.English))
    print(i18n.ConnectMode)
