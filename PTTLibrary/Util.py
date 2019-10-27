import os
import traceback


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

        # print(f'>{Temp}')
        MaxIndex = len(MainString)
        BestIndex = MaxIndex
        for B in TargetB:
            CurrentIndex = Temp.find(B)
            if CurrentIndex < BestIndex and CurrentIndex >= 0:
                BestIndex = CurrentIndex
        #         print(f'BestIndex: {BestIndex}')

        # print(f'QQ BestIndex: {BestIndex}')
        # print(f'QQ len(TargetB): {len(TargetB)}')
        if BestIndex != MaxIndex:
            Temp = Temp[:BestIndex].strip()
            result.append(Temp)

        MainString = MainString[MainString.find(TargetA) + len(TargetA):]

    return result


def getCurrentFuncName():
    return traceback.extract_stack(None, 2)[0][2]


def findnth(haystack, needle, n):
    parts = haystack.split(needle, n+1)
    if len(parts) <= n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)
