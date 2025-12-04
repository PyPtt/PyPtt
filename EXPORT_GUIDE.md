# PTT 文章匯出功能使用指南

## 簡介

PyPtt 現在支援將 PTT/PTT2 文章匯出為多種格式：

- **Markdown** (.md 或 .markdown) - 格式化的可讀文件
- **Plaintext** (.txt) - 純文字格式
- **CSV** (.csv) - 試算表格式，適合批次分析

## 快速開始

### 基本使用

```python
import PyPtt
from PyPtt import export_util

# 連接並登入 PTT2
ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT2)
ptt_bot.login('your_id', 'your_password')

# 取得文章
post = ptt_bot.get_post('WhoAmI', index=1)

# 匯出為不同格式
export_util.export_post_to_markdown(post, 'article.md')
export_util.export_post_to_plaintext(post, 'article.txt')
export_util.export_post_to_csv(post, 'article.csv')

ptt_bot.logout()
```

### 自動偵測格式

```python
# 根據副檔名自動選擇格式
export_util.export_post(post, 'article.md')      # Markdown
export_util.export_post(post, 'article.txt')     # Plaintext
export_util.export_post(post, 'article.csv')     # CSV
```

## 匯出格式說明

### Markdown 格式 (.md)

適合閱讀和分享，包含完整的格式化：

```markdown
# 文章標題

**Author:** 作者名稱  
**Board:** 看板名稱  
**Date:** 發文日期  
**URL:** 文章網址  

---

文章內容...

---

## Comments (推文數)

- 👍 **推文者** (時間): 推文內容
- 👎 **噓文者** (時間): 噓文內容
- ➡️ **箭頭** (時間): 箭頭內容
```

### Plaintext 格式 (.txt)

純文字格式，適合簡單閱讀：

```
================================================================================
Title: 文章標題
Author: 作者名稱
Board: 看板名稱
Date: 發文日期
URL: 文章網址
================================================================================

Content:
文章內容...

================================================================================
Comments (推文數):

[PUSH] 推文者 (時間): 推文內容
[BOO] 噓文者 (時間): 噓文內容
[ARROW] 箭頭 (時間): 箭頭內容
================================================================================
```

### CSV 格式 (.csv)

試算表格式，適合資料分析：

| 欄位 | 說明 |
|------|------|
| board | 看板名稱 |
| aid | 文章 AID |
| index | 文章編號 |
| author | 作者 |
| date | 日期 |
| title | 標題 |
| content | 內容 |
| url | 網址 |
| ip | IP 位址 |
| location | 發文地點 |
| comments_count | 推文數量 |
| comments_json | 推文資料 (JSON 格式) |

## 進階使用

### 批次匯出多篇文章

```python
# 取得多篇文章
posts = []
for i in range(1, 11):
    post = ptt_bot.get_post('WhoAmI', index=i)
    posts.append(post)

# 匯出為單一 CSV 檔案
export_util.export_posts_to_csv(posts, 'articles_batch.csv')
```

### 匯出搜尋結果

```python
# 搜尋文章
index = ptt_bot.get_newest_index(
    PyPtt.NewIndex.BOARD,
    board='WhoAmI',
    search_type=PyPtt.SearchType.KEYWORD,
    search_condition='[問題]'
)

# 取得並匯出
post = ptt_bot.get_post(
    'WhoAmI',
    index=index,
    search_type=PyPtt.SearchType.KEYWORD,
    search_condition='[問題]'
)

export_util.export_post_to_markdown(post, 'search_result.md')
```

### 自訂輸出路徑

```python
import os

# 建立輸出目錄
output_dir = 'exported_articles'
os.makedirs(output_dir, exist_ok=True)

# 匯出到指定目錄
export_util.export_post_to_markdown(
    post, 
    os.path.join(output_dir, 'article.md')
)
```

### 匯出整個看板所有文章

**新功能！** 現在可以一次匯出整個看板的所有文章，每篇文章都會儲存為獨立的 Markdown 檔案：

```python
# 匯出整個看板
stats = export_util.export_board_to_markdown(
    ptt_bot=ptt_bot,
    board='WhoAmI',
    output_dir='exported_board/'
)

print(f"成功匯出 {stats['success']} 篇文章")
print(f"跳過 {stats['skipped']} 篇（已刪除）")
print(f"失敗 {stats['failed']} 篇")
```

**帶進度顯示：**

```python
def show_progress(current, total, title):
    print(f"[{current}/{total}] {title}")

stats = export_util.export_board_to_markdown(
    ptt_bot=ptt_bot,
    board='WhoAmI',
    output_dir='exported_board/',
    progress_callback=show_progress
)
```

**匯出特定範圍：**

```python
# 只匯出前 100 篇文章
stats = export_util.export_board_to_markdown(
    ptt_bot=ptt_bot,
    board='WhoAmI',
    output_dir='exported_board/',
    start_index=1,
    end_index=100
)
```

**檔案命名規則：**

匯出的檔案會以 `{index}_{aid}_{title}.md` 格式命名，例如：
- `00001_1ABC2DEF_[公告]_看板規則.md`
- `00123_1XYZ9ABC_Re_[問題]_如何使用.md`

這樣可以確保：
- 檔案按照文章編號排序
- 每個檔案都有唯一識別碼 (AID)
- 標題可讀且符合檔案系統規範


## API 參考

### export_post_to_markdown(post_dict, output_path)

匯出文章為 Markdown 格式。

**參數：**
- `post_dict` (Dict): 從 `get_post()` 取得的文章字典
- `output_path` (str): 輸出檔案路徑 (.md 或 .markdown)

### export_post_to_plaintext(post_dict, output_path)

匯出文章為純文字格式。

**參數：**
- `post_dict` (Dict): 從 `get_post()` 取得的文章字典
- `output_path` (str): 輸出檔案路徑 (.txt)

### export_post_to_csv(post_dict, output_path, append=False)

匯出文章為 CSV 格式。

**參數：**
- `post_dict` (Dict): 從 `get_post()` 取得的文章字典
- `output_path` (str): 輸出檔案路徑 (.csv)
- `append` (bool): 是否附加到現有檔案（預設：False）

### export_posts_to_csv(post_list, output_path)

批次匯出多篇文章為單一 CSV 檔案。

**參數：**
- `post_list` (List[Dict]): 文章字典列表
- `output_path` (str): 輸出檔案路徑 (.csv)

### export_post(post_dict, output_path, format=None)

通用匯出函數，自動偵測格式。

**參數：**
- `post_dict` (Dict): 從 `get_post()` 取得的文章字典
- `output_path` (str): 輸出檔案路徑
- `format` (str, optional): 指定格式 ('markdown', 'plaintext', 'csv')，若為 None 則自動偵測

### export_board_to_markdown(ptt_bot, board, output_dir, start_index=None, end_index=None, progress_callback=None)

**新功能！** 匯出整個看板所有文章為獨立的 Markdown 檔案。

**參數：**
- `ptt_bot` (API): PyPtt API 實例（必須已登入）
- `board` (str): 看板名稱
- `output_dir` (str): 輸出目錄路徑
- `start_index` (int, optional): 起始文章編號（預設：1）
- `end_index` (int, optional): 結束文章編號（預設：最新編號）
- `progress_callback` (callable, optional): 進度回調函數 `callback(current, total, title)`

**回傳值：**
- Dict 包含統計資訊：
  - `total`: 嘗試匯出的文章總數
  - `success`: 成功匯出的文章數
  - `failed`: 失敗的文章數
  - `skipped`: 跳過的文章數（已刪除等）
  - `output_dir`: 輸出目錄的絕對路徑


## 完整範例

請參考以下範例檔案：

1. **[example_export_article.py](file:///Users/cjhuang/GitHub/PyPtt/example_export_article.py)** - 單篇文章匯出
   - 單篇文章匯出
   - 批次匯出多篇文章
   - 匯出搜尋結果
   - 錯誤處理

2. **[example_export_board.py](file:///Users/cjhuang/GitHub/PyPtt/example_export_board.py)** - 整個看板匯出 ⭐ 新增
   - 匯出整個看板所有文章
   - 帶進度顯示的匯出
   - 匯出特定範圍
   - 檔案命名規則說明


## 注意事項

1. **編碼**：所有匯出檔案使用 UTF-8 編碼
2. **目錄建立**：如果輸出路徑的目錄不存在，會自動建立
3. **檔案覆蓋**：預設會覆蓋同名檔案（CSV 可使用 `append=True` 附加）
4. **推文資料**：CSV 格式中，推文會以 JSON 字串儲存在 `comments_json` 欄位

## 常見問題

### Q: 如何處理大量文章匯出？

A: 使用 `export_posts_to_csv()` 批次匯出，並適當處理例外：

```python
posts = []
for i in range(1, 101):
    try:
        post = ptt_bot.get_post('Board', index=i)
        if post:
            posts.append(post)
    except Exception as e:
        print(f"Error fetching post {i}: {e}")

export_util.export_posts_to_csv(posts, 'batch_export.csv')
```

### Q: 匯出的 Markdown 檔案可以在哪裡查看？

A: Markdown 檔案可以在以下工具中查看：
- GitHub/GitLab（自動渲染）
- VS Code（內建預覽）
- Typora、Mark Text 等 Markdown 編輯器
- 任何文字編輯器（查看原始碼）

### Q: CSV 檔案可以用 Excel 開啟嗎？

A: 可以！但請注意：
- 使用 Excel 的「資料」→「從文字/CSV」功能匯入
- 選擇 UTF-8 編碼以正確顯示中文
- 或使用 Google Sheets（自動處理 UTF-8）

### Q: 如何只匯出文章內容，不要推文？

A: 目前匯出會包含所有可用資料。如需自訂，可以修改 post_dict：

```python
# 移除推文資料
post_copy = post.copy()
post_copy[PyPtt.PostField.comments] = []

export_util.export_post_to_markdown(post_copy, 'article_no_comments.md')
```
