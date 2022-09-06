# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.mel as mel
import maya.OpenMayaUI as omui

import os
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class EXTRACT_META(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(EXTRACT_META, self).__init__(parent)

        self.setWindowTitle(u'Meta��ͷ��')
        if mc.about(ntOS=True):  # �ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        now_path = mc.internalVar(uad=True) + mc.about(v=True)
        self.target_path = '{}/target.mb'.format(now_path)

    def create_widgets(self):
        self.tips_lab = QtWidgets.QLabel(u'ʲôҲ���ùܣ���run�����ˡ�')
        self.run_but = QtWidgets.QPushButton(u'<< R U N >>')

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.tips_lab)
        main_layout.addWidget(self.run_but)

    def create_connections(self):
        self.run_but.clicked.connect(self.main_run)

    def main_run(self):
        self.delete_useless()
        self.set_scene()
        self.del_nameSpace()
        self.rotate_headJoint()
        self.save_scene()
        cls_dir, cls_name_dir = self.get_dir()
        self.rot_headMode()
        self.set_skinCluster(cls_dir, cls_name_dir)
        self.copy_weights(cls_name_dir)
        self.clear_scene()

    def delete_useless(self):
        del_lis = ['Lights', 'DHIbody:root', 'export_geo_GRP', 'root_drv', 'PSD', 'Body_joints', 'FacialControls']
        mc.delete(del_lis)

        mc.parent('head_grp', w = True)
        mc.delete('rig')

        for i in range(4):
            mc.delete('body_lod{}_layer'.format(i))
        for i in range(8):
            mc.delete('head_lod{}_layer'.format(i))
            if i == 0:
                continue
            mc.delete('head_lod{}_grp'.format(i))
        log.info('���������ô�١���ʾ�㡢LOD��')

    def set_scene(self):
        mc.setAttr('persp.rotateZ', 0)
        mel.eval('setUpAxis "y";')
        mc.modelEditor('modelPanel4', e = True, j = True)
        log.info('����ֱ�������������ΪY�����ϡ���ʾ�����еĹؽڡ�')

    def del_nameSpace(self):
        nsLs = mc.namespaceInfo(lon=True)
        defaultNs = ["UI", "shared", "mod"]
        pool = [item for item in nsLs if item not in defaultNs]
        for ns in pool:
            mc.namespace(rm=ns, mnr=1, f=1)
            log.info('������ռ���{}��'.format(ns))

    def rotate_headJoint(self):
        mc.group(n='grp_rotHead_001', w=True, em=True)
        mc.parent('spine_04', 'grp_rotHead_001')
        mc.setAttr('grp_rotHead_001.rx', -90)
        mc.setAttr('LOC_world.rx', -90)
        mc.parent('spine_04', w=True)
        mc.delete('grp_rotHead_001')
        log.info('����ֱ��Ƥ�Ǽܡ�')

    def save_scene(self):
        mc.SaveSceneAs()

        self.mod_lis = mc.listRelatives('head_lod0_grp')
        mc.select(self.mod_lis)
        mc.select('spine_04', add=True)
        mc.file(self.target_path, f=True, es=True, typ='mayaBinary', op='v = 1', pr=True)
        log.info('����泡��������Ŀ��Ȩ���ļ���')

    def get_dir(self):
        cls_dir = {}
        cls_name_dir = {}
        for trs in self.mod_lis:
            shp = mc.listRelatives(trs, s=1)[0]
            clst = mc.listConnections(shp, t='skinCluster', et=True)[0]
            jnt = mc.listConnections(clst, t='joint', et=True)
            cls_dir[trs] = jnt
            cls_name_dir[trs] = clst
            mc.delete(clst)
        log.info('�ѻ�ȡ��Ƥ�ؽ�����Ƥ�ڵ������ֵ䡣')
        return cls_dir, cls_name_dir

    def rot_headMode(self):
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
        log.info('����ֱͷ��ģ�͡�')

    def set_skinCluster(self, cls_dir, cls_name_dir):
        for clst in cls_dir:
            jnt_lis = []
            for jnt in cls_dir[clst]:
                jnt_lis.append(jnt)
            jnt_lis.append(clst)
            mc.skinCluster(jnt_lis, tsb=True, n=cls_name_dir[clst])
        log.info('���ظ���Ƥ��')

    def copy_weights(self, cls_name_dir):
        mc.file(self.target_path, r=True, typ='mayaBinary', ns='tst')
        for obj in cls_name_dir:
            mc.copySkinWeights(ss='tst:{}'.format(cls_name_dir[obj]), ds=cls_name_dir[obj], nm=True, sa='closestPoint',
                               ia='closestJoint')
            log.info('�Ѵ���{}��Ƥ��'.format(cls_name_dir[obj]))
            mc.select(obj)
            mc.BakeNonDefHistory()
        mc.file(self.target_path, rr=True)

    def clear_scene(self):
        mc.modelEditor('modelPanel4', e=True, sdw=False)
        mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")')
        mc.DisplayShaded()

    def closeEvent(self, event):
        '''
        qt���ڹر��Ǵ����ĸú���
        '''
        try:
            if os.path.exists(self.target_path):
                os.remove(self.target_path)
        except:
            log.error('�ĵ��б�����Ƥ�ļ�����Ȼ���ڣ���Ϊɾ��ʱ�����ˡ�')

try:
    my_window.close()
    my_window.deleteLater()
except:
    pass
finally:
    my_window = EXTRACT_META()
    my_window.show()