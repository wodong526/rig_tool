# coding=gbk
import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui

import os

import data_path
from feedback_tool import Feedback_info as fb_print, LIN as lin

FILE_PATH = __file__


def create_ctl(nam, num=1, cid='D00', color=None):
    """
    ͨ����ȡ������·��������������Ϣ����������������
    :param color: Ҫ��������ɫ
    :param num: Ҫ����������
    :param cid: Ҫ�����Ŀ�������״��id��
    :param nam: ��������trs��
    :return: �����Ŀ�������trs��
    """
    ctl_path = data_path.controllerFilesDataPath
    if os.path.exists(ctl_path):
        ctl_lis = []
        for i in range(num):
            with open('{}{}.cs'.format(ctl_path, cid), 'r') as f:
                con = f.read()
            trs = mc.createNode('transform', n='ctrl_{}_{:03d}'.format(nam, i + 1))
            shape = mc.createNode('nurbsCurve', n='{}Shape'.format(trs), p=trs)
            mm.eval(con)

            if color:
                add_curveShape_color(trs, color)

            if mc.objExists('Sets'):
                if 'AllSet' in mc.listConnections('Sets', d=False):
                    mc.sets(trs, e=True, fe='AllSet')
                    mc.sets(shape, e=True, fe='AllSet')
                if 'ControlSet' in mc.listConnections('Sets', d=False):
                    mc.sets(trs, e=True, fe='ControlSet')

            ctl_lis.append(trs)
        mc.select(ctl_lis)
        if num != 1:
            return ctl_lis
        else:
            return ctl_lis[0]
    else:
        fb_print('��������·�������ڣ��뽫�������ӵ���������', error=True, path=FILE_PATH, line=lin())


def replace_controller_shape(ctl_lis, cid=None, color=None):
    """
    ��һ�����ߵ�����shape�滻����һ�����ߵ�shape
    :param color: �Ƿ���滻����shape����ɫ
    :param ctl_lis: ���ߵ�trs�б�
    :param cid: Ҫ�滻�ɵĿ�������id
    :return: None
    """

    def set_ctl(ctl, cid):
        ctl_nam = create_ctl('dub_ctl_AA', cid=cid, color=color)
        ctl_shape = mc.listRelatives(ctl_nam, s=True)[0]
        old_shape = mc.listRelatives(ctl, s=True)

        mc.parent(ctl_shape, ctl, add=True, s=True)
        mc.delete(old_shape)
        mc.rename(ctl_shape, old_shape[0])
        mc.delete(ctl_nam)

    if cid:
        if type(ctl_lis) == list:
            for ctl in ctl_lis:
                set_ctl(ctl, cid)
        else:
            set_ctl(ctl_lis, cid)


def add_curveShape_color(ctl_lis, *args):
    """
    �����ߵ�shape����ɫ�ı�Ϊָ����ɫ
    :param ctl_lis: ��������trs�б�
    :param args: Ҫ�ı��rgb�����±���ɫ��ͨ���������Ϣ�����ж���rgb�����±�
    :return: None
    """

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


def fromObjCreateGroup(objs, name='', num=1, rename_ctl=True):
    """
    ͨ���������ƣ��������������ڶ����ϴ�����
    :param rename_ctl: �Ƿ񽫶��������Ҳ�ĳɹ淶ģʽ
    :param num: ÿ�������������ĸ���
    :param name: ���ɵ������Ҫ����
    :param objs:Ҫ������Ķ���
    :return:
    """
    zero_lis = []
    obj_lis = []
    if type(objs) == list:
        pass
    elif type(objs) == str or type(objs) == unicode:
        objs = [objs]
    else:
        fb_print('�ú���ֻ�����ַ����б���ַ������ͣ�ʵ�ʴ���{}����'.format(type(objs)), error=True)

    for obj in objs:
        for i in range(num):
            i += 1
            pos = mc.xform(obj, t=True, q=True, ws=True)
            rot = mc.xform(obj, ro=True, q=True, ws=True)
            scl = mc.xform(obj, s=True, q=True, ws=True)

            if name:
                nam = name
            else:
                if len(obj.split('_')) >= 2:
                    nam = obj.split('_', 1)[1].rsplit('_', 1)[0]
                else:
                    nam = obj

            grp = mc.group(em=True, n='zero_{}_{:03d}'.format(nam, i), w=True)
            grpOffset = mc.group(em=True, p=grp, n='Offset_{}_{:03d}'.format(nam, i))
            mc.xform(grp, t=pos, ro=rot, s=scl, ws=True)
            if mc.listRelatives(obj, p=True):
                mc.parent(grp, mc.listRelatives(obj, p=True)[0])
            mc.parent(obj, grpOffset)
            if rename_ctl:
                ctl = mc.rename(obj, 'ctrl_{}_{:03d}'.format(nam, i))
                if mc.listRelatives(ctl, s=True):
                    mc.rename(mc.listRelatives(ctl, s=True)[0], '{}Shape'.format(ctl))

            zero_lis.append(grp)
            obj_lis.append(obj)
            mc.select(grp)

    if len(zero_lis) == 1:
        return zero_lis[0], obj_lis[0]
    else:
        return zero_lis, obj_lis
