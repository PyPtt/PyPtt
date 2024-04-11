import re

from . import _api_util
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import log
from . import screens

pattern = re.compile(r'[\d]+:[\d][\d]')


def get_time(api) -> str:
    _api_util.one_thread(api)
    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append('A')
    cmd_list.append(command.right)
    cmd_list.append(command.left)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(screens.Target.MainMenu, log_level=log.DEBUG, break_detect=True),
    ]

    index = api.connect_core.send(cmd, target_list)
    if index != 0:
        return None

    ori_screen = api.connect_core.get_screen_queue()[-1]
    line_list = ori_screen.split('\n')[-3:]

    # 0:00

    for line in line_list:
        if '星期' in line and '線上' in line and '我是' in line:
            result = pattern.search(line)
            if result is not None:
                return result.group(0)
    return None
