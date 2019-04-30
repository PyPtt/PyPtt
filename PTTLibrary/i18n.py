

try:
    from . import DataType
    from . import Config
    from . import Util
    from . import Exceptions
except:
    import DataType
    import Config
    import Util
    import Exceptions

LanguageList = [
    DataType.Language.Chinese,
    DataType.Language.English,
]


def SpecificLoad(Language, LangList):
    global LanguageList

    if len(LanguageList) != len(LangList):
        Util.log('SpecificLoad error')
        Util.log('length error')
        return None
    
    if Language not in LanguageList:
        Util.log('SpecificLoad error')
        Util.showValue('Unknow language', Language)
        return None
    return LangList[LanguageList.index(Language)]


def load(Language):
    if not (DataType.Language.MinValue <=
            Language <= DataType.Language.MaxValue):
        Util.showValue('Error Language valve', Language)
        return ErrorCode.ErrorInput
    
    global Connect
    Connect = SpecificLoad(
        Language, [
            '連線',
            'Connection',
        ])

    global Start
    Start = SpecificLoad(
        Language, [
            '開始',
            'Start',
        ])

    global ConnectMode
    ConnectMode = SpecificLoad(
        Language, [
            Connect + '模式',
            Connect + 'mode',
        ])
    
    global ConnectMode_Telnet
    ConnectMode_Telnet = SpecificLoad(
        Language, [
            'Telnet',
            'Telnet',
        ])
    
    global ConnectMode_WebSocket
    ConnectMode_WebSocket = SpecificLoad(
        Language, [
            'WebSocket',
            'WebSocket',
        ])

    global Active
    Active = SpecificLoad(
        Language, [
            '啟動',
            'Active',
        ])
    
    global ErrorParameter
    ErrorParameter = SpecificLoad(
        Language, [
            '參數錯誤',
            'Wrong parameter',
        ])
    
    global Core
    Core = SpecificLoad(
        Language, [
            '核心',
            'Core',
        ])
    
    global PTT
    PTT = SpecificLoad(
        Language, [
            '批踢踢',
            'PTT',
        ])
    
    global Init
    Init = SpecificLoad(
        Language, [
            '初始化',
            'Initialization',
        ])

    global Done
    Done = SpecificLoad(
        Language, [
            '完成',
            'Done',
        ])

    global i18n
    i18n = SpecificLoad(
        Language, [
            '多國語系',
            'i18n',
        ])
    
    global Library
    Library = SpecificLoad(
        Language, [
            '函式庫',
            'Library',
        ])
    
    global Fail
    Fail = SpecificLoad(
        Language, [
            '失敗',
            'Fail',
        ])

    # Final check
    for k, v in globals().items():
        # System Var
        if k.startswith('__'):
            continue
        # print(k)
        # print(v)
        if v is None:
            raise Exceptions.InitError(
                Util.getFileName(__file__), k + ' is None')


def _createlist():

    i18nStrList = []

    for k, v in globals().items():
        # System Var
        if k.startswith('_'):
            continue
        if isinstance(k, str) and isinstance(v, str):
            i18nStrList.append(k)

    with open('i18n.txt', 'w') as F:
        F.write('\n'.join(i18nStrList))

if __name__ == '__main__':
    load(Config.Language)
    _createlist()
