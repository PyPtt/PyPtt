參數型態
===========
這裡介紹 PyPtt 的參數型態

.. _host:

HOST
-----------
* 連線的 PTT 伺服器。

.. py:attribute:: PyPtt.HOST.PTT1

    批踢踢實業坊

.. py:attribute:: PyPtt.HOST.PTT2

    批踢踢兔

.. _language:

Language
-----------
* 顯示訊息的語言。

.. py:attribute:: PyPtt.Language.MANDARIN

    繁體中文

.. py:attribute:: PyPtt.Language.ENGLISH

    英文

.. _connect-mode:

ConnectMode
-----------
* 連線的模式。

.. py:attribute:: PyPtt.ConnectMode.WEBSOCKETS

    使用 WEBSOCKETS 連線

.. py:attribute:: PyPtt.ConnectMode.TELNET

    使用 TELNET 連線

.. _new-index:

NewIndex
-----------
* 搜尋 Index 的種類。

.. py:attribute:: PyPtt.NewIndex.BOARD

    搜尋看板 Index

.. py:attribute:: PyPtt.NewIndex.MAIL

    搜尋信箱 Index

.. _search-type:

SearchType
-----------
* 搜尋看板的方式。

.. py:attribute:: PyPtt.SearchType.KEYWORD

    搜尋關鍵字

.. py:attribute:: PyPtt.SearchType.AUTHOR

    搜尋作者

.. py:attribute:: PyPtt.SearchType.COMMENT

    搜尋推文數

.. py:attribute:: PyPtt.SearchType.MARK

    搜尋標記

.. py:attribute:: PyPtt.SearchType.MONEY

    搜尋稿酬

.. _reply-to:

ReplyTo
-----------
* 回文的方式。

.. py:attribute:: PyPtt.ReplyTo.BOARD

    回文至看板

.. py:attribute:: PyPtt.ReplyTo.MAIL

    回文至信箱

.. py:attribute:: PyPtt.ReplyTo.BOARD_MAIL

    回文至看板與信箱

.. _comment-type:

CommentType
-----------
* 推文方式。

.. py:attribute:: PyPtt.CommentType.PUSH

    推

.. py:attribute:: PyPtt.CommentType.BOO

    噓

.. py:attribute:: PyPtt.CommentType.ARROW

    箭頭

.. _post-status:

PostStatus
-----------
* 文章狀態。

.. py:attribute:: PyPtt.PostStatus.EXISTS

    文章存在

.. py:attribute:: PyPtt.PostStatus.DELETED_BY_AUTHOR

    被作者刪除

.. py:attribute:: PyPtt.PostStatus.DELETED_BY_MODERATOR

    被板主刪除

.. py:attribute:: PyPtt.PostStatus.DELETED_BY_UNKNOWN

    無法判斷，被如何刪除

.. _mark-type:

MarkType
-----------
* 版主標記文章種類

.. py:attribute:: PyPtt.MarkType.S

    S 文章

.. py:attribute:: PyPtt.MarkType.D

    標記文章

.. py:attribute:: PyPtt.MarkType.DELETE_D

    刪除標記文章

.. py:attribute:: PyPtt.MarkType.M

    M 起來

.. py:attribute:: PyPtt.MarkType.UNCONFIRMED

    待證實文章


.. _user-field:

UserField
-----------
* 使用者資料欄位。

.. py:attribute:: PyPtt.UserField.ptt_id

    使用者 ID

.. py:attribute:: PyPtt.UserField.money

    經濟狀態

.. py:attribute:: PyPtt.UserField.login_count

    登入次數

.. py:attribute:: PyPtt.UserField.account_verified

    是否通過認證

.. py:attribute:: PyPtt.UserField.legal_post

    文章數量

.. py:attribute:: PyPtt.UserField.illegal_post

    退文數量

.. py:attribute:: PyPtt.UserField.activity

    目前動態

.. py:attribute:: PyPtt.UserField.mail

    信箱狀態

.. py:attribute:: PyPtt.UserField.last_login_date

    最後登入時間

.. py:attribute:: PyPtt.UserField.last_login_ip

    最後登入 IP

.. py:attribute:: PyPtt.UserField.five_chess

    五子棋戰積

.. py:attribute:: PyPtt.UserField.chess

    象棋戰積

.. py:attribute:: PyPtt.UserField.signature_file

    簽名檔

.. _comment-field:

CommentField
--------------
* 推文資料欄位。

.. py:attribute:: PyPtt.CommentField.type

    推文類型，推噓箭頭，詳見 :ref:`comment-type`

.. py:attribute:: PyPtt.CommentField.author

    推文作者

.. py:attribute:: PyPtt.CommentField.content

    推文內容

.. py:attribute:: PyPtt.CommentField.ip

    推文 IP (如果存在)

.. py:attribute:: PyPtt.CommentField.time

    推文時間

.. _favorite-board-field:

FavouriteBoardField
--------------------
* 我的最愛資料欄位。

.. py:attribute:: PyPtt.FavouriteBoardField.board

    看板名稱

.. py:attribute:: PyPtt.FavouriteBoardField.title

    看板標題

.. py:attribute:: PyPtt.FavouriteBoardField.type

    類別

.. _mail-field:

MailField
----------
* 信件資料欄位。

.. py:attribute:: PyPtt.MailField.origin_mail

    原始信件全文

.. py:attribute:: PyPtt.MailField.author

    信件作者

.. py:attribute:: PyPtt.MailField.title

    信件標題

.. py:attribute:: PyPtt.MailField.date

    信件日期

.. py:attribute:: PyPtt.MailField.content

    信件內容

.. py:attribute:: PyPtt.MailField.ip

    信件 IP

.. py:attribute:: PyPtt.MailField.location

    信件位置

.. py:attribute:: PyPtt.MailField.is_red_envelope

    是否為紅包

.. _board-field:

BoardField
-----------
* 看板資料欄位。

.. py:attribute:: PyPtt.BoardField.board

    看板名稱

.. py:attribute:: PyPtt.BoardField.online_user

    在線人數

.. py:attribute:: PyPtt.BoardField.chinese_des

    看板中文名稱

.. py:attribute:: PyPtt.BoardField.moderators

    看板板主清單

.. py:attribute:: PyPtt.BoardField.open_status

    看板公開狀態，是否隱板

.. py:attribute:: PyPtt.BoardField.into_top_ten_when_hide

    隱板時是否可以進入十大排行榜

.. py:attribute:: PyPtt.BoardField.can_non_board_members_post

    非看板成員是否可以發文

.. py:attribute:: PyPtt.BoardField.can_reply_post

    是否可以回覆文章

.. py:attribute:: PyPtt.BoardField.self_del_post

    是否可以自刪文章

.. py:attribute:: PyPtt.BoardField.can_comment_post

    是否可以推文

.. py:attribute:: PyPtt.BoardField.can_boo_post

    是否可以噓文

.. py:attribute:: PyPtt.BoardField.can_fast_push

    是否可以快速推文

.. py:attribute:: PyPtt.BoardField.min_interval_between_comments

    推文間隔時間

.. py:attribute:: PyPtt.BoardField.is_comment_record_ip

    是否記錄推文 IP

.. py:attribute:: PyPtt.BoardField.is_comment_aligned

    推文是否對齊

.. py:attribute:: PyPtt.BoardField.can_moderators_del_illegal_content

    板主是否可以刪除違規文字

.. py:attribute:: PyPtt.BoardField.does_tran_post_auto_recorded_and_require_post_permissions

    是否自動記錄轉錄文章並需要發文權限

.. py:attribute:: PyPtt.BoardField.is_cool_mode

    是否為冷板模式

.. py:attribute:: PyPtt.BoardField.is_require18

    是否為 18 禁看板

.. py:attribute:: PyPtt.BoardField.require_login_time

    發文需要登入次數

.. py:attribute:: PyPtt.BoardField.require_illegal_post

    發文需要最低退文數量

.. py:attribute:: PyPtt.BoardField.post_kind_list

    發文類別，例如 [公告] [問卦] 等

.. _post-field:

PostField
-----------
* 文章資料欄位。

.. py:attribute:: PyPtt.PostField.board

    文章所在看板

.. py:attribute:: PyPtt.PostField.aid

    文章 ID，例如：`#1Z69g2ts`

.. py:attribute:: PyPtt.PostField.index

    文章編號，例如：906

.. py:attribute:: PyPtt.PostField.author

    文章作者

.. py:attribute:: PyPtt.PostField.date

    文章日期

.. py:attribute:: PyPtt.PostField.title

    文章標題

.. py:attribute:: PyPtt.PostField.content

    文章內容

.. py:attribute:: PyPtt.PostField.money

    文章稿酬，P 幣

.. py:attribute:: PyPtt.PostField.url

    文章網址

.. py:attribute:: PyPtt.PostField.ip

    文章 IP

.. py:attribute:: PyPtt.PostField.comments

    文章推文清單，詳見 :ref:`comment-field`

.. py:attribute:: PyPtt.PostField.post_status

    文章狀態，詳見 :ref:`post-status`

.. py:attribute:: PyPtt.PostField.list_date

    文章列表日期

.. py:attribute:: PyPtt.PostField.has_control_code

    文章是否有控制碼

.. py:attribute:: PyPtt.PostField.pass_format_check

    文章是否通過格式檢查

.. py:attribute:: PyPtt.PostField.location

    文章 IP 位置

.. py:attribute:: PyPtt.PostField.push_number

    文章推文數量

.. py:attribute:: PyPtt.PostField.is_lock

    文章是否鎖定

.. py:attribute:: PyPtt.PostField.full_content

    文章完整內容

.. py:attribute:: PyPtt.PostField.is_unconfirmed

    文章是否為未確認文章