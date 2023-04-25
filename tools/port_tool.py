# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui

import sys
import os
from feedback_tool import Feedback_info as fb_print
LIN = sys._getframe()
FILE_PATH = __file__

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class Export_SM(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(Export_SM, self).__init__(parent)

        self.setWindowTitle(u'����SM�ļ�')
        if mc.about(ntOS=True):  #�ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.scence_path = mc.file(exn=1, q=1)
        self.jnt_dir = {}
        self.export_nam_dir = {}

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.lab_faces = QtWidgets.QLabel(u'��������:')
        self.spn_faces = QtWidgets.QSpinBox()
        self.spn_faces.setMinimum(1)
        self.spn_faces.setMaximum(999999999)
        self.spn_faces.setValue(65000)
        self.spn_faces.setSuffix(u'  ��������')
        self.spn_faces.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.but_faces = QtWidgets.QPushButton(u'��ȡ��Ӧ')

        self.lst_jnts = QtWidgets.QListWidget()
        self.lst_jnts.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.lst_mods = QtWidgets.QListWidget()
        self.lst_mods.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.but_export = QtWidgets.QPushButton(u'����')

    def create_layout(self):
        layout_face = QtWidgets.QHBoxLayout()
        layout_face.addWidget(self.lab_faces)
        layout_face.addWidget(self.spn_faces)
        layout_face.addWidget(self.but_faces)

        layout_spt = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        layout_spt.addWidget(self.lst_jnts)
        layout_spt.addWidget(self.lst_mods)

        layout_main = QtWidgets.QVBoxLayout(self)
        layout_main.addLayout(layout_face)
        layout_main.addWidget(layout_spt)
        layout_main.addWidget(self.but_export)

    def create_connections(self):
        self.but_faces.clicked.connect(self.get_data)
        self.lst_jnts.itemSelectionChanged.connect(self.create_modItems)
        self.lst_jnts.customContextMenuRequested.connect(self.contextMenu_jnt)
        self.lst_mods.customContextMenuRequested.connect(self.contextMenu_mod)
        self.lst_jnts.itemSelectionChanged.connect(self.select_jnt)
        self.lst_mods.itemSelectionChanged.connect(self.select_mod)
        self.but_export.clicked.connect(self.exportSM)

    def get_data(self):
        '''
        ��ȡ���뾲̬ģ�͵���������
        ���ɹؽ�����ģ������Ӧ���ֵ�
        ���ɹؽ�����ؽڶ�Ӧ�ľ�̬ģ��(sm�ļ���)���ֵ�
        :return:
        '''
        clamp_num = self.spn_faces.value()
        mod_dir = self.get_mod(clamp_num)
        self.jnt_dir = self.get_joint(mod_dir)#�ؽ���==��Ӧ�ؽڵ�����ģ�����б�

        self.export_nam_dir = {}#�ؽ���==��Ӧ�ؽڵ�sm���б�
        for jnt, mods in self.jnt_dir.items():
            self.export_nam_dir[jnt] = 'SM_{}'.format(mods[0])

        if self.export_nam_dir:
            self.create_jntItems()
            self.spn_faces.clearFocus()#�ڵ����ѯ������ť��ʹ�����ʧȥ����
        else:
            fb_print('������û�г���{}������ģ��'.format(clamp_num), warning=True, path=FILE_PATH)

    def create_jntItems(self, *itm):
        '''
        ���ɹؽ��б���ͼ�����
        :param itm: ������������ʱ�����ϴ�ѡ�е���������ѡ�жԷ�
        :return:
        '''
        self.lst_jnts.clear()
        self.lst_mods.clear()
        if self.jnt_dir:
            for jnt, mods in self.jnt_dir.items():
                item = QtWidgets.QListWidgetItem('{}==>  {}'.format(jnt.ljust(30, ' '), self.export_nam_dir[jnt]))
                item.setData(QtCore.Qt.UserRole, jnt)#���ؽ������ӵ�����
                self.lst_jnts.addItem(item)

        if itm:
            self.lst_jnts.item(itm[0]).setSelected(True)
        else:
            self.lst_jnts.item(0).setSelected(True)


    def create_modItems(self, *itm):
        '''
        ����ģ���б���ͼ�����
        :return:
        '''
        sel_item = self.lst_jnts.selectedItems()
        self.lst_mods.clear()
        if sel_item:
            for mod in self.jnt_dir[sel_item[0].data(QtCore.Qt.UserRole)]:
                if mod:
                    item = QtWidgets.QListWidgetItem(mod)
                    self.lst_mods.addItem(item)
                else:
                    fb_print('�ؽ�{}û�ж�Ӧ��ģ�͡�'.format(sel_item[0].data(QtCore.Qt.UserRole)))

    def contextMenu_jnt(self, pos):
        '''
        �ؽ��б���ͼ���������Ҽ����ɵĲ˵�
        :param pos: ����Ҽ�ʱ��λ�����������ڲ��ֵ�λ��
        :return:
        '''
        menu = QtWidgets.QMenu()
        action_addJnt = menu.addAction(u'���ѡ�йؽ�')
        action_addJnt.triggered.connect(self.add_JntItem)
        if self.lst_jnts.itemAt(pos):
            action_rename = menu.addAction(u'�����������ļ���')
            action_remove = menu.addAction(u'ɾ������')
            action_copy = menu.addAction(u'���ƹؽ���')
            action_rename.triggered.connect(self.rename_jntItem)
            action_remove.triggered.connect(self.remove_jntItem)
            action_copy.triggered.connect(self.duplicate_jntName)

        menu.exec_(self.lst_jnts.mapToGlobal(pos))#�˵����ɵ�λ��

    def contextMenu_mod(self, pos):
        menu = QtWidgets.QMenu()
        action_addMod = menu.addAction(u'��ѡ�ж�����ӵ���sm�ļ���')
        action_addMod.triggered.connect(self.add_modItem)
        if self.lst_mods.itemAt(pos):
            action_remove = menu.addAction(u'ɾ������')
            action_copy = menu.addAction(u'����ģ����')
            action_remove.triggered.connect(self.remove_modItem)
            action_copy.triggered.connect(self.duplicate_modName)

        menu.exec_(self.lst_mods.mapToGlobal(pos))  #�˵����ɵ�λ��

    def select_mod(self):
        '''
        ��ģ���б��Ӵ��е��ѡ��ʱ�Զ�ѡ�г������Ӧ��ģ��
        :return:
        '''
        sel_item = self.lst_mods.selectedItems()
        if sel_item:
            obj = sel_item[0].text()
            mc.select(obj)

    def select_jnt(self):
        '''
        ���ؽ��б��Ӵ��е��ѡ��ʱ�Զ�ѡ�г������Ӧ�Ĺؽ�
        :return:
        '''
        sel_item = self.lst_jnts.selectedItems()
        if sel_item:
            jnt = sel_item[0].data(QtCore.Qt.UserRole)
            mc.select(jnt)

    def duplicate_jntName(self):
        '''
        ����ѡ�йؽ���Ĺؽ���
        :return:
        '''
        sel_item = self.lst_jnts.selectedItems()
        nam = sel_item[0].data(QtCore.Qt.UserRole)
        com = 'echo | set /p unl = ' + nam.strip() + '| clip'
        os.system(com)

    def duplicate_modName(self):
        '''
        ����ѡ��ģ�����ģ����
        :return:
        '''
        sel_item = self.lst_mods.selectedItems()
        nam = sel_item[0].text()
        com = 'echo | set /p unl = ' + nam.strip() + '| clip'
        os.system(com)

    def add_modItem(self):
        '''
        Ϊģ���б���ͼ������µ�ģ����
        :return:
        '''
        sel_lis = mc.ls(sl=True)
        if sel_lis:
            jnt_item = self.lst_jnts.selectedItems()
            if jnt_item:
                i = self.lst_jnts.currentRow()
                jnt = jnt_item[0].data(QtCore.Qt.UserRole)

                append_lis = []

                for obj in sel_lis:
                    shape = None
                    if mc.listRelatives(obj, s=True):
                        shape = mc.listRelatives(obj, s=True)[0]
                    if obj not in self.jnt_dir[jnt] and mc.nodeType(shape) == 'mesh':
                        self.jnt_dir[jnt].append(obj)
                        append_lis.append(obj)

                if append_lis:
                    self.create_modItems(i)
                    fb_print('��Ϊ{}�ļ��м���ģ��{}'.format(self.export_nam_dir[jnt], append_lis), info=True)
                else:
                    fb_print('ѡ���б���û�пɼ���SM�ļ�����Чģ��', warning=True, viewMes=True)

    def add_JntItem(self):
        """
        Ϊ�ؽ��б���ͼ������µĹؽ���
        :return:
        """
        sel_lis = mc.ls(sl=True)
        if sel_lis:
            add_lis = []
            for obj in sel_lis:
                if mc.nodeType(obj) == 'joint' and obj not in self.jnt_dir:
                    self.jnt_dir[obj] = []
                    self.export_nam_dir[obj] = 'SM_{}'.format(obj)
                    add_lis.append(obj)

            if add_lis:
                self.create_jntItems()
                fb_print('����ӹؽ�{}'.format(add_lis), info=True)
            else:
                fb_print('ѡ���б���û����Ч�ؽ�', warning=True)

    def remove_jntItem(self):
        """
        ��ѡ�еĹؽ���ɾ��
        :return:
        """
        jnt_item = self.lst_jnts.selectedItems()
        if jnt_item:
            jnt = jnt_item[0].data(QtCore.Qt.UserRole)
            mods = self.jnt_dir.pop(jnt, None)
            del self.export_nam_dir[jnt]
            self.create_jntItems()
            fb_print('��ɾ����{}��ģ��{}�����ᱻ����'.format(jnt, mods), info=True)

    def remove_modItem(self):
        """
        ��ѡ�е�ģ����ɾ��
        :return:
        """
        mod_item = self.lst_mods.selectedItems()
        if mod_item:
            jnt_item = self.lst_jnts.selectedItems()
            jnt = jnt_item[0].data(QtCore.Qt.UserRole)

            mod = mod_item[0].text()
            print(jnt)
            print(self.jnt_dir)
            if mod in self.jnt_dir[jnt]:
                self.jnt_dir[jnt].remove(mod)
                self.create_modItems()
                fb_print('�Ѵ�{}��ɾ��ģ��{}'.format(jnt, mod), info=True)
            else:
                fb_print('ģ��{}�����ڹؽ�{}�ĵ�������'.format(mod, jnt), error=True)

    def exportSM(self):
        '''
        ����sm�ļ�
        ����Ӧ��ģ�ͽ���󶨲�p������㼶��
        ����Ӧ��ģ��ѡ�в�������fbx
        ���ô���txt�ؽ���ģ�Ͷ�Ӧ��Ϣ�ļ�
        :return:
        '''
        export_lis = []
        for jnt, SM_nam in self.export_nam_dir.items():
            for mod in self.jnt_dir[jnt]:
                skin = mm.eval('findRelatedSkinCluster("{}")'.format(mod))
                if skin:
                    mc.skinCluster(skin, e=True, ub=True)
                else:
                    fb_print('ģ��{}û����Ƥ'.format(mod), info=True)

            if self.jnt_dir[jnt]:
                try:
                    mc.parent(self.jnt_dir[jnt], w=True)
                except Exception as e:
                    print('��ģ�Ϳ�����������������㣬����������\n{}'.format(e))
                fbx_path = os.path.split(self.scence_path)[0] + '/' + self.export_nam_dir[jnt] + '.fbx'

                mc.select(self.jnt_dir[jnt])
                mc.file(fbx_path, f=True, typ='FBX export', pr=True, es=True)
                export_lis.append(jnt)
                fb_print('�ѵ���ģ��{}'.format(self.jnt_dir[jnt]), info=True, path=FILE_PATH, line=LIN.f_lineno)
            else:
                fb_print('�ؽ�{}û�ж�Ӧ��ģ�Ϳɹ�����'.format(jnt), warning=True)

        n, path = self.write_txt(export_lis)
        fb_print('��������̬ģ��{}�������ɶ�Ӧ�ļ�{}��'.format(n, path), info=True, path=FILE_PATH, line=LIN.f_lineno, viewMes=True)

    def write_txt(self, export_lis):
        '''
        ������д��txt�ؽ��뾲̬ģ�Ͷ�Ӧ��Ϣ�ļ�
        :return:
        '''
        txt = ''
        i = 0
        for jnt in export_lis:
            sm_nam = self.export_nam_dir[jnt]
            i += 1
            mid = '---'.center(15)

            txt = txt + jnt + mid + sm_nam + '\n'

        with open(self.scence_path.replace('.ma', '.txt'), "w") as f:
            f.write(txt)
        fb_print('��Ӧ�ļ�д�����', path=FILE_PATH, line=LIN.f_lineno, info=True)

        return i, self.scence_path.replace('.ma', '.txt')


    def rename_jntItem(self):
        '''
        ���ؽ��б���ͼ�еĲ˵����еı����ʱ���޸ĵ����ֵ䣨self.export_nam_dir������Ķ�Ӧsm�ļ��������������ɹؽ��б���ͼ�е���
        :return:
        '''
        new_SM_nam = self.get_newName()
        if new_SM_nam:
            i = self.lst_jnts.currentRow()
            item = self.lst_jnts.item(i)
            jnt = item.data(QtCore.Qt.UserRole)

            self.export_nam_dir[jnt] = new_SM_nam
            self.create_jntItems(i)

    def get_newName(self):
        '''
        ���ɶԻ����ڣ����û������µ�sm�ļ���
        :return:
        '''
        mes = QtWidgets.QInputDialog.getText(self, u'������SM�ļ���', u'�����µ�SM�ļ�����', QtWidgets.QLineEdit.Normal, 'SM_')
        if mes[0]:
            return mes[0]
        else:
            fb_print('û��������Ч���ݣ��Խ�����ԭ������', warning=True, viewMes=True)

    def get_mod(self, i):
        '''
        ��ѯ�����е�ģ�ͣ���ģ��������ڵ����������������ʱ��ȡ��ģ����
        :param i: �û���������ģ������
        :return:ģ�͵�transform�������������Ķ�Ӧ��ϵ�ֵ�
        '''
        mods = {}
        for obj in mc.ls(typ='mesh'):
            if 'Orig' not in obj:
                if mc.polyEvaluate(obj, t=True) >= i:
                    trs = mc.listRelatives(obj, p=True)[0]
                    mods[trs] = mc.polyEvaluate(obj, t=True)

        return mods

    def get_joint(self, mod_dir):
        '''
        ͨ��ģ�ͻ�ȡģ�͵���Ƥ�ؽڣ�����Ƥ�ؽ�ֻ��һ��ʱ��ģ�����ɶ�Ӧ�ֵ�
        :param mod_dir:ģ���ֵ�
        :return:
        '''
        jnt_dir = {}
        error_lis = {}
        for mod in mod_dir:
            jnt_lis = self.get_modJoint(mod)
            if len(jnt_lis) == 1:
                if jnt_lis[0] not in jnt_dir.keys():
                    jnt_dir[jnt_lis[0]] = [mod]
                else:
                    jnt_dir[jnt_lis[0]].append(mod)
            else:
                error_lis[mod] = len(jnt_lis)

        if error_lis:
            for key, itme in error_lis.items():
                fb_print('ģ��{}����Ƥ�ؽ�ӦΪһ����ʵ��Ϊ{}��'.format(key, itme),
                         warning=True, path=FILE_PATH, line=LIN.f_lineno, viewMes=True)
        return jnt_dir

    def get_modJoint(self, mod):
        '''
        ��ȡģ�͵���Ƥ�ؽ��б�
        :param mod: ����Ƥ��ģ��
        :return:
        '''
        jnt_lis = []  #ģ�͵�Ӱ��ؽڻᱻ��������б���
        skin = mm.eval('findRelatedSkinCluster("{}")'.format(mod))
        if skin:
            for jnt in mc.skinCluster(skin, inf=1, q=1):  #����Ƥ�ڵ����õ���Ӱ��Ĺؽ�
                if jnt not in jnt_lis:
                    jnt_lis.append(jnt)
        return jnt_lis


def export_SM():
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = Export_SM()
        my_window.show()

