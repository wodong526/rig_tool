# -*- coding:GBK -*-
import os

import maya.cmds as mc
import maya.mel as mm
import pymel.core as pm
import maya.OpenMayaUI as omui

from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import traceback

from feedback_tool import Feedback_info as fp
from dutils import clearUtils, toolUtils, attrUtils, ctrlUtils, apiUtils

FILE_PATH = __file__


def LIN():
    line_number = traceback.extract_stack()[-2][1]
    return line_number


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def freeze_rotation():
    objs = pm.selected()
    for obj in objs:
        if isinstance(obj, pm.nt.Joint):
            rot = obj.rotate.get()
            ra = obj.rotateAxis.get()
            jo = obj.jointOrient.get()
            rotMatrix = pm.dt.EulerRotation(rot, unit='degrees').asMatrix()
            raMatrix = pm.dt.EulerRotation(ra, unit='degrees').asMatrix()
            joMatrix = pm.dt.EulerRotation(jo, unit='degrees').asMatrix()
            rotationMatrix = rotMatrix * raMatrix * joMatrix
            tmat = pm.dt.TransformationMatrix(rotationMatrix)
            newRotation = tmat.eulerRotation()
            newRotation = [pm.dt.degrees(x) for x in newRotation.asVector()]
            obj.rotate.set(0, 0, 0)
            obj.rotateAxis.set(0, 0, 0)
            obj.jointOrient.set(newRotation)
            fp('{}的旋转已冻结。'.format(obj), info=True)
            continue


def select_skinJoint():
    """
    通过选中的模型获取该模型的蒙皮关节
    :return:
    """
    sel_lis = mc.ls(sl=1)
    jnt_lis = []
    for mod in sel_lis:
        fn_skin = apiUtils.fromObjGetRigNode(mod, path_name=False)[0]
        jnt_lis = jnt_lis+apiUtils.fromSkinGetInfluence(fn_skin)
    if jnt_lis:
        mc.select(jnt_lis)
        fp('已选中蒙皮关节。', info=True)
    else:
        fp('选中对象没有蒙皮关节。', error=True)


def get_length():
    obj = mc.ls(sl=True, fl=True)
    n = len(obj)
    fp('选中对象共有：{}个。对象为：{}。'.format(n, obj), info=True)


def selectSameName():
    """
    生成获取字符的对话框，通过名称匹配得到与指定字符相同的节点，并选择他们
    :return: None
    """
    try:
        obj_tag = raw_input()
    except EOFError:
        fp('没有输入有效对象', warning=True)
    else:
        try:
            mc.select(obj_tag)
        except ValueError:
            all_lis = mc.ls()
            mc.select(cl=True)
            uid_lis = []
            for obj in all_lis:
                uid_lis.append(mc.ls(obj, uid=True)[0])
            for key, obj in enumerate(all_lis):
                if '|' in obj:
                    obj = obj.split('|')[-1]
                if obj_tag == obj:
                    mc.select(mc.ls(uid_lis[key])[0], add=True)
        finally:
            if mc.ls(sl=True):
                #mc.FrameSelectedWithoutChildren()
                fp('与{}同名的对象有{}个'.format(obj_tag, len(mc.ls(sl=True))), info=True)
            else:
                fp('没有与{}同名的对象'.format(obj_tag), info=True)


def exportSelectToFbx():
    """
    将选中的对象导出为fbx，切断开关节与控制器的链接。
    """
    def to_Tpose():
        if mc.objExists('FKShoulder_R') and mc.objExists('FKShoulder_L'):
            if mc.getAttr('FKShoulder_R.ry') == -45 and mc.getAttr('FKShoulder_L.ry') == -45:
                return
            else:
                mc.setAttr('FKShoulder_R.ry', -45)
                mc.setAttr('FKShoulder_L.ry', -45)
        else:
            fp('场景中不存在对象：FKShoulder_R或FKShoulder_L。', error=True, viewMes=True)

    sel_lis = mc.ls(sl=1)
    if sel_lis:

        #################检查毛发对象
        obj_lis = []
        hair_lis = []
        for obj in sel_lis:
            for inf in mc.listRelatives(obj, ad=True):
                obj_lis.append(inf)
        if obj_lis:
            for obj in obj_lis:
                if 'Hair' in obj or 'hair' in obj:
                    if not mc.nodeType(obj) == 'joint':
                        hair_lis.append(obj)
        if hair_lis:
            resout = mc.confirmDialog(title='警告：', message='{}\n可能是毛发模型，应该删除。'.format(hair_lis),
                                      button=['取消导出', '继续导出'])
            if resout == u'取消导出':
                return None
            elif resout == u'继续导出':
                pass
        #################检查空间名称
        namSpas, namSpas_lis = clearUtils.clear_nameSpace(q=True)  #当场景里有空间名时提示
        if namSpas:
            resout = mc.confirmDialog(title='警告：', button=['清理空间名后再导出', '不清理直接导出', '取消'],
                                      message='场景中有空间名称：\n{}\n是否清理后再导出或直接导出？'.format('\n'.join(namSpas_lis)))
            if resout == u'清理空间名后再导出':
                clearUtils.clear_nameSpace()
            elif resout == u'不清理直接导出':
                pass
            else:
                return None
        #################掰直手臂
        resout = mc.confirmDialog(title='导出设置：', button=['导出为TPose', '直接导出当前姿势', '取消'],
                                  message='是否将APose以TPose姿势导出？')#将APose绑定以TPose姿势导出
        if resout == u'导出为TPose':
            to_Tpose()
        elif resout == u'直接导出当前姿势':
            pass
        else:
            return None

        file_path = mc.file(exn=True, q=True)
        file_nam = file_path.split('/')[-1].split('.')[0]
        fbx_nam = 'SK'
        for nam in file_nam.split('_')[2:-1]:
            fbx_nam = fbx_nam + '_' + nam
        file_path = QtWidgets.QFileDialog.getSaveFileName(maya_main_window(), u'选择fbx文件',
                                                          file_path.replace(file_path.split('/')[-1], fbx_nam),
                                                          '(*.fbx)')  #获取导出fbx路径

        if file_path[0]:
            node_lis = []
            pert_dir = {}
            for inf in sel_lis:  #断开选择对象的父级以避免导出多于对象
                if mc.listRelatives(inf, p=True):
                    pert_dir[inf] = mc.listRelatives(inf, p=True)[0]
                    mc.parent(inf, w=True)
                else:
                    fp('{}已在世界层级下。'.format(inf), info=True)

                if mc.listConnections(inf, d=False):
                    node_lis = mc.listConnections(inf, d=False, c=1, p=1)
                    for n in range(len(node_lis) // 2):
                        mc.disconnectAttr(node_lis[n * 2 + 1], node_lis[n * 2])
                        fp('已断开{}。'.format(node_lis[n * 2 + 1]), info=True)

            mc.select(sel_lis)
            mc.FBXProperty('Export|IncludeGrp|Animation', '-v', '0')
            mc.file(file_path[0], f=True, typ='FBX export', pr=True, es=True)
            fp('已导出{}。'.format(sel_lis), info=True)

            for n in range(len(node_lis) // 2):  #重新链接上游节点
                mc.connectAttr(node_lis[n * 2 + 1], node_lis[n * 2])
                fp('已链接{}。'.format(node_lis[n * 2 + 1]), info=True)
            for inf in pert_dir:  # 重新p回父级
                mc.parent(inf, pert_dir[inf])
            return file_path[0]
        else:
            fp('没有选择有效路径。', error=True)

    else:
        fp('没有选择有效对象。', error=True)


def createRibbon(nam, ctl_n, jnt_n, foll_ctl=False):
    """
    从两根曲线之间生成ik关节链和控制器，使控制器能随时调整ik
    :param foll_ctl: 生成的曲面段数是否跟随控制器数量，不跟随则跟随曲线段数
    :param nam: 此rig的名称
    :param ctl_n: 控制器数量
    :param jnt_n: ik关节数量
    :return: None
    """
    sel_lis = mc.ls(sl=True)
    for cvr in sel_lis:
        if foll_ctl:
            mc.rebuildCurve(cvr, rpo=True, end=1, kr=0, kt=False, s=ctl_n - 1)
        else:
            mc.rebuildCurve(cvr, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kt=0, s=1, d=3, tol=0.01)
    surf = mc.loft(sel_lis[0], sel_lis[1], ch=False, u=True, rn=False, po=0, n='surf_{}_{:03d}'.format(nam, 1))[0]
    mc.setAttr('{}.inheritsTransform'.format(surf), False)

    crvFromSur = mc.createNode('curveFromSurfaceIso', n='crvFromSur_{}_{:03d}'.format(nam, 1))
    mc.setAttr('{}.isoparmValue'.format(crvFromSur), 0.5)
    mc.setAttr('{}.isoparmDirection'.format(crvFromSur), 1)
    lsoShape = mc.createNode('nurbsCurve', n='crv_{}_{:03d}Shape'.format(nam, 1))
    lso = mc.rename(mc.listRelatives(lsoShape, p=True), 'crv_{}_{:03d}'.format(nam, 1))
    mc.setAttr('{}.v'.format(lso), False)
    mc.connectAttr('{}.worldSpace[0]'.format(surf), '{}.inputSurface'.format(crvFromSur))
    mc.connectAttr('{}.outputCurve'.format(crvFromSur), '{}.create'.format(lsoShape))

    motPath_node = mc.createNode('motionPath', n='motPath_{}_{:03d}'.format(nam, 1))
    mc.setAttr('{}.fractionMode'.format(motPath_node), 1)
    mc.connectAttr('{}.worldSpace[0]'.format(lsoShape), '{}.geometryPath'.format(motPath_node))
    jnt_lis = []
    for i in range(1, jnt_n + 1):
        mc.select(cl=True)
        jnt = mc.joint(n='jnt_{}_{:03d}'.format(nam, i))
        mc.connectAttr('{}.allCoordinates'.format(motPath_node), '{}.translate'.format(jnt))
        mc.setAttr('{}.uValue'.format(motPath_node), (i - 1) / (jnt_n - 1.0))
        mc.disconnectAttr('{}.allCoordinates'.format(motPath_node), '{}.translate'.format(jnt))
        mc.makeIdentity(jnt, a=True, r=True)
        if jnt_lis:
            mc.parent(jnt, jnt_lis[-1])
        jnt_lis.append(jnt)

    grp_lis = []
    ctl_lis = []
    ctlJnt_lis = []
    for i in range(1, ctl_n + 1):
        ctl = ctrlUtils.create_ctl('ctl_{}_{:03d}'.format(nam, i), cid='C01')
        grp, ctl = ctrlUtils.fromObjCreateGroup(nam, ctl)

        mc.select(cl=True)
        ctlJnt = mc.joint(n='jnt_ctl_{}_{:03d}'.format(nam, i))
        mc.setAttr('{}.v'.format(ctlJnt), False)
        mc.parent(ctlJnt, ctl[0])
        grp_lis.append(grp[0])
        ctl_lis.append(ctl[0])
        ctlJnt_lis.append(ctlJnt)

        mc.connectAttr('{}.allCoordinates'.format(motPath_node), '{}.translate'.format(grp[0]))
        mc.setAttr('{}.uValue'.format(motPath_node), (i - 1) / (ctl_n - 1.0))
        mc.disconnectAttr('{}.allCoordinates'.format(motPath_node), '{}.translate'.format(grp[0]))

    mc.joint(jnt_lis[0], e=True, oj='xyz', sao='yup', zso=True, ch=True)
    ikHad = mc.ikHandle(sj=jnt_lis[0], ee=jnt_lis[-1], c=lso, sol='ikSplineSolver', ccv=False,
                        n='ikHad_{}_{:03d}'.format(nam, 1))[0]
    surSkin = mc.skinCluster(ctlJnt_lis, surf, n='skin_{}_{:03d}'.format(nam, 1))[0]

    grp_main = mc.group(n='grp_{}_001'.format(nam), w=True, em=True)
    mc.parent(ikHad, jnt_lis[0], grp_lis, surf, lso, grp_main)

    cvr_info = mc.createNode('curveInfo', n='cvrInfo_{}_{:03d}'.format(nam, 1))
    mc.connectAttr('{}.worldSpace[0]'.format(lsoShape), '{}.inputCurve'.format(cvr_info))
    cvr_length = mc.getAttr('{}.arcLength'.format(cvr_info))

    mult_node = mc.createNode('multiplyDivide', n='mult_{}_cvrLength_{:03d}'.format(nam, 1))
    mc.setAttr('{}.operation'.format(mult_node), 2)
    mc.setAttr('{}.input2X'.format(mult_node), cvr_length)
    mc.connectAttr('{}.arcLength'.format(cvr_info), '{}.input1X'.format(mult_node))

    for i in range(len(jnt_lis) - 1):
        mc.connectAttr('{}.outputX'.format(mult_node), '{}.scaleX'.format(jnt_lis[i]))


def cleanBindingDistortion():
    """
    解决绑定离原点太远造成模型抖动的启动函数
    :return:
    """
    topLevel = mc.ls(sl=True)[0]
    if mc.listConnections(topLevel, d=False):
        mods = mc.listRelatives(topLevel, ad=True)
        toolUtils.processingSkinPrecision(mods)

    else:
        fp('选择对象还没有被root控制约束', error=True, viewMes=True)


def createFollicle(geo, tag_geo, nam='', geo_parent=''):
    """
    在geo（多边形或者曲面）上生成毛囊，毛囊位置为离tag对象最近的位置
    :param nam: 生成的毛囊的主要名字
    :param geo_parent: 生成的毛囊要放在这个组下
    :param geo: 多边形或者曲面
    :param tag_geo: 毛囊离它最近
    :return:
    """
    geo_shape = toolUtils.getShape(geo)
    if not geo_shape:
        fp('对象{}没有shape节点'.format(geo), error=True)

    uv = toolUtils.fromClosestPointGetUv(geo, tag_geo)
    if uv:
        follicle_grp = 'grp_rivet_AA'
        if not mc.objExists(follicle_grp):
            mc.group(n='grp_rivet_AA', em=True, w=True)
            mc.setAttr('{}.v'.format(follicle_grp), 0)
            attrUtils.lock_and_hide_attrs(follicle_grp, attrs=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'],
                                          hide=True, lock=True)

        if geo_parent:
            mc.parent(follicle_grp, geo_parent)
        if not nam:
            nam = geo

        follicle_shape = 'folc_{}_foliShape'.format(nam)
        if mc.objExists(follicle_shape):
            follicle = mc.listRelatives(follicle_shape, p=True)[0]
            mc.delete(follicle, follicle_shape)

        follicle_shape = mc.createNode('follicle', n=follicle_shape)
        follicle = mc.listRelatives(follicle_shape, p=True)[0]

        mc.setAttr('{}.parameterU'.format(follicle_shape), uv[0])
        mc.setAttr('{}.parameterV'.format(follicle_shape), uv[1])
        mc.connectAttr('{}.worldMatrix[0]'.format(geo_shape[0]), '{}.inputWorldMatrix'.format(follicle_shape))
        mc.connectAttr('{}.outTranslate'.format(follicle_shape), '{}.translate'.format(follicle), f=True)
        mc.connectAttr('{}.outRotate'.format(follicle_shape), '{}.rotate'.format(follicle), f=True)
        mc.parent(follicle, follicle_grp, a=True)

        shape_typ = mc.objectType(geo_shape[0])
        if shape_typ == 'mesh':
            mc.connectAttr('{}.outMesh'.format(geo_shape[0]), '{}.inputMesh'.format(follicle_shape))
        elif shape_typ == 'nurbsSurface':
            mc.connectAttr('{}.local'.format(geo_shape[0]), '{}.inputSurface'.format(follicle_shape))
        else:
            fp('对象{}不是模型或者曲面，{}类型是不支持的类型'.format(geo, shape_typ), error=True)

        return follicle
    else:
        fp('对象{}没有uv'.format(geo), error=True)


def create_shape_helper(nam, grp_parent=''):
    """
    创建八方向控制器
    :param nam: 生成的对象的主要名字
    :param grp_parent: 是否要p到某个组里
    :return:
    """
    shape_helper_grp = 'grp_{}_helper_001'.format(nam)
    if not mc.objExists(shape_helper_grp):
        mc.group(empty=True, name=shape_helper_grp)

    if grp_parent:
        mc.parent(shape_helper_grp, grp_parent)

    base_name = '{}_Helper'.format(nam)

    sh_sphere_grp = mc.group(empty=True, name='grp_{}_sphere_001'.format(base_name))
    sh_sphere = mc.sphere(name='{}_sphere'.format(base_name), axis=[0, 1, 0],
                          degree=3, ssw=270, esw=450, r=1, nsp=4, s=4, ch=False)[0]
    sh_sphere_shape = mc.listRelatives(sh_sphere, shapes=True)[0]
    mc.parent(sh_sphere, sh_sphere_grp, absolute=True)
    mc.parent(sh_sphere_grp, shape_helper_grp, absolute=True)

    sh_aim_loc = mc.spaceLocator(name='loc_{}_001'.format(base_name), absolute=True)[0]
    mc.setAttr('{}.tx'.format(sh_aim_loc), 10)
    mc.parent(sh_aim_loc, shape_helper_grp, absolute=True)

    cpos_node = mc.createNode('closestPointOnSurface', name='cloOnSuf_{}_001'.format(base_name))
    mc.connectAttr('{}.worldSpace[0]'.format(sh_sphere_shape), '{}.inputSurface'.format(cpos_node))
    mc.connectAttr('{}.translate'.format(sh_aim_loc), '{}.inPosition'.format(cpos_node))
    mc.setAttr('{}.inPosition'.format(cpos_node), lock=True)

    for attr, uv in {'right': [2, 4], 'left': [2, 0], 'down': [0, 2], 'up': [4, 2]}.items():
        mc.addAttr(sh_aim_loc, ln=attr, at='double', min=0, max=1, dv=0, keyable=True)

        posi_node = mc.createNode('pointOnSurfaceInfo',
                                  name='pntOnSufInf_{}_pointOnSurfaceInfo_{}'.format(base_name, attr))
        mc.connectAttr('{}.worldSpace[0]'.format(sh_sphere_shape), '{}.inputSurface'.format(posi_node))
        mc.setAttr('{}.parameterU'.format(posi_node), uv[0])
        mc.setAttr('{}.parameterV'.format(posi_node), uv[1])

        dist_node = mc.createNode('distanceDimShape', name='dis_{}_{}Shape'.format(base_name, attr))
        mc.parent(mc.listRelatives(dist_node, parent=True)[0], shape_helper_grp, absolute=True)
        mc.connectAttr('{}.position'.format(cpos_node), '{}.startPoint'.format(dist_node))
        mc.connectAttr('{}.position'.format(posi_node), '{}.endPoint'.format(dist_node))

        remap_node = mc.createNode('remapValue', name='remapVal_{}_{}_001'.format(base_name, attr))
        mc.connectAttr('{}.distance'.format(dist_node), '{}.inputValue'.format(remap_node))
        value = mc.getAttr('{}.inputValue'.format(remap_node))

        for a, v in {'inputMin': 0, 'inputMax': value, 'outputMin': 1, 'outputMax': 0}.items():
            mc.setAttr('{}.{}'.format(remap_node, a), v, lock=True)
        mc.connectAttr('{}.outValue'.format(remap_node), '{}.{}'.format(sh_aim_loc, attr))

    return sh_sphere_grp, sh_aim_loc


def brSmoothTool():
    """
    打开brsmooth工具
    :return:
    """
    if not mc.pluginInfo('brSmoothWeights', q=True, r=True):
        for year in ['2018', '2020', '2022', '2023']:
            if mc.about(version = True) == year:
                brSmooth_path = 'C:/Rig_Tools/scripts/brSmoothWeights/plug-ins/win64/{}'.format(year)
                if os.path.exists(brSmooth_path):
                    if brSmooth_path not in os.environ['MAYA_PLUG_IN_PATH']:
                        os.environ['MAYA_PLUG_IN_PATH'] = os.environ['MAYA_PLUG_IN_PATH'] + ';' + brSmooth_path
                    try:
                        mc.loadPlugin('brSmoothWeights.mll')
                    except:
                        fp('brSmoothWeights无法被加载，请检查brSmoothWeights.mll是否在路径中', error=True)
                    mm.eval('brSmoothWeightsToolCtx')
                else:
                    fp('插件不在工具架文件夹中，如果工具架版本不是最新版请同步到最新版。', error=True, viewMes=True, block=False)
    else:
        mm.eval('brSmoothWeightsToolCtx')





