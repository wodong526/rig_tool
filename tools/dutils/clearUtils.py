# coding=gbk
import maya.cmds as mc
import maya.mel as mm
import pymel.core as pm
import maya.OpenMayaUI as omui

import traceback

from feedback_tool import Feedback_info as fb_print, LIN as len

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

def clear_key():
    '''
    ɾ�����������йؼ�֡
    '''
    sel_lis = mc.ls(sl=True)
    mc.select('persp')
    mm.eval('doClearKeyArgList 3 { "1","0:10","keys","none","0","1","0","1","animationList","0","noOptions","0","0" };')
    fb_print('��ɾ�����������йؼ�֡��', info=True)
    mc.select(sel_lis)

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