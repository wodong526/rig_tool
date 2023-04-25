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

        self.setWindowTitle(u'导出SM文件')
        if mc.about(ntOS=True):  #判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.scence_path = mc.file(exn=1, q=1)
        self.jnt_dir = {}
        self.export_nam_dir = {}

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.lab_faces = QtWidgets.QLabel(u'限制面数:')
        self.spn_faces = QtWidgets.QSpinBox()
        self.spn_faces.setMinimum(1)
        self.spn_faces.setMaximum(999999999)
        self.spn_faces.setValue(65000)
        self.spn_faces.setSuffix(u'  个三角面')
        self.spn_faces.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.but_faces = QtWidgets.QPushButton(u'获取对应')

        self.lst_jnts = QtWidgets.QListWidget()
        self.lst_jnts.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.lst_mods = QtWidgets.QListWidget()
        self.lst_mods.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.but_export = QtWidgets.QPushButton(u'导出')

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
        获取输入静态模型的面数下线
        生成关节名与模型名对应的字典
        生成关节名与关节对应的静态模型(sm文件名)的字典
        :return:
        '''
        clamp_num = self.spn_faces.value()
        mod_dir = self.get_mod(clamp_num)
        self.jnt_dir = self.get_joint(mod_dir)#关节名==对应关节的所有模型名列表

        self.export_nam_dir = {}#关节名==对应关节的sm名列表
        for jnt, mods in self.jnt_dir.items():
            self.export_nam_dir[jnt] = 'SM_{}'.format(mods[0])

        if self.export_nam_dir:
            self.create_jntItems()
            self.spn_faces.clearFocus()#在点击查询场景按钮后使输入框失去焦点
        else:
            fb_print('场景中没有超过{}面数的模型'.format(clamp_num), warning=True, path=FILE_PATH)

    def create_jntItems(self, *itm):
        '''
        生成关节列表视图里的项
        :param itm: 当重新排列项时记忆上次选中的项，方便继续选中对方
        :return:
        '''
        self.lst_jnts.clear()
        self.lst_mods.clear()
        if self.jnt_dir:
            for jnt, mods in self.jnt_dir.items():
                item = QtWidgets.QListWidgetItem('{}==>  {}'.format(jnt.ljust(30, ' '), self.export_nam_dir[jnt]))
                item.setData(QtCore.Qt.UserRole, jnt)#将关节名附加到项上
                self.lst_jnts.addItem(item)

        if itm:
            self.lst_jnts.item(itm[0]).setSelected(True)
        else:
            self.lst_jnts.item(0).setSelected(True)


    def create_modItems(self, *itm):
        '''
        生成模型列表视图里的项
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
                    fb_print('关节{}没有对应的模型。'.format(sel_item[0].data(QtCore.Qt.UserRole)))

    def contextMenu_jnt(self, pos):
        '''
        关节列表视图中在项上右键生成的菜单
        :param pos: 鼠标右键时的位置在整个窗口布局的位置
        :return:
        '''
        menu = QtWidgets.QMenu()
        action_addJnt = menu.addAction(u'添加选中关节')
        action_addJnt.triggered.connect(self.add_JntItem)
        if self.lst_jnts.itemAt(pos):
            action_rename = menu.addAction(u'重命名导出文件名')
            action_remove = menu.addAction(u'删除该项')
            action_copy = menu.addAction(u'复制关节名')
            action_rename.triggered.connect(self.rename_jntItem)
            action_remove.triggered.connect(self.remove_jntItem)
            action_copy.triggered.connect(self.duplicate_jntName)

        menu.exec_(self.lst_jnts.mapToGlobal(pos))#菜单生成的位置

    def contextMenu_mod(self, pos):
        menu = QtWidgets.QMenu()
        action_addMod = menu.addAction(u'将选中对象添加到该sm文件中')
        action_addMod.triggered.connect(self.add_modItem)
        if self.lst_mods.itemAt(pos):
            action_remove = menu.addAction(u'删除该项')
            action_copy = menu.addAction(u'复制模型名')
            action_remove.triggered.connect(self.remove_modItem)
            action_copy.triggered.connect(self.duplicate_modName)

        menu.exec_(self.lst_mods.mapToGlobal(pos))  #菜单生成的位置

    def select_mod(self):
        '''
        当模型列表视窗中的项被选中时自动选中场景里对应的模型
        :return:
        '''
        sel_item = self.lst_mods.selectedItems()
        if sel_item:
            obj = sel_item[0].text()
            mc.select(obj)

    def select_jnt(self):
        '''
        当关节列表视窗中的项被选中时自动选中场景里对应的关节
        :return:
        '''
        sel_item = self.lst_jnts.selectedItems()
        if sel_item:
            jnt = sel_item[0].data(QtCore.Qt.UserRole)
            mc.select(jnt)

    def duplicate_jntName(self):
        '''
        复制选中关节项的关节名
        :return:
        '''
        sel_item = self.lst_jnts.selectedItems()
        nam = sel_item[0].data(QtCore.Qt.UserRole)
        com = 'echo | set /p unl = ' + nam.strip() + '| clip'
        os.system(com)

    def duplicate_modName(self):
        '''
        复制选中模型项的模型名
        :return:
        '''
        sel_item = self.lst_mods.selectedItems()
        nam = sel_item[0].text()
        com = 'echo | set /p unl = ' + nam.strip() + '| clip'
        os.system(com)

    def add_modItem(self):
        '''
        为模型列表视图中添加新的模型项
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
                    fb_print('已为{}文件中加入模型{}'.format(self.export_nam_dir[jnt], append_lis), info=True)
                else:
                    fb_print('选择列表中没有可加入SM文件的有效模型', warning=True, viewMes=True)

    def add_JntItem(self):
        """
        为关节列表视图中添加新的关节项
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
                fb_print('已添加关节{}'.format(add_lis), info=True)
            else:
                fb_print('选择列表中没有有效关节', warning=True)

    def remove_jntItem(self):
        """
        将选中的关节项删除
        :return:
        """
        jnt_item = self.lst_jnts.selectedItems()
        if jnt_item:
            jnt = jnt_item[0].data(QtCore.Qt.UserRole)
            mods = self.jnt_dir.pop(jnt, None)
            del self.export_nam_dir[jnt]
            self.create_jntItems()
            fb_print('已删除项{}，模型{}将不会被导出'.format(jnt, mods), info=True)

    def remove_modItem(self):
        """
        将选中的模型项删除
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
                fb_print('已从{}中删除模型{}'.format(jnt, mod), info=True)
            else:
                fb_print('模型{}不存在关节{}的导出项中'.format(mod, jnt), error=True)

    def exportSM(self):
        '''
        导出sm文件
        将对应的模型解除绑定并p到世界层级下
        将对应的模型选中并导出成fbx
        调用创建txt关节与模型对应信息文件
        :return:
        '''
        export_lis = []
        for jnt, SM_nam in self.export_nam_dir.items():
            for mod in self.jnt_dir[jnt]:
                skin = mm.eval('findRelatedSkinCluster("{}")'.format(mod))
                if skin:
                    mc.skinCluster(skin, e=True, ub=True)
                else:
                    fb_print('模型{}没有蒙皮'.format(mod), info=True)

            if self.jnt_dir[jnt]:
                try:
                    mc.parent(self.jnt_dir[jnt], w=True)
                except Exception as e:
                    print('该模型可能是已在世界最外层，报错内容是\n{}'.format(e))
                fbx_path = os.path.split(self.scence_path)[0] + '/' + self.export_nam_dir[jnt] + '.fbx'

                mc.select(self.jnt_dir[jnt])
                mc.file(fbx_path, f=True, typ='FBX export', pr=True, es=True)
                export_lis.append(jnt)
                fb_print('已导出模型{}'.format(self.jnt_dir[jnt]), info=True, path=FILE_PATH, line=LIN.f_lineno)
            else:
                fb_print('关节{}没有对应的模型可供导出'.format(jnt), warning=True)

        n, path = self.write_txt(export_lis)
        fb_print('共导出静态模型{}个，生成对应文件{}。'.format(n, path), info=True, path=FILE_PATH, line=LIN.f_lineno, viewMes=True)

    def write_txt(self, export_lis):
        '''
        创建并写入txt关节与静态模型对应信息文件
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
        fb_print('对应文件写入完毕', path=FILE_PATH, line=LIN.f_lineno, info=True)

        return i, self.scence_path.replace('.ma', '.txt')


    def rename_jntItem(self):
        '''
        当关节列表视图中的菜单项中的被点击时，修改导出字典（self.export_nam_dir）该项的对应sm文件名，并重新生成关节列表视图中的项
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
        生成对话窗口，让用户输入新的sm文件名
        :return:
        '''
        mes = QtWidgets.QInputDialog.getText(self, u'重命名SM文件：', u'输入新的SM文件名：', QtWidgets.QLineEdit.Normal, 'SM_')
        if mes[0]:
            return mes[0]
        else:
            fb_print('没有输入有效内容，仍将保留原本命名', warning=True, viewMes=True)

    def get_mod(self, i):
        '''
        查询场景中的模型，当模型面熟大于等于输入的面数下限时获取该模型名
        :param i: 用户输入的最低模型面数
        :return:模型的transform名与它的面数的对应关系字典
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
        通过模型获取模型的蒙皮关节，当蒙皮关节只有一个时与模型生成对应字典
        :param mod_dir:模型字典
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
                fb_print('模型{}的蒙皮关节应为一个，实际为{}个'.format(key, itme),
                         warning=True, path=FILE_PATH, line=LIN.f_lineno, viewMes=True)
        return jnt_dir

    def get_modJoint(self, mod):
        '''
        获取模型的蒙皮关节列表
        :param mod: 有蒙皮的模型
        :return:
        '''
        jnt_lis = []  #模型的影响关节会被放入这个列表里
        skin = mm.eval('findRelatedSkinCluster("{}")'.format(mod))
        if skin:
            for jnt in mc.skinCluster(skin, inf=1, q=1):  #从蒙皮节点名得到受影响的关节
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

