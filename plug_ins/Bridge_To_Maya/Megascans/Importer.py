"""
This module:
- Imports the actual textures linked with asset
- Imports the actual geometry/mesh of the asset 
"""

import os
import maya.cmds as mc
import maya.mel as melc

from Megascans.ImporterSetup import importerSetup
instance = importerSetup.getInstance()

""" importTextureData creates a file node for each texture in instance.TexturesList. This imports the actual textures associated with the geometry """

def importTextureData():

    instance.tex_nodes = []

    cm_attrs = [("cme", "cme"), ("cfe", "cmcf"), ("cfp", "cmcp"), ("wsn", "ws")]
    colMgmtGlob = ('defaultColorMgtGlobals')
    instance.coord_2d = mc.shadingNode('place2dTexture', asUtility=True, name=(instance.ID + "_Coords"))

    maps_ = [item[1] for item in instance.TexturesList]

    # tex = instance.TexturesList[2]
    for tex in instance.TexturesList:

        texture_ = tex[2]

        if tex[1] == "displacement":
            print("DISPLACEMENT SET TO EXR...")
            dirn_ = os.path.dirname(tex[2])
            filen_ = os.path.splitext(os.path.basename(tex[2]))[0]
            if os.path.exists(os.path.join(dirn_, filen_ + ".exr")):
                texture_ = os.path.join(dirn_, filen_ + ".exr")

        newMap = mc.shadingNode('file', asTexture=True, name=(instance.Name + "_" + tex[1].capitalize()) )

        mc.setAttr(newMap+".ftn", texture_, type="string")
        try:
            for attr in cm_attrs:
                mc.connectAttr(colMgmtGlob +"."+attr[0], newMap+"."+attr[1])
        except:
            pass

        mc.setAttr(newMap+".ft", 2)
        mc.defaultNavigation(connectToExisting=True, source=instance.coord_2d, destination=newMap)
        
        if tex[0] == "exr":
            melc.eval('setAttr "'+ newMap +'.cs" -type "string" "Raw";')
        else:
            if tex[1].lower() in ["albedo", "translucency", "specular"]:
                melc.eval('setAttr "'+ newMap +'.cs" -type "string" "sRGB";')
            else:
                melc.eval('setAttr "'+ newMap +'.cs" -type "string" "Raw";')


        instance.tex_nodes.append((newMap, tex[1]))
        
"""importGeometryData imports the actual geometry """
def importGeometryData():

    scene_a = mc.ls()

    if instance.ApplyToSelection and instance.Type.lower() not in ["3dplant", "3d"]:
        try:
            for m in mc.ls(sl=True,typ="transform"):
                objectProps = mc.listRelatives(m, typ="mesh")
                if objectProps is not None and len(objectProps) >= 1:
                    instance.mesh_transforms.append(m)
                else:
                    objectProps = mc.listRelatives(m, typ="nurbsSurface")
                    if objectProps is not None and len(objectProps) >= 1:
                        instance.mesh_transforms.append(m)
        except:
            pass

    for mesh in instance.GeometryList:
        if mesh[0] == "fbx":
            path_ = mesh[1]
            mc.file(path_, i=True, type="FBX", ignoreVersion=True, rpr=os.path.basename(instance.Name), options="fbx")

        elif mesh[0] == "obj":
            path_ = mesh[1]
            mc.file(path_, i=True, type="OBJ", ignoreVersion=True, rpr=os.path.basename(instance.Name), options="obj")
        
        elif mesh[0] == "abc":
            path_ = mesh[1]
            mc.file(path_, i=True, type="Alembic", ignoreVersion=True, rpr=os.path.basename(instance.Name), importFrameRate = True, importTimeRange = "override")

    imported_ = list(set(mc.ls())-set(scene_a))
    # get shapes of selection:
    # get shading groups from shapes:
    shadingGrps = mc.listConnections(imported_,type='shadingEngine')
    # remove duplicate shading groups from list
    if not shadingGrps == None:  
        shadingGrps = list(set(shadingGrps))
        # get the shaders:
        shaders = mc.ls(mc.listConnections(shadingGrps),materials=1)
        # remove duplicate shaders from list
        shaders = list(set(shaders))
        instance.defaultShaderList = shadingGrps
    
    #print(instance.defaultShaderList)

    #Checks if the object is multimaterial, if it is then deletes the shader only
    if not instance.isMultiMat:
        for a in imported_:
            try:
                if mc.nodeType(a) == "transform":
                    melc.eval('assignSG lambert1 '+ a +';')

                    newMesh = mc.rename(a, instance.createName(a) )
                    instance.mesh_transforms.append(newMesh)
                    instance.imported_geo.append(newMesh)

                if mc.nodeType(a) not in ["transform", "mesh"]:
                        try:
                            melc.eval('delete ' + a)
                        except:
                            pass
                    # elif mc.nodeType(a) not in instance.defaultShaderList:
                    #     print("MULTI MAT AND NOT IN DEFAULT")
                    #     try:
                    #         melc.eval('delete ' + a)
                    #     except:
                    #         pass
            except:
                pass
            
    else:
         mc.delete (mc.ls(mc.listConnections(shadingGrps),materials=1))
