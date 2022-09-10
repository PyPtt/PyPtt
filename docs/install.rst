安裝 PyPtt
===================

Python 版本
--------------
| 推薦使用 CPython_ 3.8+。

.. _CPython: https://www.python.org/

相依套件
--------------
PyPtt 目前相依於以下套件，這些套件都會在安裝的過程中被自動安裝。

* websockets_ is a library for building WebSocket_ servers and clients in Python with a focus on correctness, simplicity, robustness, and performance.
* uao_ is a pure Python implementation of the Unicode encoder/decoder.
* SingleLog_ is a simple logging library for Python.
* requests_ is a Python HTTP library, released under the Apache License 2.0.
* AutoStrEnum_ is a Python library that provides an Enum class that automatically converts enum values to and from strings.

.. _websockets: https://websockets.readthedocs.io/en/stable/
.. _`WebSocket`: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API
.. _uao: https://github.com/eight04/pyUAO
.. _SingleLog: https://github.com/PttCodingMan/SingleLog
.. _requests: https://requests.readthedocs.io/en/master/
.. _AutoStrEnum: https://github.com/PttCodingMan/PttCodingMan

使用虛擬環境安裝 (推薦)
-------------------------
| 我們推薦各位使用虛擬環境 venv_ 來安裝 PyPtt，因為可以盡可能地避免套件衝突。
|
| 你可以從 `Virtual Environments and Packages`_ 中了解，更多關於使用虛擬環境的理由以及如何建立你的虛擬環境。

.. _`Virtual Environments and Packages`: https://docs.python.org/3/tutorial/venv.html#tut-venv
.. _venv: https://docs.python.org/3/library/venv.html

安裝指令
----------------
你可以使用以下指令來安裝 PyPtt。

.. code-block:: bash

    pip install PyPtt

現在 PyPtt 已經成功安裝了，來看看 PyPtt 的 :doc:`API 說明 <api/index>` 或者 :doc:`使用範例 <examples>` 吧！

