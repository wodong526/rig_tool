class DNAEstimatorError(Exception):
    '''Basic DNAEstimator exception. This is super-class for all DNAEstimator exceptions.'''

    def __init__(self, message=None):
        '''
        self.message is string representing human readable message.
        '''
        self.message = message

    def __str__(self):
        return "DNAEstimatorError: " + self.message
