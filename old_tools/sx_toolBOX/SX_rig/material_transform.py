# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import sys
import logging

import maya.cmds as mc
import maya.OpenMayaUI as omui

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class MaterialTransform(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(MaterialTransform, self).__init__(parent)

        self.setWindowTitle(u'跨文件传递材质')
        if mc.about(ntOS=True):  # 判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # 删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.lab_lite = QtWidgets.QLabel(u'先选材质球再点run')
        self.but_filePath = QtWidgets.QPushButton(u'获取对象路径文件')
        self.lab_filePath = QtWidgets.QLabel()
        self.but_run = QtWidgets.QPushButton('R U N')

    def create_layout(self):
        getPath_layout = QtWidgets.QHBoxLayout()
        getPath_layout.addWidget(self.but_filePath)
        getPath_layout.addWidget(self.lab_filePath)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.lab_lite)
        main_layout.addLayout(getPath_layout)
        main_layout.addWidget(self.but_run)

    def create_connections(self):
        self.but_filePath.clicked.connect(self.get_path)
        self.but_run.clicked.connect(self.run_mat)

    def get_path(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, u'选择需要将材质传递到的目标文件：', '*.ma;; *.mb')
        if file_path[0]:
            if mc.file(file_path[0], ex = True, q = True):
                self.lab_filePath.setText(file_path[0])
            else:
                log.warning('{}路径文件不存在。'.format(file_path))
        else:
            log.info('没有选择任何文件。')

    def run_mat(self):
        mi_dir = self.get_mi()
        if mi_dir:
            self.judge_path(self.lab_filePath.text())
            self.set_mi(mi_dir)

    def get_mi(self):
        mi_lis = mc.ls(sl = True)
        mi_dir = {}
        for mi in mi_lis:
            if mc.nodeType(mi) != 'lambert':
                log.error('{}对象不是lambert材质球，已跳过。'.format(mi))
                break
            mc.hyperShade(mi, o = mi)
            mi_f = mc.ls(sl = True)
            for i in range(len(mi_f)):
                if '[' in mi_f[i]:
                    continue
                if mc.nodeType(mi_f[i]) == 'mesh':
                    mi_f[i] = mc.listRelatives(mi_f[i], p = True)[0]
            mi_dir[mi] = mi_f
        if mi_dir:
            return mi_dir
        else:
            log.error('没有提供有效对象。')

    def judge_path(self, path):
        if mc.file(path, q = 1, ex = True):
            if mc.file(mf=True, q=True) == True:
                ret = mc.confirmDialog(title='是否保存', message = '当前场景已被修改，是否保存后再打开目标场景？', button = ['保存', '直接打开目标场景'], defaultButton = '保存', dismissString = 'No', icn = 'warning')
                if ret == u'保存':
                    mc.file(s = True)
                elif ret == u'直接打开目标场景':
                    pass
                else:
                    sys.exit()
            mc.file(path, o = True, f = 1)
        else:
            mc.error('{}路径文件不存在。'.format(path))

    def set_mi(self, mi_dir):
        for mi in mi_dir:
            mat_obj = mi_dir[mi]
            none_lis = []
            for f in mi_dir[mi]:
                if not mc.objExists(f):
                    none_lis.append(f)
            if none_lis:
                ret = mc.confirmDialog(title='对象不存在', message='材质{}的以下着色对象不存在\n{}'.format(mi, none_lis), button=['跳过这些着色对象', '跳过该材质球'], defaultButton='跳过该材质球', dismissString='No', icn='warning')
                if ret == u'跳过这些着色对象':
                    for f in none_lis:
                        mat_obj.remove(f)
                elif ret == u'跳过该材质球':
                    continue
                else:
                    sys.exit()
            if mat_obj:
                lbt = mc.shadingNode('lambert', asShader = True, n = mi)
                lbt_sg = mc.sets(r = True, nss = True, em = True, n = '{}SG'.format(mi))
                mc.connectAttr('{}.outColor'.format(lbt), '{}.surfaceShader'.format(lbt_sg))
                mc.select(mat_obj)
                mc.sets(e = True, fe = lbt_sg)
                log.info('{}材质已转移完毕。'.format(mi))



try:
    my_window.close()
    my_window.deleteLater()
except:
    pass
finally:
    my_window = MaterialTransform()
    my_window.show()