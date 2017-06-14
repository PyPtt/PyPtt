import sys
import time
from time import gmtime, strftime

def Log(InputMessage):
    TotalMessage = "[" + strftime("%Y-%m-%d %H:%M:%S") + "] " + InputMessage

    print(TotalMessage)
def getTime():
    return strftime("%H:%M")
    