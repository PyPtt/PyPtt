import sys


def test_hello():
    for arg in sys.argv:
        print(arg)
    print('Hello success')
