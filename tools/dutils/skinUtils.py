# coding=gbk
import maya.cmds as mc
import maya.mel as mm

from feedback_tool import Feedback_info as fb_print, LIN as lin


def processingSkinPrecision(objs):
    """
    �������ԭ��̫Զ��ʧ���ȶ�Ť��
    ��ģ���ϲ�������root�ؽ��ߣ�Ȼ���ñ�����ʹ�ؽڵ���������ģ���������������󣬵ó�ÿ���ؽ����root�ľֲ��������Ƥ�ڵ�
    ����ģ�ͱ�root����������root�ؽ�����λ�ô������Լ���󶨷�����ԭ�㣬�ؽڸ�����Ƥ�ı任Ҳ�Ǿֲ�����ģ�͵ı���λ�û�����root�ؽ�����λ��
    :param args:Ҫ�޸ĵ���Ƥģ�ͣ�����������Ҳ�У��ᱻ�������
    :return:
    """
    jnt_lis = []
    for obj in objs:
        if mm.eval('findRelatedSkinCluster("{}")'.format(obj)):
            skin = mm.eval('findRelatedSkinCluster("{}")'.format(obj))
            for jnt in mc.skinCluster(skin, inf=1, q=1):  #����Ƥ�ڵ����õ���Ӱ��Ĺؽ�
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

    fb_print('������', info=True, viewMes=True)
