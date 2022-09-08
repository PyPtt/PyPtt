如何安裝 PyPtt
===================

Python 版本
--------------
建議你使用 Python 3.8 以上的版本。
因為所有測試都建立在 Python 3.8 以上的版本上。

相依套件
--------------
PyPtt 目前相依於以下套件，這些套件都會在安裝 PyPtt 的過程被自動安裝。

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

從 PyPi 安裝
----------------
你可以使用以下指令來安裝 PyPtt

.. code-block:: bash

    pip install PyPtt

現在 PyPtt 已經成功安裝了，來看看 PyPtt 的 :doc:`API 說明 <api/index>` 或者 :doc:`使用範例 <examples>` 吧！

