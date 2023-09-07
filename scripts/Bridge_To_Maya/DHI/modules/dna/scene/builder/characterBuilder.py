from DHI.core.error import DNAEstimatorError
from DHI.modules.dna.model.mesh import Mesh
try:
    # Python 2
    xrange
except NameError:
    # Python 3, xrange is now named range
    xrange = range

class CharacterBuilderError(DNAEstimatorError):
    def __init__(self, missingElement, additionaInfo=""):
        self.message = "Character creation failed. Missing %s! %s" % (missingElement, additionaInfo)


class CharacterBuilder(object):
    '''
    TODO add comments
    '''

    def __init__(self):
        self._meshIndex = None
        self._createMesh = False
        self._createSkin = False
        self._createBlendshape = False
        self._addNormals = False
        self._dnaProvider = None
        self._jointNames = None
        self._jointIds = None
        self._linearModifier = None

    def WithJoints(self, jointsArray):
        self._prepareJoints(jointsArray)
        return self

    def WithDnaProvider(self, dnaProvider):
        self._dnaProvider = dnaProvider
        return self

    def WithMeshId(self, meshIndex):
        self._meshIndex = int(meshIndex)
        return self

    def WithMesh(self):
        self._createMesh = True
        return self

    def WithBlendshape(self):
        self._createBlendshape = True
        return self

    def WithSkin(self):
        self._createSkin = True
        return self

    def And(self):
        return self

    def WithNormals(self):
        self._addNormals = True
        return self

    def WithLinearModifier(self, value):
        self._linearModifier = value
        return self

    def _prepareJoints(self, jointsArray):
        jointsTemp = []
        jointIndices = self._dnaProvider.getAllSkinWeightsJointIndicesForMesh(self._meshIndex)
        for i in xrange(len(jointIndices)):
            for j in xrange(len(jointIndices[i])):
                jointsTemp.append(jointIndices[i][j])

        self._jointIds = list(set(jointsTemp))
        self._jointIds.sort()
        self._jointNames = [jointsArray[jointId].name for jointId in self._jointIds]

    def Now(self):
        if self._meshIndex == None:
            raise CharacterBuilderError("mesh index")
        if not self._dnaProvider:
            raise CharacterBuilderError("DNAProvider")
        if not self._jointIds:
            raise CharacterBuilderError("joints", "Check if DNA has geometry exported.")

        mesh = Mesh(self._jointIds,
                    self._jointNames,
                    self._dnaProvider,
                    self._meshIndex,
                    self._linearModifier)

        if self._createMesh:
            mesh.createNeutralMesh()
            if self._addNormals:
                mesh.addNormals()

        if self._createBlendshape:
            mesh.addBlendshapes()

        if self._createSkin:
            mesh.addSkin()
