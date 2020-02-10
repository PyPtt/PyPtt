import sys
import time
import json
import traceback
import PTTLibrary
from PTTLibrary import PTT


def getPW():
    try:
        with open('Account2.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        print('Please note PTT ID and Password in Account2.txt')
        print('{"ID":"YourID", "Password":"YourPassword"}')
        sys.exit()

    return ID, Password


def Echo():

    OperateType = PTT.waterball_operate_type.CLEAR
    WaterBallList = PTTBot.get_waterball(OperateType)

    while True:
        PTTBot.set_call_status(PTT.data_type.call_status.OFF)
        time.sleep(1)
        WaterBallList = PTTBot.get_waterball(OperateType)
        if WaterBallList is None:
            continue
        for WaterBall in WaterBallList:
            # Target = WaterBall.getTarget()
            # Content = WaterBall.getContent()

            # print(f'來自 {Target} 的水球 [{Content}]')

            # print('=' * 30)

            if not WaterBall.type == PTT.waterball_type.CATCH:
                continue

            Target = WaterBall.target
            Content = WaterBall.content

            print(f'收到來自 {Target} 的水球 [{Content}]')

            while True:
                try:
                    PTTBot.throw_waterball(Target, 'I heard')
                except PTT.exceptions.UserOffline:
                    time.sleep(1)
                    continue
                break


def listWaterBall():
    OperateType = PTT.waterball_operate_type.CLEAR
    WaterBallList = PTTBot.get_waterball(OperateType)
    OperateType = PTT.waterball_operate_type.NOTHING
    while True:
        PTTBot.set_call_status(PTT.data_type.call_status.OFF)
        time.sleep(1)
        WaterBallList = PTTBot.get_waterball(OperateType)
        if WaterBallList is None:
            continue
        for WaterBall in WaterBallList:

            Target = WaterBall.target
            Content = WaterBall.content

            print(f'收到來自 {Target} 的水球 [{Content}]')

        print('=' * 30)


if __name__ == '__main__':
    print('Welcome to PTT Library v ' + PTT.Version + ' Echo Server')

    ID, Password = getPW()

    try:

        PTTBot = PTT.Library(
            # log_level=PTT.log_level.TRACE,
        )
        try:
            PTTBot.login(
                ID,
                Password,
                kick_other_login=True
            )
        except PTTLibrary.exceptions.LoginError:
            PTTBot.log('登入失敗')
            sys.exit()

        Echo()
        # listWaterBall()

    except Exception as e:

        traceback.print_tb(e.__traceback__)
        print(e)

    PTTBot.logout()
