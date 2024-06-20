# -*- coding:GBK -*-
import maya.cmds as mc

from feedback_tool import Feedback_info as fb_print


def get_core(get_pos=False, to_typ = 'locator'):
    """
    ��ѡ���������Ĵ�����λ����
    """
    obj_lis = mc.ls(sl=1, fl=1)

    if len(obj_lis) == 0:
        loc = mc.spaceLocator()[0]
        fb_print('����ԭ�㴴����λ��{}'.format(loc), info=True)
    else:
        pos_lis = []
        for obj in obj_lis:
            pos_lis.append(mc.xform(obj, ws=True, q=True, t=True))

        crv = mc.curve(d=1, p=pos_lis)
        clst = mc.cluster()
        if to_typ == 'locator':
            loc = mc.spaceLocator()[0]
        elif to_typ == 'joint':
            loc = mc.createNode('joint')
        else:
            fb_print('δ֪�Ľڵ�����', error=True, path=True)
        mc.matchTransform(loc, clst)
        if get_pos:
            pos = mc.xform(loc, q=True, ws=True, t=True)
            mc.delete(loc, clst, crv)
            return pos
        else:
            mc.delete(crv, clst)
            fb_print('����ѡ���������Ĵ�����λ��{}'.format(loc), info=True)
            return loc


def create_joint():
    '''
    �����ؽڵ�Ŀ��λ�ò�ƥ����ת
    ���û��ѡ������򴴽���ԭ��
    '''
    sel_lis = mc.ls(sl=True)
    if len(sel_lis) == 1:
        mc.select(cl=True)
        jnt = mc.joint()
        mc.matchTransform(jnt, sel_lis[0], pos=True, rot=True)
        fb_print('�Ѵ����ؽ�{}��{}���Ĳ�ƥ����ת��'.format(jnt, sel_lis[0]), info=True)
    else:
        fb_print('Ӧѡ��1������ʵ��Ϊ{}����'.format(len(sel_lis)), error=True)


def get_jnt_core():
    '''
    ��ѡ���������Ĵ����ؽڡ�
    '''
    obj_lis = mc.ls(sl=1, fl=1)
    if len(obj_lis) == 0:
        mc.joint(p=[0, 0, 0])
        fb_print('����ԭ�㴴���ؽڡ�', info=True)
    else:
        pos_lis = []
        for obj in obj_lis:
            pos_lis.append(mc.xform(obj, ws=True, q=True, t=True))

        crv = mc.curve(d=1, p=pos_lis)
        clst = mc.cluster()
        mc.select(cl=True)
        jnt = mc.joint()
        mc.matchTransform(jnt, clst)
        mc.delete(crv, clst)

        fb_print('����ѡ���������Ĵ����ؽ�{}'.format(jnt), info=True)
        return jnt


def get_trm_rot():
    '''
    ������λ����ѡ���������Ĳ�ƥ����ת
    '''
    obj = mc.ls(sl=True)
    if obj.__len__() == 1:
        mc.matchTransform(mc.spaceLocator(), obj[0], pos=True, rot=True)
        fb_print('����{}λ���ϴ�����λ����ƥ��'.format(obj[0]), info=True)
    else:
        fb_print('Ӧѡ��1������ʵ��ѡ��{}������'.format(obj.__len__()), error=True)


def allMatchOne():
    '''
    ��ѡ���б������ж����λ��ƥ�䵽���һ��ѡ�����
    '''
    sel_lis = mc.ls(sl=True, fl=1)
    if len(sel_lis) < 2:
        fb_print('ѡ�����Ӧ������2����ʵ��Ϊ{}����'.format(len(sel_lis)), error=True)
        return False
    else:
        obj_target = sel_lis[-1]
        for i in range(0, len(sel_lis) - 1):
            mc.matchTransform(sel_lis[i], obj_target, pos=True, rot=True, scl=True)
            fb_print('�ѽ�{}ƥ�䵽{}��'.format(sel_lis[i], obj_target), info=True)


def oneMatchAll(set_attr=False, *args):
    """
    ��ѡ���б������ж����λ����ת����ƥ�䵽��һ��ѡ�����
    """
    if args:
        sel_lis = args
    else:
        sel_lis = mc.ls(sl=True, fl=1)

    if len(sel_lis) < 2:
        fb_print('ѡ�����Ӧ������2����ʵ��Ϊ{}����'.format(len(sel_lis)), error=True)
    else:
        tag_obj = sel_lis[-1]
        pos_obj = sel_lis[:-1]
        mc.select(pos_obj)
        loc = get_core()
        mc.matchTransform(tag_obj, loc)
        mc.delete(loc)
        fb_print('�ѽ�{}ƥ�䵽����'.format(tag_obj), info=True)
        return tag_obj, pos_obj

    if set_attr:
        pass
