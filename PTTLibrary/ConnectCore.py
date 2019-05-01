
import time
import telnetlib
# import paramiko
# from paramiko import ECDSAKey

try:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import Exceptions
    # from . import ErrorCode
    from . import Log
except:
    import DataType
    import Config
    import Util
    import i18n
    import Exceptions
    # import ErrorCode
    import Log

# ErrorCode = ErrorCode.ErrorCode()


class ConnectMode(object):

    Telnet = 1
    WebSocket = 2

    MinValue = Telnet
    MaxValue = WebSocket


class ConnectError(Exception):
    def __init__(self):
        self.message = [i18n.Connect, i18n.Fail]

    def __str__(self):

        if Config.Language == i18n.Language.Chinese:
            return ''.join(self.message)
        return ' '.join(self.message)


class API(object):

    def __init__(self, ConnectMode: int):
        # i18n.load(Config.Language)

        self._ConnectMode = ConnectMode

        Log.showValue(Log.Level.INFO, [
            i18n.ConnectCore,
            ],
            i18n.Active
        )

    def connect(self):

        ConnectSuccess = False

        if self._ConnectMode == ConnectMode.Telnet:
            Log.showValue(Log.Level.INFO, [
                    i18n.Connect,
                    i18n.PTT,
                ],
                i18n.ConnectMode_Telnet
            )
        else:
            Log.showValue(Log.Level.INFO, [
                    i18n.Connect,
                    i18n.PTT,
                ],
                i18n.ConnectMode_WebSocket
            )

        for _ in range(2):

            if self._ConnectMode == ConnectMode.Telnet:
                try:
                    self.Connect = telnetlib.Telnet(Config.Host, Config.Port)
                    ConnectSuccess = True
                except:
                    Log.showValue(Log.Level.INFO, [
                        i18n.Connect,
                        i18n.PTT,
                        ],
                        i18n.Fail
                    )
                    self._wait()
                    continue
                break
            elif self._ConnectMode == DataType.ConnectionMode.WebSocket:
                # Do something

                break
        
        if ConnectSuccess:
            Log.showValue(Log.Level.INFO, [
                    i18n.Connect,
                    i18n.PTT,
                ],
                i18n.Done
            )
            # return ErrorCode.Success
        else:
            raise ConnectError()

    def _wait(self):
        for i in range(Config.RetryWaitTime):
            Log.showValue(Log.Level.INFO, [
                    i18n.Prepare,
                    i18n.Again,
                    i18n.Connect,
                    i18n.PTT,
                ],
                str(Config.RetryWaitTime - i)
            )
            time.sleep(1)