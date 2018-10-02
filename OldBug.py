import sys
import time
import json
import getpass
import codecs
from PTTLibrary import PTT

PTTBot = None

ResPath = './OldBug/'
def End():
    PTTBot.logout()
    sys.exit()

def FastPushError():

    Board = 'Test'

    ErrCode, NewestIndex = PTTBot.getNewestIndex(Board=Board)
    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('取得 ' + Board + ' 板最新文章編號失敗')
        End()
    
    if NewestIndex == -1:
        PTTBot.Log('取得 ' + Board + ' 板最新文章編號失敗')
        End()

    PTTBot.Log('取得 ' + Board + ' 板最新文章編號: ' + str(NewestIndex))

    for i in range(100):
        Stop = False

        while True:

            PTTBot.Log('-----------------')
            ErrCode = PTTBot.push(Board, PTT.PushType.Push, '快速推文測試 手速 400 ' + str(i), PostIndex=NewestIndex)
            PTTBot.Log('-----------------=========')
            if ErrCode == PTT.ErrorCode.Success:
                PTTBot.Log('使用文章編號: 推文成功')
                break
            elif ErrCode == PTT.ErrorCode.ErrorInput:
                PTTBot.Log('使用文章編號: 參數錯誤')
                Stop = True
                break
            elif ErrCode == PTT.ErrorCode.NoPermission:
                PTTBot.Log('使用文章編號: 無發文權限')
                Stop = True
                break
            elif ErrCode == PTT.ErrorCode.NoFastPush:
                PTTBot.Log('禁止快速推文 等待一秒後重試')
                time.sleep(1)
                PTTBot.Log('禁止快速推文 等待一秒後重試 QQ')
            else:
                PTTBot.Log('使用文章編號: 推文失敗 ErrCode: ' + str(ErrCode))
                Stop = True
                break

        if Stop:
            break
    return
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

    PTTBot = PTT.Library()

    ErrCode = PTTBot.login(ID, Password)
    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('登入失敗')
        sys.exit()
    
    try:
        FastPushError()
        pass
    except Exception as e:
        print(e)
        PTTBot.Log('接到例外 啟動緊急應變措施')
    # 請養成登出好習慣
    PTTBot.logout()