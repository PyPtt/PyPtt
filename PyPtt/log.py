import logging
from typing import Optional


class LogLv:
    _level: int = logging.NOTSET

    def __init__(self, level):
        self._level = level


INFO = LogLv(logging.INFO)
DEBUG = LogLv(logging.DEBUG)


class LogLevel:
    INFO = LogLv(logging.INFO)
    DEBUG = LogLv(logging.DEBUG)


class Logger:
    logger: logging.Logger = None
    level: LogLv = None

    def __init__(self, name: str, log_level: LogLv = INFO):
        self.level = log_level
        logging.basicConfig(datefmt='%m.%d %H:%M:%S',
                            format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s')

        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level._level)

    def info(self, *args):
        self.logger.info(' '.join([str(x) for x in args]))

    def debug(self, *args):
        if self.level._level > logging.DEBUG:
            return
        self.logger.debug(' '.join([str(x) for x in args]))


logger: Optional[Logger] = None


def init(log_level: LogLv, name: Optional[str] = None) -> Logger:
    name = name or 'PyPtt'
    current_logger = Logger(name, log_level=log_level)

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
