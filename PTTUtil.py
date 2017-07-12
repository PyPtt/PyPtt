import sys
import time
from time import gmtime, strftime

def Log(InputMessage):
    TotalMessage = "[" + strftime("%Y-%m-%d %H:%M:%S") + "] " + InputMessage
    #text.encode(sys.stdout.encoding)
    #print(TotalMessage.encode('utf-8-sig', 'ignore').decode('utf-8-sig'))
    print(TotalMessage.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding))
    #
def getTime():
    return strftime("%H:%M")
    