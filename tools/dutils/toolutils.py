# coding=gbk
import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui

from feedback_tool import Feedback_info as fb_print, LIN as lin

FILE_PATH = __file__


def clear_orig():
    """
    将选中的模型列表依次遍历 如果有orig节点就删除
    :return:
    """
    sel_lis = mc.ls(sl=1)
    for obj in sel_lis:
        for sub_node in mc.listHistory(obj):
            if 'Orig' in sub_node and mc.nodeType(sub_node) == 'mesh':
                mc.delete(sub_node)
                fb_print('模型{}的orig节点{}已删除。'.format(obj, sub_node), info=True)
                continue


def goToADV_pose():
    '''
    使场景内的adv的buildPose节点储存的对象都回归原位
    :return:
    '''
    if mc.objExists('buildPose'):
        mel_str = mc.getAttr('buildPose.udAttr')
        for order in mel_str.split(';'):
            if order:
                if order.split(' ')[-1][0].isalpha() and mc.objExists(order.split(' ')[-1]):
                    mm.eval(order)
        fb_print('adv控制器已回归原位。', info=True, viewMes=True)
    else:
        fb_print('场景内没有adv的buildPose节点', error=True)


def add_skinJnt(clster, *joints):
    '''
    将关节添加进某蒙皮节点中
    :param clster: 被添加蒙皮关节的蒙皮节点
    :param joints: 要被添加进蒙皮节点的关节
    :return: None
    '''
    infJnt_lis = mc.skinCluster(clster, inf=True, q=True)
    for jnt in joints:
        if jnt not in infJnt_lis:
            mc.skinCluster(clster, e=True, lw=True, wt=0, ai=jnt)


def transform_jnt_skin(outSkin_lis, obtain_jnt, mod, delete=False):
    '''
    outSkin_lis:要输出权重的关节列表
    obtain_jnt：要获取权重的关节
    mod_lis：要改变权重的模型
    delete：是否删除输出权重的关节
    '''
    cluster = mm.eval('findRelatedSkinCluster("{}")'.format(mod))
    infJnt_lis = mc.skinCluster(cluster, inf=True, q=True)  #获取所有该蒙皮节点影响的关节

    for jnt in infJnt_lis:
        mc.setAttr('{}.liw'.format(jnt), True)  #锁住该蒙皮节点下所有关节的权重
    mc.setAttr('{}.liw'.format(obtain_jnt), False)

    for jnt in outSkin_lis:  # 将每个关节的权重都反向给到脖子关节
        mc.select(mod)  #传递关节权重需要指定实际对象，选择或者在skinPercent的蒙皮节点名后加上模型的trs名也行
        if jnt in infJnt_lis:
            mc.setAttr('{}.liw'.format(jnt), False)
            mc.skinPercent(cluster, tv=[(jnt, 0)])
            mc.skinCluster(cluster, e=True, ri=jnt)
        else:
            fb_print('{}不在蒙皮中'.format(jnt), warning=True, path=FILE_PATH, line=lin())

        if delete:  #当关节不在世界下时放到世界下，将子级p给父级再把关节放到世界下，当关节在世界下时，当关节有子级时，将子级对象p到世界下
            if mc.listRelatives(jnt, p=True):
                if mc.listRelatives(jnt):
                    sub_obj = mc.listRelatives(jnt)
                    mc.parent(sub_obj, mc.listRelatives(jnt, p=True))
                mc.parent(jnt, w=True)
            else:
                if mc.listRelatives(jnt):
                    sub_obj = mc.listRelatives(jnt)
                    mc.parent(sub_obj, w=True)
            mc.delete(jnt)
    mc.setAttr('{}.liw'.format(obtain_jnt), True)


def createFollicle(geo, tag):
    """
    在geo（多边形或者曲面）上生成毛囊，毛囊位置为离tag对象最近的位置
    :param geo: 多边形或者曲面
    :param tag: 毛囊离它最近
    :return:
    """
    pass


def getShapeType(getTrs=False, q=False, typ='', *nodes):
    """
    检测对象是什么类型，通过对象的shape节点来检测对象类型
    :param typ: 要返回的类型
    :param q: 为true时只返回typ参数指定的类型
    :param getTrs:True返回对象shape类型名，false返回对象trs名
    :param nodes:要检测的对象
    :return:list
    """
    if q and typ not in ['mesh', 'nurbsCurve', 'nurbsSurface', 'lattice', 'locator']:
        fb_print('typ参数没有指定有效类型', error=True)

    rtn_lis = []
    for node in nodes:
        if mc.nodeType(node) == 'transform':
            shape = mc.listRelatives(node, s=True)
            if shape:
                if q and shape[0] == typ:
                    if getTrs:
                        rtn_lis.append(shape[0])
                    elif not getTrs:
                        rtn_lis.append(node)
                elif not q:
                    if getTrs:
                        rtn_lis.append(shape[0])
                    elif not getTrs:
                        rtn_lis.append(node)
            else:
                continue
        elif mc.nodeType(node) in ['mesh', 'nurbsCurve', 'nurbsSurface', 'lattice', 'locator']:
            if q and node == typ:
                if getTrs:
                    rtn_lis.append(node)
                elif not getTrs:
                    rtn_lis.append(mc.listRelatives(node, p=True)[0])
            elif not q:
                if getTrs:
                    rtn_lis.append(node)
                elif not getTrs:
                    rtn_lis.append(mc.listRelatives(node, p=True)[0])
