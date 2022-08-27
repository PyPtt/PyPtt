from SingleLog.log import Logger

from . import i18n

logger = Logger('check value')


def check_type(value_type, name, value) -> None:
    if not isinstance(value, value_type):
        if value_type is str:
            raise TypeError(f'{name} {i18n.must_be_a_string}, but got {value}')
        elif value_type is int:
            raise TypeError(f'{name} {i18n.must_be_a_integer}, but got {value}')
        elif value_type is bool:
            raise TypeError(f'{name} {i18n.must_be_a_boolean}, but got {value}')
        else:
            raise TypeError(f'{name} {i18n.must_be} {value_type}, but got {value}')


def check_range(name, value, min_value, max_value) -> None:
    check_type(int, name, value)
    check_type(int, 'min_value', min_value)
    check_type(int, 'max_value', max_value)

    if min_value <= value <= max_value:
        return
    raise ValueError(f'{name} {value} {i18n.must_between} {min_value} ~ {max_value}')


def check_index(name, index, max_value=None) -> None:
    check_type(int, name, index)
    if index < 1:
        raise ValueError(f'{name} {i18n.must_bigger_than} 0')

    if max_value is not None:
        if index > max_value:
            logger.info('index', index)
            logger.info('max_value', max_value)
            raise ValueError(f'{name} {index} {i18n.must_between} 0 ~ {max_value}')


def check_index_range(
        start_name,
        start_index,
        end_name,
        end_index,
        max_value=None) -> None:
    check_type(int, start_name, start_index)
    check_type(int, end_name, end_index)

    if start_index < 1:
        raise ValueError(f'{start_name} {start_index} {i18n.must_bigger_than} 0')

    if end_index <= 1:
        raise ValueError(f'{end_name} {end_index} {i18n.must_bigger_than} 1')

    if start_index > end_index:
        raise ValueError(f'{end_name} {end_index} {i18n.must_bigger_than} {start_name} {start_index}')

    if max_value is not None:
        if start_index > max_value:
            raise ValueError(f'{start_name} {start_index} {i18n.must_small_than} {max_value}')

        if end_index > max_value:
            raise ValueError(f'{end_name} {end_index} {i18n.must_small_than} {max_value}')


if __name__ == '__main__':
    QQ = str

    if QQ is str:
        print('1')

    if QQ == str:
        print('2')

    if isinstance('', QQ):
        print('3')
