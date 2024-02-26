__version__ = '1.0.12'

from .PTT import API
from .data_type import *
from .exceptions import *
from .log import LogLevel
from .service import Service

# deprecated at 1.2
LOG_LEVEL = LogLevel
