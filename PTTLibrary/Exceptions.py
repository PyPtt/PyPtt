
try:
    from . import DataType
    from . import i18n
except ModuleNotFoundError:
    import DataType
    import i18n

Config = None


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
        # self.message = i18n.NoSuchBoard + ': ' + Board
        self.board = Board
        if Config.Host == DataType.Host.PTT1:
            self.message = [
                i18n.PTT,
                i18n.NoSuchBoard
            ]
        else:
            self.message = [
                i18n.PTT2,
                i18n.NoSuchBoard
            ]

    def __str__(self):

        if Config.Language == i18n.Language.Chinese:
            return ''.join(self.message) + ': ' + self.board
        return ' '.join(self.message) + ': ' + self.board


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


class UseTooManyResources(Exception):
    def __init__(self):
        self.message = i18n.UseTooManyResources

    def __str__(self):
        return self.message


class HostNotSupport(Exception):
    def __init__(self, API):
        self.message = f'{i18n.PTT2NotSupport}: {API}'

    def __str__(self):
        return self.message


class NoPush(Exception):
    def __init__(self):
        self.message = i18n.NoPush

    def __str__(self):
        return self.message


class NoResponse(Exception):
    def __init__(self):
        self.message = i18n.NoResponse

    def __str__(self):
        return self.message


class NeedModeratorPermission(Exception):
    def __init__(self, Board):
        self.message = f'{i18n.NeedModeratorPermission}: {Board}'

    def __str__(self):
        return self.message


class ConnectError(Exception):
    def __init__(self):
        self.message = [i18n.Connect, i18n.Fail]

    def __str__(self):

        if Config.Language == i18n.Language.Chinese:
            return ''.join(self.message)
        return ' '.join(self.message)


class NoMatchTargetError(Exception):
    def __init__(self, ScreenQueue: list):
        self.ScreenQueue = ScreenQueue

    def __str__(self):
        Screens = ('\n' + '-' * 50 + '\n').join(self.ScreenQueue.get(3))
        return Screens + '\n' + i18n.ScreenNoMatchTarget


class NoSuchPost(Exception):
    def __init__(self, Board, AID):
        self.message = i18n.replace(
            i18n.NoSuchPost,
            Board,
            AID
        )

    def __str__(self):
        return self.message


class CanNotUseSearchPostCode(Exception):
    def __init__(self):
        self.message = i18n.CanNotUseSearchPostCodeF

    def __str__(self):
        return self.message


class UserHasPreviouslyBeenBanned(Exception):
    def __init__(self):
        self.message = i18n.UserHasPreviouslyBeenBanned

    def __str__(self):
        return self.message
