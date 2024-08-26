import os
import random

from . import __version__
from . import data_type

locale_pool = {
    data_type.Language.ENGLISH,
    data_type.Language.MANDARIN
}

_script_path = os.path.dirname(__file__)
_lang_data = {}

mapping = {
    '{version}': __version__,
}


def replace(string, *args):
    for i in range(len(args)):
        target = f'{args[i]}'
        string = string.replace(f'_target{i}_', target)
    return string


def init(locale: str, cache: bool = False) -> None:
    if locale not in locale_pool:
        raise ValueError(f'Unknown locale: {locale}')

    if locale == data_type.Language.ENGLISH:
        from . import lang_en_US as lang
    elif locale == data_type.Language.MANDARIN:
        from . import lang_zh_TW as lang
    string_data = lang.string_data

    if string_data is None:
        raise ValueError(f'Unknown locale: {locale}')

    for k, v in string_data.items():

        if isinstance(v, list):
            v = random.choice(v)
        elif isinstance(v, str):
            pass
        else:
            raise ValueError(f'Unknown string data type: {v}')

        if locale == data_type.Language.ENGLISH:
            v = v[0].upper() + v[1:]

        for mk, mv in mapping.items():
            v = v.replace(mk, mv)

        globals()[k] = v
        if cache:
            global _lang_data
            _lang_data[k] = v

