# coding=gbk
import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as om
import maya.OpenMayaAnim as omain

from dutils import apiUtils
from feedback_tool import Feedback_info as fb_print, LIN as lin

reload(apiUtils)
FILE_PATH = __file__


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
                fb_print('��ɾ���ռ���{}��'.format(ns), info=True)
            except:
                fb_print('��ռ���{}��ɾ��ʧ�ܡ�'.format(ns), error=True)
        clear_nameSpace()
    else:
        fb_print('�������������пռ�����', info=True)
        return False


def clear_key():
    '''
    ɾ�����������йؼ�֡
    '''
    sel_lis = mc.ls(sl=True)
    mc.select('persp')
    mm.eval('doClearKeyArgList 3 { "1","0:10","keys","none","0","1","0","1","animationList","0","noOptions","0","0" };')
    fb_print('��ɾ�����������йؼ�֡��', info=True)
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
            fb_print('��ɾ��HIK{}��'.format(hik), info=True)
    else:
        fb_print('������û��HIK��', info=True)
    return False


def clear_animLayer():
    '''
    ɾ�����������ж�����
    '''
    for ani in mc.ls(type='animLayer'):
        try:
            mc.delete(ani)
            fb_print('��ɾ��������{}��'.format(ani), info=True)
        except:
            fb_print('������{}ɾ��ʧ�ܣ���������Ϊ������������Ӽ���������ɾ������ʱ�Զ�ɾ�����Ӽ��㡣'.format(ani), warning=True)
    fb_print('��ɾ�����ж�����', info=True)
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
        fb_print("������������{}����{}".format(error_lis.__len__() / 2, ', '.join(error_lis)), info=True)
        return True
    fb_print("������û�������������", info=True)
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
            fb_print('��Ƥ�ڵ�{}�ı���Ƥ������{}���͵�{}��������'.format(fn.name(), apiUtils.get_skinModelType(fn),
                                                                        ','.join(apiUtils.get_skinModelName(fn))),
                     warning=True)
    else:
        if error_dir:
            fb_print('����Ȩ�ز�Ϊ1�ĵ��У�{}'.format(''.join(
                ['\n{}.vtx[{}]'.format(mod, ','.join(vtx_lis)) for mod, vtx_lis in error_dir.items()])),
                info=True, viewMes=True)
            return True
        else:
            fb_print('����������ģ�͵ĵ�Ȩ�ض�����Ϊ1', info=True, viewMes=True)
            return False
