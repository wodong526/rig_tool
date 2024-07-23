# AdvancedSkeleton To ModularRig
#	Copyright (C) Animation Studios
# email: support@animationstudios.com.au
# exported using AdvancedSkeleton version:x.xx
import unreal
import re

engineVersion = unreal.SystemLibrary.get_engine_version()
asExportVersion = 'x.xx'
asExportTemplate = '4x'
print ('AdvancedSkeleton To ModularControlRig (Unreal:'+engineVersion+') (AsExport:'+str(asExportVersion)+') (Template:'+asExportTemplate+')')
utilityBase = unreal.GlobalEditorUtilityBase.get_default_object()
selectedAssets = utilityBase.get_selected_assets()
if len(selectedAssets)<1:
	raise Exception('Nothing selected, you must select a ControlRig')
selectedAsset = selectedAssets[0]
if selectedAsset.get_class().get_name() != 'ControlRigBlueprint':
	raise Exception('Selected object is not a ControlRigBlueprint, you must select a ControlRigBlueprint')
blueprint = selectedAsset
RigGraphDisplaySettings = blueprint.get_editor_property('rig_graph_display_settings')
RigGraphDisplaySettings.set_editor_property('node_run_limit',256)
library = blueprint.get_local_function_library()
library_controller = blueprint.get_controller(library)
hierarchy = blueprint.hierarchy
hierarchy_controller = hierarchy.get_controller()
ModularRigController = blueprint.get_modular_rig_controller()

def asObjExists (obj):
	RigElementKeys = hierarchy.get_all_keys()
	LocObject = None
	for key in RigElementKeys:
		if key.name == obj:
			return True
	return False

def asGetKeyFromName (name):
	all_keys = hierarchy.get_all_keys(traverse = True)
	for key in all_keys:
		if key.name == name:
			return key
	return ''

def asConnect (target_key_name, connector_key_name):
	connector_key = asGetKeyFromName (connector_key_name)
	target_key = asGetKeyFromName (target_key_name)
	ModularRigController.connect_connector_to_element (connector_key, target_key)

def main ():
	RigElementKeys = hierarchy.get_all_keys()

	target_key = asGetKeyFromName ('spine_01_socket')
	if not (target_key):

		#remove old sockets
		for key in RigElementKeys:
			x = re.search("_socket", str(key.name))
			if x:
				hierarchy_controller.remove_element(key)

		hierarchy_controller.add_socket('spine_01_socket', unreal.RigElementKey(type=unreal.RigElementType.BONE, name='spine_01'), unreal.Transform(location=[0.000000,0.000000,0.000000],rotation=[-0.000000,0.000000,-0.000000],scale=[1.000000,1.000000,1.000000]), False, unreal.LinearColor(1.000000, 1.000000, 1.000000, 1.000000), '')
		hierarchy_controller.add_socket('neck_socket', unreal.RigElementKey(type=unreal.RigElementType.BONE, name='neck'), unreal.Transform(location=[0.000000,0.000000,0.000000],rotation=[-0.000000,0.000000,-0.000000],scale=[1.000000,1.000000,1.000000]), False, unreal.LinearColor(1.000000, 1.000000, 1.000000, 1.000000), '')
		for side in ['_r','_l']:
			hierarchy_controller.add_socket('shoulder'+side+'_socket', unreal.RigElementKey(type=unreal.RigElementType.BONE, name='upperArm'+side), unreal.Transform(location=[0.000000,0.000000,0.000000],rotation=[-0.000000,0.000000,-0.000000],scale=[1.000000,1.000000,1.000000]), False, unreal.LinearColor(1.000000, 1.000000, 1.000000, 1.000000), '')
			hierarchy_controller.add_socket('hand'+side+'_socket', unreal.RigElementKey(type=unreal.RigElementType.BONE, name='hand'+side), unreal.Transform(location=[0.000000,0.000000,0.000000],rotation=[-0.000000,0.000000,-0.000000],scale=[1.000000,1.000000,1.000000]), False, unreal.LinearColor(1.000000, 1.000000, 1.000000, 1.000000), '')


		module_class = unreal.load_class(None, '/ControlRigModules/Modules/Spine.Spine_C')
		ModularRigController.add_module (module_name='Spine', class_= module_class , parent_module_path='Root')
		module_class = unreal.load_class(None, '/ControlRigModules/Modules/Neck.Neck_C')
		ModularRigController.add_module (module_name='Neck', class_= module_class , parent_module_path='Root:Spine')

		for side in ['_r','_l']:
			module_class = unreal.load_class(None, '/ControlRigModules/Modules/Shoulder.Shoulder_C')
			ModularRigController.add_module (module_name='Shoulder'+side, class_= module_class , parent_module_path='Root:Spine')
			module_class = unreal.load_class(None, '/ControlRigModules/Modules/Arm.Arm_C')
			ModularRigController.add_module (module_name='Arm'+side, class_= module_class , parent_module_path='Root:Spine:Shoulder'+side)
			module_class = unreal.load_class(None, '/ControlRigModules/Modules/Leg.Leg_C')
			ModularRigController.add_module (module_name='Leg'+side, class_= module_class , parent_module_path='Root')

			for finger in ['index','middle','ring','pinky','thumb']:
				module_class = unreal.load_class(None, '/ControlRigModules/Modules/Finger.Finger_C')
				ModularRigController.add_module (module_name='Finger'+finger+side, class_= module_class , parent_module_path='Root:Spine:Shoulder'+side+':Arm'+side)


		print ('First run Complete, Now open the ControlRig, then run the python-script again.')
		return


	asConnect ('root' , 'Root:Root')
	asConnect ('spine_01_socket' , 'Root:Spine:Spine Primary')
	asConnect ('spine_05' , 'Root:Spine:Spine End Bone')
	asConnect ('neck_socket' , 'Root:Spine:Neck:Neck Primary')
	asConnect ('neck_01' , 'Root:Spine:Neck:Neck Start Bone')
	asConnect ('head' , 'Root:Spine:Neck:Head Bone')

	for side in ['_r','_l']:
		asConnect ('shoulder'+side+'_socket' , 'Root:Spine:Shoulder'+side+':Shoulder Primary')
		asConnect ('spine_05' , 'Root:Spine:Shoulder'+side+':Chest Bone')
		asConnect ('hand'+side+'_socket' , 'Root:Spine:Shoulder'+side+':Arm'+side+':Arm Primary')
		asConnect ('spine_01_socket' , 'Root:Leg'+side+':Leg Primary')
		asConnect ('thigh'+side , 'Root:Leg'+side+':Thigh Bone')
		asConnect ('foot'+side , 'Root:Leg'+side+':Foot Bone')

		for finger in ['index','middle','ring','pinky','thumb']:
			asConnect ('hand'+side+'_socket' , 'Root:Spine:Shoulder'+side+':Arm'+side+':Finger'+finger+side+':Finger Primary')
			if finger == 'thumb':
				asConnect (finger+'_01'+side , 'Root:Spine:Shoulder'+side+':Arm'+side+':Finger'+finger+side+':Start Bone')
			else:
				asConnect (finger+'_metacarpal'+side , 'Root:Spine:Shoulder'+side+':Arm'+side+':Finger'+finger+side+':Start Bone')
			asConnect (finger+'_03'+side , 'Root:Spine:Shoulder'+side+':Arm'+side+':Finger'+finger+side+':End Bone')


	print ('Second run complete.')

if __name__ == "__main__":
    main()