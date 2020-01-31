import sys
import time
import json
import traceback
import PTTLibrary
from PTTLibrary import PTT


def getPW():
    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        print('Please note PTT ID and Password in Account.txt')
        print('{"ID":"YourID", "Password":"YourPassword"}')
        sys.exit()

    return ID, Password


def SendEcho():

    OperateType = PTT.WaterBallOperateType.Clear
    WaterBallList = PTTBot.get_waterball(OperateType)

    while True:
        try:
            PTTBot.throw_waterball('DeepLearning', 'Hey')
        except PTT.Exceptions.UserOffline:
            time.sleep(1)
            continue
        break

    while True:
        PTTBot.set_callstatus(PTT.CallStatus.Off)
        time.sleep(1)
        WaterBallList = PTTBot.get_waterball(OperateType)
        if WaterBallList is None:
            continue

        for WaterBall in WaterBallList:
            if not WaterBall.get_type() == PTT.WaterBallType.Catch:
                continue

            Target = WaterBall.get_target()
            Content = WaterBall.get_content()

            print(f'收到來自 {Target} 的水球 [{Content}]')

            while True:
                try:
                    PTTBot.throw_waterball(Target, 'Hey')
                except PTT.Exceptions.UserOffline:
                    time.sleep(1)
                    continue
                break


if __name__ == '__main__':
    print('Welcome to PTT Library v ' + PTT.Version + ' Echo Server')

    ID, Password = getPW()

    try:

        PTTBot = PTT.Library()
        try:
            PTTBot.login(
                ID,
                Password,
                kick_other_login=True
            )
        except PTTLibrary.Exceptions.LoginError:
            PTTBot.log('登入失敗')
            sys.exit()

        SendEcho()
    except Exception as e:

        traceback.print_tb(e.__traceback__)
        print(e)

    PTTBot.logout()
