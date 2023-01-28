FAQ
==========
這裡搜集了一些常見問題的解答，如果你有任何問題，請先看看這裡。

Q: 我該如何使用這個腳本？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| A: 可以先參考 :doc:`install`、:doc:`api/index` 與 :doc:`examples`。

Q: 我該如何提出問題？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. 請先確認你使用的版本是否為 |version_pic|，如果不是，請更新到最新版本。
2. 如果你使用的是最新版本，請確認你的問題是否已經在這裡被回答過了。如果你的問題還沒有被回答過，請依照以下程式碼將 LogLevel_ 設定為 `TRACE`，並附上 **可以重現問題的程式碼**。

.. code-block:: python

    import PyPtt

    ptt_bot = PyPtt.API(LogLevel=PyPtt.LogLevel.TRACE)

    # 你的程式碼

.. |version_pic| image:: https://img.shields.io/pypi/v/PyPtt.svg
    :target: https://pypi.org/project/PyPtt/

.. _LogLevel: https://github.com/PttCodingMan/SingleLog/blob/d7c19a1b848dfb1c9df8201f13def9a31afd035c/SingleLog/SingleLog.py#L22


Q: 在 jupyter 遭遇 `the event loop is already running` 錯誤
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| A: 因為 jupyter 內部也使用了 asyncio 作為協程管理工具，會跟 PyPtt 內部的 asyncio 衝突，所以如果想要在 jypyter 內使用，請在你的程式碼中加入以下程式碼

.. code-block:: bash
    :caption: 安裝 nest_asyncio

    ! pip install nest_asyncio



.. code-block:: python
    :caption: 在程式碼中引用 nest_asyncio

    import nest_asyncio
    nest_asyncio.apply()

Q: 在 Mac 無法使用 WebSocket 連線，遭遇 SSL 相關錯誤
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| A: 請參考以下指令，安裝 Python 的 SSL 憑證

.. code-block:: bash
    :caption: 以 Python 3.10 為例

    sh /Applications/Python\ 3.10/Install\ Certificates.command