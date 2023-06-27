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
    ��ѡ�е�ģ���б����α��� �����orig�ڵ��ɾ��
    :return:
    """
    sel_lis = mc.ls(sl=1)
    for obj in sel_lis:
        for sub_node in mc.listRelatives(obj, s=True):
            if 'Orig' in sub_node and mc.nodeType(sub_node) == 'mesh':
                mc.delete(sub_node)
                fb_print('ģ��{}��orig�ڵ�{}��ɾ����'.format(obj, sub_node), info=True)
                continue


def goToADV_pose():
    """
    ʹ�����ڵ�adv��buildPose�ڵ㴢��Ķ��󶼻ع�ԭλ
    :return:
    """
    if mc.objExists('buildPose'):
        mel_str = mc.getAttr('buildPose.udAttr')
        for order in mel_str.split(';'):
            if order:
                if order.split(' ')[-1][0].isalpha() and mc.objExists(order.split(' ')[-1]):
                    mm.eval(order)
        fb_print('adv�������ѻع�ԭλ��', info=True, viewMes=True)
    else:
        fb_print('������û��adv��buildPose�ڵ�', error=True)


def getShape(nodes, getTrs=False, q=False, typ=''):
    """
    ��������ʲô���ͣ�ͨ�������shape�ڵ�������������
    :param typ: Ҫ���ص�����
    :param q: Ϊtrueʱֻ����typ����ָ��������
    :param getTrs:True���ض���shape��������false���ض���trs��
    :param nodes:Ҫ���Ķ���
    :return:list
    """
    if q and typ not in ['mesh', 'nurbsCurve', 'nurbsSurface', 'lattice', 'locator', 'joint']:
        fb_print('typ����û��ָ����Ч����', error=True)

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
            fb_print('����{}�ǲ�֧�ֵ�����'.format(node), warning=True)
    if rtn_lis:
        return rtn_lis
    else:
        return None


def fromClosestPointGetUv(geo, tag_geo):
    """
    ��ȡgeo����tagGeo������uvֵ
    :param geo: Ҫ��ȡuvֵ��ģ��
    :param tag_geo: �����Ŀ��ģ��
    :return:geo����tat_geo������uvֵ
    """
    unit = mc.currentUnit(q=True)
    mc.currentUnit(l='cm')

    geo_shpae = getShape(geo)
    if not geo_shpae:
        fb_print('����{}û��shape�ڵ�'.format(geo), error=True)

    geo_dag = apiUtils.getDagPath(geo)
    poj_pos = apiUtils.getMPoint(tag_geo)

    uv = None
    shape_typ = mc.objectType(geo_shpae)
    if shape_typ == 'mesh':
        fm_geo = oma.MFnMesh(geo_dag)
        uv = fm_geo.getUVAtPoint(poj_pos, space=oma.MSpace.kWorld)[:-1]  #���ص���uv��faceId
    elif shape_typ == 'nurbsSurface':
        fm_geo = oma.MFnNurbsSurface(geo_dag)
        cpos_node = mc.createNode('closestPointOnSurface', n='cloOnSur{}_{:03d}'.format(geo, 1))
        mc.connectAttr('{}.worldSpace[0]'.format(geo_shpae), '{}.inputSurface'.format(cpos_node))
        mc.connectAttr('{}.translate'.format(tag_geo), '{}.inPosition'.format(cpos_node))
        pos = mc.getAttr('{}.position'.format(cpos_node))[0]  #��ȡ��tag_geo��Ӧ���������ϵ�λ�ã�Ҫ��tag_geo���������ͬһ��������
        mc.delete(cpos_node)

        result_pos = oma.MPoint(pos[0], pos[1], pos[2], 1.0)  #��xyz��ϳ�mpoint����
        pu, pv = fm_geo.getParamAtPoint(result_pos, ignoreTrimBoundaries=False, tolerance=0.01, space=oma.MSpace.kWorld)

        uv = (pu / fm_geo.numSpansInU, pv / fm_geo.numSpansInV)
    mc.currentUnit(l=unit)

    return uv


def processingSkinPrecision(objs):
    """
    �������ԭ��̫Զ��ʧ���ȶ�Ť��
    ��ģ���ϲ�������root�ؽ��ߣ�Ȼ���ñ�����ʹ�ؽڵ���������ģ���������������󣬵ó�ÿ���ؽ����root�ľֲ��������Ƥ�ڵ�
    ����ģ�ͱ�root����������root�ؽ�����λ�ô������Լ���󶨷�����ԭ�㣬�ؽڸ�����Ƥ�ı任Ҳ�Ǿֲ�����ģ�͵ı���λ�û�����root�ؽ�����λ��
    :param objs:Ҫ�޸ĵ���Ƥģ�ͣ�����������Ҳ�У��ᱻ�������
    :return:
    """
    jnt_lis = []
    for obj in objs:
        if mm.eval('findRelatedSkinCluster("{}")'.format(obj)):
            skin = mm.eval('findRelatedSkinCluster("{}")'.format(obj))
            for jnt in mc.skinCluster(skin, inf=1, q=1):  #����Ƥ�ڵ����õ���Ӱ��Ĺؽ�
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

    fb_print('������', info=True, viewMes=True)


def closeSkinPrecision():
    """
    �����������б�������Ȳ���������Ƥ��ԭЧ��
    :return:
    """
    for mult in mc.ls(typ='multMatrix'):
        skin_lis = mc.listConnections(mult + '.matrixSum', s=False, t='skinCluster')
        if skin_lis:
            for skin_attr in mc.listConnections(mult + '.matrixSum', s=False, t='skinCluster', p=True):
                for jnt_attr in mc.listConnections(mult, d=False, t='joint', p=True):
                    mc.connectAttr(jnt_attr, skin_attr, f=1)
            fb_print('�ѽ������˳��ڵ�{}'.format(mult), info=True)


def list_operation(list_a, list_b, operation='|'):
    """
    ͨ����ͬ���ŷ��������б��Ԫ�ز���
    :param list_a:һ���б�
    :param list_b:��һ���б�
    :param operation:���ֲ���ķ��ţ�|��������&��������-��a�б��b�б��Ԫ�أ�^��a�б���b�б���û�е�Ԫ��
    :return:list
    """
    if not list_a:
        list_a = []
    if not list_b:
        list_b = []

    set_a = set(list_a)
    set_b = set(list_b)

    if operation == '|':
        return list(set_a.union(set_b))  #����a��b�Ĳ���
    elif operation == '&':
        return list(set_a.intersection(set_b))  #����a��b�Ľ���
    elif operation == '-':
        return list(set_a.difference(set_b))  #a�ж�bû�е�Ԫ���б�
    elif operation == '^':
        return list(set_a.symmetric_difference(set_b))  #����a��b������ͬ��Ԫ��
