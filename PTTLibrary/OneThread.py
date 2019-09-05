
from functools import wraps
import threading

try:
    import Log
    import Exceptions
except ModuleNotFoundError:
    from . import Log
    from . import Exceptions

ThreadID = None


def OneThreadFunc():
    def wrapper(f):
        @wraps(f)
        def inner_wrapper(*args, **kwargs):
            global ThreadID
            if ThreadID is None:
                ThreadID = threading.get_ident()
            else:
                CurrentThreadID = threading.get_ident()
                if CurrentThreadID != ThreadID:
                    Log.showValue(
                        Log.Level.DEBUG,
                        'ThreadID',
                        ThreadID
                    )
                    Log.showValue(
                        Log.Level.DEBUG,
                        'Current thread id',
                        CurrentThreadID
                    )
                    raise Exceptions.MultiThreadOperated()

            return f(*args, **kwargs)
        return inner_wrapper
    return wrapper


class OneThread:
    def __init_subclass__(cls, **kwargs):
        OneThreadF = OneThreadFunc()
        for name in cls.__dict__:
            if name.startswith('_') and name != '__init__':
                continue
            # print(name)
            attr = getattr(cls, name)
            if callable(attr):
                setattr(cls, name, OneThreadF(attr))
