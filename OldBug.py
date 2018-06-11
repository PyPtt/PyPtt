import sys
import time
import json
import getpass
import codecs
from PTTLibrary import PTT
from PTTLibrary import Big5uao

PTTBot = None

ResPath = './OldBug/'

def Big5uaoTest():
    
    Big5FileName = ResPath + 'Big5.txt'
    UTF8OutFileName = ResPath + 'Utf8Out.txt'
    Big5OutFileName = ResPath + 'Big5uaoOut.txt'

    s = open(Big5FileName,"rb").read().decode("Big5uao").encode("utf8")
    open(UTF8OutFileName,"wb").write(s)

    if open(UTF8OutFileName,"r", encoding = 'utf-8').read() != '哈囉世界這是大五中文測試':
        print('Big5uao decode error')
        return False
    
    s = open(UTF8OutFileName,"rb").read().decode("utf8").encode("Big5uao")
    open(Big5OutFileName,"wb").write(s)

    if open(Big5OutFileName,"r", encoding = 'big5').read() != '哈囉世界這是大五中文測試':
        print('Big5uao encode error')
        return False
    
    return True

if __name__ == '__main__':
    print('Welcome to PTT Library v ' + PTT.Version + ' Demo')

    print('Big5uao 測試: ' + str(Big5uaoTest()))
    sys.exit()

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

        pass
    except Exception as e:
        print(e)
        PTTBot.Log('接到例外 啟動緊急應變措施')
    # 請養成登出好習慣
    PTTBot.logout()