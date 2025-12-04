# 如何使用 PyPtt 連接 PTT2

## PTT2 簡介

PTT2 (批踢踢兔)，簡稱 P2，是以提供個人板以及團體等私人性質為主的看板服務的 BBS 站，成立於 2000 年 4 月 21 日。

- **網址**: ptt2.cc
- **參考資料**: https://pttpedia.fandom.com/zh/wiki/PTT2

## 與 PTT1 的差異

1. **沒有噓文功能**
2. **每篇文章最多只有 100 P 幣** (P 幣和 PTT1 的 P 幣不能相通)
3. **編輯文章時一般人不會看到編輯紀錄**，只有板主能看到
4. **沒有退文**，不過一樣有水桶
5. **個板沒有樂透**，只有全站有
6. **沒有小天使**

## 使用方法

### 基本連接

```python
import PyPtt

# 建立 PTT2 連接 (使用 PyPtt.HOST.PTT2)
ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT2)

# 登入 PTT2
ptt_bot.login(
    ptt_id='your_ptt2_id',
    password='your_ptt2_password',
    kick_other_session=True
)

# 使用完畢後登出
ptt_bot.logout()
```

### PTT1 vs PTT2 比較

```python
# 連接 PTT1 (ptt.cc)
ptt1_bot = PyPtt.API(host=PyPtt.HOST.PTT1)

# 連接 PTT2 (ptt2.cc)
ptt2_bot = PyPtt.API(host=PyPtt.HOST.PTT2)
```

### 常見 PTT2 看板

- **Amginevar**: PTT2 八希板 (大斷線時為臨時八卦板和希洽板，現在為 PTT2 第一大板)
- **sysop**: PTT1 掛掉的時候會聚集用
- **Ptt2Law**: PTT2 法律板
- **z9板**
- **8A板**: 一度為 P2 中聊各種話題新聞的板

## 完整範例

請參考 `example_ptt2_login.py` 檔案，裡面包含了：

1. 如何連接 PTT2
2. 如何取得看板資訊
3. 如何取得文章列表
4. 錯誤處理

## 注意事項

1. PTT2 的帳號和 PTT1 的帳號是**分開的**
2. 需要分別註冊 PTT2 帳號才能登入
3. 某些功能在 PTT2 上可能不支援或行為不同

## WebSocket 連接資訊

PyPtt 使用 WebSocket 連接到 PTT2：

- **WebSocket Host**: `wss://ws.ptt2.cc/bbs/`
- **Origin**: `https://term.ptt2.cc`

這些設定已經在 PyPtt 內部自動處理，使用者只需要指定 `host=PyPtt.HOST.PTT2` 即可。
