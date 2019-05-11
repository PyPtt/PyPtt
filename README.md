![PTTLibrary: A PTT Library in Python](https://i.imgur.com/B1kIMgR.png)
# PTT Library
[![Package Version](https://img.shields.io/pypi/v/PTTLibrary.svg)](https://pypi.python.org/pypi/PTTLibrary)
[![Build Status](https://travis-ci.org/Truth0906/PTTLibrary.svg?branch=master)](https://travis-ci.org/Truth0906/PTTLibrary)
[![Codacy Badge](https://api.codacy.com/project/badge/grade/8f2eee1a277d499f95dfd5ee46094fdf)](https://www.codacy.com/app/hunkim/TensorFlow-Tutorials)
[![Requirements Status](https://requires.io/github/Truth0906/PTTLibrary/requirements.svg?branch=master)](https://requires.io/github/Truth0906/PTTLibrary/requirements/?branch=master)
![license](https://img.shields.io/github/license/mashape/apistatus.svg)
[![Join the chat at https://gitter.im/PTTLibrary/Lobby](https://badges.gitter.im/PTTLibrary/Lobby.svg)](https://gitter.im/PTTLibrary/Lobby?utm_source=badge&utm_medium=badge&utm_content=badge)

#### Do you want PTT in Python? import PTT !

##### PTT Library 是一個由 Python 所開發，用來操作 PTT 的函式庫，只要支援 Python 就可以執行你的 PTT 機器人。
##### 直接登入 PTT 解析最即時推文，給你最快速的資訊!
##### 支援經典的 Telnet 與最新的 WebSocket 連線模式
##### 支援多國語系，繁體中文與英文
##### 歡迎發起 pull request，提交你開發的 API!
##### 測試平台: Windows 10, Ubuntu 18.04, MacOS 10.14
##### 原始碼
##### github: https://github.com/Truth0906/PTTLibrary
##### Pypi: https://pypi.org/project/PTTLibrary/

## 介紹影片

[![](http://img.youtube.com/vi/ng48ITuePlg/0.jpg)](http://www.youtube.com/watch?v=ng48ITuePlg "")

版本
-------------------
##### 0.8 beta
##### 穩定後版號將進入 1.0 正式版

取得
-------------------
#### 安裝
```
pip3 install PTTLibrary
```
#### 更新
#### [更新前注意] 0.8 不支援 0.7 之前的版本
```
pip3 install PTTLibrary --upgrade
```

基本使用
-------------------
```
import PTTLibrary
from PTTLibrary import PTT

PTTBot = PTT.Library()
try:
    PTTBot.login(ID, Password)
except PTTLibrary.ConnectCore.LoginError:
    PTTBot.log('登入失敗')
    sys.exit()
PTTBot.log('登入成功')

    .... Do something magic

PTTBot.logout()
```

詳細說明
-------------------
##### 請參考 Demo.py 有 API 的詳細範例與參數說明

需求
-------------------
##### Python ≥ 3.6

相依函式庫
-------------------
##### progressbar2
##### websockets
##### requests
##### uao

正在工作
-------------------
##### 支援 i18n
##### 重構
##### 同時支援 WebSocket 與 Telnet 連線

API
-------------------
| API  | 說明|
| :---------- | -----------|
| getVersion   | 取得版本資訊   |
| login   | 登入   |
| logout   | 登出   |

贊助
-------------------
##### 在這個 github 的小園地，用熱血的心為您打造在 PTT 翱翔的翅膀。
##### 您可以贊助這雙翅膀，讓我們一起飛得更遠，
##### Paypal
##### [贊助連結](http://paypal.me/CodingMan)
##### XMR
##### 448CUe2q4Ecf9tx6rwanrqM9kfCwqpNbhJ5jtrTf9FHqHNq7Lvv9uBoQ74SEaAu9FFceNBr6p3W1yhqPcxPPSSTv2ctufnQ
