
import telnetlib
# import paramiko
# from paramiko import ECDSAKey

try:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import ErrorCode
except:
    import DataType
    import Config
    import Util
    import i18n
    import ErrorCode

ErrorCode = ErrorCode.ErrorCode()


class API(object):

    def __init__(self, ConnectionMode: int):
        i18n.load(Config.Language)

        self.ConnectionMode = ConnectionMode

        Util.showValue([
            i18n.Core,
            i18n.Init,
            ],
            i18n.Done
        )

    def connect(self):

        ConnectSuccess = False

        for i in range(3):

            if self.ConnectionMode == DataType.ConnectionMode.Telnet:
                Util.showValue([
                    i18n.ConnectMode,
                    ],
                    i18n.ConnectMode_Telnet
                )
                try:
                    self.Connect = telnetlib.Telnet(Config.Host, Config.Port)
                    ConnectSuccess = True
                except:
                    Util.showValue([
                        i18n.Connect,
                        i18n.PTT,
                        ],
                        i18n.Fail
                    )

                    for ii in range(Config.RetryWaitTime):
                        time.sleep(1)
                        Util.showValue([
                            i18n.Connect,
                            i18n.PTT,
                            ],
                            str(ii + 1)
                        )
                    continue

                Util.showValue([
                    i18n.ConnectMode,
                    i18n.ConnectMode_Telnet,
                    ],
                    i18n.Active
                )
                break
            elif self.ConnectionMode == DataType.ConnectionMode.WebSocket:
                Util.showValue([
                    i18n.ConnectMode
                    ],
                    i18n.ConnectMode_WebSocket
                )

                # Do something

                Util.showValue([
                    i18n.ConnectMode,
                    i18n.ConnectMode_WebSocket,
                    ],
                    i18n.Active
                )
                break
        
        if ConnectSuccess:
            Util.showValue([
                i18n.Connect,
                i18n.PTT,
                ],
                i18n.Done
            )
            return ErrorCode.Success
        else:
            Util.showValue([
                i18n.Connect,
                i18n.PTT,
                ],
                i18n.Fail
            )
            return ErrorCode.ConnectError
    