import os
from DHI.modules.file.handler import FileHandler
import DHI.core.consts as consts
import dna


class CharacterConfig(object):
    def __init__(self, config):
        self.current = os.path.dirname(os.path.abspath(__file__))

        self.dnaPath = self.prepareInput(config["characterAssets"]["dnaPath"])
        self.dnaPathDir = self.resolveDnaPathDir(self.dnaPath)
        self.characterName = self.resolveCharacterName(self.dnaPath)
        self.workspaceDir = self.resolveWorkspacePath(self.dnaPath)
        self.bodyScenePath = self.prepareInput(config["characterAssets"]["bodyPath"])
        self.dnaVersion = self.resolve_dna_version(self.dnaPath)

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
        self.db_version_path = FileHandler.joinPath(("db_versions", self.dnaVersion, "assets"))

        '''
        Head GUI controls
        '''
        self.guiPath = FileHandler.joinPath((self.current, self.db_version_path, self.resolvePlatform(), "head_gui.ma"))

        '''
        Eye controls
        '''
        self.flipflopsDirPath = config["characterAssets"]["mapsDirPath"]
        self.flipflopsScenePath = FileHandler.joinPath(
            (self.current, self.db_version_path, "flipflops", "filplop_mtl_v001.ma"))
        self.acPath = FileHandler.joinPath((self.current, self.db_version_path, self.resolvePlatform(), "head_ac.ma"))
        self.shaderScenePath = FileHandler.joinPath(
            (self.current, self.db_version_path, self.resolvePlatform(), "head_shader.ma"))
        self.bodyShaderScenePath = FileHandler.joinPath(
            (self.current, self.db_version_path, self.resolvePlatform(), "body_shader.ma"))
        self.lightScenePath = FileHandler.joinPath(
            (self.current, self.db_version_path, self.resolvePlatform(), "dh_lights.ma"))

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

    def resolve_dna_version(self, dna_path):
        input_dna = dna.FileStream(str(dna_path),
                                   dna.FileStream.AccessMode_Read, dna.FileStream.OpenMode_Binary)
        input_reader = dna.BinaryStreamReader(input_dna)
        input_reader.read()
        db_name = input_reader.getDBName()

        if db_name == "DHI":
            version = "MH.2"
        else:
            version = db_name

        return version

    def __str__(self):
        return """
            DNA path: %s
            DNA Version: %s
            DNA Version Data Path: %s
            Body Scene Path: %s
            Body Mesh Name: %s
            Head Shaders Dir Path: %s
            Head Specific Maps Dir Path: %s
            Head Common Maps Dir Path: %s
            Masks dir path: %s
            Eye controls: %s
            FlipFlops dir path: %s
            Scene Orientation: %s
        """ % (self.dnaPath,
               self.dnaVersion,
               self.db_version_path,
               self.bodyScenePath,
               self.bodyMeshName,
               self.shadersDirPath,
               self.mapsDirPath,
               self.headMapsPath,
               self.masksDirPath,
               self.acPath,
               self.flipflopsDirPath,
               self.sceneOrientation)
