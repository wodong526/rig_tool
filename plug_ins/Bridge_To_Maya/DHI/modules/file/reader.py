from abc import ABCMeta, abstractmethod
import imp
import csv
from DHI.core.logger import Logger
from DHI.modules.file.handler import FileHandler


class ConfigurationReader(object):
    '''
    Abstract Base class for reading config files.
    '''
    _metaclass_ = ABCMeta
    
    logger = Logger.getInstance(__name__)
    
    def __init__(self, path, fileExtension):
        self.confFilePath = path
        self._fileExtension = fileExtension
    
    def readFile(self):
        '''
        Method for reading documents/maya config file.
        @return: configuration
        '''
        if FileHandler.isFile(self.confFilePath) and self.confFilePath.endswith(self._fileExtension):
            try:
                return self._doReadFile()
            except Exception as ex:
                self.logger.error("Couldn't read configuration file. Reason: %s" % str(ex))
                return None
        else:
            return None
    
    @abstractmethod 
    def _doReadFile(self):
        pass

class PythonConfigurationReader(ConfigurationReader):
    '''
    Class for reading documents/maya config file.
    '''
    def __init__(self, path):
        super(PythonConfigurationReader, self).__init__(path, ".py")
    
    def _doReadFile(self):
        '''
        @return: Returns python module that contains configuration. Module is loaded every time this method is invoked
        '''
        configurationFile = imp.load_source("configurationFile", self.confFilePath)
        return configurationFile
        
class JsonConfigurationReader(ConfigurationReader):
    '''
    Class for reading json documents/maya config file.
    '''
    def __init__(self, path, inputPath, outputPath):
        super(JsonConfigurationReader, self).__init__(path, ".json")
        self._inputPath = inputPath
        self._outputPath = outputPath
        self._conf = None
        
        import json
        
        with open(self.confFilePath, "r") as jsonConfig:
            self._conf = json.load(jsonConfig)
            self._conf["inputfolder"] = self._inputPath
            self._conf["outputfolder"] = self._outputPath
            
            found = True
            
            while found:
                found = self._replacePlaceholders()
        
    def _doReadFile(self):
        '''
        @return: Returns python module that contains configuration. Module is loaded every time this method is invoked
        '''
        return self._conf
    
    def _replacePlaceholders(self):
        import re
                
        found = False
        for confitem in self._conf.iteritems():
            result = re.match("{[^}]*}", str(confitem[1]))
            if result:
                self._conf[confitem[0]] = confitem[1].replace(result.group(0), self._conf[result.group(0)[1:-1]])
                found = True
                
        return found
        
class InitialConfigurationReader(PythonConfigurationReader):
    '''
    Class for reading documents/maya config file.
    @return: Returns namespace
    '''
    # Singleton instance
    _instance = None
    
    def __init__(self, confFilePath):
        super(InitialConfigurationReader, self).__init__(confFilePath)

    @staticmethod
    def getInstance(confFilePath):
        '''
        Gets instance of client main object.

        This is static method returning instance of singleton class.
        @return DeliveryController instance. (DeliveryController)
        '''

        if InitialConfigurationReader._instance is None:
            InitialConfigurationReader._instance = InitialConfigurationReader(confFilePath)
        return InitialConfigurationReader._instance 
                        
    