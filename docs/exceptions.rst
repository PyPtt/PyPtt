例外
========
| 這裡介紹 PyPtt 的例外。
| 可以用 try...except... 來處理。

| 例外的種類

.. py:exception:: PyPtt.exceptions.RequireLogin
    :module: PyPtt

    需要登入。

.. py:exception:: PyPtt.exceptions.NoPermission
    :module: PyPtt

    沒有權限。

.. py:exception:: PyPtt.exceptions.LoginError
    :module: PyPtt

    登入失敗。

.. py:exception:: PyPtt.exceptions.NoFastComment
    :module: PyPtt

    無法快速推文。

.. py:exception:: PyPtt.exceptions.NoSuchUser
    :module: PyPtt

    查無此使用者。

.. py:exception:: PyPtt.exceptions.NoSuchMail
    :module: PyPtt

    查無此信件。

.. py:exception:: PyPtt.exceptions.NoMoney
    :module: PyPtt

    餘額不足。

.. py:exception:: PyPtt.exceptions.NoSuchBoard
    :module: PyPtt

    查無此看板。

.. py:exception:: PyPtt.exceptions.ConnectionClosed
    :module: PyPtt

    連線已關閉。

.. py:exception:: PyPtt.exceptions.UnregisteredUser
    :module: PyPtt

    未註冊使用者。

.. py:exception:: PyPtt.exceptions.MultiThreadOperated
    :module: PyPtt

    同時使用多個 thread 呼叫 PyPtt 。

.. py:exception:: PyPtt.exceptions.WrongIDorPassword
    :module: PyPtt

    帳號或密碼錯誤。

.. py:exception:: PyPtt.exceptions.WrongPassword
    :module: PyPtt

    密碼錯誤。

.. py:exception:: PyPtt.exceptions.LoginTooOften
    :module: PyPtt

    登入太頻繁。

.. py:exception:: PyPtt.exceptions.UseTooManyResources
    :module: PyPtt

    使用過多資源。

.. py:exception:: PyPtt.exceptions.HostNotSupport
    :module: PyPtt

    主機不支援。詳見 :ref:`host`。

.. py:exception:: PyPtt.exceptions.CantComment
    :module: PyPtt

    禁止推文。

.. py:exception:: PyPtt.exceptions.CantResponse
    :module: PyPtt

    已結案並標記, 不得回應。

.. py:exception:: PyPtt.exceptions.NeedModeratorPermission
    :module: PyPtt

    需要版主權限。

.. py:exception:: PyPtt.exceptions.ConnectError
    :module: PyPtt

    連線失敗。

.. py:exception:: PyPtt.exceptions.NoSuchPost
    :module: PyPtt

    文章不存在。

.. py:exception:: PyPtt.exceptions.CanNotUseSearchPostCode
    :module: PyPtt

    無法使用搜尋文章代碼。

.. py:exception:: PyPtt.exceptions.UserHasPreviouslyBeenBanned
    :module: PyPtt

    `水桶`_ 使用者，但已經被 `水桶`_。

.. py:exception:: PyPtt.exceptions.MailboxFull
    :module: PyPtt

    信箱已滿。

.. py:exception:: PyPtt.exceptions.NoSearchResult
    :module: PyPtt

    搜尋結果為空。

.. py:exception:: PyPtt.exceptions.OnlySecureConnection
    :module: PyPtt

    只能使用安全連線。

.. py:exception:: PyPtt.exceptions.SetContactMailFirst
    :module: PyPtt

    請先設定聯絡信箱。

.. py:exception:: PyPtt.exceptions.ResetYourContactEmail
    :module: PyPtt

    請重新設定聯絡信箱。

.. _水桶: https://pttpedia.fandom.com/zh/wiki/%E6%B0%B4%E6%A1%B6