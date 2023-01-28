from . import data_type
from . import i18n


class Error(Exception):
    pass


class UnknownError(Error):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class RequireLogin(Error):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class NoPermission(Error):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class LoginError(Error):
    def __init__(self):
        self.message = i18n.login_fail

    def __str__(self):
        return self.message


class NoFastComment(Error):
    def __init__(self):
        self.message = i18n.no_fast_comment

    def __str__(self):
        return self.message


class NoSuchUser(Error):
    def __init__(self, user):
        self.message = i18n.no_such_user + ': ' + user

    def __str__(self):
        return self.message


class NoSuchMail(Error):
    def __init__(self):
        self.message = i18n.no_such_mail

    def __str__(self):
        return self.message


# class UserOffline(Error):
#     def __init__(self, user):
#         self.message = i18n.user_offline + ': ' + user
#
#     def __str__(self):
#         return self.message


# class ParseError(Error):
#     def __init__(self, screen):
#         self.message = screen
#
#     def __str__(self):
#         return self.message


class NoMoney(Error):
    def __init__(self):
        self.message = i18n.no_money

    def __str__(self):
        return self.message


class NoSuchBoard(Error):
    def __init__(self, config, board):
        if config.host == data_type.HOST.PTT1:
            self.message = [
                i18n.PTT,
                i18n.no_such_board
            ]
        else:
            self.message = [
                i18n.PTT2,
                i18n.no_such_board
            ]

        if config.language == data_type.Language.MANDARIN:
            self.message = ''.join(self.message) + ': ' + board
        else:
            self.message = ' '.join(self.message) + ': ' + board

    def __str__(self):
        return self.message


class ConnectionClosed(Error):
    def __init__(self):
        self.message = i18n.connection_closed

    def __str__(self):
        return self.message


class UnregisteredUser(Error):
    def __init__(self, api_name):
        self.message = i18n.unregistered_user_cant_use_this_api + ': ' + api_name

    def __str__(self):
        return self.message


class MultiThreadOperated(Error):
    def __init__(self):
        self.message = i18n.multi_thread_operate

    def __str__(self):
        return self.message


class WrongIDorPassword(Error):
    def __init__(self):
        self.message = i18n.wrong_id_pw

    def __str__(self):
        return self.message


class WrongPassword(Error):
    def __init__(self):
        self.message = i18n.error_pw

    def __str__(self):
        return self.message


class LoginTooOften(Error):
    def __init__(self):
        self.message = i18n.login_too_often

    def __str__(self):
        return self.message


class UseTooManyResources(Error):
    def __init__(self):
        self.message = i18n.use_too_many_resources

    def __str__(self):
        return self.message


class HostNotSupport(Error):
    def __init__(self, api):
        self.message = f'{i18n.ptt2_not_support}: {api}'

    def __str__(self):
        return self.message


class CantComment(Error):
    def __init__(self):
        self.message = i18n.no_comment

    def __str__(self):
        return self.message


class CantResponse(Error):
    def __init__(self):
        self.message = i18n.no_response

    def __str__(self):
        return self.message


class NeedModeratorPermission(Error):
    def __init__(self, board):
        self.message = f'{i18n.need_moderator_permission}: {board}'

    def __str__(self):
        return self.message


class ConnectError(Error):
    def __init__(self, config):
        self.message = i18n.connect_fail

    def __str__(self):
        return self.message


class NoSuchPost(Error):
    def __init__(self, board, aid):
        self.message = i18n.replace(
            i18n.no_such_post,
            board,
            aid)

    def __str__(self):
        return self.message


class CanNotUseSearchPostCode(Error):
    """
    此狀態下無法使用搜尋文章代碼(AID)功能
    """

    def __init__(self):
        self.message = i18n.can_not_use_search_post_code_f

    def __str__(self):
        return self.message


class UserHasPreviouslyBeenBanned(Error):
    def __init__(self):
        self.message = i18n.user_has_previously_been_banned

    def __str__(self):
        return self.message


class MailboxFull(Error):
    def __init__(self):
        self.message = i18n.mail_box_full

    def __str__(self):
        return self.message


class NoSearchResult(Error):
    def __init__(self):
        self.message = i18n.no_search_result

    def __str__(self):
        return self.message


# 此帳號已設定為只能使用安全連線

class OnlySecureConnection(Error):
    def __init__(self):
        self.message = i18n.only_secure_connection

    def __str__(self):
        return self.message


class SetContactMailFirst(Error):
    def __init__(self):
        self.message = i18n.set_contact_mail_first

    def __str__(self):
        return self.message


class ResetYourContactEmail(Error):
    def __init__(self):
        self.message = i18n.reset_your_contact_email

    def __str__(self):
        return self.message
