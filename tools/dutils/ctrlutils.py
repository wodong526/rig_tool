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
    通过获取服务器路径里控制器库的信息来创建控制器本身
    :param color: 要给定的颜色
    :param num: 要创建的数量
    :param cid: 要创建的控制器形状的id名
    :param nam: 控制器的trs名
    :return: 创建的控制器的trs名
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
        fb_print('控制器库路径不存在，请将电脑链接到服务器。', error=True, path=FILE_PATH, line=lin())


def replace_controller_shape(ctl_lis, cid=None, color=None):
    """
    将一个曲线的所有shape替换成另一个曲线的shape
    :param color: 是否给替换的新shape加颜色
    :param ctl_lis: 曲线的trs列表
    :param cid: 要替换成的控制器库id
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
    将曲线的shape的颜色改变为指定颜色
    :param ctl_lis: 控制器的trs列表
    :param args: 要改变的rgb或者下标颜色，通过传入的信息数量判断是rgb还是下标
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
                fb_print('节点{}改变颜色时传参错误。'.format(ctl), warning=True)

    if type(ctl_lis) == 'list':
        for ctl in ctl_lis:
            set_color(ctl, *args)
    else:
        set_color(ctl_lis, *args)


def fromObjCreateGroup(objs, name='', num=1, rename_ctl=True):
    """
    通过传入名称，对象，类型批量在对象上创建组
    :param rename_ctl: 是否将对象的名字也改成规范模式
    :param num: 每个控制器创建的个数
    :param name: 生成的组的主要名字
    :param objs:要生成组的对象
    :return:
    """
    zero_lis = []
    obj_lis = []
    if type(objs) == list:
        pass
    elif type(objs) == str or type(objs) == unicode:
        objs = [objs]
    else:
        fb_print('该函数只接受字符串列表或字符串类型，实际传入{}类型'.format(type(objs)), error=True)

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
