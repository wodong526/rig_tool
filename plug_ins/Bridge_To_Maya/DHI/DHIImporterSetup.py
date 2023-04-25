import os
import DHI.core.progressWindowManager as progressWindowManager
from DHI.characterConfig import CharacterConfig

from DHI.modules.dna.model.gui import AnalogGuiOptions
from DHI.modules.dna.scene.builder.rlNodeBuilder import RigLogicNodeBuilder
from DHI.modules.file.handler import FileHandler
from DHI.modules.dna.scene.builder.sceneBuilder import SceneBuilder, SceneBuilderError
import pymel.core as pycore
import maya.cmds as cmds
from pymel.core.language import mel
from DHI.modules.maya.util import MayaUtil

try:
    # Python 2
    xrange
except NameError:
    # Python 3, xrange is now named range
    xrange = range


class DHIImporterSetup:
    Instance = None

    def __init__(self):
        DHIImporterSetup.Instance = self

    def set_Asset_Data(self, json_data):
        MayaUtil.logger.info("Received JSON data for Digital Human Asset")
        self.jsonData = json_data
        self.characterConfig = CharacterConfig(self.jsonData["character"])
        MayaUtil.logger.info(self.characterConfig)
        confirmDialogResponse = pycore.confirmDialog(title='Confirm dialog',
                                                     message='Are you sure you want to import MetaHuman character? All unsaved progress will be lost.',
                                                     button=['Yes', 'No'],
                                                     defaultButton='Yes',
                                                     cancelButton='No', dismissString='No')

        if confirmDialogResponse == 'Yes':
            self.importCharacter()

    def importCharacter(self):
        try:
            import time
            start_time = time.time()
            progressWindowManager.reset()
            progressWindowManager.show()
            self.preImportCharacter()

            self.importHead()
            self.importBodyAndAttachToHead()

            self.postImportCharacter()
            progressWindowManager.hide()
            MayaUtil.logger.info("--- Import finished in %s seconds ---" % (time.time() - start_time))
        except Exception as e:
            MayaUtil.logger.error(e)
            progressWindowManager.hide()

    def preImportCharacter(self):
        MayaUtil.logger.info('PreCharacter Import started...')
        MayaUtil.logger.info("Setting project environment variables...")
        os.environ["PROJECT_ROOT"] = self.characterConfig.workspaceDir

        self.backupDNAWithGeometry()
        MayaUtil.logger.info('PreCharacter Import finished...')

    def backupDNAWithGeometry(self):
        MayaUtil.logger.info('Backup DNA with geometry started...')
        from shutil import copyfile
        rlDNAPath = self.resolveRLDNAPathFromDNAPath(self.characterConfig.dnaPath)
        copyfile(self.characterConfig.dnaPath, rlDNAPath)
        MayaUtil.logger.info('Backup DNA with geometry finished...')

    def resolveRLDNAPathFromDNAPath(self, dnaPath):
        '''
        returns a string with _rl as a sufix
        '''
        return dnaPath.replace('.dna', '') + "_rl.dna"

    def removeNonExistingElementsFromScene(self):
        # remove sufficient meshes
        resolvedBodyMeshName = self.characterConfig.bodyMeshName.replace("_body", "")

        MayaUtil.logger.info("Removing sufficient objects")
        if pycore.objExists("ROM_root"):
            pycore.delete("ROM_root")

        if pycore.objExists(resolvedBodyMeshName + "_lod0"):
            pycore.delete(resolvedBodyMeshName + "_lod0")

        if pycore.objExists(resolvedBodyMeshName + "_lod1"):
            pycore.delete(resolvedBodyMeshName + "_lod1")

        if pycore.objExists(resolvedBodyMeshName + "_lod2"):
            pycore.delete(resolvedBodyMeshName + "_lod2")

        if pycore.objExists(resolvedBodyMeshName + "_lod3"):
            pycore.delete(resolvedBodyMeshName + "_lod3")

        if pycore.objExists(resolvedBodyMeshName + "_body_uExport"):
            pycore.delete(resolvedBodyMeshName + "_body_uExport")

        # remove animation joint chain0
        if pycore.objExists("anim:root"):
            pycore.delete("anim:root")

    def createJointsGroupAndMoveJoints(self):
        pycore.group(parent="rig", empty=True, name="joints_grp")
        pycore.parent("DHIhead:spine_04", "joints_grp")
        pycore.parent("DHIbody:root", "joints_grp")
        pycore.parent("root_drv", "joints_grp")

    def postImportCharacter(self):
        MayaUtil.logger.info("Post import reached")
        from DHI.core.consts import MESH_NAMES

        MayaUtil.createWorkspace(self.characterConfig.workspaceDir)
        MayaUtil.removeGeometryFromDNA(self.resolveRLDNAPathFromDNAPath(self.characterConfig.dnaPath))
        self.removeNonExistingElementsFromScene()

        MayaUtil.logger.info("Moving body to world space")
        pycore.parent("root", world=True)
        pycore.parent("root_drv", world=True)

        if pycore.objExists("Skeletons"):
            pycore.delete("Skeletons")

        MayaUtil.logger.info("Adding body namespace")
        bodyNamespace = "DHIbody"
        cmds.select("root")
        bodyJointNames = cmds.listRelatives(allDescendents=True, type='joint')
        bodyJointNames.append("root")
        bodyJoints = []
        for mayaJoint in bodyJointNames:
            # get joint node
            jointNodes = pycore.ls(mayaJoint, type="joint")
            bodyJoints.append(jointNodes[0])

        self.createControlsSet()
        self.createBodyJointsSet(bodyJointNames)

        pycore.namespace(add=bodyNamespace)
        self.addJointsToNamespace(bodyNamespace, bodyJoints)

        pycore.group(world=True, empty=True, name="rig")
        pycore.parent("head_grp", "rig")
        # self.createJointsGroupAndMoveJoints()

        if pycore.objExists("rig_setup_GRP"):
            pycore.rename("rig_setup_GRP", "rig_setup_grp")
            pycore.parent("rig_setup_grp", "rig")

        pycore.group(parent="rig", empty=True, name="body_grp")
        pycore.group(parent="body_grp", empty=True, name="geometry_grp")
        pycore.parent("body_lod0_grp", "body_grp|geometry_grp")
        pycore.parent("body_lod1_grp", "body_grp|geometry_grp")
        pycore.parent("body_lod2_grp", "body_grp|geometry_grp")
        pycore.parent("body_lod3_grp", "body_grp|geometry_grp")
        self.scaleAndAttachGUIToHead()
        self.connectFollowHead()

        MayaUtil.deleteHistory(MESH_NAMES)

        MayaUtil.saveMayaScene(self.characterConfig.dnaPathDir + "/" + self.characterConfig.characterName + "_full_rig",
                               fileType="mayaBinary")

    def connectFollowHead(self):
        MayaUtil.logger.info('Connecting head follow controls')
        try:
            pycore.spaceLocator(name="LOC_world")
            pycore.parent("LOC_world", "headGui_grp")
            pycore.setAttr("LOC_world.rx", 0.0)
            pycore.setAttr("LOC_world.ry", 0.0)
            pycore.setAttr("LOC_world.rz", 0.0)
            pycore.setAttr("LOC_world.visibility", 0)

            pycore.parentConstraint(["DHIhead:head", "GRP_faceGUI"], maintainOffset=True,
                                    name="GRP_faceGUI_parentConstraint1")
            pycore.setAttr("GRP_faceGUI_parentConstraint1.interpType", 0)
            pycore.parentConstraint(["LOC_world", "GRP_faceGUI"], maintainOffset=True,
                                    name="GRP_faceGUI_parentConstraint1")

            pycore.setDrivenKeyframe("GRP_faceGUI_parentConstraint1.LOC_worldW1", itt="linear", ott="linear",
                                     currentDriver="CTRL_faceGUIfollowHead.ty", driverValue=0.0, value=1.0)
            pycore.setDrivenKeyframe("GRP_faceGUI_parentConstraint1.LOC_worldW1", itt="linear", ott="linear",
                                     currentDriver="CTRL_faceGUIfollowHead.ty", driverValue=1.0, value=0.0)
            pycore.setDrivenKeyframe("GRP_faceGUI_parentConstraint1.headW0", itt="linear", ott="linear",
                                     currentDriver="CTRL_faceGUIfollowHead.ty", driverValue=0.0, value=0.0)
            pycore.setDrivenKeyframe("GRP_faceGUI_parentConstraint1.headW0", itt="linear", ott="linear",
                                     currentDriver="CTRL_faceGUIfollowHead.ty", driverValue=1.0, value=1.0)

            pycore.parentConstraint(["DHIhead:head", "GRP_C_eyesAim"], maintainOffset=True,
                                    name="GRP_C_eyesAim_parentConstraint1")
            pycore.setAttr("GRP_C_eyesAim_parentConstraint1.interpType", 0)
            pycore.parentConstraint(["LOC_world", "GRP_C_eyesAim"], maintainOffset=True,
                                    name="GRP_C_eyesAim_parentConstraint1")
            pycore.setDrivenKeyframe("GRP_C_eyesAim_parentConstraint1.LOC_worldW1", itt="linear", ott="linear",
                                     currentDriver="CTRL_eyesAimFollowHead.ty", driverValue=0.0, value=1.0)
            pycore.setDrivenKeyframe("GRP_C_eyesAim_parentConstraint1.LOC_worldW1", itt="linear", ott="linear",
                                     currentDriver="CTRL_eyesAimFollowHead.ty", driverValue=1.0, value=0.0)
            pycore.setDrivenKeyframe("GRP_C_eyesAim_parentConstraint1.headW0", itt="linear", ott="linear",
                                     currentDriver="CTRL_eyesAimFollowHead.ty", driverValue=0.0, value=0.0)
            pycore.setDrivenKeyframe("GRP_C_eyesAim_parentConstraint1.headW0", itt="linear", ott="linear",
                                     currentDriver="CTRL_eyesAimFollowHead.ty", driverValue=1.0, value=1.0)
        except Exception as ex:
            print ("Error during connectFollowHead")
            print (ex)

    def getGUITranslation(self, gender, height):
        from DHI.core.consts import GUI_TRANSLATIONS
        val = "_".join([gender, height])
        if val in GUI_TRANSLATIONS:
            if GUI_TRANSLATIONS[val] is not None:
                return [GUI_TRANSLATIONS[val][0], GUI_TRANSLATIONS[val][1], GUI_TRANSLATIONS[val][2]]
            else:
                return None
        else:
            return None

    def getGUIScale(self, gender, height):
        from DHI.core.consts import GUI_SCALES
        val = "_".join([gender, height])
        if val in GUI_SCALES:
            return GUI_SCALES[val]
        else:
            return None

    def scaleAndAttachGUIToHead(self):
        MayaUtil.logger.info("Attaching gui to head")
        resolvedTranslation = self.getGUITranslation(self.characterConfig.gender, self.characterConfig.height)
        resolvedScale = self.getGUIScale(self.characterConfig.gender, self.characterConfig.height)
        if pycore.objExists("GRP_faceGUI"):
            if resolvedTranslation:
                pycore.select(clear=True)
                pycore.xform("CTRL_faceGUI", translation=resolvedTranslation, relative=True)

            if resolvedScale:
                pycore.select(clear=True)
                cmds.select("GRP_faceGUI", add=True)
                cmds.scale(resolvedScale, resolvedScale, resolvedScale)

            convergenceGrp = pycore.PyNode("GRP_convergenceGUI")
            convergenceGrp.translate.set([0.0, 0.0, 0.0])

    def createBodyJointsSet(self, bodyJoints):
        pycore.select(clear=True)
        for bj in bodyJoints:
            if pycore.objExists(bj):
                cmds.select(bj, add=True)
        cmds.sets(n="Body joints")

    def createControlsSet(self):
        import dna
        fileStream = dna.FileStream(str(self.characterConfig.dnaPath),
                                    dna.FileStream.AccessMode_Read, dna.FileStream.OpenMode_Binary)
        reader = dna.StreamReader(fileStream)
        reader.read()
        pycore.select(clear=True)
        for i in range(reader.getGUIControlCount()):
            controlName = reader.getGUIControlName(i).split(".")[0]
            if pycore.objExists(controlName):
                cmds.select(controlName, add=True)

        if pycore.objExists("CTRL_C_eye"):
            cmds.select("CTRL_C_eye", add=True)

        if pycore.objExists("CTRL_rigLogicSwitch"):
            cmds.select("CTRL_rigLogicSwitch", add=True)

        if pycore.objExists("CTRL_lookAtSwitch"):
            cmds.select("CTRL_lookAtSwitch", add=True)

        if pycore.objExists("CTRL_C_eyesAim"):
            cmds.select("CTRL_C_eyesAim", add=True)

        if pycore.objExists("CTRL_C_neck_swallow"):
            cmds.select("CTRL_C_neck_swallow", add=True)

        if pycore.objExists("CTRL_L_eyeAim"):
            cmds.select("CTRL_L_eyeAim", add=True)

        if pycore.objExists("CTRL_R_eyeAim"):
            cmds.select("CTRL_R_eyeAim", add=True)

        if pycore.objExists("CTRL_convergenceSwitch"):
            cmds.select("CTRL_convergenceSwitch", add=True)

        if pycore.objExists("CTRL_neckCorrectivesMultiplyerU"):
            cmds.select("CTRL_neckCorrectivesMultiplyerU", add=True)

        if pycore.objExists("CTRL_neckCorrectivesMultiplyerM"):
            cmds.select("CTRL_neckCorrectivesMultiplyerM", add=True)

        if pycore.objExists("CTRL_neckCorrectivesMultiplyerD"):
            cmds.select("CTRL_neckCorrectivesMultiplyerD", add=True)

        if pycore.objExists("CTRL_faceGUIfollowHead"):
            cmds.select("CTRL_faceGUIfollowHead", add=True)

        if pycore.objExists("CTRL_eyesAimFollowHead"):
            cmds.select("CTRL_eyesAimFollowHead", add=True)

        cmds.sets(n="FacialControls")

    def moveBodyMeshesToLODGroups(self, bodyMeshName):
        from DHI.core.consts import FLIP_FLOP_SHADERS
        try:
            # create layer groups
            pycore.group(parent="geometry_grp", empty=True, name="body_lod0_grp")
            pycore.group(parent="geometry_grp", empty=True, name="body_lod1_grp")
            pycore.group(parent="geometry_grp", empty=True, name="body_lod2_grp")
            pycore.group(parent="geometry_grp", empty=True, name="body_lod3_grp")

            pycore.select(clear=True)
            pycore.select("body_lod3_grp", replace=True)
            pycore.createDisplayLayer(name="body_lod3_layer", noRecurse=True)
            pycore.setAttr("body_lod3_layer.visibility", 0)

            pycore.select("body_lod2_grp", replace=True)
            pycore.createDisplayLayer(name="body_lod2_layer", noRecurse=True)
            pycore.setAttr("body_lod2_layer.visibility", 0)

            pycore.select("body_lod1_grp", replace=True)
            pycore.createDisplayLayer(name="body_lod1_layer", noRecurse=True)
            pycore.setAttr("body_lod1_layer.visibility", 0)

            pycore.select("body_lod0_grp", replace=True)
            pycore.createDisplayLayer(name="body_lod0_layer", noRecurse=True)
            pycore.setAttr("body_lod0_layer.visibility", 1)
            pycore.select(clear=True)

            # remove unused layers
            if pycore.objExists(self.characterConfig.bodyMeshName.replace("_body", "") + "_LOD0_layer"):
                pycore.delete(self.characterConfig.bodyMeshName.replace("_body", "") + "_LOD0_layer")
            if pycore.objExists(self.characterConfig.bodyMeshName.replace("_body", "") + "_LOD1_layer"):
                pycore.delete(self.characterConfig.bodyMeshName.replace("_body", "") + "_LOD1_layer")
            if pycore.objExists(self.characterConfig.bodyMeshName.replace("_body", "") + "_LOD2_layer"):
                pycore.delete(self.characterConfig.bodyMeshName.replace("_body", "") + "_LOD2_layer")
            if pycore.objExists(self.characterConfig.bodyMeshName.replace("_body", "") + "_LOD3_layer"):
                pycore.delete(self.characterConfig.bodyMeshName.replace("_body", "") + "_LOD3_layer")
            if pycore.objExists(self.characterConfig.bodyMeshName.replace("_body", "") + "_lod0_layer"):
                pycore.delete(self.characterConfig.bodyMeshName.replace("_body", "") + "_lod0_layer")
            if pycore.objExists(self.characterConfig.bodyMeshName.replace("_body", "") + "_lod1_layer"):
                pycore.delete(self.characterConfig.bodyMeshName.replace("_body", "") + "_lod1_layer")
            if pycore.objExists(self.characterConfig.bodyMeshName.replace("_body", "") + "_lod2_layer"):
                pycore.delete(self.characterConfig.bodyMeshName.replace("_body", "") + "_lod2_layer")
            if pycore.objExists(self.characterConfig.bodyMeshName.replace("_body", "") + "_lod3_layer"):
                pycore.delete(self.characterConfig.bodyMeshName.replace("_body", "") + "_lod3_layer")

            # move body meshes to world so we can group them in LOD (no parents allowed)
            for i in range(0, 4):
                meshName = "%s_lod%s_mesh" % (bodyMeshName, str(i))
                if pycore.objExists(meshName):
                    pycore.parent(meshName, "body_lod" + str(i) + "_grp")

            # move combined mesh to LOD_0
            resolvedBodyMeshName = self.characterConfig.bodyMeshName.replace("_body", "") + "_combined_lod0_mesh"
            if pycore.objExists(resolvedBodyMeshName):
                # set default shader
                pycore.select(clear=True)
                pycore.select(resolvedBodyMeshName, r=True)
                mel.eval("sets -e -forceElement initialShadingGroup")
                pycore.hide(resolvedBodyMeshName)
                pycore.parent(resolvedBodyMeshName, "body_lod0_grp")

            # move flip flops
            flipFlopsMeshes = []
            for i in range(0, 4):
                flipFlopsMeshName = bodyMeshName.replace('_body', '') + '_flipflops'
                flipFlopsMesh = "%s_lod%s_mesh" % (flipFlopsMeshName, str(i))
                flipFlopsMeshes.append((str(i), flipFlopsMesh))

                # quick fix for bodies with non aligned flip flop names
                flipFlopsMesh = "f_med_shs_flipflops_lod%s_mesh" % (str(i))
                flipFlopsMeshes.append((str(i), flipFlopsMesh))

                flipFlopsMesh = "OBJ_m_srt_shs_flipflops_lod%s_mesh" % (str(i))
                flipFlopsMeshes.append((str(i), flipFlopsMesh))

            for lod, meshName in flipFlopsMeshes:
                if pycore.objExists(meshName):
                    pycore.parent(meshName, "body_lod" + lod + "_grp")

            MESH_SHADER_MAPPING = {}
            MESH_SHADER_MAPPING[bodyMeshName.replace("_body", "") + "_flipflops_lod"] = u'flipflop_shader'
            MESH_SHADER_MAPPING["f_med_shs_flipflops_lod"] = u'flipflop_shader'
            MESH_SHADER_MAPPING["OBJ_m_srt_shs_flipflops_lod"] = u'flipflop_shader'
            MayaUtil.importShader(self.characterConfig.flipflopsScenePath, MESH_SHADER_MAPPING)
            MayaUtil.resolveSceneMapPaths(FLIP_FLOP_SHADERS, self.characterConfig.flipflopsDirPath)

            # remove unused body group and meshes
            if pycore.objExists("export_geo_grp"):
                pycore.delete("export_geo_grp")
        except Exception as e:
            print("Error moving body meshes to their corresponding LOD groups")
            print (e)
            pass

    def importBodyAndAttachToHead(self):
        from DHI.modules.file.reader import PythonConfigurationReader
        current = os.path.dirname(os.path.abspath(__file__))

        progressWindowManager.update(0, 'Starting body import')

        self.configurationModule = PythonConfigurationReader(
            FileHandler.joinPath((current, "core/consts.py"))).readFile()

        self.importBodyAndParentConstraint()
        self.removeUnknownPlugins()
        self.moveBodyMeshesToLODGroups(self.characterConfig.bodyMeshName)

        self.importBodyShader(self.characterConfig.bodyShaderScenePath, self.characterConfig.bodyMeshName)
        progressWindowManager.update(0, 'Body import done')

    def removeUnknownPlugins(self):
        unknown_plugins = cmds.unknownPlugin(query=True, list=True)
        if unknown_plugins:
            for plugin in unknown_plugins:
                try:
                    cmds.unknownPlugin(plugin, remove=True)
                except Exception as err:
                    print(err.message)

    def importBodyAndParentConstraint(self):
        from DHI.modules.maya.handler import MayaSkinHandler
        import DHI.core.consts as consts

        headNamespace = "DHIhead"
        headJoints = [joint for joint in pycore.ls(type="joint")]

        pycore.namespace(add=headNamespace)
        self.addJointsToNamespace(headNamespace, headJoints)

        # import body to scene
        pycore.importFile(self.characterConfig.bodyScenePath, options="v=0", type="mayaAscii")

        # add parent constraint for all matching head joints to body joints
        cmds.select("root")
        bodyJoints = cmds.listRelatives(allDescendents=True, type='joint')

        bodyMeshName = self.characterConfig.bodyMeshName
        meshNames = []
        for i in range(0, 4):
            meshName = "%s_lod%s_mesh" % (bodyMeshName, str(i))
            meshNames.append(meshName)
            flipFlopsMeshName = bodyMeshName.replace('_body', '') + ('_flipflops')
            flipFlopsMesh = "%s_lod%s_mesh" % (flipFlopsMeshName, str(i))
            meshNames.append(flipFlopsMesh)

        meshesToAdapt = []
        skinWeights = []

        msh = MayaSkinHandler()
        # fetch all mesh names and skin weights and remove mesh clusters

        MayaUtil.logger.info("Fetching all mesh names and skin weights and remove mesh clusters")
        for meshName in meshNames:
            if pycore.objExists(meshName):
                meshesToAdapt.append(meshName)
                skinWeights.append(msh.getSkinWeightsFromScene(meshName))
                pycore.delete(msh.getSkinWeightsData(meshName)[1])

        MayaUtil.logger.info("Moving pelvis")
        cmds.move(0, 0, 2, 'pelvis_drv', r=True)

        MayaUtil._adaptMeshes(consts.SCALE, consts.SCALE_PIVOT, [0.0, 0.0, 0.0], meshNames, consts.TRANSLATE_FACTOR)
        MayaUtil.logger.info("Moving pivots for meshes")
        for meshName in meshNames:
            if pycore.objExists(meshName):
                cmds.move(0, 0, 0, meshName + ".scalePivot", meshName + ".rotatePivot", absolute=True)

        # # apply skin weights
        for meshName, skinWeight in zip(meshesToAdapt, skinWeights):
            msh.createSkinCluster(skinWeight.joints, meshName, meshName + "_skinCluster", skinWeight.noOfInfluences)
            msh.setSkinWeightsToScene(meshName, skinWeight)

        bodyJoints.append("root")
        for bj in bodyJoints:
            hj = headNamespace + ":" + bj
            if hj in headJoints:
                pycore.parentConstraint(bj, hj, maintainOffset=True)
                pycore.scaleConstraint(bj, hj, maintainOffset=True)

    def addJointsToNamespace(self, name, joints):
        for joint in joints:
            newname = joint.swapNamespace(name)
            joint.rename(newname)

    def importHeadShaders(self):
        from DHI.core.consts import MASKS, SHADERS, MESH_SHADER_MAPPING, MAP_INFOS, COMMON_MAP_INFOS, \
            SHADER_ATTRIBUTES_MAPPING

        shaderScenePath = self.characterConfig.shaderScenePath
        MayaUtil.logger.info("Shader scene path: %s" % (shaderScenePath))
        progressWindowManager.update(0, "Importing shader scene from: %s" % shaderScenePath)
        MayaUtil.importShader(shaderScenePath, MESH_SHADER_MAPPING)
        if self.characterConfig.platform is "Windows":
            MayaUtil.resolveSceneShaderPaths(SHADERS, self.characterConfig.shadersDirPath)
        MayaUtil.resolveSceneMaskPaths(MASKS, self.characterConfig.masksDirPath)
        MayaUtil.resolveSceneMapPaths(COMMON_MAP_INFOS, self.characterConfig.headMapsPath)
        MayaUtil.resolveSceneMapPaths(MAP_INFOS, self.characterConfig.mapsDirPath)

        MayaUtil.connectAttributesToShader(SHADER_ATTRIBUTES_MAPPING)
        progressWindowManager.update(0, "Shader imported.")

    def importBodyShader(self, shaderScenePath, bodyMeshName):
        pycore.importFile(shaderScenePath, options="v=0", type="mayaAscii")
        from DHI.core.consts import BODY_MAP_INFOS, BODY_SHADERS, COMMON_MAP_INFOS_BODY
        for lodLvl in range(0, 4):
            try:
                # Apply shader to all meshes based on LOD level
                resolvedMeshName = bodyMeshName + "_lod" + str(lodLvl) + "_mesh"
                pycore.select(resolvedMeshName, replace=True)
                pycore.mel.eval("sets -e -forceElement shader_body_shaderSG")
            except (pycore.MayaNodeError, ValueError):
                MayaUtil.logger.warning("Skipped adding shader for body mesh %s." % lodLvl)

        MayaUtil.resolveSceneMapPaths(BODY_MAP_INFOS, self.characterConfig.mapsDirPath)

        if self.characterConfig.platform is "Windows":
            MayaUtil.resolveSceneShaderPaths(BODY_SHADERS, self.characterConfig.shadersDirPath)
        MayaUtil.resolveSceneMapPaths(COMMON_MAP_INFOS_BODY, self.characterConfig.headMapsPath)

    def importHeadLightScene(self):
        progressWindowManager.update(0, "Importing head light scene.")

        lightScenePath = self.characterConfig.lightScenePath
        MayaUtil.createLights(lightScenePath, self.characterConfig.sceneOrientation)
        progressWindowManager.update(0, "Importing head light scene done.")

    def importHead(self):
        MayaUtil.logger.info('Head import started...')
        progressWindowManager.update(0, 'Starting head import')

        MayaUtil.logger.info('Resolving DNA path...')
        dnaPath = self.resolveRLDNAPathFromDNAPath(self.characterConfig.dnaPath)
        MayaUtil.logger.info('Resolving GUI path...')
        guiPath = self.characterConfig.guiPath
        progressWindowManager.update(0, "Importing head from DNA path: %s" % dnaPath)

        MayaUtil.logger.info('Opening new file...')
        pycore.newFile(force=True)
        pycore.upAxis(ax=self.characterConfig.sceneOrientationStringValue, rv=True)

        MayaUtil.logger.info('Fetching character name...')
        characterName = FileHandler.getCharNameFromFileName(dnaPath)[0]
        MayaUtil.logger.info("Character name is " + characterName)

        MayaUtil.logger.info("Initiating rig logic node builder")
        rl4nb = RigLogicNodeBuilder()
        rl4nb.setName("rl4Embedded_" + characterName)
        rl4nb.setFlag("-dfp", dnaPath)

        analogGuiOptions = AnalogGuiOptions.defaultOptions()
        analogGuiOptions.GuiPath = self.characterConfig.acPath
        current = os.path.dirname(os.path.abspath(__file__))

        sceneBuilder = SceneBuilder()

        sceneBuilder. \
            FromDnaPath(dnaPath). \
            And(). \
            WithGui(guiPath). \
            And(). \
            WithAnalogGuiOptions(analogGuiOptions). \
            And(). \
            WithFRMAttrs("FRM_WMmultipliers"). \
            And(). \
            WithRigLogicNodeBuilder(rl4nb). \
            And(). \
            WithNormals(). \
            And(). \
            WithSceneOrientation(self.characterConfig.sceneOrientation). \
            And(). \
            WithLinearUnit("cm"). \
            And(). \
            WithAngleUnit("degree"). \
            And(). \
            WithGender(self.characterConfig.gender). \
            And(). \
            WithCharacterHeight(self.characterConfig.height). \
            And(). \
            WithAAS(FileHandler.joinPath((current, "connectexp.py")))

        try:
            sceneBuilder.build()
            self.importHeadShaders()
            self.importHeadLightScene()
        except SceneBuilderError as ex:
            print ("Scene builder error", ex.message)
        except Exception as ex:
            print ("Unexpected error occurred - %s!" % ex.message)
            print (ex)
