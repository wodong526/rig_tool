'''
This module contains importer classes that read data from dna file using stream.
'''
from DHI.core.error import DNAEstimatorError
from DHI.modules.dna.dnaholder import DNAHolder
from DHI.modules.dna.model.joint import Joint
from DHI.modules.dna.scene.transformations import Translation, \
    Orientation

try:
    # Python 2
    xrange
except NameError:
    # Python 3, xrange is now named range
    xrange = range

class DNAProviderError(DNAEstimatorError):
    def __init__(self, missingElement, additionaInfo=""):
        self.message = "Character creation failed. Missing %s! %s" % (missingElement, additionaInfo)

class DNAProvider(object):
    def __init__(self, binaryFilePath):
        self._dnaHolder = DNAHolder(binaryFilePath)

    def _jointsAsDictionary(self, joints):
        '''
        Gets neutral joints from dna, returns dictionary object so they can be searched by name.
    
        @return Python dictionary object. ({ jointName : [tx, ty, tx, jox, joy, joz] })
        @throws MayaSceneError: If joint doesn't exist or bean joints hierarchy is not same as on scene.
        '''
        jointsDict = {}

        for joint in joints:
            jointsDict[joint.name] = joint

        return jointsDict

    def readAllNeutralJointsAsArray(self):
        joints = []

        for jointIndex in xrange(self._dnaHolder.getJointCount()):
            jointName = self._dnaHolder.getJointName(jointIndex)
            translation = self.createTranslation(self._dnaHolder.getNeutralJointTranslation(jointIndex))
            orientation = self.createOrientation(self._dnaHolder.getNeutralJointRotation(jointIndex))
            parentName = self._dnaHolder.getParentName(jointIndex)

            joint = Joint(jointName, translation, orientation, parentName)

            joints.append(joint)

        return joints

    def readAllNeutralJoints(self, asDictionary = True):
        joints = self.readAllNeutralJointsAsArray()

        if not asDictionary:
            return joints
        else:
            return self._jointsAsDictionary(joints)

    def getJointCount(self):
        return self._dnaHolder.getJointCount()

    def getJointName(self, jointIndex):
        return self._dnaHolder.getJointName(jointIndex)

    def getFacesForMesh(self, meshIndex):
        return self._dnaHolder.getFacesForMesh(meshIndex)

    def getMeshCount(self):
        return self._dnaHolder.getMeshCount()

    def getMeshNameFromIndex(self, meshIndex):
        return self._dnaHolder.getMeshName(meshIndex)

    def getMeshIndexFromName(self, meshName):
        for meshId in xrange(self.getMeshCount()):
            if self.getMeshNameFromIndex(meshId) == meshName:
                return meshId

        return -1

    def getMaximumInfluencePerVertex(self, meshIndex):
        return self._dnaHolder.getMaximumInfluencePerVertex(meshIndex)

    def getVertexPositionCount(self, meshIndex):
        return self._dnaHolder.getVertexPositionCount(meshIndex)

    def getVertexPositionsForMesh(self, meshIndex):
        return self._dnaHolder.getVertexPositionsForMesh(meshIndex)

    def getVertexNormalsForMesh(self, meshIndex):
        return self._dnaHolder.getVertexNormalsForMesh(meshIndex)

    def getVertexLayoutPositionIndices(self, meshIndex):
        return self._dnaHolder.getVertexLayoutPositionIndices(meshIndex)

    def getVertexLayoutNormalIndices(self, meshIndex):
        return self._dnaHolder.getVertexLayoutNormalIndices(meshIndex)

    def getSkinWeightMatrixForMesh(self, meshIndex):
        vertexPositionCount = self._dnaHolder.getVertexPositionCount(meshIndex)

        jointIndices = self.getAllSkinWeightsJointIndicesForMesh(meshIndex)
        if len(jointIndices) != vertexPositionCount:
            raise Exception("Number of joint indices and vertex count don't match!")

        skinWeightValues = self._dnaHolder.getAllSkinWeightsValuesForMesh(meshIndex)
        if len(skinWeightValues) != vertexPositionCount:
            raise Exception("Number of skin weight values and vertex count don't match!")

        weightMatrix = []

        for i in xrange(vertexPositionCount):
            if len(jointIndices[i]) != len(skinWeightValues[i]):
                raise Exception("Number of skin weight values and joint indices count don't match for vertex %s!" %i)
            vertexWeights = []
            if len(jointIndices[i]) < 1:
                raise Exception("JointIndexArray for vertex id %s can't be less than one!" %i)
            for j in xrange(len(jointIndices[i])):
                vertexWeights.append(jointIndices[i][j])
                vertexWeights.append(skinWeightValues[i][j])
            weightMatrix.append(vertexWeights)

        return weightMatrix

    def getLODCount(self):
        return self._dnaHolder.getLODCount()

    def getMeshIndicesForLOD(self, lod):
        return self._dnaHolder.getMeshIndicesForLOD(lod)

    def getAllSkinWeightsJointIndicesForMesh(self, meshIndex):
        return self._dnaHolder.getAllSkinWeightsJointIndicesForMesh(meshIndex)

    def getBlendshapeTargetDeltasWithVertexId(self, meshIndex, blendshapeTargetIndex):
        return self._dnaHolder.getBlendshapeTargetDeltasWithVertexId(meshIndex, blendshapeTargetIndex)

    def getBlendShapeTargetCount(self, meshIndex):
        return self._dnaHolder.getBlendShapeTargetCount(meshIndex)

    def getBlendshapeNameFromBlendshapeTargetIndex(self, meshIndex, blendshapeTargetIndex):
        return self._dnaHolder.getBlendshapeNameFromBlendshapeTargetIndex(meshIndex, blendshapeTargetIndex)

    def getVertexLayoutTextureCoordinateIndicesForMesh(self, meshIndex):
        return self._dnaHolder.getVertexLayoutTextureCoordinateIndices(meshIndex)

    def getVertexTextureCoordinatesForMesh(self, meshIndex):
        return self._dnaHolder.getVertexTextureCoordinatesForMesh(meshIndex)

    def getRawControlNames(self):
        return self._dnaHolder.getRawControlNames()

    def getTranslationUnit(self):
        return self._dnaHolder.getTranslationUnit()

    def getRotationUnit(self):
        return self._dnaHolder.getRotationUnit()

    def getAnimatedMapNames(self):
        return self._dnaHolder.getAnimatedMapNames()

    @staticmethod
    def getLinearUnitFromInt(value):
        if value == 0:
            return "cm"
        elif value == 1:
            return "m"
        else:
            raise Exception("Unknown linear unit set in dna file! value %s"%value)

    @staticmethod
    def getAngleUnitFromInt(value):
        if value == 0:
            return "degree"
        elif value == 1:
            return "radian"
        else:
            raise Exception("Unknown angle unit set in dna file! value %s"%value)

    @staticmethod
    def createTranslation(sourceTranslation):
        result = Translation()
        result.X = sourceTranslation[0]
        result.Y = sourceTranslation[1]
        result.Z = sourceTranslation[2]

        return result

    @staticmethod
    def createOrientation(sourceOrientation):
        result = Orientation()
        result.X = sourceOrientation[0]
        result.Y = sourceOrientation[1]
        result.Z = sourceOrientation[2]

        return result
