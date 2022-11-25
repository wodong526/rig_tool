import os
from DHI.modules.file.handler import FileHandler
import DHI.core.consts as consts


class CharacterConfig(object):
    def __init__(self, config):
        self.current = os.path.dirname(os.path.abspath(__file__))

        self.dnaPath = self.prepareInput(config["characterAssets"]["dnaPath"])
        self.dnaPathDir = self.resolveDnaPathDir(self.dnaPath)
        self.characterName = self.resolveCharacterName(self.dnaPath)
        self.workspaceDir = self.resolveWorkspacePath(self.dnaPath)
        self.bodyScenePath = self.prepareInput(config["characterAssets"]["bodyPath"])

        self.platform = self.resolvePlatform()
        '''
        Each body has its own body mesh name. This information is needed in later steps of character assembly when 
        we are grouping body meshes into their corresponding LOD groups 
        '''
        self.bodyMeshName = self.resolveBodyMeshName(self.prepareInput(config["characterAssets"]["bodyPath"]))
        self.shadersDirPath = config["common"]["shadersDirPath"]
        self.masksDirPath = config["common"]["masksDirPath"]
        self.sceneOrientationStringValue = self.resolveSceneOrientationStringValue(config["common"])
        self.sceneOrientation = self.resolveSceneOrientation()

        self.gender = self.bodyMeshName.split("_")[0]
        self.height = self.bodyMeshName.split("_")[1]
        self.weight = self.bodyMeshName.split("_")[2]

        '''
        Path to head common maps (specular, diffuse, jitter,...). Assets found here are common for all characters and 
        are part of plugin
        '''
        self.headMapsPath = config["common"]["headMapsPath"]
        self.mapsDirPath = config["characterAssets"]["mapsDirPath"]

        '''
        Head GUI controls
        '''
        self.guiPath = FileHandler.joinPath((self.current, "assets", self.resolvePlatform(), "head_gui.ma"))

        '''
        Eye controls
        '''
        self.flipflopsDirPath = config["characterAssets"]["mapsDirPath"]
        self.flipflopsScenePath = FileHandler.joinPath((self.current, "assets", "flipflops", "filplop_mtl_v001.ma"))
        self.acPath = FileHandler.joinPath((self.current, "assets", self.resolvePlatform(), "head_ac.ma"))
        self.shaderScenePath = FileHandler.joinPath((self.current, "assets", self.resolvePlatform(), "head_shader.ma"))
        self.bodyShaderScenePath = FileHandler.joinPath((self.current, "assets", self.resolvePlatform(), "body_shader.ma"))
        self.lightScenePath = FileHandler.joinPath((self.current, "assets", self.resolvePlatform(), "dh_lights.ma"))

    def prepareInput(self, val):
        return val.replace("\\", "/")

    def resolveBodyMeshName(self, bodyPath):
        fileName = bodyPath.split("/")[-1]
        retval = fileName.replace("_rig.ma", "")
        return retval

    def resolveCharacterName(self, dnaFilePath):
        fileName = dnaFilePath.split("/")[-1]
        retval = fileName.replace(".dna", "")
        return retval

    def resolveDnaPathDir(self, dnaFilePath):
        resolvedPath = os.path.dirname(dnaFilePath).replace("\\", "/")
        return resolvedPath.replace("\\", "/")

    def resolveWorkspacePath(self, dnaFilePath):
        resolvedPath = os.path.dirname(dnaFilePath).replace("\\", "/")
        resolvedPath = os.path.abspath(os.path.join(resolvedPath, "../.."))
        return resolvedPath.replace("\\", "/")

    def resolveSceneOrientationStringValue(self, configCommon):
        orientation = 'z'

        if "sceneOrientation" in configCommon:
            orientation = configCommon["sceneOrientation"]

        return orientation

    def resolveSceneOrientation(self):
        orientation = self.sceneOrientationStringValue

        if orientation == 'x':
            return consts.ORIENT_X
        elif orientation == 'y':
            return consts.ORIENT_Y
        else:
            return consts.ORIENT_Z

    def resolvePlatform(self):
        import platform
        platform = platform.system()

        if platform not in ["Windows", "Linux"]:
            platform = "Windows"

        return platform

    def __str__(self):
        return """
            DNA path: %s
            Body Scene Path: %s
            Body Mesh Name: %s
            Head Shaders Dir Path: %s
            Head Specific Maps Dir Path: %s
            Head Common Maps Dir Path: %s
            Masks dir path: %s
            Eye controls: %s
            Scene Orientation: %s
        """ % (self.dnaPath,
               self.bodyScenePath,
               self.bodyMeshName,
               self.shadersDirPath,
               self.mapsDirPath,
               self.headMapsPath,
               self.masksDirPath,
               self.acPath,
               self.sceneOrientation)
