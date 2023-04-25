'''
This module contains additional adapters which define how some objects 
have to be additionally adapted for later use.

Adapter objects can be connected into chains. If so, object is being adapted by
first adapter in chain. Once first adapter finish adapting, it calls next
adapter in chain to do its adapting, and so on.
'''

import pymel.core as pycore


class AdditionalAdapter:
    '''
    Base AdditionalAdapter class. 
    
    All adapters have to inherent this class and redefine method adapt().
    Attributes:
        nextAdapter (AdditionalAdapter): Next adapter in adapting chain.
    '''

    def __init__(self):
        self.nextAdapter = None

    def adapt(self, object):
        '''
        Changes given data in a way to adapt it for later use depending on context.
        
        This method has to be overridden.        
        When method finish with adapting objects, it calls next adapter in chain.
        @param object: Object which has to be adapted.
        '''

        if self.nextAdapter:
            self.nextAdapter.adapt(object)


# ----------------------------
# Joint additional adapters
# ----------------------------
class MayaJointsDataScaleAA(AdditionalAdapter):
    '''
    Maya joint data additional adapter.
    
    This adapter changes joints scale.
    @see trilateral.api.maya.MayaJoint
    @see trilateral.api.maya.MayaJointDataHolder
    '''

    def __init__(self, scale, pivot):
        AdditionalAdapter.__init__(self)
        self._scale = scale
        self._pivot = pivot

    def adapt(self, object):
        '''
        Adapt Maya joints scale based on scale coefficient and pivot.
        
        @param object: Maya joints object. (trilateral.api.maya.MayaJointDataHolder)
        '''

        # adapt
        if self._scale != 1.0:
            object.scale(self._scale, self._pivot)

        # call next in chain
        if self.nextAdapter:
            self.nextAdapter.adapt(object)


class MayaJointsDataOrientAA(AdditionalAdapter):
    '''
    Maya joint data additional adapter.
    
    This adapter changes joints orient.
    @see trilateral.api.maya.MayaJoint
    @see trilateral.api.maya.MayaJointDataHolder
    '''

    def __init__(self, orient, translate):
        AdditionalAdapter.__init__(self)
        self._orient = orient
        self._translate = translate

    def adapt(self, joints):
        '''
        Adapt Maya joints orientation based on given orient.
        
        @param object: Maya joints object. (trilateral.api.maya.MayaJointDataHolder)
        '''

        # adapt
        for mayaJoint in joints:
            # create joints
            pycore.select(clear=True)
            jointNode = pycore.joint(name="temp_root_jnt")
            jointNode.jointOrient.set(mayaJoint.jointOrient.get())
            jointNode.translate.set(mayaJoint.translate.get())
            jointNode.rotate.set(mayaJoint.rotate.get())
            jointNode.scale.set(mayaJoint.scale.get())

            # rotate
            locator = pycore.spaceLocator()
            jointNode.setParent(locator)
            if self._orient[0] != 0.0 or self._orient[1] != 0.0 or self._orient[2] != 0.0:
                locator.rotate.set(self._orient)

            if self._translate[0] != 0.0 or self._translate[1] != 0.0 or self._translate[2] != 0.0:
                locator.translate.set(self._translate)

            jointNode.setParent(None)
            pycore.delete(locator)

            # save changes
            mayaJoint.translate.set(jointNode.translate.get())
            mayaJoint.rotate.set(jointNode.rotate.get())
            mayaJoint.scale.set(jointNode.scale.get())
            mayaJoint.jointOrient.set(jointNode.jointOrient.get())
            pycore.delete(jointNode)

        # call next in chain
        if self.nextAdapter:
            self.nextAdapter.adapt(object)


# ----------------------------
# Mesh additional adapters
# ----------------------------
class MeshScaleAA(AdditionalAdapter):
    '''
    Mesh additional adapter.
    
    This adapter changes mesh scale.
    '''

    def __init__(self, scale, pivot):
        AdditionalAdapter.__init__(self)
        self._scale = scale
        self._pivot = pivot

    def adapt(self, object):
        '''
        Adapt Mesh scale based on scale coefficient and pivot.
        
        This method leave clean channels (translations and rotations at 0.0, 
        scale at 1.0).
        @param object: Maya mesh node. (Mesh)
        '''

        # adapt
        locator = pycore.spaceLocator()
        locator.translate.set(self._pivot)
        object.setParent(locator)
        locator.scale.set([self._scale, self._scale, self._scale])
        object.setParent(None)
        pycore.delete(locator)
        pycore.makeIdentity(object, apply=True, t=True, r=True, s=True, n=True)
        pycore.polyNormalPerVertex(object, unFreezeNormal=True)

        # call next in chain
        if self.nextAdapter:
            self.nextAdapter.adapt(object)


class MeshOrientAA(AdditionalAdapter):
    '''
    Mesh additional adapter.
    
    This adapter changes mesh orientation.
    '''

    def __init__(self, orient, translate):
        AdditionalAdapter.__init__(self)
        self._orient = orient
        self._translate = translate

    def adapt(self, object):
        '''
        Adapt Mesh orientation based on given orient.
        
        This method leave clean channels (translations and rotations at 0.0, 
        scale at 1.0).      
        @param object: Maya mesh node. (Mesh)
        '''

        # adapt
        if self._orient[0] != 0.0 or self._orient[1] != 0.0 or self._orient[2] != 0.0:
            object.rotate.set(self._orient)

        if self._translate[0] != 0.0 or self._translate[1] != 0.0 or self._translate[2] != 0.0:
            object.translate.set(self._translate)

        pycore.makeIdentity(object, apply=True, t=True, r=True, s=True, n=True)
        pycore.polyNormalPerVertex(object, unFreezeNormal=True)

        # call next in chain
        if self.nextAdapter:
            self.nextAdapter.adapt(object)


# ----------------------------
# GUI additional adapters
# ----------------------------
class GuiScaleAA(AdditionalAdapter):
    '''
    Gui additional adapter.
    
    This adapter changes scale.
    '''

    def __init__(self, scale, pivot):
        AdditionalAdapter.__init__(self)
        self._scale = scale
        self._pivot = pivot

    def adapt(self, object):
        '''
        Adapt 2D gui scale based on scale coefficient and pivot.
        
        This method does not leave clean channels (translations and rotations
        can be different than 0.0, and scale different than 1.0).
        
        @param object: List of root gui Maya nodes. (DagNode[])
        
        Algorithm:
        1. Creates helper locator.
        2. Parent all root nodes under helper locator.
        3. Moves and scales helper locator.
        4. Unparent all root nodes. 
        5. Delete helper locator.
        '''

        # adapt
        for rootNode in object:
            locator = pycore.spaceLocator()
            locator.translate.set(self._pivot)
            parent = rootNode.getParent()
            rootNode.setParent(locator)
            locator.scale.set([self._scale, self._scale, self._scale])
            rootNode.setParent(parent)
            pycore.delete(locator)

        # call next in chain
        if self.nextAdapter:
            self.nextAdapter.adapt(object)


class GuiOrientAA(AdditionalAdapter):
    '''
    Gui additional adapter.
    
    This adapter changes 2D GUI orientation.
    '''

    def __init__(self, orient):
        AdditionalAdapter.__init__(self)
        self._orient = orient

    def adapt(self, object):
        '''
        Adapt 2D gui orientation based on given orient.
        
        This method does not leave clean channels (translations and rotations
        can be different than 0.0, and scale different than 1.0).        
        
        @param object: List of root gui Maya nodes. (DagNode[])
                
        Algorithm:
        1. Creates helper locator.
        2. Parent all root nodes under helper locator.
        3. Rotates helper locator.
        4. Unparent all root nodes. 
        5. Delete helper locator.
        '''

        # adapt
        for rootNode in object:
            locator = pycore.spaceLocator()
            parent = rootNode.getParent()
            rootNode.setParent(locator)
            locator.rotate.set(self._orient)
            rootNode.setParent(parent)
            pycore.delete(locator)

        # call next in chain
        if self.nextAdapter:
            self.nextAdapter.adapt(object)


# ----------------------------
# Controls additional adapters
# ----------------------------
class ControlsScaleAA(AdditionalAdapter):
    '''
    Analog controls additional adapter.
    
    This adapter changes scale.
    '''

    def __init__(self, scale, pivot):
        AdditionalAdapter.__init__(self)
        self._scale = scale
        self._pivot = pivot

    def adapt(self, object):
        '''
        Adapt analog controls (or controls in general) scale based on scale
        coefficient and pivot.
        This method leave clean channels (translations and rotations at 0.0, 
        scale at 1.0).      
        
        @param object: List of root analog control Maya nodes. (DagNode[])
        
        Algorithm:
        1. Make list of all nodes sorted from parent to children.
        2. Scale all objects:
           - take each root node,
           - create locator, move locator to pivot position, parent root node
             under it,
           - scale locator for scale coefficient,
           - unparent root node,
           - delete locator.
        3. Unlock channels: 
           - for all nodes, save data which channels (translate, rotate, scale)
             are locked,
           - for all nodes unlock all channels,
        4. Clean controls channels. For each node:
           - disconnect node from parent and children,
           - save node translate and rotate data,
           - move node to 0, 0, 0,
           - freeze transformations,
           - return node to its previous position using saved translate 
             and rotate data,
           - connect node with its previous parent and children.
        5. Lock channels which were locked using saved data.
        '''

        # adapt
        # get all nodes and scale them all
        nodes = []
        for rootNode in object:
            nodes.extend(pycore.listRelatives(rootNode, allDescendents=True, type="transform"))
            locator = pycore.spaceLocator()
            locator.translate.set(self._pivot)
            parent = rootNode.getParent()
            rootNode.setParent(locator)
            locator.scale.set([self._scale, self._scale, self._scale])
            rootNode.setParent(parent)
            pycore.delete(locator)
        nodes.extend(object)
        nodes.reverse()

        # unlock translate, rotate, scale on all nodes
        lockedDict = {}
        for node in nodes:
            locks = [node.translateX.isLocked(), node.translateY.isLocked(), node.translateZ.isLocked(),
                     node.rotateX.isLocked(), node.rotateY.isLocked(), node.rotateZ.isLocked(),
                     node.scaleX.isLocked(), node.scaleY.isLocked(), node.scaleZ.isLocked()]
            lockedDict[node.longName()] = locks
            node.translateX.setLocked(False)
            node.translateY.setLocked(False)
            node.translateZ.setLocked(False)
            node.rotateX.setLocked(False)
            node.rotateY.setLocked(False)
            node.rotateZ.setLocked(False)
            node.scaleX.setLocked(False)
            node.scaleY.setLocked(False)
            node.scaleZ.setLocked(False)

        # clean transformations
        for node in nodes:
            # save data
            parent = node.getParent()
            children = node.getChildren(type="transform")
            if parent:
                node.setParent(None)
            for child in children:
                child.setParent(None)
            translateValues = node.translate.get()
            rotateValues = node.rotate.get()

            # freeze
            node.translate.set([0, 0, 0])
            pycore.makeIdentity(node, apply=True, t=True, r=True, s=True, n=True)
            if node.hasAttr("localScale"):
                node.localScale.set([self._scale, self._scale, self._scale])

            # parent and return previous state
            node.translate.set(translateValues)
            node.rotate.set(rotateValues)
            if parent:
                node.setParent(parent)
            for child in children:
                child.setParent(node)

        # lock translate, rotate, scale on all nodes
        for node in nodes:
            locks = lockedDict[node.longName()]
            node.translateX.setLocked(locks[0])
            node.translateY.setLocked(locks[1])
            node.translateZ.setLocked(locks[2])
            node.rotateX.setLocked(locks[3])
            node.rotateY.setLocked(locks[4])
            node.rotateZ.setLocked(locks[5])
            node.scaleX.setLocked(locks[6])
            node.scaleY.setLocked(locks[7])
            node.scaleZ.setLocked(locks[8])

        # call next in chain
        if self.nextAdapter:
            self.nextAdapter.adapt(object)


class ControlsOrientAA(AdditionalAdapter):
    '''
    Gui additional adapter.
    
    This adapter changes controls orientation.
    '''

    def __init__(self, orient):
        AdditionalAdapter.__init__(self)
        self._orient = orient

    def adapt(self, object):
        '''
        Adapt analog controls (or controls in general) orientation based on
        given orient.
        
        This method does not leave clean channels (translations and rotations
        can be different than 0.0, and scale different than 1.0).        
        
        @param object: List of root analog control Maya nodes. (DagNode[])
                        
        Algorithm:
        1. Creates helper locator.
        2. Parent all root nodes under helper locator.
        3. Rotates helper locator.
        4. Unparent all root nodes. 
        5. Delete helper locator.
        '''

        # adapt
        for rootNode in object:
            locator = pycore.spaceLocator()
            parent = rootNode.getParent()
            rootNode.setParent(locator)
            locator.rotate.set(self._orient)
            rootNode.setParent(parent)
            pycore.delete(locator)

        # call next in chain
        if self.nextAdapter:
            self.nextAdapter.adapt(object)


# ----------------------------
# Addition adapter builders
# ----------------------------
class AdditionalAdapterBuilder:
    '''
    This class contains static methods for building addition adapter chains 
    depending on its usage.
    
    @see AdditionalAdapter
    '''

    @staticmethod
    def buildMayaJointsDataAA(scale, pivot, orient, translate):
        '''
        Builds additional adapters chain for Maya joint data adaptation.
        
        @param scale: Scale factor (float)
        @param pivor: Scale pivot position. ([float, float, float])
        @param orient: Orientation rotations. ([float, float, float])
        '''

        firstAA = None
        lastAA = None
        if scale != 1.0:
            aa = MayaJointsDataScaleAA(scale, pivot)
            firstAA = aa
            lastAA = aa
        if orient[0] != 0.0 or orient[1] != 0.0 or orient[2] != 0.0 or translate[0] != 0.0 or translate[1] != 0.0 or translate[2] != 0.0:
            aa = MayaJointsDataOrientAA(orient, translate)
            if lastAA:
                lastAA.nextAdapter = aa
            else:
                firstAA = aa
            lastAA = aa
        return firstAA

    @staticmethod
    def buildMeshAA(scale, pivot, orient, translate):
        '''
        Builds additional adapters chain for mesh adaptation.
        
        @param scale: Scale factor (float)
        @param pivor: Scale pivot position. ([float, float, float])
        @param orient: Orientation rotations. ([float, float, float])
        @param orient: Translate position. ([float, float, float])
        '''

        firstAA = None
        lastAA = None
        if scale != 1.0:
            aa = MeshScaleAA(scale, pivot)
            firstAA = aa
            lastAA = aa
        if orient[0] != 0.0 or orient[1] != 0.0 or orient[2] != 0.0 or translate[0] != 0.0 or translate[1] != 0.0 or translate[2] != 0.0:
            aa = MeshOrientAA(orient, translate)
            if lastAA:
                lastAA.nextAdapter = aa
            else:
                firstAA = aa
            lastAA = aa
        return firstAA

    @staticmethod
    def buildGuiAA(scale, pivot, orient):
        '''
        Builds additional adapters chain for 2D GUI adaptation.
        
        @param scale: Scale factor (float)
        @param pivor: Scale pivot position. ([float, float, float])
        @param orient: Orientation rotations. ([float, float, float])
        '''

        firstAA = None
        lastAA = None
        if scale != 1.0:
            aa = GuiScaleAA(scale, pivot)
            firstAA = aa
            lastAA = aa
        if orient[0] != 0.0 or orient[1] != 0.0 or orient[2] != 0.0:
            aa = GuiOrientAA(orient)
            if lastAA:
                lastAA.nextAdapter = aa
            else:
                firstAA = aa
            lastAA = aa
        return firstAA

    @staticmethod
    def buildControlsAA(scale, pivot, orient):
        '''
        Builds additional adapters chain for controls adaptation.
        
        @param scale: Scale factor (float)
        @param pivor: Scale pivot position. ([float, float, float])
        @param orient: Orientation rotations. ([float, float, float])
        '''

        firstAA = None
        lastAA = None
        if scale != 1.0:
            aa = ControlsScaleAA(scale, pivot)
            firstAA = aa
            lastAA = aa
        if orient[0] != 0.0 or orient[1] != 0.0 or orient[2] != 0.0:
            aa = ControlsOrientAA(orient)
            if lastAA:
                lastAA.nextAdapter = aa
            else:
                firstAA = aa
            lastAA = aa
        return firstAA
