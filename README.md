![PTTLibrary: A PTT Library in Python](https://i.imgur.com/B1kIMgR.png)
# PTT Library
[![Package Version](https://img.shields.io/pypi/v/PTTLibrary.svg)](https://pypi.python.org/pypi/PTTLibrary)
[![Build Status](https://travis-ci.org/Truth0906/PTTLibrary.svg?branch=master)](https://travis-ci.org/Truth0906/PTTLibrary)
[![Codacy Badge](https://api.codacy.com/project/badge/grade/8f2eee1a277d499f95dfd5ee46094fdf)](https://www.codacy.com/app/hunkim/TensorFlow-Tutorials)
[![Requirements Status](https://requires.io/github/Truth0906/PTTLibrary/requirements.svg?branch=master)](https://requires.io/github/Truth0906/PTTLibrary/requirements/?branch=master)
![license](https://img.shields.io/github/license/mashape/apistatus.svg)
[![Join the chat at https://gitter.im/PTTLibrary/Lobby](https://badges.gitter.im/PTTLibrary/Lobby.svg)](https://gitter.im/PTTLibrary/Lobby?utm_source=badge&utm_medium=badge&utm_content=badge)

#### Do you want PTT in Python? import PTT !

###### PTT Library 是一個由 Python 寫成用來操作 PTT 的函式庫，你可以在任何可以使用 Python 的地方，執行你的 PTT 機器人。
###### 拋棄過往網頁形式的解析，直接登入 PTT 分析最即時的文章與推文，給你最快速的資訊!
###### 程式碼發布在
###### github: https://github.com/Truth0906/PTTLibrary
###### Pypi: https://pypi.org/project/PTTLibrary/

版本
-------------------
###### 0.6.2

安裝
-------------------
```
pip3 install PTTLibrary
```

基本使用
-------------------
```
from PTTLibrary import PTT

PTTBot = PTT.Library(ID, Password)
ErrCode = PTTBot.login()
if ErrCode != PTT.ErrorCode.Success:
    PTTBot.Log('登入失敗')
    sys.exit()

......

PTTBot.logout()
```
###### 你可以參考 Test.py 裡面有 API 的範例與說明

詳細說明
-------------------
###### 請參考 Test.py

需求
-------------------
###### Python 3.6

相依函式庫
-------------------
###### progressbar2
###### paramiko

未來工作
-------------------
###### 加入搜尋條件
###### 對於有控制碼的文章開發新方式解析
###### 可蒐集使用者清單
###### 支援 PTT2

API
-------------------
| API  | 說明|
| :---------- | -----------|
| getVersion   | 取得版本資訊   |
| login   | 登入   |
| logout   | 登出   |
| post   | 發佈文章   |
| push   | 推文   |
| mail   | 寄信   |
| getPost   | 取得文章資訊   |
| getNewestIndex   | 取得該看板最新的文章編號或者信箱最新信件編號   |
| giveMoney   | 給予使用者 P 幣   |
| getTime   | 取得 PTT 系統時間   |
| getUser   | 取得使用者資訊   |
| crawlBoard   | 多線程爬蟲 以多重登入增加爬蟲速度 可傳入 call back 自訂存檔格式  |
| getMail   | 取得信件資訊   |
| Log   | 顯示訊息   |
| changePassword   | 變更密碼   |
| replyPost   | 回覆文章   |
| throwWaterBall   | 丟水球   |
| delPost   | 刪除文章   |

贊助
-------------------
###### 如果這個專案減少了你的開發時間，你可以贊助我一杯咖啡 :D
###### XMR 贊助位址
###### 448CUe2q4Ecf9tx6rwanrqM9kfCwqpNbhJ5jtrTf9FHqHNq7Lvv9uBoQ74SEaAu9FFceNBr6p3W1yhqPcxPPSSTv2ctufnQ

