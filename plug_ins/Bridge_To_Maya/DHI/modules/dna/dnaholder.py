import dna
from DHI.core.error import DNAEstimatorError
from DHI.modules.file.handler import FileHandler
from DHI.modules.maya.util import MayaUtil


class DNAHolderError(DNAEstimatorError):
    def __init__(self, errorMsg):
        self.message = "DNAHolder creation failed! %s." % (errorMsg)


try:
    # Python 2
    xrange
except NameError:
    # Python 3, xrange is now named range
    xrange = range


class DNAHolder(object):

    def __init__(self, binaryFilePath):
        self._fileStream = None
        self._writer = None
        self._reader = None

        if not FileHandler.isFile(binaryFilePath):
            raise DNAHolderError("File '%s' does not exist." % binaryFilePath)
        MayaUtil.logger.info('Initiatig DNA Holder reader')
        try:
            readStream = dna.FileStream(binaryFilePath.encode('utf-8'), dna.FileStream.AccessMode_Read,
                                    dna.FileStream.OpenMode_Binary)
        except:
            readStream = dna.FileStream(binaryFilePath, dna.FileStream.AccessMode_Read, dna.FileStream.OpenMode_Binary)
        self._reader = dna.StreamReader(readStream)
        self._reader.read()

        readStream.close()

        try:
            self._fileStream = dna.FileStream(binaryFilePath.encode('utf-8'), dna.FileStream.AccessMode_Write,
                                              dna.FileStream.OpenMode_Binary)
        except:
            self._fileStream = dna.FileStream(binaryFilePath, dna.FileStream.AccessMode_Write,
                                          dna.FileStream.OpenMode_Binary)
        self._writer = dna.StreamWriter(self._fileStream)

        self._writer.setFrom(self._reader)

    def writeVertexPositions(self, vertexPositions, meshIndex=0):
        self._writer.setVertexPositions(meshIndex, vertexPositions)
        self._writer.write()

    def readVertexPositions(self, meshIndex=0):
        vertexPosCount = self._reader.getVertexPositionCount(meshIndex)

        vertexPos = []

        for i in xrange(vertexPosCount):
            vertexPos.append(self._reader.getVertexPosition(meshIndex, i))

        return vertexPos

    def getLinearUnit(self):
        value = self._reader.getTranslationUnit()

        if value == 0:
            return "cm"
        elif value == 1:
            return "m"
        else:
            raise DNAHolderError("Unknown linear unit set in DNA file! value %s" % value)

    def getJointCount(self):
        return self._reader.getJointCount()

    def getJointName(self, jointIndex):
        return self._reader.getJointName(jointIndex)

    def getNeutralJointTranslation(self, jointIndex):
        return self._reader.getNeutralJointTranslation(jointIndex)

    def getNeutralJointRotation(self, jointIndex):
        return self._reader.getNeutralJointRotation(jointIndex)

    def getParentName(self, jointIndex):
        parentIndex = self._reader.getJointParentIndex(jointIndex)
        return self.getJointName(parentIndex)

    def getVertexPositionCount(self, meshIndex):
        return self._reader.getVertexPositionCount(meshIndex)

    def getVertexPositionsForMesh(self, meshIndex):
        vertexPositions = []
        for i in xrange(self.getVertexPositionCount(meshIndex)):
            vertexPositions.append(self._reader.getVertexPosition(meshIndex, i))
        return vertexPositions

    def getVertexLayoutPositionIndices(self, meshIndex):
        return self._reader.getVertexLayoutPositionIndices(meshIndex)

    def getVertexLayoutNormalIndices(self, meshIndex):
        return self._reader.getVertexLayoutNormalIndices(meshIndex)

    def getVertexLayoutTextureCoordinateIndices(self, meshIndex):
        return self._reader.getVertexLayoutTextureCoordinateIndices(meshIndex)

    def getFacesForMesh(self, meshIndex):
        faces = []
        for i in xrange(self._reader.getFaceCount(meshIndex)):
            faces.append(self._reader.getFaceVertexLayoutIndices(meshIndex, i))

        return faces

    def getVertexLayoutCount(self, meshIndex):
        return self._reader.getVertexLayoutCount(meshIndex)

    def getVertexNormalsForMesh(self, meshIndex):
        meshVertexNormals = []
        for i in xrange(self._reader.getVertexNormalCount(meshIndex)):
            meshVertexNormals.append(self._reader.getVertexNormal(meshIndex, i))
        return meshVertexNormals

    def getMeshCount(self):
        return self._reader.getMeshCount()

    def getMeshName(self, index):
        return self._reader.getMeshName(index)

    def getAllSkinWeightsValuesForMesh(self, meshIndex):
        skinWeightValues = []
        for i in xrange(self.getVertexPositionCount(meshIndex)):
            skinWeightValues.append(self._reader.getSkinWeightsValues(meshIndex, i))

        return skinWeightValues

    def getAllSkinWeightsJointIndicesForMesh(self, meshIndex):
        jointIndicesForMesh = []
        for i in xrange(self.getVertexPositionCount(meshIndex)):
            jointIndicesForMesh.append(self._reader.getSkinWeightsJointIndices(meshIndex, i))
        return jointIndicesForMesh

    def getBlendShapeChannelName(self, index):
        return self._reader.getBlendShapeChannelName(index)

    def getMaximumInfluencePerVertex(self, meshIndex):
        return self._reader.getMaximumInfluencePerVertex(meshIndex)

    def getBlendShapeTargetCount(self, meshIndex):
        return self._reader.getBlendShapeTargetCount(meshIndex)

    def getBlendshapeTargetDeltasWithVertexId(self, meshIndex, blendshapeTargetIndex):
        indices = self._reader.getBlendShapeTargetVertexIndices(meshIndex, blendshapeTargetIndex)

        deltas = []

        for deltaIndex in xrange(self._reader.getBlendShapeTargetDeltaCount(meshIndex, blendshapeTargetIndex)):
            deltas.append(self._reader.getBlendShapeTargetDelta(meshIndex, blendshapeTargetIndex, deltaIndex))

        if len(deltas) == 0:
            return []

        return zip(indices, deltas)

    def getLODCount(self):
        return self._reader.getLODCount()

    def getMeshIndicesForLOD(self, lod):
        return self._reader.getMeshIndicesForLOD(lod)

    def getBlendshapeNameFromBlendshapeTargetIndex(self, meshIndex, blendshapeTargetIndex):
        globalBSIndex = self._reader.getBlendShapeChannelIndex(meshIndex, blendshapeTargetIndex)

        return self._reader.getBlendShapeChannelName(globalBSIndex)

    def getVertexTextureCoordinatesForMesh(self, meshIndex):
        textureCoordinates = []
        for i in xrange(self._reader.getVertexTextureCoordinateCount(meshIndex)):
            textureCoordinates.append(self._reader.getVertexTextureCoordinate(meshIndex, i))

        return textureCoordinates

    def getTranslationUnit(self):
        return self._reader.getTranslationUnit()

    def getRotationUnit(self):
        return self._reader.getRotationUnit()

    def getRawControlNames(self):
        rawControlCount = self._reader.getRawControlCount()
        controlNames = [self._reader.getRawControlName(i) for i in range(rawControlCount)]

        return controlNames

    def getAnimatedMapNames(self):
        rawMapsCount = self._reader.getAnimatedMapCount()
        mapNames = [self._reader.getAnimatedMapName(i) for i in range(rawMapsCount)]
        return mapNames
