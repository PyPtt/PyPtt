import sys
import time

try:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import Exceptions
    from . import Core
    from . import ErrorCode
    from . import Synchronize
except FileNotFoundError:
    import DataType
    import Config
    import Util
    import i18n
    import Exceptions
    import Core
    import ErrorCode
    import Synchronize

Version = Config.Version
ErrorCode = ErrorCode.ErrorCode()
Language = DataType.Language
ConnectionMode = DataType.ConnectionMode


class Library(Synchronize.SynchronizeAllMethod):

    def __init__(self,
                 Language: int=0,
                 ConnectionMode: int=0,
                 ):

        if Language == 0:
            Language = Config.Language
        elif not Util.checkRange(DataType.Language, Language):
            raise Exceptions.ParameterError('Unknow language', Language)
        else:
            Config.Language = Language
        i18n.load(Language)

        Util.showValue([
            i18n.i18n,
            i18n.Init,
            ],
            i18n.Done
        )

        if ConnectionMode == 0:
            ConnectionMode = Config.ConnectionMode
        elif not Util.checkRange(DataType.ConnectionMode, ConnectionMode):
            Util.showValue(i18n.ErrorParameter, ConnectionMode)
            return
        else:
            Config.ConnectionMode = ConnectionMode
        self._Core = Core.API(ConnectionMode)

        Util.showValue([
            i18n.PTT,
            i18n.Library,
            ' v ' + Version,
            i18n.Init,
            ],
            i18n.Done
        )

    def login(self, ID: str, Password: str):
        ErrCode = self._Core.connect()

        return ErrCode
        
    def logout(self):
        pass

    def log(self, Msg):
        Util.log(Msg)

if __name__ == '__main__':

    print('PTT Library v ' + Version)
    print('Developed by PTT CodingMan')
