# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm

import sys
import traceback

if sys.version_info.major == 3:
    #当环境为py3时
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
        fb_print('当且仅当adv的颈椎twist关节数量为1时该工具才有效，请重建adv骨架', error=True, path=FILE_PATH,
                 line=LIN(), viewMes=True)


def hide_adv_ctrlAndJoint():
    '''
    将adv的头部无关控制器与关节隐藏
    :return: None
    '''
    hide_lis = ['FKOffsetJaw_M', 'FKAimEye_R', 'FKAimEye_L', 'AimFollowEye', 'Eye_R', 'Eye_L', 'Jaw_M']
    for obj in hide_lis:
        if mc.objExists(obj):
            mc.setAttr('{}.v'.format(obj), False)
    fb_print('已隐藏adv头部无关控制器与关节', info=True, path=FILE_PATH, line=LIN())


def set_advJoint_pos():
    '''
    匹配adv脊椎关节到meta的关节位置
    :return: None
    '''
    #获取meta脊椎的关节位置
    meta_neck_01_pos = mc.xform('neck_01', q=True, ws=True, t=True)
    meta_neck_02_pos = mc.xform('neck_02', q=True, ws=True, t=True)
    meta_head_pos = mc.xform('head', q=True, ws=True, t=True)
    #设置adv脊椎关节的控制父级组的位置与meta脊椎位置相同，设置adv定位关节链的脊椎的位置与meta脊椎位置相同
    mc.xform('FKOffsetNeck_M', ws=True, t=meta_neck_01_pos)
    mc.xform('Neck', ws=True, t=meta_neck_01_pos)
    mc.xform('FKPS2NeckPart1_M', ws=True, t=meta_neck_02_pos)
    mc.xform('FKPS2Head_M', ws=True, t=meta_head_pos)
    mc.xform('Head', ws=True, t=meta_head_pos)
    fb_print('已匹配adv骨架到meta', info=True, path=FILE_PATH, line=LIN())

    if mc.objExists('drv_spine_04'):  #当被头部变换工具操作过，adv的头的控制器需要控制的关节链为驱动关节链
        mc.parentConstraint('FKXHead_M', 'drv_head', mo=True)
    else:
        mc.parentConstraint('FKXHead_M', 'head', mo=True)
    fb_print('adv头控制器已约束meta头关节', info=True, path=FILE_PATH, line=LIN())


def transform_skin():
    '''
    将meta关节上需要移植到adv关节上的权重传递过去
    :return: None
    '''
    add_joint_dir = {'Scapula_L': ['clavicle_out_l', 'clavicle_scap_l', 'clavicle_l'],
                     'Scapula_R': ['clavicle_out_r', 'clavicle_scap_r', 'clavicle_r'],
                     'Chest_M': ['spine_04', 'clavicle_pec_l', 'clavicle_pec_r', 'spine_04_latissimus_l',
                                 'spine_04_latissimus_r'],
                     'Shoulder_L': ['upperarm_out_l', 'upperarm_bck_l', 'upperarm_fwd_l', 'upperarm_in_l'],
                     'Shoulder_R': ['upperarm_out_r', 'upperarm_bck_r', 'upperarm_fwd_r', 'upperarm_in_r'],
                     'Neck_M': ['neck_01'], 'NeckPart1_M': ['neck_02']}
    for jnt in add_joint_dir:  #将adv的头的关节加入到meta头的蒙皮中
        mc.skinCluster('head_lod0_mesh_skinCluster', e=True, lw=True, wt=0, ai=jnt)

    for adv_jnt, meta_jnt_lis in add_joint_dir.items():
        toolutils.transform_jnt_skin(meta_jnt_lis, adv_jnt, 'head_lod0_mesh', delete=True)


def transform_neck_weight():
    '''
    将meta脖子上的子关节权重移植到颈椎关节上
    :return: None
    '''
    neck_2_subJoint = mc.listRelatives('FACIAL_C_Neck2Root')  # 获取FACIAL_C_Neck2Root下的所有关节
    neck_1_subJoint = mc.listRelatives('FACIAL_C_Neck1Root')  # 获取FACIAL_C_Neck1Root下的所有关节

    toolutils.transform_jnt_skin(neck_1_subJoint, 'Neck_M', 'head_lod0_mesh', True)
    toolutils.transform_jnt_skin(neck_2_subJoint, 'NeckPart1_M', 'head_lod0_mesh', True)

    #将眼睑、泪腺、眼罩子和头在head关节上的蒙皮放到Head_M上
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
    fb_print('脖子关节权重转换完成', info=True, path=FILE_PATH, line=LIN())


def arrangement_scence():
    '''
    收尾工作，删除无用的对象，重命名驱动关节为原本的名字，以便meta插件加载时有对象可以链接
    :return:
    '''
    mc.delete('spine_05')
    if mc.objExists('drv_spine_04'):
        for jnt in mc.listRelatives('grp_moveDrvJnt_001', ad=True):
            if not mc.objExists(jnt.replace('drv_', '')):
                mc.rename(jnt, jnt.replace('drv_', ''))
        mc.parent('head', 'grp_moveDrvJnt_001')
    mm.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    fb_print('转换完成', info=True, path=FILE_PATH, line=LIN(), viewMes=True)
