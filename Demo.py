import sys
import time
import json
import getpass
import traceback

import PTTLibrary
from PTTLibrary import PTT


def LoginLogout():
    # 登入登出範例

    # Library 參數
    #   LogLevel (Optional):
    #       PTT.LogLevel.DEBUG
    #       PTT.LogLevel.INFO (預設值)
    #       PTT.LogLevel.SLIENT
    #   Language (Optional):
    #       PTT.Language.Chinese (預設值)
    #       PTT.Language.English
    #   ConnectMode (Optional):
    #       PTT.ConnectMode.Telnet
    #       PTT.ConnectMode.WebSocket (預設值)

    # login 參數
    #   ID:
    #       你的 PTT 帳號
    #   Password:
    #       你的 PTT 密碼
    #   KickOtherLogin (Optional):
    #       是否剔除其他登入。
    #       預設值為 False

    PTTBot = PTT.Library()
    try:
        PTTBot.login(ID, Password)
    except PTTLibrary.ConnectCore.LoginError:
        PTTBot.log('登入失敗')
        return
    PTTBot.log('登入成功')
    PTTBot.logout()


def GetTime():
    PTT_TIME = PTTBot.getTime()
    print(PTT_TIME)

if __name__ == '__main__':
    print('Welcome to PTT Library v ' + PTT.Version + ' Demo')

    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        ID = input('請輸入帳號: ')
        Password = getpass.getpass('請輸入密碼: ')

    LoginLogout()

    PTTBot = PTT.Library()
    try:
        PTTBot.login(ID, Password)
    except PTTLibrary.ConnectCore.LoginError:
        PTTBot.log('登入失敗')
        sys.exit()
    PTTBot.log('登入成功')

    GetTime()

    PTTBot.logout()
