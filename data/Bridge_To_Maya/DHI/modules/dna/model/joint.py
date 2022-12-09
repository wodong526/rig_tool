class Joint(object):
    def __init__(self, name, translation, orientation, parentName):
        self._name = name
        self._translation = translation
        self._orientation = orientation
        self._parentName = parentName
        
    @property
    def name(self):
        return self._name
    
    @property
    def parentName(self):
        return self._parentName
    
    @property
    def translation(self):
        return self._translation
    
    @property
    def orientation(self):
        return self._orientation