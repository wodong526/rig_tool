# coding=gbk
import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui

from feedback_tool import Feedback_info as fb_print, LIN as lin

FILE_PATH = __file__

def clear_orig():
    """
    ��ѡ�е�ģ���б����α��� �����orig�ڵ��ɾ��
    :return:
    """
    sel_lis = mc.ls(sl=1)
    for obj in sel_lis:
        for sub_node in mc.listHistory(obj):
            if 'Orig' in sub_node and mc.nodeType(sub_node) == 'mesh':
                mc.delete(sub_node)
                fb_print('ģ��{}��orig�ڵ�{}��ɾ����'.format(obj, sub_node), info=True)
                continue


def goToADV_pose():
    '''
    ʹ�����ڵ�adv��buildPose�ڵ㴢��Ķ��󶼻ع�ԭλ
    :return:
    '''
    if mc.objExists('buildPose'):
        mel_str = mc.getAttr('buildPose.udAttr')
        for order in mel_str.split(';'):
            if order:
                if order.split(' ')[-1][0].isalpha() and mc.objExists(order.split(' ')[-1]):
                    mm.eval(order)
        fb_print('adv�������ѻع�ԭλ��', info=True, viewMes=True)
    else:
        fb_print('������û��adv��buildPose�ڵ�', error=True)


def add_skinJnt(clster, *joints):
    '''
    ���ؽ���ӽ�ĳ��Ƥ�ڵ���
    :param clster: �������Ƥ�ؽڵ���Ƥ�ڵ�
    :param joints: Ҫ����ӽ���Ƥ�ڵ�Ĺؽ�
    :return: None
    '''
    infJnt_lis = mc.skinCluster(clster, inf=True, q=True)
    for jnt in joints:
        if jnt not in infJnt_lis:
            mc.skinCluster(clster, e=True, lw=True, wt=0, ai=jnt)


def transform_jnt_skin(outSkin_lis, obtain_jnt, mod, delete=False):
    '''
    outSkin_lis:Ҫ���Ȩ�صĹؽ��б�
    obtain_jnt��Ҫ��ȡȨ�صĹؽ�
    mod_lis��Ҫ�ı�Ȩ�ص�ģ��
    delete���Ƿ�ɾ�����Ȩ�صĹؽ�
    '''
    cluster = mm.eval('findRelatedSkinCluster("{}")'.format(mod))
    infJnt_lis = mc.skinCluster(cluster, inf=True, q=True)  #��ȡ���и���Ƥ�ڵ�Ӱ��Ĺؽ�

    for jnt in infJnt_lis:
        mc.setAttr('{}.liw'.format(jnt), True)  #��ס����Ƥ�ڵ������йؽڵ�Ȩ��
    mc.setAttr('{}.liw'.format(obtain_jnt), False)

    for jnt in outSkin_lis:  # ��ÿ���ؽڵ�Ȩ�ض�����������ӹؽ�
        mc.select(mod)  #���ݹؽ�Ȩ����Ҫָ��ʵ�ʶ���ѡ�������skinPercent����Ƥ�ڵ��������ģ�͵�trs��Ҳ��
        if jnt in infJnt_lis:
            mc.setAttr('{}.liw'.format(jnt), False)
            mc.skinPercent(cluster, tv=[(jnt, 0)])
            mc.skinCluster(cluster, e=True, ri=jnt)
        else:
            fb_print('{}������Ƥ��'.format(jnt), warning=True, path=FILE_PATH, line=lin())

        if delete:  #���ؽڲ���������ʱ�ŵ������£����Ӽ�p�������ٰѹؽڷŵ������£����ؽ���������ʱ�����ؽ����Ӽ�ʱ�����Ӽ�����p��������
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
