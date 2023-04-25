from DHI.core.logger import Logger
import pymel.core as pycore

try:
    # Python 2
    xrange
except NameError:
    # Python 3, xrange is now named range
    xrange = range

class MayaSceneError(Exception):

    def __init__(self, message):
        Exception.__init__(self, message)

    def __str__(self):
        return "MayaSceneError: " + self.message


class MayaSkinWeights:

    METHOD_CLASIC_LINEAR = 0
    METHOD_DUAL_QUATERNION = 1
    METHOD_WEIGHT_BLENDED = 2

    def __init__(self):
        self.noOfInfluences = 0  # (int)
        self.skinningMethod = MayaSkinWeights.METHOD_CLASIC_LINEAR
        self.joints = []  # (string[])
        self.verticesInfo = []  # (float[][])
        
    def getWeightsMatrix(self):
        '''
        Converts MayaSkinWeights.verticesInfo data into [nVertices, nJoints] list of lists.        
        First index (rows) represents vertex id number, while second index (columns) represents
        joint number. (weights[vtxId][jntId])
        
        @return Matrix containing skin weights. (float[nVerts, nJoints]) 
        '''

        nVerts = len(self.verticesInfo)
        nJoints = len(self.joints)
        weights = [None for i in xrange(nVerts)]

        for vtxId, vtxInfo in enumerate(self.verticesInfo):
            vertWeights = [0.0 for i in xrange(nJoints)]
            for inW in range(0, len(vtxInfo), 2):
                vertWeights[vtxInfo[inW]] = vtxInfo[inW + 1]
            weights[vtxId] = vertWeights

        return weights


class MayaSkinHandler(object):
    
    logger = Logger.getInstance(__name__)

    def getSkinWeightsData(self, meshName):
        meshNode = pycore.ls(meshName, type="transform")[0]
        if (meshNode.getShape().type() != "mesh"):
            raise MayaSceneError("Unable to find mesh: " + meshName)

        skinClusterName = pycore.language.Mel.eval("findRelatedSkinCluster " + meshName)
        if skinClusterName:
            skinCluster = pycore.PyNode(skinClusterName)
        if not skinCluster:
            raise MayaSceneError("Unable to find skin for given mesh: " + meshName)
        return (meshNode, skinCluster)

    def getSkinWeightsFromScene(self, meshName):
        self.logger.info("Get skin weights for mesh: " + meshName)
        skinCluster = self.getSkinWeightsData(meshName)[1]
        skinWeights = MayaSkinWeights()

        # joints
        skinWeights.noOfInfluences = skinCluster.getMaximumInfluences()
        skinWeights.skinningMethod = skinCluster.getSkinMethod()
        skinWeights.joints = [obj.name() for obj in skinCluster.getInfluence()]

        # weights
        iterator = skinCluster.getWeights(meshName + ".vtx[:]")
        for weights in iterator:
            vertexWeights = []
            skinWeights.verticesInfo.append(vertexWeights)

            # if weight is different then 0.0, write it to file
            for i, weight in enumerate(weights):
                if weight:
                    vertexWeights.append(i)
                    vertexWeights.append(weight)

        self.logger.info("Get skin weights ended.")
        return skinWeights

    def createSkinCluster(self, influences, mesh, skinClusterName, maximumInfluences=4, skinningMethod=0):
        pycore.select(influences[0], replace=True)
        pycore.select(mesh, add=True)
        skinCluster = pycore.skinCluster(toSelectedBones=True, name=skinClusterName,
            maximumInfluences=maximumInfluences, skinMethod=skinningMethod, obeyMaxInfluences=True)
        if len(influences) > 1:
            pycore.skinCluster(skinCluster, edit=True, addInfluence=influences[1:], weight=0)
        return skinCluster

    def setSkinWeightsToScene(self, meshName, skinWeights):
        self.logger.info("Set skin weights for mesh: " + meshName)
        meshNode, skinCluster = self.getSkinWeightsData(meshName)
        vtxIds = xrange(pycore.polyEvaluate(meshNode, vertex=True))

        # prepare mapping data
        fileJointMapping = []
        for jointName in skinWeights.joints:
            fileJointMapping.append(skinCluster.indexForInfluenceObject(jointName))

        # import skin weights
        tempStr = skinCluster.name() + ".wl["
        for vtxId in vtxIds:
            # file vertices weights
            vtxInfo = skinWeights.verticesInfo[vtxId]

            # set all skin weights to zero
            vtxStr = tempStr + str(vtxId) + "].w["
            pycore.setAttr(vtxStr + "0]", 0.0)

            # import skin weights
            for w in range(0, len(vtxInfo), 2):
                pycore.setAttr(vtxStr + str(fileJointMapping[vtxInfo[w]]) + "]", vtxInfo[w + 1])
        self.logger.info("Set skin weights ended.")


