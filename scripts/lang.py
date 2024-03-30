import json
import os
import sys
from collections import defaultdict

import yaml

sys.path.append(os.getcwd())

import PyPtt


def add_lang():
    new_words = [
        (PyPtt.Language.MANDARIN, 'get_board_info', '取得看板資訊 _target0_'),
        (PyPtt.Language.ENGLISH, 'get_board_info', 'get board info _target0_'),
    ]

    for lang, key, value in new_words:
        PyPtt.i18n.init(lang, cache=True)

        PyPtt.i18n._lang_data[key] = value

        with open(f'PyPtt/lang/{lang}.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(PyPtt.i18n._lang_data, f, allow_unicode=True, default_flow_style=False)


def check_lang():
    import re

    # 搜尋 PyPtt 資料夾底下，所有用到 i18n 的字串

    PyPtt.i18n.init(PyPtt.Language.MANDARIN, cache=True)

    # init count dict
    count_dict = {}
    for key, value in PyPtt.i18n._lang_data.items():
        print('->', key, value)
        count_dict[key] = 0

    # 1. 用 os.walk() 搜尋所有檔案
    for dirpath, dirnames, filenames in os.walk('./PyPtt'):
        print(f'================= directory: {dirpath}')
        for file_name in filenames:

            if not file_name.endswith('.py'):
                continue

            if file_name == 'i18n.py':
                continue

            print(file_name)

            with open(f'{dirpath}/{file_name}', 'r', encoding='utf-8') as f:
                data = f.read()

            for match in re.finditer(r'i18n\.(\w+)', data):
                # print(match.group(0))
                # print(match.group(1))

                data_key = match.group(1)

                if data_key not in count_dict:
                    print(f'Unknown key: {data_key}')
                else:
                    count_dict[data_key] += 1
                print('-----------------')

    print(json.dumps(count_dict, indent=4, ensure_ascii=False))

    # collect the keys with 0 count
    zero_count_keys = [key for key, value in count_dict.items() if value == 0]

    for lang in PyPtt.i18n.locale_pool:
        PyPtt.i18n.init(lang, cache=True)
        for key in zero_count_keys:
            # remove the key from the lang data
            PyPtt.i18n._lang_data.pop(key, None)
            print(f'Removed key: {key} from {lang}.yaml')

        with open(f'PyPtt/lang/{lang}.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(PyPtt.i18n._lang_data, f, allow_unicode=True, default_flow_style=False)

if __name__ == '__main__':
    add_lang()
    # check_lang()
    pass

