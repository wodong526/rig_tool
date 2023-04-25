from DHI.modules.dna.model.transform import Transformation


class Translation(Transformation):
    def __init__(self):
        super(Translation, self).__init__()
      
    def name(self):
        return 'Translation'
    
class Orientation(Transformation):
    def __init__(self):
        super(Orientation, self).__init__()
      
    def name(self):
        return 'Orientation'