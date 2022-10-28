# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui

import os
import json
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class TransformMaterial(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(TransformMaterial, self).__init__(parent)

        self.setWindowTitle(u'材质传递工具')
        if mc.about(ntOS=True):  # 判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # 删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.but_file_path = QtWidgets.QPushButton(self.get_scence_path())
        self.but_ex_select = QtWidgets.QPushButton(u'导出选择材质球的材质')
        self.but_ex_select.setMinimumHeight(40)
        self.but_ex_all = QtWidgets.QPushButton(u'导出场景内所有材质')
        self.but_ex_all.setMinimumHeight(40)
        self.but_imp_material = QtWidgets.QPushButton(u'导入材质')
        self.but_imp_material.setMinimumHeight(40)
        self.but_delete_useless = QtWidgets.QPushButton(u'删除场景中无用节点')

        self.line_v = QtWidgets.QFrame()
        self.line_v.setFrameShape(QtWidgets.QFrame.HLine)

    def create_layout(self):
        except_layout = QtWidgets.QHBoxLayout()
        except_layout.addWidget(self.but_ex_select)
        except_layout.addWidget(self.but_ex_all)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.but_file_path)
        main_layout.addLayout(except_layout)
        main_layout.addWidget(self.line_v)
        main_layout.addWidget(self.but_imp_material)
        main_layout.addWidget(self.but_delete_useless)

    def create_connections(self):
        self.but_file_path.clicked.connect(self.open_path)
        self.but_ex_select.clicked.connect(self.get_sel_material)
        self.but_ex_all.clicked.connect(self.get_all_material)
        self.but_imp_material.clicked.connect(self.get_json_path)
        self.but_delete_useless.clicked.connect(self.delete_unusedNode)

    def get_scence_path(self):
        '''
        获取当前场景的路径
        :return:返回场景的路径，不包含文件本身
        '''
        file_path = mc.file(exn=True, q=True)
        return os.path.dirname(file_path) + '/'

    def open_path(self):
        '''
        刷新按钮上的文件路径，在点击时打开文件路径
        :return:
        '''
        self.but_file_path.setText(self.get_scence_path())
        json_nam = mc.file(q=True, sn=True).split('.')[0]
        if os.path.exists('{}.json'.format(json_nam)):
            os.system('explorer /select, {}.json'.format(json_nam.replace('/', '\\')))
        else:
            os.startfile(self.get_scence_path())

    def get_sel_material(self):
        '''
        获取选择对象里是材质球的节点
        :return:
        '''
        sel_lis = mc.ls(sl=True)
        all_matType = mc.listNodeTypes('shader')#获取场景里所有材质节点类型，加载了第三方材质的也会被查询到
        mat_lis = []
        for obj in sel_lis:
            if mc.nodeType(obj) in all_matType:
                mat_lis.append(obj)
            else:
                log.info('{}对象不是材质球，已跳过。'.format(obj))

        if mat_lis:
            self.set_json(mat_lis)
        else:
            self.display_remind('选择对象里没有有效项用于导出材质。', 1)

    def get_all_material(self):
        '''
        获取场景内所有材质球节点,剔除默认材质球particleCloud1
        :return:
        '''
        all_mat = mc.ls(mat=True)
        all_mat.remove('particleCloud1')
        self.set_json(all_mat)

    def set_json(self, mat_lis):
        '''
        通过给定的材质球列表获取其对应的材质模型
        lambert1有两个sg节点，遂做判断，指向正确的对象
        :param mat_lis: 需要获取的材质球列表
        :return:
        '''
        mat_dir = {}
        for mat in mat_lis:
            if mat == 'lambert1':
                sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[1]
            else:
                sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[0]

            mc.hyperShade(o=mat)#将材质球的赋予对象选中
            f_lis = mc.ls(sl=True)
            if f_lis:
                f_lis.insert(0, mc.nodeType(mat))
                f_lis.insert(1, sg_node)
                mat_dir[mat] = f_lis
            else:
                self.display_remind('材质球{}没有赋予任何对象，遂跳过。'.format(mat), 0)

        file_path = mc.file(q=True, sn=True).split('.')[0]
        if os.path.exists('{}.json'.format(file_path)):
            os.remove('{}.json'.format(file_path))
            self.display_remind('当前文件路径下材质文件已存在，已删除该文件并重新生成。', 0)
        with open('{}.json'.format(file_path), 'w') as f:
            json.dump(mat_dir, f)

    def get_json_path(self):
        '''
        选择json文件，将里面的材质信息导入场景
        :return:
        '''
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, u'选择材质文件', self.get_scence_path(), '(*.json)')
        if file_path:
            with open(file_path[0], 'r') as f:
                result = json.load(f)
        else:
            self.display_remind('没有选择有效文件。', 1)
            return False

        for mat in result:
            mat_f = result[mat]
            if mc.objExists(mat):
                if mat == 'lambert1':
                    sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[1]
                else:
                    sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[0]

                if mc.nodeType(mat) != mat_f[0]:
                    self.display_remind('材质球{}存在且与原场景内的材质球类型不匹配，已跳过。', 1)
                    continue
                else:
                    if sg_node != mat_f[1]:
                        print sg_node
                        mc.rename(sg_node, mat_f[1])
                        self.display_remind('材质球{}的shadingEngine节点与原材质节点名不同，已改为{}。'.format(mat, mat_f[1]), 0)
                    for obj_f in mat_f[2:]:
                        if mc.objExists(obj_f):
                            mc.sets(obj_f, e=True, fe=mat_f[1])
                        else:
                            self.display_remind('材质球的{}赋予对象{}不存在，已跳过。'.format(mat, obj_f), 1)
                            continue
            elif mc.objExists(mat) == False:
                mat_node = mc.shadingNode(mat_f[0], asShader=True, n=mat)
                mat_SG = mc.sets(r=True, nss=True, em=True, n=mat_f[1])
                mc.connectAttr('{}.outColor'.format(mat_node), '{}.surfaceShader'.format(mat_SG))

                for obj_f in mat_f[2:]:
                    if mc.objExists(obj_f):
                        mc.sets(obj_f, e=True, fe=mat_f[1])
                    else:
                        self.display_remind('材质球的{}赋予对象{}不存在，已跳过。'.format(mat, obj_f), 1)
                        continue

            log.info('材质球{}已传递完成。'.format(mat))

    def delete_unusedNode(self):
        mm.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
        log.info('已删除场景中所有未使用节点。')

    def display_remind(self, tex, t):
        '''
        在屏幕上显示警告与报错
        :param tex: 需要显示的内容
        :param t: 显示内容是警告还是报错
        :return:
        '''
        if t == 0:
            mc.inViewMessage(amg='<font color="yellow">{}</font>'.format(tex), pos='midCenter', f=True)
            log.warning(tex)
        elif t == 1:
            mc.inViewMessage(amg = '<font color="red">{}</font>'.format(tex), pos='midCenter', f=True)
            log.error(tex)



try:
    my_mat_transform_window.close()
    my_mat_transform_window.deleteLater()
except:
    pass
finally:
    my_mat_transform_window = TransformMaterial()
    my_mat_transform_window.show()