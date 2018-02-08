import sys
import time
import json
import getpass
from PTTLibrary import SSHPTT as PTT

# 如果你想要自動登入，建立 Account.txt
# 然後裡面填上 {"ID":"YourID", "Password":"YourPW"}

BoardList = ['Wanted', 'Gossiping', 'Test', 'NBA', 'Baseball', 'LOL', 'C_Chat']
PostIDList = ['1PC1YXYj', '1PCBfel1', '1D89C0oV']

PTTBot = None

def PostDemo():

    JapanText = "水馬赤いな。ア、イ、ウ、エ、オ。\r\n\
浮藻に子蝦もおよいでる。 \r\n\
\r\n\
柿の木、栗の木。カ、キ、ク、ケ、コ。 \r\n\
啄木鳥こつこつ、枯れけやき。 \r\n\
\r\n\
大角豆に醋をかけ、サ、シ、ス、セ、ソ。 \r\n\
その魚浅瀬で刺しました。 \r\n\
\r\n\
立ちましょ、喇叭で、タ、チ、ツ、テ、ト。 \r\n\
トテトテタッタと飛び立った。 \r\n\
\r\n\
蛞蝓のろのろ、ナ、ニ、ヌ、ネ、ノ。 \r\n\
納戸にぬめって、なにねばる。 \r\n\
\r\n\
鳩ぽっぽ、ほろほろ。ハ、ヒ、フ、ヘ、ホ。 \r\n\
日向のお部屋にや笛を吹く。 \r\n\
\r\n\
蝸牛、螺旋巻、マ、ミ、ム、メ、モ。 \r\n\
梅の実落ちても見もしまい。 \r\n\
\r\n\
焼栗、ゆで栗。ヤ、イ、ユ、エ、ヨ。 \r\n\
山田に灯のつく宵の家。 \r\n\
\r\n\
雷鳥は寒かろ、ラ、リ、ル、レ、ロ。 \r\n\
蓮花が咲いたら、瑠璃の鳥。 \r\n\
\r\n\
わい、わい、わっしょい。ワ、ヰ、ウ、ヱ、ヲ。 \r\n\
植木屋、井戸換へ、お祭りだ。\r\n"

    #這個範例是如何PO文
    #第一個參數是你要PO文的板
    #第二個參數是文章標題
    #第三個參數是文章內文
    #第四個參數是發文類別       1
    #第五個參數是第幾個簽名檔    0 表示不放簽名檔
    
    #回傳值 錯誤碼

    for i in range(3):
        
        ErrorCode = PTTBot.post('Test', 'Python 機器人自動PO文測試', '自動PO文測試，如有打擾請告知。\r\n\r\n使用PTT Library 測試\r\n\r\nhttps://goo.gl/5hdAqu\r\n\r\n' + JapanText, 1, 0)
        if ErrorCode == PTT.ErrorCode.Success:
            PTTBot.Log('在 Test 板發文成功')
        elif ErrorCode == PTT.ErrorCode.NoPermission:
            PTTBot.Log('發文權限不足')
        else:
            PTTBot.Log('在 Test 板發文失敗')

def GetNewestPostIndexDemo():

    #這個範例是如何取得某版的最新文章編號
    #第一個參數是板面
    
    #回傳值 就是錯誤碼跟最新文章編號

    # ErrorCode, NewestIndex = PTTBot.getNewestPostIndex('Wanted')
    # if ErrorCode == PTTBot.ErrorCode.Success:
    #     PTTBot.Log('取得 Wanted 板最新文章編號成功: ' + str(NewestIndex))
    # else:
    #     PTTBot.Log('取得 Wanted 板最新文章編號失敗')
    #     return False


    for i in range(10):
        for Board in BoardList:
            ErrorCode, NewestIndex = PTTBot.getNewestPostIndex(Board)
            if ErrorCode == PTT.ErrorCode.Success:
                PTTBot.Log('取得 ' + Board + ' 板最新文章編號成功: ' + str(NewestIndex))
            else:
                PTTBot.Log('取得 ' + Board + ' 板最新文章編號失敗')
                return False
            #time.sleep(1)

def GetPostInfoDemo():
    
    # 這個範例是如何取得單一文章資訊
    # getPostInfoByIndex
    # 第一個參數是板面
    # 第二個參數就是你想查詢的文章編號
    # 如果你不幸的只有文章代碼 那就使用 getPostInfoByID
    # getPostInfoByID
    # 第一個參數是板面
    # 第二個參數就是你想查詢的文章代碼
    
    #回傳值 錯誤碼, 文章資訊
    
    #文章資訊的資料結構可參考如下
    
    ################## 文章資訊 Post information ##################
    # getPostBoard              文章所在版面
    # getPostID                 文章 ID ex: 1PCBfel1
    # getPostAuthor             作者
    # getPostDate               文章發布時間
    # getTitle                  文章標題
    # getPostContent            文章內文
    # getMoney                  文章P幣
    # getWebUrl                 文章網址
    # getPushList               文章推文清單 備註: 推文是從網頁解析，極有可能不即時
    # getOriginalData           文章網頁原始資料 (開發用)
    
    ################## 推文資訊 Push information ##################
    # getPushType               推文類別 推噓箭頭
    # getPushID                 推文ID
    # getPushContent            推文內文
    # getPushTime               推文時間
    
    ErrorCode, NewestIndex = PTTBot.getNewestPostIndex('Wanted')
    if ErrorCode != PTTBot.Success:
        PTTBot.Log('取得最新文章編號失敗')
        return False
    TryPost = 3
    if NewestIndex == -1:
        PTTBot.Log('取得最新文章編號失敗')
        return False

    for i in range(TryPost)[::-1]:
        
        ErrorCode, Post = PTTBot.getPostInfoByIndex('Wanted', NewestIndex - i)
        if ErrorCode == PTTBot.PostDeleted:
            PTTBot.Log('文章已經被刪除')
            continue
        if ErrorCode == PTTBot.WebFormatError:
            PTTBot.Log('網頁結構錯誤')
            continue
        if ErrorCode != PTTBot.Success:
            PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrorCode))
            return False
        PTTBot.Log(str(int(((i) * 2 * 100) / (TryPost * 2))) + ' % ')

        PTTBot.Log('文章代碼: ' + Post.getPostID())
        PTTBot.Log('作者: ' + Post.getPostAuthor())
        PTTBot.Log('時間: ' + Post.getPostDate())
        PTTBot.Log('標題: ' + Post.getTitle())
        PTTBot.Log('價錢: ' + str(Post.getMoney()))
        PTTBot.Log('網址: ' + Post.getWebUrl())
        PTTBot.Log('內文: \r\n' + Post.getPostContent())

        for Push in Post.getPushList():
            if Push.getPushType() == PTTBot.PushType_Push:
                PushTypeString = '推'
            elif Push.getPushType() == PTTBot.PushType_Boo:
                PushTypeString = '噓'
            elif Push.getPushType() == PTTBot.PushType_Arrow:
                PushTypeString = '→'
                
            PTTBot.Log(PushTypeString + ' ' + Push.getPushID() + ' ' + Push.getPushContent() + ' ' + Push.getPushTime())
        
        ErrorCode, Post = PTTBot.getPostInfoByID('Wanted', Post.getPostID())
        if ErrorCode != PTTBot.Success:
            PTTBot.Log('使用文章代碼取得文章詳細資訊失敗 錯誤碼: ' + str(ErrorCode))
            return False
        PTTBot.Log(str(int(((i + 1) * 2 * 100) / (TryPost * 2))) + ' % ' + Post.getPostID() + ' 標題: ' + Post.getTitle())
        
        PTTBot.Log('-----------------------')
        
def GetNewPostIndexListDemo():

    # 這個範例是如何取得某版的最新文章編號清單
    # 跟上一次使用 getPostInfoByIndex 比較
    # 第一個參數是板面
    # 第二個參數就是你上一次查詢的最新文章編號 代入 0 就會等到有PO文才會有清單結果
    
    # 詳細使用方式可以參考 範例程式中的 汪踢推文機器人
    
    # 回傳值 錯誤碼, 最新文章編號清單

    ErrorCode, NewestIndex = PTTBot.getNewestPostIndex('Wanted')
    if ErrorCode != PTTBot.Success:
        return False
    
    LastIndex = NewestIndex - 5
    for i in range(3):
        #Return new post list LastIndex ~ newest without LastIndex
        ErrorCode, LastIndexList = PTTBot.getNewPostIndexList('Wanted', LastIndex)
        if ErrorCode != PTTBot.Success:
            return False
        if not len(LastIndexList) == 0:
            for NewPostIndex in LastIndexList:
                PTTBot.Log('偵測到新文章編號 ' + str(NewPostIndex))
            LastIndex = LastIndexList.pop()
def PushDemo():
    
    # 這個範例是示範如何對特定文章推文
    # 第一個參數是板面
    # 第二個參數是推文類別

    ################## 推文種類 Push Type ##################
    # PTTBot.PushType_Push      推
    # PTTBot.PushType_Boo       噓
    # PTTBot.PushType_Arrow     箭頭
    
    # 第三個參數是推文內文
    # 第四個參數是文章編號或者ID 端看你用 ByIndex 或 ByID
    
    # 回傳值 錯誤碼

    ErrorCode, NewestIndex = PTTBot.getNewestPostIndex('Test')
    if ErrorCode != PTT.ErrorCode.Success:
        PTTBot.Log('取得最新文章編號失敗 錯誤碼: ' + str(ErrorCode))
        return False
    PTTBot.Log('最新文章編號: ' + str(NewestIndex))

    for i in range(1):
        ErrorCode = PTTBot.push('Test', PTT.PushType.Push, 'PTT Library Push API https://goo.gl/5hdAqu', PostIndex=NewestIndex)
        if ErrorCode == PTT.ErrorCode.Success:
            PTTBot.Log('使用文章編號: 推文成功')
        elif ErrorCode == PTT.ErrorCode.ErrorInput:
            PTTBot.Log('使用文章編號: 參數錯誤')
            return False
        elif ErrorCode == PTT.ErrorCode.NoPermission:
            PTTBot.Log('使用文章編號: 無發文權限')
            return False
        else:
            PTTBot.Log('使用文章編號: 推文失敗')
            return False

def MailDemo():
    
    # 這個範例是如何寄信給某鄉民

    # 第一個參數是你想寄信的ID
    # 第二個參數是信件標題
    # 第三個參數是信件內容
    # 第四個參數是簽名檔選擇 0 不加簽名檔
    
    for i in range(1):
        ErrorCode = PTTBot.mail(ID, '自動寄信測試標題', '自動測試 如有誤寄打擾 抱歉QQ', 0)
        if ErrorCode == PTTBot.Success:
            PTTBot.Log('寄信給 ' + ID + ' 成功')
        else:
            PTTBot.Log('寄信給 ' + ID + ' 失敗')
def GiveMoneyDemo():

    # 這個範例是如何送P幣給某鄉民

    # 第一個參數是你想寄信的ID
    # 第二個參數是你想給予多少P幣
    # 第三個參數是你自己的密碼
    
    WhoAreUwantToGiveMoney = 'CodingMan'
    try:
        PTTBot.Log('偵測到前景執行使用編碼: ' + sys.stdin.encoding)
        Donate = input('請問願意贊助作者 10 P幣嗎？[Y/n] ').lower()
    except Exception:
        # 被背景執行了..邊緣程式沒資格問要不要贊助..
        # 反正..從來沒收到過贊助，角落就是我的圈圈!!! 嗚嗚嗚
        pass
        return

    if Donate == 'y' or Donate == '':
        ErrorCode = PTTBot.giveMoney(WhoAreUwantToGiveMoney, 10, Password)
        
        if ErrorCode == PTTBot.Success:
            PTTBot.Log('送P幣給 ' + WhoAreUwantToGiveMoney + ' 成功')
        else:
            PTTBot.Log('送P幣給 ' + WhoAreUwantToGiveMoney + ' 失敗')
    else:
        PTTBot.Log('贊助又被拒絕了..可..可惡')
def GetTimeDemo():

    #這個範例是取得PTT的時間，有時需要跟PTT對時的需求，比如說 準點報時
        
    for i in range(3):
        ErrorCode, Time = PTTBot.getTime()
        if ErrorCode != PTTBot.Success:
            PTTBot.Log('取得時間失敗')
            return False
        PTTBot.Log('Ptt time: ' + Time + '!')
        time.sleep(1)

def PostHandler(Post):
    
    #這是 crawlBoard 需要的 call back function
    #每當爬蟲取得新文章就會呼叫此函式一次
    #因此你可以在這自由地決定存檔的格式 或者任何你想做的分析
    
    #文章資料結構可參考如下
    ################## 文章資訊 Post information ##################
    # getPostBoard              文章所在版面
    # getPostID                 文章 ID ex: 1PCBfel1
    # getPostAuthor             作者
    # getPostDate               文章發布時間
    # getTitle                  文章標題
    # getPostContent            文章內文
    # getMoney                  文章P幣
    # getWebUrl                 文章網址
    # getPushList               文章推文清單 備註: 推文是從網頁解析，極有可能不即時
    # getOriginalData           文章網頁原始資料 (開發用)
    
    ################## 推文資訊 Push information ##################
    # getPushType               推文類別 推噓箭頭?
    # getPushID                 推文ID
    # getPushContent            推文內文
    # getPushTime               推文時間
    
    with open("CrawlBoardResult.txt", "a") as ResultFile:
        ResultFile.write(Post.getTitle() + '\n')
    
def CrawlBoardDemo():
    
    #範例是從編號 1 爬到 編號 100 的文章
    #如果想要取得所有文章可省略編號參數
    #PTTBot.crawlBoard('Wanted', PostHandler)
    #這樣就會全部文章都會爬下來
    
    ErrorCode = PTTBot.crawlBoard('Wanted', PostHandler, 1, 100)
    if ErrorCode == PTTBot.Success:
        PTTBot.Log('爬行成功')
        
def GetUserInfoDemo():
    
    #範例是追蹤 某些ID的情況
    #此API可以持續追蹤某ID的動態
    #詳細可以參考 範例程式中的 ID追蹤器
    
    #使用者資訊資料結構可參考如下
    
    ################## 使用者資訊 User information ##################
    # getID                     ID
    # getMoney                  使用者經濟狀況
    # getLoginTime              登入次數
    # getPost                   有效文章數
    # getState                  目前動態
    # getMail                   信箱狀態
    # getLastLogin              最後登入時間
    # getLastIP                 上次故鄉
    # getFiveChess              五子棋戰績
    # getChess                  象棋戰績
    
    for IDs in [ID, 'FakeID_____']:
        
        PTTBot.Log('---------------------------')
        PTTBot.Log('Start query: ' + IDs)
        ErrorCode, UserInfo = PTTBot.getUserInfo(IDs)
        if ErrorCode == PTTBot.NoUser:
            PTTBot.Log('No such user')
            continue
        if ErrorCode != PTTBot.Success:
            PTTBot.Log('getUserInfo fail error code: ' + str(ErrorCode))
            continue
        
        PTTBot.Log('使用者ID: ' + UserInfo.getID())
        PTTBot.Log('使用者經濟狀況: ' + str(UserInfo.getMoney()))
        PTTBot.Log('登入次數: ' + str(UserInfo.getLoginTime()))
        PTTBot.Log('有效文章數: ' + str(UserInfo.getPost()))
        PTTBot.Log('目前動態: ' + UserInfo.getState() + '!')
        PTTBot.Log('信箱狀態: ' + UserInfo.getMail() + '!')
        PTTBot.Log('最後登入時間: ' + UserInfo.getLastLogin() + '!')
        PTTBot.Log('上次故鄉: ' + UserInfo.getLastIP() + '!')
        PTTBot.Log('五子棋戰績: ' + UserInfo.getFiveChess() + '!')
        PTTBot.Log('象棋戰績: ' + UserInfo.getChess() + '!')

def ReplyPostDemo():
    
    #此範例是因應回文的需求
    #此API可以用三種方式回文 回文至板上 信箱 或者皆是

    # 第一個參數是版面
    # 第二個參數是回文內容
    # 第三個參數是回文種類

    ################## 回文種類 ReplyPost information ##################
    # PTTBot.ReplyPost_Board    回文至板上
    # PTTBot.ReplyPost_Mail     回文至信箱
    # PTTBot.ReplyPost_Board + PTTBot.ReplyPost_Mail 回文至信箱與板上
     
    # 回傳 錯誤碼

    ErrorCode = PTTBot.post('Test', '自動回文測試文章', '標準測試流程，如有打擾請告知。\r\n\r\n使用PTT Library 測試\r\n\r\nhttps://goo.gl/5hdAqu', 1, 0)
    if ErrorCode == PTTBot.Success:
        PTTBot.Log('在 Test 板發文成功')
    elif ErrorCode == PTTBot.NoPermission:
        PTTBot.Log('發文權限不足')
    else:
        PTTBot.Log('在 Test 板發文失敗')
    
    ErrorCode, NewestIndex = PTTBot.getNewestPostIndex('Test')
    if ErrorCode == PTTBot.Success:
        PTTBot.Log('取得 ' + 'Test' + ' 板最新文章編號成功: ' + str(NewestIndex))
    else:
        PTTBot.Log('取得 ' + 'Test' + ' 板最新文章編號失敗')
        return False

    ErrorCode = PTTBot.replyPost('Test', '回文測試 回文至板上', PTTBot.ReplyPost_Board, Index=NewestIndex)
    if ErrorCode == PTTBot.Success:
        PTTBot.Log('在 Test 回文至板上成功!')
    else:
        PTTBot.Log('在 Test 回文至板上失敗 ' + str(ErrorCode))
    
    ErrorCode = PTTBot.replyPost('Test', '回文測試 回文至信箱', PTTBot.ReplyPost_Mail, Index=NewestIndex)
    if ErrorCode == PTTBot.Success:
        PTTBot.Log('在 Test 回文至信箱成功!')
    else:
        PTTBot.Log('在 Test 回文至信箱失敗 ' + str(ErrorCode))
        
    ErrorCode = PTTBot.replyPost('Test', '回文測試 回文至版上與信箱', PTTBot.ReplyPost_Board + PTTBot.ReplyPost_Mail, Index=NewestIndex)
    if ErrorCode == PTTBot.Success:
        PTTBot.Log('在 Test 回文至版上與信箱成功!')
    else:
        PTTBot.Log('在 Test 回文至版上與信箱失敗 ' + str(ErrorCode))

def GetMailDemo():
    
    # 這是用來取得信件的 api
    # 輸入信件編號
    # 回傳 錯誤碼、郵件結構
    
    #信件資訊資料結構可參考如下
    
    ################## 信件資訊 Mail information ##################
    # getAuthor                 寄件人資訊
    # getTitle                  信件標題
    # getDate                   寄件日期
    # getContent                信件內文
    # getIP                     寄件IP

    ErrorCode, NewestMailIndex = PTTBot.getNewestMailIndex()
    if ErrorCode == PTTBot.Success:
        PTTBot.Log('取得最新信件編號成功')
    else:
        PTTBot.Log('取得最新信件編號失敗 錯誤碼: ' + str(ErrorCode))
        return

    PTTBot.Log('最新信件編號: ' + str(NewestMailIndex))

    if NewestMailIndex > 3:
        MailStartIndex = NewestMailIndex - 3
    else:
        MailStartIndex = 1

    for i in range(MailStartIndex, NewestMailIndex):
        MailIndex = i + 1
        ErrorCode, Mail = PTTBot.getMail(MailIndex)
        if ErrorCode == PTTBot.Success:
            PTTBot.Log('取得編號 ' + str(MailIndex) + ' 信件成功')

            PTTBot.Log('信件作者: ' + Mail.getAuthor())
            PTTBot.Log('信件標題: ' + Mail.getTitle())
            PTTBot.Log('信件日期: ' + Mail.getDate())
            # PTTBot.Log('信件內文: ' + Mail.getContent())
            PTTBot.Log('信件IP: ' + Mail.getIP())

            PTTBot.Log('=' * 30)

        else:
            PTTBot.Log('取得編號 ' + str(MailIndex) + ' 信件失敗 錯誤碼: ' + str(ErrorCode))
            return
    return 

if __name__ == '__main__':
    print('Welcome to PTT Library v ' + PTT.Version + ' Demo')

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
    
    PTTBot = PTT.Library(ID, Password, kickOtherLogin=False, _LogLevel=PTT.LogLevel.DEBUG)
    # PTTBot = PTT.Library(ID, Password, kickOtherLogin=True)
    if not PTTBot.isLoginSuccess():
        PTTBot.Log('登入失敗')
        sys.exit()

    # GetNewestPostIndexDemo()
    PostDemo()
    # PushDemo()

    # GetPostInfoDemo()
    # GetNewPostIndexListDemo()
    # MailDemo()
    # GetTimeDemo()
    # GetUserInfoDemo()
    # GiveMoneyDemo()
    # CrawlBoardDemo()
    # ReplyPostDemo()
    # GetMailDemo()

    # 請養成登出好習慣
    PTTBot.logout()
    