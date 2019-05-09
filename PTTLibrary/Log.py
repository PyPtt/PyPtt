import sys
from time import gmtime, strftime
try:
    import DataType
    import Config
    import Util
    import i18n
except ModuleNotFoundError:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n


class Level(object):

    DEBUG = 1
    INFO = 2
    SLIENT = 3

    MinValue = DEBUG
    MaxValue = SLIENT


def merge(Msg) ->str:
    if isinstance(Msg, list):
        if Config.Language == i18n.Language.Chinese:

            for i in range(len(Msg)):
                if Msg[i][0].upper() != Msg[i][0].lower() and i != 0:
                    Msg[i] = ' ' + Msg[i].lstrip()
                if (Msg[i][-1].upper() != Msg[i][-1].lower() and
                   i != len(Msg) - 1):
                    Msg[i] = Msg[i].rstrip() + ' '
                
            Msg = ''.join(Msg)
        else:
            Msg = ' '.join(Msg)
    Msg = str(Msg)
    Msg = Msg.replace('  ', ' ')

    return Msg


def log(LogLevel, Msg):

    if not Util.checkRange(Level, LogLevel):
        raise ValueError('LogLevel', LogLevel)

    Msg = merge(Msg)

    TotalMessage = '[' + strftime('%m%d %H:%M:%S') + ']'
    if LogLevel == Level.DEBUG:
        TotalMessage += '[' + i18n.Debug + '] ' + Msg
    elif LogLevel == Level.INFO:
        TotalMessage += '[' + i18n.Info + '] ' + Msg

    try:
        print(TotalMessage.encode(sys.stdin.encoding,
                                  "replace").decode(sys.stdin.encoding))
    except Exception:
        print(TotalMessage.encode('utf-8', "replace").decode('utf-8'))


def showValue(LogLevel, Msg, Value):

    if not Util.checkRange(Level, LogLevel):
        raise ValueError('LogLevel', LogLevel)

    if Config.LogLevel > LogLevel:
        return

    Msg = merge(Msg)
    Value = merge(Value)

    TotalMessage = []
    TotalMessage.append(Msg)
    TotalMessage.append(' [')
    TotalMessage.append(Value)
    TotalMessage.append(']')

    log(LogLevel, ''.join(TotalMessage))
