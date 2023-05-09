# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm

import sys
import traceback

if sys.version_info.major == 3:
    #������Ϊpy3ʱ
    from importlib import reload

from feedback_tool import Feedback_info as fb_print
from dutils import toolutils


def LIN():
    line_number = traceback.extract_stack()[-2][1]
    return line_number


FILE_PATH = __file__


def metaHead_to_adv():
    if mc.objExists('NeckPart1_M') and not mc.objExists('NeckPart2_M'):
        hide_adv_ctrlAndJoint()
        set_advJoint_pos()
        transform_skin()
        transform_neck_weight()
        arrangement_scence()
    else:
        fb_print('���ҽ���adv�ľ�׵twist�ؽ�����Ϊ1ʱ�ù��߲���Ч�����ؽ�adv�Ǽ�', error=True, path=FILE_PATH,
                 line=LIN(), viewMes=True)


def hide_adv_ctrlAndJoint():
    '''
    ��adv��ͷ���޹ؿ�������ؽ�����
    :return: None
    '''
    hide_lis = ['FKOffsetJaw_M', 'FKAimEye_R', 'FKAimEye_L', 'AimFollowEye', 'Eye_R', 'Eye_L', 'Jaw_M']
    for obj in hide_lis:
        if mc.objExists(obj):
            mc.setAttr('{}.v'.format(obj), False)
    fb_print('������advͷ���޹ؿ�������ؽ�', info=True, path=FILE_PATH, line=LIN())


def set_advJoint_pos():
    '''
    ƥ��adv��׵�ؽڵ�meta�Ĺؽ�λ��
    :return: None
    '''
    #��ȡmeta��׵�Ĺؽ�λ��
    meta_neck_01_pos = mc.xform('neck_01', q=True, ws=True, t=True)
    meta_neck_02_pos = mc.xform('neck_02', q=True, ws=True, t=True)
    meta_head_pos = mc.xform('head', q=True, ws=True, t=True)
    #����adv��׵�ؽڵĿ��Ƹ������λ����meta��׵λ����ͬ������adv��λ�ؽ����ļ�׵��λ����meta��׵λ����ͬ
    mc.xform('FKOffsetNeck_M', ws=True, t=meta_neck_01_pos)
    mc.xform('Neck', ws=True, t=meta_neck_01_pos)
    mc.xform('FKPS2NeckPart1_M', ws=True, t=meta_neck_02_pos)
    mc.xform('FKPS2Head_M', ws=True, t=meta_head_pos)
    mc.xform('Head', ws=True, t=meta_head_pos)
    fb_print('��ƥ��adv�Ǽܵ�meta', info=True, path=FILE_PATH, line=LIN())

    if mc.objExists('drv_spine_04'):  #����ͷ���任���߲�������adv��ͷ�Ŀ�������Ҫ���ƵĹؽ���Ϊ�����ؽ���
        mc.parentConstraint('FKXHead_M', 'drv_head', mo=True)
    else:
        mc.parentConstraint('FKXHead_M', 'head', mo=True)
    fb_print('advͷ��������Լ��metaͷ�ؽ�', info=True, path=FILE_PATH, line=LIN())


def transform_skin():
    '''
    ��meta�ؽ�����Ҫ��ֲ��adv�ؽ��ϵ�Ȩ�ش��ݹ�ȥ
    :return: None
    '''
    add_joint_dir = {'Scapula_L': ['clavicle_out_l', 'clavicle_scap_l', 'clavicle_l'],
                     'Scapula_R': ['clavicle_out_r', 'clavicle_scap_r', 'clavicle_r'],
                     'Chest_M': ['spine_04', 'clavicle_pec_l', 'clavicle_pec_r', 'spine_04_latissimus_l',
                                 'spine_04_latissimus_r'],
                     'Shoulder_L': ['upperarm_out_l', 'upperarm_bck_l', 'upperarm_fwd_l', 'upperarm_in_l'],
                     'Shoulder_R': ['upperarm_out_r', 'upperarm_bck_r', 'upperarm_fwd_r', 'upperarm_in_r'],
                     'Neck_M': ['neck_01'], 'NeckPart1_M': ['neck_02']}
    for jnt in add_joint_dir:  #��adv��ͷ�Ĺؽڼ��뵽metaͷ����Ƥ��
        mc.skinCluster('head_lod0_mesh_skinCluster', e=True, lw=True, wt=0, ai=jnt)

    for adv_jnt, meta_jnt_lis in add_joint_dir.items():
        toolutils.transform_jnt_skin(meta_jnt_lis, adv_jnt, 'head_lod0_mesh', delete=True)


def transform_neck_weight():
    '''
    ��meta�����ϵ��ӹؽ�Ȩ����ֲ����׵�ؽ���
    :return: None
    '''
    neck_2_subJoint = mc.listRelatives('FACIAL_C_Neck2Root')  # ��ȡFACIAL_C_Neck2Root�µ����йؽ�
    neck_1_subJoint = mc.listRelatives('FACIAL_C_Neck1Root')  # ��ȡFACIAL_C_Neck1Root�µ����йؽ�

    toolutils.transform_jnt_skin(neck_1_subJoint, 'Neck_M', 'head_lod0_mesh', True)
    toolutils.transform_jnt_skin(neck_2_subJoint, 'NeckPart1_M', 'head_lod0_mesh', True)

    #�����������١������Ӻ�ͷ��head�ؽ��ϵ���Ƥ�ŵ�Head_M��
    toolutils.add_skinJnt('head_lod0_mesh_skinCluster', 'Head_M')
    toolutils.transform_jnt_skin(['head'], 'Head_M', 'head_lod0_mesh')
    toolutils.add_skinJnt('eyeEdge_lod0_mesh_skinCluster', 'Head_M')
    toolutils.transform_jnt_skin(['head'], 'Head_M', 'eyeEdge_lod0_mesh')
    toolutils.add_skinJnt('cartilage_lod0_mesh_skinCluster', 'Head_M')
    toolutils.transform_jnt_skin(['head'], 'Head_M', 'cartilage_lod0_mesh')
    toolutils.add_skinJnt('eyeshell_lod0_mesh_skinCluster', 'Head_M')
    toolutils.transform_jnt_skin(['head'], 'Head_M', 'eyeshell_lod0_mesh')
    mc.parent(mc.listRelatives('head'), 'Head_M')

    mc.delete('FACIAL_C_Neck2Root', 'FACIAL_C_Neck1Root')
    fb_print('���ӹؽ�Ȩ��ת�����', info=True, path=FILE_PATH, line=LIN())


def arrangement_scence():
    '''
    ��β������ɾ�����õĶ��������������ؽ�Ϊԭ�������֣��Ա�meta�������ʱ�ж����������
    :return:
    '''
    mc.delete('spine_05')
    if mc.objExists('drv_spine_04'):
        for jnt in mc.listRelatives('grp_moveDrvJnt_001', ad=True):
            if not mc.objExists(jnt.replace('drv_', '')):
                mc.rename(jnt, jnt.replace('drv_', ''))
        mc.parent('head', 'grp_moveDrvJnt_001')
    mm.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    fb_print('ת�����', info=True, path=FILE_PATH, line=LIN(), viewMes=True)
