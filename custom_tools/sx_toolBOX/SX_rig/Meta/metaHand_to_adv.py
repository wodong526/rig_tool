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
    将meta的头的需要将权重传到adv的关节的权重传到adv的骨架上，并将无用的关节删除、将约束控制重新做好
    '''
    hide_lis = ['FKOffsetJaw_M', 'FKAimEye_R', 'FKAimEye_L', 'Eye_R', 'Eye_L', 'Jaw_M']
    for grp in hide_lis:#隐藏adv上无用的控制器
        if mc.objExists(grp):
            mc.setAttr('{}.visibility'.format(grp), False)

    if mc.objExists('NeckPart2_M') or not mc.objExists('NeckPart1_M'):
        log.error('只有当adv的颈椎关节链的twist关节为1个时，该脚本才能使用。')
        return None

def set_joint_pos():
    #获取meta上的关节位置（由于meta脖子只有两个关节，所以这里只考虑adv的脖子上为两个关节）
    meta_neck_pos = mc.xform('neck_01', q=True, ws=True, t=True)
    meta_neck_end_pos = mc.xform('neck_02', q=True, ws=True, t=True)
    meta_head_pos = mc.xform('head', q=True, ws=True, t=True)
    #将adv的控制器位置位移到meta的关节点上
    mc.xform('FKOffsetNeck_M', ws=True, t=meta_neck_pos)
    mc.xform('FKPS2NeckPart1_M', ws=True, t=meta_neck_end_pos)
    mc.xform('FKPS2Head_M', ws=True, t=meta_head_pos)
    mc.xform('Neck', ws=True, t=meta_neck_pos)
    mc.xform('Head', ws=True, t=meta_head_pos)

    if mc.objExists('drv_spine_04'):#当被头部变换工具操作过，adv的头的控制器需要控制的关节链为驱动关节链
        mc.parentConstraint('FKXHead_M', 'drv_head', mo=True)
    else:
        mc.parentConstraint('FKXHead_M', 'head', mo=True)

def transform_skin():
    '''
    将meta关节上需要移植到adv关节上的权重传递过去
    '''
    add_joint_dir = {'Scapula_L':['clavicle_out_l', 'clavicle_scap_l', 'clavicle_l'],
                     'Scapula_R':['clavicle_out_r', 'clavicle_scap_r', 'clavicle_r'],
                     'Chest_M':['spine_04', 'clavicle_pec_l', 'clavicle_pec_r', 'spine_04_latissimus_l', 'spine_04_latissimus_r'],
                     'Shoulder_L':['upperarm_out_l', 'upperarm_bck_l', 'upperarm_fwd_l', 'upperarm_in_l'],
                     'Shoulder_R':['upperarm_out_r', 'upperarm_bck_r', 'upperarm_fwd_r', 'upperarm_in_r'],
                     'Neck_M':['neck_01'], 'NeckPart1_M':['neck_02']}
    for jnt in add_joint_dir:#将adv的头的关节加入到meta头的蒙皮中
        mc.skinCluster('head_lod0_mesh_skinCluster', e=True, lw=True, wt=0, ai=jnt)

    for jnt in mc.skinCluster('head_lod0_mesh_skinCluster', inf='', q=True):#将所有关节的权重都锁住
        mc.setAttr('{}.liw'.format(jnt), True)

    mc.parent('head', mc.listRelatives('Head_M', p=True)[0])#将meta头的蒙皮关节链p到adv的脖子末端关节链中

    mc.select('head_lod0_mesh')#skinPercent需要选中模型或在蒙皮节点后加入模型trs名才能正常使用
    for adv_jnt, meta_jnt_lis in add_joint_dir.items():
        mc.setAttr('{}.liw'.format(adv_jnt), False)#打开要接受权重的关节
        for meta_jnt in meta_jnt_lis:
            mc.setAttr('{}.liw'.format(meta_jnt), False)#打开要传出权重的关节
            mc.skinPercent('head_lod0_mesh_skinCluster', tv=[(meta_jnt, 0)])#传递权重
            mc.skinCluster('head_lod0_mesh_skinCluster', e=True, ri=meta_jnt)#将该关节移出蒙皮
        mc.setAttr('{}.liw'.format(adv_jnt), True)#重新锁住要接受权重的关节


def transform_neck_weight():
    '''
    将meta脖子上的子关节权重移植到颈椎关节上
    '''
    neck_2_subJoint = mc.listRelatives('FACIAL_C_Neck2Root')  # 获取FACIAL_C_Neck2Root下的所有关节
    neck_1_subJoint = mc.listRelatives('FACIAL_C_Neck1Root')  # 获取FACIAL_C_Neck1Root下的所有关节
    mc.skinCluster('head_lod0_mesh_skinCluster', e=True, lw=True, wt=0, ai='neck_01')  # 将neck_01加入到模型的蒙皮里
    mc.skinCluster('head_lod0_mesh_skinCluster', e=True, lw=True, wt=0, ai='neck_02')  # 将neck_02加入到模型的蒙皮里
    for jnt in mc.skinCluster('head_lod0_mesh_skinCluster', inf=True, q=1):  # 全锁所有关节
        mc.setAttr('{}.liw'.format(jnt), True)

    mc.setAttr('neck_01.liw', False)  # 单开脖子关节
    skin_jnt_lis = mc.skinCluster('head_lod0_mesh_skinCluster', inf=True, q=True)  #获取所有该蒙皮节点影响的关节
    mc.select('head_lod0_mesh')  #传递关节权重需要指定实际对象，选择或者在skinPercent的蒙皮节点名后加上模型的trs名也行
    for jnt in neck_1_subJoint:  # 将每个关节的权重都反向给到脖子关节
        if jnt in skin_jnt_lis:
            mc.setAttr('{}.liw'.format(jnt), False)
            mc.skinPercent('head_lod0_mesh_skinCluster', tv=[(jnt, 0)])
            mc.skinCluster('head_lod0_mesh_skinCluster', e=True, ri=jnt)
        else:
            log.warning('{}不在蒙皮中。'.format(jnt))
        mc.delete(jnt)
    mc.setAttr('neck_01.liw', True)

    mc.setAttr('neck_02.liw', False)
    for jnt in neck_2_subJoint:  # 将每个关节的权重都反向给到脖子关节
        if jnt in skin_jnt_lis:
            mc.setAttr('{}.liw'.format(jnt), False)
            mc.skinPercent('head_lod0_mesh_skinCluster', tv=[(jnt, 0)])
            mc.skinCluster('head_lod0_mesh_skinCluster', e=True, ri=jnt)
        else:
            log.warning('{}不在蒙皮中。'.format(jnt))
        mc.delete(jnt)
    mc.setAttr('neck_02.liw', True)

    mc.delete('FACIAL_C_Neck2Root', 'FACIAL_C_Neck1Root')
    log.info('脖子关节权重转换完成。')

def arrangement_scence():
    if mc.objExists('drv_spine_04'):
        mc.parent('drv_head', 'grp_moveDrvJnt_001')
        mc.delete('drv_spine_04')
    mc.delete('spine_04')
    log.info('转换完成。')