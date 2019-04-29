

try:
    from . import Util
    from . import DataType
    from . import ErrorCode
except:
    import Util
    import DataType
    import ErrorCode

ErrorCode = ErrorCode.ErrorCode()

ConnectMode = None


def load(Language):
    if not (DataType.Language.MinValue <=
            Language <= DataType.Language.MaxValue):
        Util.showValue('Error Langauge valve', Language)
        return ErrorCode.ErrorInput

    global ConnectMode
    if Language == DataType.Language.Chinese:
        ConnectMode = '連線模式'
    elif Language == DataType.Language.English:
        ConnectMode = 'Connect mode'

    return ErrorCode.Success

