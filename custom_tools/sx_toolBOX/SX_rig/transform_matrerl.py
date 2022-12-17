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
        all_matType = mc.listNodeTypes('shader')  #��ȡ���������в��ʽڵ����ͣ������˵��������ʵ�Ҳ�ᱻ��ѯ��
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
            self.display_remind('������{}�ƺ�û����ɫ������ԣ�������������޷�������ɫ��'.format(mat), 0)
            return None

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
            elif mc.nodeType(mat) == 'dx11Shader':
                self.display_remind('������{}�����Ͳ�����dx11�������������Maya�Դ��Ĳ��������͡�'.format(mat), 1)
                return None
            else:
                sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[0]

            mc.hyperShade(o=mat)  #��������ĸ������ѡ��
            f_lis = mc.ls(sl=True)
            if f_lis:
                color = self.get_mat_color(mat)

                f_lis.insert(0, mc.nodeType(mat))#��һλ�ǲ���������
                f_lis.insert(1, sg_node)#�ڶ�λ����ɫ������
                f_lis.insert(2, color)#����λ����ɫ
                mat_dir[mat] = f_lis
            else:
                self.display_remind('������{}û�и����κζ�����������'.format(mat), 0)

        file_path = mc.file(q=True, sn=True).split('.')[0]
        if os.path.exists('{}.json'.format(file_path)):
            os.remove('{}.json'.format(file_path))
            self.display_remind('��ǰ�ļ�·���²����ļ��Ѵ��ڣ���ɾ�����ļ����������ɡ�', 0)
        with open('{}.json'.format(file_path), 'w') as f:
            json.dump(mat_dir, f, indent=4)

    def get_json_path(self):
        '''
        ѡ��json�ļ���������Ĳ�����Ϣ���볡��
        :return:
        '''
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, u'ѡ������ļ�', self.get_scence_path(), '(*.json)')
        if file_path[0]:
            with open(file_path[0], 'r') as f:
                result = json.load(f)
        else:
            self.display_remind('û��ѡ����Ч�ļ���', 1)
            return False

        for mat in result:#mat�ǲ�������
            mat_f = result[mat]#mat_f��key��Ӧ������
            if mc.objExists(mat):
                if mat == 'lambert1':
                    sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[1]
                else:
                    sg_node = mc.listConnections('{}.outColor'.format(mat), s=False, t='shadingEngine', et=True)[0]

                if mc.nodeType(mat) != mat_f[0]:#����������ͬ �����������Ͳ�ͬ������������ʡ�
                    self.display_remind('������{}��������ԭ�����ڵĲ��������Ͳ�ƥ�䣬��������'.format(mat), 1)
                    continue
                else:
                    if sg_node != mat_f[1]:#����������ͬ������ɫ�����ֲ�ͬ��ǿ�Ƹ�Ϊ��ͬ��ɫ��
                        mc.rename(sg_node, mat_f[1])
                        self.display_remind('������{}����ɫ��ڵ���ԭ���ʽڵ�����ͬ���Ѹ�Ϊ{}��'.format(mat, mat_f[1]), 0)
                    for obj_f in mat_f[3:]:#�������
                        if mc.objExists(obj_f):#ģ�Ͷ������ʱ�����裬������ʱ����
                            mc.sets(obj_f, e=True, fe=mat_f[1])
                        else:
                            self.display_remind('�������{}�������{}�����ڣ���������'.format(mat, obj_f), 1)
                            continue

            elif mc.objExists(mat) == False:#��������򲻴��ھ��½�������
                mat_node = mc.shadingNode(mat_f[0], asShader=True, n=mat)
                if mc.objExists(mat_f[1]):#����������Ӧ����ɫ����ھ�ֱ��ʹ�������ɫ��
                    mc.connectAttr('{}.outColor'.format(mat_node), '{}.surfaceShader'.format(mat_f[1]), f=True)
                else:#�����ɫ�鲻���ھ��½�
                    mat_SG = mc.sets(r=True, nss=True, em=True, n=mat_f[1])
                    mc.connectAttr('{}.outColor'.format(mat_node), '{}.surfaceShader'.format(mat_SG))

                for obj_f in mat_f[3:]:#�������
                    if mc.objExists(obj_f):
                        mc.sets(obj_f, e=True, fe=mat_f[1])
                    else:
                        self.display_remind('�������{}�������{}�����ڣ���������'.format(mat, obj_f), 1)
                        continue

            self.set_color(mat, mat_f)#������ɫ
            log.info('������{}�Ѵ�����ɡ�'.format(mat))

    def set_color(self, nam, mat_f):
        if mat_f[2] == None:#�����Щ������û����ɫ���ԣ�����
            self.display_remind('������{}û��Я����ɫ��ע��鿴ԭ�ļ��ĸò������Ƿ�����ɫ��'.format(nam), 0)
        elif mat_f[2][0] == 'color':#������ɫ���ԣ���û���ϼ���ͼ�ļ�ʱ��ֱ�Ӹ��������ɫ
            mc.setAttr('{}.color'.format(nam), mat_f[2][1][0], mat_f[2][1][1], mat_f[2][1][2])
        elif mat_f[2][0] == 'file':#���������ϼ�����ͼ�ļ�ʱ��������ͼ�ļ���������ͼ·��
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
            log.info('�Ѵ�����ͼ�ļ��ڵ�{}����ͼ·��Ϊ{}��'.format(fil, mat_f[2][2]))
        else:
            self.display_remind('������{}�����⡣'.format(nam), 1)

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