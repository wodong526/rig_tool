import json
import os
import re
import shutil
import tempfile
import time
import webbrowser

import maya.cmds as cmds
import xgenm as xg

material_attributes = {
    'aiStandardSurface': {
        'TEX_DIFFWEIGHT': 'base',
        'TEX_DIFF': 'baseColor',
        'TEX_METAL': 'metalness',
        'TEX_SPECWEIGHT': 'specular',
        'TEX_SPEC': 'specularColor',
        'TEX_ROUGH': 'specularRoughness',
        'TEX_ANITROP': 'specularAnisotropy',
        'TEX_ANITROPROT': 'specularRotation',
        'TEX_TRANSWEIGHT': 'transmission',
        'TEX_TRANS': 'transmissionColor',
        'TEX_IOR': 'specularIOR',
        'TEX_SSSWEIGHT': 'subsurface',
        'TEX_SSS': 'subsurfaceColor',
        'TEX_SSSRAD': 'subsurfaceRadius',
        'TEX_COATWEIGHT': 'coat',
        'TEX_COAT': 'coatColor',
        'TEX_EMISSIONWEIGHT': 'emission',
        'TEX_EMISSION': 'emissionColor',
        'TEX_OPAC': 'opacity',
        'TEX_BUMP': 'normalCamera',
    },
    'aiFlat': {'TEX_EMISSION': 'color'},
}

accepting_textures = [
    'TEX_DIFF',
    'TEX_METAL',
    'TEX_SPEC',
    'TEX_ROUGH',
    'TEX_TRANS',
    'TEX_SSS',
    'TEX_COAT',
    'TEX_EMISSION',
    'TEX_OPAC',
    'TEX_BUMP',
]

# ----------------------------------------------------------------------------------------------


def export_meshes(export_dir):

    print('\n>>> Exporting meshes...\n')

    selection = cmds.ls(sl=True)
    rig_selection = ''
    blendshapes_selection = []

    all_shapes = cmds.listRelatives(selection, ad=True, noIntermediate=True, type='shape')

    for shape in all_shapes:

        # Get skin cluster
        skin_cluster = cmds.listConnections(shape, type='skinCluster')

        if skin_cluster is not None:

            joints = cmds.listConnections(skin_cluster[0], type='joint')

            if joints is not None:

                # Find root joints
                root_joint = joints[0]

                while True:

                    parent = cmds.listRelatives(root_joint, parent=True, type='joint')

                    if not parent:

                        break

                    root_joint = parent[0]

                rig_selection = root_joint

                break

    all_blendshapes = cmds.listConnections('shapeEditorManager', type='blendShape')

    if all_blendshapes is not None:

        for blendshape in all_blendshapes:

            bs_geometries = cmds.listConnections(blendshape + '.inputTarget')

            if bs_geometries:

                for bs_geo in bs_geometries:

                    blendshapes_selection.append(bs_geo)

    cmds.select(selection)
    if rig_selection:
        cmds.select(rig_selection, add=True)
    else:
        cmds.warning('>>> No rig found. Make sure it\'s attached to the mesh.')

    if blendshapes_selection:
        cmds.select(blendshapes_selection, add=True)
    else:
        cmds.warning('>>> No blendshapes found.')

    export_path = os.path.join(export_dir, 'character.fbx').replace('\\', '/')

    cmds.loadPlugin('fbxmaya')

    mel.eval('FBXResetExport')
    mel.eval('FBXExportFileVersion -v FBX202000')
    mel.eval('FBXExportInAscii -v false')
    mel.eval('FBXExport -f "{}" -s'.format(export_path))

    print('\n>>> All meshes exported.')


# ----------------------------------------------------------------------------------------------


def extract_faces(faces):

    geo = faces.split('.')[0]
    face_number = faces.split('.')[-1]

    duplicate_geo = cmds.duplicate(geo)[0]
    duplicate_geo_faces = '{geo}.{face}'.format(geo=duplicate_geo, face=face_number)

    # Invert selection
    cmds.select(duplicate_geo_faces)
    cmds.select(duplicate_geo + '.f[0:]', tgl=True)

    cmds.delete()

    return duplicate_geo


# ----------------------------------------------------------------------------------------------


def group_meshes_by_material(objects, shadingGroup):

    bake_object = []

    for obj in objects:

        if '.f[' in obj:

            extracted_faces = extract_faces(obj)
            bake_object.append(extracted_faces)

        else:

            duplicate_geo = cmds.duplicate(obj)[0]
            bake_object.append(duplicate_geo)

    bake_object_name = shadingGroup + '_bake'
    cmds.polyUnite(bake_object, n=bake_object_name)
    cmds.delete(bake_object_name, constructionHistory=True)

    return bake_object_name


# ----------------------------------------------------------------------------------------------


def bake(shading_group, bake_node, resolution=1024):

    # Create temp bake directory
    temp_directory = tempfile.gettempdir()
    root_dir_name = 'wonder_temp'

    t = time.localtime()
    current_time = time.strftime('%Y%m%d-%H%M%S', t)

    sub_dir = '{sg}-{time}'.format(sg=shading_group, time=current_time)

    sub_dir = os.path.join(root_dir_name, sub_dir).replace('\\', '/')
    bake_dir = os.path.join(temp_directory, sub_dir).replace('\\', '/')

    os.makedirs(bake_dir)

    material = cmds.listConnections('%s.surfaceShader' % shading_group)[0]

    # Create bake mesh
    objects = cmds.sets(shading_group, q=True)

    if len(objects) != 1:

        mesh = group_meshes_by_material(objects, shading_group)

    else:

        mesh = cmds.duplicate(objects[0])

    bake_material = cmds.shadingNode('aiFlat', asShader=True)

    # Connect bake node to bake material
    if cmds.getAttr(bake_node, type=True) == 'float':

        cmds.connectAttr(bake_node, bake_material + '.color.colorR', force=True)
        cmds.connectAttr(bake_node, bake_material + '.color.colorG', force=True)
        cmds.connectAttr(bake_node, bake_material + '.color.colorB', force=True)

    else:

        cmds.connectAttr(bake_node, bake_material + '.color', force=True)

    # Connect bake material to shading engine
    cmds.connectAttr(bake_material + '.outColor', shading_group + '.surfaceShader', force=True)

    # BAKE MATERIAL
    cmds.select(mesh)
    cmds.arnoldRenderToTexture(folder=bake_dir, shader=bake_material, resolution=resolution, all_udims=True)

    # Reconnect the original material to shading engine
    cmds.connectAttr(material + '.outColor', shading_group + '.surfaceShader', force=True)
    # Remove bake material and mesh
    cmds.delete(bake_material)
    cmds.delete(mesh)

    baked_texture = os.path.join(bake_dir, os.listdir(bake_dir)[0]).replace('\\', '/')

    return baked_texture


# ----------------------------------------------------------------------------------------------


def get_file_path(shader_node, shading_group):

    node_type = cmds.nodeType(shader_node)

    if node_type == 'file':

        node = '.'.join(shader_node.split('.')[0:-1])
        texture_path = cmds.getAttr('%s.fileTextureName' % node)

    elif node_type == 'aiImage':

        node = '.'.join(shader_node.split('.')[0:-1])
        texture_path = cmds.getAttr('%s.filename' % node)

    else:

        texture_path = bake(bake_node=shader_node, shading_group=shading_group)

    return texture_path


# ----------------------------------------------------------------------------------------------


def get_bump_data(shader_node, shading_group):

    node = '.'.join(shader_node.split('.')[0:-1])
    node_type = cmds.nodeType(node)

    if node_type == 'file' or node_type == 'file':

        texture_path = get_file_path(shader_node, shading_group)

    elif node_type == 'bump2d':

        bump_attr_name = '%s.bumpValue' % node
        bump_input = cmds.listConnections(bump_attr_name, plugs=True)[0]

        texture_path = get_file_path(bump_input, shading_group)

        bump_weight = cmds.getAttr('%s.bumpDepth' % node)
        bump_type = cmds.getAttr('%s.bumpInterp' % node)

        if bump_type == 0:
            bump_type = 'bump'

        else:
            bump_type = 'normal'

    elif node_type == 'bump3d':

        bump_attr_name = '%s.bumpValue' % node
        bump_input = cmds.listConnections(bump_attr_name, plugs=True)[0]

        texture_path = get_file_path(bump_input, shading_group)

        bump_weight = cmds.getAttr('%s.bumpDepth' % node)
        bump_type = 'bump'

    elif node_type == 'aiBump2d' or node_type == 'aiBump3d':

        bump_attr_name = '%s.bumpMap' % node
        bump_input = cmds.listConnections(bump_attr_name, plugs=True)[0]

        texture_path = get_file_path(bump_input, shading_group)

        bump_weight = cmds.getAttr('%s.bumpHeight' % node)
        bump_type = 'bump'

    elif node_type == 'aiNormalMap':

        bump_attr_name = '%s.input' % node
        bump_input = cmds.listConnections(bump_attr_name, plugs=True)[0]

        texture_path = get_file_path(bump_input, shading_group)

        bump_weight = cmds.getAttr('%s.strength' % node)
        bump_type = 'normal'

    else:

        texture_path = None
        bump_weight = 0
        bump_type = 'bump'

    return [texture_path, bump_weight, bump_type]


# ----------------------------------------------------------------------------------------------


def copy_texture(texture_path, texture_name, export_dir):

    extension = os.path.splitext(texture_path)[1]

    full_texture_name = texture_name + extension
    destination_path = os.path.join(export_dir, full_texture_name).replace('\\', '/')

    shutil.copy(texture_path, destination_path)

    return full_texture_name


# ----------------------------------------------------------------------------------------------


def export_textures(export_dir):

    print('\n>>> Exporting materials...\n')

    character = cmds.ls(sl=True)[0]

    all_objects = cmds.listRelatives(character, ad=True, ni=True, type='shape')

    # Gather all shading groups
    shading_groups = []

    for obj in all_objects:

        obj_shading_nodes = cmds.listConnections(obj, type='shadingEngine', s=False)

        if obj_shading_nodes:

            for sg in obj_shading_nodes:

                # Make sure there are no duplicates
                if sg not in shading_groups:

                    shading_groups.append(sg)

    materials = {}

    for sg in shading_groups:

        # Export Surface Shader
        material = cmds.listConnections('%s.surfaceShader' % sg)
        displacement = cmds.listConnections('%s.displacementShader' % sg)

        if material:

            material = material[0]
            material_type = cmds.objectType(material)

            if material_type in material_attributes.keys():

                materials[material] = {}

                if material_type == 'aiStandardSurface':

                    materials[material]['type'] = 'surface'

                elif material_type == 'aiFlat':

                    materials[material]['type'] = 'flat'

                print('>>> Exporting material:', material)

                for attr in material_attributes[material_type].keys():

                    attribute_name = material_attributes[material_type][attr]
                    base_name = '_'.join(material.split('_')[:-1])

                    texture_name = '{mat}_{type}'.format(mat=base_name, type=attr)

                    full_name = material + '.' + attribute_name
                    connection_status = cmds.connectionInfo(full_name, isDestination=True)

                    # If there is a incoming connection check
                    if connection_status and attr in accepting_textures:

                        connection = cmds.listConnections(full_name, plugs=True)[0]

                        if attribute_name != 'normalCamera':

                            texture_path = get_file_path(connection, sg)
                            full_texture_name = copy_texture(texture_path, texture_name, export_dir)
                            materials[material][attr] = full_texture_name

                        else:

                            connection_node = '.'.join(connection.split('.')[0:-1])
                            incoming_connection = cmds.listConnections(connection_node, d=False, s=True) or None

                            if incoming_connection:

                                texture_path, bump_value, bump_type = get_bump_data(connection, sg)

                                if bump_type == 'bump':

                                    bump_key = 'TEX_BUMP'

                                elif bump_type == 'normal':

                                    bump_key = 'TEX_NORM'

                                texture_name = '{mat}_{type}'.format(mat=base_name, type=bump_key)

                                full_texture_name = copy_texture(texture_path, texture_name, export_dir)

                                materials[material][bump_key] = full_texture_name
                                materials[material]['TEX_BUMPWEIGHT'] = bump_value

                            else:

                                cmds.warning(
                                    '>>> Node "{}" has no incoming connection. Skipping.'.format(connection_node)
                                )

                    # If not write attr value to dict
                    else:

                        if attribute_name != 'normalCamera':

                            attr_value = cmds.getAttr(full_name)

                            if type(attr_value) == list:

                                attr_value = attr_value[0]

                            materials[material][attr] = attr_value

                        else:

                            materials[material][attr] = None

                print('>>>', material, 'exported.')

        else:

            print('>>> Missing surface shader for shading group:', sg)

        # Export displacement
        if displacement != None:

            displacement = displacement[0]
            displacement_shader_type = cmds.objectType(displacement)

            if displacement_shader_type == 'displacementShader':

                disp_connection = cmds.connectionInfo('%s.displacement' % displacement, sourceFromDestination=True)

                if disp_connection:

                    base_name = '_'.join(material.split('_')[:-1])

                    texture_name = '{mat}_{type}'.format(mat=base_name, type='TEX_DISP')

                    texture_path = get_file_path(disp_connection, sg)
                    full_texture_name = copy_texture(texture_path, texture_name, export_dir)
                    materials[material]['TEX_DISP'] = full_texture_name

                    disp_scale = '%s.scale' % displacement
                    disp_zero_value = '%s.aiDisplacementZeroValue' % displacement
                    materials[material]['disp_scale'] = disp_scale
                    materials[material]['disp_zero_value'] = disp_zero_value

                else:

                    cmds.warning('>>> Displacement shader:', displacement, ',has no input connection. Skipping.')

            else:

                cmds.warning('>>> Unsupported displacement shader used with material:', material)

    # Export json
    json_export_path = os.path.join(export_dir, 'material_settings.json').replace('\\', '/')

    with open(json_export_path, 'w') as fp:
        json.dump(materials, fp, indent=4)

    print('\n>>> All materials exported.')


# ----------------------------------------------------------------------------------------------


def export_groom(export_dir):

    print('\n>>> Exporting xGen groom...\n')

    all_descriptions = xg.descriptions()
    all_interactive_grooms = []
    for_conversion = {}
    all_materials = {}

    i = 1

    for description in all_descriptions:

        collection = xg.palette(description)

        scalp_geo = xg.boundGeometry(collection, description)[0]
        scalp_geo_shape = cmds.listRelatives(scalp_geo, shapes=True, noIntermediate=True)[0]

        spline_base = cmds.listConnections('{}.worldMesh'.format(scalp_geo_shape), type='xgmSplineBase')

        new_name = 'groom{id}_{mesh}_splineDescription'.format(id=str(i), mesh=scalp_geo)

        if spline_base != None:

            interactive_groom = cmds.listConnections(
                '{}.outSplineData'.format(spline_base[0]), type='xgmSplineDescription'
            )[0]
            interactive_groom_shape = cmds.listRelatives(interactive_groom, type='xgmSplineDescription')[0]
            interactive_groom_sg = cmds.listConnections('{}.instObjGroups'.format(interactive_groom_shape))[0]
            material = cmds.listConnections('{}.surfaceShader'.format(interactive_groom_sg))[0]

            if material not in all_materials.keys():
                all_materials[material] = [new_name]
            else:
                all_materials[material].append(new_name)

            cmds.rename(interactive_groom, new_name)
            all_interactive_grooms.append(new_name)

        else:

            for_conversion[description] = new_name

        i += 1

    if for_conversion:

        for desc, name in for_conversion.items():

            # Find hair material
            desc_shape = cmds.listRelatives(desc, type='xgmDescription')[0]
            desc_shading_group = cmds.listConnections('{}.instObjGroups'.format(desc_shape))[0]
            material = cmds.listConnections('{}.surfaceShader'.format(desc_shading_group))[0]

            if material not in all_materials.keys():
                all_materials[material] = [name]
            else:
                all_materials[material].append(name)

            cmds.select(desc)
            interactive_groom_shape = cmds.xgmGroomConvert()[0]
            interactive_groom = cmds.listRelatives(interactive_groom_shape, p=True)[0]

            # Assign hair material to interactive groom
            interactive_groom_sg = cmds.listConnections('{}.instObjGroups'.format(interactive_groom_shape))[0]
            cmds.connectAttr(material + '.outColor', interactive_groom_sg + '.surfaceShader', force=True)

            cmds.rename(interactive_groom, name)
            all_interactive_grooms.append(name)

    for m, g in all_materials.items():

        materials_jsos_path = os.path.join(export_dir, 'material_settings.json').replace('\\', '/')
        f = open(materials_jsos_path)
        data = json.load(f)

        base_color = cmds.getAttr('%s.baseColor' % m)
        melanin = cmds.getAttr('%s.melanin' % m)
        melanin_redness = cmds.getAttr('%s.melaninRedness' % m)
        melanin_randomize = cmds.getAttr('%s.melaninRandomize' % m)
        roughness = cmds.getAttr('%s.roughness' % m)
        ior = cmds.getAttr('%s.ior' % m)

        data[m] = {}
        data[m]['type'] = 'hair'
        data[m]['assigned_groom'] = g
        data[m]['base_color'] = tuple(base_color[0])
        data[m]['melanin'] = melanin
        data[m]['melanin_redness'] = melanin_redness
        data[m]['melanin_randomize'] = melanin_randomize
        data[m]['roughness'] = roughness
        data[m]['ior'] = ior

        with open(materials_jsos_path, 'w') as outfile:
            json.dump(data, outfile, indent=4)

    if all_interactive_grooms:

        # Export groom
        export_path = os.path.join(export_dir, 'groom.abc').replace('\\', '/')
        current_frame = cmds.currentTime(query=True)

        job = '-f {path} -fr {sf} {ef} -step 1 -wfw'.format(
            path=export_path,
            sf=current_frame,
            ef=current_frame,
        )

        for groom in all_interactive_grooms:
            job += ' -obj {}'.format(groom)

        cmds.xgmSplineCache(export=True, j=job)

        print('>>> All xGen grooms exported.')

    else:

        cmds.warning('>>> No interactive grooms for export.')


# ----------------------------------------------------------------------------------------------


def check_groom_materials():

    print('\n>>> Checking hair materials...\n')

    all_descriptions = xg.descriptions()
    abort_message = []

    for description in all_descriptions:

        collection = xg.palette(description)

        scalp_geo = xg.boundGeometry(collection, description)[0]
        scalp_geo_shape = cmds.listRelatives(scalp_geo, shapes=True, noIntermediate=True)[0]

        spline_base = cmds.listConnections('{}.worldMesh'.format(scalp_geo_shape), type='xgmSplineBase')

        if spline_base != None:

            interactive_groom = cmds.listConnections(
                '{}.outSplineData'.format(spline_base[0]), type='xgmSplineDescription'
            )[0]
            interactive_groom_shape = cmds.listRelatives(interactive_groom, type='xgmSplineDescription')[0]
            interactive_groom_sg = cmds.listConnections('{}.instObjGroups'.format(interactive_groom_shape)) or None
            material = cmds.listConnections('{}.surfaceShader'.format(interactive_groom_sg[0])) or None
            groom_name = interactive_groom

        else:

            description_shape = cmds.listRelatives(description, type='xgmDescription')[0]
            description_sg = cmds.listConnections('{}.instObjGroups'.format(description_shape)) or None
            material = cmds.listConnections('{}.surfaceShader'.format(description_sg[0])) or None
            groom_name = description

        if material:

            material_type = cmds.objectType(material[0])

            if material_type != 'aiStandardHair':

                cmds.warning(
                    '>>> Material "{}" is not supported. Only "aiStandardHair" materials are suppored'.format(
                        material[0]
                    )
                )

                if 'invalid mat' not in abort_message:
                    abort_message.append('invalid mat')
        else:

            cmds.warning(
                '>>> "{}" has no material assigned. Make sure that all xGen descriptions have "aiStandardHair" assigned to them."'.format(
                    groom_name
                )
            )

            if 'no sg' not in abort_message:
                abort_message.append('no sg')

    if abort_message:

        if len(abort_message) == 1:

            if abort_message[0] == 'no sg':

                message = 'Hair is missing a material. Make sure that all hair descriptions have proper material assigned. Aborting...'

            else:

                message = 'Unsupported hair materials. Only "aiStandardHair" materials are supported. Aborting...'

        else:

            message = 'Unsupported hair materials used and some hair decriptions are missing materials. Aborting...'

        user_return = cmds.confirmDialog(title='Error!', message=message, button=['OK', 'Help'])

        if user_return == 'Help':
            webbrowser.open(
                'https://www.notion.so/wonderdynamics/Character-Development-Documentation-for-Maya-a8b5b8baa7be4b1684a84a951cdccd92?pvs=4#c9a661aa243f4eff819d570759062336'
            )

        quit('Hair material error.')

    else:

        print('>>> Hair materials check - PASS')


# ----------------------------------------------------------------------------------------------


def create_export_dir():

    scene_path = cmds.file(query=True, sceneName=True)
    scene_root_dir = os.path.dirname(scene_path)

    pack_dir = os.path.join(scene_root_dir, '01_character_data').replace('\\', '/')

    if os.path.isdir(pack_dir) == False:

        os.mkdir(pack_dir)

    return pack_dir


# ----------------------------------------------------------------------------------------------


def make_camelcase(string):

    camelcase = re.sub(r'(_| |-)+', ' ', string)

    if len(camelcase.split(' ')) > 1:

        camelcase = camelcase.title().replace(' ', '')
        camelcase = ''.join([camelcase[0].lower(), camelcase[1:]])

    else:

        camelcase = string

    return camelcase


# ----------------------------------------------------------------------------------------------


def resolve_naming_conflicts():

    all_meshes = cmds.ls(type='mesh', noIntermediate=True)

    checked_list = []
    rename_dict = {}

    for transform in all_meshes:

        short_name = transform.split('|')[-1]

        if short_name in checked_list:

            if short_name not in rename_dict.keys():

                rename_dict[short_name] = []

            rename_dict[short_name].append(transform)

        else:

            checked_list.append(short_name)

    if rename_dict:

        user_return = cmds.confirmDialog(
            title='Error!', message='Geometries with the same name found.', button=['Abort', 'Fix', 'Help']
        )

        if user_return == 'Help':
            webbrowser.open(
                'https://www.notion.so/wonderdynamics/Character-Development-Documentation-for-Maya-a8b5b8baa7be4b1684a84a951cdccd92?pvs=4#b91c9fcd546040cfa3c4bddaba3535f6'
            )
            quit('Geometries with the same name found.')

        if user_return == 'Abort':
            quit('Geometries with the same name found.')

        if user_return == 'Fix':

            for clashing_geo in rename_dict.values():

                i = 1
                for geo in clashing_geo:

                    geo_parent = cmds.listRelatives(geo, parent=True, type='transform', path=True)[0]
                    new_name = '{root}_{num}'.format(root=geo_parent.split('|')[-1], num=str(i))
                    cmds.rename(geo_parent, new_name)

                    print('>>> Renamed: {old} > {new}'.format(old=geo_parent, new=new_name))

                    i += 1


# ----------------------------------------------------------------------------------------------


def check_naming():

    print('\n>>> Checking naming...\n')

    resolve_naming_conflicts()

    character = cmds.ls(sl=True)[0]
    all_shapes = cmds.listRelatives(character, ad=True, noIntermediate=True, type='shape')

    all_objects = []
    all_shading_nodes = []

    for shape in all_shapes:

        object = cmds.listRelatives(shape, parent=True)[0]
        obj_shading_nodes = cmds.listConnections(shape, type='shadingEngine', s=False)

        if object not in all_objects:

            all_objects.append(object)

        if obj_shading_nodes:

            if obj_shading_nodes not in all_shading_nodes:

                all_shading_nodes.append(obj_shading_nodes)

    # Rename objects
    for obj in all_objects:

        camelcase_name = make_camelcase(obj)
        cmds.rename(obj, camelcase_name)

    for shading_nodes in all_shading_nodes:

        for sg in shading_nodes:

            material = cmds.listConnections('%s.surfaceShader' % sg)

            if material is not None:

                material_name = material[0].split('_')

                if material_name[-1] != 'MAT':

                    new_material_name = make_camelcase(material[0]) + '_MAT'
                    cmds.rename(material, new_material_name)

                else:

                    new_material_name = make_camelcase('_'.join(material_name[:-1])) + '_MAT'
                    cmds.rename(material, new_material_name)

    rig_group = cmds.ls(type='joint', long=True)[0].split('|')[1]
    rig_group_sufix = rig_group.split('_')[-1]

    if rig_group_sufix != 'BODY':

        user_return = cmds.confirmDialog(
            title='Error!', message='Group with the rig needs to have "_BODY" sufix! Aborting...', button=['OK', 'Help']
        )

        if user_return == 'Help':
            webbrowser.open(
                'https://www.notion.so/wonderdynamics/Character-Development-Documentation-for-Maya-a8b5b8baa7be4b1684a84a951cdccd92?pvs=4#866cb3df206a4736888b4295a1646657'
            )

        quit('Wrong group naming.')

    else:

        print('>>> Naming check - PASS')


# ----------------------------------------------------------------------------------------------


def check_missing_files():

    print('\n>>> Checking for missing files...\n')

    all_file_nodes = cmds.ls(type='file')

    missing_files = []
    not_linked_files = []

    for file_node in all_file_nodes:

        texture_path = cmds.getAttr(file_node + '.fileTextureName')

        if texture_path:

            if not os.path.exists(texture_path):

                missing_files.append(texture_path)

        else:

            not_linked_files.append(file_node)

    if missing_files:

        for mf in missing_files:

            cmds.warning('>>> Missing texture: ' + mf)

        mel.eval('FilePathEditor')
        user_return = cmds.confirmDialog(
            title='Error!',
            message='Missing some textures! Please make sure all textures are linked properly. Aborting...',
            button=['OK', 'Help'],
        )

        if user_return == 'Help':
            webbrowser.open(
                'https://www.notion.so/wonderdynamics/Character-Development-Documentation-for-Maya-a8b5b8baa7be4b1684a84a951cdccd92?pvs=4#c612627dde4b4cf48aaff43886a71dad'
            )

        quit('Missing some textures.')

    if not_linked_files:

        for file in not_linked_files:

            cmds.warning('>>> File node "{}" is empty.'.format(file))

        user_return = cmds.confirmDialog(
            title='Error!', message='Some file nodes are empty.', button=['Abort', 'Fix', 'Help']
        )

        if user_return == 'Help':
            webbrowser.open(
                'https://www.notion.so/wonderdynamics/Character-Development-Documentation-for-Maya-a8b5b8baa7be4b1684a84a951cdccd92?pvs=4#8e6426521ce9453dbfecf72f9967d3f5'
            )
            quit('Empty file nodes.')

        if user_return == 'Fix':
            for file in not_linked_files:
                print('>>> File node "{}" - FIXED'.format(file))
                cmds.delete(file)

        if user_return == 'Abort':
            quit('Empty file nodes.')

    else:

        print('>>> Missing files check - PASS')


# ----------------------------------------------------------------------------------------------


def make_selection():

    cmds.select(clear=True)

    geo_group = cmds.ls('|GEO')

    if geo_group:

        cmds.select(geo_group)

    else:

        user_return = cmds.confirmDialog(
            title='Error!', message='Group "GEO" could not be found. Aborting...', button=['OK', 'Help']
        )

        if user_return == 'Help':
            webbrowser.open(
                'https://www.notion.so/wonderdynamics/Character-Development-Documentation-for-Maya-a8b5b8baa7be4b1684a84a951cdccd92?pvs=4#3d4825eccc2749ba974ef3cd06901d51'
            )

        quit('Group "GEO" could not be found.')


# ----------------------------------------------------------------------------------------------


def check_materials():

    print('\n>>> Checking materials...\n')

    suported_material_type = ['aiStandardSurface', 'aiFlat']

    all_meshes = cmds.listRelatives('|GEO', ad=True, type='mesh')
    not_suppored_materials = {}

    for mesh in all_meshes:

        if cmds.getAttr('%s.intermediateObject' % mesh) == 0:

            shading_group = cmds.listConnections(mesh, type='shadingEngine') or None

            if shading_group:

                material = cmds.listConnections('%s.surfaceShader' % shading_group[0]) or [None]
                material = material[0]

                if material:

                    if material not in not_suppored_materials.keys():

                        material_type = cmds.objectType(material)

                        if material_type not in suported_material_type:

                            not_suppored_materials[material] = material_type
                else:

                    cmds.warning(
                        '>>> Mesh "{m}" with the shading group "{sg}" has no material assinged.'.format(
                            m=mesh, sg=shading_group
                        )
                    )

            else:

                cmds.warning('>>> Mesh "{}" is missing a shading group.'.format(mesh))

    if not_suppored_materials:

        for k, v in not_suppored_materials.items():

            cmds.warning('>>> Material {mat} is of type {type} which is not supported.'.format(mat=k, type=v))

        user_return = cmds.confirmDialog(
            title='Error!',
            message='One or more materials are not supported. Currently only "aiStandardSurface" and "aiFlat" are supported. Aborting...',
            button=['OK', 'Help'],
        )

        if user_return == 'Help':
            webbrowser.open(
                'https://www.notion.so/wonderdynamics/Character-Development-Documentation-for-Maya-a8b5b8baa7be4b1684a84a951cdccd92?pvs=4#54e3941a7465476f98fd350dce4956ff'
            )

        quit('Materials not supported.')

    else:

        print('>>> Character materials check - PASS')


# ----------------------------------------------------------------------------------------------


def main():

    print('\n------ SCRIPT START ------\n')

    # Check for xGen
    xg_collections = xg.palettes()

    if xg_collections:

        user_return = cmds.confirmDialog(
            title='Character Export',
            message='XGen is detected in the scene. Continue the character export...',
            button=['With XGen', 'Without XGen', 'Abort'],
        )

        if user_return == 'Abort':
            quit('User abort.')

    else:

        user_return = 'Without XGen'

    make_selection()

    # Scene validations
    check_materials()

    if user_return == 'With XGen':
        check_groom_materials()

    check_missing_files()
    check_naming()

    # Export elements
    export_dir = create_export_dir()
    export_meshes(export_dir)
    export_textures(export_dir)

    if user_return == 'With XGen':
        export_groom(export_dir)

    print('\n------- SCRIPT END -------\n')


# ----------------------------------------------------------------------------------------------

if __name__ == '__main__':

    main()
