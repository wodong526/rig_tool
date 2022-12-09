import pymel.core as pycore

class AnalogGuiBuilder(object):
    def __init__(self, options):        
        self._guiPath = options.GuiPath
        self._facialRootJointName = options.FacialRootJointName
        self._leftEyeJointName = options.LeftEyeJointName
        self._rightEyeJointName = options.RightEyeJointName
        
        self._centralDriverName = options.CentralDriverName
        self._leftEyeDriverName = options.LeftEyeDriverName
        self._rightEyeDriverName = options.RightEyeDriverName
        self._leftEyeAimUpName = options.LeftEyeAimUpName
        self._rightEyeAimUpName = options.RightEyeAimUpName
        self._centralAim = options.CentralAim
        self._leAim = options.LeAim
        self._reAim = options.ReAim
    
    def _getElementByNameAndType(self, name, t):
        return pycore.ls(name, type=t)[0]

    def _getLocatorByName(self, name):
        return self._getElementByNameAndType(name, "transform")
   
    def _getJointByName(self, name):
        return self._getElementByNameAndType(name, "joint")

    def _getTranslation(self, element, space="world"):
        return element.getTranslation(space)

    def _setTranslationToElement(self, element, translation, space="world"):
        element.setTranslation(translation, space)
    
    def _importGui(self):
        pycore.importFile(self._guiPath, defaultNamespace=True)
        
    def build(self):
        if self._guiPath != None:
            self._importGui()
        
        self._setTranslationToElement(self._getLocatorByName(self._centralDriverName), self._getTranslation(self._getJointByName(self._facialRootJointName)))
        eyeLPos = self._getTranslation(self._getJointByName(self._leftEyeJointName))
        eyeRPos = self._getTranslation(self._getJointByName(self._rightEyeJointName))

        deltaL = self._getTranslation(self._getLocatorByName(self._leftEyeAimUpName)) - self._getTranslation(self._getLocatorByName(self._leftEyeDriverName))
        deltaR = self._getTranslation(self._getLocatorByName(self._rightEyeAimUpName)) - self._getTranslation(self._getLocatorByName(self._rightEyeDriverName))

        eyeLLocatorPos = self._getTranslation(self._getLocatorByName(self._leAim))
        eyeRLocatorPos = self._getTranslation(self._getLocatorByName(self._reAim))
        centralAimPos = self._getTranslation(self._getLocatorByName(self._centralAim))

        self._setTranslationToElement(self._getLocatorByName(self._leftEyeDriverName), eyeLPos)
        self._setTranslationToElement(self._getLocatorByName(self._rightEyeDriverName), eyeRPos)
        self._setTranslationToElement(self._getLocatorByName(self._leftEyeAimUpName), [eyeLPos[0] + deltaL[0], eyeLPos[1] + deltaL[1], eyeLPos[2] + deltaL[2]])
        self._setTranslationToElement(self._getLocatorByName(self._rightEyeAimUpName), [eyeRPos[0] + deltaR[0], eyeRPos[1] + deltaR[1], eyeRPos[2] + deltaR[2]])

        eyeMiddleDelta = (eyeLPos - eyeRPos) / 2

        eyeMiddle = eyeRPos + eyeMiddleDelta

        self._setTranslationToElement(self._getLocatorByName(self._centralAim), [eyeMiddle[0], eyeMiddle[1], centralAimPos[2]])
        self._setTranslationToElement(self._getLocatorByName(self._leAim), [eyeLPos[0], eyeLPos[1], eyeLLocatorPos[2]])
        self._setTranslationToElement(self._getLocatorByName(self._reAim), [eyeRPos[0], eyeRPos[1], eyeRLocatorPos[2]])
