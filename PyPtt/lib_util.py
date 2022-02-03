import os
import random
import string
import traceback
from enum import Enum


def check_range(define_obj, value):
    if value < define_obj.min_value or define_obj.max_value < value:
        return False
    return True


def get_file_name(string):
    result = os.path.basename(string)
    result = result[:result.find('.')]
    return result


def get_current_func_name():
    return traceback.extract_stack(None, 2)[0][2]


def findnth(haystack, needle, n):
    parts = haystack.split(needle, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(haystack) - len(parts[-1]) - len(needle)


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


def get_random_str(length):
    return ''.join(random.choices(string.hexdigits, k=length))


if __name__ == '__main__':
    for _ in range(5):
        print(get_random_str(10))