
from functools import wraps
from threading import Lock


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
            if name.startswith('_'):
                continue
            # print(name)
            attr = getattr(cls, name)
            if callable(attr):
                setattr(cls, name, sychronizer(attr))

        # print('Synchronize complete')