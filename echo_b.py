import sys
import time
import json
import traceback
import PTTLibrary
from PyPtt import PTT


def get_pw():
    try:
        with open('Account2.txt') as AccountFile:
            account = json.load(AccountFile)
            ptt_id = account['ID']
            password = account['Password']
    except FileNotFoundError:
        print('Please note PTT ID and Password in Account2.txt')
        print('{"ID":"YourID", "Password":"YourPassword"}')
        sys.exit()

    return ptt_id, password


def echo():
    operate_type = PTT.data_type.waterball_operate_type.CLEAR
    ptt_bot.get_waterball(operate_type)

    while True:
        ptt_bot.set_call_status(PTT.data_type.call_status.OFF)
        time.sleep(1)
        waterball_list = ptt_bot.get_waterball(operate_type)
        if waterball_list is None:
            continue
        for waterball in waterball_list:
            if not waterball.type == PTT.data_type.waterball_type.CATCH:
                continue

            target = waterball.target
            content = waterball.content

            print(f'收到來自 {target} 的水球 [{content}]')

            while True:
                try:
                    ptt_bot.throw_waterball(target, f'I heard {content}')
                except PTT.exceptions.UserOffline:
                    time.sleep(1)
                    continue
                break


# def list_waterball():
#     operate_type = PTT.waterball_operate_type.CLEAR
#     ptt_bot.get_waterball(operate_type)
#     operate_type = PTT.waterball_operate_type.NOTHING
#     while True:
#         ptt_bot.set_call_status(PTT.data_type.call_status.OFF)
#         time.sleep(1)
#         waterball_list = ptt_bot.get_waterball(operate_type)
#         if waterball_list is None:
#             continue
#         for waterball in waterball_list:
#             target = waterball.target
#             content = waterball.content
#
#             print(f'收到來自 {target} 的水球 [{content}]')
#
#         print('=' * 30)


if __name__ == '__main__':
    print('Welcome to PyPtt v ' + PTT.version.V + ' Echo Server')

    ptt_id, password = get_pw()

    try:

        ptt_bot = PTT.API(
            # log_level=PTT.log_level.TRACE,
        )
        try:
            ptt_bot.login(
                ptt_id,
                password,
                kick_other_login=True
            )
        except PTTLibrary.exceptions.LoginError:
            ptt_bot.log('登入失敗')
            sys.exit()

        echo()
        # listWaterBall()

    except Exception as e:

        traceback.print_tb(e.__traceback__)
        print(e)

    ptt_bot.logout()
