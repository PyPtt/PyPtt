# PyPtt 完全使用手冊

> 註1:此手冊僅支援 [![Package Version](https://img.shields.io/pypi/v/PyPtt.svg)](https://pypi.python.org/pypi/PyPtt)，如果你使用的版本為 0.8.x，請參考 [[使用手冊 0.8]](https://hackmd.io/@CodingMan/PTTLibraryManual_0_8)  
> 註2:有出現在本手冊中的使用者或文章，如果不想出現，很抱歉請馬上告知我

有任何使用上的問題都可以直接問我 [![chatroom icon](https://patrolavia.github.io/telegram-badge/chat.png)](https://t.me/PyPtt)

---

## 取得

###### 安裝

```batch=
pip install PyPtt
```

###### 更新

```batch=
pip install PyPtt --upgrade
```

###### 安裝特定版本

```batch=
pip install PyPtt==VERSION
```
---

## 例外

這裡列出了你可能遭遇到的例外

###### PTT.exceptions.LoginError
    登入失敗
###### PTT.exceptions.NoSuchUser
    無此使用者
###### PTT.exceptions.RequireLogin
    使用此 API 前請先登入
###### PTT.exceptions.NoPermission
    無權限，你可能被水桶或者帳號資格不符
###### PTT.exceptions.NoFastPush
    此看板不支援快速推文，推文 API 會幫你重推
###### PTT.exceptions.UserOffline
    使用者離線
###### PTT.exceptions.ParseError
    此畫面解析錯誤，導致原因可能為傳輸過程中遺失訊息
###### PTT.exceptions.NoMoney
    沒錢
###### PTT.exceptions.MoneyTooFew
    錢太少
###### PTT.exceptions.NoSuchBoard
    沒有這個看板
###### PTT.exceptions.ConnectionClosed
    Since 0.8.13
    連線已經被關閉
###### PTT.exceptions.UnregisteredUser
    Since 0.8.13
    尚未註冊使用者或被退註使用者，因權限受限將無法使用全部功能
###### PTT.exceptions.MultiThreadOperated
    Since 0.8.13
    一個 PyPtt 物件只能被同一個 thread 操作
    如果有第二個 thread 使用就會跳出此例外
###### PTT.exceptions.WrongIDorPassword
    Since 0.8.14
    帳號密碼錯誤
###### PTT.exceptions.LoginTooOften
    Since 0.8.14
    登入太頻繁
###### PTT.exceptions.UseTooManyResources
    Since 0.8.15
    使用過多 PTT 資源，請稍等一段時間並增加操作之間的時間間隔
###### PTT.exceptions.HostNotSupport
    Since 0.8.25
    批踢踢萬或批踢踢兔不支援這個操作
###### PTT.exceptions.NoPush
    Since 0.8.25
    禁止推文
###### PTT.exceptions.NoResponse
    Since 0.8.26
    禁止回應
###### PTT.exceptions.NeedModeratorPermission
    Since 0.8.26
    需要板主權限
###### PTT.exceptions.NoSuchPost
    Since 0.8.27
    沒有該文章
###### PTT.exceptions.CanNotUseSearchPostCode
    Since 0.9.1
    此狀態下無法使用搜尋文章代碼(AID)功能
###### PTT.exceptions.UserHasPreviouslyBeenBanned
    Since 0.9.1
    使用者之前已被禁言
###### PTT.exceptions.WrongPassword
    Since 0.9.16
    密碼錯誤
###### PTT.exceptions.NoSearchResult
    Since 0.9.17
    沒有搜尋結果

---

## API

### 初始設定

> PyPtt 並不支援兩個以上的 thread 同時操作一個物件  
> 如果有需求，請啟動新 thread 後，所有操作都在同一個 thread

以下是初始化物件的方式，如果沒有特別需求，這樣就可以取得物件了

```python=
from PyPtt import PTT
ptt_bot = PTT.API()
```

如果有改變語言顯示的需求，目前有支援英文與繁體中文

```python=
from PyPtt import PTT
ptt_bot = PTT.API(
    # (預設值) Chinese
    # language=PTT.i18n.language.CHINESE,
    language=PTT.i18n.language.ENGLISH,
)
```

也可以修改 Log 等級方便回報錯誤

```python=
from PyPtt import PTT
ptt_bot = PTT.API(
    # (預設值) INFO
    # log_level=PTT.log.level.INFO,
    # log_level=PTT.log.level.DEBUG,
    log_level=PTT.log.level.TRACE,
)
```

如果你的網路環境比較慢(例如海外)，常常不小心就 timeout，也有參數可以調整  
Since 0.9.1
```python=
from PyPtt import PTT
ptt_bot = PTT.API(
    # 預設 3 秒後判定此畫面沒有可辨識的目標
    screen_time_out=5,
    # 預設 10 秒後判定此畫面沒有可辨識的目標
    # 適用於需要特別等待的情況，例如: 剔除其他登入、發文等等
    # 建議不要低於 10 秒，剔除其他登入最長可能會花費約 6 ~ 7 秒
    screen_long_timeout=15,
    # 預設 60 秒後判定此畫面沒有可辨識的目標
    # 適用於貼文等待的情況，建議不要低於 60 秒
    screen_post_timeout=120,
)
```

當然如果你有需要將 log 輸出成檔案或者其他需要處理 log 的需求  
你可以加入 log handler 就可以捕捉到所有輸出  
Since 0.8.11

```python=
from PyPtt import PTT
def handler(msg):
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

ptt_bot = PTT.API(
    log_handler=handler
)
```

當然 PyPtt 也支援批踢踢兔與本機。  
批踢踢兔 Since 0.8.25  
本機 Since 0.9.1

```python=
from PyPtt import PTT
ptt2_bot = PTT.API(
    # (預設值) PTT1
    # host=PTT.data_type.host_type.PTT1,
    # host=PTT.data_type.host_type.PTT2,
    # host=PTT.data_type.host_type.LOCALHOST,
    host=PTT.data_type.host_type.PTT2
)
```

如果有 telnet 的需求，可以切換連線模式  
如果需要更換 port 也是支援的  
值得注意的是，根據測試結果無加密的 telnet 比 websocket 慢  
Since 0.9.1

```python=
from PyPtt import PTT
ptt_bot = PTT.API(
    # (預設值) WEBSOCKET
    # connect_mode=PTT.connect_core.connect_mode.WEBSOCKET,
    connect_mode=PTT.connect_core.connect_mode.TELNET,
    # (預設值) 23
    port=8888
)
```

---
    
### 登入登出

以下就是登入登出範例  
登入完成，你可以查看一些變數來了解帳號的狀態

```python=
import sys
from PyPtt import PTT

ptt_bot = PTT.API()
try:
    ptt_bot.login(ptt_id, password)
except PTT.exceptions.LoginError:
    ptt_bot.log('登入失敗')
    sys.exit()
except PTT.exceptions.WrongIDorPassword:
    ptt_bot.log('帳號密碼錯誤')
    sys.exit()
except PTT.exceptions.LoginTooOften:
    ptt_bot.log('請稍等一下再登入')
    sys.exit()
ptt_bot.log('登入成功')

if ptt_bot.unregistered_user:
    print('未註冊使用者')

    if ptt_bot.process_picks != 0:
        print(f'註冊單處理順位 {ptt_bot.process_picks}')

if ptt_bot.registered_user:
    print('已註冊使用者')

# call ptt_bot other api

ptt_bot.logout()
```
執行結果

![](https://i.imgur.com/wfaf8Bk.gif)

如果你的登入需要剔除其他的登入  
那可以將 kick_other_login=True 加入 login 參數

```python=
import sys
from PyPtt import PTT

ptt_bot = PTT.API()
try:
    ptt_bot.login(
        ptt_id,
        password,
        kick_other_login=True
    )
except PTT.exceptions.LoginError:
    ptt_bot.log('登入失敗')
    sys.exit()
except PTT.exceptions.WrongIDorPassword:
    ptt_bot.log('帳號密碼錯誤')
    sys.exit()
except PTT.exceptions.LoginTooOften:
    ptt_bot.log('請稍等一下再登入')
    sys.exit()
ptt_bot.log('登入成功')

# call ptt_bot other api

ptt_bot.logout()
```

---

### 取得特定文章

以下便是最簡單的取得特定文章的範例  
註: Python 板第 7486 篇文章
```python=
from PyPtt import PTT

post_info = ptt_bot.get_post(
    'Python',
    post_index=7486
)
```

或者用 AID 也可以的

```python=
import sys
from PyPtt import PTT

post_info = ptt_bot.get_post(
    'Python',
    post_aid='1TJH_XY0'
)

# 從以上兩個範例可以看到 get_post 回傳了 post_info
# 這裡面包含了文章所有屬性
# 這可以從以下範例明白怎麼取出每個屬性

if post_info is None:
    print('post_info is None')
    sys.exit()

if post_info.delete_status != PTT.data_type.post_delete_status.NOT_DELETED:
    if post_info.delete_status == PTT.data_type.post_delete_status.MODERATOR:
        print(f'[板主刪除][{post_info.author}]')
    elif post_info.delete_status == PTT.data_type.post_delete_status.AUTHOR:
        print(f'[作者刪除][{post_info.author}]')
    elif post_info.delete_status == PTT.data_type.post_delete_status.UNKNOWN:
        print(f'[不明刪除]')
    return

if post_info.is_lock:
    print('[鎖文]')
    sys.exit()

if not post_info.pass_format_check:
    print('[不合格式]')
    sys.exit()

print('Board: ' + post_info.board)
print('AID: ' + post_info.aid)
print('index:' + str(post_info.index))
print('Author: ' + post_info.author)
print('Date: ' + post_info.date)
print('Title: ' + post_info.title)
print('content: ' + post_info.content)
print('Money: ' + str(post_info.money))
print('URL: ' + post_info.web_url)
print('IP: ' + post_info.ip)
# 在文章列表上的日期
print('List Date: ' + post_info.list_date)
print('地區: ' + post_info.location)
# Since 0.8.19
print('文章推文數: ' + post_info.push_number)

if post_info.unconfirmed:
    # Since 0.8.30
    print('待證實文章')

push_count = 0
boo_count = 0
arrow_count = 0

for push_info in post_info.push_list:
    if push_info.type == PTT.data_type.push_type.PUSH:
        push_type = '推'
        push_count += 1
    if push_info.type == PTT.data_type.push_type.BOO:
        push_type = '噓'
        boo_count += 1
    if push_info.type == PTT.data_type.push_type.ARROW:
        push_type = '箭頭'
        arrow_count += 1

    author = push_info.author
    content = push_info.content

    buffer = f'{author} 給了一個{push_type} 說 {content}'
    if push_info.ip is not None:
        buffer += f'來自 {push_info.ip}'
    buffer += f'時間是 {push_info.time}'
    print(buffer)

print(f'Total {push_count} Pushs {boo_count} Boo {arrow_count} Arrow')
```
執行結果

![](https://i.imgur.com/M6XGFzD.png)

> 備註: 因為根據 PTT 原始碼推文計數擁有**神奇演算法**，在文章前面顯示的推噓文統計
> 可能是不準確的，可能會與直接計算內部推噓文結果不同，  
> 所以在使用推文條件搜尋的情況下，可能導致結果不夠準確

當然如果需要加條件搜尋也是可以的  
只是我們需要知道加了搜尋條件之後的最大編號是多少  
請看以下範例

```python=
test_list = [
    ('Python', PTT.data_type.post_search_type.KEYWORD, '[公告]')
]

for (test_board, search_type, condition) in test_list:
    index = ptt_bot.get_newest_index(
        PTT.data_type.index_type.BBS,
        test_board,
        search_type=search_type,
        search_condition=condition,
    )
    print(f'{test_board} 最新文章編號 {index}')

    post = ptt_bot.get_post(
        test_board,
        post_index=index,
        search_type=search_type,
        search_condition=condition,
    )

    print('標題:')
    print(post.title)
    print('內文:')
    print(post.content)
    print('=' * 50)
```

執行結果

![](https://i.imgur.com/jF63MGp.png)

如果只需要對文章按 Q 的資訊  
Since 0.8.16

![](https://i.imgur.com/TdP5wL4.png)


你可以啟用 query 模式，這樣就不會進入文章解析內文、推文、IP與地點等等  
可以提升效能

```python=
post_info = ptt_bot.get_post(
    'Python',
    post_aid='1TJH_XY0',
    query=True,
)
```

---

### 取得最新文章編號

當你想要取得的文章編號範圍包含最新文章的時候  
你就會需要這隻 API 來取得最新編號是多少

```python=
test_board_list = [
    'Wanted',
    'Gossiping',
    'Test',
    'Stock',
    'movie',
]

for test_board in test_board_list:
    index = ptt_bot.get_newest_index(
        PTT.data_type.index_type.BBS,
        board=test_board
    )
    print(f'{test_board} 最新文章編號 {index}')
```
當然如果下了搜尋條件，編號也會跟著不同，這時候只需要把搜尋條件塞進去即可

```python=
test_list = [
    ('Stock', PTT.data_type.post_search_type.KEYWORD, '盤中閒聊'),
    ('Baseball', PTT.data_type.post_search_type.PUSH, '20')
]

for (test_board, search_type, condition) in test_list:
    newest_index = ptt_bot.get_newest_index(
        PTT.data_type.index_type.BBS,
        test_board,
        search_type=search_type,
        search_condition=condition,
    )
    print(f'{test_board} 最新文章編號 {newest_index}')
```

---

### 取得大範圍文章

以下是大範圍爬文範例

[效能比較表](https://hackmd.io/@CodingMan/crawlerbenchmark)

文章資料結構(post_info)可參考，[取得特定文章](#取得特定文章)

```python=
def crawl_handler(post_info):

    if post_info.delete_status != PTT.data_type.post_delete_status.NOT_DELETED:
        if post_info.delete_status == PTT.data_type.post_delete_status.MODERATOR:
            print(f'[板主刪除][{post_info.author}]')
        elif post_info.delete_status == PTT.data_type.post_delete_status.AUTHOR:
            print(f'[作者刪除][{post_info.author}]')
        elif post_info.delete_status == PTT.data_type.post_delete_status.UNKNOWN:
            print(f'[不明刪除]')
        return

    print(f'[{post_info.aid}][{post_info.title}]')


test_board = 'Gossiping'
test_range = 1000

newest_index = ptt_bot.get_newest_index(
    PTT.data_type.index_type.BBS,
    board=test_board
)
start_index = newest_index - test_range + 1

print(f'預備爬行 {test_board} 編號 {start_index} ~ {newest_index} 文章')

# start_aid = ptt_bot.get_post_index(test_board, start_index)
# end_aid = ptt_bot.get_post_index(test_board, newest_index)

error_post_list, del_post_list = ptt_bot.crawl_board(
    PTT.data_type.crawl_type.BBS,
    crawl_handler,
    test_board,
    # 使用 index 來標示文章範圍
    start_index=start_index,
    end_index=newest_index,
    # 使用 aid 來標示文章範圍
    # Since 0.8.27
    # start_aid=start_aid,
    # end_aid=end_aid,
    # index 與 aid 標示方式擇一即可
)

if len(error_post_list) > 0:
    print('格式錯誤文章: \n' + '\n'.join(str(x) for x in error_post_list))
else:
    print('沒有偵測到格式錯誤文章')

if len(del_post_list) > 0:
    print(f'共有 {len(del_post_list)} 篇文章被刪除')
```

執行結果

![](https://i.imgur.com/BO3QLf2.png)


> 備註: 因為 PTT 推文計數有三分鐘的時間間隔，所以在使用推文條件搜尋的情況下
> 可能導致結果不夠即時  
> 在有下搜尋條件的情況下，無法使用 AID 來標記爬文範圍

當然我們也可以像 get_post 那樣加入搜尋條件來爬我們的結果

```python=
def show_condition(board, search_type, condition):
    if search_type == PTT.data_type.post_search_type.KEYWORD:
        condition_type = '關鍵字'
    if search_type == PTT.data_type.post_search_type.AUTHOR:
        condition_type = '作者'
    if search_type == PTT.data_type.post_search_type.PUSH:
        condition_type = '推文數'
    if search_type == PTT.data_type.post_search_type.MARK:
        condition_type = '標記'
    if search_type == PTT.data_type.post_search_type.MONEY:
        condition_type = '稿酬'

    print(f'{board} 使用 {condition_type} 搜尋 {condition}')


test_range = 10

test_list = [
    ('Wanted', PTT.data_type.post_search_type.KEYWORD, '[公告]'),
    ('Wanted', PTT.data_type.post_search_type.AUTHOR, 'gogin'),
    ('Wanted', PTT.data_type.post_search_type.PUSH, '10'),
    ('Wanted', PTT.data_type.post_search_type.MARK, 'm'),
    ('Wanted', PTT.data_type.post_search_type.MONEY, '5'),
    ('Gossiping', PTT.data_type.post_search_type.KEYWORD, '[公告]'),
    ('Gossiping', PTT.data_type.post_search_type.AUTHOR, 'ReDmango'),
    ('Gossiping', PTT.data_type.post_search_type.PUSH, '10'),
    ('Gossiping', PTT.data_type.post_search_type.MARK, 'm'),
    ('Gossiping', PTT.data_type.post_search_type.MONEY, '5'),
    ('Gossiping', PTT.data_type.post_search_type.PUSH, '-100'),
]

for (test_board, search_type, condition) in test_list:
    show_condition(test_board, search_type, condition)
    newest_index = ptt_bot.get_newest_index(
        PTT.data_type.index_type.BBS,
        test_board,
        search_type=search_type,
        search_condition=condition,
    )
    print(f'{test_board} 最新文章編號 {newest_index}')

    start_index = newest_index - test_range + 1
    # 有下條件的情況下，無法使用 aid 來標記範圍
    error_post_list, del_post_list = ptt_bot.crawl_board(
        PTT.data_type.crawl_type.BBS,
        crawlHandler,
        test_board,
        start_index=start_index,
        end_index=newest_index,
        search_type=search_type,
        search_condition=condition,
    )

    print('=' * 50)
```

如果只需要對文章按 Q 的資訊  
Since 0.8.16

![](https://i.imgur.com/p4kt1JC.png)

你可以啟用 Query 模式，這樣就不會點進去解析內文、推文跟 IP 等等  
可以加快一些速度，並減少出錯機率

```python=
error_post_list, del_post_list = ptt_bot.crawl_board(
    PTT.data_type.crawl_type.BBS,
    crawlHandler,
    'Gossiping',
    start_index=1,
    end_index=100,
    query=True,  # Optional
)
```

---
### 貼文推文

以下範例是在測試板貼文的範例

```python=
content = '''
此為 PyPtt 貼文測試內容，如有打擾請告知。
github: https://tinyurl.com/umqff3v

開發手冊: https://hackmd.io/@CodingMan/PTTLibraryManual
'''
content = content.replace('\n', '\r\n')

for _ in range(3):
    ptt_bot.post(
        # 看板
        'Test',
        # 標題
        'PyPtt 程式貼文測試',
        # 內文
        content,
        # 標題分類
        1,
        # 簽名檔
        0
    )
```

以下則是推文範例

```python+=20
test_board = 'Test'
test_index = 398
index = ptt_bot.get_newest_index(PTT.data_type.index_type.BBS, board=test_board)
print(f'{test_board} 最新文章編號 {index}')

content = '''
What is Ptt?
批踢踢 (Ptt) 是以學術性質為目的，提供各專業學生實習的平台，而以電子佈告欄系統 (BBS, Bulletin Board System) 為主的一系列服務。
期許在網際網路上建立起一個快速、即時、平等、免費，開放且自由的言論空間。批踢踢實業坊同時承諾永久學術中立，絕不商業化、絕不營利。
'''
ptt_bot.push(test_board, PTT.data_type.push_type.PUSH, content, post_index=test_index)
```
執行結果

![](https://i.imgur.com/EhJlJ2l.png)

![](https://i.imgur.com/bd1Vjjf.png)

---

### 查詢使用者

以下是查詢使用者範例  
如果查無使用者則會丟出 PTT.exceptions.NoSuchUser 例外

```python=
try:
    user = ptt_bot.get_user('CodingMan')
    if user is None:
        sys.exit()

    ptt_bot.log('使用者ID: ' + user.id)
    ptt_bot.log('使用者經濟狀況: ' + str(user.money))
    ptt_bot.log('登入次數: ' + str(user.login_time))
    ptt_bot.log('有效文章數: ' + str(user.legal_post))
    ptt_bot.log('退文文章數: ' + str(user.illegal_post))
    ptt_bot.log('目前動態: ' + user.status)
    ptt_bot.log('信箱狀態: ' + user.mail_status)
    ptt_bot.log('最後登入時間: ' + user.last_login)
    ptt_bot.log('上次故鄉: ' + user.last_ip)
    ptt_bot.log('五子棋戰績: ' + user.five_chess)
    ptt_bot.log('象棋戰績:' + user.chess)
    ptt_bot.log('簽名檔:' + user.signature_file)

except PTT.exceptions.NoSuchUser:
    print('無此使用者')
```

執行結果

![](https://i.imgur.com/wz4Zcy6.png)


---

### 呼叫器

在這裡將會展示取得現在呼叫器狀態後  
隨機地去設定除了現在以外的一種呼叫器狀態

```python=
def show_call_status(call_status):
    if call_status == PTT.data_type.call_status.ON:
        print('呼叫器狀態[打開]')
    elif call_status == PTT.data_type.call_status.OFF:
        print('呼叫器狀態[關閉]')
    elif call_status == PTT.data_type.call_status.UNPLUG:
        print('呼叫器狀態[拔掉]')
    elif call_status == PTT.data_type.call_status.WATERPROOF:
        print('呼叫器狀態[防水]')
    elif call_status == PTT.data_type.call_status.FRIEND:
        print('呼叫器狀態[朋友]')
    else:
        print(f'Unknown call_status: {call_status}')


call_status = ptt_bot.get_call_status()
show_call_status(call_status)

TestQueue = [x for x in range(
    PTT.data_type.call_status.min_value, PTT.data_type.call_status.max_value + 1
)]
random.shuffle(TestQueue)
TestQueue.remove(call_status)

ptt_bot.set_call_status(TestQueue[0])
call_status = ptt_bot.get_call_status()
show_call_status(call_status)
```

執行結果

![](https://i.imgur.com/C0qco4O.png)

---

### 水球

首先展示丟水球的範例  
在這裡則可以看到有兩種例外

無此使用者 PTT.exceptions.NoSuchUser  
使用者離線 PTT.exceptions.UserOffline

```python=
ptt_id = 'SampleUser'
content = '水球測試 :D'
try:
    ptt_bot.throw_waterball(ptt_id, content)
except PTT.exceptions.NoSuchUser:
    print('無此使用者')
except PTT.exceptions.UserOffline:
    print('使用者離線')
```

接下來是接水球範例  
建議如果要穩定收到水球請參考 [呼叫器](#呼叫器) 先將呼叫器切換成關閉

```python=
import sys
import time

# 存取歷史水球可以有三個後續動作可以選
# 不做任何事
# OperateType = PTT.data_type.waterball_operate_type.NOTHING
# 存入信箱
# OperateType = PTT.data_type.waterball_operate_type.MAIL
# 清除
operate_type = PTT.data_type.waterball_operate_type.CLEAR

while True:
    waterball_list = ptt_bot.get_waterball(operate_type)
    if waterball_list is None:
        time.sleep(1)
        continue

    for waterball_info in waterball_list:
        if waterball_info.type == PTT.data_type.waterball_type.CATCH:
            # 收到水球
            temp = '★' + waterball_info.target + ' '
        elif waterball_info.type == PTT.data_type.waterball_type.SEND:
            # 你丟出去的水球紀錄
            temp = 'To ' + waterball_info.target + ': '
        temp += waterball_info.content + ' [' + waterball_info.date + ']'
        print(temp)
```

---

### 給 P 幣

以下是給 P 幣的範例

```python=
ptt_bot.give_money('CodingMan', 100)
```

---

### 寄信 取得信件 刪除信件

以下是寄信範例  
如果對象不存在則會丟出 PTT.exceptions.NoSuchUser 例外

```python=
ptt_id = 'CodingMan'
content = '''如有誤寄，對..對不起
PyPtt 程式寄信測試內容

程式碼: https://github.com/PttCodingMan/PyPtt
'''
content = content.replace('\n', '\r\n')

try:
    ptt_bot.mail(
        # 寄信對象
        ptt_id,
        # 標題
        '程式寄信標題',
        # 內文
        content,
        # 簽名檔
        0
    )
except PTT.exceptions.NoSuchUser:
    print('No Such User')
```

執行結果

![](https://i.imgur.com/749XDXD.png)

![](https://i.imgur.com/V5R24nJ.png)

![](https://i.imgur.com/XubpFRP.png)

如果有取得信件的需求，可以使用 get_mail 這支 API  
因為是根據 index 來取得信件，所以一樣要使用 get_newest_index 來取得最新的信件編號    
範例程式碼是固定取得最新的信件
信件 index 範圍是 1 ~ newest_index  
Since 0.9.8

```python=
newest_index = ptt_bot.get_newest_index(PTT.data_type.index_type.MAIL)
print(f'最新郵件編號 {newest_index}')
mail_info = ptt_bot.get_mail(newest_index)

print(mail_info.origin_mail)    # 原始信件
print(mail_info.author)         # 作者
print(mail_info.title)          # 標題
print(mail_info.date)           # 日期
print(mail_info.content)        # 內文
print(mail_info.ip)             # ip
print(mail_info.location)       # 地區: 舊版本信件則為 None
```

取完信件之後，我們來看看怎麼刪除信件  
範例程式碼是固定刪掉最新的信件  
信件 index 範圍是 1 ~ newest_index  
Since 0.9.8

```python=
newest_index = ptt_bot.get_newest_index(PTT.data_type.index_type.MAIL)
print(f'最新郵件編號 {newest_index}')
ptt_bot.del_mail(newest_index)
```

---

### 偵測是否有新信

此為偵測新信 API，如果大於 1，就是有新信:D
> 註: 如果你的信箱信件處在 1 ~ 20 封信，那會稍微等久一點

```python=
result = ptt_bot.has_new_mail()
if result > 0:
    print(f'You got {result} mail(s)')
else:
    print('No new mail')
```

執行結果

![](https://i.imgur.com/15iTEbM.png)

---

### 取得所有 PTT 看板名稱

Since 0.8.13

```python=
board_list = ptt_bot.get_board_list()
print(f'總共有 {len(board_list)} 個看板')
```

執行結果

![](https://i.imgur.com/mWoxxEA.png)

---

### 取得我的最愛列表

Since 0.8.28

```python=
favourite_board_list = ptt_bot.get_favourite_board()

for board in favourite_board_list:
    # getBoard 板名
    # getType 類別
    # getBoardTitle 板標
    buff = f'[{board.board}][{board.type}][{board.title}]'
    print(buff)
```

執行結果

![](https://i.imgur.com/ynLfYJn.png)

---

### 搜尋網友
以下是搜尋網友功能，輸入部分帳號回傳所有可能  
支援特定頁面範圍，以提升搜尋效能  
Since 0.8.30

```python=
user_list = ptt_bot.search_user(
    'coding',
    # min_page=1,
    # max_page=10
)

print(user_list)
print(len(user_list))
```

執行結果

![](https://i.imgur.com/gce3qy4.png)

---

### 取得時間
以下是取得批踢踢時間功能

```python=
ptt_time = ptt_bot.get_time()
print(ptt_time)
```

---

### 取得看板資訊

以下是取得看板資訊 API  
Since 0.8.32

```python=
if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
    board_info = ptt_bot.get_board_info('Gossiping')
else:
    board_info = ptt_bot.get_board_info('WhoAmI')
print('板名: ', board_info.board)
print('線上人數: ', board_info.online_user)
print('中文敘述: ', board_info.chinese_des)
print('板主: ', board_info.moderators)
print('公開狀態(是否隱形): ', board_info.is_open)
print('隱板時是否可進入十大排行榜: ', board_info.is_into_top_ten_when_hide)
print('是否開放非看板會員發文: ', board_info.can_non_board_members_post)
print('是否開放回應文章: ', board_info.can_reply_post)
print('是否開放自刪文章: ', board_info.can_self_del_post)
print('是否開放推薦文章: ', board_info.can_push_post)
print('是否開放噓文: ', board_info.can_boo_post)
print('是否可以快速連推文章: ', board_info.can_fast_push)
print('推文最低間隔時間: ', board_info.min_interval)
print('推文時是否記錄來源 IP: ', board_info.is_push_record_ip)
print('推文時是否對齊開頭: ', board_info.is_push_aligned)
print('板主是否可刪除部份違規文字: ', board_info.can_moderator_del_illegal_content)
print('轉錄文章是否自動記錄，且是否需要發文權限: ',
      board_info.is_tran_post_auto_recorded_and_require_post_permissions)
print('是否為冷靜模式: ', board_info.is_cool_mode)
print('是否需要滿十八歲才可進入: ', board_info.is_require18)
print('發文與推文限制登入次數需多少次以上: ', board_info.require_login_time)
print('發文與推文限制退文篇數多少篇以下: ', board_info.require_illegal_post)
```

![](https://i.imgur.com/TIR71MY.png)

執行結果

![](https://i.imgur.com/unHbEUp.png)

---

### 回覆文章

以下是回覆文章 API  
Since 0.8.26

```python=
reply_post_index = 313

ptt_bot.reply_post(
    PTT.data_type.reply_type.BOARD,
    'Test',
    '測試回應到板上，如有打擾抱歉',
    post_index=reply_post_index
)

ptt_bot.reply_post(
    PTT.data_type.reply_type.MAIL,
    'Test',
    '測試回應到信箱，如有打擾抱歉',
    post_index=reply_post_index
)

ptt_bot.reply_post(
    PTT.data_type.reply_type.BOARD_MAIL,
    'Test',
    '測試回應到板上還有信箱，如有打擾抱歉',
    post_index=reply_post_index
)
```

---

### 更改密碼

以下是更改密碼 API  
Since 0.9.16

```python=
ptt_bot.change_pw(new_password)
```

---

## 板主專用 API

### 設定板標

如果有定時設定板標的需求，這時候就可以使用 set_board_title  
Since 0.8.26

```python=
from time import strftime

test_board = 'QQboard'

while True:
    time_format = strftime('%H:%M:%S')
    try:
        ptt_bot.set_board_title(
            test_board,
            f'現在時間 {time_format}'
        )
    except PTT.exceptions.ConnectionClosed:
        while True:
            try:
                ptt_bot.login(
                    ptt_id,
                    password
                )
                break
            except PTT.exceptions.LoginError:
                ptt_bot.log('登入失敗')
                time.sleep(1)
            except PTT.exceptions.ConnectError:
                ptt_bot.log('登入失敗')
                time.sleep(1)
    print('已經更新時間 ' + time_format, end='\r')
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print('已經更新時間 ' + time_format)
        ptt_bot.set_board_title(
            test_board,
            f'[{test_board}]'
        )
        print('板標已經恢復')
        break
```

---

### 標記文章

如果板主有標記文章 S or D 的需求，可以參考以下使用方法
Since 0.8.26

```python=
# s 文章
mark_type = PTT.data_type.mark_type.S
# 標記文章
mark_type = PTT.data_type.mark_type.D
# 刪除標記文章
mark_type = PTT.data_type.mark_type.DeleteD
# M 起來
# Since 0.8.27
mark_type = PTT.data_type.mark_type.M
# 待證實文章
# Since 0.8.30
mark_type = PTT.data_type.mark_type.UNCONFIRMED

ptt_bot.mark_post(
    mark_type,
    'YourBoad',
    # AID 與 index 擇一使用
    post_aid='QQaid',
    # Postindex 可搭配 SearchType and SearchCondition 使用
    post_index=10,
    search_type=search_type, # Optional
    search_condition=search_condition # Optional
)
```

---

### 水桶
如果板主想要自動化水桶，當然也是可以的喔!!  
Since 0.8.29

```python=
ptt_bot.bucket(
    # 看板
    'QQBoard',
    # 幾天，請自行轉換成天數
    7,
    # 水桶原因
    'Bucket Reason',
    # 水桶對象
    'CodingMan'
)
```

---

## 疑難排解

### 在 jupyter 使用

因為 jupyter 內部也使用了 asyncio 作為協程管理工具  
會跟 PyPtt 內部的 asyncio 衝突  
所以如果想要在 jypyter 內使用，請在你的程式碼中加入以下程式碼  

安裝

```python=
! pip install nest_asyncio
```
引用
```python=
import nest_asyncio
```
全部引用完之後
```python=
nest_asyncio.apply()
```
就可以順利在 jupyter 使用了

### Po 文上色教學

如果在 Po 文的時候有上色的需求，可以透過模擬鍵盤輸入的方式達到上色碼的效果

```python=
content = [
    PTT.command.Ctrl_C + PTT.command.Left + '5' + PTT.command.Right + '這是閃爍字' + PTT.command.Ctrl_C,
    PTT.command.Ctrl_C + PTT.command.Left + '31' + PTT.command.Right + '前景紅色' + PTT.command.Ctrl_C,
    PTT.command.Ctrl_C + PTT.command.Left + '44' + PTT.command.Right + '背景藍色' + PTT.command.Ctrl_C,   
]
content = '\r\n'.join(content)

ptt_bot.post(
    'Test',
    'PyPtt 程式色碼貼文測試',
    content,
    1,
    0
)
```
執行結果

![](https://i.imgur.com/TOskgf0.png)
