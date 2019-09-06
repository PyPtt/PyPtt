
try:
    import Config
    import Util
    import i18n
except ModuleNotFoundError:
    from . import Config
    from . import Util
    from . import i18n


class Error(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


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


class LoginError(Exception):
    def __init__(self):
        self.message = [i18n.LoginFail]

    def __str__(self):

        if Config.Language == i18n.Language.Chinese:
            return ''.join(self.message)
        return ' '.join(self.message)


class NoFastPush(Exception):
    def __init__(self):
        self.message = [i18n.NoFastPush]

    def __str__(self):

        if Config.Language == i18n.Language.Chinese:
            return ''.join(self.message)
        return ' '.join(self.message)


class NoSuchUser(Exception):
    def __init__(self, User):
        self.message = i18n.NoSuchUser + ': ' + User

    def __str__(self):
        return self.message


class UserOffline(Exception):
    def __init__(self, User):
        self.message = i18n.UserOffline + ': ' + User

    def __str__(self):
        return self.message


class ParseError(Exception):
    def __init__(self, Screen):
        self.message = Screen

    def __str__(self):
        return self.message


class NoMoney(Exception):
    def __init__(self):
        self.message = i18n.NoMoney

    def __str__(self):
        return self.message


class MoneyTooFew(Exception):
    def __init__(self):
        self.message = i18n.MoneyTooFew

    def __str__(self):
        return self.message


class NoSuchBoard(Exception):
    def __init__(self, Board):
        self.message = i18n.NoSuchBoard + ': ' + Board

    def __str__(self):
        return self.message


class ConnectionClosed(Exception):
    def __init__(self):
        self.message = i18n.ConnectionClosed

    def __str__(self):
        return self.message


class UnregisteredUser(Exception):
    def __init__(self, ApiName):
        self.message = i18n.UnregisteredUserCantUseThisAPI + ': ' + ApiName

    def __str__(self):
        return self.message


class MultiThreadOperated(Exception):
    def __init__(self):
        self.message = i18n.MultiThreadOperate

    def __str__(self):
        return self.message


class WrongIDorPassword(Exception):
    def __init__(self):
        self.message = i18n.ErrorIDPW

    def __str__(self):
        return self.message


class LoginTooOften(Exception):
    def __init__(self):
        self.message = i18n.LoginTooOften

    def __str__(self):
        return self.message
