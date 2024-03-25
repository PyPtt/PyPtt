import os
import sys

sys.path.append(os.getcwd())
from PyPtt import log


def func():
    logger = log.init(log.INFO)

    logger.info('1')
    logger.info('1', '2')
    logger.info('1', '2', '3')

    logger.debug('debug 1')
    logger.debug('1', '2')
    logger.debug('1', '2', '3')

    logger = log.init(log.DEBUG)

    logger.info('234')
    logger.info('1', '2')
    logger.info('1', '2', '3')

    logger.debug('debug 2')
    logger.debug('1', '2')
    logger.debug('1', '2', '3')


if __name__ == '__main__':
    func()
