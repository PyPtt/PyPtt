from SingleLog.log import Logger

from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import screens


def get_call_status(api) -> None:
    logger = Logger('api', api.config.log_level)

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append('A')
    cmd_list.append(command.right)
    cmd_list.append(command.left)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.get_call_status_success,
            '[呼叫器]打開',
            break_detect=True,
            log_level=Logger.DEBUG),
        connect_core.TargetUnit(
            i18n.get_call_status_success,
            '[呼叫器]拔掉',
            break_detect=True,
            log_level=Logger.DEBUG),
        connect_core.TargetUnit(
            i18n.get_call_status_success,
            '[呼叫器]防水',
            break_detect=True,
            log_level=Logger.DEBUG),
        connect_core.TargetUnit(
            i18n.get_call_status_success,
            '[呼叫器]好友',
            break_detect=True,
            log_level=Logger.DEBUG),
        connect_core.TargetUnit(
            i18n.get_call_status_success,
            '[呼叫器]關閉',
            break_detect=True,
            log_level=Logger.DEBUG),
        connect_core.TargetUnit(
            i18n.get_call_status,
            '★',
            response=cmd,
            log_level=Logger.DEBUG),
    ]

    for i in range(2):
        index = api.connect_core.send(cmd, target_list)
        if index < 0:
            if i == 0:
                continue
            ori_screen = api.connect_core.get_screen_queue()[-1]
            raise exceptions.UnknownError(ori_screen)

    if index == 0:
        return data_type.call_status.ON
    if index == 1:
        return data_type.call_status.UNPLUG
    if index == 2:
        return data_type.call_status.WATERPROOF
    if index == 3:
        return data_type.call_status.FRIEND
    if index == 4:
        return data_type.call_status.OFF

    ori_screen = api.connect_core.get_screen_queue()[-1]
    raise exceptions.UnknownError(ori_screen)


def set_call_status(api, call_status) -> None:
    # 打開 -> 拔掉 -> 防水 -> 好友 -> 關閉

    current_call_status = api._get_call_status()

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append(command.ctrl_u)
    cmd_list.append('p')

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.set_call_status_success,
            screens.Target.InUserList,
            break_detect=True)]

    while current_call_status != call_status:
        api.connect_core.send(
            cmd,
            target_list,
            screen_timeout=api.config.screen_long_timeout)

        current_call_status = api._get_call_status()
