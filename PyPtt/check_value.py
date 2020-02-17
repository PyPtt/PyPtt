try:
    from . import i18n
    from . import log
    from . import lib_util
except ModuleNotFoundError:
    import i18n
    import log
    import lib_util


def check(
        config,
        value_type,
        name,
        value,
        value_class=None) ->None:
    if not isinstance(value, value_type):
        if value_type is str:
            raise TypeError(
                log.merge(
                    config,
                    [
                        name,
                        str(value),
                        i18n.MustBe,
                        i18n.String
                    ]))
        elif value_type is int:
            raise TypeError(
                log.merge(
                    config,
                    [
                        name,
                        str(value),
                        i18n.MustBe,
                        i18n.Integer
                    ]))
        elif value_type is bool:
            raise TypeError(
                log.merge(
                    config,
                    [
                        name,
                        str(value),
                        i18n.MustBe,
                        i18n.Boolean
                    ]))

    if value_class is not None:
        if not lib_util.check_range(value_class, value):
            raise ValueError(f'Unknown {name}', value)


def check_index(
        config,
        index_name,
        index,
        max_value=None) -> None:
    check(config, int, index_name, index)
    if index < 1:
        raise ValueError(
            log.merge(
                config,
                [
                    index_name,
                    str(index),
                    i18n.ErrorParameter,
                    i18n.OutOfRange,
                ]))

    if max_value is not None:
        if index > max_value:
            log.show_value(
                config,
                log.level.INFO,
                'Index',
                index
            )
            log.show_value(
                config,
                log.level.INFO,
                'max_value',
                max_value
            )
            raise ValueError(
                log.merge(
                    config,
                    [
                        index_name,
                        str(index),
                        i18n.ErrorParameter,
                        i18n.OutOfRange,
                    ]))


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
        raise ValueError(
            log.merge(
                config,
                [
                    start_name,
                    str(start_name),
                    i18n.ErrorParameter,
                    i18n.OutOfRange,
                ]))

    if end_index < 1:
        raise ValueError(
            log.merge(
                config,
                [
                    end_name,
                    str(end_index),
                    i18n.ErrorParameter,
                    i18n.OutOfRange,
                ]))

    if start_index > end_index:
        raise ValueError(
            log.merge(
                config,
                [
                    start_name,
                    str(start_index),
                    i18n.MustSmallOrEqual,
                    end_name,
                    str(end_index),
                ]))

    if max_value is not None:
        if start_index > max_value:
            raise ValueError(
                log.merge(
                    config,
                    [
                        start_name,
                        str(start_index),
                        i18n.ErrorParameter,
                        i18n.OutOfRange,
                        str(max_value),
                    ]))

        if end_index > max_value:
            raise ValueError(
                log.merge(
                    config,
                    [
                        end_name,
                        i18n.ErrorParameter,
                        i18n.OutOfRange,
                        str(max_value),
                    ]))


if __name__ == '__main__':
    QQ = str

    if QQ is str:
        print('1')

    if QQ == str:
        print('2')

    if isinstance('', QQ):
        print('3')
