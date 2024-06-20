"""
Maya checks for userSetup.py file and runs it while loading other libraries at the start of the program
This Module :
- Creates the shelf in Maya
- Starts the LiveLink
"""

#import pymel.core as pm
from LiveLink import initLiveLink
from Megascans import Installer
from DHI import DHIPluginLoader

# Runs this code automatically at the start of Maya
#pm.evalDeferred("initPlugin()")


# Delete Old Shelf, create a new shelf (install livelink) and start the listening at socket/start LiveLink
def initPlugin():
    try:
        DHIPluginLoader.load()
    finally:   
        #Installer.createMSshelf()
        initLiveLink()
