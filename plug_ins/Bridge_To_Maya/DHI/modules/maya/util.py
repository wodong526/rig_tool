from pymel.core.language import Mel

from DHI.core.logger import Logger
from DHI.modules.file.handler import FileHandler
from DHI.modules.maya.adapter import AdditionalAdapterBuilder
from DHI.modules.maya.handler import MayaSkinHandler
import pymel.core as pycore
import pymel.core.uitypes as uitypes
import maya.OpenMaya as om
import DHI.core.progressWindowManager as progressWindowManager

try:
    # Python 2
    xrange
except NameError:
    # Python 3, xrange is now named range
    xrange = range


class MayaUtil(object):
    logger = Logger.getInstance(__name__)

    ATTRIBUTE_NAMES = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

    @staticmethod
    def startLogToFile(path):
        if not path.endswith(".log"):
            path += ".log"

        return pycore.cmdFileOutput(open=path)

    @staticmethod
    def endLogToFile():
        return pycore.cmdFileOutput(close=True)

    @staticmethod
    def createWorkspace(mayaProjectPath):
        if FileHandler.pathExists(mayaProjectPath):
            cmd = "setProject \"" + mayaProjectPath + "\";"
            Mel.eval(cmd)

    @staticmethod
    def deleteHistory(meshNames):
        for meshName in meshNames:
            if pycore.objExists(meshName):
                pycore.select(clear=True)
                pycore.select(meshName)
                Mel.eval('doBakeNonDefHistory( 1, {"prePost" });')

    @staticmethod
    def addControlAttributesToRoot(rootJointName, ctrlMap):
        # make attributes
        try:
            items = ctrlMap.iteritems()
        except:
            items = ctrlMap.items()

        for ctrlName, attrInfo in items:
            if not pycore.objExists(rootJointName + "." + attrInfo[0]):
                pycore.addAttr(rootJointName, longName=attrInfo[0], keyable=True, attributeType="float",
                               minValue=attrInfo[1], maxValue=attrInfo[2])
                MayaUtil.logger.info("Added attribute: " + rootJointName + "." + attrInfo[0])
                if (pycore.objExists(ctrlName)):
                    pycore.connectAttr(ctrlName, rootJointName + "." + attrInfo[0])
            else:
                MayaUtil.logger.info("Skipping attribute " + ctrlName)

        pycore.select(rootJointName)
        pycore.setKeyframe()

    @staticmethod
    def addWMAttributesToRoot(rootJointName, wmControlName, multiplierNames):
        for multiplierName in multiplierNames:
            if not pycore.objExists(rootJointName + "." + multiplierName):
                pycore.addAttr(rootJointName, longName=multiplierName, keyable=True, attributeType="float",
                               minValue=0.0, maxValue=1.0)
                MayaUtil.logger.info("Added attribute: " + rootJointName + "." + multiplierName)
                if wmControlName and pycore.objExists(wmControlName + "." + multiplierName):
                    pycore.connectAttr(wmControlName + "." + multiplierName, rootJointName + "." + multiplierName)

        pycore.select(rootJointName)
        pycore.setKeyframe()

    @staticmethod
    def renameBlendShapes(meshNames):
        for meshName in meshNames:
            if pycore.objExists(meshName + "_blendShapes"):
                blendshapeAliases = pycore.aliasAttr(meshName + "_blendShapes", q=True)
                try:
                    for aliasIndex in xrange(len(blendshapeAliases) / 2):
                        oldAlias = blendshapeAliases[aliasIndex * 2]
                        newAlias = meshName + "__" + oldAlias
                        if not (oldAlias == newAlias):
                            pycore.aliasAttr(newAlias, meshName + "_blendShapes" + "." + oldAlias)
                except TypeError:
                    MayaUtil.logger.error("Renaming blendshapes on mesh %s skipped." % meshName)

    @staticmethod
    def removeNeckJointFromHead(rootJoints, neckJoints):
        # move root joint to world root, prevent these from being deleted
        pycore.parent(rootJoints[0], world=True)
        pycore.parent(rootJoints[1], world=True)
        pycore.parent(rootJoints[2], world=True)
        # remove neck joint
        pycore.delete(neckJoints[0])

    @staticmethod
    def attachHeadRootAndNeckJointsToBody(rootJoints, neckJoints):
        pycore.parent(rootJoints[1], neckJoints[6])
        pycore.parent(rootJoints[2], neckJoints[7])
        pycore.parent(rootJoints[0], neckJoints[8])

    @staticmethod
    def createHeadAndBodyScene(neckMeshes, rootJoints, neckJoints, bodyFilePath):
        '''
        Load body scene and attach it to head.
        '''
        meshNames = []
        skinWeights = []

        msh = MayaSkinHandler()
        progressWindowManager.update(0, "Fetching skin weights")

        # fetch all mesh names and skin weights and remove mesh clusters
        for meshName in neckMeshes:
            if pycore.objExists(meshName):
                meshNames.append(meshName)
                skinWeights.append(msh.getSkinWeightsFromScene(meshName))
                pycore.delete(meshName + "_skinCluster")

        MayaUtil.removeNeckJointFromHead(rootJoints, neckJoints)

        # import body to scene
        pycore.importFile(bodyFilePath, options="v=0", type="mayaAscii")

        MayaUtil.attachHeadRootAndNeckJointsToBody(rootJoints, neckJoints)
        progressWindowManager.update(progressWindowManager.percentage['HEAD_BODY_SKIN_WEIGHTS'],
                                     "Applying skin weights")
        progressIncrementVal = progressWindowManager.calculateProgressStepValue(len(meshNames),
                                                                                progressWindowManager.percentage[
                                                                                    'HEAD_BODY_SKIN_WEIGHTS'])

        # apply skin weights
        for meshName, skinWeight in zip(meshNames, skinWeights):
            msh.createSkinCluster(skinWeight.joints, meshName, meshName + "_skinCluster", skinWeight.noOfInfluences)
            progressWindowManager.update(progressIncrementVal, "Setting skin weights for %s." % meshName)
            msh.setSkinWeightsToScene(meshName, skinWeight)

    @staticmethod
    def importShader(shaderScenePath, meshShaderMapping):
        MayaUtil.logger.info("Shader scene imported")
        pycore.importFile(shaderScenePath, options="v=0", type="mayaAscii")
        progressIncrementVal = progressWindowManager.calculateProgressStepValue(len(meshShaderMapping),
                                                                                progressWindowManager.percentage[
                                                                                    'HEAD_SHADERS'] / 8)
        try:
            items = meshShaderMapping.iteritems()
        except:
            items = meshShaderMapping.items()
        for meshName, shaderName in items:
            for lodLvl in range(0, 8):
                try:
                    # Apply shader to all meshes based on LOD level
                    resolvedMeshName = meshName + str(lodLvl) + "_mesh"
                    shader = pycore.PyNode("shader_" + shaderName)
                    pycore.select(resolvedMeshName, replace=True)
                    pycore.mel.eval("sets -e -forceElement " + shader.name() + "SG")
                    progressWindowManager.update(progressIncrementVal, "Added shader for mesh %s." % resolvedMeshName)
                    MayaUtil.logger.info("Added shader for mesh %s." % resolvedMeshName)
                except (pycore.MayaNodeError, ValueError, TypeError):
                    MayaUtil.logger.warning("Skipped adding shader for mesh %s." % meshName)

    @staticmethod
    def resolveSceneMapPaths(mapInfos, folderName):
        for mapInfo in mapInfos:
            nodeName = "mapFile_" + mapInfo[0]
            if mapInfo[1]:
                nodeName = "baseMapFile_" + mapInfo[0]
            if not pycore.objExists(nodeName):
                continue
            fileTextureName = pycore.getAttr(nodeName + ".fileTextureName")
            textureFolderName, textureFileName = FileHandler.splitPath(fileTextureName)
            textureFolderName = folderName
            pycore.setAttr(nodeName + ".fileTextureName", textureFolderName + "/" + textureFileName, type="string")

    @staticmethod
    def resolveSceneMaskPaths(masks, folderName):
        for mask in masks:
            nodeName = "maskFile_" + mask
            if not pycore.objExists(nodeName):
                continue
            fileTextureName = pycore.getAttr(nodeName + ".fileTextureName")
            textureFolderName, textureFileName = FileHandler.splitPath(fileTextureName)
            textureFolderName = folderName
            pycore.setAttr(nodeName + ".fileTextureName", textureFolderName + "/" + textureFileName, type="string")

    @staticmethod
    def resolveSceneShaderPaths(shaders, folderName):
        for shader in shaders:
            nodeName = "shader_" + shader
            if not pycore.objExists(nodeName):
                continue
            fileShaderName = pycore.getAttr(nodeName + ".shader")
            shaderFolderName, shaderFileName = FileHandler.splitPath(fileShaderName)
            shaderFolderName = folderName
            pycore.setAttr(nodeName + ".shader", shaderFolderName + "/" + shaderFileName, type="string")

    @staticmethod
    def createLights(lightsFilePath, orient):
        pycore.system.importFile(lightsFilePath, defaultNamespace=True)

        # Set viewport 2.0 properties needed:
        modelPanelList = []
        modelEditorList = pycore.lsUI(editors=True)
        for myModelPanel in modelEditorList:
            if myModelPanel.find('modelPanel') != -1:
                modelPanelList.append(myModelPanel)
        for modelPanel in modelPanelList:
            if uitypes.ModelEditor(modelPanel).getActiveView():
                try:
                    uitypes.ModelEditor(modelPanel).setDisplayTextures(val=True)
                    uitypes.ModelEditor(modelPanel).setDisplayLights(val="all")
                    uitypes.ModelEditor(modelPanel).setShadows(val=True)
                    uitypes.ModelEditor(modelPanel).setJoints(val=False)
                except:
                    MayaUtil.logger.error("An error has occured importing lights scene!.\n")
        pycore.rotate("Lights", orient)
        pycore.makeIdentity("Lights", apply=True)

    @staticmethod
    def saveMayaScene(filePath, fileType="mayaAscii"):
        pycore.saveAs(filePath, force=True, save=True, options="v=0", type=fileType)

    @staticmethod
    def copyCurrentScene(destination, nameFlag, fileType="mayaBinary"):
        currentName = pycore.sceneName()
        folderName, fileName = FileHandler.splitPath(currentName)
        newName = FileHandler.joinPath((destination, nameFlag + "_" + fileName))
        pycore.renameFile(newName)
        pycore.saveFile(type=fileType)
        pycore.renameFile(currentName)
        return newName

    @staticmethod
    def openScene(path):
        pycore.openFile(path, f=True)

    @staticmethod
    def loadPlugin(name, path, platform, forcedExtension=None):
        """
            Loads plugin for given name.
            @param name: Plugin name. (string)
            @param path: Path to plugin. (string)
            @param platform: OS platform. (string)
        """
        import maya.cmds as cmds

        isLoaded = False
        extension = ".mll"
        if platform == "Linux":
            extension = ".so"

        if forcedExtension:
            extension = forcedExtension

        if not (cmds.pluginInfo(name, query=True, loaded=True)):
            try:
                print("Loading plugin: ", path + "/" + name + extension)
                cmds.loadPlugin(path + "/" + name + extension)
                isLoaded = True
            except:
                print("Error loading plugin %s" % name)
                pass
        else:
            print("Plugin %s already loaded" % name)
            isLoaded = True
        return isLoaded

    @staticmethod
    def adaptScene(scale, scalePivot, orient, translate, meshNames, guiNames, controlNames):
        meshesToAdapt = []
        skinWeights = []

        msh = MayaSkinHandler()
        # fetch all mesh names and skin weights and remove mesh clusters
        for meshName in meshNames:
            if pycore.objExists(meshName):
                meshesToAdapt.append(meshName)
                skinWeights.append(msh.getSkinWeightsFromScene(meshName))
                pycore.delete(meshName + "_skinCluster")

        MayaUtil._adaptJoints(scale, scalePivot, orient, translate)
        MayaUtil._adaptMeshes(scale, scalePivot, orient, meshNames, translate)
        MayaUtil._adaptGUI(scale, scalePivot, orient, guiNames)
        MayaUtil._adaptControls(scale, scalePivot, orient, controlNames)

        # # apply skin weights
        for meshName, skinWeight in zip(meshesToAdapt, skinWeights):
            msh.createSkinCluster(skinWeight.joints, meshName, meshName + "_skinCluster", skinWeight.noOfInfluences)
            msh.setSkinWeightsToScene(meshName, skinWeight)

    @staticmethod
    def _adaptJoints(scale, scalePivot, orient, translate):
        jointAdapter = AdditionalAdapterBuilder.buildMayaJointsDataAA(scale, scalePivot, orient, translate)

        joints = [joint for joint in pycore.ls(type="joint") if not joint.listRelatives(parent=True, type="joint")]

        jointAdapter.adapt(joints)

    @staticmethod
    def _adaptMeshes(scale, scalePivot, orient, meshNames, translate):
        meshAdapter = AdditionalAdapterBuilder.buildMeshAA(scale, scalePivot, orient, translate)

        for meshName in meshNames:
            try:
                meshNode = pycore.PyNode(meshName)
                for attrName in MayaUtil.ATTRIBUTE_NAMES:
                    pycore.PyNode(meshNode + "." + attrName).unlock()
                meshAdapter.adapt(meshNode)
                for attrName in MayaUtil.ATTRIBUTE_NAMES:
                    pycore.PyNode(meshNode + "." + attrName).lock()
                pycore.select(meshNode, replace=True)
                Mel.eval('doBakeNonDefHistory( 1, {"pre" });')
                pycore.polySoftEdge(meshNode, a=180, ch=False)
            except (pycore.MayaNodeError, ValueError):
                MayaUtil.logger.info("Mesh %s adaptation skipped." % meshName)
        pycore.select(clear=True)

    @staticmethod
    def _adaptGUI(scale, scalePivot, orient, guiNames):
        guiAdapter = AdditionalAdapterBuilder.buildGuiAA(scale, scalePivot, orient)

        if guiAdapter:
            try:
                guiAdapter.adapt([pycore.PyNode(guiName) for guiName in guiNames])
            except (pycore.MayaNodeError, ValueError):
                MayaUtil.logger.info("GUI adaptation skipped.")

    @staticmethod
    def _adaptControls(scale, scalePivot, orient, controlNames):
        controlAdapter = AdditionalAdapterBuilder.buildControlsAA(scale, scalePivot, orient)

        if controlAdapter:
            try:
                controlAdapter.adapt([pycore.PyNode(controlName) for controlName in controlNames])
            except (pycore.MayaNodeError, ValueError):
                MayaUtil.logger.info("Analog controls adaptation skipped.")

    @staticmethod
    def exportFBX(fbxFileName, meshNames, rootJointNames):
        minTime = pycore.playbackOptions(minTime=True, query=True)
        maxTime = pycore.playbackOptions(maxTime=True, query=True)

        pycore.mel.FBXResetExport()
        pycore.mel.FBXExportBakeComplexAnimation(v=True)
        pycore.mel.FBXExportBakeComplexStart(v=minTime)
        pycore.mel.FBXExportBakeComplexEnd(v=maxTime)
        pycore.mel.FBXExportConstraints(v=True)
        pycore.mel.FBXExportSkeletonDefinitions(v=True)
        pycore.mel.FBXExportInputConnections(v=True)
        pycore.mel.FBXExportSmoothingGroups(v=True)
        pycore.mel.FBXExportSkins(v=True)
        pycore.mel.FBXExportShapes(v=True)
        pycore.mel.FBXExportCameras(v=False)
        pycore.mel.FBXExportLights(v=False)
        pycore.mel.FBXExportUpAxis('y')
        pycore.select(clear=True)

        for mesh in meshNames:
            if pycore.objExists(mesh):
                pycore.select(mesh, add=True)
        for rJoint in rootJointNames:
            pycore.select(rJoint, add=True)

        pycore.mel.FBXExport(s=True, f=fbxFileName)

    @staticmethod
    def connectAttributesToShader(shaderAttributesMapping):
        MayaUtil.logger.info("Connecting attributes to shader.")
        try:
            items = shaderAttributesMapping.iteritems()
        except:
            items = shaderAttributesMapping.items()

        for frmAttribute, shaderAttribute in items:
            if pycore.objExists(frmAttribute) and pycore.objExists(shaderAttribute):
                pycore.connectAttr(frmAttribute, shaderAttribute, force=True)

    @staticmethod
    def removeGeometryFromDNA(dnaFilePath):
        import dna

        try:
            fileStream = dna.FileStream(str(dnaFilePath), dna.FileStream.AccessMode_Read,
                                        dna.FileStream.OpenMode_Binary)
            reader = dna.StreamReader(fileStream, dna.DataLayer_Behavior)
            reader.read()

            stream = dna.FileStream(str(dnaFilePath), dna.FileStream.AccessMode_Write, dna.FileStream.OpenMode_Binary)
            writer = dna.StreamWriter(stream)

            writer.setFrom(reader)
            writer.write()
        except Exception as ex:
            print(ex)

    @staticmethod
    def setDriverBlendshapeChannels(driverNode, blendshapeWeights):
        bsChannels = MayaUtil.getChannelNames(driverNode)

        for i, channel in enumerate(bsChannels):
            pycore.setAttr(driverNode + "." + channel, blendshapeWeights[i])

    @staticmethod
    def getBlendshapeWeights(meshName="head_mesh"):
        try:
            pycore.select(meshName)
        except:
            MayaUtil.logger.error("ERROR: mesh with name \"%s\" not found in scene." % meshName)

        blendShapeNode = pycore.PyNode(meshName).getShape().inputs(type='blendShape')[0]

        return [blendShapeNode.getWeight(i) for i in range(blendShapeNode.getWeightCount())]

    @staticmethod
    def getSceneLinearUnit():
        return pycore.currentUnit(query=True, linear=True)

    @staticmethod
    def calculateModifier(dnaLinearUnit):
        '''
        Calculates modifier which should be used for modification of data read from DNA with regard to the units used in Maya scene.

        @param dnaLinearUnit: Linear Unit used in DNA file

        @return: modifier (float)
        '''
        res = 1

        if MayaUtil.getSceneLinearUnit() != dnaLinearUnit:
            if dnaLinearUnit == "cm":
                res = 0.01
            elif dnaLinearUnit == "m":
                res = 100.0

        return res

    @staticmethod
    def isMeshSelected(sourceMeshName=None):
        if sourceMeshName:
            pycore.select(sourceMeshName, replace=True)
        selection = pycore.ls(selection=True, type=["transform", "mesh"])
        if len(selection) == 1:
            if pycore.objectType(selection[0]) == "transform" and selection[0].getShape() and pycore.objectType(
                    selection[0].getShape()) == "mesh":
                return (True, selection[0])
            if pycore.objectType(selection[0]) == "mesh":
                return (True, selection[0])
        return (False, "")

    @staticmethod
    def getChannelNames(driverNode):
        #         return pycore.PyNode(driverNode).getTarget()
        try:
            pycore.select(driverNode, replace=True)
            return pycore.listAttr(userDefined=True)
        except Exception as ex:
            MayaUtil.logger.error("Couldn't find blenshape node!")
            raise ex

    @staticmethod
    def breakDmtConnections(dmtNodeName, driverNode):
        MayaUtil._changeDmtConnections(dmtNodeName, driverNode, False)

    @staticmethod
    def connectDmt(dmtNodeName, driverNode):
        MayaUtil._changeDmtConnections(dmtNodeName, driverNode, True)

    @staticmethod
    def _changeDmtConnections(dmtNodeName, driverNode, isConnect):
        """
        Changes connections on blendshape attributes.
        """
        bsChannels = MayaUtil.getChannelNames(driverNode)

        try:
            dmtnode = pycore.PyNode(dmtNodeName + ".output")
        except Exception as ex:
            MayaUtil.logger.error("Couldn't find DMT node")
            raise ex

        ind = 0
        try:
            MayaUtil.logger.debug("Changing connections. Parameter \"isConnect\" is %s" % isConnect)
            MayaUtil.logger.debug("Number of connections: %s" % (len(bsChannels)))
            for index in range(len(bsChannels)):
                if isConnect:
                    pycore.connectAttr(dmtnode[index], driverNode + "." + bsChannels[index])
                else:
                    pycore.disconnectAttr(dmtnode[index], driverNode + "." + bsChannels[index])
                ind = index
            MayaUtil.logger.debug("Changing connections Done.")
        except Exception as ex:
            MayaUtil._processDmtConnectionsError(ex, ind, isConnect)

    @staticmethod
    def _processDmtConnectionsError(ex, ind, isConnect):
        if isConnect:
            errorMessage1 = "C"
            errorMessage2 = "Disc"
            errorMessage3 = "Attributes dis"
            errorMessage4 = "Disc"
        else:
            errorMessage1 = "Disc"
            errorMessage2 = "C"
            errorMessage3 = "Attributes "
            errorMessage4 = "C"

        errorMessage1 += "connecting attributes from driver node failed! Reason: %s" % str(ex)
        errorMessage2 += "connecting attributes..."
        errorMessage3 += "connected."
        errorMessage4 += "Connecting attributes on driver node failed! "

        MayaUtil.logger.error(errorMessage1)
        try:
            MayaUtil.logger.info(errorMessage2)
            for _ in xrange(ind):
                pycore.undo()
            MayaUtil.logger.info(errorMessage3)
        except Exception as ex1:
            MayaUtil.logger.fatal(errorMessage4 + "Reason: %s" % str(ex1))
            MayaUtil.logger.fatal("Scene is in invalid state!")

    @staticmethod
    def isSelectedMeshValid(defaultMeshName, sourceMeshName=None):
        meshSelected, meshNode = MayaUtil.isMeshSelected(sourceMeshName)

        if meshSelected:
            defaultMeshNode = pycore.PyNode(defaultMeshName)
            if len(meshNode.vtx) == len(defaultMeshNode.vtx):
                return (True, meshNode.name())
            else:
                MayaUtil.logger.warning("Selected mesh doesn't have the expected topology.")
                pycore.warning("Selected mesh doesn't have the expected topology.")
                return (False, "")

        MayaUtil.logger.warning("Selected node is not a mesh.")
        pycore.warning("Selected node is not a mesh.")
        return (False, "")

    @staticmethod
    def setMeshVtxPositions(meshName, array, worldSpace=False):
        '''
        Sets mesh vertex positions for given array.

        @param meshName: Mesh node name in scene. (string)
        @param array: Array containing new vertex positions. (array)
        @param worldSpace: Indicates is vertex positions should be set
            in word space. If False, they will be set in object space. (boolean)
        '''

        sel = om.MSelectionList()
        sel.add(meshName)

        dagPath = om.MDagPath()
        sel.getDagPath(0, dagPath)

        mfMesh = om.MFnMesh(dagPath)
        mpArray = om.MPointArray()
        for pos in array:
            mpArray.append(om.MPoint(pos[0], pos[1], pos[2]))

        space = om.MSpace.kObject
        if worldSpace:
            space = om.MSpace.kWorld

        mfMesh.setPoints(mpArray, space)

    @staticmethod
    def getSelectedMeshName(meshType="transform"):
        res = ""
        selectedMesh = pycore.ls(selection=True, type=meshType)

        nrOfMeshes = len(selectedMesh)

        if nrOfMeshes == 1:
            res = selectedMesh[0].name()
        elif nrOfMeshes == 0:
            MayaUtil.logger.warning("Warning: No mesh is selected!")
        else:
            MayaUtil.logger.warning("Warning: Multiple meshes selected!")

        return res
