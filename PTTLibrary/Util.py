import os
import sys
import time
from time import gmtime, strftime

try:
    from . import DataType
    from . import Config
    from . import Util
except:
    import DataType
    import Config
    import Util


def log(InputMessage):
    if isinstance(InputMessage, list):

        if Config.Language == DataType.Language.Chinese:

            LetterList = 'abcdefghijklmnopqrstuvwxyz'
        
            for i in range(len(InputMessage)):
                Msg = InputMessage[i]
                EnglistStr = True

                for letter in Msg:
                    letter = letter.lower()
                    if letter not in LetterList:
                        EnglistStr = False
                        break
                if EnglistStr:
                    InputMessage[i] = ' ' + InputMessage[i].strip() + ' '

            InputMessage = ''.join(InputMessage)
        else:
            InputMessage = ' '.join(InputMessage)

    InputMessage = InputMessage.replace('  ', ' ')
    TotalMessage = "[" + strftime("%m-%d %H:%M:%S") + "] " + InputMessage

    try:
        print(TotalMessage.encode(sys.stdin.encoding, 
                                  "replace").decode(sys.stdin.encoding))
    except Exception:
        print(TotalMessage.encode('utf-8', "replace").decode('utf-8'))


def getTime():
    return strftime("%H:%M")


def showValue(Msg, Value):

    if isinstance(Msg, list):

        if Config.Language == DataType.Language.Chinese:
            LetterList = 'abcdefghijklmnopqrstuvwxyz'
        
            for i in range(len(Msg)):
                Temp = Msg[i]
                EnglistStr = True
                
                for letter in Temp:
                    letter = letter.lower()
                    if letter not in LetterList:
                        EnglistStr = False
                        break
                if EnglistStr:
                    Msg[i] = ' ' + Msg[i].strip() + ' '

            Msg = ''.join(Msg)
        else:
            Msg = ' '.join(Msg)

    TotalMessage = []
    TotalMessage.append(Msg)
    TotalMessage.append(' [')
    TotalMessage.append(str(Value))
    TotalMessage.append(']')

    log(''.join(TotalMessage))


def checkRange(DefineObj, Value):
    if Value < DefineObj.MinValue or DefineObj.MaxValue < Value:
        return False
    return True


def getFileName(String):
    result = os.path.basename(String)
    result = result[:result.find('.')]
    return result
