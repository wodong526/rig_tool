# coding=gbk
import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as om
import maya.OpenMayaAnim as omain

from dutils import apiUtils
from feedback_tool import Feedback_info as fp


def clear_nameSpace(q=False):
    """
    ɾ�����������пռ���
    """
    nsLs = mc.namespaceInfo(lon=True)
    defaultNs = ["UI", "shared", "mod"]
    pool = [item for item in nsLs if item not in defaultNs]
    if pool and q:
        return True, pool
    elif not pool and q:
        return False, []
    elif pool and not q:
        for ns in pool:
            try:
                mc.namespace(rm=ns, mnr=1, f=1)
                fp('��ɾ���ռ���{}��'.format(ns), info=True)
            except:
                fp('��ռ���{}��ɾ��ʧ�ܡ�'.format(ns), error=True)
        clear_nameSpace()
    else:
        fp('�������������пռ�����', info=True)
        return False


def clear_key():
    '''
    ɾ�����������йؼ�֡
    '''
    sel_lis = mc.ls(sl=True)
    mc.select('persp')
    mm.eval('doClearKeyArgList 3 { "1","0:10","keys","none","0","1","0","1","animationList","0","noOptions","0","0" };')
    fp('��ɾ�����������йؼ�֡��', info=True)
    mc.select(sel_lis)
    return False


def clear_hik():
    '''
    ɾ������������hik
    '''
    hik_lis = mc.ls(typ='HIKCharacterNode')
    if hik_lis:
        for hik in hik_lis:
            del_lis = mc.listConnections(hik, d=False)
            mc.delete(del_lis)
            fp('��ɾ��HIK{}��'.format(hik), info=True)
    else:
        fp('������û��HIK��', info=True)
    return False


def clear_animLayer():
    '''
    ɾ�����������ж�����
    '''
    for ani in mc.ls(type='animLayer'):
        try:
            mc.delete(ani)
            fp('��ɾ��������{}��'.format(ani), info=True)
        except:
            fp('������{}ɾ��ʧ�ܣ���������Ϊ������������Ӽ���������ɾ������ʱ�Զ�ɾ�����Ӽ��㡣'.format(ani), warning=True)
    fp('��ɾ�����ж�����', info=True)
    return False


def clear_name():
    """
    ��ѯ���������е�����
    """
    error_lis = []
    sel_lis = mc.ls()
    for obj in sel_lis:
        if '|' in obj:
            error_lis.append(obj)

    if error_lis:
        fp("������������{}����{}".format(error_lis.__len__() / 2, ', '.join(error_lis)), info=True)
        return True
    fp("������û�������������", info=True)
    return False


def inspect_weight():
    """
    �����Ƥģ�͸������Ȩ�غ��Ƿ�Ϊ1�����в�����Ϊ1ʱ����
    :return:
    """
    error_dir = {}

    for skin in mc.ls(typ='skinCluster'):
        mobject = apiUtils.getApiNode(skin, dag=False)
        fn = omain.MFnSkinCluster(mobject)
        if apiUtils.get_skinModelType(fn) == 'mesh':  #�����Ƥ�ڵ㱻��Ƥ�����Ƿ�Ϊģ��
            dagPath, components = apiUtils.getGeometryComponents(fn)  #��ȡ��Ƥ�ڵ���Ƥ�������Ϣ
            weights = apiUtils.getCurrentWeights(fn, dagPath, components)  #��ȡȨ���б���1.�ؽ�1����1.�ؽ�2����2.�ؽ�1����2�ؽ�2��������
            influencePaths = om.MDagPathArray()
            fn.influenceObjects(influencePaths)  #��Ƥ�ؽڶ���datPath����

            for i in range(0, len(weights), influencePaths.length()):  #���������ܳ��ȣ�����Ϊ��Ƥ�ؽ�������ÿ��i����ÿ����ĵ�һ����Ƥ�ؽ��±�
                weight = 0.0
                for n in range(influencePaths.length()):
                    weight += weights[i + n]

                if round(weight, 5) != 1.0:  #ȡС�������λ����
                    skin_mod = apiUtils.get_skinModelName(fn)[0]
                    if skin_mod in error_dir.keys():
                        error_dir[skin_mod].append(str(i / 2))
                    else:
                        error_dir[skin_mod] = [str(i / 2)]
        else:
            fp('��Ƥ�ڵ�{}�ı���Ƥ������{}���͵�{}��������'.format(fn.name(), apiUtils.get_skinModelType(fn),
                                                                        ','.join(apiUtils.get_skinModelName(fn))),
                     warning=True)
    else:
        if error_dir:
            fp('����Ȩ�ز�Ϊ1�ĵ��У�{}'.format(''.join(
                ['\n{}.vtx[{}]'.format(mod, ','.join(vtx_lis)) for mod, vtx_lis in error_dir.items()])),
                info=True, viewMes=True)
            return True
        else:
            fp('����������ģ�͵ĵ�Ȩ�ض�����Ϊ1', info=True, viewMes=True)
            return False

def clear_unknown_node():
    """
    ����δ֪�ڵ�
    :return:����󳡾��е�δ֪�ڵ�
    """
    nuk_lis = mc.ls(typ='unknown')
    if nuk_lis:
        for node in nuk_lis:
            if mc.objExists(node):
                mc.lockNode(node, l=False)
                mc.delete(node)
                fp('������δ֪�ڵ�{}'.format(node), info=True)

    return mc.ls(typ='unknown')

def clear_unknown_plug():
    """
    ����δ֪���
    :return: ����󳡾��е�δ֪���
    """
    [mc.unknownPlugin(p, r=True) for p in mc.unknownPlugin(q=True, l=True)] if mc.unknownPlugin(q=True, l=True) else None


    return mc.unknownPlugin(q=True, l=True)
