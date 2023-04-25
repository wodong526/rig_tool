from DHI.modules.dna.model.gui import AnalogGuiOptions
from DHI.modules.dna.scene.builder.rlNodeBuilder import RigLogicNodeBuilder
from DHI.modules.dna.scene.builder.sceneBuilder import SceneBuilder

import pymel.core as pycore


class AssembleUtil(object):

    @staticmethod
    def assembleSceneFromDNA(fullDnaPath, nodeName="defaultNN", additionalScriptPath=None, additionalScriptMethod=None, addNode=False, guiPath=None, acPath=None, isMale=False):
        sceneBuilder = SceneBuilder()
        sceneBuilder. \
        FromDnaPath(fullDnaPath).\
        And(). \
        WithLinearUnit("cm"). \
        And(). \
        WithAngleUnit("degree")

        if additionalScriptPath:
            sceneBuilder.WithAAS(additionalScriptPath, additionalScriptMethod)

        if addNode:
            rl4nb = RigLogicNodeBuilder()
            rl4nb.setName(nodeName)
            rl4nb.setFlag("-dfp", fullDnaPath)
            sceneBuilder.WithRigLogicNodeBuilder(rl4nb)

        if guiPath:
            sceneBuilder.WithGui(guiPath). \
            And(). \
            WithFRMAttrs("FRM_WMmultipliers")

        if acPath:
            acOptions = AnalogGuiOptions.defaultOptions()
            acOptions.GuiPath = acPath
            sceneBuilder.WithAnalogGuiOptions(acOptions)

        sceneBuilder.build()

        # To be removed when GUI builder is implemented
        if guiPath and isMale:
            pycore.xform("CTRL_faceGUI", translation=[2.0, 10.0, 0.0], relative=True)
