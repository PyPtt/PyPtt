
import telnetlib
import paramiko
from paramiko import ECDSAKey

try:
    from . import Util
    from . import Config
except:
    import Util
    import Config


class API(object):

    def __init__(self):

        self.Connect = None

        while True:
            try:
                if self.Connect is None:
                    Util.log('連線 ' + str(TelnetConnectIndex) + ' 啟動')
                    self.Connect = telnetlib.Telnet(Config.Host, Config.Port)
                break
            except ConnectionRefusedError:
                self.Log('連接至 ' + self.__host + ' 失敗 10 秒後重試')
                time.sleep(10)
        
        self.Log('連接成功')
    
    