try:
    from . import i18n
    from . import Log
    from . import Util
except ModuleNotFoundError:
    import i18n
    import Log
    import Util


def check(
        config,
        value_type,
        name,
        value,
        value_class=None) ->None:
    if not isinstance(value, value_type):
        if value_type is str:
            raise TypeError(
                Log.merge(
                    config,
                    [
                        name,
                        i18n.MustBe,
                        i18n.String
                    ]))
        elif value_type is int:
            raise TypeError(
                Log.merge(
                    config,
                    [
                        name,
                        i18n.MustBe,
                        i18n.Integer
                    ]))
        elif value_type is bool:
            raise TypeError(
                Log.merge(
                    config,
                    [
                        name,
                        i18n.MustBe,
                        i18n.Boolean
                    ]))

    if value_class is not None:
        if not Util.check_range(value_class, value):
            raise ValueError(f'Unknown {name}', value)


def check_index(
        config,
        index_name,
        index,
        max_value=None):
    check(config, int, index_name, index)
    if index < 1:
        raise ValueError(
            Log.merge(
                config,
                [
                    index_name,
                    i18n.ErrorParameter,
                    i18n.OutOfRange,
                ]))

    if max_value is not None:
        if index > max_value:
            Log.show_value(
                config,
                Log.Level.INFO,
                'Index',
                index
            )
            Log.show_value(
                config,
                Log.Level.INFO,
                'MaxValue',
                max_value
            )
            raise ValueError(
                Log.merge(
                    config,
                    [
                        index_name,
                        i18n.ErrorParameter,
                        i18n.OutOfRange,
                    ]))


def check_index_range(
        config,
        start_name,
        start_index,
        end_name,
        end_index,
        max_value=None
):
    check(config, int, start_name, start_index)
    check(config, int, end_name, end_index)

    if start_index < 1:
        raise ValueError(
            Log.merge(
                config,
                [
                    start_name,
                    i18n.ErrorParameter,
                    i18n.OutOfRange,
                ]))

    if start_index < 1:
        raise ValueError(
            Log.merge(
                config,
                [
                    start_name,
                    i18n.ErrorParameter,
                    i18n.OutOfRange,
                ]))

    if start_index > end_index:
        raise ValueError(
            Log.merge(
                config,
                [
                    start_name,
                    i18n.MustSmallOrEqual,
                    end_name,
                ]))

    if max_value is not None:
        if start_index > max_value:
            raise ValueError(
                Log.merge(
                    config,
                    [
                        start_name,
                        i18n.ErrorParameter,
                        i18n.OutOfRange,
                    ]))

        if end_index > max_value:
            raise ValueError(
                Log.merge(
                    config,
                    [
                        end_name,
                        i18n.ErrorParameter,
                        i18n.OutOfRange,
                    ]))


if __name__ == '__main__':
    QQ = str

    if QQ is str:
        print('1')

    if QQ == str:
        print('2')

    if isinstance('', QQ):
        print('3')
