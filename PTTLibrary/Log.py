import sys
from time import gmtime, strftime
try:
    import DataType
    import Config
    import Util
    import i18n
    import Exceptions
except ModuleNotFoundError:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import Exceptions


class Level(object):

    DEBUG = 1
    INFO = 2
    SLIENT = 3

    MinValue = DEBUG
    MaxValue = SLIENT


def _merge(Msg):
    if isinstance(Msg, list):
        if Config.Language == i18n.Language.Chinese:
            for i in range(len(Msg)):
                if Msg[i].upper() != Msg[i].lower():
                    Msg[i] = ' ' + Msg[i].strip() + ' '

            Msg = ''.join(Msg)
        else:
            Msg = ' '.join(Msg)
    Msg = str(Msg)
    Msg = Msg.replace('  ', ' ')
    
    return Msg


def log(LogLevel, Msg):

    if not Util.checkRange(Level, LogLevel):
        raise Exceptions.ParameterError('LogLevel', LogLevel)

    Msg = _merge(Msg)

    TotalMessage = '[' + strftime('%m%d %H:%M:%S') + ']'
    if LogLevel == Level.DEBUG:
        TotalMessage += '[' + i18n.Debug + '] ' + Msg
    elif LogLevel == Level.INFO:
        TotalMessage += '[' + i18n.Info + '] ' + Msg

    # [' +  + '] ' + Msg

    try:
        print(TotalMessage.encode(sys.stdin.encoding,
                                  "replace").decode(sys.stdin.encoding))
    except Exception:
        print(TotalMessage.encode('utf-8', "replace").decode('utf-8'))


def showValue(LogLevel, Msg, Value):

    if not Util.checkRange(Level, LogLevel):
        raise Exceptions.ParameterError('LogLevel', LogLevel)

    if Config.LogLevel > LogLevel:
        return

    Msg = _merge(Msg)
    Value = _merge(Value)

    TotalMessage = []
    TotalMessage.append(Msg)
    TotalMessage.append(' [')
    TotalMessage.append(Value)
    TotalMessage.append(']')

    log(LogLevel, ''.join(TotalMessage))

