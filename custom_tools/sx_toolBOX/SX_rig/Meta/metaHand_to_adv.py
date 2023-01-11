# -*- coding:GBK -*-
import maya.cmds as mc

import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def metaHead_to_adv():
    prepare_scene()
    set_joint_pos()
    transform_neck_weight()
    transform_skin()
    arrangement_scence()    

def prepare_scene():
    '''
    ��meta��ͷ����Ҫ��Ȩ�ش���adv�Ĺؽڵ�Ȩ�ش���adv�ĹǼ��ϣ��������õĹؽ�ɾ������Լ��������������
    '''
    hide_lis = ['FKOffsetJaw_M', 'FKAimEye_R', 'FKAimEye_L', 'Eye_R', 'Eye_L', 'Jaw_M']
    for grp in hide_lis:#����adv�����õĿ�����
        if mc.objExists(grp):
            mc.setAttr('{}.visibility'.format(grp), False)

    if mc.objExists('NeckPart2_M') or not mc.objExists('NeckPart1_M'):
        log.error('ֻ�е�adv�ľ�׵�ؽ�����twist�ؽ�Ϊ1��ʱ���ýű�����ʹ�á�')
        return None

def set_joint_pos():
    #��ȡmeta�ϵĹؽ�λ�ã�����meta����ֻ�������ؽڣ���������ֻ����adv�Ĳ�����Ϊ�����ؽڣ�
    meta_neck_pos = mc.xform('neck_01', q=True, ws=True, t=True)
    meta_neck_end_pos = mc.xform('neck_02', q=True, ws=True, t=True)
    meta_head_pos = mc.xform('head', q=True, ws=True, t=True)
    #��adv�Ŀ�����λ��λ�Ƶ�meta�Ĺؽڵ���
    mc.xform('FKOffsetNeck_M', ws=True, t=meta_neck_pos)
    mc.xform('FKPS2NeckPart1_M', ws=True, t=meta_neck_end_pos)
    mc.xform('FKPS2Head_M', ws=True, t=meta_head_pos)
    mc.xform('Neck', ws=True, t=meta_neck_pos)
    mc.xform('Head', ws=True, t=meta_head_pos)

    if mc.objExists('drv_spine_04'):#����ͷ���任���߲�������adv��ͷ�Ŀ�������Ҫ���ƵĹؽ���Ϊ�����ؽ���
        mc.parentConstraint('FKXHead_M', 'drv_head', mo=True)
    else:
        mc.parentConstraint('FKXHead_M', 'head', mo=True)

def transform_skin():
    '''
    ��meta�ؽ�����Ҫ��ֲ��adv�ؽ��ϵ�Ȩ�ش��ݹ�ȥ
    '''
    add_joint_dir = {'Scapula_L':['clavicle_out_l', 'clavicle_scap_l', 'clavicle_l'],
                     'Scapula_R':['clavicle_out_r', 'clavicle_scap_r', 'clavicle_r'],
                     'Chest_M':['spine_04', 'clavicle_pec_l', 'clavicle_pec_r', 'spine_04_latissimus_l', 'spine_04_latissimus_r'],
                     'Shoulder_L':['upperarm_out_l', 'upperarm_bck_l', 'upperarm_fwd_l', 'upperarm_in_l'],
                     'Shoulder_R':['upperarm_out_r', 'upperarm_bck_r', 'upperarm_fwd_r', 'upperarm_in_r'],
                     'Neck_M':['neck_01'], 'NeckPart1_M':['neck_02']}
    for jnt in add_joint_dir:#��adv��ͷ�Ĺؽڼ��뵽metaͷ����Ƥ��
        mc.skinCluster('head_lod0_mesh_skinCluster', e=True, lw=True, wt=0, ai=jnt)

    for jnt in mc.skinCluster('head_lod0_mesh_skinCluster', inf='', q=True):#�����йؽڵ�Ȩ�ض���ס
        mc.setAttr('{}.liw'.format(jnt), True)

    mc.parent('head', mc.listRelatives('Head_M', p=True)[0])#��metaͷ����Ƥ�ؽ���p��adv�Ĳ���ĩ�˹ؽ�����

    mc.select('head_lod0_mesh')#skinPercent��Ҫѡ��ģ�ͻ�����Ƥ�ڵ�����ģ��trs����������ʹ��
    for adv_jnt, meta_jnt_lis in add_joint_dir.items():
        mc.setAttr('{}.liw'.format(adv_jnt), False)#��Ҫ����Ȩ�صĹؽ�
        for meta_jnt in meta_jnt_lis:
            mc.setAttr('{}.liw'.format(meta_jnt), False)#��Ҫ����Ȩ�صĹؽ�
            mc.skinPercent('head_lod0_mesh_skinCluster', tv=[(meta_jnt, 0)])#����Ȩ��
            mc.skinCluster('head_lod0_mesh_skinCluster', e=True, ri=meta_jnt)#���ùؽ��Ƴ���Ƥ
        mc.setAttr('{}.liw'.format(adv_jnt), True)#������סҪ����Ȩ�صĹؽ�


def transform_neck_weight():
    '''
    ��meta�����ϵ��ӹؽ�Ȩ����ֲ����׵�ؽ���
    '''
    neck_2_subJoint = mc.listRelatives('FACIAL_C_Neck2Root')  # ��ȡFACIAL_C_Neck2Root�µ����йؽ�
    neck_1_subJoint = mc.listRelatives('FACIAL_C_Neck1Root')  # ��ȡFACIAL_C_Neck1Root�µ����йؽ�
    mc.skinCluster('head_lod0_mesh_skinCluster', e=True, lw=True, wt=0, ai='neck_01')  # ��neck_01���뵽ģ�͵���Ƥ��
    mc.skinCluster('head_lod0_mesh_skinCluster', e=True, lw=True, wt=0, ai='neck_02')  # ��neck_02���뵽ģ�͵���Ƥ��
    for jnt in mc.skinCluster('head_lod0_mesh_skinCluster', inf=True, q=1):  # ȫ�����йؽ�
        mc.setAttr('{}.liw'.format(jnt), True)

    mc.setAttr('neck_01.liw', False)  # �������ӹؽ�
    skin_jnt_lis = mc.skinCluster('head_lod0_mesh_skinCluster', inf=True, q=True)  #��ȡ���и���Ƥ�ڵ�Ӱ��Ĺؽ�
    mc.select('head_lod0_mesh')  #���ݹؽ�Ȩ����Ҫָ��ʵ�ʶ���ѡ�������skinPercent����Ƥ�ڵ��������ģ�͵�trs��Ҳ��
    for jnt in neck_1_subJoint:  # ��ÿ���ؽڵ�Ȩ�ض�����������ӹؽ�
        if jnt in skin_jnt_lis:
            mc.setAttr('{}.liw'.format(jnt), False)
            mc.skinPercent('head_lod0_mesh_skinCluster', tv=[(jnt, 0)])
            mc.skinCluster('head_lod0_mesh_skinCluster', e=True, ri=jnt)
        else:
            log.warning('{}������Ƥ�С�'.format(jnt))
        mc.delete(jnt)
    mc.setAttr('neck_01.liw', True)

    mc.setAttr('neck_02.liw', False)
    for jnt in neck_2_subJoint:  # ��ÿ���ؽڵ�Ȩ�ض�����������ӹؽ�
        if jnt in skin_jnt_lis:
            mc.setAttr('{}.liw'.format(jnt), False)
            mc.skinPercent('head_lod0_mesh_skinCluster', tv=[(jnt, 0)])
            mc.skinCluster('head_lod0_mesh_skinCluster', e=True, ri=jnt)
        else:
            log.warning('{}������Ƥ�С�'.format(jnt))
        mc.delete(jnt)
    mc.setAttr('neck_02.liw', True)

    mc.delete('FACIAL_C_Neck2Root', 'FACIAL_C_Neck1Root')
    log.info('���ӹؽ�Ȩ��ת����ɡ�')

def arrangement_scence():
    if mc.objExists('drv_spine_04'):
        mc.parent('drv_head', 'grp_moveDrvJnt_001')
        mc.delete('drv_spine_04')
    mc.delete('spine_04')
    log.info('ת����ɡ�')