import os
import sys

sys.path.append(os.getcwd())

import PyPtt


def test():
    print('=== default ===')
    PyPtt.API()
    print('=== 中文顯示 ===')
    PyPtt.API(language=PyPtt.Language.MANDARIN)
    print('=== 英文顯示 ===')
    PyPtt.API(language=PyPtt.Language.ENGLISH)
    print('=== log DEBUG ===')
    PyPtt.API(log_level=PyPtt.LogLevel.DEBUG)
    print('=== log INFO ===')
    PyPtt.API(log_level=PyPtt.LogLevel.INFO)
    print('=== log SILENT===')
    PyPtt.API(log_level=PyPtt.LogLevel.SILENT)

    print('=== set host with PTT ===')
    ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT1)
    print(f'host result {ptt_bot.host}')

    print('=== set host with PTT2 ===')
    ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT2)
    print(f'host result {ptt_bot.host}')

    print('=== set host with PTT and TELNET ===')
    try:
        PyPtt.API(host=PyPtt.HOST.PTT1, connect_mode=PyPtt.ConnectMode.TELNET)
        assert False
    except PyPtt.ParameterError:
        print('通過')

    print('=== set host with PTT2 and TELNET ===')
    try:
        PyPtt.API(host=PyPtt.HOST.PTT2, connect_mode=PyPtt.ConnectMode.TELNET)
        assert False
    except PyPtt.ParameterError:
        print('通過')

    try:
        print('=== 語言 99 ===')
        PyPtt.API(language=99)
    except TypeError:
        print('通過')
    except Exception:
        print('沒通過')
        assert False
    print('=== 語言放字串 ===')
    try:
        PyPtt.API(language='PyPtt.i18n.language.ENGLISH')
    except TypeError:
        print('通過')
    except Exception:
        print('沒通過')
        assert False

    print('complete')


if __name__ == '__main__':
    test()
    # PyPtt.API()
