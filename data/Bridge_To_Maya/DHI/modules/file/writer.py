from DHI.core.error import DNAEstimatorError
from DHI.core.logger import Logger


class FileWriteError(DNAEstimatorError):
    def __init__(self, myfile, error):
        self.message = "Error while writing in file: %s\n %s" % (myfile, error)


class FileWriter():
    
    logger = Logger.getInstance(__name__)
    
    def __init__(self, path):
        self.path = path
        
        with open(self.path, "w"):
            pass
        
    def writeToFile(self, attribute, value):
        """
        This function overides existing attribute in file with new value. If there is no attribute existing, it will be added.
        @param attribute: Attribute name.
        @param value: New attribute value.
        """
        attribute = str(attribute)
        value = str(value)
        
        if value == "" or attribute == "":
            self.logger.debug("Warning: Nothing to write.")
            return False
        
        try:
            with open(self.path, 'r') as f:
                # read a list of lines into data and get index of attributes line
                data = f.readlines()
                for index, line in enumerate(data):
                    if attribute in line:
                        try:
                            # specific attribute line should have this value
                            data[index] = attribute + " = " + "'" + value + "'" + "\n"
                            # overwrite everything in file with specific line changed
                            with open(self.path, 'w') as f:
                                f.writelines( data )
                        except Exception as ex:
                            self.logger.error("File is in invalid state")
                            raise FileWriteError(self.path, ex.message)
                        return True
                # if attr does not exist in file append line
                data.append(attribute + " = " + "'" + value + "'" + "\n")
                with open(self.path, 'w') as f:
                    f.writelines( data )
                return True
        except Exception as ex:
            self.logger.error("Invalid file path")
            raise FileWriteError(self.path, ex.message)