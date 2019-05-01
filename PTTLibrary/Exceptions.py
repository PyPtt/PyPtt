try:
    from . import Config
    from . import Util
    from . import i18n
except:
    import Config
    import Util
    import i18n


class ParameterError(Exception):
    def __init__(self, message, Value):
        self.message = message + ' [' + str(Value) + ']'

    def __str__(self):
        return self.message


class InitError(Exception):
    def __init__(self, message, Value):
        self.message = message + ' [' + str(Value) + ']'

    def __str__(self):
        return self.message
