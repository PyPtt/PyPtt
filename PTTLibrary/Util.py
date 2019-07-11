import os
import sys
import time

try:
    import DataType
    import Config
    import Util
except ModuleNotFoundError:
    from . import DataType
    from . import Config
    from . import Util


def checkRange(DefineObj, Value):
    if Value < DefineObj.MinValue or DefineObj.MaxValue < Value:
        return False
    return True


def getFileName(String):
    result = os.path.basename(String)
    result = result[:result.find('.')]
    return result


def getSubStringList(MainString, TargetA, TargetB):

    result = []

    if not isinstance(TargetB, list):
        TargetB = [TargetB]

    while TargetA in MainString:
        Temp = MainString[MainString.find(TargetA) + len(TargetA):]

        BestIndex = len(MainString)
        for B in TargetB:
            CurrentIndex = Temp.find(B)
            if CurrentIndex < BestIndex and CurrentIndex >= 0:
                BestIndex = CurrentIndex

        if BestIndex != len(TargetB):
            Temp = Temp[:BestIndex].strip()
            result.append(Temp)
        
        MainString = MainString[MainString.find(TargetA) + len(TargetA):]
    
    return result
