# -*- coding:GBK -*-
import maya.cmds as mc

from feedback_tool import Feedback_info as fb_print


def get_core(get_pos=False, to_typ = 'locator'):
    """
    在选择对象的中心创建定位器。
    """
    obj_lis = mc.ls(sl=1, fl=1)

    if len(obj_lis) == 0:
        loc = mc.spaceLocator()[0]
        fb_print('已在原点创建定位器{}'.format(loc), info=True)
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
            fb_print('未知的节点类型', error=True, path=True)
        mc.matchTransform(loc, clst)
        if get_pos:
            pos = mc.xform(loc, q=True, ws=True, t=True)
            mc.delete(loc, clst, crv)
            return pos
        else:
            mc.delete(crv, clst)
            fb_print('已在选择对象的中心创建定位器{}'.format(loc), info=True)
            return loc


def create_joint():
    '''
    创建关节到目标位置并匹配旋转
    如果没有选择对象，则创建在原点
    '''
    sel_lis = mc.ls(sl=True)
    if len(sel_lis) == 1:
        mc.select(cl=True)
        jnt = mc.joint()
        mc.matchTransform(jnt, sel_lis[0], pos=True, rot=True)
        fb_print('已创建关节{}到{}中心并匹配旋转。'.format(jnt, sel_lis[0]), info=True)
    else:
        fb_print('应选择1个对象，实际为{}个。'.format(len(sel_lis)), error=True)


def get_jnt_core():
    '''
    在选择对象的中心创建关节。
    '''
    obj_lis = mc.ls(sl=1, fl=1)
    if len(obj_lis) == 0:
        mc.joint(p=[0, 0, 0])
        fb_print('已在原点创建关节。', info=True)
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

        fb_print('已在选择对象的中心创建关节{}'.format(jnt), info=True)
        return jnt


def get_trm_rot():
    '''
    创建定位器到选择对象的中心并匹配旋转
    '''
    obj = mc.ls(sl=True)
    if obj.__len__() == 1:
        mc.matchTransform(mc.spaceLocator(), obj[0], pos=True, rot=True)
        fb_print('已在{}位置上创建定位器并匹配'.format(obj[0]), info=True)
    else:
        fb_print('应选择1个对象，实际选择{}个对象。'.format(obj.__len__()), error=True)


def allMatchOne():
    '''
    将选择列表中所有对象的位移匹配到最后一个选择对象。
    '''
    sel_lis = mc.ls(sl=True, fl=1)
    if len(sel_lis) < 2:
        fb_print('选择对象应不少于2个，实际为{}个。'.format(len(sel_lis)), error=True)
        return False
    else:
        obj_target = sel_lis[-1]
        for i in range(0, len(sel_lis) - 1):
            mc.matchTransform(sel_lis[i], obj_target, pos=True, rot=True, scl=True)
            fb_print('已将{}匹配到{}。'.format(sel_lis[i], obj_target), info=True)


def oneMatchAll(set_attr=False, *args):
    """
    将选择列表中所有对象的位移旋转缩放匹配到第一个选择对象。
    """
    if args:
        sel_lis = args
    else:
        sel_lis = mc.ls(sl=True, fl=1)

    if len(sel_lis) < 2:
        fb_print('选择对象应不少于2个，实际为{}个。'.format(len(sel_lis)), error=True)
    else:
        tag_obj = sel_lis[-1]
        pos_obj = sel_lis[:-1]
        mc.select(pos_obj)
        loc = get_core()
        mc.matchTransform(tag_obj, loc)
        mc.delete(loc)
        fb_print('已将{}匹配到对象。'.format(tag_obj), info=True)
        return tag_obj, pos_obj

    if set_attr:
        pass
