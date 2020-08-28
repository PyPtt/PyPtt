import os


def test_hello():
    test_secret = os.getenv('TEST_SECRET')
    print(test_secret)
    print('Hello success')


test_hello()
