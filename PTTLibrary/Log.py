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

    TRACE = 1
    DEBUG = 2
    INFO = 3
    SLIENT = 4

    MinValue = TRACE
    MaxValue = SLIENT


def merge(Msg) -> str:
    if isinstance(Msg, list):
        if Config.Language == i18n.Language.Chinese:
            for i in range(len(Msg)):
                if len(Msg[i]) == 0:
                    continue
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

    if Config.LogLevel > LogLevel:
        return
    if len(Msg) == 0:
        return
    Msg = merge(Msg)

    TotalMessage = '[' + strftime('%m%d %H:%M:%S') + ']'
    if LogLevel == Level.DEBUG:
        TotalMessage += '[' + i18n.Debug + '] ' + Msg
    elif LogLevel == Level.INFO:
        TotalMessage += '[' + i18n.Info + '] ' + Msg

    try:
        print(TotalMessage.encode(
            sys.stdin.encoding,
            'replace'
        ).decode(
            sys.stdin.encoding
        ))
    except Exception:
        print(TotalMessage.encode('utf-8', "replace").decode('utf-8'))

    if Config.LogHandler is not None:
        Config.LogHandler(TotalMessage)


LastValue = None


def showValue(LogLevel, Msg, Value):

    if not Util.checkRange(Level, LogLevel):
        raise ValueError('LogLevel', LogLevel)

    if Config.LogLevel > LogLevel:
        return
    global LastValue

    CheckPTTMsg = merge([i18n.PTT, i18n.Msg])
    Msg = merge(Msg)
    Value = merge(Value)

    if len(Msg) == 0:
        return
    if len(Value) == 0:
        return

    if CheckPTTMsg == Msg and Value == LastValue:
        return

    TotalMessage = []
    TotalMessage.append(Msg)
    TotalMessage.append(' [')
    TotalMessage.append(Value)
    TotalMessage.append(']')

    log(LogLevel, ''.join(TotalMessage))

    LastValue = Value
