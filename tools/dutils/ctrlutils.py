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
    通过获取服务器路径里控制器库的信息来创建控制器本身
    :param id: 要创建的控制器形状的id名
    :param nam: 控制器的trs名
    :return: 创建的控制器的trs名
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
        fb_print('控制器库路径不存在，请将电脑链接到服务器。', error=True, path=FILE_PATH, line=lin())


def replace_controller_shape(ctl_lis, id=None, color=None):
    '''
    将一个曲线的所有shape替换成另一个曲线的shape
    :param color: 是否给替换的新shape加颜色
    :param ctl_lis: 曲线的trs列表
    :param id: 要替换成的控制器库id
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
    将曲线的shape的颜色改变为指定颜色
    :param ctl_lis: 控制器的trs列表
    :param args: 要改变的rgb或者下标颜色，通过传入的信息数量判断是rgb还是下标
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
                fb_print('节点{}改变颜色时传参错误。'.format(ctl), warning=True)

    if type(ctl_lis) == 'list':
        for ctl in ctl_lis:
            set_color(ctl, *args)
    else:
        set_color(ctl_lis, *args)


def fromObjCreateGroup(name,  typ='ctl', *objs):
    """
    通过传入名称，对象，类型批量在对象上创建组
    :param name: 对象名
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
