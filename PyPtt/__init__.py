from SingleLog.log import Logger

LOG_LEVEL = Logger
version = '1.0.0'

from .PTT import API
from .data_type import HOST
from .data_type import Post
from .data_type import PostDelStatus
from .data_type import SearchType
from .data_type import NewIndex
from .exceptions import *
from .i18n import Lang
