import PyPtt
from tests import util


def test():
    util.logger.info('===預設值===')
    PyPtt.API()
    util.logger.info('===中文顯示===')
    PyPtt.API(language=PyPtt.Language.MANDARIN)
    util.logger.info('===英文顯示===')
    PyPtt.API(language=PyPtt.Language.ENGLISH)
    util.logger.info('===log DEBUG===')
    PyPtt.API(log_level=PyPtt.LOG_LEVEL.DEBUG)
    util.logger.info('===log INFO===')
    PyPtt.API(log_level=PyPtt.LOG_LEVEL.INFO)

    util.logger.info('===set host with PTT===')
    ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT1)
    util.logger.info('host result', ptt_bot.host)

    util.logger.info('===set host with PTT2===')
    ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT2)
    util.logger.info('host result', ptt_bot.host)

    util.logger.info('===set host with PTT and TELNET ===')
    try:
        PyPtt.API(host=PyPtt.HOST.PTT1, connect_mode=PyPtt.ConnectMode.TELNET)
        assert False
    except ValueError:
        util.logger.info('通過')

    util.logger.info('===set host with PTT2 and TELNET ===')
    try:
        PyPtt.API(host=PyPtt.HOST.PTT2, connect_mode=PyPtt.ConnectMode.TELNET)
        assert False
    except ValueError:
        util.logger.info('通過')

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

    util.logger.info('complete')


if __name__ == '__main__':
    test()