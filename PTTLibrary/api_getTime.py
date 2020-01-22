import re
import time
try:
    from . import DataType
    from . import Util
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Screens
    from . import Exceptions
    from . import Command
    from . import CheckValue
except ModuleNotFoundError:
    import DataType
    import Util
    import i18n
    import ConnectCore
    import Log
    import Screens
    import Exceptions
    import Command
    import CheckValue


def getTime(api):

    CmdList = []
    CmdList.append(Command.GoMainMenu)
    CmdList.append('A')
    CmdList.append(Command.Right)
    CmdList.append(Command.Left)

    Cmd = ''.join(CmdList)

    TargetList = [
        ConnectCore.TargetUnit(
            [
                i18n.GetPTTTime,
                i18n.Success,
            ],
            Screens.Target.MainMenu,
            BreakDetect=True
        ),
    ]

    index = api._ConnectCore.send(Cmd, TargetList)
    if index != 0:
        return None

    OriScreen = api._ConnectCore.getScreenQueue()[-1]
    LineList = OriScreen.split('\n')
    pattern = re.compile('[\d]+:[\d][\d]')

    LineList = LineList[-3:]

    # 0:00

    for line in LineList:
        if '星期' in line and '線上' in line and '我是' in line:
            Result = pattern.search(line)
            if Result is not None:
                return Result.group(0)
    return None
