from __future__ import annotations

import re
from datetime import datetime
from typing import List, Dict

from . import _api_util
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import lib_util
from . import log
from . import screens
from .data_type import WaterballField, WaterballPostAction, WaterballType


_date_pattern = re.compile(r'\[(\d+/\d+/\d+ \d+:\d+:\d+)\]')
_to_target_pattern = re.compile(r'To (\S+):')
_from_target_pattern = re.compile(r'★(\S+) ')


def _parse_date(date_str: str) -> datetime:
    """Parse waterball date string into datetime object."""
    return datetime.strptime(date_str, '%m/%d/%Y %H:%M:%S')


def _merge_continuation_lines(lines: list) -> list:
    merged = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if (line.startswith('To ') or line.startswith('★')) and not _date_pattern.search(line):
            while i + 1 < len(lines) and not _date_pattern.search(line):
                i += 1
                line = line + lines[i]
        merged.append(line)
        i += 1
    return merged


def _parse_waterball_line(line: str) -> Dict | None:
    date_match = _date_pattern.search(line)
    if not date_match:
        return None
    date = date_match.group(1)
    date_str = '[' + date + ']'

    if line.startswith('To '):
        target_match = _to_target_pattern.search(line)
        if not target_match:
            return None
        target = target_match.group(1)
        content_start = line.find(target + ':') + len(target) + 1
        content_end = line.rfind(date_str)
        content = line[content_start:content_end].strip()
        return {
            WaterballField.type: WaterballType.SEND,
            WaterballField.target: target,
            WaterballField.content: content,
            WaterballField.date: _parse_date(date),
        }
    elif line.startswith('★'):
        target_match = _from_target_pattern.search(line)
        if not target_match:
            return None
        target = target_match.group(1)
        content_start = line.find(target + ' ') + len(target) + 1
        content_end = line.rfind(date_str)
        content = line[content_start:content_end].strip()
        return {
            WaterballField.type: WaterballType.CATCH,
            WaterballField.target: target,
            WaterballField.content: content,
            WaterballField.date: _parse_date(date),
        }
    return None


_post_action_cmd = {
    WaterballPostAction.CLEAR: 'C',
    WaterballPostAction.MAILBOX: 'M',
    WaterballPostAction.KEEP: 'R',
}


def get_waterball(api, post_action: WaterballPostAction = WaterballPostAction.KEEP) -> List[Dict]:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    log.logger.info(i18n.get_waterball)

    # 主選單 → T (聊天說話) → D (顯示上幾次熱訊)
    cmd = command.go_main_menu + 'T' + command.enter + 'D' + command.enter

    seen_lines = set()
    all_content_parts = []

    with _api_util.expanded_screen(api):
        while True:
            target_list = [
                connect_core.TargetUnit('◆ 暫無訊息記錄', log_level=log.DEBUG, break_detect=True),
                connect_core.TargetUnit(screens.Target.WaterBallListEnd, log_level=log.DEBUG, break_detect=True),
                connect_core.TargetUnit(screens.Target.InWaterBallList, log_level=log.DEBUG, break_detect=True),
            ]

            index = api.connect_core.send(cmd, target_list)

            if index == 0:
                # no waterball records
                api.connect_core.send('q' + command.go_main_menu, [
                    connect_core.TargetUnit(screens.Target.MainMenu, log_level=log.DEBUG, break_detect=True),
                ])
                log.logger.info(i18n.get_waterball, '...', i18n.success)
                return []

            if index < 0:
                break

            screen = api.connect_core.get_screen_queue()[-1]
            for line in screen.split('\n'):
                line = line.strip()
                if line and line not in seen_lines:
                    seen_lines.add(line)
                    all_content_parts.append(line)

            if index == 1:
                # WaterBallListEnd — collect done, exit viewer; handle post-action prompt
                action_cmd = _post_action_cmd[post_action]
                target_list_exit = [
                    connect_core.TargetUnit(screens.Target.WaterBallPostAction, log_level=log.DEBUG,
                                            response=action_cmd + command.enter),
                    connect_core.TargetUnit(screens.Target.WaterballCleanup, log_level=log.DEBUG,
                                            response='y' + command.enter),
                    connect_core.TargetUnit(screens.Target.MainMenu, log_level=log.DEBUG, break_detect=True),
                ]
                api.connect_core.send('q', target_list_exit)
                api.connect_core.send(command.go_main_menu, [
                    connect_core.TargetUnit(screens.Target.MainMenu, log_level=log.DEBUG, break_detect=True),
                ])
                break

            # index == 2: InWaterBallList — next page
            cmd = command.ctrl_f

    result = []
    for line in _merge_continuation_lines(all_content_parts):
        waterball = _parse_waterball_line(line)
        if waterball:
            result.append(waterball)

    log.logger.info(i18n.get_waterball, '...', i18n.success)
    return result
