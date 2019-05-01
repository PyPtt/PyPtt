try:
    from . import DataType
    from . import Log
    from . import i18n
    from . import ConnectCore
except:
    import DataType
    import Log
    import i18n
    import ConnectCore

Version = '0.8.0 beta'
Host = 'ptt.cc'
Port = '23'

RetryWaitTime = 3

Language = i18n.Language.Chinese
ConnectMode = ConnectCore.ConnectMode.Telnet
LogLevel = Log.Level.INFO
