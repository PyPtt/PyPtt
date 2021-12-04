from SingleLog.log import Logger

LOG_LEVEL = Logger

from .config import Config

version = Config.version

from .PTT import API

from .data_type import HOST
from .data_type import Article
from .data_type import ArticleDelStatus
from .exceptions import *
from .i18n import Lang
