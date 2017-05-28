import sys
from time import gmtime, strftime

def Log(InputMessage):
    TotalMessage = "[" + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "] " + InputMessage

    print(TotalMessage)
