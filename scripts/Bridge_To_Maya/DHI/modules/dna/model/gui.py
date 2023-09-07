
class AnalogGuiOptions(object):
    '''
    @TODO write class description.
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self._guiPath = None
        self._facialRootJointName = None
        self._leftEyeJointName = None
        self._rightEyeJointName = None
        self._centralDriverName = None
        self._leftEyeDriverName = None
        self._rightEyeDriverName = None
        self._leftEyeAimUpName = None
        self._rightEyeAimUpName = None
        self._centralAim = None
        self._leAim = None
        self._reAim = None
        
    @property
    def GuiPath(self):
        return self._guiPath
    
    @GuiPath.setter
    def GuiPath(self, value):
        self._guiPath = value

    @property
    def FacialRootJointName(self):
        return self._facialRootJointName
    
    @FacialRootJointName.setter
    def FacialRootJointName(self, value):
        self._facialRootJointName = value
    
    @property
    def LeftEyeJointName(self):
        return self._leftEyeJointName

    @LeftEyeJointName.setter
    def LeftEyeJointName(self, value):
        self._leftEyeJointName = value
    
    @property
    def RightEyeJointName(self):
        return self._rightEyeJointName

    @RightEyeJointName.setter
    def RightEyeJointName(self, value):
        self._rightEyeJointName = value
    
    @property
    def CentralDriverName(self):
        return self._centralDriverName
    
    @CentralDriverName.setter
    def CentralDriverName(self, value):
        self._centralDriverName = value
    
    @property
    def LeftEyeDriverName(self):
        return self._leftEyeDriverName

    @LeftEyeDriverName.setter
    def LeftEyeDriverName(self, value):
        self._leftEyeDriverName = value
    
    @property
    def RightEyeDriverName(self):
        return self._rightEyeDriverName

    @RightEyeDriverName.setter
    def RightEyeDriverName(self, value):
        self._rightEyeDriverName = value
    
    @property
    def LeftEyeAimUpName(self):
        return self._leftEyeAimUpName

    @LeftEyeAimUpName.setter
    def LeftEyeAimUpName(self, value):
        self._leftEyeAimUpName = value
    
    @property
    def RightEyeAimUpName(self):
        return self._rightEyeAimUpName

    @RightEyeAimUpName.setter
    def RightEyeAimUpName(self, value):
        self._rightEyeAimUpName = value
    
    @property
    def CentralAim(self):
        return self._centralAim
    
    @CentralAim.setter
    def CentralAim(self, value):
        self._centralAim = value
     
    @property
    def LeAim(self):
        return self._leAim
    
    @LeAim.setter
    def LeAim(self, value):
        self._leAim = value
        
    @property
    def ReAim(self):
        return self._reAim
    
    @ReAim.setter
    def ReAim(self, value):
        self._reAim = value
        
    @staticmethod
    def defaultOptions():
        defaultOptions = AnalogGuiOptions()
        
        defaultOptions.FacialRootJointName = "FACIAL_C_FacialRoot"
        defaultOptions.LeftEyeJointName = "FACIAL_L_Eye"
        defaultOptions.RightEyeJointName = "FACIAL_R_Eye"
        defaultOptions.CentralDriverName = "LOC_C_eyeDriver"
        defaultOptions.LeftEyeDriverName = "LOC_L_eyeDriver"
        defaultOptions.RightEyeDriverName = "LOC_R_eyeDriver"
        defaultOptions.LeftEyeAimUpName = "LOC_L_eyeAimUp"
        defaultOptions.RightEyeAimUpName = "LOC_R_eyeAimUp"
        defaultOptions.CentralAim = "GRP_C_eyesAim"
        defaultOptions.LeAim = "GRP_L_eyeAim"
        defaultOptions.ReAim = "GRP_R_eyeAim"
        
        return defaultOptions