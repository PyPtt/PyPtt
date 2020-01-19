import sys
from time import strftime

try:
    from . import Util
    from . import i18n
except ModuleNotFoundError:
    import Util
    import i18n


class Level(object):

    TRACE = 1
    DEBUG = 2
    INFO = 3
    SLIENT = 4

    MinValue = TRACE
    MaxValue = SLIENT


def merge(Config, Msg) -> str:
    if isinstance(Msg, list):
        if Config.Language == i18n.Language.Chinese:

            for i, element in enumerate(Msg):
                if len(element) == 0:
                    continue
                if element[0].upper() != element[0].lower() and i != 0:
                    Msg[i] = ' ' + element.lstrip()
                if (element[-1].upper() != element[-1].lower() and
                        i != len(Msg) - 1):
                    Msg[i] = element.lstrip() + ' '

            Msg = ''.join(Msg)
        else:
            Msg = ' '.join(Msg)
    Msg = str(Msg)
    Msg = Msg.replace('  ', ' ')

    return Msg


def log(Config, LogLevel, Msg):

    if not Util.checkRange(Level, LogLevel):
        raise ValueError('LogLevel', LogLevel)

    if Config.LogLevel > LogLevel:
        return
    if len(Msg) == 0:
        return
    Msg = merge(Config, Msg)

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


def showValue(Config, LogLevel, Msg, Value):

    if not Util.checkRange(Level, LogLevel):
        raise ValueError('LogLevel', LogLevel)

    if Config.LogLevel > LogLevel:
        return
    global LastValue

    CheckPTTMsg = merge(Config, [i18n.PTT, i18n.Msg])
    Msg = merge(Config, Msg)
    Value = merge(Config, Value)

    if len(Msg) == 0:
        return
    # if len(Value) == 0:
    #     return

    if CheckPTTMsg == Msg and Value == LastValue:
        return

    TotalMessage = []
    TotalMessage.append(Msg)
    TotalMessage.append(' [')
    TotalMessage.append(Value)
    TotalMessage.append(']')

    log(Config, LogLevel, ''.join(TotalMessage))

    LastValue = Value
