
class API(object):

    def __init__(self):
        pass

    def operatePTT(self, SendMessage):
        
        self.__APILock[ConnectIndex].acquire()

        result = self.__operatePTT(SendMessage=SendMessage, Refresh=True)

        self.__WaterBallProceeor()
        self.__APILock[ConnectIndex].release()
        
        return result

    def __operatePTT(self, SendMessage='', CatchTargetList=[], Refresh=False, ExtraWait=0):
        
        SendMessageTimeout = 10.0
        PreWait = self.__PreWait
        EveryWait = self.__EveryWait

        MaxEveryWait = self.__MaxEveryWait
        MinEveryWait = self.__MinEveryWait

        if CatchTargetList == None:
            CatchTargetList = []
        
        ErrCode = ErrorCode.Success
        
        self.__PreReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex]
        self.__ReceiveData[ConnectIndex] = ''

        try:
            if SendMessage != '':
                if Refresh:
                    SendMessage += self.__Refresh
                
                TimeCout = 0
                StartTime = time.time()
                time.sleep(PreWait)
                while not self.__ConnectList[ConnectIndex].channel.send_ready():
                    time.sleep(EveryWait)

                    if TimeCout >= 100:
                        TimeCout = 0
                        NowTime = time.time()
                        if (NowTime - StartTime) >= SendMessageTimeout:
                            self.Log('超時斷線，重新連線')
                            self.__connectRemote(ConnectIndex)
                            return self.__operatePTT(ConnectIndex, SendMessage, CatchTargetList, Refresh, ExtraWait)
                    TimeCout += 1
                try:
                    EncodeMessage, Len = uao.encode(SendMessage)
                except:
                    EncodeMessage = SendMessage.encode('big5', 'replace')
                self.__ConnectList[ConnectIndex].channel.send(EncodeMessage)
            
            TimeCout = 0
            StartTime = time.time()
            time.sleep(PreWait)
            while not self.__ConnectList[ConnectIndex].channel.recv_ready():
                time.sleep(EveryWait)

                if TimeCout >= 100:
                    TimeCout = 0
                    NowTime = time.time()
                    if (NowTime - StartTime) >= SendMessageTimeout:
                        self.Log('超時斷線，重新連線')
                        self.__connectRemote(ConnectIndex)
                        return self.__operatePTT(ConnectIndex, SendMessage, CatchTargetList, Refresh, ExtraWait)
                TimeCout += 1

            self.__ReceiveData[ConnectIndex] = self.__wait_str(ConnectIndex)
            while self.__ConnectList[ConnectIndex].channel.recv_ready():
                time.sleep(EveryWait)
                self.__ReceiveData[ConnectIndex] += self.__recv_str(ConnectIndex)

            
            DelateDetect = [False] * 5
            while DelateDetect.count(True) == 5:
                DelateDetect = [False] * 5
                for i in range(5):
                    time.sleep(PreWait)
                    while self.__ConnectList[ConnectIndex].channel.recv_ready():
                        DelateDetect[i] = True
                        time.sleep(EveryWait)
                        self.__ReceiveData[ConnectIndex] += self.__recv_str(ConnectIndex)
            
            DelateDetectCount = DelateDetect.count(True)

            if DelateDetectCount > 3:
                EveryWait += 0.01
                if EveryWait > MaxEveryWait:
                    EveryWait = MaxEveryWait
            elif DelateDetectCount == 0:
                EveryWait -= 0.01
                if EveryWait < MinEveryWait:
                    EveryWait = MinEveryWait
                
        except socket.timeout:
            self.Log('超時斷線，重新連線')
            self.__connectRemote(ConnectIndex)
            return self.__operatePTT(ConnectIndex, SendMessage, CatchTargetList, Refresh, ExtraWait)
        except OSError:
            self.Log('作業系統錯誤斷線，重新連線')
            self.__connectRemote(ConnectIndex)
            return self.__operatePTT(ConnectIndex, SendMessage, CatchTargetList, Refresh, ExtraWait)
        except KeyboardInterrupt:
            self.Log('使用者中斷')
            self.__ErrorCode = ErrorCode.UserInterrupt
            return self.__ErrorCode, -1
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
            self.Log('斷線，重新連線')
            if self.__ErrorCode != ErrorCode.UserInterrupt:
                self.__connectRemote(ConnectIndex)
            else:
                return self.__ErrorCode, -1
            return self.__operatePTT(ConnectIndex, SendMessage, CatchTargetList, Refresh, ExtraWait)

        # self.__ReceiveData[ConnectIndex] = self.__ReceiveData[ConnectIndex].decode(encoding='big5',errors='ignore')
        # self.__ReceiveRawData[ConnectIndex] = self.__ReceiveData[ConnectIndex]
        self.__ReceiveRawData[ConnectIndex], Len = uao.decode(self.__ReceiveData[ConnectIndex])

        self.__ReceiveData[ConnectIndex] = self.__ReceiveRawData[ConnectIndex]

        self.__ReceiveRawData[ConnectIndex] = self.__cleanScreen(self.__ReceiveRawData[ConnectIndex], NoColor=False)
        self.__ReceiveData[ConnectIndex] = self.__cleanScreen(self.__ReceiveData[ConnectIndex])
        if ConnectIndex == 0:
            self.ReceiveData = self.__ReceiveData[ConnectIndex]

        if self.__WaterBallHandler != None:
            line = self.__ReceiveData[ConnectIndex].split('\n').pop()
                # if '★' in line:
            if line.startswith('  ★'):
                line = line[3:]
                WaterBallAuthor = line[:line.find(' ')]
                WaterBallContent = line[line.find(' ') + 1:line.find(' [K')]
                # print('WaterBallAuthor: =' + WaterBallAuthor + '=')
                # print('WaterBallContent: =' + WaterBallContent + '=')
                CurrentWaterBall = Information.WaterBallInformation(WaterBallType.Catch, WaterBallAuthor, WaterBallContent)
                self.__WaterBallList.append(CurrentWaterBall)
                
        for i in range(len(CatchTargetList)):
            if CatchTargetList[i] in self.__ReceiveData[ConnectIndex]:
                self.__ConnectList[ConnectIndex].channel.settimeout(self.__DefaultTimeout)
                return ErrorCode.Success, i

        self.__ConnectList[ConnectIndex].channel.settimeout(self.__DefaultTimeout)

        self.__ErrorCode = ErrCode
        return ErrCode, -1
    def __cleanScreen(self, screen, NoColor=True):
        if not screen:
            return screen
        # http://asf.atmel.com/docs/latest/uc3l/html/group__group__avr32__utils__print__funcs.html#ga024c3e2852fe509450ebc363df52ae73
        
        PreNewLineMark = -1
        PTTLibraryNewLineMark = '==PTTLibraryNewLineMark=='
        for NewLineMark in range(1, 25):
            for Type in range(1, 26):
                Target = '[' + str(NewLineMark) + ';' + str(Type) + 'H'
                if Target in screen:

                    if PreNewLineMark == -1:
                        NewLineCount = screen[:screen.find(Target)].count('\n')

                        NewLine = NewLineMark - NewLineCount - 1
                        # if ShowTarget in screen:
                        #     print('NewLineMark', NewLineMark)
                        #     print('NewLineCount', NewLineCount)
                        #     print('NewLine', NewLine)
                        if NewLine < 1:
                            NewLine = 1
                        screen = screen.replace(Target, PTTLibraryNewLineMark * NewLine)
                    else:
                        NewLineMarkCount = NewLineMark - PreNewLineMark
                        NewLineCount = screen[screen.rfind(PTTLibraryNewLineMark) : screen.find(Target)].count('\n')
                        NewLine = NewLineMarkCount - NewLineCount
                        # if ShowTarget in screen:
                        #     print('NewLineMark', NewLineMark)
                        #     print('NewLineCount', NewLineCount)
                        #     print('NewLine', NewLine)

                        if NewLine < 1:
                            NewLine = 1

                        screen = screen.replace(Target, PTTLibraryNewLineMark * NewLine)

                    PreNewLineMark = NewLineMark
        
        screen = screen.replace(PTTLibraryNewLineMark, '\n')
        # if ShowTarget in screen:
        #     self.Log('----------------------')
        #     self.Log(str(screen))
        #     self.Log('----------------------')
        # screen = screen.replace('[2J    ', '')
        screen = screen.replace('[2J', '')

        if NoColor:
            screen = re.sub('\[[\d+;]*[mH]', '', screen)

        screen = re.sub(r'[\r]', '', screen)
        screen = re.sub(r'[\x00-\x08]', '', screen)
        screen = re.sub(r'[\x0b\x0c]', '', screen)
        screen = re.sub(r'[\x0e-\x1f]', '', screen)
        screen = re.sub(r'[\x7f-\xff]', '', screen)
        # self.Log('after: ' + str(screen))
        return screen
    def __wait_str(self, ConnectIndex):
        ch = ''
        while True:
            ch = self.__ConnectList[ConnectIndex].channel.recv(1)
            if ch:
                break
        # return self.__dec_bytes(ch)
        return ch
    def __recv_str(self, ConnectIndex):
        # return self.__dec_bytes(self.__ConnectList[ConnectIndex].channel.recv(self.buf_size))
        return self.__ConnectList[ConnectIndex].channel.recv(self.buf_size)
    # decode byte array to UTF-8 string
    def __dec_bytes(self, bytes):
        return bytes.decode('utf-8', errors='ignore')