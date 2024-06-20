import sys
import maya.api.OpenMaya as OpenMaya
# ... additional imports here ...
def maya_useNewAPI():
 """
 The presence of this function tells Maya that the plugin produces, and
 expects to be passed, objects created using the Maya Python API 2.0.
 """
 pass
# Plug-in information:
kPluginNodeName = 'myNodeName' # The name of the node.
kPluginNodeClassify = 'utility/general' # Where this node will be found in the Maya UI.
kPluginNodeId = OpenMaya.MTypeId( 0x87EFE ) # A unique ID associated to this node type.
# Default attribute values
sampleDefaultValue = 1
##########################################################
# Plug-in
##########################################################
class myNode(OpenMaya.MPxNode):
 # Static variables which will later be replaced by the node's attributes.
 sampleInAttribute = OpenMaya.MObject()
 sampleOutAttribute = OpenMaya.MObject()
 def __init__(self):
  ''' Constructor. '''
  OpenMaya.MPxNode.__init__(self)
 def compute(self, pPlug, pDataBlock):
  '''
  Node computation method.
  - pPlug: A connection point related to one of our node attributes (could be an input or an output)
  - pDataBlock: Contains the data on which we will base our computations.
  '''
  if( pPlug == myNode.sampleOutAttribute ):
   # Obtain the data handles for each attribute
   sampleInDataHandle = pDataBlock.inputValue( myNode.sampleInAttribute )
   sampleOutDataHandle = pDataBlock.outputValue( myNode.sampleOutAttribute )

   sampleInValue = sampleInDataHandle.asFloat()
   # Mark the output data handle as being clean; it need not be computed given its input.
   sampleOutDataHandle.setClean()
  else:
   return OpenMaya.kUnknownParameter
##########################################################
# Plug-in initialization.
##########################################################
def nodeCreator():
 ''' Creates an instance of our node class and delivers it to Maya as a pointer. '''
 return myNode()
def nodeInitializer():
 ''' Defines the input and output attributes as static variables in our plug-in class. '''
 # The following MFnNumericAttribute function set will allow us to create our attributes.
 numericAttributeFn = OpenMaya.MFnNumericAttribute()
 #==================================
 # INPUT NODE ATTRIBUTE(S)
 #==================================
 global sampleDefaultValue
 myNode.sampleInAttribute = numericAttributeFn.create( 'myInputAttribute', 'i',
 OpenMaya.MFnNumericData.kFloat,
sampleDefaultValue )
 numericAttributeFn.writable = True
 numericAttributeFn.storable = True
 numericAttributeFn.hidden = False
 myNode.addAttribute( myNode.sampleInAttribute ) # Calls the MPxNode.addAttribute function.
 #==================================
 # OUTPUT NODE ATTRIBUTE(S)
 #==================================
 myNode.sampleOutAttribute = numericAttributeFn.create( 'myOutputAttribute', 'o',
 OpenMaya.MFnNumericData.kFloat )
 numericAttributeFn.storable = False
 numericAttributeFn.writable = False
 numericAttributeFn.readable = True
 numericAttributeFn.hidden = False
 myNode.addAttribute( myNode.sampleOutAttribute )
 #==================================
 # NODE ATTRIBUTE DEPENDENCIES
 #==================================
 # If sampleInAttribute changes, the sampleOutAttribute data must be recomputed.
 myNode.attributeAffects( myNode.sampleInAttribute, myNode.sampleOutAttribute )
def initializePlugin( mobject ):
 ''' Initialize the plug-in '''
 mplugin = OpenMaya.MFnPlugin( mobject )
 try:
  mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator,
  nodeInitializer, OpenMaya.MPxNode.kDependNode, kPluginNodeClassify )
 except:
  sys.stderr.write( 'Failed to register node: ' + kPluginNodeName )
 raise
def uninitializePlugin( mobject ):
 ''' Uninitializes the plug-in '''
 mplugin = OpenMaya.MFnPlugin( mobject )
 try:
  mplugin.deregisterNode( kPluginNodeId )
 except:
  sys.stderr.write( 'Failed to deregister node: ' + kPluginNodeName )