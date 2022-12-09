
class RigLogicNodeBuilder(object):
    '''
    This class is responsible for creating RigLogic maya nod.
    '''
    def __init__(self):
        '''
        Constructor
        ''' 
        self._command = "createEmbeddedNodeRL4"
        self._name = ""
        self._flags = dict()
        self._flags["-dfp"] = ""
        self._flags["-cn"] = "<objName>.<attrName>" 
        self._flags["-jn"] = "<objName>.<attrName>"
        self._flags["-bsn"] = "<objName>_blendShapes.<attrName>"
        self._flags["-amn"] = "FRM_WMmultipliers.<objName>_<attrName>"
    
    def setName(self, name):
        self._name = name    
        
    def setFlag(self, flagName, flagValue):
        self._flags[flagName] = flagValue  
       
    
    def build(self):
        returnString = self._command + " -n \"" + self._name + "\""
        try:
            items = self._flags.iteritems()
        except:
            items = self._flags.items()

        for pair in items:
            returnString += " " + pair[0]
            if pair[1]:
                returnString += " \"" + pair[1] + "\""
                
        return returnString
    
    
    

    
