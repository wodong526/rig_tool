import logging

class Logger(object):
    '''
    Base class to initialize logger.
    '''
    LOGGER_NAME = "dhi"
    
    # Singleton instance
    _instance = None

    def __init__(self, logger):
        '''
        Constructor
        '''
        self.setupLogger(logger)

    @staticmethod
    def getInstance(name):
        '''
        Gets instance of cache object.

        This is static method returning instance of singleton class.
        '''
        if Logger._instance is None:   
            logger = logging.getLogger(Logger.LOGGER_NAME)
            logger.propagate = False
            if not logger.handlers:
                Logger._instance = Logger(logger)      
        return logging.getLogger(name)
    
    
            

    def setupLogger(self, logger, default_level=logging.DEBUG):
        '''
        Setup logging configuration
        '''
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s'))
        handler.setLevel(default_level)
        logger.addHandler(handler)
        
