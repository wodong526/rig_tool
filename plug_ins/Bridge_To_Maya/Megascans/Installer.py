"""
This Module:
- Adds the plugin to Maya (Creates a shelf and deletes the old shelf)

"""
import maya.cmds as cmds
import maya.mel as mel
import os

import sys
sys.path.append("..") # Adds higher directory to python modules path.

# Creates Maya Shelf - Add LiveLink button on the shelf
def createMSshelf():
    path_ = os.path.dirname(__file__).replace("\\", "/")

    shelfName_ = "MSPlugin"
    imgPath = os.path.join( path_, "MS_Logo.png" ).replace("\\", "/")
    cmd_ = ("""import sys
path_ = 'PATH'
if path_ not in sys.path:
    sys.path.append( path_ )
import LiveLink as msAPI
msAPI.initLiveLink()
            """).replace("PATH", os.path.dirname(path_).replace("\\", "/") )
    
    shelftoplevel = mel.eval("$gShelfTopLevel = $gShelfTopLevel;")
    shelfList_ = cmds.tabLayout(shelftoplevel, query=True, childArray=True)

    try:
        DeleteMayaOldShelf()
    except:
        pass

    if shelftoplevel != None:
        if shelfName_ in shelfList_:
            try:
                for element in cmds.shelfLayout(shelfName_, q=1, ca=1):
                    cmds.deleteUI(element)
            except:
                pass
        else:
            mel.eval("addNewShelfTab " + shelfName_ + ";")
            
        cmds.shelfButton( label="MS", command=cmd_, parent=shelfName_, image=imgPath)
        cmds.saveAllShelves(shelftoplevel)

# Delete Old Maya Shelf  - Remove LiveLink from shelf
def DeleteMayaOldShelf(shelfName = "MSLiveLink"):
    try:
        shelfExists = cmds.shelfLayout(shelfName, ex=True)
        if shelfExists:
            mel.eval('deleteShelfTab %s' % shelfName)
            gShelfTopLevel = mel.eval('$tmpVar=$gShelfTopLevel')
            cmds.saveAllShelves(gShelfTopLevel)
        else:
            return
    except:
        pass
