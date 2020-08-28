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


def test_hello():
    test_secret = os.getenv('TEST_SECRET')
    print(test_secret)
    print('Hello success')
    # assert (1 == 2)


class TestCase:
    # def __init__(self):
    #     print('Welcome to PyPtt v ' + PTT.version.V + ' test case')
    #
    #     self.run_ci = False
    #     self.travis_ci = False
    #
    #     if '-ci' in sys.argv:
    #         self.run_ci = True
    #
    #     if self.run_ci:
    #
    #         self.ptt_id = os.getenv('PTT_ID_0')
    #         self.password = os.getenv('PTT_PW_0')
    #         if self.ptt_id is None or self.password is None:
    #             print('從環境變數取得帳號密碼失敗')
    #             self.ptt_id, self.password = get_password('test_account.txt')
    #             self.travis_ci = False
    #         else:
    #             self.travis_ci = True
    #
    #     assert (1 == 2)

    def test_init(self):
        assert (3 == 2)
