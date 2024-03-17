# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui

import os
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class TRANSFORMATION_META(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(TRANSFORMATION_META, self).__init__(parent)

        self.setWindowTitle(u'Transformation_to_metaHead')
        if mc.about(ntOS=True):  # 判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # 删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        now_path = mc.internalVar(uad=True) + mc.about(v=True)
        self.target_path = '{}/target.mb'.format(now_path)

    def create_widgets(self):
        self.getMod_but = QtWidgets.QPushButton(u'获取其下所有模型')
        self.getMod_but.setToolTip(u'将选中对象及其子级对象中的所有模型获取')

        self.Mod_cbx = QtWidgets.QCheckBox()
        self.Mod_cbx.setEnabled(False)

        self.crat_but = QtWidgets.QPushButton(u'生成目标')
        self.crat_but.setEnabled(False)
        self.crat_but.setToolTip(u'生成头部模型目标，调控目标到合适位置')
        self.mach_but = QtWidgets.QPushButton(u'匹配目标')
        self.mach_but.setEnabled(False)
        self.mach_but.setToolTip(u'将权重关节等匹配到目标变换')

    def create_layout(self):
        getMod_layout = QtWidgets.QHBoxLayout()
        getMod_layout.addWidget(self.getMod_but)
        getMod_layout.addWidget(self.Mod_cbx)

        setMod_layout = QtWidgets.QHBoxLayout()
        setMod_layout.addWidget(self.crat_but)
        setMod_layout.addWidget(self.mach_but)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(getMod_layout)
        main_layout.addLayout(setMod_layout)

    def create_connections(self):
        self.getMod_but.clicked.connect(self.get_mod)
        self.crat_but.clicked.connect(self.run_transformation)
        self.mach_but.clicked.connect(self.match_transformation)

    def run_transformation(self):
        self.save_scene()  #保存场景并复制出备用蒙皮场景
        self.set_transformation()

    def get_mod(self):
        sel_lis = mc.ls(sl=True)
        mod_lis = []
        self.modAll_lis = []  #所有模型对象
        for obj in sel_lis:
            if mc.nodeType(mc.listRelatives(obj, s=True)) == 'mesh':
                mod_lis.append(obj)
            self.modAll_lis = self.modAll_lis + self.get_subMod(obj, mod_lis)

        self.mod_parent = {}  #模型名：模型父级名
        for obj in self.modAll_lis:
            p = mc.listRelatives(obj, p=True)
            self.mod_parent[obj] = p[0]

        if self.modAll_lis:
            self.Mod_cbx.setChecked(True)
            self.crat_but.setEnabled(True)
            self.mach_but.setEnabled(True)
        else:
            self.Mod_cbx.setChecked(False)
            log.error('没有获取有效对象。')
            return False

    def get_subMod(self, trs, lis):
        trs_lis = mc.listRelatives(trs)
        for obj in trs_lis:
            shp = mc.listRelatives(obj, s=True)
            if shp:
                if mc.nodeType(shp[0]) == 'mesh':
                    lis.append(obj)
            if mc.listRelatives(obj):
                self.get_subMod(obj, lis)
        return lis

    def save_scene(self):
        mc.select(self.modAll_lis)
        mc.select('spine_04', add=True)
        mc.file(self.target_path, f=True, es=True, typ='mayaBinary', op='v = 1', pr=True)
        # new_path = mc.file(q=True, exn=True)
        # copyfile(new_path, self.target_path)
        # mc.file(rn = self.target_path)
        # mc.file(f = True, s = True, typ = 'mayaBinary')

    def set_transformation(self):
        for obj in self.modAll_lis:
            if 'head' in obj:
                self.head_mod = obj  #头部模型的名字
                res_mod = mc.duplicate(obj, n='reference_head')
                mc.parent(res_mod, w=True)
        if res_mod:
            box = mc.xform(res_mod, q=True, bb=True)
            self.t = [(box[0] + box[3]) / 2, (box[1] + box[4]) / 2, box[5]]
            mc.spaceLocator(n='reference_target', p=self.t)
            mc.setAttr('reference_target.rotateY', l=True)
            mc.setAttr('reference_target.rotateZ', l=True)
            mc.xform('reference_target', piv=self.t)
            mc.parent(res_mod, 'reference_target')
            mc.select('reference_target')

            for obj in self.modAll_lis:
                mc.setAttr('{}.visibility'.format(obj), False)
            mc.setAttr('spine_04.visibility', False)

    def match_transformation(self):
        cls_dir, cls_name_dir = self.get_dir()
        self.duplicate_joints()

        for clst in cls_name_dir:
            mc.delete(cls_name_dir[clst])

        pos = mc.xform('reference_target', t=True, q=True)
        rot = mc.xform('reference_target', ro=True, q=True)
        scl = mc.xform('reference_target', s=True, q=True)

        self.create_attr(pos, rot, scl)

        self.rot_mod(pos, rot, scl)
        self.trs_joint(pos, rot, scl)
        self.trs_drvJoint(pos, rot, scl)

        self.create_skin(cls_dir, cls_name_dir)
        self.connect_jnt(cls_dir)

        self.reference_target(pos, rot, scl)
        self.copy_weigths(cls_name_dir)
        self.clear_scene()

    def get_dir(self):
        cls_dir = {}
        cls_name_dir = {}
        for trs in self.modAll_lis:
            shp = mc.listRelatives(trs, s=1)[0]
            clst = mc.listConnections(shp, t='skinCluster', et=True)[0]
            jnt = mc.listConnections(clst, t='joint', et=True)
            cls_dir[trs] = jnt
            cls_name_dir[trs] = clst
        return cls_dir, cls_name_dir

    def duplicate_joints(self):
        jnt_lis = []
        jnt_chain = self.get_subJnt('spine_04', jnt_lis)
        jnt_chain.insert(0, 'spine_04')

        for jnt in jnt_chain:
            mc.rename(jnt, 'drv_{}'.format(jnt))
            new_jnt = mc.duplicate('drv_{}'.format(jnt), n=jnt, po=True)[0]
            if jnt == 'spine_04':
                continue
            essence_jnt = mc.listRelatives('drv_{}'.format(jnt), p=True)[0]
            mc.parent(new_jnt, essence_jnt.split('_', 1)[-1])

    def get_subJnt(self, jnt, jnt_lis):
        new_jnt = mc.listRelatives(jnt)
        for f in new_jnt:
            jnt_lis.append(f)
            if mc.listRelatives(f):
                self.get_subJnt(f, jnt_lis)
        return jnt_lis

    def rot_mod(self, pos, rot, scl):
        #使模型回到原位
        # mc.group(n = 'grp_moveMod_001', w = True, em = True)
        # for obj in self.modAll_lis:
        #     mc.parent(obj, 'grp_moveMod_001')
        #     for aix in ['X', 'Y', 'Z']:
        #         mc.setAttr('{}.translate{}'.format(obj, aix), l=False)
        #         mc.setAttr('{}.rotate{}'.format(obj, aix), l=False)
        #         mc.setAttr('{}.scale{}'.format(obj, aix), l=False)
        # mc.setAttr('grp_moveMod_001.rotateX', -90)
        # mc.makeIdentity('grp_moveMod_001', a = True, r = True, n = False, pn = True)

        # #将模型都p出来
        # for obj in self.modAll_lis:
        #     mc.parent(obj, w = True)
        # mc.delete('grp_moveMod_001')

        #生成新的组对模型进行变换
        mc.group(n='grp_moveMod_001', w=True, em=True)
        mc.xform('grp_moveMod_001', ws=True, t=self.t)
        mc.makeIdentity('grp_moveMod_001', a=True, t=True, n=False, pn=True)
        for obj in self.modAll_lis:
            mc.parent(obj, 'grp_moveMod_001')
            for aix in ['X', 'Y', 'Z']:
                mc.setAttr('{}.translate{}'.format(obj, aix), l=False)
                mc.setAttr('{}.rotate{}'.format(obj, aix), l=False)
                mc.setAttr('{}.scale{}'.format(obj, aix), l=False)
        mc.xform('grp_moveMod_001', t=pos, ro=rot, s=scl)
        mc.makeIdentity('grp_moveMod_001', a=True, t=True, r=True, s=True, n=False, pn=True)

        #将模型p出来并删除原来的组
        for obj in self.mod_parent:
            mc.parent(obj, self.mod_parent[obj])
        mc.delete('grp_moveMod_001')

    def trs_joint(self, pos, rot, scl):
        mc.group(n='grp_moveJnt_001', w=True, em=True)
        mc.xform('grp_moveJnt_001', ws=True, t=self.t)
        mc.makeIdentity('grp_moveJnt_001', a=True, t=True, n=False, pn=True)
        mc.parent('spine_04', 'grp_moveJnt_001')
        mc.xform('grp_moveJnt_001', t=pos, ro=rot, s=scl)
        mc.makeIdentity('grp_moveJnt_001', a=True, s=True, n=False, pn=True)
        mc.parent('spine_04', w=True)
        mc.delete('grp_moveJnt_001')

    def trs_drvJoint(self, pos, rot, scl):
        mc.group(n='grp_moveDrvJnt_001', w=True, em=True)
        mc.xform('grp_moveDrvJnt_001', ws=True, t=self.t)
        mc.makeIdentity('grp_moveDrvJnt_001', a=True, t=True, n=False, pn=True)
        mc.parent('drv_spine_04', 'grp_moveDrvJnt_001')
        mc.xform('grp_moveDrvJnt_001', t=pos, ro=rot, s=scl)

    def create_skin(self, cls_dir, cls_name_dir):
        for clst in cls_dir:
            jnt_lis = []
            for jnt in cls_dir[clst]:
                jnt_lis.append(jnt)
            jnt_lis.append(clst)
            mc.skinCluster(jnt_lis, tsb=True, n=cls_name_dir[clst])

    def connect_jnt(self, cls_dir):
        if mc.objExists('xform'):
            if mc.objExists('connects'):
                pass
            else:
                mc.group(n='connects', p='xform', em=True)
        else:
            mc.group(n='xform', em=True, w=True)
            mc.group(n='connects', p='xform', em=True)

        conn_lis = []
        for clst in cls_dir:
            for jnt in cls_dir[clst]:
                if jnt not in conn_lis:
                    conn_lis.append(jnt)
        for jnt in conn_lis:
            par_con = mc.parentConstraint('drv_{}'.format(jnt), jnt)
            mc.parent(par_con, 'connects')

    def reference_target(self, pos, rot, scl):
        mc.file(self.target_path, r=True, typ='mayaBinary', ns='tst')

        mc.group(n='grp_refJnt_001', w=True, em=True)
        mc.xform('grp_refJnt_001', ws=True, t=self.t)
        mc.makeIdentity('grp_refJnt_001', a=True, t=True, n=False, pn=True)
        mc.parent('tst:spine_04', 'grp_refJnt_001')
        mc.xform('grp_refJnt_001', t=pos, ro=rot, s=scl)

    def copy_weigths(self, clst_lis):
        for obj in clst_lis:
            mc.copySkinWeights(ss='tst:{}'.format(clst_lis[obj]), ds=clst_lis[obj], nm=True, sa='closestPoint',
                               ia='closestJoint')

    def clear_scene(self):
        mc.delete('reference_target')
        for obj in self.modAll_lis:
            mc.select(obj)
            mc.BakeNonDefHistory()
            mc.setAttr('{}.visibility'.format(obj), True)
        mc.setAttr('spine_04.visibility', True)

        mc.file(self.target_path, rr=True)
        mc.delete('grp_refJnt_001')
        log.info('转换完毕。')

    def create_attr(self, pos, rot, scl):
        attr_dir = {'head_translate': '位移', 'head_rotate': '旋转', 'head_scale': '缩放'}
        aix_lis = ['X', 'Y', 'Z']
        if mc.objExists('{}.head_translate'.format(self.head_mod)):
            for attr in attr_dir:
                mc.deleteAttr('{}.{}'.format(self.head_mod, attr))
        else:
            for attr in attr_dir:
                mc.addAttr(self.head_mod, ln=attr, nn=attr_dir[attr], at='double3', k=False)
                for aix in aix_lis:
                    mc.addAttr(self.head_mod, ln='{}_{}'.format(attr, aix), nn='{}_{}'.format(attr_dir[attr], aix),
                               at='double', p=attr, k=False)

        for i in range(3):
            mc.setAttr('{}.head_translate_{}'.format(self.head_mod, aix_lis[i]), pos[i], cb=True, l=True)
            mc.setAttr('{}.head_rotate_{}'.format(self.head_mod, aix_lis[i]), rot[i], cb=True, l=True)
            mc.setAttr('{}.head_scale_{}'.format(self.head_mod, aix_lis[i]), scl[i], cb=True, l=True)

    def closeEvent(self, event):
        """
        qt窗口关闭是触发的该函数
        """
        try:
            if os.path.exists(self.target_path):
                os.remove(self.target_path)
        except:
            log.error('文档中备份蒙皮文件夹仍然存在，因为删除时出错了。')


def transform_head():
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = TRANSFORMATION_META()
        my_window.show()
