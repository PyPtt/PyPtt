import sys

from SingleLog.log import Logger

import PyPtt

if __name__ == '__main__':
    logger = Logger('TEST INIT')

    logger.info('===正向===')
    logger.info('===預設值===')
    PyPtt.API()
    logger.info('===中文顯示===')
    PyPtt.API(language=PyPtt.i18n.language.CHINESE)
    logger.info('===英文顯示===')
    PyPtt.API(language=PyPtt.i18n.language.ENGLISH)
    logger.info('===log DEBUG===')
    PyPtt.API(log_level=PyPtt.LOG_LEVEL.DEBUG)
    logger.info('===log INFO===')
    PyPtt.API(log_level=PyPtt.LOG_LEVEL.INFO)
    logger.info('===log SLIENT===')
    PyPtt.API(log_level=PyPtt.LOG_LEVEL.SILENT)
    logger.info('===log SLIENT======')

    logger.info('===負向===')
    try:
        logger.info('===語言 99===')
        PyPtt.API(language=99)
    except ValueError:
        logger.info('通過')
    except:
        logger.info('沒通過')
        sys.exit(-1)
    logger.info('===語言放字串===')
    try:
        PyPtt.API(language='PyPtt.i18n.language.ENGLISH')
    except TypeError:
        logger.info('通過')
    except:
        logger.info('沒通過')
        sys.exit(-1)


    def handler(msg):
        with open('log.txt', 'a', encoding='utf-8') as f:
            f.write(msg + '\n')


    ptt_bot = PyPtt.API(
        log_handler=handler)
    logger.info('Test log')
