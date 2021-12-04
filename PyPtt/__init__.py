from SingleLog.log import Logger

LOG_LEVEL = Logger
version = '1.0.0'
host = None

from .PTT import API

from .data_type import HOST
from .data_type import Article
from .data_type import ArticleDelStatus
from .exceptions import *
from .i18n import Lang
