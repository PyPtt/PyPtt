import unittest

from SingleLog.log import Logger

import PyPtt
import util
from api import get_time, get_post, get_newest_index
from basic import init


class Init(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        util.logger = Logger('==========Init TEST')

    def test_init(self):
        init.func()

    # def test_loginout(self):
    #     login_logout.func()


class ApiTest:
    ptt_bot = None

    @classmethod
    def tearDownClass(cls):
        cls.ptt_bot.logout()

    def test_get_time(self):
        get_time.test(self.ptt_bot)

    def test_get_post(self):
        get_post.test_no_condition(self.ptt_bot)

    def test_get_post(self):
        get_newest_index.test(self.ptt_bot)


class Ptt1Test(ApiTest, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ptt_bot = PyPtt.API(
            host=PyPtt.HOST.PTT1)

        util.logger = Logger('==========PTT1 TEST')

        util.login(cls.ptt_bot)


class Ptt2Test(ApiTest, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ptt_bot = PyPtt.API(
            host=PyPtt.HOST.PTT2)

        util.logger = Logger('==========PTT2 TEST')

        util.login(cls.ptt_bot)
