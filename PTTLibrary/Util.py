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
