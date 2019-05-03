import sys
import time
import json
import getpass
import traceback
from PTTLibrary import PTT


if __name__ == '__main__':
    print('Welcome to PTT Library v ' + PTT.Version + ' test case')

    if len(sys.argv) == 2:
        if sys.argv[1] == '-ci':
            print('CI test run success!!')
            sys.exit()

    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        ID = input('請輸入帳號: ')
        Password = getpass.getpass('請輸入密碼: ')
    
    # PTTBot = PTT.Library()
    PTTBot = PTT.Library(LogLevel=PTT.LogLevel.DEBUG)
    ErrCode = PTTBot.login(ID, Password, KickOtherLogin=False)
    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.log('登入失敗')
        sys.exit()
    
    try:

        # PostDemo()
        # PushDemo()
        # GetNewestIndexDemo()
        # GetPostDemo()
        # MailDemo()
        # GetTimeDemo()
        # GetMailDemo()
        # GetUserDemo()
        # GiveMoneyDemo()
        # ChangePasswordDemo()
        # ReplyPostDemo()
        # CrawlBoardDemo()
        # ThrowWaterBallDemo()
        # DelPostDemo()
        # GetFriendListDemo()
        # GetHistoricalWaterBallDemo()
        # SendMessageDemo()
        # CallStatusDemo()

        pass
    except Exception as e:
        
        traceback.print_tb(e.__traceback__)
        print(e)
        PTTBot.Log('接到例外 啟動緊急應變措施')
    # 請養成登出好習慣
    PTTBot.logout()