__version__ = '1.0.13'

from .PTT import API
from .data_type import *
from .exceptions import *
from .log import LogLevel, Logger, init
from .service import Service

# deprecated at 1.2
LOG_LEVEL = log.LogLevel
