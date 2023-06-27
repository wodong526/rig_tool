# coding=gbk
import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as oma

from feedback_tool import Feedback_info as fb_print, LIN as lin
from dutils import apiUtils

FILE_PATH = __file__


def clear_orig():
    """
    将选中的模型列表依次遍历 如果有orig节点就删除
    :return:
    """
    sel_lis = mc.ls(sl=1)
    for obj in sel_lis:
        for sub_node in mc.listRelatives(obj, s=True):
            if 'Orig' in sub_node and mc.nodeType(sub_node) == 'mesh':
                mc.delete(sub_node)
                fb_print('模型{}的orig节点{}已删除。'.format(obj, sub_node), info=True)
                continue


def goToADV_pose():
    """
    使场景内的adv的buildPose节点储存的对象都回归原位
    :return:
    """
    if mc.objExists('buildPose'):
        mel_str = mc.getAttr('buildPose.udAttr')
        for order in mel_str.split(';'):
            if order:
                if order.split(' ')[-1][0].isalpha() and mc.objExists(order.split(' ')[-1]):
                    mm.eval(order)
        fb_print('adv控制器已回归原位。', info=True, viewMes=True)
    else:
        fb_print('场景内没有adv的buildPose节点', error=True)


def getShape(nodes, getTrs=False, q=False, typ=''):
    """
    检测对象是什么类型，通过对象的shape节点来检测对象类型
    :param typ: 要返回的类型
    :param q: 为true时只返回typ参数指定的类型
    :param getTrs:True返回对象shape类型名，false返回对象trs名
    :param nodes:要检测的对象
    :return:list
    """
    if q and typ not in ['mesh', 'nurbsCurve', 'nurbsSurface', 'lattice', 'locator', 'joint']:
        fb_print('typ参数没有指定有效类型', error=True)

    rtn_lis = []
    if type(nodes) != list:
        nodes = [nodes]

    for node in nodes:
        if mc.nodeType(node) == 'transform':
            shape = mc.listRelatives(node, s=True)
            if shape:
                if q and mc.nodeType(shape[0]) == typ:
                    if not getTrs:
                        rtn_lis.append(shape[0])
                    elif getTrs:
                        rtn_lis.append(node)
                elif not q:
                    if not getTrs:
                        rtn_lis.append(shape[0])
                    elif getTrs:
                        rtn_lis.append(node)
            else:
                continue
        elif mc.nodeType(node) in ['mesh', 'nurbsCurve', 'nurbsSurface', 'lattice', 'locator', 'joint']:
            if q and mc.nodeType(node) == typ:
                if not getTrs:
                    rtn_lis.append(node)
                elif getTrs:
                    rtn_lis.append(mc.listRelatives(node, p=True)[0])
            elif not q:
                if not getTrs:
                    rtn_lis.append(node)
                elif getTrs:
                    rtn_lis.append(mc.listRelatives(node, p=True)[0])
        else:
            fb_print('对象{}是不支持的类型'.format(node), warning=True)
    if rtn_lis:
        return rtn_lis
    else:
        return None


def fromClosestPointGetUv(geo, tag_geo):
    """
    获取geo上离tagGeo最近点的uv值
    :param geo: 要提取uv值的模型
    :param tag_geo: 最近的目标模型
    :return:geo上离tat_geo最近点的uv值
    """
    unit = mc.currentUnit(q=True)
    mc.currentUnit(l='cm')

    geo_shpae = getShape(geo)
    if not geo_shpae:
        fb_print('对象{}没有shape节点'.format(geo), error=True)

    geo_dag = apiUtils.getDagPath(geo)
    poj_pos = apiUtils.getMPoint(tag_geo)

    uv = None
    shape_typ = mc.objectType(geo_shpae)
    if shape_typ == 'mesh':
        fm_geo = oma.MFnMesh(geo_dag)
        uv = fm_geo.getUVAtPoint(poj_pos, space=oma.MSpace.kWorld)[:-1]  #返回的是uv和faceId
    elif shape_typ == 'nurbsSurface':
        fm_geo = oma.MFnNurbsSurface(geo_dag)
        cpos_node = mc.createNode('closestPointOnSurface', n='cloOnSur{}_{:03d}'.format(geo, 1))
        mc.connectAttr('{}.worldSpace[0]'.format(geo_shpae), '{}.inputSurface'.format(cpos_node))
        mc.connectAttr('{}.translate'.format(tag_geo), '{}.inPosition'.format(cpos_node))
        pos = mc.getAttr('{}.position'.format(cpos_node))[0]  #获取该tag_geo对应到该曲面上的位置，要求tag_geo与该曲面在同一个父级下
        mc.delete(cpos_node)

        result_pos = oma.MPoint(pos[0], pos[1], pos[2], 1.0)  #将xyz组合成mpoint类型
        pu, pv = fm_geo.getParamAtPoint(result_pos, ignoreTrimBoundaries=False, tolerance=0.01, space=oma.MSpace.kWorld)

        uv = (pu / fm_geo.numSpansInU, pv / fm_geo.numSpansInV)
    mc.currentUnit(l=unit)

    return uv


def processingSkinPrecision(objs):
    """
    解决绑定离原点太远丢失精度而扭曲
    让模型上层的组跟着root关节走，然后用本代码使关节的世界矩阵乘模型上组的世界逆矩阵，得出每个关节相对root的局部矩阵给蒙皮节点
    由于模型被root控制器拉到root关节所在位置处，所以即便绑定发生在原点，关节给到蒙皮的变换也是局部，但模型的变形位置还是在root关节所在位置
    :param objs:要修改的蒙皮模型（有其他东西也行，会被清除掉）
    :return:
    """
    jnt_lis = []
    for obj in objs:
        if mm.eval('findRelatedSkinCluster("{}")'.format(obj)):
            skin = mm.eval('findRelatedSkinCluster("{}")'.format(obj))
            for jnt in mc.skinCluster(skin, inf=1, q=1):  #从蒙皮节点名得到受影响的关节
                if jnt not in jnt_lis:
                    jnt_lis.append(jnt)

    if jnt_lis:
        for jnt in jnt_lis:
            plug_lis = mc.listConnections('{}.worldMatrix'.format(jnt), s=False, p=True)
            multMat = mc.createNode('multMatrix', n='multMat_{}_{:03d}'.format(jnt, 1))
            mc.connectAttr(jnt + '.worldMatrix[0]', multMat + '.matrixIn[0]')
            mc.connectAttr('Geometry.worldInverseMatrix[0]', multMat + '.matrixIn[1]')
            for plug in plug_lis:
                mc.connectAttr(multMat + '.matrixSum', plug, f=True)

    fb_print('解决完成', info=True, viewMes=True)


def closeSkinPrecision():
    """
    将场景里所有被解决精度操作过的蒙皮还原效果
    :return:
    """
    for mult in mc.ls(typ='multMatrix'):
        skin_lis = mc.listConnections(mult + '.matrixSum', s=False, t='skinCluster')
        if skin_lis:
            for skin_attr in mc.listConnections(mult + '.matrixSum', s=False, t='skinCluster', p=True):
                for jnt_attr in mc.listConnections(mult, d=False, t='joint', p=True):
                    mc.connectAttr(jnt_attr, skin_attr, f=1)
            fb_print('已解决矩阵乘除节点{}'.format(mult), info=True)


def list_operation(list_a, list_b, operation='|'):
    """
    通过不同符号返回两个列表的元素差异
    :param list_a:一个列表
    :param list_b:另一个列表
    :param operation:区分差异的符号，|：并集；&：交集；-：a列表减b列表的元素；^：a列表与b列表互相没有的元素
    :return:list
    """
    if not list_a:
        list_a = []
    if not list_b:
        list_b = []

    set_a = set(list_a)
    set_b = set(list_b)

    if operation == '|':
        return list(set_a.union(set_b))  #返回a与b的并集
    elif operation == '&':
        return list(set_a.intersection(set_b))  #返回a与b的交集
    elif operation == '-':
        return list(set_a.difference(set_b))  #a有而b没有的元素列表
    elif operation == '^':
        return list(set_a.symmetric_difference(set_b))  #返回a与b互不相同的元素
