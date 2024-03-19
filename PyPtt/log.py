import logging
from typing import Optional


class LogLv:
    _level: int = logging.NOTSET

    def __init__(self, level):
        self._level = level

    @property
    def level(self):
        return self._level


INFO = LogLv(logging.INFO)
DEBUG = LogLv(logging.DEBUG)


class LogLevel:
    INFO = LogLv(logging.INFO)
    DEBUG = LogLv(logging.DEBUG)


class Logger:
    logger: logging.Logger

    def __init__(self, name: str, level: int = logging.NOTSET):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

    def info(self, *args):
        self.logger.info(' '.join([str(x) for x in args]))

    def debug(self, *args):
        self.logger.debug(' '.join([str(x) for x in args]))


logger: Optional[Logger] = None


def init(log_level: LogLv, name: Optional[str] = None) -> Logger:
    name = name or 'PyPtt'
    current_logger = Logger(name, log_level.level)

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
