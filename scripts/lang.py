import os
import sys

import yaml

sys.path.append(os.getcwd())

import PyPtt


def add_lang():
    new_words = [
        (PyPtt.Language.MANDARIN, 'english_module', '英文'),
        (PyPtt.Language.ENGLISH, 'english_module', 'english'),
    ]

    for lang, key, value in new_words:
        PyPtt.i18n.init(lang)

        PyPtt.i18n._lang_data[key] = value

        with open(f'PyPtt/lang/{lang}.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(PyPtt.i18n._lang_data, f, allow_unicode=True, default_flow_style=False)


def check_lang():
    PyPtt.i18n.init(PyPtt.Language.MANDARIN)
    print(PyPtt.i18n.goodbye)


if __name__ == '__main__':
    # add_lang()
    check_lang()
