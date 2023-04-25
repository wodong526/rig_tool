# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm
import pymel.core as pm
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import logging
import sys
from feedback_tool import Feedback_info as fb_print
LINE = sys._getframe()
FILE_PATH = __file__

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def clear_orig():
    sel_lis = mc.ls(sl=1)
    for obj in sel_lis:
        for sub_node in mc.listRelatives(obj, ad=True):
            if 'Orig' in sub_node:
                mc.delete(sub_node)
                log.info('模型{}的orig节点{}已删除。'.format(obj, sub_node))
                continue


def freeze_rotation():
    objs = pm.selected()
    for obj in objs:
        if isinstance(obj, pm.nt.Joint):
            rot = obj.rotate.get()
            ra = obj.rotateAxis.get()
            jo = obj.jointOrient.get()
            rotMatrix = pm.dt.EulerRotation(rot, unit='degrees').asMatrix()
            raMatrix = pm.dt.EulerRotation(ra, unit='degrees').asMatrix()
            joMatrix = pm.dt.EulerRotation(jo, unit='degrees').asMatrix()
            rotationMatrix = rotMatrix * raMatrix * joMatrix
            tmat = pm.dt.TransformationMatrix(rotationMatrix)
            newRotation = tmat.eulerRotation()
            newRotation = [pm.dt.degrees(x) for x in newRotation.asVector()]
            obj.rotate.set(0, 0, 0)
            obj.rotateAxis.set(0, 0, 0)
            obj.jointOrient.set(newRotation)
            log.info('{}的旋转已冻结。'.format(obj))
            continue


def select_skinJoint():
    sel_lis = mc.ls(sl=1)
    jnt_lis = []
    for mod in sel_lis:
        for obj in mc.listHistory(mod, af=True):
            if mc.nodeType(obj) == 'skinCluster':
                for jnt in mc.skinCluster(obj, inf=1, q=1):
                    if jnt not in jnt_lis:
                        jnt_lis.append(jnt)
    if jnt_lis:
        mc.select(jnt_lis)
        log.info('已选中蒙皮关节。')
    else:
        log.error('选中对象没有蒙皮关节。')


def get_length():
    obj = mc.ls(sl=True, fl=True)
    n = len(obj)
    log.info('选中对象共有：{}个。对象为：{}。'.format(n, obj))


class SameName(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(SameName, self).__init__(parent)

        self.setWindowTitle(u'选择同名节点')
        if mc.about(ntOS=True):  # 判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # 删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.lin_name = QtWidgets.QLineEdit()
        self.lin_name.setAttribute(QtCore.Qt.WA_AcceptDrops)
        self.lin_name.setAlignment(QtCore.Qt.AlignCenter)
        self.lin_name.setPlaceholderText(u'填入需要选择的对象名')

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.lin_name)

    def create_connections(self):
        self.lin_name.returnPressed.connect(self.select_same)

    def select_same(self):
        sel_lis = mc.ls(l=True)
        same_lis = []
        for obj in sel_lis:
            obj_lis = obj.split('|')
            if obj_lis[-1] == self.lin_name.text():
                same_lis.append(obj)
        mc.select(same_lis)
        log.info('已选择同名节点{}。'.format(same_lis))
        self.close()

    def closeEvent(self, event):
        self.close()
        self.deleteLater()


def showSameNameWindow():
    try:
        sameNamewindow.close()
        sameNamewindow.deleteLater()
    except:
        pass
    finally:
        sameNamewindow = SameName()
        sameNamewindow.show()


def exportSelectToFbx():
    '''
    将选中的对象导出为fbx，切断开关节与控制器的链接。
    '''
    sel_lis = mc.ls(sl=1)
    if sel_lis:

        #先检查模型里有没有毛发模型
        obj_lis = []
        hair_lis = []
        for obj in sel_lis:
            for inf in mc.listRelatives(obj, ad=True):
                obj_lis.append(inf)
        if obj_lis:
            for obj in obj_lis:
                if 'Hair' in obj or 'hair' in obj:
                    if not mc.nodeType(obj) == 'joint':
                        hair_lis.append(obj)
        if hair_lis:
            mc.confirmDialog(title='警告：', message='{}\n可能是毛发模型，应该删除。'.format(hair_lis), button=['确定'])
            return None

        file_path = mc.file(exn=True, q=True)
        file_nam = file_path.split('/')[-1].split('.')[0]
        fbx_nam = 'SK'
        for nam in file_nam.split('_')[2:-1]:
            fbx_nam = fbx_nam + '_' + nam
        file_path = QtWidgets.QFileDialog.getSaveFileName(maya_main_window(), u'选择fbx文件',
                                                          file_path.replace(file_path.split('/')[-1], fbx_nam),
                                                          '(*.fbx)')  #获取导出fbx路径

        if file_path[0]:
            node_lis = []
            pert_dir = {}
            for inf in sel_lis:  #断开选择对象的父级以避免导出多于对象
                if mc.listRelatives(inf, p=True):
                    pert_dir[inf] = mc.listRelatives(inf, p=True)[0]
                    mc.parent(inf, w=True)
                else:
                    log.info('{}已在世界层级下。'.format(inf))

                if mc.listConnections(inf, d=False):
                    node_lis = mc.listConnections(inf, d=False, c=1, p=1)
                    for n in range(len(node_lis) / 2):
                        mc.disconnectAttr(node_lis[n * 2 + 1], node_lis[n * 2])
                        log.info('已断开{}。'.format(node_lis[n * 2 + 1]))

            mc.select(sel_lis)
            mc.file(file_path[0], f=True, typ='FBX export', pr=True, es=True)
            log.info('已导出{}。'.format(sel_lis))

            for n in range(len(node_lis) / 2):  #重新链接上游节点
                mc.connectAttr(node_lis[n * 2 + 1], node_lis[n * 2])
                log.info('已链接{}。'.format(node_lis[n * 2 + 1]))
            for inf in pert_dir:  # 重新p回父级
                mc.parent(inf, pert_dir[inf])

        else:
            log.error('没有选择有效路径。')

    else:
        log.error('没有选择有效对象。')

def transform_jnt_skin(outSkin_lis, obtain_jnt, mod, delete=False):
    '''
    outSkin_lis:要输出权重的关节列表
    obtain_jnt：要获取权重的关节
    mod_lis：要改变权重的模型
    delete：是否删除输出权重的关节
    '''
    cluster = mm.eval('findRelatedSkinCluster("{}")'.format(mod))
    infJnt_lis = mc.skinCluster(cluster, inf=True, q=True)#获取所有该蒙皮节点影响的关节

    for jnt in infJnt_lis:
        mc.setAttr('{}.liw'.format(jnt), True)#锁住该蒙皮节点下所有关节的权重
    mc.setAttr('{}.liw'.format(obtain_jnt), False)

    for jnt in outSkin_lis:  # 将每个关节的权重都反向给到脖子关节
        mc.select(mod)  #传递关节权重需要指定实际对象，选择或者在skinPercent的蒙皮节点名后加上模型的trs名也行
        if jnt in infJnt_lis:
            mc.setAttr('{}.liw'.format(jnt), False)
            mc.skinPercent(cluster, tv=[(jnt, 0)])
            mc.skinCluster(cluster, e=True, ri=jnt)
        else:
            fb_print('{}不在蒙皮中'.format(jnt), warning=True, path=FILE_PATH, line=LINE.f_lineno)

        if delete:#当关节不在世界下时放到世界下，将子级p给父级再把关节放到世界下，当关节在世界下时，当关节有子级时，将子级对象p到世界下
            if mc.listRelatives(jnt, p=True):
                if mc.listRelatives(jnt):
                    sub_obj = mc.listRelatives(jnt)
                    mc.parent(sub_obj, mc.listRelatives(jnt, p=True))
                mc.parent(jnt, w=True)
            else:
                if mc.listRelatives(jnt):
                    sub_obj = mc.listRelatives(jnt)
                    mc.parent(sub_obj, w=True)
            mc.delete(jnt)
    mc.setAttr('{}.liw'.format(obtain_jnt), True)

def add_skinJnt(clster, *joints):
    '''
    将关节添加进某蒙皮节点中
    :param clster: 被添加蒙皮关节的蒙皮节点
    :param joints: 要被添加进蒙皮节点的关节
    :return: None
    '''
    infJnt_lis = mc.skinCluster(clster, inf=True, q=True)
    for jnt in joints:
        if jnt not in infJnt_lis:
            mc.skinCluster(clster, e=True, lw=True, wt=0, ai=jnt)