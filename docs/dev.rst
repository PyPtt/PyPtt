Development
================
如果你想參與開發，請參考以下須知：

開發環境
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
我們建議您使用 virtualenv 來建立獨立的 Python 環境，以避免相依性問題。

.. code-block:: bash

    python3 -m venv .venv

安裝相依套件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
你可以使用以下指令來安裝測開發的相依套件：

.. code-block:: bash

    pip install .[dev]

產生文件網頁

.. code-block:: bash

    make html

你可以在 docs/_build/html/index.html 中找到根據你的修改產生的網頁。

執行測試
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
你可以使用以下指令來執行測試：

.. code-block:: bash

    python3 -m pytest

此外，在執行之前你可能會想要設定測試用的帳號，你可以直接建立 .env 檔案，並加入以下內容：

.. code-block:: dosini

    PTT1_ID="id1"
    PTT1_PW="pw1"

    PTT2_ID="id2"
    PTT2_PW="pw2"

    TEST_USER="id2" # 用給 P 幣測試的帳號

NOTE: 如果你有任何貢獻，請確保所有測試都能通過。

撰寫文件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| 如果你的變更涉及文件，請記得更新文件。
| 我們使用 Sphinx 來撰寫文件，你可以在 docs/ 中找到文件的原始碼。

建立你的 Pull Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
如果你想要貢獻程式碼，請參考以下步驟：

1. Fork 這個專案。
2. 建立你的特性分支 (`git checkout -b feat/my-new-feature`)。
3. Commit 你的變更 (`git commit -am 'feat: add some feature`)。
    commit msg 格式，請參考 `Conventional Commits`_。
4. Push 到你的分支 (`git push origin feat/my-new-feature`)。
5. 建立一個新的 Pull Request。
6. 你可以跟 reviewer 要求測試你的變更。

NOTE: 我們會優先處理符合 `Conventional Commits`_ 的 Pull Request。

.. _Conventional Commits: https://www.conventionalcommits.org/en/v1.0.0/
