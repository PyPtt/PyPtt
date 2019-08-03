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
        print('Please note PTT ID and Password in Account.txt')
        print('{"ID":"YourID", "Password":"YourPassword"}')
        sys.exit()

    return ID, Password


def Echo():

    OperateType = PTT.WaterBallOperateType.Clear
    WaterBallList = PTTBot.getWaterBall(OperateType)

    TestWaterBall = [str(x % 10) for x in range(10)]
    TagetID = 'DeepLearning'

    while True:
        WaterBallList = PTTBot.getWaterBall(OperateType)
        if WaterBallList is None:
            time.sleep(1)
            continue
        for WaterBall in WaterBallList:
            if not WaterBall.getType() == PTT.WaterBallType.Catch:
                continue

            Target = WaterBall.getTarget()
            Content = WaterBall.getContent()

            PTTBot.throwWaterBall(Target, 'Echo: ' + Content)


if __name__ == '__main__':
    os.system('cls')
    print('Welcome to PTT Library v ' + PTT.Version + ' Echo Server')

    ID, Password = getPW()

    try:

        PTTBot = PTT.Library(
            ConnectMode=PTT.ConnectMode.WebSocket,
            # LogLevel=PTT.LogLevel.TRACE,
            LogLevel=PTT.LogLevel.DEBUG,
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
    except Exception as e:

        traceback.print_tb(e.__traceback__)
        print(e)

    PTTBot.logout()
