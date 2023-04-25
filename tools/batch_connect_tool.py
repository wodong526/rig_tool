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
        self.setWindowTitle(u'批量链接属性')

        self.icon_path = 'C:/Rig_Tools/icons/'

        if mc.about(ntOS=True):  #判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.lst_out_node = QtWidgets.QListWidget()#节点框
        self.lst_out_node.setMaximumHeight(200)
        self.lst_inp_node = QtWidgets.QListWidget()
        self.lst_inp_node.setMaximumHeight(200)
        self.lst_inp_node.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.but_out_load = QtWidgets.QPushButton(u'加载输入节点')#加载节点按钮
        self.but_inp_load = QtWidgets.QPushButton(u'加载输入节点')

        self.lin_out_lookup = QtWidgets.QLineEdit()#搜索节点属性按钮
        self.lin_out_lookup.setMinimumHeight(35)
        self.lin_inp_lookup = QtWidgets.QLineEdit()
        self.lin_inp_lookup.setMinimumHeight(35)

        self.but_del_out_lookup = QtWidgets.QPushButton()#删除属性内容按钮
        self.but_del_out_lookup.setFixedSize(35, 35)
        self.but_del_out_lookup.setIcon(QtGui.QIcon('{}delete.png'.format(self.icon_path)))
        self.but_del_out_lookup.setIconSize(QtCore.QSize(35, 35))
        self.but_del_inp_lookup = QtWidgets.QPushButton()
        self.but_del_inp_lookup.setFixedSize(35, 35)
        self.but_del_inp_lookup.setIcon(QtGui.QIcon('{}delete.png'.format(self.icon_path)))
        self.but_del_inp_lookup.setIconSize(QtCore.QSize(35, 35))

        self.lst_out_type = QtWidgets.QListWidget()#节点属性框
        self.lst_inp_type = QtWidgets.QListWidget()

        self.lab_out_screen = QtWidgets.QLabel(u'筛选：')#显示属性类别枚举
        self.lab_out_screen.setMaximumWidth(45)
        self.cmb_out_screen = QtWidgets.QComboBox()
        self.cmb_out_screen.addItems([u'全部', u'可见', u'添加'])
        self.lab_inp_screen = QtWidgets.QLabel(u'筛选：')
        self.lab_inp_screen.setMaximumWidth(45)
        self.cmb_inp_screen = QtWidgets.QComboBox()
        self.cmb_inp_screen.addItems([u'全部', u'可见', u'添加'])

        self.but_link = QtWidgets.QPushButton(u'<< 链接属性 >>')#开始链接
        self.but_link.setStyleSheet("background-color: rgb(195, 124, 174);")
        self.but_link.setMinimumHeight(60)

        self.rdo_force = QtWidgets.QRadioButton(u'强制')
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
        self.lst_inp_node.itemSelectionChanged.connect(self.set_input_plug)#当为多选时，按下并拖动选择项时itemClicked不能正常触发

        self.lin_out_lookup.textChanged.connect(self.set_output_plug)
        self.lin_inp_lookup.textChanged.connect(self.set_input_plug)

        self.but_del_out_lookup.clicked.connect(self.lin_out_lookup.clear)
        self.but_del_inp_lookup.clicked.connect(self.lin_inp_lookup.clear)

        self.cmb_out_screen.activated.connect(self.set_output_plug)
        self.cmb_inp_screen.activated.connect(self.set_input_plug)

        self.but_link.clicked.connect(self.set_link)

    def get_select_output_node(self):
        '''
        设置选中的输出节点
        '''
        self.lst_out_node.clear()
        self.lst_out_type.clear()
        sel = mc.ls(sl=True)
        if sel:
            for obj in sel:
                item = QtWidgets.QListWidgetItem(obj)#在项上填短名
                item.setData(QtCore.Qt.UserRole, obj.split('|')[-1])#每个项带上自己的长名
                self.lst_out_node.addItem(item)
        else:
            log.warning('没有选择有效对象。')

    def get_select_input_node(self):
        '''
        设置选中的输入节点
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
            log.warning('没有选择有效对象。')

    def set_output_plug(self):
        '''
        生成选中项的输出属性
        '''
        sel_items = self.lst_out_node.selectedItems()
        self.lst_out_type.clear()

        typ_lis = None#获取要显示的属性列表
        if self.cmb_out_screen.currentIndex() == 0:#所有属性
            typ_lis = mc.listAttr(sel_items[0].data(QtCore.Qt.UserRole), r=True, c=True)
        elif self.cmb_out_screen.currentIndex() == 1:#能被k帧的都在通道盒里可见
            typ_lis = mc.listAttr(sel_items[0].data(QtCore.Qt.UserRole), k=True)
        elif self.cmb_out_screen.currentIndex() == 2:#用户自定义的属性
            typ_lis = mc.listAttr(sel_items[0].data(QtCore.Qt.UserRole), ud=True)

        typ_lis = self.get_lookup(typ_lis, self.lin_out_lookup)#返回与输入的限制字符相附和的属性名

        if typ_lis:
            for typ in typ_lis:
                item = QtWidgets.QListWidgetItem(typ)
                self.lst_out_type.addItem(item)

    def set_input_plug(self):
        '''
        生成选中项的输入属性
        '''
        sel_items = self.lst_inp_node.selectedItems()
        self.lst_inp_type.clear()

        typ_lis = []
        repeat_lis = []
        if sel_items:#当有选中的项时
            if self.cmb_inp_screen.currentIndex() == 0:  #所有属性
                for item in sel_items:#遍历每一个项
                    aitem_lis = self.get_screen(item, 0)#获取对应类别的属性名
                    repeat_lis = repeat_lis + aitem_lis#当多选时将所有附和类别的属性名放到同一个列表里
            elif self.cmb_inp_screen.currentIndex() == 1:  #能被k帧的都在通道盒里可见
                for item in sel_items:
                    aitem_lis = self.get_screen(item, 1)
                    repeat_lis = repeat_lis + aitem_lis
            elif self.cmb_inp_screen.currentIndex() == 2:  #用户自定义的属性
                for item in sel_items:
                    aitem_lis = self.get_screen(item, 2)
                    repeat_lis = repeat_lis + aitem_lis

            if len(sel_items) > 1:#当为多选时需要去重
                b = dict(Counter(repeat_lis))#将每个元素的重复次数作为value，元素作为key
                typ_lis = [key for key,value in b.items() if value > 1]#当重复次数大于1时返回这个key
            else:
                typ_lis = repeat_lis#当只有一个选中项时，属性列表就为返回的内容

            typ_lis = self.get_lookup(typ_lis, self.lin_inp_lookup)#只留下与输入信息类似的属性

        for typ in typ_lis:
            item = QtWidgets.QListWidgetItem(typ)
            self.lst_inp_type.addItem(item)

    def set_link(self):
        '''
        将上下游连接起来
        '''
        if self.lst_out_node.selectedItems():
            out_node = self.lst_out_node.selectedItems()[0].data(QtCore.Qt.UserRole)#获取输出节点的长名
        else:
            log.warning('没有选中输出节点。')
            return None
        if self.lst_out_type.selectedItems():
            out_type = self.lst_out_type.selectedItems()[0].text()
        else:
            log.warning('没有选中输出属性。')
            return None
        if self.lst_inp_node.selectedItems():
            inp_items = self.lst_inp_node.selectedItems()
        else:
            log.warning('没有选中输入节点。')
            return None
        if self.lst_inp_type.selectedItems():
            inp_type = self.lst_inp_type.selectedItems()[0].text()
        else:
            log.warning('没有选中输入属性。')
            return None

        for item in inp_items:#遍历每个输入节点
            inp_node = item.data(QtCore.Qt.UserRole)#获取输入节点的长名
            if mc.listConnections('{}.{}'.format(inp_node, inp_type)):#当输入属性的上游没有链接时
                if self.rdo_force.isChecked():#当强制链接按钮打开时
                    mc.connectAttr('{}.{}'.format(out_node, out_type), '{}.{}'.format(inp_node, inp_type), f=True)
                else:
                    continue
            else:
                mc.connectAttr('{}.{}'.format(out_node, out_type), '{}.{}'.format(inp_node, inp_type))

    def get_screen(self, item, ind):
        '''
        根据不同的类别限制返回对应的属性名，当没有对应的属性名时，返回空列表
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
        获取限制输入框中的字符，当输入的属性列表里的属性名包含该字符时，返回这个字符
        '''
        return_lis = []
        if lin.text() and typ_lis:#当有限制输入且属性列表里有元素时（有时候一些类型的属性不存在，如添加的属性）
            for typ in typ_lis:#遍历每一个属性名
                if lin.text() in typ:#当属性名包含限制字符时
                    return_lis.append(typ)#在返回列表中添加该属性名

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