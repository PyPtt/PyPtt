import sys
import time
import types

try:
    from . import Util
    from . import Config
except:
    import Util
    import Config

Version = Config.Version


class Library(object):

    def __init__(self):
        pass
    
    def method1(self):
        pass

    def method2(self):
        pass
        

if __name__ == '__main__':

    print('PTT Library v ' + Version)
    print('Developed by PTT CodingMan')
