import sys
from time import gmtime, strftime
try:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import Exceptions
except:
    import DataType
    import Config
    import Util
    import i18n
    import Exceptions


class Level(object):

    DEBUG = 1
    INFO = 2
    SLIENT = 3

    MinValue = DEBUG
    MaxValue = SLIENT


def log(LogLevel, Msg):

    if not Util.checkRange(Level, LogLevel):
        raise Exceptions.ParameterError('LogLevel', LogLevel)

    if isinstance(Msg, list):

        if Config.Language == i18n.Language.Chinese:

            for i in range(len(Msg)):
                if Msg[i].isalnum():
                    Msg[i] = ' ' + Msg[i].strip() + ' '

            Msg = ''.join(Msg)
        else:
            Msg = ' '.join(Msg)

    Msg = Msg.replace('  ', ' ')

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

    if isinstance(Msg, list):
        if Config.Language == i18n.Language.Chinese:
            for i in range(len(Msg)):
                if Msg[i].upper() != Msg[i].lower():
                    Msg[i] = ' ' + Msg[i].strip() + ' '

            Msg = ''.join(Msg)
        else:
            Msg = ' '.join(Msg)

    TotalMessage = []
    TotalMessage.append(Msg)
    TotalMessage.append(' [')
    TotalMessage.append(str(Value))
    TotalMessage.append(']')

    log(LogLevel, ''.join(TotalMessage))

