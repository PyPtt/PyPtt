更新日誌
====================
| 這裡寫著 PyPtt 的故事。

| 2026.04.05 修正 ``connect_core`` 編碼回退機制僅支援單向（big5uao → utf-8），導致 ``UseTooManyResources`` 偵測失敗的問題。
| 2026.04.05 修正 ``_decode_screen`` 中 ``UseTooManyResources`` 匹配後未設定 ``find_target``，導致編碼回退覆蓋偵測結果的問題。
| 2026.04.05 偵測到 ``UseTooManyResources`` 時直接拋出例外，由上層處理重新連線。

| 2026.03.26 重構 ``parse_query_post`` 為 ``PostQueryResult`` dataclass，改善內部結構。

| 2025.10.18 PyPtt 支援 Python 3.14 Free Threaded。
| 2025.10.18 重構測試全面採用 pytest，終於可以一次測完所有功能了！
| 重構 CI/CD 流程。重構底層與批踢踢連線模組。

| 2025.09.26 支援 Python 3.13。
| 2025.09.07 新增 :doc:`api/get_post_list` API，可以批次取得文章列表。
| 2025.04.21 修正 get_newest_index 錯誤。
| 2024.12.24 修正推文解析錯誤。
| 2024.09.09 支援 websockets 13。

| 2022.12.20 PyPtt 1.0.3，logger 改採用以 logging_ 為基底。

.. _logging: https://docs.python.org/3/howto/logging.html

| 2022.12.19 發佈 :doc:`Docker Image <docker>`。

| 2022.12.18 PyPtt 新增 :doc:`service` 功能。

| 2022.12.08 PyPtt 1.0.1, 1.0.2，修正一些小錯誤

| 2022.12.08 PyPtt 1.0.0 正式發布。

| 2022.12.01 開發 頁面改名為 Roadmap。

| 2022.09.19 更換主題為 furo_。

.. _furo: https://sphinx-themes.org/sample-sites/furo/

| 2022.09.14 太棒了！我們終於有更新日誌了。