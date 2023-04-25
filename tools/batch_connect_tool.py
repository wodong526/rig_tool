# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui

from collections import Counter
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class ConnectType_Window(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(ConnectType_Window, self).__init__(parent)
        self.setFixedSize(500, 700)
        self.setWindowTitle(u'������������')

        self.icon_path = 'C:/Rig_Tools/icons/'

        if mc.about(ntOS=True):  #�ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.lst_out_node = QtWidgets.QListWidget()#�ڵ��
        self.lst_out_node.setMaximumHeight(200)
        self.lst_inp_node = QtWidgets.QListWidget()
        self.lst_inp_node.setMaximumHeight(200)
        self.lst_inp_node.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.but_out_load = QtWidgets.QPushButton(u'��������ڵ�')#���ؽڵ㰴ť
        self.but_inp_load = QtWidgets.QPushButton(u'��������ڵ�')

        self.lin_out_lookup = QtWidgets.QLineEdit()#�����ڵ����԰�ť
        self.lin_out_lookup.setMinimumHeight(35)
        self.lin_inp_lookup = QtWidgets.QLineEdit()
        self.lin_inp_lookup.setMinimumHeight(35)

        self.but_del_out_lookup = QtWidgets.QPushButton()#ɾ���������ݰ�ť
        self.but_del_out_lookup.setFixedSize(35, 35)
        self.but_del_out_lookup.setIcon(QtGui.QIcon('{}delete.png'.format(self.icon_path)))
        self.but_del_out_lookup.setIconSize(QtCore.QSize(35, 35))
        self.but_del_inp_lookup = QtWidgets.QPushButton()
        self.but_del_inp_lookup.setFixedSize(35, 35)
        self.but_del_inp_lookup.setIcon(QtGui.QIcon('{}delete.png'.format(self.icon_path)))
        self.but_del_inp_lookup.setIconSize(QtCore.QSize(35, 35))

        self.lst_out_type = QtWidgets.QListWidget()#�ڵ����Կ�
        self.lst_inp_type = QtWidgets.QListWidget()

        self.lab_out_screen = QtWidgets.QLabel(u'ɸѡ��')#��ʾ�������ö��
        self.lab_out_screen.setMaximumWidth(45)
        self.cmb_out_screen = QtWidgets.QComboBox()
        self.cmb_out_screen.addItems([u'ȫ��', u'�ɼ�', u'���'])
        self.lab_inp_screen = QtWidgets.QLabel(u'ɸѡ��')
        self.lab_inp_screen.setMaximumWidth(45)
        self.cmb_inp_screen = QtWidgets.QComboBox()
        self.cmb_inp_screen.addItems([u'ȫ��', u'�ɼ�', u'���'])

        self.but_link = QtWidgets.QPushButton(u'<< �������� >>')#��ʼ����
        self.but_link.setStyleSheet("background-color: rgb(195, 124, 174);")
        self.but_link.setMinimumHeight(60)

        self.rdo_force = QtWidgets.QRadioButton(u'ǿ��')
        self.rdo_force.setMaximumWidth(70)

    def create_layout(self):
        delete_out_layout = QtWidgets.QHBoxLayout()
        delete_out_layout.addWidget(self.lin_out_lookup)
        delete_out_layout.addWidget(self.but_del_out_lookup)

        delete_inp_layout = QtWidgets.QHBoxLayout()
        delete_inp_layout.addWidget(self.lin_inp_lookup)
        delete_inp_layout.addWidget(self.but_del_inp_lookup)

        screen_out_layout = QtWidgets.QHBoxLayout()

        screen_out_layout.addWidget(self.lab_out_screen)
        screen_out_layout.addWidget(self.cmb_out_screen)

        screen_inp_layout = QtWidgets.QHBoxLayout()
        screen_inp_layout.addWidget(self.lab_inp_screen)
        screen_inp_layout.addWidget(self.cmb_inp_screen)

        output_layout = QtWidgets.QVBoxLayout()
        output_layout.setSpacing(1)
        output_layout.addWidget(self.lst_out_node)
        output_layout.addWidget(self.but_out_load)
        output_layout.addLayout(delete_out_layout)
        output_layout.addWidget(self.lst_out_type)
        output_layout.addLayout(screen_out_layout)

        input_layout = QtWidgets.QVBoxLayout()
        input_layout.setSpacing(1)
        input_layout.addWidget(self.lst_inp_node)
        input_layout.addWidget(self.but_inp_load)
        input_layout.addLayout(delete_inp_layout)
        input_layout.addWidget(self.lst_inp_type)
        input_layout.addLayout(screen_inp_layout)

        lin_output_layout = QtWidgets.QWidget()
        lin_output_layout.setLayout(output_layout)
        lin_input_layout = QtWidgets.QWidget()
        lin_input_layout.setLayout(input_layout)

        spt_layout = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        spt_layout.addWidget(lin_output_layout)
        spt_layout.addWidget(lin_input_layout)

        link_layout = QtWidgets.QHBoxLayout()
        link_layout.addWidget(self.but_link)
        link_layout.addWidget(self.rdo_force)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.addWidget(spt_layout)
        main_layout.addLayout(link_layout)

    def create_connections(self):
        self.but_out_load.clicked.connect(self.get_select_output_node)
        self.but_inp_load.clicked.connect(self.get_select_input_node)

        self.lst_out_node.itemSelectionChanged.connect(self.set_output_plug)
        self.lst_inp_node.itemSelectionChanged.connect(self.set_input_plug)#��Ϊ��ѡʱ�����²��϶�ѡ����ʱitemClicked������������

        self.lin_out_lookup.textChanged.connect(self.set_output_plug)
        self.lin_inp_lookup.textChanged.connect(self.set_input_plug)

        self.but_del_out_lookup.clicked.connect(self.lin_out_lookup.clear)
        self.but_del_inp_lookup.clicked.connect(self.lin_inp_lookup.clear)

        self.cmb_out_screen.activated.connect(self.set_output_plug)
        self.cmb_inp_screen.activated.connect(self.set_input_plug)

        self.but_link.clicked.connect(self.set_link)

    def get_select_output_node(self):
        '''
        ����ѡ�е�����ڵ�
        '''
        self.lst_out_node.clear()
        self.lst_out_type.clear()
        sel = mc.ls(sl=True)
        if sel:
            for obj in sel:
                item = QtWidgets.QListWidgetItem(obj)#�����������
                item.setData(QtCore.Qt.UserRole, obj.split('|')[-1])#ÿ��������Լ��ĳ���
                self.lst_out_node.addItem(item)
        else:
            log.warning('û��ѡ����Ч����')

    def get_select_input_node(self):
        '''
        ����ѡ�е�����ڵ�
        '''
        self.lst_inp_node.clear()
        self.lst_inp_type.clear()
        sel = mc.ls(sl=True)
        if sel:
            for obj in sel:
                item = QtWidgets.QListWidgetItem(obj)
                item.setData(QtCore.Qt.UserRole, obj.split('|')[-1])
                self.lst_inp_node.addItem(item)
        else:
            log.warning('û��ѡ����Ч����')

    def set_output_plug(self):
        '''
        ����ѡ������������
        '''
        sel_items = self.lst_out_node.selectedItems()
        self.lst_out_type.clear()

        typ_lis = None#��ȡҪ��ʾ�������б�
        if self.cmb_out_screen.currentIndex() == 0:#��������
            typ_lis = mc.listAttr(sel_items[0].data(QtCore.Qt.UserRole), r=True, c=True)
        elif self.cmb_out_screen.currentIndex() == 1:#�ܱ�k֡�Ķ���ͨ������ɼ�
            typ_lis = mc.listAttr(sel_items[0].data(QtCore.Qt.UserRole), k=True)
        elif self.cmb_out_screen.currentIndex() == 2:#�û��Զ��������
            typ_lis = mc.listAttr(sel_items[0].data(QtCore.Qt.UserRole), ud=True)

        typ_lis = self.get_lookup(typ_lis, self.lin_out_lookup)#����������������ַ��฽�͵�������

        if typ_lis:
            for typ in typ_lis:
                item = QtWidgets.QListWidgetItem(typ)
                self.lst_out_type.addItem(item)

    def set_input_plug(self):
        '''
        ����ѡ�������������
        '''
        sel_items = self.lst_inp_node.selectedItems()
        self.lst_inp_type.clear()

        typ_lis = []
        repeat_lis = []
        if sel_items:#����ѡ�е���ʱ
            if self.cmb_inp_screen.currentIndex() == 0:  #��������
                for item in sel_items:#����ÿһ����
                    aitem_lis = self.get_screen(item, 0)#��ȡ��Ӧ����������
                    repeat_lis = repeat_lis + aitem_lis#����ѡʱ�����и��������������ŵ�ͬһ���б���
            elif self.cmb_inp_screen.currentIndex() == 1:  #�ܱ�k֡�Ķ���ͨ������ɼ�
                for item in sel_items:
                    aitem_lis = self.get_screen(item, 1)
                    repeat_lis = repeat_lis + aitem_lis
            elif self.cmb_inp_screen.currentIndex() == 2:  #�û��Զ��������
                for item in sel_items:
                    aitem_lis = self.get_screen(item, 2)
                    repeat_lis = repeat_lis + aitem_lis

            if len(sel_items) > 1:#��Ϊ��ѡʱ��Ҫȥ��
                b = dict(Counter(repeat_lis))#��ÿ��Ԫ�ص��ظ�������Ϊvalue��Ԫ����Ϊkey
                typ_lis = [key for key,value in b.items() if value > 1]#���ظ���������1ʱ�������key
            else:
                typ_lis = repeat_lis#��ֻ��һ��ѡ����ʱ�������б��Ϊ���ص�����

            typ_lis = self.get_lookup(typ_lis, self.lin_inp_lookup)#ֻ������������Ϣ���Ƶ�����

        for typ in typ_lis:
            item = QtWidgets.QListWidgetItem(typ)
            self.lst_inp_type.addItem(item)

    def set_link(self):
        '''
        ����������������
        '''
        if self.lst_out_node.selectedItems():
            out_node = self.lst_out_node.selectedItems()[0].data(QtCore.Qt.UserRole)#��ȡ����ڵ�ĳ���
        else:
            log.warning('û��ѡ������ڵ㡣')
            return None
        if self.lst_out_type.selectedItems():
            out_type = self.lst_out_type.selectedItems()[0].text()
        else:
            log.warning('û��ѡ��������ԡ�')
            return None
        if self.lst_inp_node.selectedItems():
            inp_items = self.lst_inp_node.selectedItems()
        else:
            log.warning('û��ѡ������ڵ㡣')
            return None
        if self.lst_inp_type.selectedItems():
            inp_type = self.lst_inp_type.selectedItems()[0].text()
        else:
            log.warning('û��ѡ���������ԡ�')
            return None

        for item in inp_items:#����ÿ������ڵ�
            inp_node = item.data(QtCore.Qt.UserRole)#��ȡ����ڵ�ĳ���
            if mc.listConnections('{}.{}'.format(inp_node, inp_type)):#���������Ե�����û������ʱ
                if self.rdo_force.isChecked():#��ǿ�����Ӱ�ť��ʱ
                    mc.connectAttr('{}.{}'.format(out_node, out_type), '{}.{}'.format(inp_node, inp_type), f=True)
                else:
                    continue
            else:
                mc.connectAttr('{}.{}'.format(out_node, out_type), '{}.{}'.format(inp_node, inp_type))

    def get_screen(self, item, ind):
        '''
        ���ݲ�ͬ��������Ʒ��ض�Ӧ������������û�ж�Ӧ��������ʱ�����ؿ��б�
        '''
        typ_lis = []
        if ind == 0:
            typ_lis = mc.listAttr(item.data(QtCore.Qt.UserRole), r=True, c=True)
        elif ind == 1:
            typ_lis = mc.listAttr(item.data(QtCore.Qt.UserRole), k=True)
        elif ind == 2:
            typ_lis = mc.listAttr(item.data(QtCore.Qt.UserRole), ud=True)

        if typ_lis:
            return typ_lis
        else:
            return []

    def get_lookup(self, typ_lis, lin):
        '''
        ��ȡ����������е��ַ���������������б�����������������ַ�ʱ����������ַ�
        '''
        return_lis = []
        if lin.text() and typ_lis:#�������������������б�����Ԫ��ʱ����ʱ��һЩ���͵����Բ����ڣ�����ӵ����ԣ�
            for typ in typ_lis:#����ÿһ��������
                if lin.text() in typ:#�����������������ַ�ʱ
                    return_lis.append(typ)#�ڷ����б�����Ӹ�������

        if return_lis:
            return return_lis
        else:
            return typ_lis

def main():
    try:
        nodeLink_window.close()
        nodeLink_window.deleteLater()
    except:
        pass
    finally:
        nodeLink_window = ConnectType_Window()
        nodeLink_window.show()