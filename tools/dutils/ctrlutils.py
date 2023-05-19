# coding=gbk
import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui

import os

import data_path
from feedback_tool import Feedback_info as fb_print, LIN as lin

FILE_PATH = __file__


def create_ctl(nam, num=1, id='D00', color=None):
    """
    ͨ����ȡ������·��������������Ϣ����������������
    :param id: Ҫ�����Ŀ�������״��id��
    :param nam: ��������trs��
    :return: �����Ŀ�������trs��
    """
    ctl_path = data_path.CONTROLLERFILES_PATH
    if os.path.exists(ctl_path):
        ctl_lis = []
        for i in range(num):
            with open('{}{}.cs'.format(ctl_path, id), 'r') as f:
                con = f.read()
            trs = mc.createNode('transform', n=nam)
            mc.createNode('nurbsCurve', n='{}Shape'.format(trs), p=trs)
            mm.eval(con)

            if color:
                add_curveShape_color(trs, color)
            ctl_lis.append(trs)
        if num != 1:
            return ctl_lis
        else:
            return ctl_lis[0]
    else:
        fb_print('��������·�������ڣ��뽫�������ӵ���������', error=True, path=FILE_PATH, line=lin())


def replace_controller_shape(ctl_lis, id=None, color=None):
    '''
    ��һ�����ߵ�����shape�滻����һ�����ߵ�shape
    :param color: �Ƿ���滻����shape����ɫ
    :param ctl_lis: ���ߵ�trs�б�
    :param id: Ҫ�滻�ɵĿ�������id
    :return: None
    '''

    def set_ctl(ctl, id):
        ctl_nam = create_ctl('dub_ctl_AA', id=id, color=color)
        ctl_shape = mc.listRelatives(ctl_nam, s=True)[0]
        old_shape = mc.listRelatives(ctl, s=True)

        mc.parent(ctl_shape, ctl, add=True, s=True)
        mc.delete(old_shape)
        mc.rename(ctl_shape, old_shape[0])
        mc.delete(ctl_nam)

    if id:
        if type(ctl_lis) == list:
            for ctl in ctl_lis:
                set_ctl(ctl, id)
        else:
            set_ctl(ctl_lis, id)


def add_curveShape_color(ctl_lis, *args):
    '''
    �����ߵ�shape����ɫ�ı�Ϊָ����ɫ
    :param ctl_lis: ��������trs�б�
    :param args: Ҫ�ı��rgb�����±���ɫ��ͨ���������Ϣ�����ж���rgb�����±�
    :return: None
    '''

    def set_color(ctl, *args):
        cv_shape_lis = mc.listRelatives(ctl, s=True)
        for shape in cv_shape_lis:
            mc.setAttr('{}.overrideEnabled'.format(shape), 1)
            if len(args) == 3:
                mc.setAttr('{}.overrideRGBColors'.format(shape), 1)
                mc.setAttr('{}.overrideColorRGB'.format(shape), args[0], args[1], args[2])
            elif len(args) == 1:
                mc.setAttr('{}.overrideRGBColors'.format(shape), 0)
                mc.setAttr('{}.overrideColor'.format(shape), args[0])
            else:
                fb_print('�ڵ�{}�ı���ɫʱ���δ���'.format(ctl), warning=True)

    if type(ctl_lis) == 'list':
        for ctl in ctl_lis:
            set_color(ctl, *args)
    else:
        set_color(ctl_lis, *args)


def fromObjCreateGroup(name,  typ='ctl', *objs):
    """
    ͨ���������ƣ��������������ڶ����ϴ�����
    :param name: ������
    :param objs:
    :param typ:
    :return:
    """
    zero_lis = []
    obj_lis = []
    i = 0
    for obj in objs:
        i += 1
        pos = mc.xform(obj, t=True, q=True, ws=True)
        rot = mc.xform(obj, ro=True, q=True, ws=True)
        scl = mc.xform(obj, s=True, q=True, ws=True)

        if typ == 'ctl':
            ctl_name = mc.rename(obj, 'ctl_{}_{:03d}'.format(name, i))
        elif typ == 'mod':
            ctl_name = mc.rename(obj, 'mod_{}_{:03d}'.format(name, i))

        mc.rename(mc.listRelatives(ctl_name, s=True)[0], '{}Shape'.format(ctl_name))
        grp = mc.group(em=True, n='zero_{}_{:03d}'.format(name, i), w=True)
        grpOffset = mc.group(em=True, p=grp, n='grpOffset_{}_{:03d}'.format(name, i))
        mc.xform(grp, t=pos, ro=rot, s=scl, ws=True)
        mc.parent(ctl_name, grpOffset)

        zero_lis.append(grp)
        obj_lis.append(ctl_name)
        mc.select(grp)

    return zero_lis, obj_lis
