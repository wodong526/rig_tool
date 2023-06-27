# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mel

import os
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class EXTRACT_META(object):
    def __init__(self):

        now_path = mc.internalVar(uad=True) + mc.about(v=True)
        self.target_path = '{}/target.mb'.format(now_path)

        self.main_run()

    def main_run(self):
        mc.undoInfo(ock=True)
        self.delete_useless()
        self.set_scene()
        self.del_nameSpace()
        self.rotate_headJoint()
        self.save_scene()
        cls_dir, cls_name_dir = self.get_dir()
        self.rot_headMode()
        self.set_skinCluster(cls_dir, cls_name_dir)
        self.copy_weights(cls_name_dir)
        #self.transform_neck_weight()#废弃的函数，会导致读取文件时节点读不到关节而无法驱动关节
        self.clear_scene()
        mc.undoInfo(cck=True)

    def delete_useless(self):
        # 删除无用组和模型，包括灯光和一些set集、显示层，并把头的非lod0的组删除
        del_lis = ['Lights', 'DHIbody:root', 'export_geo_GRP', 'root_drv', 'PSD', 'Body_joints']
        mc.delete(del_lis)

        mc.parent('head_grp', w=True)
        mc.delete('rig')

        for i in range(4):
            mc.delete('body_lod{}_layer'.format(i))
        for i in range(8):
            mc.delete('head_lod{}_layer'.format(i))
            if i == 0:
                continue
            mc.delete('head_lod{}_grp'.format(i))
        log.info('已清理无用大纲、显示层、LOD。')

    def set_scene(self):
        # 将摄像机轴向放正,将场景转为Y轴向上，显示关节
        for aix in ['X', 'Y', 'Z']:
            mc.setAttr('persp.rotate{}'.format(aix), 0)
        mel.eval('setUpAxis "y";')
        mc.modelEditor('modelPanel4', e=True, j=True)
        log.info('已掰直摄像机、场景换为Y轴向上、显示场景中的关节。')

    def del_nameSpace(self):
        # 通过遍历场景所有空间名并删除非默认空间名
        nsLs = mc.namespaceInfo(lon=True)
        defaultNs = ["UI", "shared", "mod"]
        pool = [item for item in nsLs if item not in defaultNs]
        for ns in pool:
            mc.namespace(rm=ns, mnr=1, f=1)
            log.info('已清理空间名{}。'.format(ns))

    def rotate_headJoint(self):
        # 用一个新的组将骨架掰直，头的模型会因为蒙皮也一起被掰直
        mc.group(n='grp_rotHead_001', w=True, em=True)
        mc.parent('spine_04', 'grp_rotHead_001')
        mc.setAttr('grp_rotHead_001.rx', -90)
        mc.setAttr('LOC_world.rx', -90)
        mc.parent('spine_04', w=True)
        mc.delete('grp_rotHead_001')
        log.info('已掰直蒙皮骨架。')

    def save_scene(self):
        # 另存场景，并保存一份target文件用于后面拷贝权重
        mc.SaveSceneAs()    

        self.mod_lis = mc.listRelatives('head_lod0_grp')
        mc.select(self.mod_lis)
        mc.select('spine_04', add=True)
        mc.file(self.target_path, f=True, es=True, typ='mayaBinary', op='v = 1', pr=True)
        log.info('已另存场景并保存目标权重文件。')

    def get_dir(self):
        # 获取两个字典，模型名：对该模型蒙皮的关节列表、模型名：cluster节点名，并删除蒙皮节点
        cls_dir = {}
        cls_name_dir = {}
        for trs in self.mod_lis:
            shp = mc.listRelatives(trs, s=1)[0]
            clst = mc.listConnections(shp, t='skinCluster', et=True)[0]
            jnt = mc.listConnections(clst, t='joint', et=True)
            cls_dir[trs] = jnt
            cls_name_dir[trs] = clst
            mc.delete(clst)
        log.info('已获取蒙皮关节与蒙皮节点名的字典。')
        return cls_dir, cls_name_dir

    def rot_headMode(self):
        # 用新生成的组将因为删除蒙皮节点后模型返回原位
        mc.group(n='grp_rotMod_001', w=True, em=True)
        mc.parent(self.mod_lis, 'grp_rotMod_001')
        mc.setAttr('grp_rotMod_001.rx', -90)
        for obj in self.mod_lis:
            for aix in ['X', 'Y', 'Z']:
                mc.setAttr('{}.translate{}'.format(obj, aix), l=False)
                mc.setAttr('{}.rotate{}'.format(obj, aix), l=False)
                mc.setAttr('{}.scale{}'.format(obj, aix), l=False)
        mc.makeIdentity('grp_rotMod_001', a=True, r=True, n=False, pn=True)
        mc.parent(self.mod_lis, 'head_lod0_grp')
        mc.delete('grp_rotMod_001')
        log.info('已掰直头的模型。')

    def set_skinCluster(self, cls_dir, cls_name_dir):
        # 将模型与关节重新做蒙皮，蒙皮节点名和原来一样
        for clst in cls_dir:
            jnt_lis = []
            for jnt in cls_dir[clst]:
                jnt_lis.append(jnt)
            jnt_lis.append(clst)
            mc.skinCluster(jnt_lis, tsb=True, n=cls_name_dir[clst])
        log.info('已重给蒙皮。')

    def copy_weights(self, cls_name_dir):
        # 将保存的target文件引用进来对现在的蒙皮进行拷贝，通过蒙皮节点进行拷贝
        mc.file(self.target_path, r=True, typ='mayaBinary', ns='tst')
        for obj in cls_name_dir:
            mc.copySkinWeights(ss='tst:{}'.format(cls_name_dir[obj]), ds=cls_name_dir[obj], nm=True, sa='closestPoint',
                               ia='closestJoint')
            log.info('已传递{}蒙皮。'.format(cls_name_dir[obj]))
            mc.select(obj)
            mc.BakeNonDefHistory()
        mc.file(self.target_path, rr=True)

    def transform_neck_weight(self):
        neck_2_subJoint = mc.listRelatives('FACIAL_C_Neck2Root')  # 获取FACIAL_C_Neck2Root下的所有关节
        neck_1_subJoint = mc.listRelatives('FACIAL_C_Neck1Root')  # 获取FACIAL_C_Neck1Root下的所有关节
        mc.skinCluster('head_lod0_mesh_skinCluster', e=True, lw=True, wt=0, ai='neck_01')  # 将neck_01加入到模型的蒙皮里
        mc.skinCluster('head_lod0_mesh_skinCluster', e=True, lw=True, wt=0, ai='neck_02')  # 将neck_02加入到模型的蒙皮里
        for jnt in mc.skinCluster('head_lod0_mesh_skinCluster', inf=True, q=1):  # 全锁所有关节
            mc.setAttr('{}.liw'.format(jnt), True)

        mc.setAttr('neck_01.liw', False)  # 单开脖子关节
        skin_jnt_lis = mc.skinCluster('head_lod0_mesh_skinCluster', inf=True, q=True)#获取所有该蒙皮节点影响的关节
        mc.select('head_lod0_mesh')#传递关节权重需要指定实际对象，选择或者在skinPercent的蒙皮节点名后加上模型的trs名也行
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

    def clear_scene(self):
        # 将显示贴图和灯光、显示阴影关掉，将无用材质节点删除 
        mc.modelEditor('modelPanel4', e=True, sdw=False)
        mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")')
        mc.DisplayShaded()
        mc.setAttr('CTRL_faceGUIfollowHead.ty', True)
        mc.setAttr('CTRL_eyesAimFollowHead.ty', True)
        log.info('扣头完毕。')

        try:
            if os.path.exists(self.target_path):
                os.remove(self.target_path)
        except:
            log.error('文档中备份蒙皮文件夹仍然存在，因为删除时出错了。')

