# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mel

import os

from feedback_tool import Feedback_info as fp

class Extract_Body(object):
    def __init__(self):
        self.del_grp()
        self.set_mod()
        self.del_nameSpace()
        self.set_heand_ctl()
        self.set_heand_ctl()
        self.set_joint()
        self.parent_mod()
        self.clear_scene()
        mc.SaveSceneAs()

    def del_grp(self):
        for i in range(8):
            mc.delete('head_lod{}_layer'.format(i))
            if i < 4:
                mc.delete('body_lod{}_layer'.format(i))

            if i == 0:
                continue
            else:
                if i < 4:
                    mc.delete('body_lod{}_grp'.format(i))
                mc.delete('head_lod{}_grp'.format(i))
        fp('lod与显示层已删除。', info=True)

        del_lis = ['export_geo_GRP', 'Body_joints', 'Lights', 'FacialControls',
                   'PSD', 'eyelashes_lod0_mesh']
        for d in del_lis:
            mc.delete(d)
        mod_lis = mc.listRelatives('body_lod0_grp')
        for obj in mod_lis:
            if '_combined_' in obj:
                mc.delete(obj)
        fp('多余选择集与组已删除。')

    def set_mod(self):
        mc.setAttr('root_drv.rotateX', -90)

        now_path = mc.internalVar(uad=True) + mc.about(v=True)
        self.target_path = '{}/target.mb'.format(now_path)
        mc.file(self.target_path, f=True, ea=True, typ='mayaBinary', op='v = 1', pr=True)

        self.head_mod = mc.listRelatives('head_lod0_grp')
        self.body_mod = mc.listRelatives('body_lod0_grp')
        sel_lis = self.head_mod + self.body_mod
        cls_dir = {}
        cls_name_dir = {}
        for obj in sel_lis:
            shp = mc.listRelatives(obj, s=1)[0]
            clst = mc.listConnections(shp, t='skinCluster', et=True)[0]
            jnt = mc.listConnections(clst, t='joint', et=True)
            cls_dir[obj] = jnt
            cls_name_dir[obj] = clst
            mc.delete(clst)

        for obj in sel_lis:
            for aix in ['X', 'Y', 'Z']:
                mc.setAttr('{}.translate{}'.format(obj, aix), l=False)
                mc.setAttr('{}.rotate{}'.format(obj, aix), l=False)
                mc.setAttr('{}.scale{}'.format(obj, aix), l=False)

        for grp in ['head_lod0_grp', 'body_lod0_grp']:
            mc.setAttr('{}.rotateX'.format(grp), -90)
            mc.setAttr('{}.rotateX'.format(grp), -90)
            mc.makeIdentity(grp, a=True, r=True, n=False, pn=True)

        for clst in cls_dir:
            jnt_lis = []
            for jnt in cls_dir[clst]:
                jnt_lis.append(jnt)
            jnt_lis.append(clst)
            mc.skinCluster(jnt_lis, tsb=True, n=cls_name_dir[clst])

        mc.file(self.target_path, r=True, typ='mayaBinary', ns='tst')
        for obj in cls_name_dir:
            mc.copySkinWeights(ss='tst:{}'.format(cls_name_dir[obj]), ds=cls_name_dir[obj],
                               nm=True, sa='closestPoint', ia='closestJoint')
            mc.select(obj)
            mc.BakeNonDefHistory()
        mc.file(self.target_path, rr=True)
        fp('掰直模型并重传权重已完成。')

    def del_nameSpace(self):
        mc.namespace(rm='DHIhead', mnr=1, f=1)
        fp('已清理空间名DHIhead。')

    def set_heand_ctl(self):
        for ctl in ['CTRL_eyesAimFollowHead', 'CTRL_faceGUIfollowHead']:
            mc.setAttr('{}.translateY'.format(ctl), 1)
        fp('已拉正头部控制器。')

    def set_joint(self):
        for jnt in ['DHIbody:pelvis', 'pelvis_drv']:
            p = mc.listRelatives(jnt, p = True)[0]
            mc.parent(jnt, w = True)
            mc.delete(p)
        mc.setAttr('DHIbody:pelvis.visibility', False)
        fp('已删除原点关节。')

    def parent_mod(self):
        grp_head = mc.group(n = 'grp_head', w = True, em = True)
        grp_body = mc.group(n = 'grp_body', w=True, em=True)
        mc.parent(self.head_mod, grp_head)
        mc.parent(self.body_mod, grp_body)
        for grp in ['headRig_grp', 'rig_setup_grp']:
            mc.parent(grp, w = True)
        mc.delete('rig')
        fp('已排布好模型。')

    def clear_scene(self):
        mc.modelEditor('modelPanel4', e=True, sdw=False)
        mc.modelEditor('modelPanel4', e=True, j=True)
        mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")')
        mc.DisplayShaded()

        for aix in ['X', 'Y', 'Z']:
            mc.setAttr('persp.rotate{}'.format(aix), 0)
        mel.eval('setUpAxis "y";')

        if os.path.exists(self.target_path):
            os.remove(self.target_path)
        fp('场景清理已完成。')