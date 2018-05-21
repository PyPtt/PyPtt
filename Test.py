import sys
import time
import json
import getpass
import codecs
from PTTLibrary import PTT

# 如果你想要自動登入，建立 Account.txt
# 然後裡面填上 {"ID":"YourID", "Password":"YourPW"}

BoardList = ['Wanted', 'Gossiping', 'Test', 'NBA', 'Baseball', 'LOL', 'C_Chat']

PTTBot = None

def PostDemo():

    #這個範例是如何 po 文
    #第一個參數是你要 po 文的板
    #第二個參數是文章標題
    #第三個參數是文章內文
    #第四個參數是發文類別       1
    #第五個參數是第幾個簽名檔    0 表示不放簽名檔
    
    #回傳值 錯誤碼

    for i in range(3):
        
        Content = ''
        
        if i == 0:
            for ii in range(3):
                Content += '測試行 ' + str(ii) + '\r'
        if i == 1:
            for ii in range(16):
                Content += '測試行 ' + str(ii) + '\r'
        if i == 2:
            for ii in range(128):
                Content += '測試行 ' + str(ii) + '\r'
        
        ErrCode = PTTBot.post('Test', 'Python 機器人自動PO文測試' + str(i), '自動PO文測試，如有打擾請告知。\r\n\r\n使用PTT Library 測試\r\n\r\nhttps://goo.gl/5hdAqu\r\n\r\n' + Content, 1, 0)
        if ErrCode == PTT.ErrorCode.Success:
            PTTBot.Log('在 Test 板發文成功')
        elif ErrCode == PTT.ErrorCode.NoPermission:
            PTTBot.Log('發文權限不足')
        else:
            PTTBot.Log('在 Test 板發文失敗')

def GetNewestIndexDemo():
    
    # 這個範例是如何取得信箱最新郵件編號或者某版最新文章編號
    # 帶入版面則回傳該版面最新文章編號
    # 若無 則回傳信箱最新郵件編號
    
    #回傳值 錯誤碼

    BoardList = ['Wanted', 'Gossiping', 'Test', 'NBA', 'Baseball', 'LOL', 'C_Chat']

    for i in range(1):
        for Board in BoardList:
            ErrCode, NewestIndex = PTTBot.getNewestIndex(Board=Board)
            if ErrCode != PTT.ErrorCode.Success:
                PTTBot.Log('取得 ' + Board + ' 板最新文章編號失敗')
                break
            
            if NewestIndex == -1:
                PTTBot.Log('取得 ' + Board + ' 板最新文章編號失敗')
                break
        
            PTTBot.Log('取得 ' + Board + ' 板最新文章編號: ' + str(NewestIndex))
    
    for i in range(1):
        ErrCode, NewestMailIndex = PTTBot.getNewestIndex()
        if ErrCode == PTT.ErrorCode.Success:
            PTTBot.Log(str(i) + ' 取得最新信件編號成功 共有 ' + str(NewestMailIndex) + ' 封信')
        else:
            PTTBot.Log('取得最新信件編號失敗 錯誤碼: ' + str(ErrCode))
    
    PTTBot.Log('GetNewestIndexDemo 測試完成')
    return
def showPost(Post):
    PTTBot.Log('文章代碼: ' + Post.getID())
    PTTBot.Log('作者: ' + Post.getAuthor())
    PTTBot.Log('時間: ' + Post.getDate())
    PTTBot.Log('標題: ' + Post.getTitle())
    PTTBot.Log('價錢: ' + str(Post.getMoney()))
    PTTBot.Log('IP: ' + Post.getIP())
    PTTBot.Log('網址: ' + Post.getWebUrl())

    # PTTBot.Log('內文: ' + Post.getContent())

    PushCount = 0
    BooCount = 0
    ArrowCount = 0
    for Push in Post.getPushList():
        if Push.getType() == PTT.PushType.Push:
            PushCount += 1
        elif Push.getType() == PTT.PushType.Boo:
            BooCount += 1
        elif Push.getType() == PTT.PushType.Arrow:
            ArrowCount += 1
    
    PTTBot.Log('共有 ' + str(PushCount) + ' 推 ' + str(BooCount) + ' 噓 ' + str(ArrowCount) + ' 箭頭')

def GetPostDemo():
    
    # 這個範例是如何取得單一文章資訊
    # getPost
    # 第一個固定參數是板面
    # 第二個參數就是你想查詢的文章編號或者文章代碼
        
    #回傳值 錯誤碼, 文章資訊
    
    #文章資訊的資料結構可參考如下
    
    ################## 文章資訊 Post information ##################
    # getBoard                  文章所在版面
    # getID                     文章 ID ex: 1PCBfel1
    # getAuthor                 作者
    # getDate                   文章發布時間
    # getTitle                  文章標題
    # getContent                文章內文
    # getMoney                  文章P幣
    # getWebUrl                 文章網址
    # getPushList               文章即時推文清單
    
    ################## 推文資訊 Push information ##################
    # getType                   推文類別 推噓箭頭
    # getAuthor                 推文ID
    # getContent                推文內文
    # getTime                   推文時間
    
    TryPost = 3
    
    BoardList = ['Wanted', 'Gossiping', 'Test', 'NBA', 'Baseball', 'LOL', 'C_Chat']
    # BoardList = ['Gossiping']

    for Board in BoardList:
        
        ErrCode, NewestIndex = PTTBot.getNewestIndex(Board=Board)
        if ErrCode != PTT.ErrorCode.Success:
            PTTBot.Log('取得 ' + Board + ' 板最新文章編號失敗')
            return False
        
        if NewestIndex == -1:
            PTTBot.Log('取得 ' + Board + ' 板最新文章編號失敗')
            return False
        
        PTTBot.Log('取得 ' + Board + ' 板最新文章編號: ' + str(NewestIndex))
        for i in range(TryPost):
            PTTBot.Log('-' * 50)
            PTTBot.Log(str(i) + ' 測試 ' + Board + ' ' + str(NewestIndex - i))

            ErrCode, Post = PTTBot.getPost(Board, PostIndex=NewestIndex - i)
            if ErrCode == PTT.ErrorCode.PostDeleted:
                PTTBot.Log('文章已經被刪除')
                continue
            elif ErrCode != PTT.ErrorCode.Success:
                PTTBot.Log('使用文章編號取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
                continue
            
            PTTBot.Log('測試 ' + Board + ' ' + Post.getID())

            # 使用 PostID 模式可能會撞到 PTT BUG
            ErrCode, Post = PTTBot.getPost(Board, PostID=Post.getID())
            if ErrCode == PTT.ErrorCode.PostDeleted:
                PTTBot.Log('文章已經被刪除')
                sys.exit()
            elif ErrCode != PTT.ErrorCode.Success:
                PTTBot.Log('使用文章代碼取得文章詳細資訊失敗 錯誤碼: ' + str(ErrCode))
                sys.exit()
            
            # if '任意鍵' in Post.getTitle():
            showPost(Post)

def PushDemo():
    
    # 這個範例是示範如何對特定文章推文
    # 第一個參數是板面
    # 第二個參數是推文類別

    ################## 推文種類 Push Type ##################
    # PTT.PushType.Push         推
    # PTT.PushType.Boo          噓
    # PTT.PushType.Arrow        箭頭
    
    # 第三個參數是推文內文
    # 第四個參數是文章編號或者文章代碼 擇一使用
    
    # 回傳值 錯誤碼

    ErrCode, NewestIndex = PTTBot.getNewestIndex(Board='Test')
    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('取得最新文章編號失敗 錯誤碼: ' + str(ErrCode))
        return False
    PTTBot.Log('最新文章編號: ' + str(NewestIndex))
    
    for i in range(10):
        ErrCode = PTTBot.push('Test', PTT.PushType.Push, 'PTT Library Push API https://goo.gl/5hdAqu', PostIndex=NewestIndex)
        if ErrCode == PTT.ErrorCode.Success:
            PTTBot.Log('使用文章編號: 推文成功')
        elif ErrCode == PTT.ErrorCode.ErrorInput:
            PTTBot.Log('使用文章編號: 參數錯誤')
            return False
        elif ErrCode == PTT.ErrorCode.NoPermission:
            PTTBot.Log('使用文章編號: 無發文權限')
            return False
        else:
            PTTBot.Log('使用文章編號: 推文失敗')
            return False
    
    TestString = '批踢踢實業坊，簡稱批踢踢、PTT，是一個台灣BBS，採用Telnet BBS技術運作，以學術性質為目的在網路上提供言論空間。目前由國立臺灣大學電子布告欄系統研究社管理，大部份的系統原始碼由國立臺灣大學資訊工程學系的學生與校友進行維護，並且邀請法律專業人士擔任法律顧問。它有兩個分站，分別為批踢踢兔與批踢踢參。目前在批踢踢實業坊與批踢踢兔註冊總人數約150萬人，尖峰時段兩站超過15萬名使用者同時上線，擁有超過2萬個不同主題的看板，每日超過2萬篇新文章及50萬則推文被發表，是台灣使用人次最多的網路論壇之一。'

    ErrCode = PTTBot.push('Test', PTT.PushType.Push, 'PTT Library Long Push https://goo.gl/5hdAqu', PostIndex=NewestIndex)
    if ErrCode == PTT.ErrorCode.Success:
        PTTBot.Log('使用文章編號: 推文成功')
    elif ErrCode == PTT.ErrorCode.ErrorInput:
        PTTBot.Log('使用文章編號: 參數錯誤')
        return False
    elif ErrCode == PTT.ErrorCode.NoPermission:
        PTTBot.Log('使用文章編號: 無發文權限')
        return False
    else:
        PTTBot.Log('使用文章編號: 推文失敗')
        return False

    for i in range(3):
        ErrCode = PTTBot.push('Test', PTT.PushType.Push, TestString, PostIndex=NewestIndex)
        if ErrCode == PTT.ErrorCode.Success:
            PTTBot.Log('使用文章編號: 推文成功')
        elif ErrCode == PTT.ErrorCode.ErrorInput:
            PTTBot.Log('使用文章編號: 參數錯誤')
            return False
        elif ErrCode == PTT.ErrorCode.NoPermission:
            PTTBot.Log('使用文章編號: 無發文權限')
            return False
        else:
            PTTBot.Log('使用文章編號: 推文失敗')
            return False
def MailDemo():
    
    # 這個範例是如何寄信給某鄉民

    # 第一個參數是你想寄信的鄉民 ID
    # 第二個參數是信件標題
    # 第三個參數是信件內容
    # 第四個參數是簽名檔選擇 0 不加簽名檔
    Content = ''

    for i in range(3):
        Content += '測試行 ' + str(i) + '\r'

    for i in range(1):
        ErrCode = PTTBot.mail(ID, '自動寄信測試標題', '自動測試 如有誤寄打擾 抱歉QQ\r' + Content, 0)
        if ErrCode == PTT.ErrorCode.Success:
            PTTBot.Log('寄信給 ' + ID + ' 成功')
        else:
            PTTBot.Log('寄信給 ' + ID + ' 失敗')
def GiveMoneyDemo():

    # 這個範例是如何送P幣給某鄉民

    # 第一個參數是你想送錢的鄉民 ID
    # 第二個參數是你想給予多少P幣
    # 第三個參數是你自己的密碼
    
    WhoAreUwantToGiveMoney = 'CodingMan'
    try:
        PTTBot.Log('偵測到前景執行使用編碼: ' + sys.stdin.encoding)
        Donate = input('請問願意贊助作者 10 P幣嗎？[Y/n] ').lower()
    except Exception:
        # 被背景執行了..邊緣程式沒資格問要不要贊助..
        # 反正..從來沒收到過贊助，角落就是我的舒適圈!!! 嗚嗚嗚
        pass
        return

    if Donate == 'y' or Donate == '':
        ErrCode = PTTBot.giveMoney(WhoAreUwantToGiveMoney, 10, Password)
        
        if ErrCode == PTT.ErrorCode.Success:
            PTTBot.Log('送P幣給 ' + WhoAreUwantToGiveMoney + ' 成功')
        else:
            PTTBot.Log('送P幣給 ' + WhoAreUwantToGiveMoney + ' 失敗')
    else:
        PTTBot.Log('贊助又被拒絕了..可..可惡')
def GetTimeDemo():

    #這個範例是取得PTT的時間，如果有需要跟 PTT 對時的需求，可以使用
        
    for i in range(3):
        ErrCode, Time = PTTBot.getTime()
        if ErrCode != PTT.ErrorCode.Success:
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
    
    with codecs.open("CrawlBoardResult.txt", "a", "utf-8") as ResultFile:
        ResultFile.write(Post.getTitle() + '\n')

    # PTTBot.Log(Post.getTitle())
    
def CrawlBoardDemo():
    
    # 範例是爬最新的一百篇文章
    # 如果想要取得所有文章可省略編號參數
    # PTTBot.crawlBoard('Wanted', PostHandler)
    # 這樣就會全部文章都會爬下來

    ErrCode, NewestIndex = PTTBot.getNewestIndex(Board='Wanted')
    if ErrCode == PTT.ErrorCode.Success:
        PTTBot.Log('取得 ' + 'Wanted' + ' 板最新文章編號成功: ' + str(NewestIndex))
    else:
        PTTBot.Log('取得 ' + 'Wanted' + ' 板最新文章編號失敗')
        return False    
    
    ErrCode, SuccessCount, DeleteCount = PTTBot.crawlBoard('Wanted', PostHandler, StartIndex=NewestIndex - 499, EndIndex=NewestIndex)
    if ErrCode == PTT.ErrorCode.Success:
        PTTBot.Log('爬行成功共 ' + str(SuccessCount) + ' 篇文章 共有 ' + str(DeleteCount) + ' 篇文章被刪除')
        
def GetUserDemo():
    
    # 範例是追蹤特定 ID 的情況
    # 此API可以追蹤某 ID 的動態
    
    # 使用者資訊資料結構可參考如下
    
    ################## 使用者資訊 User information ##################
    # getID                     ID
    # getMoney                  使用者經濟狀況
    # getLoginTime              登入次數
    # getLegalPost              有效文章數
    # getIllegalPost            退文數
    # getState                  目前動態
    # getMail                   信箱狀態
    # getLastLogin              最後登入時間
    # getLastIP                 上次故鄉
    # getFiveChess              五子棋戰績
    # getChess                  象棋戰績
    
    for IDs in [ID, 'FakeID_____']:
        
        PTTBot.Log('---------------------------')
        PTTBot.Log('Start query: ' + IDs)
        ErrCode, UserInfo = PTTBot.getUser(IDs)
        if ErrCode == PTT.ErrorCode.NoUser:
            PTTBot.Log('沒有此使用者')
            continue
        elif ErrCode != PTT.ErrorCode.Success:
            PTTBot.Log('getUserInfo fail error code: ' + str(ErrCode))
            continue
        
        PTTBot.Log('使用者ID: ' + UserInfo.getID())
        PTTBot.Log('使用者經濟狀況: ' + str(UserInfo.getMoney()))
        PTTBot.Log('登入次數: ' + str(UserInfo.getLoginTime()))
        PTTBot.Log('有效文章數: ' + str(UserInfo.getLegalPost()))
        PTTBot.Log('退文文章數: ' + str(UserInfo.getIllegalPost()))
        PTTBot.Log('目前動態: ' + UserInfo.getState() + '!')
        PTTBot.Log('信箱狀態: ' + UserInfo.getMail() + '!')
        PTTBot.Log('最後登入時間: ' + UserInfo.getLastLogin() + '!')
        PTTBot.Log('上次故鄉: ' + UserInfo.getLastIP() + '!')
        PTTBot.Log('五子棋戰績: ' + str(UserInfo.getFiveChess()[0]) + ' 勝 ' + str(UserInfo.getFiveChess()[1]) + ' 敗 ' + str(UserInfo.getFiveChess()[2]) + ' 和')
        PTTBot.Log('象棋戰績:' + str(UserInfo.getChess()[0]) + ' 勝 ' + str(UserInfo.getChess()[1]) + ' 敗 ' + str(UserInfo.getChess()[2]) + ' 和')

def ReplyPostDemo():
    
    #此範例是因應回文的需求
    #此API可以用三種方式回文 回文至板上 信箱 或者皆是

    # 第一個參數是版面
    # 第二個參數是回文內容
    # 第三個參數是回文種類

    ################## 回文種類 ReplyPost information ##################
    # PTT.ReplyPostType.Board               回文至板上
    # PTT.ReplyPostType.Mail                回文至信箱
    # PTT.ReplyPostType.Board_Mail          回文至信箱與板上
     
    # 回傳 錯誤碼

    # ErrCode = PTTBot.post('Test', '自動回文測試文章', '標準測試流程，如有打擾請告知。\r\n\r\n使用PTT Library 測試\r\n\r\nhttps://goo.gl/5hdAqu', 1, 0)
    # if ErrCode == PTT.ErrorCode.Success:
    #     PTTBot.Log('在 Test 板發文成功')
    # elif ErrCode == PTT.ErrorCode.NoPermission:
    #     PTTBot.Log('發文權限不足')
    # else:
    #     PTTBot.Log('在 Test 板發文失敗')
    
    ErrCode, NewestIndex = PTTBot.getNewestIndex(Board='Test')
    if ErrCode == PTT.ErrorCode.Success:
        PTTBot.Log('取得 ' + 'Test' + ' 板最新文章編號成功: ' + str(NewestIndex))
    else:
        PTTBot.Log('取得 ' + 'Test' + ' 板最新文章編號失敗')
        return False

    ErrCode = PTTBot.replyPost('Test', '回文測試 回文至板上', PTT.ReplyPostType.Board, Index=NewestIndex)
    if ErrCode == PTT.ErrorCode.Success:
        PTTBot.Log('在 Test 回文至板上成功!')
    else:
        PTTBot.Log('在 Test 回文至板上失敗 ' + str(ErrCode))
    
    ErrCode = PTTBot.replyPost('Test', '回文測試 回文至信箱', PTT.ReplyPostType.Mail, Index=NewestIndex)
    if ErrCode == PTT.ErrorCode.Success:
        PTTBot.Log('在 Test 回文至信箱成功!')
    else:
        PTTBot.Log('在 Test 回文至信箱失敗 ' + str(ErrCode))
        
    ErrCode = PTTBot.replyPost('Test', '回文測試 回文至版上與信箱',PTT.ReplyPostType.Board_Mail, Index=NewestIndex)
    if ErrCode == PTT.ErrorCode.Success:
        PTTBot.Log('在 Test 回文至版上與信箱成功!')
    else:
        PTTBot.Log('在 Test 回文至版上與信箱失敗 ' + str(ErrCode))

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

    ErrCode, NewestMailIndex = PTTBot.getNewestIndex()
    if ErrCode == PTT.ErrorCode.Success:
        PTTBot.Log('取得最新信件編號成功')
    else:
        PTTBot.Log('取得最新信件編號失敗 錯誤碼: ' + str(ErrCode))
        return

    PTTBot.Log('最新信件編號: ' + str(NewestMailIndex))

    if NewestMailIndex > 3:
        MailStartIndex = NewestMailIndex - 3
    else:
        MailStartIndex = 1

    for i in range(MailStartIndex, NewestMailIndex):
        MailIndex = i + 1
        ErrCode, Mail = PTTBot.getMail(MailIndex)
        if ErrCode == PTT.ErrorCode.Success:
            PTTBot.Log('取得編號 ' + str(MailIndex) + ' 信件成功')

            PTTBot.Log('信件作者: ' + Mail.getAuthor())
            PTTBot.Log('信件標題: ' + Mail.getTitle())
            PTTBot.Log('信件日期: ' + Mail.getDate())
            # PTTBot.Log('信件內文: ' + Mail.getContent())
            PTTBot.Log('信件IP: ' + Mail.getIP())

            PTTBot.Log('=' * 30)

        else:
            PTTBot.Log('取得編號 ' + str(MailIndex) + ' 信件失敗 錯誤碼: ' + str(ErrCode))
            return
    return 
def ChangePasswordDemo():
    # 用來更改密碼的 api
    # 輸入原密碼 與 新密碼 即可自動更改你的密碼
    # 回傳 錯誤碼
    
    # 範例為示範 所以新舊密碼皆設定為原密碼
    
    ErrCode = PTTBot.changePassword(Password, Password)
    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('changePassword 失敗 錯誤碼:' + str(ErrCode))
    else:
        PTTBot.Log('changePassword 成功')
    return 
def ThrowWaterBallDemo():
    
    # 用來丟水球的 api
    # 輸入你要丟水球的鄉民 ID 與內容，即可騷擾!
    # 回傳 錯誤碼
    
    # 請不要拿來狂丟我 謝謝

    ErrCode = PTTBot.throwWaterBall('CodingMan', 'PTT Library 丟水球測試')
    if ErrCode == PTT.ErrorCode.Success:
        PTTBot.Log('丟水球成功!')
    else:
        PTTBot.Log('丟水球失敗! 錯誤碼: ' + str(ErrCode))
    return
def DelPostDemo():
    
    # 刪除文章的 API
    # 輸入版面 與文章編號或者代碼
    # 即可幫你快速刪文!
    
    # 注意: 版主使用此工具請小心

    Board = 'Test'

    for i in range(3):

        ErrCode = PTTBot.post('Test', 'Python 機器人自動刪文測試 ' + str(i), '自動刪文測試，如有打擾請告知。\r\n\r\n使用PTT Library 測試\r\n\r\nhttps://goo.gl/5hdAqu', 1, 0)
        if ErrCode == PTT.ErrorCode.Success:
            PTTBot.Log('在 ' + Board + ' 板發文成功')
        elif ErrCode == PTT.ErrorCode.NoPermission:
            PTTBot.Log('發文權限不足')
        else:
            PTTBot.Log('在 ' + Board + ' 板發文失敗')

    ErrCode, NewestIndex = PTTBot.getNewestIndex(Board=Board)
    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('取得 ' + Board + ' 板最新文章編號失敗')
        return False
    
    if NewestIndex == -1:
        PTTBot.Log('取得 ' + Board + ' 板最新文章編號失敗')
        return False
    
    PTTBot.Log('取得 ' + Board + ' 板最新文章編號: ' + str(NewestIndex))

    for i in range(5):
        DelIndex = NewestIndex - i
        ErrCode = PTTBot.delPost(Board, PostIndex=DelIndex)
        if ErrCode == PTT.ErrorCode.Success:
            PTTBot.Log('在 ' + Board + ' 板刪除 ' + str(DelIndex) + '成功')
        elif ErrCode == PTT.ErrorCode.NoPermission:
            PTTBot.Log('刪文權限不足')
        else:
            PTTBot.Log('在 ' + Board + ' 板刪除 ' + str(DelIndex) + '失敗')

    return 
def WaterBallHandler(WaterBall):
    
    # 不建議在頻繁呼叫其他 API 的情況下，試圖接住水球

    print('接到水球惹!!')
    print('WaterBallAuthor: =' + WaterBall.getAuthor() + '=')
    print('WaterBallContent: =' + WaterBall.getContent() + '=')

    PTTBot.throwWaterBall(WaterBall.getAuthor(), WaterBall.getAuthor() + ' 我接住你的水球了!')

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

    # PTTBot = PTT.Library(ID, Password, kickOtherLogin=False, _LogLevel=PTT.LogLevel.DEBUG)
    # PTTBot = PTT.Library(ID, Password, WaterBallHandler=WaterBallHandler)
    PTTBot = PTT.Library(ID, Password, _LogLevel=PTT.LogLevel.DEBUG)

    ErrCode = PTTBot.login()
    if ErrCode != PTT.ErrorCode.Success:
        PTTBot.Log('登入失敗')
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
        pass
    except:
        pass
    # 請養成登出好習慣
    PTTBot.logout()