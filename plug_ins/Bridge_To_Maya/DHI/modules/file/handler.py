import csv
from distutils.dir_util import copy_tree
import json
import os, errno
import re
import shutil
import subprocess
try:
    import cPickle as pickle
except:
    import pickle

from DHI.core.error import DNAEstimatorError
from DHI.core.logger import Logger


class OSFileError(DNAEstimatorError):

    def __init__(self, message, error):
        self.message = "%s, Error: %s" % (message, error)

class FileHandler(object):
    
    logger = Logger.getInstance(__name__)

    @staticmethod
    def cleanPath(path):
        '''This method is used to replace user-written path separators with system ones.'''
        path = path.strip()
        if path:
            return os.path.normpath(path).replace(os.sep, '/')
        return path

    @staticmethod
    def joinPath(paths):
        ''' Utility method to create path out of parts. Paths must be list or tuple. '''     
        res = os.sep.join(str(el) for el in paths)
        return FileHandler.cleanPath(res)
    
    @staticmethod
    def createMissingFolders(path):
        '''
        Create any of the missing folders on the given path which contains file name.
        If some of the folders are missing they will be created as well.
        '''
        dir, file = os.path.split(path)
        FileHandler.createFolder(dir)
        
    @staticmethod
    def getFileName(path):
        return os.path.basename(path)
    
    @staticmethod
    def splitPath(path):
        return os.path.split(path)
    
    @staticmethod
    def pathExists(path):
        ''' Check if file or folder on given path exists.'''
        path = FileHandler.cleanPath(path)
        return os.path.exists(path)
    
    @staticmethod
    def isFile(path):
        ''' Check if file on given path exists.'''
        path = FileHandler.cleanPath(path)
        return os.path.exists(path) and os.path.isfile(path)
    
    @staticmethod
    def isFolder(path):
        ''' Check if folder on given path exists.'''
        path = FileHandler.cleanPath(path)
        return os.path.exists(path) and os.path.isdir(path)

    @staticmethod
    def createFolder(path):
        '''
        Create folder on the given path. Path contains only folders.
        If some of the folders are missing they will be created as well.
        '''
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise DNAEstimatorError("Failed to create folder", str(e))

            
    @staticmethod
    def copyFolder(sourceFolder, destinationFolder):
        '''Copy folder from sourceFolder to destinationFolder.'''
        try:
            sourceFolder = FileHandler.cleanPath(sourceFolder)
            if FileHandler.pathExists(sourceFolder):
                # Add missing parent folders for destination
                destinationFolder = FileHandler.cleanPath(destinationFolder)
                FileHandler.createFolder(destinationFolder)
                # Copy folder
                copy_tree(sourceFolder, destinationFolder)
                FileHandler.logger.debug("Folder copied from: '%s' to: '%s'." % (sourceFolder, destinationFolder))
                return True
            FileHandler.logger.warn("Folder is not copied as path '%s' does not exists." % sourceFolder)
            return False
        except OSError as e:
            if e.errno != errno.EEXIST:
                msg = "Folder is not copied"
                FileHandler.logger.error(msg)
                raise OSFileError(msg, str(e))
            
    @staticmethod
    def copyFile(sourceFilePath, destinationFolderPath, newName=None):
        '''Copy file from sourceFilePath to destinationFolderPath with renaming if newName is provided.'''
        try:
            sourceFilePath = FileHandler.cleanPath(sourceFilePath)
            if FileHandler.pathExists(sourceFilePath):
                # Add missing parent folders for destination
                destinationFolderPath = FileHandler.cleanPath(destinationFolderPath)
                FileHandler.createFolder(destinationFolderPath)
                # Copy file
                dir, file = os.path.split(sourceFilePath)
                if newName:
                    oldName = os.path.splitext(file)[0]
                    file = file.replace(oldName, newName)
                dest = FileHandler.joinPath((destinationFolderPath, file))
                shutil.copyfile(sourceFilePath, dest)
                FileHandler.logger.debug("File copied from: '%s' to: '%s'." % (sourceFilePath, dest))
                return True
            FileHandler.logger.warn("File is not copied as path '%s' does not exists." % sourceFilePath)
            return False
        except OSError as ex:
            msg = "File is not copied"
            FileHandler.logger.error(msg)
            raise OSFileError(msg, str(ex))

    @staticmethod
    def delete(path):
        '''
        Delete file or folder. Returns status.
        @param path: path to the folder or file to be removed.
        @return: status - true in case it is deleted, false if not.
        '''
        path = FileHandler.cleanPath(path)
        if os.path.isfile(path):
            os.remove(path)
            FileHandler.logger.debug("File removed: '%s'" % path)
            return True
        elif os.path.isdir(path):
            shutil.rmtree(path)
            FileHandler.logger.debug("Folder and all its sub-folders removed: '%s'" % path)
            return True
        return False
    
    @staticmethod
    def listFiles(folder, criteria="*", fileNameOnly=True):
        '''
        Give the list of files inside folder which match criteria regular expression.
        @param folder: root directory which will be listed
        @param criteria: regular expression to match list
        @param fileNameOnly: True if only list of file names should be returned, False if full paths are to be returned
        @return: list of files that match input parameters
        ''' 
        criteria = criteria.replace(".", "\.").replace("*", ".+")
        criteria = "^" + criteria + "$"
        FileHandler.logger.debug("[listFiles] Criteria is '%s'." % criteria)
        try:
            folder = FileHandler.cleanPath(folder)
            if fileNameOnly:
                return sorted([file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))\
                         and re.findall(criteria, file)])
            return sorted([FileHandler.cleanPath(file) for file in (os.path.join(folder, f) for f in os.listdir(folder) if re.findall(criteria, f))\
                     if os.path.isfile(file)])
        except Exception as ex:
            raise OSFileError("Failed to list files", str(ex))
    
    @staticmethod
    def getLastFile(folder, filePrefix):
        '''
        List folder and find the last file with given criteria (name prefix).
        '''
        files = FileHandler.listFiles(folder, filePrefix + "*")
        if files:
            return files[-1]
        return None
        
    @staticmethod
    def getNextFileName(fileName):
        '''
        This method would check for number sequence (example _001) and return the same name with increased value. 
        In case more than one sequence is found - the last one would be increased.
        For example:
            - for input test_001.txt would get test_002.txt
            - for delivery_01.py => delivery_02.py
        @param fileName: original file name
        @return: string that would be file name with increased number for version  
        '''
        
        values = re.findall("_\d+", fileName)
        if values:
            # get the last one
            value = values[-1]
            size = len(value)
            newValue = int(value[1:]) + 1
            
            replacement = "_" + str(newValue).zfill(size-1)
            index = fileName.rfind(value)
            return fileName[:index] + replacement + fileName[index+size:]
        else:
            return fileName
        
    @staticmethod
    def getCharNameFromFileName(fileName):
        '''
        This method would check for number sequence (example _001) and return the tuple name (example) and version (001). 
        @param fileName: original file name
        @return: (string, string) file name and version with leading 0 if found in original name  
        '''
        name = FileHandler.getFileName(fileName)
        values = re.findall("_\d+", name)
        if values:
            # get the last one
            value = values[-1]    
            index = name.rfind(value)
            return (name[:index], value[1:])
        
        else:
            # no version - remove extension if exists
            return (os.path.splitext(name)[0], "0")
            
    @staticmethod
    def openPathInExplorer(path):
        try:
            path = os.path.normpath(path)
            if os.path.isdir(path):
                subprocess.Popen(r'explorer %s' % path)
        except Exception as ex:
            raise OSFileError("Failed to open path %s in explorer" % path, ex.message)
        
    @staticmethod
    def createVersionedName(name, version, versionLength):
        return name + "_" + str(version).zfill(versionLength)
    
    @staticmethod
    def zipFolder(zipPath, folderPath):
        try:
            shutil.make_archive(zipPath, 'zip', folderPath)
        except Exception as ex:
            raise OSFileError("Failed to make zip from folder %s." % folderPath, ex.message)    
    
class FileUtil(object):
    
    logger = Logger.getInstance(__name__)
    
    @staticmethod
    def readRegionsFromCSVFile(filePath):
        regions = []
        try:
            with open(filePath, 'r') as csvfile:
                fileread = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in fileread:
                    if len(row) > 2:
                        regions = row
                        break
        except Exception as ex:
            FileUtil.logger.error("Reading regions from csv file '%s' failed. Reason: %s" % (filePath, ex.message))
        return regions
    
    @staticmethod
    def writeToJson(data, filePath):
        try:
            with open(filePath, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as ex:
            FileUtil.logger.error("Writing in JSON file '%s' failed. Reason: %s" % (filePath, ex.message))        
          
    @staticmethod
    def readFromJson(filePath):
        data = {}
        try:
            with open(filePath, 'r') as f:
                data = json.load(f)
        except Exception as ex:
            FileUtil.logger.error("reading from JSON file '%s' failed. Reason: %s" % (filePath, ex.message))     
        return data
    
    
    @staticmethod
    def writeToPickle(data, filePath):
        try:
            with open(filePath, 'w') as file:
                pickle.dump(data, file)
        except Exception as ex:
            FileUtil.logger.error("Writing to pickle file '%s' failed. Reason: %s" % (filePath, ex.message))        
          
    @staticmethod
    def readFromPickle(filePath):
        data = {}
        try:
            with open(filePath, 'r') as f:
                data = pickle.load(f)
        except Exception as ex:
            FileUtil.logger.error("reading from JSON file '%s' failed. Reason: %s" % (filePath, ex.message))     
        return data