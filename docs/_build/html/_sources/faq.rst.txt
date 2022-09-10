FAQ
==========
這裡搜集了一些常見問題的解答，如果你有任何問題，請先看看這裡。

| Q: 我該如何使用這個腳本？
| A: 請參考 :doc:`install`、:doc:`api/index` 與 :doc:`examples`。

| Q: 我使用 jupyter，遭遇 the event loop is already running 錯誤
| A: 因為 jupyter 內部也使用了 asyncio 作為協程管理工具，會跟 PyPtt 內部的 asyncio 衝突，所以如果想要在 jypyter 內使用，請在你的程式碼中加入以下程式碼

* 安裝 nest_asyncio

.. code-block:: bash

    ! pip install nest_asyncio

* 在程式碼中引用 nest_asyncio

.. code-block:: python

    import nest_asyncio
    nest_asyncio.apply()

| Q: 在 Mac 無法使用 WebSocket 連線，遭遇 SSL 相關錯誤
| A: 請參考以下指令，安裝 Python 的 SSL 憑證

* 以 Python 3.10 為例

.. code-block:: bash

    sh /Applications/Python\ 3.10/Install\ Certificates.command