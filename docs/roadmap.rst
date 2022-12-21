開發
=============
| 這裡列了一些我們正在開發的功能，如果你有任何建議，歡迎找我們聊聊。
| 或者你也可以直接在 github 上開 issue，我們會盡快回覆。

| 當然如果你有興趣參與開發，也歡迎你加入我們，我們會盡快回覆你的加入申請。

未來開發計劃
--------------------
* WebSocket 支援 Tor or Proxy
    期待有一天可以透過 Tor 或 Proxy 來連接到 PTT，讓 PyPtt 可以自由地在雲端伺服器運作。

開發中
--------------------
* 支援 PTT 官方 APP API
    你可以在 ptt-app-api_ 分支上找到目前的進度。

.. _ptt-app-api: https://github.com/PyPtt/PyPtt/tree/ptt-app-api

已完成
--------------------
* PyPtt Service docker
    | 期待 PyPtt 在未來可以有 API 形式的服務，讓大家可以透過 API 呼叫來使用 PyPtt。
    | 這樣其實在某個層面也上可以達到使用 Tor or Proxy 的目的。

    * PyPtt :doc:`service` 2022.12.18 完成
    * Docker :doc:`docker` 2022.12.19 完成
* 官方網站的建置 2022.12.18 完成
     使用 sphinx 來建置官方網站，讓大家可以更方便地了解 PyPtt。
* 測試案例 2022.12.15 完成
* 1.0 正式版本重構 2022.11.15 完成