try:
    from . import data_type
    from . import i18n
except ModuleNotFoundError:
    import data_type
    import i18n


class Error(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class UnknownError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Requirelogin(Exception):
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
        self.message = i18n.loginFail

    def __str__(self):
        return self.message


class NoFastPush(Exception):
    def __init__(self):
        self.message = i18n.NoFastPush

    def __str__(self):
        return self.message


class NoSuchUser(Exception):
    def __init__(self, user):
        self.message = i18n.NoSuchUser + ': ' + user

    def __str__(self):
        return self.message


class UserOffline(Exception):
    def __init__(self, user):
        self.message = i18n.UserOffline + ': ' + user

    def __str__(self):
        return self.message


class ParseError(Exception):
    def __init__(self, screen):
        self.message = screen

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
    def __init__(self, config, board):
        if config.host == data_type.host_type.PTT1:
            self.message = [
                i18n.PTT,
                i18n.NoSuchBoard
            ]
        else:
            self.message = [
                i18n.PTT2,
                i18n.NoSuchBoard
            ]

        if config.language == i18n.language.CHINESE:
            self.message = ''.join(self.message) + ': ' + board
        else:
            self.message = ' '.join(self.message) + ': ' + board

    def __str__(self):
        return self.message


class ConnectionClosed(Exception):
    def __init__(self):
        self.message = i18n.ConnectionClosed

    def __str__(self):
        return self.message


class UnregisteredUser(Exception):
    def __init__(self, api_name):
        self.message = i18n.UnregisteredUserCantUseThisAPI + ': ' + api_name

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


class WrongPassword(Exception):
    def __init__(self):
        self.message = i18n.ErrorPW

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
    def __init__(self, api):
        self.message = f'{i18n.PTT2NotSupport}: {api}'

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
    def __init__(self, board):
        self.message = f'{i18n.NeedModeratorPermission}: {board}'

    def __str__(self):
        return self.message


class ConnectError(Exception):
    def __init__(self, config):
        self.message = [i18n.Connect, i18n.Fail]

        if config.language == i18n.language.CHINESE:
            self.message = ''.join(self.message)
        else:
            self.message = ' '.join(self.message)

    def __str__(self):
        return self.message


class NoMatchTargetError(Exception):
    def __init__(self, screen_queue: list):
        self.ScreenQueue = screen_queue

    def __str__(self):
        screens = ('\n' + '-' * 50 + '\n').join(self.ScreenQueue.get(3))
        return screens + '\n' + i18n.ScreenNoMatchTarget


class NoSuchPost(Exception):
    def __init__(self, board, aid):
        self.message = i18n.replace(
            i18n.NoSuchPost,
            board,
            aid
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


class MailboxFull(Exception):
    def __init__(self):
        self.message = i18n.MailBoxFull

    def __str__(self):
        return self.message


class Timeout(Exception):
    def __init__(self):
        self.message = i18n.timeout

    def __str__(self):
        return self.message


class NoSearchResult(Exception):
    def __init__(self):
        self.message = i18n.NoSearchResult

    def __str__(self):
        return self.message


# 此帳號已設定為只能使用安全連線

class OnlySecureConnection(Exception):
    def __init__(self):
        self.message = i18n.OnlySecureConnection

    def __str__(self):
        return self.message
