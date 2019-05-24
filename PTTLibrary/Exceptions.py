
try:
    import Config
    import Util
    import i18n
except ModuleNotFoundError:
    from . import Config
    from . import Util
    from . import i18n


class UnknowError(Exception):
    def __init__(self, message):

        self.message = message

    def __str__(self):
        return self.message


class RequireLogin(Exception):
    def __init__(self, message):

        self.message = message

    def __str__(self):
        return self.message


class NoPermission(Exception):
    def __init__(self, message):

        self.message = message

    def __str__(self):
        return self.message

