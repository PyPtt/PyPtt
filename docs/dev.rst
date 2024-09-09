Development
================
如果你想參與開發，請參考以下須知：

開發環境
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
我們建議您使用 virtualenv 來建立獨立的 Python 環境，以避免相依性問題。

.. code-block:: bash

    virtualenv venv
    source venv/bin/activate

安裝相依套件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
你可以使用以下指令來安裝相依套件：

.. code-block:: bash

    pip install -r requirements.txt

如果你想更改文件，請安裝開發相依套件：

.. code-block:: bash

    pip install -r docs/requirements.txt

產生文件網頁

.. code-block:: bash

    bash make_doc.sh

你可以在 docs/_build/html/index.html 中找到根據你的修改產生的網頁。

執行測試
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
你可以使用以下指令來執行測試：

.. code-block:: bash

    for test in tests/*.py; do python3 $test; done

此外，在執行之前你可能會想要設定測試用的帳號，這部份可以透過直接修改
tests/config.py，或是設定 PTT1_ID、PTT1_PW、PTT2_ID 與 PTT2_PW 四個
環境變數來達成。

如果有遺漏的測試，請不吝發起 Pull Request。

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
