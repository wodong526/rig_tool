# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mel

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class CreatBied(object):
    def __init__(self):
        self.move_joint()
        self.copy_joint()
        self.set_handCtl()
        mc.namespace(rm='DHIbody', mnr=True, f=True)
        mc.delete('spine_04_w')
        self.import_biped()

        mc.setAttr('front.rotateX', 0)
        mc.xform('side', ro=[0, 90, 0])
        mc.xform('top', ro=[90, 0, 0])

    def move_joint(self):
        mc.parent('FACIAL_C_FacialRoot', 'DHIbody:head')
        mc.parent('FACIAL_C_Neck2Root', 'DHIbody:neck_02')
        mc.parent('FACIAL_C_Neck1Root', 'DHIbody:neck_01')


    def copy_joint(self):
        head_jnt = ['spine_04', 'head', 'clavicle_r', 'upperarm_bck_r', 'upperarm_fwd_r',
                    'upperarm_out_r', 'upperarm_in_r', 'clavicle_out_r', 'clavicle_scap_r', 'clavicle_l',
                    'upperarm_bck_l', 'upperarm_fwd_l', 'upperarm_out_l', 'upperarm_in_l', 'clavicle_out_l',
                    'clavicle_scap_l', 'clavicle_pec_l', 'clavicle_pec_r', 'spine_04_latissimus_r',
                    'spine_04_latissimus_l']
        for jnt in head_jnt:
            body_jnt = 'DHIbody:{}'.format(jnt)
            mc.skinCluster('head_lod0_mesh_skinCluster', e=True, wt=0, ai=body_jnt)
        log.info('已将身体关节给到头模型。')

        inf_jnt = mc.skinCluster('head_lod0_mesh_skinCluster', q=True, inf=True)
        for jnt in inf_jnt:  # 锁定全部权重
            mc.setAttr('{}.liw'.format(jnt), 1)

        for jnt in head_jnt:
            mc.setAttr('{}.liw'.format(jnt), 0)
            mc.setAttr('DHIbody:{}.liw'.format(jnt), 0)
            jnt_h = mc.rename(jnt, '{}_w'.format(jnt))
            mc.rename('DHIbody:{}'.format(jnt), jnt)
            mc.skinPercent('head_lod0_mesh_skinCluster', 'head_lod0_mesh.vtx[:]', tv=[(jnt_h, 0)])
            mc.setAttr('{}.liw'.format(jnt), 1)
            mc.setAttr('{}.liw'.format(jnt_h), 1)
            mc.skinCluster('head_lod0_mesh_skinCluster', e=True, ri=jnt_h)
            log.info('已传递关节{}的权重。'.format(jnt))

        for obj in ['eyeshell', 'eyeEdge', 'cartilage']:
            mc.skinCluster('{}_lod0_mesh_skinCluster'.format(obj), e=True, lw=True, wt=0, ai='head')
            mc.setAttr('head_w.liw', 0)
            mc.setAttr('head.liw', 0)
            mc.skinPercent('{}_lod0_mesh_skinCluster'.format(obj), '{}_lod0_mesh.vtx[:]'.format(obj), tv=[('head_w', 0)])
            mc.skinCluster('{}_lod0_mesh_skinCluster'.format(obj), e=True, ri='head_w')
            log.info('已传递模型{}的head关节权重。'.format(obj))


    def set_handCtl(self):
        mc.setAttr('headGui_grp.rotateX', -90)
        for grp in ['GRP_faceGUI', 'GRP_C_eyesAim']:
            p_con = mc.listRelatives(grp)
            for conn in p_con:
                if mc.nodeType(conn) == 'parentConstraint':
                    tim_conn = mc.listConnections(conn, s=True, et=True, t='animCurveUU', c=True, p=True)
                    mc.disconnectAttr(tim_conn[1], tim_conn[0])
                    mc.delete(conn)

                    parCon = mc.parentConstraint('head', 'LOC_world', grp, mo=True)[0]
                    mc.connectAttr(tim_conn[1], '{}.headW0'.format(parCon), f=True)

                    nam = grp.split('_')[-1]
                    rvs = mc.createNode('reverse', n='rvs_{}_001'.format(nam))
                    mc.connectAttr(tim_conn[1], '{}.input.inputX'.format(rvs), f=True)
                    mc.connectAttr('{}.output.outputX'.format(rvs), '{}.LOC_worldW1'.format(parCon), f=True)
                    log.info('已重新链接{}控制器。'.format(nam))

    def import_biped(self):
        bid_path = 'D:/adv/AdvancedSkeleton5Files/fitSkeletons/biped.ma'
        mc.file(bid_path, i=True, typ='mayaAscii', iv=True, ra=True, op='v=0', pr=True, itr='combine', ns='adv')

        del_lis = ['Eye', 'Jaw']
        for jnt in del_lis:
            mc.delete('adv:{}'.format(jnt))
            log.info('已删除{}关节。'.format(jnt))
        mc.namespace(rm='adv', mnr=True, f=True)
        mel.eval('source \"D:/adv/AdvancedSkeleton5.mel\";AdvancedSkeleton5;')

        set_dir = {'Root':'inbetweenJoints', 'Spine1':'inbetweenJoints', 'Neck':'inbetweenJoints',
                   'Shoulder':'twistJoints', 'Elbow':'twistJoints', 'Hip':'twistJoints'}
        for obj in set_dir:
            mc.setAttr('{}.{}'.format(obj, set_dir[obj]), 0)
            log.info('已设置{}关节的twist为零。'.format(obj))

        log.info('已导入adv骨架，请对其进行缩放并建立控制关系。')

class MatchJoint(object):
    def __init__(self):
        self.match_joint()

    def match_joint(self):
        drv_lis = [['pelvis_drv', 'Root'], ['spine_03_drv', 'Spine1'], ['spine_05_drv', 'Chest'], ['neck_01_drv', 'Neck'], ['head_drv', 'Head'],
                   ['thigh_r_drv', 'Hip'], ['calf_r_drv', 'Knee'], ['foot_r_drv', 'Ankle'], ['ball_r_drv', 'Toes'],
                   ['clavicle_r_drv', 'Scapula'], ['upperarm_r_drv', 'Shoulder'], ['lowerarm_r_drv', 'Elbow'], ['hand_r_drv', 'Wrist'],
                   ['thumb_01_r_drv', 'ThumbFinger1'], ['thumb_02_r_drv', 'ThumbFinger2'], ['thumb_03_r_drv', 'ThumbFinger3'],
                   ['index_01_r_drv', 'IndexFinger1'], ['index_02_r_drv', 'IndexFinger2'], ['index_03_r_drv', 'IndexFinger3'],
                   ['middle_01_r_drv', 'MiddleFinger1'], ['middle_02_r_drv', 'MiddleFinger2'], ['middle_03_r_drv', 'MiddleFinger3'],
                   ['pinky_metacarpal_r_drv', 'Cup'], ['pinky_01_r_drv', 'PinkyFinger1'],
                   ['pinky_02_r_drv', 'PinkyFinger2'], ['pinky_03_r_drv', 'PinkyFinger3'],
                   ['ring_01_r_drv', 'RingFinger1'], ['ring_02_r_drv', 'RingFinger2'], ['ring_03_r_drv', 'RingFinger3']
                   ]

        for jnt in drv_lis:
            pos = mc.xform(jnt[0], ws=True, q=True, t=True)
            mc.xform(jnt[1], ws=True, t=pos)
        log.info('已匹配完成关节位置。')

class createLink(object):
    def __init__(self, assets_name):
        self.create_link()
        self.clear_scene(assets_name)
    def create_link(self):
        adv_lis = [['pelvis_drv', 'Root_M'], ['spine_03_drv', 'Spine1_M'], ['spine_05_drv', 'Chest_M'], ['neck_01_drv', 'Neck_M'], ['head_drv', 'Head_M'],
                   ['thigh_r_drv', 'Hip_R'], ['calf_r_drv', 'Knee_R'], ['foot_r_drv', 'Ankle_R'], ['ball_r_drv', 'Toes_R'],
                   ['clavicle_r_drv', 'Scapula_R'], ['upperarm_r_drv', 'Shoulder_R'], ['lowerarm_r_drv', 'Elbow_R'], ['hand_r_drv', 'Wrist_R'],
                   ['thumb_01_r_drv', 'ThumbFinger1_R'], ['thumb_02_r_drv', 'ThumbFinger2_R'], ['thumb_03_r_drv', 'ThumbFinger3_R'],
                   ['index_01_r_drv', 'IndexFinger1_R'], ['index_02_r_drv', 'IndexFinger2_R'], ['index_03_r_drv', 'IndexFinger3_R'],
                   ['middle_01_r_drv', 'MiddleFinger1_R'], ['middle_02_r_drv', 'MiddleFinger2_R'], ['middle_03_r_drv', 'MiddleFinger3_R'],
                   ['ring_01_r_drv', 'RingFinger1_R'], ['ring_02_r_drv', 'RingFinger2_R'], ['ring_03_r_drv', 'RingFinger3_R'],
                   ['pinky_metacarpal_r_drv', 'Cup_R'], ['pinky_01_r_drv', 'PinkyFinger1_R'], ['pinky_02_r_drv', 'PinkyFinger2_R'], ['pinky_03_r_drv', 'PinkyFinger3_R'],

                   ['thigh_l_drv', 'Hip_L'], ['calf_l_drv', 'Knee_L'], ['foot_l_drv', 'Ankle_L'], ['ball_l_drv', 'Toes_L'],
                   ['clavicle_l_drv', 'Scapula_L'], ['upperarm_l_drv', 'Shoulder_L'], ['lowerarm_l_drv', 'Elbow_L'],
                   ['hand_l_drv', 'Wrist_L'],
                   ['thumb_01_l_drv', 'ThumbFinger1_L'], ['thumb_02_l_drv', 'ThumbFinger2_L'],
                   ['thumb_03_l_drv', 'ThumbFinger3_L'],
                   ['index_01_l_drv', 'IndexFinger1_L'], ['index_02_l_drv', 'IndexFinger2_L'],
                   ['index_03_l_drv', 'IndexFinger3_L'],
                   ['middle_01_l_drv', 'MiddleFinger1_L'], ['middle_02_l_drv', 'MiddleFinger2_L'],
                   ['middle_03_l_drv', 'MiddleFinger3_L'],
                   ['ring_01_l_drv', 'RingFinger1_L'], ['ring_02_l_drv', 'RingFinger2_L'], ['ring_03_l_drv', 'RingFinger3_L'],
                   ['pinky_metacarpal_l_drv', 'Cup_L'], ['pinky_01_l_drv', 'PinkyFinger1_L'],
                   ['pinky_02_l_drv', 'PinkyFinger2_L'], ['pinky_03_l_drv', 'PinkyFinger3_L']
                   ]
        for jnt in adv_lis:
            mc.parentConstraint(jnt[1], jnt[0], mo=True)
        log.info('已将adv骨架链接到meta驱动骨架。')

    def clear_scene(self, nam):
        for grp in ['grp_head', 'grp_body']:
            mc.parent(grp, 'Geometry')
        mc.rename('Geometry', 'Gr_{}'.format(nam))

        grp_xform = mc.group(n='grp_xform', p='Group', em=True)
        for obj in ['rig_setup_grp', 'headRig_grp', 'pelvis_drv', 'Root_M']:
            mc.parent(obj, grp_xform)
        mc.parent('pelvis', 'DeformationSystem')
        mc.setAttr('Root_M.visibility', 0)
        log.info('已创建好大纲层级。')
        mc.rename('Group', '{}_Rig_Group'.format(nam))

