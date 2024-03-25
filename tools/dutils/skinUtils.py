# coding=gbk
import maya.cmds as mc
import maya.mel as mm

from feedback_tool import Feedback_info as fb_print

FILE_PATH = __file__


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
    在同一个模型上将一堆关节的权重给到某一个关节
    outSkin_lis:要输出权重的关节列表
    obtain_jnt：要获取权重的关节
    mod_lis：要改变权重的模型
    delete：是否删除输出权重的关节
    '''
    cluster = mm.eval('findRelatedSkinCluster("{}")'.format(mod))
    infJnt_lis = mc.skinCluster(cluster, inf=True, q=True)  #获取所有该蒙皮节点影响的关节

    for jnt in infJnt_lis:
        mc.setAttr('{}.liw'.format(jnt), True)  #锁住该蒙皮节点下所有关节的权重

    if obtain_jnt not in infJnt_lis:
        mc.skinCluster(cluster, e=1, lw=1, wt=0, ai=obtain_jnt)
    mc.setAttr('{}.liw'.format(obtain_jnt), False)#只解锁获取权重关节

    for jnt in outSkin_lis:  # 将每个关节的权重都反向给到脖子关节
        mc.select(mod)  #传递关节权重需要指定实际对象，选择或者在skinPercent的蒙皮节点名后加上模型的trs名也行
        if jnt in infJnt_lis:
            mc.setAttr('{}.liw'.format(jnt), False)
            mc.skinPercent(cluster, tv=[(jnt, 0)])
            mc.skinCluster(cluster, e=True, ri=jnt)
        else:
            fb_print('{}不在蒙皮中'.format(jnt), warning=True, path=True)

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
