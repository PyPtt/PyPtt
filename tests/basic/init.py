import PyPtt
from .. import util


def test():
    util.logger.info('===預設值===')
    PyPtt.API()
    util.logger.info('===中文顯示===')
    PyPtt.API(language=PyPtt.Lang.CHINESE)
    util.logger.info('===英文顯示===')
    PyPtt.API(language=PyPtt.Lang.ENGLISH)
    util.logger.info('===log DEBUG===')
    PyPtt.API(log_level=PyPtt.LOG_LEVEL.DEBUG)
    util.logger.info('===log INFO===')
    PyPtt.API(log_level=PyPtt.LOG_LEVEL.INFO)
    util.logger.info('===log SLIENT===')
    PyPtt.API(log_level=PyPtt.LOG_LEVEL.SILENT)
    util.logger.info('===log SLIENT======')

    ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT1)
    util.logger.info('host', ptt_bot.host)

    ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT2)
    util.logger.info('host', ptt_bot.host)

    try:
        util.logger.info('===語言 99===')
        PyPtt.API(language=99)
    except TypeError:
        util.logger.info('通過')
    except:
        util.logger.info('沒通過')
        assert False
    util.logger.info('===語言放字串===')
    try:
        PyPtt.API(language='PyPtt.i18n.language.ENGLISH')
    except TypeError:
        util.logger.info('通過')
    except:
        util.logger.info('沒通過')
        assert False

    # def handler(msg):
    #     with open('log.txt', 'a', encoding='utf-8') as f:
    #         f.write(msg + '\n')
    #
    #
    # ptt_bot = PyPtt.API(
    #     log_handler=handler)
    # util.logger.info('Test log')

    util.logger.info('complete')


if __name__ == '__main__':
    func()
