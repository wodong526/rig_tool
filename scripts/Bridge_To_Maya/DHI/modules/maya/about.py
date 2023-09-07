'''
This module contains classes and methods which can give information about
environment in which program is running.
Depending on that information different libraries can be loaded, different 
methods can be called and so on.
For example, depending on Maya version, different Python version is used.
Because of that, different set of Python libraries is loaded depending on Maya 
version.
'''

import pymel.core as pycore
from maya.OpenMaya import MGlobal


class AboutEnv:
    '''
    Maya about environment class. This is a singleton class.
    
    This class contains data about Maya environment.
    Arrtibutes:        
        version (string): Maya version number.
        bit (string): 32 or 64 bit Maya version indicator.
        qtVersion (string): Supported Qt version number.
    '''

    # singleton instance
    _instance = None

    @staticmethod
    def getInstance():
        if AboutEnv._instance is None:
            AboutEnv._instance = AboutEnv()
        return AboutEnv._instance

    def __init__(self):
        self.version = "2017"
        self.bit = "x64"
        self.qtVersion = pycore.about(qtVersion=True)
        self.hasGui = MGlobal.mayaState() == MGlobal.kInteractive or \
                      MGlobal.mayaState() == MGlobal.kBaseUIMode

        aboutVersion = pycore.about(version=True)

        supportedVersions = {
            "2017": [],
            "2018": [],
            "2019": [],
            "2020": [],
            "2022": [],
            "2023": []
        }

        for version, extraArgs in supportedVersions.items():
            # first check if required extra arguments comply with aboutVersion
            extraArgsComply = True
            for arg in extraArgs:
                if arg not in aboutVersion:
                    extraArgsComply = False
                    break
            # if extra arguments comply, and the version also fits...
            if extraArgsComply and version in aboutVersion:
                self.version = version
                if version == "2016 Extension":
                    self.version = "2016"

    def getNameWithVersionPrefix(self, name):
        '''
        Gets given name string expended for Maya version and bit as a prefix.
        
        @param name: Given name string to be extended. (string)
        @return New name string extended with prefix. (string)
        '''

        return (self.version + "_" + self.bit + "_" + name)
