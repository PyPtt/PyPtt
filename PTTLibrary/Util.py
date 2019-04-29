import sys
import time
from time import gmtime, strftime


def log(InputMessage):
    TotalMessage = "[" + strftime("%m-%d %H:%M:%S") + "]" + InputMessage

    try:
        print(TotalMessage.encode(sys.stdin.encoding, 
                                  "replace").decode(sys.stdin.encoding))
    except Exception:
        print(TotalMessage.encode('utf-8', "replace").decode('utf-8'))


def getTime():
    return strftime("%H:%M")


def showValue(Msg, Value):

    TotalMessage = []
    TotalMessage.append(Msg)
    TotalMessage.append(' [')
    TotalMessage.append(str(Value))
    TotalMessage.append(']')

    log(''.join(TotalMessage))
    
