import sys
import os
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

    OperateType = PTT.WaterBallOperateType.Clear
    WaterBallList = PTTBot.getWaterBall(OperateType)

    while True:
        PTTBot.setCallStatus(PTT.CallStatus.Off)
        time.sleep(1)
        WaterBallList = PTTBot.getWaterBall(OperateType)
        if WaterBallList is None:
            continue
        for WaterBall in WaterBallList:
            # Target = WaterBall.getTarget()
            # Content = WaterBall.getContent()

            # print(f'來自 {Target} 的水球 [{Content}]')

            # print('=' * 30)

            if not WaterBall.getType() == PTT.WaterBallType.Catch:
                continue

            Target = WaterBall.getTarget()
            Content = WaterBall.getContent()

            print(f'收到來自 {Target} 的水球 [{Content}]')

            while True:
                try:
                    PTTBot.throwWaterBall(Target, 'I heard')
                except PTT.Exceptions.UserOffline:
                    time.sleep(1)
                    continue
                break


def listWaterBall():
    OperateType = PTT.WaterBallOperateType.Clear
    WaterBallList = PTTBot.getWaterBall(OperateType)
    OperateType = PTT.WaterBallOperateType.DoNothing
    while True:
        PTTBot.setCallStatus(PTT.CallStatus.Off)
        time.sleep(1)
        WaterBallList = PTTBot.getWaterBall(OperateType)
        if WaterBallList is None:
            continue
        for WaterBall in WaterBallList:

            Target = WaterBall.getTarget()
            Content = WaterBall.getContent()

            print(f'收到來自 {Target} 的水球 [{Content}]')

        print('=' * 30)


if __name__ == '__main__':
    os.system('cls')
    print('Welcome to PTT Library v ' + PTT.Version + ' Echo Server')

    ID, Password = getPW()

    try:

        PTTBot = PTT.Library(
            # LogLevel=PTT.LogLevel.TRACE,
        )
        try:
            PTTBot.login(
                ID,
                Password,
                KickOtherLogin=True
            )
        except PTTLibrary.Exceptions.LoginError:
            PTTBot.log('登入失敗')
            sys.exit()

        Echo()
        # listWaterBall()

    except Exception as e:

        traceback.print_tb(e.__traceback__)
        print(e)

    PTTBot.logout()
