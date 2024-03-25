import json
import re
from typing import Dict

from AutoStrEnum import AutoJsonEncoder

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import lib_util
from . import log
from . import screens
from .data_type import UserField


def get_user(api, ptt_id: str) -> Dict:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(ptt_id, str, 'UserID')
    if len(ptt_id) < 2:
        raise ValueError(f'wrong parameter user_id: {ptt_id}')

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append('T')
    cmd_list.append(command.enter)
    cmd_list.append('Q')
    cmd_list.append(command.enter)
    cmd_list.append(ptt_id)
    cmd_list.append(command.enter)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(screens.Target.AnyKey, break_detect=True),
        connect_core.TargetUnit(screens.Target.InTalk, break_detect=True),
    ]

    index = api.connect_core.send(
        cmd,
        target_list)
    ori_screen = api.connect_core.get_screen_queue()[-1]
    if index == 1:
        raise exceptions.NoSuchUser(ptt_id)
    # PTT1
    # 《ＩＤ暱稱》CodingMan (專業程式 BUG 製造機)《經濟狀況》小康 ($73866)
    # 《登入次數》1118 次 (同天內只計一次) 《有效文章》15 篇 (退:0)
    # 《目前動態》閱讀文章     《私人信箱》最近無新信件
    # 《上次上站》10/06/2019 17:29:49 Sun  《上次故鄉》111.251.231.184
    # 《 五子棋 》 0 勝  0 敗  0 和 《象棋戰績》 0 勝  0 敗  0 和

    # https://github.com/Truth0906/PTTLibrary

    # 強大的 PTT 函式庫
    # 提供您 快速 穩定 完整 的 PTT API

    # 提供專業的 PTT 機器人諮詢服務

    # PTT2
    # 《ＩＤ暱稱》CodingMan (專業程式 BUG 製造機)《經濟狀況》家徒四壁 ($0)
    # 《登入次數》8 次 (同天內只計一次)  《有效文章》0 篇
    # 《目前動態》看板列表     《私人信箱》最近無新信件
    # 《上次上站》10/06/2019 17:27:55 Sun  《上次故鄉》111.251.231.184
    # 《 五子棋 》 0 勝  0 敗  0 和 《象棋戰績》 0 勝  0 敗  0 和

    # 《個人名片》CodingMan 目前沒有名片

    lines = ori_screen.split('\n')[1:]

    def parse_user_info_from_line(line: str) -> (str, str):
        part_0 = line[line.find('》') + 1:]
        part_0 = part_0[:part_0.find('《')].strip()

        part_1 = line[line.rfind('》') + 1:].strip()

        return part_0, part_1

    ptt_id, buff_1 = parse_user_info_from_line(lines[0])
    money = int(int_list[0]) if len(int_list := re.findall(r'\d+', buff_1)) > 0 else buff_1
    buff_0, buff_1 = parse_user_info_from_line(lines[1])

    login_count = int(re.findall(r'\d+', buff_0)[0])
    account_verified = ('同天內只計一次' in buff_0)
    legal_post = int(re.findall(r'\d+', buff_1)[0])

    # PTT2 沒有退文
    if api.config.host == data_type.HOST.PTT1:
        illegal_post = int(re.findall(r'\d+', buff_1)[1])
    else:
        illegal_post = None

    activity, mail = parse_user_info_from_line(lines[2])
    last_login_date, last_login_ip = parse_user_info_from_line(lines[3])
    five_chess, chess = parse_user_info_from_line(lines[4])

    signature_file = '\n'.join(lines[5:-1]).strip('\n')

    log.logger.debug('ptt_id', ptt_id)
    log.logger.debug('money', money)
    log.logger.debug('login_count', login_count)
    log.logger.debug('account_verified', account_verified)
    log.logger.debug('legal_post', legal_post)
    log.logger.debug('illegal_post', illegal_post)
    log.logger.debug('activity', activity)
    log.logger.debug('mail', mail)
    log.logger.debug('last_login_date', last_login_date)
    log.logger.debug('last_login_ip', last_login_ip)
    log.logger.debug('five_chess', five_chess)
    log.logger.debug('chess', chess)
    log.logger.debug('signature_file', signature_file)

    user = {
        UserField.ptt_id: ptt_id,
        UserField.money: money,
        UserField.login_count: login_count,
        UserField.account_verified: account_verified,
        UserField.legal_post: legal_post,
        UserField.illegal_post: illegal_post,
        UserField.activity: activity,
        UserField.mail: mail,
        UserField.last_login_date: last_login_date,
        UserField.last_login_ip: last_login_ip,
        UserField.five_chess: five_chess,
        UserField.chess: chess,
        UserField.signature_file: signature_file,
    }
    user = json.dumps(user, cls=AutoJsonEncoder)
    return json.loads(user)
