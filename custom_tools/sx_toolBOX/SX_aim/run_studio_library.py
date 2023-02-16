# -----------------------------------
# Studio Library
# www.studiolibrary.com
# -----------------------------------

import os
import sys

if not os.path.exists(r'Z:\Library\rig_plug_in\maya_plug\data\studio_library'):
    raise IOError(r'The source path "Z:\Library\rig_plug_in\maya_plug\data\studio_library" does not exist!')

if r'Z:\Library\rig_plug_in\maya_plug\data\studio_library' not in sys.path:
    sys.path.insert(0, r'Z:\Library\rig_plug_in\maya_plug\data\studio_library')

import studiolibrary

studiolibrary.main()
