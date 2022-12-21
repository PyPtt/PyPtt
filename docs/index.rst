PyPtt
====================

.. image:: _static/logo_cover.png
    :alt: PyPtt: PTT bot library for Python
    :align: center

.. image:: https://img.shields.io/pypi/v/PyPtt.svg
    :target: https://pypi.org/project/PyPtt/

.. image:: https://img.shields.io/github/last-commit/pyptt/pyptt.svg?color=green
    :target: https://github.com/PyPtt/PyPtt/commits/

.. image:: https://img.shields.io/pypi/dm/PyPtt?color=ocean
    :target: https://pypi.org/project/PyPtt/

.. image:: https://github.com/PyPtt/PyPtt/actions/workflows/test.yml/badge.svg?branch=master&color=yellogreen
    :target: https://github.com/PyPtt/PyPtt/actions/workflows/test.yml

.. image:: https://img.shields.io/pypi/pyversions/PyPtt
    :target: https://pypi.org/project/PyPtt/

.. image:: https://img.shields.io/badge/License-LGPL%20v3-blue.svg
    :target: https://www.gnu.org/licenses/lgpl-3.0

.. image:: https://img.shields.io/github/stars/pyptt/pyptt?style=social
    :target: https://github.com/PyPtt/PyPtt/stargazers


| PyPtt_ 是時下最流行的 PTT library，你可以在 Python 程式碼裡面使用 PTT 常見的操作，例如：:doc:`推文 <api/comment>`、:doc:`發文 <api/post>`、:doc:`寄信 <api/mail>`、:doc:`讀取信件 <api/get_mail>`、:doc:`讀取文章 <api/get_post>` 等等操作。
|
| 本文件的內容會隨著 PyPtt_ 的更新而更新，如果你發現任何錯誤，歡迎到 PyPtt_ 發 issue 或者加入 `PyPtt Telegram 社群`_ 一起討論。
|
| PyPtt 由 CodingMan_ 與其他許多的 `貢獻者`_ 共同維護。

.. _PyPtt: https://github.com/PyPtt/PyPtt
.. _`PyPtt Telegram 社群`: https://t.me/PyPtt
.. _CodingMan: https://github.com/PttCodingMan
.. _`貢獻者`: https://github.com/PyPtt/PyPtt/graphs/contributors

重要消息
--------------------
| 2022.12.19 發佈 :doc:`Docker Image <docker>`。
| 2022.12.08 PyPtt 1.0.0 正式發布
| 2021.12.08 PyPtt 新增 :doc:`service` 功能


文件
----------------
:doc:`安裝 PyPtt <install>`
    如何把 PyPtt 安裝到你的環境中。

:doc:`APIs <api/index>`
    PyPtt 的所有 API 說明。

:doc:`Service <service>`
    如何在多線程的情況，安全地使用 PyPtt。

:doc:`參數型態 <type>`
    PyPtt 的所有參數型態選項。

:doc:`例外 <exceptions>`
    PyPtt 所有你可能遭遇到的錯誤。

:doc:`使用範例 <examples>`
    一些使用 PyPtt 的範例。

:doc:`Docker Image <docker>`
    如何使用 Docker Image 來使用 PyPtt。

:doc:`常見問題 <faq>`
    任何常見問題都可以在這找到解答。

:doc:`Roadmap <roadmap>`
    | 這裡列了我們正在做什麼與打算做什麼。
    | 如果你想要貢獻 PyPtt，可以看看這裡。

:doc:`ChangeLog <changelog>`
    | 我們曾經做了什麼。

.. toctree::
    :maxdepth: 3
    :caption: 目錄
    :hidden:

    install
    api/index
    service
    type
    exceptions
    examples
    docker
    常見問題 <faq>
    Roadmap <roadmap>
    ChangeLog <changelog>

    Github <https://github.com/PyPtt/>
    PyPI <https://pypi.org/project/PyPtt/>
