
class ErrorCode(object):
    def __init__(self):
        self.Success =                          0
        self.UnknowError =                    0.1
        self.ConnectError =                     1
        self.EOFErrorCode =                     2
        self.ConnectResetError =                3
        self.WaitTimeout =                      4
        self.WrongPassword =                    5
        self.ErrorInput =                       6
        self.PostNotFound =                     7
        self.ParseError =                       8
        self.PostDeleted =                      9
        self.WebFormatError =                  10
        self.NoPermission =                    11
        self.NoUser =                          12
        self.InvalidURLError =                 13
        self.LoginFrequently =                 14
        self.MailBoxFull =                     15
        self.SSHFail =                         16
        self.NoFastPush =                      17
        self.NoEnoughP =                       18
        self.OSError =                         19
        self.HasControlCode =                  20
        self.PttBug =                          21