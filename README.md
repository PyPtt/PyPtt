# PTT Telnet Crawler Library

###### 這是一個專為 PTT 爬蟲開發者所開發的函式庫 PTTTelnetCrawlerLibrary
###### 會根據網路速度調整操作速度 尋求最穩定的執行

#### 需求

###### Python 3.6.1

###### request

###### BeautifulSoup4

#### 版本

###### 0.1.170604 beta

#### API

###### gotoUserMenu 移動至使用者選單    
###### gotoBoard 移動至看板
###### logout 登出
###### post PO 文
###### gotoPostByIndex 根據文章編號移動至該文章前
###### gotoPostByID 根據文章ID移動至該文章前
###### pushByIndex 根據文章編號推文
###### pushByID 根據文章ID推文
###### mail 寄信給使用者
###### getPostInformationByID 根據文章ID 取得文章資訊 內含推文清單
###### getPostInformationByIndex 根據文章編號 取得文章資訊 內含推文清單
###### getNewestPostIndex 取得該看板最新的文章編號
###### getNewPostIndex 取得上次查詢之後才新增的文章清單
###### getPostFloorByIndex 取得該篇文章有多少推文數 包括推噓箭頭
###### giveMoney 給予使用者 P幣
#### Demo   
###### 請參考 Test.py

![alt text](http://i.imgur.com/ErCRUk1.png)
