例外
========
| 這裡介紹 PyPtt 的例外。
| 可以用 try...except... 來處理。

| 例外的種類

.. py:exception:: PyPtt.exceptions.RequireLogin
    :module: PyPtt

    需要登入時會拋出的例外。

.. py:exception:: PyPtt.exceptions.NoPermission
    :module: PyPtt

    沒有權限時會拋出的例外。

.. py:exception:: PyPtt.exceptions.LoginError
    :module: PyPtt

    登入失敗時會拋出的例外。

.. py:exception:: PyPtt.exceptions.NoFastComment
    :module: PyPtt

    無法快速推文時會拋出的例外。

.. py:exception:: PyPtt.exceptions.NoSuchUser
    :module: PyPtt

    查無此使用者時會拋出的例外。

.. py:exception:: PyPtt.exceptions.NoMoney
    :module: PyPtt

    餘額不足時會拋出的例外。

.. py:exception:: PyPtt.exceptions.NoSuchBoard
    :module: PyPtt

    查無此看板時會拋出的例外。

.. py:exception:: PyPtt.exceptions.ConnectionClosed
    :module: PyPtt

    連線已關閉時會拋出的例外。

.. py:exception:: PyPtt.exceptions.UnregisteredUser
    :module: PyPtt

    未註冊使用者時會拋出的例外。

.. py:exception:: PyPtt.exceptions.MultiThreadOperated
    :module: PyPtt

    同時使用多個 thread 呼叫 PyPtt 時會拋出的例外。

.. py:exception:: PyPtt.exceptions.WrongIDorPassword
    :module: PyPtt

    帳號或密碼錯誤時會拋出的例外。

.. py:exception:: PyPtt.exceptions.WrongPassword
    :module: PyPtt

    密碼錯誤時會拋出的例外。

.. py:exception:: PyPtt.exceptions.LoginTooOften
    :module: PyPtt

    登入太頻繁時會拋出的例外。

.. py:exception:: PyPtt.exceptions.UseTooManyResources
    :module: PyPtt

    使用過多資源時會拋出的例外。

.. py:exception:: PyPtt.exceptions.HostNotSupport
    :module: PyPtt

    主機不支援時會拋出的例外。詳見 :ref:`host`。

.. py:exception:: PyPtt.exceptions.NoComment
    :module: PyPtt

    禁止推薦時會拋出的例外。

.. py:exception:: PyPtt.exceptions.CantResponse
    :module: PyPtt

    已結案並標記, 不得回應時會拋出的例外。

.. py:exception:: PyPtt.exceptions.NeedModeratorPermission
    :module: PyPtt

    需要版主權限時會拋出的例外。

.. py:exception:: PyPtt.exceptions.ConnectError
    :module: PyPtt

    連線失敗時會拋出的例外。

.. py:exception:: PyPtt.exceptions.NoSuchPost
    :module: PyPtt

    文章不存在時會拋出的例外。

.. py:exception:: PyPtt.exceptions.CanNotUseSearchPostCode
    :module: PyPtt

    無法使用搜尋文章代碼時會拋出的例外。

.. py:exception:: PyPtt.exceptions.UserHasPreviouslyBeenBanned
    :module: PyPtt

    水桶使用者，但已經被水桶時會拋出的例外。

.. py:exception:: PyPtt.exceptions.MailboxFull
    :module: PyPtt

    信箱已滿時會拋出的例外。

.. py:exception:: PyPtt.exceptions.NoSearchResult
    :module: PyPtt

    搜尋結果為空時會拋出的例外。

.. py:exception:: PyPtt.exceptions.OnlySecureConnection
    :module: PyPtt

    只能使用安全連線時會拋出的例外。

.. py:exception:: PyPtt.exceptions.SetConnectMailFirst
    :module: PyPtt

    請先設定聯絡信箱時會拋出的例外。