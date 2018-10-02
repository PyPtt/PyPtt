import sys
import time
from time import gmtime, strftime

def Log(InputMessage):
    TotalMessage = "[" + strftime("%m-%d %H:%M:%S") + "]" + InputMessage

    try:
        print(TotalMessage.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding))
    except Exception:
        print(TotalMessage.encode('utf-8', "replace").decode('utf-8'))

def getTime():
    return strftime("%H:%M")

def readPostFile(FileName):
    result = ''
    try:
        with open(FileName, encoding = 'utf-8-sig') as File:
            Temp = File.readlines()
            Temp = [x.strip() for x in Temp]
            result = '\r\n'.join(Temp)
    except FileNotFoundError:
        return None
    return result
