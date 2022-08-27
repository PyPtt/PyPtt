from SingleLog.log import Logger

LOG_LEVEL = Logger
version = '1.0.0'

from .PTT import API
from .data_type import HOST
from .data_type import NewIndex
from .data_type import PostField
from .data_type import PostStatus
from .data_type import SearchType
from .data_type import ConnectMode
from .data_type import Language

from .exceptions import LoginError
from .exceptions import WrongIDorPassword
from .exceptions import LoginTooOften
