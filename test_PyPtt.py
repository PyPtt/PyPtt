import os
import sys
import json

from PyPtt import PTT


def get_password(password_file):
    try:
        with open(password_file) as AccountFile:
            account = json.load(AccountFile)
            ptt_id = account['ID']
            password = account['Password']
    except FileNotFoundError:
        print(f'Please note PTT ID and Password in {password_file}')
        print('{"ID":"YourID", "Password":"YourPassword"}')
        sys.exit()

    return ptt_id, password


run_ci = None
travis_ci = None
ptt_id = None
ptt_pw = None


def test_init():
    print('===正向===')
    print('===預設值===')
    PTT.API()
    print('===中文顯示===')
    PTT.API(language=PTT.i18n.language.CHINESE)
    print('===英文顯示===')
    PTT.API(language=PTT.i18n.language.ENGLISH)
    print('===log DEBUG===')
    PTT.API(log_level=PTT.log.level.DEBUG)
    print('===log INFO===')
    PTT.API(log_level=PTT.log.level.INFO)
    print('===log SLIENT===')
    PTT.API(log_level=PTT.log.level.SILENT)
    print('===log SLIENT======')

    print('===負向===')
    try:
        print('===語言 99===')
        PTT.API(language=99)
    except ValueError:
        print('通過')
    except:
        print('沒通過')
        sys.exit(-1)
    print('===語言放字串===')
    try:
        PTT.API(language='PTT.i18n.language.ENGLISH')
    except TypeError:
        print('通過')
    except:
        print('沒通過')
        sys.exit(-1)

    def handler(msg):
        with open('log.txt', 'a', encoding='utf-8') as f:
            f.write(msg + '\n')

    ptt_bot = PTT.API(log_handler=handler)
    ptt_bot.log('Test log')

    global run_ci
    global travis_ci
    global ptt_id
    global ptt_pw

    run_ci = False
    travis_ci = False

    if '-ci' in sys.argv:
        run_ci = True

    if run_ci:

        ptt_id = os.getenv('PTT_ID_0')
        ptt_pw = os.getenv('PTT_PW_0')
        if ptt_id is None or ptt_pw is None:
            print('從環境變數取得帳號密碼失敗')
            ptt_id, ptt_pw = get_password('test_account.txt')
            travis_ci = False
        else:
            travis_ci = True
