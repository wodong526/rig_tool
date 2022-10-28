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

        self.setWindowTitle(u'���ʴ��ݹ���')
        if mc.about(ntOS=True):  # �ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.but_file_path = QtWidgets.QPushButton(self.get_scence_path())
        self.but_ex_select = QtWidgets.QPushButton(u'����ѡ�������Ĳ���')
        self.but_ex_select.setMinimumHeight(40)
        self.but_ex_all = QtWidgets.QPushButton(u'�������������в���')
        self.but_ex_all.setMinimumHeight(40)
        self.but_imp_material = QtWidgets.QPushButton(u'�������')
        self.but_imp_material.setMinimumHeight(40)
        self.but_delete_useless = QtWidgets.QPushButton(u'ɾ�����������ýڵ�')

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
        ��ȡ��ǰ������·��
        :return:���س�����·�����������ļ�����
        '''
        file_path = mc.file(exn=True, q=True)
        return os.path.dirname(file_path) + '/'

    def open_path(self):
        '''
        ˢ�°�ť�ϵ��ļ�·�����ڵ��ʱ���ļ�·��
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
        ��ȡѡ��������ǲ�����Ľڵ�
        :return:
        '''
        sel_lis = mc.ls(sl=True)
        all_matType = mc.listNodeTypes('shader')#��ȡ���������в��ʽڵ����ͣ������˵��������ʵ�Ҳ�ᱻ��ѯ��
        mat_lis = []
        for obj in sel_lis:
            if mc.nodeType(obj) in all_matType:
                mat_lis.append(obj)
            else:
                log.info('{}�����ǲ�������������'.format(obj))

        if mat_lis:
            self.set_json(mat_lis)
        else:
            self.display_remind('ѡ�������û����Ч�����ڵ������ʡ�', 1)

    def get_all_material(self):
        '''
        ��ȡ���������в�����ڵ�,�޳�Ĭ�ϲ�����particleCloud1
        :return:
        '''
        all_mat = mc.ls(mat=True)
        all_mat.remove('particleCloud1')
        self.set_json(all_mat)

    def set_json(self, mat_lis):
        '''
        ͨ�������Ĳ������б��ȡ���Ӧ�Ĳ���ģ��
        lambert1������sg�ڵ㣬�����жϣ�ָ����ȷ�Ķ���
        :param mat_lis: ��Ҫ��ȡ�Ĳ������б�
        :return:
        '''
        mat_dir = {}
        for mat in mat_lis:
            if mat == 'lambert1':
                sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[1]
            else:
                sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[0]

            mc.hyperShade(o=mat)#��������ĸ������ѡ��
            f_lis = mc.ls(sl=True)
            if f_lis:
                f_lis.insert(0, mc.nodeType(mat))
                f_lis.insert(1, sg_node)
                mat_dir[mat] = f_lis
            else:
                self.display_remind('������{}û�и����κζ�����������'.format(mat), 0)

        file_path = mc.file(q=True, sn=True).split('.')[0]
        if os.path.exists('{}.json'.format(file_path)):
            os.remove('{}.json'.format(file_path))
            self.display_remind('��ǰ�ļ�·���²����ļ��Ѵ��ڣ���ɾ�����ļ����������ɡ�', 0)
        with open('{}.json'.format(file_path), 'w') as f:
            json.dump(mat_dir, f)

    def get_json_path(self):
        '''
        ѡ��json�ļ���������Ĳ�����Ϣ���볡��
        :return:
        '''
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, u'ѡ������ļ�', self.get_scence_path(), '(*.json)')
        if file_path:
            with open(file_path[0], 'r') as f:
                result = json.load(f)
        else:
            self.display_remind('û��ѡ����Ч�ļ���', 1)
            return False

        for mat in result:
            mat_f = result[mat]
            if mc.objExists(mat):
                if mat == 'lambert1':
                    sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[1]
                else:
                    sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[0]

                if mc.nodeType(mat) != mat_f[0]:
                    self.display_remind('������{}��������ԭ�����ڵĲ��������Ͳ�ƥ�䣬��������', 1)
                    continue
                else:
                    if sg_node != mat_f[1]:
                        print sg_node
                        mc.rename(sg_node, mat_f[1])
                        self.display_remind('������{}��shadingEngine�ڵ���ԭ���ʽڵ�����ͬ���Ѹ�Ϊ{}��'.format(mat, mat_f[1]), 0)
                    for obj_f in mat_f[2:]:
                        if mc.objExists(obj_f):
                            mc.sets(obj_f, e=True, fe=mat_f[1])
                        else:
                            self.display_remind('�������{}�������{}�����ڣ���������'.format(mat, obj_f), 1)
                            continue
            elif mc.objExists(mat) == False:
                mat_node = mc.shadingNode(mat_f[0], asShader=True, n=mat)
                mat_SG = mc.sets(r=True, nss=True, em=True, n=mat_f[1])
                mc.connectAttr('{}.outColor'.format(mat_node), '{}.surfaceShader'.format(mat_SG))

                for obj_f in mat_f[2:]:
                    if mc.objExists(obj_f):
                        mc.sets(obj_f, e=True, fe=mat_f[1])
                    else:
                        self.display_remind('�������{}�������{}�����ڣ���������'.format(mat, obj_f), 1)
                        continue

            log.info('������{}�Ѵ�����ɡ�'.format(mat))

    def delete_unusedNode(self):
        mm.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
        log.info('��ɾ������������δʹ�ýڵ㡣')

    def display_remind(self, tex, t):
        '''
        ����Ļ����ʾ�����뱨��
        :param tex: ��Ҫ��ʾ������
        :param t: ��ʾ�����Ǿ��滹�Ǳ���
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