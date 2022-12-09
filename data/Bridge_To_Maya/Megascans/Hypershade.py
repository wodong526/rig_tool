"""
This Module:
- Rearranges the hypershader material setups to give a cleaner look
"""
import os
import maya.cmds as mc
import maya.mel as melc

####### Currently not used because it isn't making any drastic changes on Maya 2020 ########

# Reorganize the hypershade to clean the node layout. You can avoid using the method if you don't want the plugin to change the position of your nodes.
def RearrangeHyperShade():
    try:
        melc.eval('HypershadeWindow;')
        melc.eval('hyperShadePanelGraphCommand("hyperShadePanel1", "rearrangeGraph");')
    except:
        pass
    
# This should close hypershade - This is not closing the hypershade window right now.
def CloseHyperShader():
    try:
        melc.eval('deleteUI hyperShadePanel1Window;')
    except:
        pass