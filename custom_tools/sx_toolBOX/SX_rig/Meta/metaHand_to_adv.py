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
    hide_lis = ['FKOffsetJaw_M', 'FKAimEye_R', 'FKAimEye_L', 'Eye_R', 'Eye_L', 'Jaw_M', 'drv_head']
    for grp in hide_lis:#����adv�����õĿ�����
        if mc.objExists(grp):
            mc.setAttr('{}.visibility'.format(grp), False)

    if mc.objExists('NeckPart2_M') or not mc.objExists('NeckPart1_M'):
        raise RuntimeError('ֻ�е�adv�ľ�׵�ؽ�����twist�ؽ�Ϊ1��ʱ���ýű�����ʹ�á�')

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

    #mc.parent('head', mc.listRelatives('Head_M', p=True)[0])#��metaͷ����Ƥ�ؽ���p��adv�Ĳ���ĩ�˹ؽ�����

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
    add_skinJnt('head_lod0_mesh_skinCluster', 'neck_01') # ��neck_01���뵽ģ�͵���Ƥ��
    add_skinJnt('head_lod0_mesh_skinCluster', 'neck_02') # ��neck_02���뵽ģ�͵���Ƥ��

    transform_jnt_skin(neck_1_subJoint, 'neck_01', 'head_lod0_mesh_skinCluster', 'head_lod0_mesh', True)
    transform_jnt_skin(neck_2_subJoint, 'neck_02', 'head_lod0_mesh_skinCluster', 'head_lod0_mesh', True)

    #�����������١������Ӻ�ͷ��head�ؽ��ϵ���Ƥ�ŵ�Head_M��
    add_skinJnt('head_lod0_mesh_skinCluster', 'Head_M')
    transform_jnt_skin(['head'], 'Head_M', 'head_lod0_mesh_skinCluster', 'head_lod0_mesh')
    add_skinJnt('eyeEdge_lod0_mesh_skinCluster', 'Head_M')
    transform_jnt_skin(['head'], 'Head_M', 'eyeEdge_lod0_mesh_skinCluster', 'eyeEdge_lod0_mesh')
    add_skinJnt('cartilage_lod0_mesh_skinCluster', 'Head_M')
    transform_jnt_skin(['head'], 'Head_M', 'cartilage_lod0_mesh_skinCluster', 'cartilage_lod0_mesh')
    add_skinJnt('eyeshell_lod0_mesh_skinCluster', 'Head_M')
    transform_jnt_skin(['head'], 'Head_M', 'eyeshell_lod0_mesh_skinCluster', 'eyeshell_lod0_mesh')
    mc.parent(mc.listRelatives('head'), 'Head_M')

    mc.delete('FACIAL_C_Neck2Root', 'FACIAL_C_Neck1Root')
    log.info('���ӹؽ�Ȩ��ת����ɡ�')

def arrangement_scence():
    if mc.objExists('drv_spine_04'):
        mc.parent('drv_head', 'grp_moveDrvJnt_001')
    mc.delete('spine_04', 'drv_spine_04')
    log.info('ת����ɡ�')

def transform_jnt_skin(outSkin_lis, obtain_jnt, cluster, mod, delete=False):
    '''
    outSkin_lis:Ҫ���Ȩ�صĹؽ��б�
    obtain_jnt��Ҫ��ȡȨ�صĹؽ��б�
    cluster��Ҫ�ı�Ȩ�ص���Ƥ�ڵ�
    mod_lis��Ҫ�ı�Ȩ�ص�ģ��
    '''
    mc.select(mod)#���ݹؽ�Ȩ����Ҫָ��ʵ�ʶ���ѡ�������skinPercent����Ƥ�ڵ��������ģ�͵�trs��Ҳ��
    infJnt_lis = mc.skinCluster(cluster, inf=True, q=True)#��ȡ���и���Ƥ�ڵ�Ӱ��Ĺؽ�
    for jnt in infJnt_lis:
        mc.setAttr('{}.liw'.format(jnt), True)
    mc.setAttr('{}.liw'.format(obtain_jnt), False)
    for jnt in outSkin_lis:  # ��ÿ���ؽڵ�Ȩ�ض�����������ӹؽ�
        if jnt in infJnt_lis:
            mc.setAttr('{}.liw'.format(jnt), False)
            mc.skinPercent(cluster, tv=[(jnt, 0)])
            mc.skinCluster(cluster, e=True, ri=jnt)
        else:
            log.warning('{}������Ƥ�С�'.format(jnt))
        if delete:
            mc.delete(jnt)
    mc.setAttr('{}.liw'.format(obtain_jnt), True)

def add_skinJnt(clster, *joints):
    infJnt_lis = mc.skinCluster(clster, inf=True, q=True)
    for jnt in joints:
        if jnt not in infJnt_lis:
            mc.skinCluster(clster, e=True, lw=True, wt=0, ai=jnt)