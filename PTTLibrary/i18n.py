

try:
    from . import DataType
    from . import Util
    from . import Exceptions
    from . import Log
except:
    import DataType
    import Util
    import Exceptions
    import Log


class Language(object):

    Chinese = 1
    English = 2

    MinValue = Chinese
    MaxValue = English


LanguageList = [
    Language.Chinese,
    Language.English,
]


def SpecificLoad(inputLanguage, LangList):
    global LanguageList

    if len(LanguageList) != len(LangList):
        Log.log(Log.Level.INFO, 'SpecificLoad error')
        Log.log(Log.Level.INFO, 'length error')
        return None
    
    if inputLanguage not in LanguageList:
        Log.log(Log.Level.INFO, 'SpecificLoad error')
        Log.showValue(Log.Level.INFO, 'Unknow language', inputLanguage)
        return None
    return LangList[LanguageList.index(inputLanguage)]


def load(inputLanguage):
    if not Util.checkRange(Language, inputLanguage):
        Log.showValue(Log.Level.INFO, 'Error Language valve', inputLanguage)
        raise Exceptions.ParameterError('Language', inputLanguage)
    
    global Connect
    Connect = SpecificLoad(
        inputLanguage, [
            '連線',
            'Connect',
        ])

    global Start
    Start = SpecificLoad(
        inputLanguage, [
            '開始',
            'Start',
        ])

    global ConnectMode
    ConnectMode = SpecificLoad(
        inputLanguage, [
            Connect + '模式',
            Connect + 'mode',
        ])
    
    global ConnectMode_Telnet
    ConnectMode_Telnet = SpecificLoad(
        inputLanguage, [
            'Telnet',
            'Telnet',
        ])
    
    global ConnectMode_WebSocket
    ConnectMode_WebSocket = SpecificLoad(
        inputLanguage, [
            'WebSocket',
            'WebSocket',
        ])

    global Active
    Active = SpecificLoad(
        inputLanguage, [
            '啟動',
            'Active',
        ])
    
    global ErrorParameter
    ErrorParameter = SpecificLoad(
        inputLanguage, [
            '參數錯誤',
            'Wrong parameter',
        ])
    
    global ConnectCore
    ConnectCore = SpecificLoad(
        inputLanguage, [
            '連線核心',
            'Connect Core',
        ])
    
    global PTT
    PTT = SpecificLoad(
        inputLanguage, [
            '批踢踢',
            'PTT',
        ])
    
    global Init
    Init = SpecificLoad(
        inputLanguage, [
            '初始化',
            'Initialization',
        ])

    global Done
    Done = SpecificLoad(
        inputLanguage, [
            '完成',
            'Done',
        ])

    global i18n
    i18n = SpecificLoad(
        inputLanguage, [
            '多國語系',
            'i18n',
        ])
    
    global Library
    Library = SpecificLoad(
        inputLanguage, [
            '函式庫',
            'Library',
        ])
    
    global Fail
    Fail = SpecificLoad(
        inputLanguage, [
            '失敗',
            'Fail',
        ])
    
    global Prepare
    Prepare = SpecificLoad(
        inputLanguage, [
            '準備',
            'Prepare',
        ])
    
    global Info
    Info = SpecificLoad(
        inputLanguage, [
            '資訊',
            'INFO',
        ])
    
    global Debug
    Debug = SpecificLoad(
        inputLanguage, [
            '除錯',
            'DBUG',
        ])
    
    global Again
    Again = SpecificLoad(
        inputLanguage, [
            '重新',
            'Re',
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
    
    Log.showValue(Log.Level.INFO, [
            i18n,
        ],
        Active
    )


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
    # load(Config.Language)
    _createlist()
