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
        all_matType = mc.listNodeTypes('shader')  #获取场景里所有材质节点类型，加载了第三方材质的也会被查询到
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

    def get_mat_color(self, mat):
        try:
            node_lis = mc.listConnections(mat, d=False)
            if node_lis:
                for inf in node_lis:
                    if mc.nodeType(inf) == 'file':
                        img_path = mc.getAttr('{}.fileTextureName'.format(inf))
                        return ['file', inf, img_path]
            return ['color', mc.getAttr('{}.color'.format(mat))[0]]
        except:
            self.display_remind('材质球{}似乎没有颜色输出属性，或者输出有误。无法导出颜色。'.format(mat), 0)
            return None

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
            elif mc.nodeType(mat) == 'dx11Shader':
                self.display_remind('材质球{}的类型不能是dx11，请更换成其它Maya自带的材质球类型。'.format(mat), 1)
                return None
            else:
                sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[0]

            mc.hyperShade(o=mat)  #将材质球的赋予对象选中
            f_lis = mc.ls(sl=True)
            if f_lis:
                color = self.get_mat_color(mat)

                f_lis.insert(0, mc.nodeType(mat))#第一位是材质球类型
                f_lis.insert(1, sg_node)#第二位是着色组名字
                f_lis.insert(2, color)#第三位是颜色
                mat_dir[mat] = f_lis
            else:
                self.display_remind('材质球{}没有赋予任何对象，遂跳过。'.format(mat), 0)

        file_path = mc.file(q=True, sn=True).split('.')[0]
        if os.path.exists('{}.json'.format(file_path)):
            os.remove('{}.json'.format(file_path))
            self.display_remind('当前文件路径下材质文件已存在，已删除该文件并重新生成。', 0)
        with open('{}.json'.format(file_path), 'w') as f:
            json.dump(mat_dir, f, indent=4)

    def get_json_path(self):
        '''
        选择json文件，将里面的材质信息导入场景
        :return:
        '''
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, u'选择材质文件', self.get_scence_path(), '(*.json)')
        if file_path[0]:
            with open(file_path[0], 'r') as f:
                result = json.load(f)
        else:
            self.display_remind('没有选择有效文件。', 1)
            return False

        for mat in result:#mat是材质球名
            mat_f = result[mat]#mat_f是key对应的内容
            if mc.objExists(mat):
                if mat == 'lambert1':
                    sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[1]
                else:
                    sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[0]

                if mc.nodeType(mat) != mat_f[0]:#材质球命相同 但材质球类型不同，跳过赋予材质。
                    self.display_remind('材质球{}存在且与原场景内的材质球类型不匹配，已跳过。'.format(mat), 1)
                    continue
                else:
                    if sg_node != mat_f[1]:#材质球名相同，但着色组名字不同，强制改为相同着色组
                        mc.rename(sg_node, mat_f[1])
                        self.display_remind('材质球{}的着色组节点与原材质节点名不同，已改为{}。'.format(mat, mat_f[1]), 0)
                    for obj_f in mat_f[3:]:#赋予材质
                        if mc.objExists(obj_f):#模型对象存在时，赋予，不存在时警告
                            mc.sets(obj_f, e=True, fe=mat_f[1])
                        else:
                            self.display_remind('材质球的{}赋予对象{}不存在，已跳过。'.format(mat, obj_f), 1)
                            continue

            elif mc.objExists(mat) == False:#如果材质球不存在就新建材质球
                mat_node = mc.shadingNode(mat_f[0], asShader=True, n=mat)
                if mc.objExists(mat_f[1]):#如果材质球对应的着色组存在就直接使用这个着色组
                    mc.connectAttr('{}.outColor'.format(mat_node), '{}.surfaceShader'.format(mat_f[1]), f=True)
                else:#如果着色组不存在就新建
                    mat_SG = mc.sets(r=True, nss=True, em=True, n=mat_f[1])
                    mc.connectAttr('{}.outColor'.format(mat_node), '{}.surfaceShader'.format(mat_SG))

                for obj_f in mat_f[3:]:#赋予材质
                    if mc.objExists(obj_f):
                        mc.sets(obj_f, e=True, fe=mat_f[1])
                    else:
                        self.display_remind('材质球的{}赋予对象{}不存在，已跳过。'.format(mat, obj_f), 1)
                        continue

            self.set_color(mat, mat_f)#设置颜色
            log.info('材质球{}已传递完成。'.format(mat))

    def set_color(self, nam, mat_f):
        if mat_f[2] == None:#如果有些材质球没有颜色属性，跳过
            self.display_remind('材质球{}没有携带颜色，注意查看原文件的该材质球是否有颜色。'.format(nam), 0)
        elif mat_f[2][0] == 'color':#当有颜色属性，且没有上级贴图文件时，直接赋予材质颜色
            mc.setAttr('{}.color'.format(nam), mat_f[2][1][0], mat_f[2][1][1], mat_f[2][1][2])
        elif mat_f[2][0] == 'file':#当材质球上级有贴图文件时，创建贴图文件并加载贴图路径
            mc.delete(mc.listConnections(nam, d=False))
            if mc.objExists(mat_f[2][1]):
                mc.delete(mat_f[2][1])
            fil = mc.shadingNode('file', at=True, icm=True, n=mat_f[2][1])
            plac_tex = mc.shadingNode('place2dTexture', au=True)
            fil_lis = ['coverage', 'translateFrame', 'rotateFrame', 'mirrorU', 'mirrorV', 'stagger', 'wrapU', 'wrapV',
                       'repeatUV', 'offset', 'rotateUV', 'noiseUV', 'vertexUvOne', 'vertexUvTwo', 'vertexUvThree',
                       'vertexCameraOne', 'uv', 'uvFilterSize']
            plac_lis = ['coverage', 'translateFrame', 'rotateFrame', 'mirrorU', 'mirrorV', 'stagger', 'wrapU', 'wrapV',
                        'repeatUV','offset', 'rotateUV', 'noiseUV', 'vertexUvOne', 'vertexUvTwo', 'vertexUvThree',
                        'vertexCameraOne', 'outUV', 'outUvFilterSize']
            for inf in zip(plac_lis, fil_lis):
                mc.connectAttr('{}.{}'.format(plac_tex, inf[0]), '{}.{}'.format(fil, inf[1]))
            mc.setAttr('{}.fileTextureName'.format(fil), mat_f[2][2], typ='string')
            mc.connectAttr('{}.outColor'.format(fil), '{}.color'.format(nam))
            log.info('已创建贴图文件节点{}，贴图路径为{}。'.format(fil, mat_f[2][2]))
        else:
            self.display_remind('材质球{}有问题。'.format(nam), 1)

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
            mc.inViewMessage(amg='<font color="red">{}</font>'.format(tex), pos='midCenter', f=True)
            log.error(tex)


try:
    my_mat_transform_window.close()
    my_mat_transform_window.deleteLater()
except:
    pass
finally:
    my_mat_transform_window = TransformMaterial()
    my_mat_transform_window.show()