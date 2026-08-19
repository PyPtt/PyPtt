import re

from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import log
from . import screens


# 狀態列有 '[呼叫器]打開' 與 '呼叫器關閉' 兩種寫法, 中括號不保證存在。
_call_status_pattern = re.compile(r'呼叫器[\]\s]*(打開|拔掉|防水|好友|關閉)')

_call_status_map = {
    '打開': data_type.CallStatus.ON,
    '拔掉': data_type.CallStatus.UNPLUG,
    '防水': data_type.CallStatus.WATERPROOF,
    '好友': data_type.CallStatus.FRIEND,
    '關閉': data_type.CallStatus.OFF,
}


def get_call_status(api) -> data_type.CallStatus:

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append('A')
    cmd_list.append(command.right)
    cmd_list.append(command.left)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(screens.Target.MainMenu, log_level=log.DEBUG, break_detect=True),
        connect_core.TargetUnit('★', log_level=log.DEBUG, response=cmd),
    ]

    for _ in range(2):
        if api.connect_core.send(cmd, target_list) == 0:
            break
    else:
        raise exceptions.UnknownError('UnknownError')

    ori_screen = api.connect_core.get_screen_queue()[-1]
    result = _call_status_pattern.search(ori_screen)
    if result is None:
        raise exceptions.UnknownError(ori_screen)
    return _call_status_map[result.group(1)]


def set_call_status(api, call_status) -> None:
    # 打開 -> 拔掉 -> 防水 -> 好友 -> 關閉

    current_call_status = api._get_call_status()

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append(command.ctrl_u)
    cmd_list.append('p')

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(screens.Target.InUserList, break_detect=True)]

    for _ in range(6):
        if current_call_status == call_status:
            break
        api.connect_core.send(
            cmd,
            target_list,
            screen_timeout=api.config.screen_long_timeout)

        current_call_status = api._get_call_status()
    else:
        raise exceptions.UnknownError('could not set call status')
