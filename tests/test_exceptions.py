import pytest
import PyPtt
from PyPtt import data_type

@pytest.fixture(scope="module", autouse=True)
def init_i18n():
    """
    Initializes the i18n system by creating a dummy PyPtt.API instance.
    This is necessary for the exception message strings to be loaded.
    """

    PyPtt.API()

class MockConfig:
    def __init__(self, host, language):
        self.host = host
        self.language = language


config_ptt1 = MockConfig(data_type.HOST.PTT1, data_type.Language.MANDARIN)
config_ptt2 = MockConfig(data_type.HOST.PTT2, data_type.Language.ENGLISH)


exception_cases = [
    (PyPtt.UnknownError, ['test message']),
    (PyPtt.RequireLogin, ['test message']),
    (PyPtt.NoPermission, ['test message']),
    (PyPtt.LoginError, []),
    (PyPtt.NoFastComment, []),
    (PyPtt.NoSuchUser, ['testuser']),
    (PyPtt.NoSuchMail, []),
    (PyPtt.NoMoney, []),
    (PyPtt.NoSuchBoard, [config_ptt1, 'testboard']),
    (PyPtt.NoSuchBoard, [config_ptt2, 'testboard']),
    (PyPtt.ConnectionClosed, []),
    (PyPtt.UnregisteredUser, ['testapi']),
    (PyPtt.MultiThreadOperated, []),
    (PyPtt.WrongIDorPassword, []),
    (PyPtt.WrongPassword, []),
    (PyPtt.LoginTooOften, []),
    (PyPtt.UseTooManyResources, []),
    (PyPtt.HostNotSupport, ['testapi']),
    (PyPtt.CantComment, []),
    (PyPtt.CantResponse, []),
    (PyPtt.NeedModeratorPermission, ['testboard']),
    (PyPtt.ConnectError, [config_ptt1]),
    (PyPtt.NoSuchPost, ['testboard', 'testaid']),
    (PyPtt.CanNotUseSearchPostCode, []),
    (PyPtt.UserHasPreviouslyBeenBanned, []),
    (PyPtt.MailboxFull, []),
    (PyPtt.NoSearchResult, []),
    (PyPtt.OnlySecureConnection, []),
    (PyPtt.SetContactMailFirst, []),
    (PyPtt.ResetYourContactEmail, []),
    (PyPtt.ParameterError, ['test message']),
]


@pytest.mark.parametrize("exception_class, args", exception_cases)
def test_exceptions(exception_class, args):
    with pytest.raises(exception_class):
        raise exception_class(*args)
