# coding=gbk
import maya.cmds as mc
import maya.mel as mm

from feedback_tool import Feedback_info as fb_print, LIN as lin


def processingSkinPrecision(objs):
    """
    解决绑定离原点太远丢失精度而扭曲
    让模型上层的组跟着root关节走，然后用本代码使关节的世界矩阵乘模型上组的世界逆矩阵，得出每个关节相对root的局部矩阵给蒙皮节点
    由于模型被root控制器拉到root关节所在位置处，所以即便绑定发生在原点，关节给到蒙皮的变换也是局部，但模型的变形位置还是在root关节所在位置
    :param args:要修改的蒙皮模型（有其他东西也行，会被清除掉）
    :return:
    """
    jnt_lis = []
    for obj in objs:
        if mm.eval('findRelatedSkinCluster("{}")'.format(obj)):
            skin = mm.eval('findRelatedSkinCluster("{}")'.format(obj))
            for jnt in mc.skinCluster(skin, inf=1, q=1):  #从蒙皮节点名得到受影响的关节
                if jnt not in jnt_lis:
                    jnt_lis.append(jnt)

    if jnt_lis:
        for jnt in jnt_lis:
            plug_lis = mc.listConnections('{}.worldMatrix'.format(jnt), s=False, p=True)
            multMat = mc.createNode('multMatrix', n='multMat_{}_{:03d}'.format(jnt, 1))
            mc.connectAttr(jnt + '.worldMatrix[0]', multMat + '.matrixIn[0]')
            mc.connectAttr('Geometry.worldInverseMatrix[0]', multMat + '.matrixIn[1]')
            for plug in plug_lis:
                mc.connectAttr(multMat + '.matrixSum', plug, f=True)

    fb_print('解决完成', info=True, viewMes=True)
