from SingleLog.log import Logger

try:
    from . import i18n
    from . import log
    from . import lib_util
except ModuleNotFoundError:
    import i18n
    import log
    import lib_util

logger = Logger('check value', Logger.INFO)


def check(
        config,
        value_type,
        name,
        value,
        value_class=None) -> None:
    if not isinstance(value, value_type):
        if value_type is str:
            raise TypeError(f'{name} {i18n.must_be_a_string}')
        elif value_type is int:
            raise TypeError(f'{name} {i18n.must_be_a_integer}')
        elif value_type is bool:
            raise TypeError(f'{name} {i18n.must_be_a_boolean}')

    if value_class is not None:
        if not lib_util.check_range(value_class, value):
            raise ValueError(f'Unknown {name}', value)


def check_index(
        config,
        name,
        index,
        max_value=None) -> None:
    check(config, int, name, index)
    if index < 1:
        raise ValueError(f'{name} {i18n.must_bigger_than} 0')

    if max_value is not None:
        if index > max_value:
            logger.info('index', index)
            logger.info('max_value', max_value)
            raise ValueError(f'{name} {index} {i18n.must_between} 0 ~ {max_value}')


def check_index_range(
        config,
        start_name,
        start_index,
        end_name,
        end_index,
        max_value=None) -> None:
    check(config, int, start_name, start_index)
    check(config, int, end_name, end_index)

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
