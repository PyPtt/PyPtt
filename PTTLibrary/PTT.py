import sys
import time

try:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import Exceptions
    from . import ConnectCore
    from . import ErrorCode
    from . import Log
    from . import Synchronize
except FileNotFoundError:
    import DataType
    import Config
    import Util
    import i18n
    import Exceptions
    import ConnectCore
    import ErrorCode
    import Log
    import Synchronize

Version = Config.Version

ErrorCode = ErrorCode.ErrorCode()
Language = i18n.Language
ConnectMode = ConnectCore.ConnectMode
LogLevel = Log.Level


class Library(Synchronize.SynchronizeAllMethod):
    def __init__(self,
                 Language: int=0,
                 ConnectMode: int=0,
                 LogLevel: int=0,
                 ):
        if LogLevel == 0:
            LogLevel = Config.LogLevel
        elif not Util.checkRange(Log.Level, LogLevel):
            raise Exceptions.ParameterError('Unknow LogLevel', LogLevel)
        else:
            Config.LogLevel = LogLevel

        if Language == 0:
            Language = Config.Language
        elif not Util.checkRange(i18n.Language, Language):
            raise Exceptions.ParameterError('Unknow language', Language)
        else:
            Config.Language = Language
        i18n.load(Language)

        if ConnectMode == 0:
            ConnectMode = Config.ConnectMode
        elif not Util.checkRange(DataType.ConnectMode, ConnectMode):
            raise Exceptions.ParameterError('Unknow ConnectMode',
                                            ConnectMode)
        else:
            Config.ConnectMode = ConnectMode
        self._ConnectCore = ConnectCore.API(ConnectMode)

        Log.showValue(Log.Level.INFO, [
            i18n.PTT,
            i18n.Library,
            ' v ' + Version,
            ],
            i18n.Active
        )

    def login(self, ID: str, Password: str):

        self._ConnectCore.connect()
        qqq
        return ErrCode

    def logout(self):
        pass

    def log(self, Msg):
        Log.log(Log.Level.INFO, Msg)

if __name__ == '__main__':

    print('PTT Library v ' + Version)
    print('Developed by PTT CodingMan')
