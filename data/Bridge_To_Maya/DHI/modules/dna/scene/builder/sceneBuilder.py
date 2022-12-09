import imp
from math import pi
from pymel.core.general import MayaNodeError

from DHI.core.error import DNAEstimatorError
from DHI.core.logger import Logger
from DHI.modules.dna.dnaprovider import DNAProvider
from DHI.modules.dna.scene.builder.analogGuiBuilder import AnalogGuiBuilder
from DHI.modules.dna.scene.builder.characterBuilder import CharacterBuilder
from DHI.modules.file.handler import FileHandler
import pymel.core as pycore
import DHI.core.progressWindowManager as progressWindowManager

try:
    # Python 2
    xrange
except NameError:
    # Python 3, xrange is now named range
    xrange = range

class SceneBuilderError(DNAEstimatorError):
    def __init__(self, message):
        self.message = "Scene creation failed! Reason: %s" % (message)


class SceneBuilder(object):
    '''
    @TODO write description
    '''
    logger = Logger.getInstance(__name__)

    def __init__(self):
        self._dnaProvider = None
        self._destinationPath = None
        self._sceneName = "DefaultSceneName"
        self._sceneExtension = ".mb"
        self._guiPath = None
        self._analogGuiOptions = None
        self._isDebug = False
        self._joints = None
        self._rigLogicNodeBuilder = None
        self._addNormalsForHeadMesh = False
        self._addNormals = False
        self._linearUnit = None
        self._angleUnit = None
        self._aasPath = None
        self._aasMethod = None
        self._buildBlendShapes = False
        # needed only if isDebug flag is active
        self._buildSkin = False
        self._gender = ''
        self._height = ''
        self._meshNames = []
        self._FRMCtrl = None
        self._sceneOrientation = None

    def FromDnaPath(self, dnaPath):
        self._dnaProvider = DNAProvider(dnaPath)
        return self

    def WithGui(self, guiPath):
        self._guiPath = guiPath
        return self

    def WithAAS(self, aasPath, aasMethod=None):
        self._aasPath = aasPath
        self._aasMethod = aasMethod
        return self

    def WithFRMAttrs(self, name):
        self._FRMCtrl = name
        return self

    def WithSceneOrientation(self, orientation):
        self._sceneOrientation = orientation
        return self

    def WithCharacterHeight(self, height):
        self._height = height
        return self

    def WithGender(self, gender):
        self._gender = gender
        return self

    def WithAnalogGuiOptions(self, guiOptions):
        self._analogGuiOptions = guiOptions
        return self

    def ForDebug(self):
        self._isDebug = True
        return self

    def SaveToDestination(self, destinationPath):
        self._destinationPath = destinationPath
        return self

    def WithName(self, sceneName):
        self._sceneName = sceneName
        return self

    def WithExtension(self, sceneExtension):
        self._sceneExtension = sceneExtension
        return self

    def WithRigLogicNodeBuilder(self, rlNodeBuilder):
        self._rigLogicNodeBuilder = rlNodeBuilder
        return self

    def And(self):
        return self

    def ForMesh(self, name):
        self._meshNames.append(name)
        return self

    def WithBlendshapes(self):
        self._buildBlendShapes = True
        return self

    def WithSkin(self):
        self._buildSkin = True
        return self

    def WithNormals(self):
        self._addNormals = True
        return self

    def WithNormalsForHeadMesh(self):
        self._addNormalsForHeadMesh = True
        return self

    def WithLinearUnit(self, unit):
        self._linearUnit = unit
        return self

    def WithAngleUnit(self, unit):
        self._angleUnit = unit
        return self

    def build(self):
        if not self._dnaProvider:
            raise SceneBuilderError("DNA path was not provided!")
        try:
            dnaLinearUnit = DNAProvider.getLinearUnitFromInt(self._dnaProvider.getTranslationUnit())
            dnaAngleUnit = DNAProvider.getAngleUnitFromInt(self._dnaProvider.getRotationUnit())

            linearModifier = self._calculateLinearModifier(dnaLinearUnit)
            angleModifier = self._calculateAngleModifier(dnaAngleUnit)

            pycore.currentUnit(linear=self._linearUnit, angle=self._angleUnit)

            progressWindowManager.update(0, "Reading all neutral joints")
            self._joints = self._dnaProvider.readAllNeutralJoints(False)

            progressWindowManager.update(0, "Processing joints")
            processor = SceneBuilder.JointsProcessor(self._dnaProvider.readAllNeutralJoints(), linearModifier,
                                                     angleModifier)
            processor.process()

            if self._isDebug:
                self._buildDebugScene(linearModifier)
            else:
                self._buildRegularScene(linearModifier)

            if self._guiPath:
                if not self._FRMCtrl:
                    raise SceneBuilderError("FRM_WMultipliers control name not provided!")
                pycore.importFile(self._guiPath)
                self._createCtrlAttributes()
                self._createFRMAttributes()

            if self._analogGuiOptions:
                self._setAnalogGuiPositions()

            if self._rigLogicNodeBuilder:
                pycore.mel.eval(self._rigLogicNodeBuilder.build())

            if self._aasPath:
                self._runAfterAssemblyScript(self._aasMethod)

            if self._destinationPath:
                pycore.saveAs(FileHandler.joinPath((self._destinationPath, self._sceneName + self._sceneExtension)))
        except SceneBuilderError:
            raise
        except Exception as ex:
            raise SceneBuilderError(ex.message)

    def _setAnalogGuiPositions(self):
        agb = AnalogGuiBuilder(self._analogGuiOptions)
        agb.build()

    def _createFRMAttributes(self):
        ctrlName = self._FRMCtrl

        frmNames = self._dnaProvider.getAnimatedMapNames()

        for name in frmNames:
            legalName = name.replace(".", "_")
            pycore.addAttr(ctrlName, longName=legalName, keyable=True, attributeType="float", minValue=0.0,
                           maxValue=1.0)

    def _createCtrlAttributes(self):
        guiControlNames = self._dnaProvider.getRawControlNames()

        for name in guiControlNames:
            ctrlAndAttrNames = name.split(".")
            pycore.addAttr(ctrlAndAttrNames[0], longName=ctrlAndAttrNames[1], keyable=True, attributeType="float",
                           minValue=0.0, maxValue=1.0)

    def _buildRegularScene(self, linearModifier):
        progressWindowManager.update(0, "Creating target meshes")
        for meshId in xrange(self._dnaProvider.getMeshCount()):
            createCharacter = CharacterBuilder()

            createCharacter.WithMeshId(meshId).And().WithDnaProvider(self._dnaProvider).And().WithJoints(
                self._joints).And(). \
                WithMesh().And().WithSkin().And().WithBlendshape().And().WithLinearModifier(linearModifier)

            if meshId == 0:
                if self._addNormalsForHeadMesh:
                    createCharacter.WithNormals()
            elif self._addNormals:
                createCharacter.WithNormals()

            createCharacter.Now()

    def _buildDebugScene(self, linearModifier):
        for name in self._meshNames:
            index = self._dnaProvider.getMeshIndexFromName(name)

            if index == -1:
                raise SceneBuilderError("Mesh with given name does not exist in DNA file.")

            createCharacter = CharacterBuilder()

            createCharacter.WithMeshId(index).And().WithDnaProvider(self._dnaProvider).And().WithJoints(
                self._joints).And().WithMesh().And().WithLinearModifier(linearModifier)

            if self._buildBlendShapes:
                createCharacter.WithBlendshape()

            if self._buildSkin:
                createCharacter.WithSkin()

            if index == 0:
                if self._addNormalsForHeadMesh:
                    createCharacter.WithNormals()
            elif self._addNormals:
                createCharacter.WithNormals()

            createCharacter.Now()

    def _calculateLinearModifier(self, dnaLinearUnit):
        '''
        @TODO - this conversion method should be placed in the conversion class.
        Right now the only two valid values are "m" and "cm"
        '''
        modifier = 1

        if self._linearUnit != dnaLinearUnit:
            if self._linearUnit == "m":
                modifier = 0.01
            else:
                modifier = 100

        return modifier

    def _calculateAngleModifier(self, dnaAngleUnit):
        '''
        @TODO - this conversion method should be placed in the conversion class.
        Right now the only two valid values are "radian" and "degree"
        '''
        modifier = 1

        if self._angleUnit != dnaAngleUnit:
            if self._angleUnit == "degree":
                modifier = 180 / pi
            else:
                modifier = pi / 180

        return modifier

    def _runAfterAssemblyScript(self, method):
        self._aasPath = FileHandler.cleanPath(self._aasPath)

        if FileHandler.isFile(self._aasPath) and self._aasPath.endswith(".py"):
            aas = imp.load_source("aas", self._aasPath)
            self.logger.info("Starting post assemble script")
            if method:
                getattr(aas, method)(self._dnaProvider, self._sceneOrientation)
            else:
                aas.interfacePostAssemble(self._dnaProvider, self._sceneOrientation, self._gender, self._height)

            self.logger.info("Post assemble script completed.")
        else:
            raise SceneBuilderError("After assembly script is not valid. Check: %s" % self._aasPath)

    class JointsProcessor(object):
        def __init__(self, joints, linearModifier, angleModifier):
            self._joints = joints
            self._linearModifier = linearModifier
            self._angleModifier = angleModifier

            self._jointFlags = {}

            for jointName in self._joints:
                self._jointFlags[jointName] = False

        def _addJointToScene(self, joint):
            if self._jointFlags[joint.name]:
                return

            inParentSpace = True
            try:
                pycore.select(joint.parentName)
            except (pycore.MayaNodeError, ValueError, TypeError):
                if not joint.name == joint.parentName:
                    self._addJointToScene(self._joints[joint.parentName])
                else:
                    pycore.select(d=True)
                    inParentSpace = False

            position = (self._linearModifier * joint.translation.X, self._linearModifier * joint.translation.Y,
                        self._linearModifier * joint.translation.Z)
            orientation = (self._angleModifier * joint.orientation.X, self._angleModifier * joint.orientation.Y,
                           self._angleModifier * joint.orientation.Z)
            pycore.joint(p=position, o=orientation, n=joint.name, r=inParentSpace, a=not inParentSpace)
            self._jointFlags[joint.name] = True

        def process(self):
            progressIncrementVal = progressWindowManager.calculateProgressStepValue(len(self._joints),
                                                                                    progressWindowManager.percentage[
                                                                                        'HEAD_JOINTS'])
            try:
                joints = self._joints.itervalues()
            except:
                joints = self._joints.values()

            for joint in joints:
                progressWindowManager.update(progressIncrementVal, "Adding joints")
                self._addJointToScene(joint)
