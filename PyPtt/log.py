import logging
from typing import Optional


class LogLv:
    _level: int

    def __init__(self, level):
        self._level = level

    @property
    def level(self):
        return self._level

    def __eq__(self, other):
        return self.level == other.level


SILENT = LogLv(logging.NOTSET)
INFO = LogLv(logging.INFO)
DEBUG = LogLv(logging.DEBUG)

# deprecated use DEBUG instead
TRACE = DEBUG


class LogLevel:
    SILENT = LogLv(logging.NOTSET)
    INFO = LogLv(logging.INFO)
    DEBUG = LogLv(logging.DEBUG)
    TRACE = DEBUG


logger_pool = {}
formatter = logging.Formatter(
    fmt='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
    datefmt='%m.%d %H:%M:%S')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)


def _combine_msg(*args) -> str:
    msg = [str(x) for x in args]
    msg = ' '.join(msg)
    return msg


class Logger:
    logger: logging.Logger

    def __init__(self, name: str, level: int = logging.NOTSET, logger_callback: Optional[callable] = None):

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        self.logger.addHandler(console_handler)

        self.logger_callback: Optional[callable] = None
        if logger_callback and callable(logger_callback):
            self.logger_callback = logger_callback

    def info(self, *args):

        if not self.logger.isEnabledFor(logging.INFO):
            return

        msg = _combine_msg(*args)
        self.logger.info(msg)
        if self.logger_callback:
            self.logger_callback(msg)

    def debug(self, *args):

        if not self.logger.isEnabledFor(logging.DEBUG):
            return

        msg = _combine_msg(*args)
        self.logger.debug(msg)
        if self.logger_callback:
            self.logger_callback(msg)


logger: Optional[Logger] = None


def init(log_level: LogLv, name: Optional[str] = None, logger_callback: Optional[callable] = None) -> Logger:
    name = name or 'PyPtt'
    current_logger = Logger(name, level=log_level.level, logger_callback=logger_callback)

    if name == 'PyPtt':
        global logger
        logger = current_logger
    return current_logger


if __name__ == '__main__':
    logger = init(INFO)

    logger.info('1')
    logger.info('1', '2')
    logger.info('1', '2', '3')

    logger.debug('debug 1')
    logger.debug('1', '2')
    logger.debug('1', '2', '3')

    logger = init(DEBUG)

    logger.info('1')
    logger.info('1', '2')
    logger.info('1', '2', '3')

    logger.debug('debug 2')
    logger.debug('1', '2')
    logger.debug('1', '2', '3')
