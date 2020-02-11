import re
try:
    from . import i18n
    from . import connect_core
    from . import screens
    from . import command
except ModuleNotFoundError:
    import i18n
    import connect_core
    import screens
    import command


def get_time(api) -> str:

    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append('A')
    cmd_list.append(command.Right)
    cmd_list.append(command.Left)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            [
                i18n.GetPTTTime,
                i18n.Success,
            ],
            screens.Target.MainMenu,
            break_detect=True
        ),
    ]

    index = api.connect_core.send(cmd, target_list)
    if index != 0:
        return None

    ori_screen = api.connect_core.get_screen_queue()[-1]
    line_list = ori_screen.split('\n')
    pattern = re.compile('[\d]+:[\d][\d]')

    line_list = line_list[-3:]

    # 0:00

    for line in line_list:
        if '星期' in line and '線上' in line and '我是' in line:
            result = pattern.search(line)
            if result is not None:
                return result.group(0)
    return None
