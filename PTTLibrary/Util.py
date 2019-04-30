import sys
import time
from time import gmtime, strftime
from functools import wraps
from threading import Lock


def log(InputMessage):
    TotalMessage = "[" + strftime("%m-%d %H:%M:%S") + "]" + InputMessage

    try:
        print(TotalMessage.encode(sys.stdin.encoding, 
                                  "replace").decode(sys.stdin.encoding))
    except Exception:
        print(TotalMessage.encode('utf-8', "replace").decode('utf-8'))


def getTime():
    return strftime("%H:%M")


def showValue(Msg, Value):

    TotalMessage = []
    TotalMessage.append(Msg)
    TotalMessage.append(' [')
    TotalMessage.append(str(Value))
    TotalMessage.append(']')

    log(''.join(TotalMessage))


def synchronized(lock):
    def wrapper(f):
        @wraps(f)
        def inner_wrapper(*args, **kwargs):
            with lock:
                return f(*args, **kwargs)
        return inner_wrapper
    return wrapper


class SynchronizeAllMethod:
    def __init_subclass__(cls, **kwargs):
        sychronizer = synchronized(Lock())
        for name in cls.__dict__:
            attr = getattr(cls, name)
            if callable(attr):
                setattr(cls, name, sychronizer(attr))