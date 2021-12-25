import unittest


class PyPttTestCase(unittest.TestCase):
    def setUp(self):
        # run before every test
        pass

    def tearDown(self):
        # run after every test
        pass

    def test_init(self):
        from basic import init

        init.func()

    def test_loginout(self):
        from basic import login_logout
        login_logout.func()
