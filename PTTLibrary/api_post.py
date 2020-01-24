try:
    from . import i18n
    from . import ConnectCore
    from . import Screens
    from . import Exceptions
    from . import Command
except ModuleNotFoundError:
    import i18n
    import ConnectCore
    import Screens
    import Exceptions
    import Command


def post(
        api,
        Board,
        Title,
        Content,
        PostType,
        SignFile):

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('qs')
    CmdList.append(Board)
    CmdList.append(Command.Enter)
    CmdList.append(Command.Ctrl_C * 2)
    CmdList.append(Command.Space)
    CmdList.append(Command.Ctrl_P)

    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.HasPostPermission,
            '發表文章於【',
            BreakDetect=True,
        ),
        ConnectCore.TargetUnit(
            i18n.NoPermission,
            '使用者不可發言',
            BreakDetect=True,
        )
    ]
    index = api._ConnectCore.send(Cmd, TargetList)
    if index < 0:
        Screens.show(api.Config, api._ConnectCore.getScreenQueue())
        raise Exceptions.UnknowError(i18n.UnknowError)
    if index == 1:
        raise Exceptions.NoPermission(i18n.NoPermission)

    Screens.show(api.Config, api._ConnectCore.getScreenQueue())

    CmdList = []
    CmdList.append(str(PostType))
    CmdList.append(Command.Enter)
    CmdList.append(str(Title))
    CmdList.append(Command.Enter)
    CmdList.append(Command.Ctrl_Y * 30)
    CmdList.append(str(Content))
    CmdList.append(Command.Ctrl_X)
    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵繼續',
            BreakDetect=True,
        ),
        ConnectCore.TargetUnit(
            i18n.SaveFile,
            '確定要儲存檔案嗎',
            Response='s' + Command.Enter,
        ),
        ConnectCore.TargetUnit(
            i18n.SelectSignature,
            'x=隨機',
            Response=str(SignFile) + Command.Enter,
        ),
    ]
    index = api._ConnectCore.send(
        Cmd,
        TargetList,
        ScreenTimeout=api.Config.ScreenPostTimeOut
    )
