# PTT2 連接說明

## 快速開始

PyPtt 已經內建支援 PTT2 (ptt2.cc)！你只需要在建立 API 實例時指定 `host=PyPtt.HOST.PTT2` 即可。

### 最簡單的範例

```python
import PyPtt

# 連接 PTT2 而非 PTT1
ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT2)

# 使用你的 PTT2 帳號登入
ptt_bot.login('your_ptt2_id', 'your_ptt2_password')

# ... 進行你的操作 ...

# 登出
ptt_bot.logout()
```

## 重要差異

**PTT1 (ptt.cc)**
```python
ptt1_bot = PyPtt.API(host=PyPtt.HOST.PTT1)  # 預設值
```

**PTT2 (ptt2.cc)**
```python
ptt2_bot = PyPtt.API(host=PyPtt.HOST.PTT2)  # 指定 PTT2
```

## 相關檔案

1. **example_ptt2_login.py** - 完整的 PTT2 連接範例程式
2. **README_PTT2.md** - 詳細的 PTT2 使用說明文件

## PTT2 資訊

- **網址**: ptt2.cc
- **WebSocket**: wss://ws.ptt2.cc/bbs/
- **參考**: https://pttpedia.fandom.com/zh/wiki/PTT2

## 技術細節

PyPtt 在 `connect_core.py` 中已經配置好 PTT2 的連接設定：

```python
elif self.config.host == data_type.HOST.PTT2:
    websocket_host = 'wss://ws.ptt2.cc/bbs/'
    websocket_origin = 'https://term.ptt2.cc'
```

所有功能都會自動適配 PTT2，包括：
- 登入/登出
- 讀取文章
- 發文
- 推文
- 搜尋
- 等等...

**注意**: PTT2 的帳號與 PTT1 是分開的，需要另外註冊。
