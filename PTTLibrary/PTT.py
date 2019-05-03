import sys
import time

try:
    import DataType
    import Config
    import Util
    import i18n
    import Exceptions
    import ConnectCore
    import ErrorCode
    import Log
    import Synchronize
except ModuleNotFoundError:
    from . import DataType
    from . import Config
    from . import Util
    from . import i18n
    from . import Exceptions
    from . import ConnectCore
    from . import ErrorCode
    from . import Log
    from . import Synchronize

Version = Config.Version

ErrorCode = ErrorCode.ErrorCode()
Language = i18n.Language
ConnectMode = ConnectCore.ConnectMode
LogLevel = Log.Level
Command = ConnectCore.Command
Exceptions = Exceptions


class Library(Synchronize.SynchronizeAllMethod):
    def __init__(self,
                 Language: int=0,
                 ConnectMode: int=0,
                 LogLevel: int=0,
                 ):
        Config.load()

        if LogLevel == 0:
            LogLevel = Config.LogLevel
        elif not Util.checkRange(Log.Level, LogLevel):
            raise Exceptions.ParameterError('Unknow LogLevel', LogLevel)
        else:
            Config.LogLevel = LogLevel

        if Language == 0:
            Language = Config.Language
        elif not Util.checkRange(i18n.Language, Language):
            raise Exceptions.ParameterError('Unknow language', Language)
        else:
            Config.Language = Language
        i18n.load(Language)

        if ConnectMode == 0:
            ConnectMode = Config.ConnectMode
        elif not Util.checkRange(ConnectCore.ConnectMode, ConnectMode):
            raise Exceptions.ParameterError('Unknow ConnectMode',
                                            ConnectMode)
        else:
            Config.ConnectMode = ConnectMode
        self._ConnectCore = ConnectCore.API(ConnectMode)

        Log.showValue(Log.Level.INFO, [
            i18n.PTT,
            i18n.Library,
            ' v ' + Version,
            ],
            i18n.Init
        )

    def login(self, ID: str, Password: str, KickOtherLogin: bool=False):

        def KickOtherLoginDisplayMsg():
            if Config.KickOtherLogin:
                return i18n.KickOtherLogin
            return i18n.NotKickOtherLogin

        def KickOtherLoginResponse(Screen):
            if Config.KickOtherLogin:
                return 'y' + ConnectCore.Command.Enter
            return 'n' + ConnectCore.Command.Enter

        if len(Password) > 8:
            Password = Password[:8]

        ID = ID.strip()
        Password = Password.strip()

        Config.KickOtherLogin = KickOtherLogin

        self._ConnectCore.connect()

        TargetList = [
            ConnectCore.TargetUnit(
                i18n.LoginSuccess,
                '我是' + ID,
                BreakDetect=True
            ),
            ConnectCore.TargetUnit(
                i18n.ErrorIDPW,
                '密碼不對或無此帳號',
                BreakDetect=True
            ),
            ConnectCore.TargetUnit(
                i18n.SystemBusyTryLater,
                '系統負荷過重, 請稍後再試',
                BreakDetect=True,
            ),
            ConnectCore.TargetUnit(
                i18n.SystemBusyTryLater,
                '系統過載',
                BreakDetect=True,
            ),
            ConnectCore.TargetUnit(
                i18n.DelWrongPWRecord,
                '您要刪除以上錯誤嘗試的記錄嗎',
                Response='y' + ConnectCore.Command.Enter,
            ),
            ConnectCore.TargetUnit(
                i18n.MailBoxFull,
                '您保存信件數目',
                Response=ConnectCore.Command.GoMainMenu,
            ),
            ConnectCore.TargetUnit(
                i18n.PostNotFinish,
                '有一篇文章尚未完成',
                Response='q' + ConnectCore.Command.Enter,
            ),
            ConnectCore.TargetUnit(
                i18n.SigningUnPleaseWait,
                '登入中，請稍候',
            ),
            ConnectCore.TargetUnit(
                KickOtherLoginDisplayMsg,
                '您想刪除其他重複登入的連線嗎',
                Response=KickOtherLoginResponse,
            ),
            ConnectCore.TargetUnit(
                i18n.AnyKeyContinue,
                '任意鍵',
                Response=' '
            ),
            ConnectCore.TargetUnit(
                i18n.SigningUpdate,
                '正在更新與同步線上使用者及好友名單',
            ),
        ]

        CmdList = []
        CmdList.append(ID)
        CmdList.append(',')
        CmdList.append(ConnectCore.Command.Enter)
        CmdList.append(Password)
        CmdList.append(ConnectCore.Command.Enter)

        Cmd = ''.join(CmdList)

        index = self._ConnectCore.send(Cmd, TargetList)
        # Log.showValue(Log.Level.INFO, 'index', index)

        if index != 0:
            raise ConnectCore.LoginError()
        return ErrorCode.Success

    def logout(self):

        CmdList = []
        CmdList.append(ConnectCore.Command.GoMainMenu)
        CmdList.append('g')
        CmdList.append(ConnectCore.Command.Enter)
        CmdList.append('y')
        CmdList.append(ConnectCore.Command.Enter)

        Cmd = ''.join(CmdList)

        TargetList = [
            ConnectCore.TargetUnit(
                [
                    i18n.Logout,
                    i18n.Success,
                ],
                '任意鍵',
                BreakDetect=True
            ),
        ]

        index = self._ConnectCore.send(Cmd, TargetList)
        self._ConnectCore.close()
        if index != 0:
            raise ConnectCore.LoginError()
        return ErrorCode.Success

    def log(self, Msg):
        Log.log(Log.Level.INFO, Msg)

if __name__ == '__main__':

    print('PTT Library v ' + Version)
    print('Developed by PTT CodingMan')
