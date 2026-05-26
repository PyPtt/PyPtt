fast_post_step0 / fast_post_step1
==================================

.. _api-fast-post:

將發文流程拆成兩步，讓你在精確時刻（例如跨年）送出文章。

**運作原理**

一般的 :ref:`post <api-post>` 是逐步互動的：每送一個指令都要等 PTT 回應，
因此整體速度受到網路來回延遲（RTT）限制。

``fast_post_step0`` 把所有準備工作（進板、填標題、填內文、Ctrl+X）打包成一個指令串一次送出，
讓連線停在「確定要儲存檔案嗎？」畫面等待。
到了精確時刻，呼叫 ``fast_post_step1`` 只送一個確認，文章立即發佈。

.. warning::
   呼叫 ``fast_post_step0`` 之後，連線處於等待狀態，**不可呼叫任何其他 API**，
   否則會造成連線錯誤。

.. automodule:: PyPtt.API
   :members: fast_post_step0, fast_post_step1
   :noindex:

範例
---------

.. code-block:: python

   import time
   import PyPtt

   ptt_bot = PyPtt.API()
   try:
       ptt_bot.login('帳號', '密碼')

       # ── 提前幾秒執行：準備好文章 ──
       ptt_bot.fast_post_step0(
           board='Gossiping',
           title='2026新年快樂',
           content='大家新年快樂！\n',
           post_type=1,
       )

       # ── 等到精確時刻 ──
       # 注意：PTT 主機時間可能與 NTP 有偏差，
       #       建議先用 get_time() 校正誤差後再計算 target。
       target = 1767196800.0  # 2026-01-01 00:00:00 UTC+8
       while time.time() < target:
           pass

       # ── 精確時刻送出 ──
       ptt_bot.fast_post_step1(sign_file=0)
   finally:
       ptt_bot.logout()

PTT 時間校正
-------------

PTT 主機時間可能與本地時間有數秒偏差，跨年搶頭香時需要補正：

.. code-block:: python

   import time
   import PyPtt

   ptt_bot = PyPtt.API()
   ptt_bot.login('帳號', '密碼')

   # 比較 PTT 主機時間與本地時間
   local_time = time.strftime('%H:%M', time.localtime())
   ptt_time = ptt_bot.get_time()  # 格式 'HH:MM'
   # 根據偏差調整 target 後再呼叫 fast_post_step0 / fast_post_step1

參考 :ref:`取得 PTT 時間 <api-get-time>`
