import datetime

import maya.api.OpenMaya as om
import pymel.core as pycore
from DHI.core.logger import Logger
import DHI.core.progressWindowManager as progressWindowManager

BlendshapeGroupPrefix = "BlendshapeGroup_"
BlendshapeNamePostfix = "_blendShapes"
SkinClusterAffix = "skinCluster"

try:
    # Python 2
    xrange
except NameError:
    # Python 3, xrange is now named range
    xrange = range

class Mesh(object):
    logger = Logger.getInstance(__name__)

    def __init__(self, jointIds, jointNames, dnaProvider, meshIndex, linearModifier):
        self._jointNames = jointNames
        self._jointIds = jointIds

        self._dnaProvider = dnaProvider
        self._meshIndex = meshIndex
        self._meshName = self._dnaProvider.getMeshNameFromIndex(self._meshIndex)
        self._dnaVertexPositions = None
        self._dnaVertexLayoutPositions = None
        self._dnaVertexLayoutNormals = None
        self._dnaVertexLayoutUVs = None
        self._vertexPositions = []
        self._vertexNormals = []
        self._vertexUVs = []
        self._dnaFaces = []
        self._polygonFaces = []
        self._polygonConnects = []
        self._vertexNormals = []
        self._derivedMeshNames = []
        self._fnMesh = om.MFnMesh()
        self._meshObject = None
        self._dagModifier = om.MDagModifier()

        self._linearModifier = linearModifier

    def createNeutralMesh(self):
        self._prepareMesh()

        self._meshObject = self._fnMesh.create(self._vertexPositions, self._polygonFaces, self._polygonConnects)

        self._dagModifier.renameNode(self._meshObject, self._meshName)
        self._dagModifier.doIt()

        self._addTextureCoordinates()

    def addNormals(self):
        self._addNormals()

    def addSkin(self):
        self._addSkinCluster()
        self._setSkinWeights()

    def addBlendshapes(self):
        if self._dnaProvider.getBlendShapeTargetCount(self._meshIndex) > 0:
            self._createAllDerivedMeshes()
            self._createBlendshapeNode()

    def _prepareMesh(self):
        self._dnaVertexPositions = self._dnaProvider.getVertexPositionsForMesh(self._meshIndex)
        self._dnaVertexLayoutPositions = self._dnaProvider.getVertexLayoutPositionIndices(self._meshIndex)

        for position in self._dnaVertexPositions:
            self._vertexPositions.append(
                om.MPoint(self._linearModifier * position[0], self._linearModifier * position[1],
                          self._linearModifier * position[2]))

        self._dnaFaces = self._dnaProvider.getFacesForMesh(self._meshIndex)

        for vertexLayoutIndexArray in self._dnaFaces:
            self._polygonFaces.append(len(vertexLayoutIndexArray))
            for i in range(len(vertexLayoutIndexArray)):
                self._polygonConnects.append(self._dnaVertexLayoutPositions[vertexLayoutIndexArray[i]])

    def _addSkinCluster(self):
        self.logger.debug("Adding skin cluster...")
        maximumInfluences = self._dnaProvider.getMaximumInfluencePerVertex(self._meshIndex)

        pycore.select(self._jointNames[0], replace=True)
        pycore.select(self._meshName, add=True)
        skinCluster = pycore.skinCluster(toSelectedBones=True, name=self._meshName + "_" + SkinClusterAffix,
                                         maximumInfluences=maximumInfluences, skinMethod=0, obeyMaxInfluences=True)
        if len(self._jointNames) > 1:
            pycore.skinCluster(skinCluster, edit=True, addInfluence=self._jointNames[1:], weight=0)

        self.logger.debug("Adding skin cluster done. Skin cluster created.")

    def _setSkinWeights(self):
        skinWeights = self._dnaProvider.getSkinWeightMatrixForMesh(self._meshIndex)

        # import skin weights
        tempStr = self._meshName + "_" + SkinClusterAffix + ".wl["
        for vertexId in xrange(len(skinWeights)):
            if vertexId % 500 == 0:
                self.logger.debug("Vertex: %s / %s" % (vertexId, len(skinWeights)))
            vertexInfo = skinWeights[vertexId]

            # set all skin weights to zero
            vertexString = tempStr + str(vertexId) + "].w["
            pycore.setAttr(vertexString + "0]", 0.0)

            # import skin weights
            for w in range(0, len(vertexInfo), 2):
                pycore.setAttr(vertexString + str(self._jointIds.index(vertexInfo[w])) + "]", float(vertexInfo[w + 1]))

    def _getTotalBlendShapeTargetCount(self):
        '''
            Fetch blend shape target count for all DNA meshes
        Returns
        -------

        '''
        total = 0
        for meshId in xrange(self._dnaProvider.getMeshCount()):
            total += self._dnaProvider.getBlendShapeTargetCount(meshId)
        return total

    def _createAllDerivedMeshes(self):
        group = pycore.group(empty=True, name=BlendshapeGroupPrefix + self._meshName)

        total = self._getTotalBlendShapeTargetCount()
        progressIncrementVal = progressWindowManager \
            .calculateProgressStepValue(total, progressWindowManager.percentage['HEAD_CREATE_DERIVED_MESHES'])

        for blendshapeTargetIndex in xrange(self._dnaProvider.getBlendShapeTargetCount(self._meshIndex)):
            progressWindowManager.update(progressIncrementVal, "Creating target mesh %s / %s" % (blendshapeTargetIndex, total))

            if blendshapeTargetIndex % 50 == 0:
                self.logger.info("Creating target mesh %s / %s" % (blendshapeTargetIndex, self._dnaProvider.getBlendShapeTargetCount(self._meshIndex)))
            self._createDerivedMesh(blendshapeTargetIndex, group)

        group.visibility.set(0)

    def _createDerivedMesh(self, blendshapeTargetIndex, group):
        derivedName = self._dnaProvider.getBlendshapeNameFromBlendshapeTargetIndex(self._meshIndex,
                                                                                   blendshapeTargetIndex)
        zippedDeltas = self._dnaProvider.getBlendshapeTargetDeltasWithVertexId(self._meshIndex, blendshapeTargetIndex)

        newVertLayout = []

        for position in self._dnaVertexPositions:
            newVertLayout.append(om.MPoint(self._linearModifier * position[0], self._linearModifier * position[1],
                                           self._linearModifier * position[2]))

        for zippedDelta in zippedDeltas:
            delta = zippedDelta[1]
            newVertLayout[zippedDelta[0]] += (
                om.MPoint(self._linearModifier * delta[0], self._linearModifier * delta[1],
                          self._linearModifier * delta[2]))

        newMesh = self._fnMesh.create(newVertLayout, self._polygonFaces, self._polygonConnects)

        self._dagModifier.renameNode(newMesh, derivedName)
        self._dagModifier.doIt()

        newNode = pycore.PyNode(derivedName)
        newNode.setParent(group)

        self._derivedMeshNames.append(derivedName)

    def _createBlendshapeNode(self):
        nodes = []
        for meshName in self._derivedMeshNames:
            nodes.append(pycore.PyNode(meshName))

        pycore.select(nodes, replace=True)
        meshNode = pycore.PyNode(self._meshName)
        pycore.select(meshNode, add=True)
        pycore.blendShape(name=self._meshName + BlendshapeNamePostfix)
        pycore.delete(BlendshapeGroupPrefix + self._meshName)

    def _addNormals(self, space=om.MSpace.kObject):
        self._vertexNormals = self._dnaProvider.getVertexNormalsForMesh(self._meshIndex)
        self._dnaVertexLayoutNormals = self._dnaProvider.getVertexLayoutNormalIndices(self._meshIndex)

        normalArray = []
        faceArray = []
        vertexArray = []

        for faceIndex, vertexLayoutIndexArray in enumerate(self._dnaFaces):
            for i in range(len(vertexLayoutIndexArray)):
                vertexLayoutIndex = vertexLayoutIndexArray[i]
                vertexNormalRaw = self._vertexNormals[self._dnaVertexLayoutNormals[vertexLayoutIndex]]
                vertexNormal = om.MVector(vertexNormalRaw[0], vertexNormalRaw[1], vertexNormalRaw[2])
                normalArray.append(vertexNormal)
                faceArray.append(faceIndex)
                vertexId = self._dnaVertexLayoutPositions[vertexLayoutIndex]
                vertexArray.append(vertexId)

        self._fnMesh.setFaceVertexNormals(normalArray, faceArray, vertexArray, space)

    def _addTextureCoordinates(self):
        textureCoordinates = self._dnaProvider.getVertexTextureCoordinatesForMesh(self._meshIndex)
        coordinateIndices = self._dnaProvider.getVertexLayoutTextureCoordinateIndicesForMesh(self._meshIndex)

        textureCoordinateUs = []
        textureCoordinateVs = []
        textureCoordinateIndices = []

        indexCounter = 0

        for vertexLayoutIndexArray in self._dnaFaces:
            for i in range(len(vertexLayoutIndexArray)):
                textureCoordinate = textureCoordinates[coordinateIndices[vertexLayoutIndexArray[i]]]
                textureCoordinateUs.append(textureCoordinate[0])
                textureCoordinateVs.append(textureCoordinate[1])
                textureCoordinateIndices.append(indexCounter)
                indexCounter += 1

        self._fnMesh.setUVs(textureCoordinateUs, textureCoordinateVs)
        self._fnMesh.assignUVs(self._polygonFaces, textureCoordinateIndices)

        pycore.select(self._meshName, replace=True)
        pycore.polyMergeUV(self._meshName, distance=0.01, constructionHistory=False)
