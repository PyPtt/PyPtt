import os
import sys
import json
import traceback
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
ptt2_id = None
ptt2_pw = None


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
    global ptt2_id
    global ptt2_pw

    run_ci = False
    travis_ci = False

    if '-ci' in sys.argv:
        run_ci = True

    if run_ci:

        ptt_id = os.getenv('PTT_ID_0')
        ptt_pw = os.getenv('PTT_PW_0')

        ptt2_id = os.getenv('PTT2_ID_0')
        ptt2_pw = os.getenv('PTT2_PW_0')
        if ptt_id is None or ptt_pw is None:
            print('從環境變數取得帳號密碼失敗')
            ptt_id, ptt_pw = get_password('test_account.txt')
            ptt2_id, ptt2_pw = get_password('test_account_2.txt')
            travis_ci = False
        else:
            travis_ci = True
    else:
        ptt_id, ptt_pw = get_password('test_account.txt')
        ptt2_id, ptt2_pw = get_password('test_account_2.txt')


def case(ptt_bot):
    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
        ptt_bot.login(ptt_id, ptt_pw)
    else:
        ptt_bot.login(ptt2_id, ptt2_pw)

    def show_test_result(board, IndexAID, result):
        if result:
            if isinstance(IndexAID, int):
                ptt_bot.log(f'{board} index {IndexAID} 測試通過')
            else:
                ptt_bot.log(f'{board} AID {IndexAID} 測試通過')
        else:
            if isinstance(IndexAID, int):
                ptt_bot.log(f'{board} index {IndexAID} 測試失敗')
            else:
                ptt_bot.log(f'{board} AID {IndexAID} 測試失敗')
                ptt_bot.logout()
                sys.exit(1)

    def get_post_test_func(board, index_aid, target_ex, check_format, check_string):

        ptt_bot.log(f'開始測試 {board} 板 文章{"編號" if isinstance(index_aid, int) else " aid"} {index_aid}')
        try:
            if isinstance(index_aid, int):
                post_info = ptt_bot.get_post(
                    board,
                    post_index=index_aid)
            else:
                post_info = ptt_bot.get_post(
                    board,
                    post_aid=index_aid)
        except Exception as e:
            if target_ex is not None and isinstance(e, target_ex):
                show_test_result(board, index_aid, True)
                return
            show_test_result(board, index_aid, False)

            traceback.ptt_bot.log_tb(e.__traceback__)
            ptt_bot.log(e)
            assert 'test fail'

        if check_string is None and target_ex is None and not check_format:
            ptt_bot.log(post_info.content)

        if check_format and not post_info.pass_format_check:
            show_test_result(board, index_aid, True)
            return

        if check_string is not None and check_string not in post_info.content:
            assert 'check_string not in post_info.content'

        ptt_bot.log(f'{board} 板 文章{"編號" if isinstance(index_aid, int) else " aid"} {index_aid} 測試通過')

    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
        test_post_list = [
            ('Python', 1, None, False, '總算可以來想想板的走向了..XD'),
            ('NotExitBoard', 1, PTT.exceptions.NoSuchBoard, False, None),
            ('Python', '1TJH_XY0', None, False, '大家嗨，我是 CodingMan'),
            # 文章格式錯誤
            ('Steam', 4444, None, True, None),
            # 文章格式錯誤
            ('movie', 457, None, True, None),
            ('Gossiping', '1TU65Wi_', None, False, None),
            ('joke', '1Tc6G9eQ', None, False, None),
            # 待證文章
            ('Test', '1U3pLzi0', None, False, None),
        ]
    else:
        test_post_list = []

    for b, i, exception_, check_format, check_string in test_post_list:
        get_post_test_func(b, i, exception_, check_format, check_string)

    ptt_bot.logout()


def run_on_ptt_1():
    ptt_bot = PTT.API(host=PTT.data_type.host_type.PTT1)
    case(ptt_bot)


def run_on_ptt_2():
    ptt_bot = PTT.API(host=PTT.data_type.host_type.PTT2)
    case(ptt_bot)


def test_PyPtt():
    run_on_ptt_1()
    run_on_ptt_2()


test_init()
test_PyPtt()
