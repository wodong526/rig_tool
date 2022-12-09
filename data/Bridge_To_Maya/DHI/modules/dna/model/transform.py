from abc import ABCMeta, abstractmethod

class Transformation(object):
    _metaclass_ = ABCMeta
    
    def __init__(self):
        self._x = None
        self._y = None
        self._z = None
        
    @property
    def X(self):
        return self._x
    
    @X.setter
    def X(self, number):
        self._x = number
        
    @property
    def Y(self):
        return self._y
    
    @Y.setter
    def Y(self, number):
        self._y = number

    @property
    def Z(self):
        return self._z
    
    @Z.setter
    def Z(self, number):
        self._z = number
        
    @abstractmethod
    def name(self):
        pass