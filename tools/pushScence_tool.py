# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.api.OpenMaya as oma
import maya.OpenMayaUI as omui

import os
import shutil
import glob
from plug_ins.pathlib import PurePath
from functools import partial

from feedback_tool import Feedback_info as fp
from data_path import icon_dic as ic, projectPath_xxtt
from dutils import fileUtils
from qtwidgets import SeparatorAction as menl
import rig_tool
reload(rig_tool)
from rig_tool import exportSelectToFbx


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class MyButton(QtWidgets.QPushButton):
    clickedRightSig = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(MyButton, self).__init__(parent)

    def mousePressEvent(self, event):
        super(MyButton, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.RightButton:
            self.clickedRightSig.emit(True)


class ClearItem(QtWidgets.QWidget):
    def __init__(self, fun, interpretation, parent=None):
        super(ClearItem, self).__init__(parent)
        self.setMaximumHeight(40)
        # self.setAutoFillBackground(True)
        # palette = self.palette()
        # palette.setColor(QtGui.QPalette.Window, QtGui.QColor(78, 42, 66))
        # self.setPalette(palette)

        self.fun = fun
        self.interpretation = interpretation

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.tooBut_switch = QtWidgets.QToolButton()
        self.tooBut_switch.setDisabled(False)
        self.tooBut_switch.setIconSize(QtCore.QSize(32, 32))
        self.tooBut_switch.setFixedSize(QtCore.QSize(35, 35))
        self.tooBut_switch.setToolTip(u'当场景被该项清理后，该复选框将被打√')
        self.on_toggled()

        self.lab_txt = QtWidgets.QLabel(self.interpretation)
        self.but_artificial = QtWidgets.QPushButton(u'单独清理')

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(self.tooBut_switch)
        main_layout.addWidget(self.lab_txt)
        main_layout.addWidget(self.but_artificial)

    def create_connections(self):
        self.but_artificial.clicked.connect(self.run_function)

    def run_function(self):
        """
        清理该item对应的问题
        :return:
        """
        from dutils import clearUtils
        reload(clearUtils)
        fun = getattr(clearUtils, self.fun)  #将模块与函数组装起来形成一个新的函数，该函数可用于直接执行
        if not fun():  #清理发生在此处
            self.on_toggled(True)
        else:
            self.on_toggled(False)

    def on_toggled(self, checked=None):
        """
        切换复选框的图标
        :param checked:
        :return:
        """
        if checked:
            self.tooBut_switch.setIcon(QtGui.QIcon(ic['checkBox_yes']))
        elif checked == False:  #不能用not checked 因为none也属于not False
            self.tooBut_switch.setIcon(QtGui.QIcon(ic['checkBox_error']))
        else:
            self.tooBut_switch.setIcon(QtGui.QIcon(ic['checkBox_blank']))


class pushWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(pushWindow, self).__init__(parent)

        self.setWindowTitle(u'上传rig到CGT')

        if mc.about(ntOS=True):  #判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.clearWgt_lis = []
        if os.path.exists(projectPath_xxtt):
            self.project_path = projectPath_xxtt
            self.project_name = self.project_path.split('/')[2]
        else:
            fp('导入服务器路径出错，请检查服务器映射是否成功.。')

        self.assetType_lis = [f for f in os.listdir(self.project_path) if
                              os.path.isdir(os.path.join(self.project_path, f))]
        self.asset_dir = {}
        for assetType in self.assetType_lis:
            self.asset_dir[assetType] = []
            assetPath = self.project_path + assetType
            for nam in [f for f in os.listdir(assetPath) if os.path.isdir(os.path.join(assetPath, f))]:
                self.asset_dir[assetType].append(nam.decode('GBK'))

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.refresh_Item()

    def create_widgets(self):
        self.but_clearScence = MyButton(u'清理当前场景')
        self.but_clearScence.setMinimumWidth(250)

        self.wdg_clear_lis = QtWidgets.QWidget()
        self.area_clear_lis = QtWidgets.QScrollArea()  # 生成一个有滑条的控件
        self.area_clear_lis.setMinimumHeight(300)
        self.area_clear_lis.setWidgetResizable(True)
        self.area_clear_lis.setWidget(self.wdg_clear_lis)
        clear_layout = QtWidgets.QVBoxLayout(self.wdg_clear_lis)
        clear_layout.setContentsMargins(2, 2, 2, 2)
        for fun in zip(['clear_name', 'clear_nameSpace', 'clear_key', 'clear_hik', 'clear_animLayer', 'inspect_weight'],
                       [u'查询场景重名', u'清理空间名称', u'清理关键帧', u'清理humanIK', u'清理动画层',
                        u'检查权重总量']):
            wdg = ClearItem(fun[0], fun[1], parent=self.area_clear_lis)
            self.clearWgt_lis.append(wdg)
            clear_layout.addWidget(wdg)
        self.area_clear_lis.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.area_clear_lis.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.lin_searchName = QtWidgets.QLineEdit()
        self.lin_searchName.setMinimumHeight(35)
        self.but_clearName = QtWidgets.QPushButton()
        self.but_clearName.setFixedSize(35, 35)
        self.but_clearName.setIcon(QtGui.QIcon(ic['delete']))
        self.but_clearName.setIconSize(QtCore.QSize(35, 35))

        self.lst_asset = QtWidgets.QListWidget()
        self.lst_asset.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.but_push_rig = QtWidgets.QPushButton(u'上传rig文件')
        self.but_push_rig.setEnabled(True)
        self.but_push_fbx = QtWidgets.QPushButton(u'上传fbx文件')

    def create_layout(self):
        layout_clear = QtWidgets.QVBoxLayout()
        layout_clear.addWidget(self.but_clearScence)
        layout_clear.addWidget(self.area_clear_lis)

        layout_search = QtWidgets.QHBoxLayout()
        layout_search.addWidget(self.lin_searchName)
        layout_search.addWidget(self.but_clearName)

        layout_pushBut = QtWidgets.QHBoxLayout()
        layout_pushBut.addWidget(self.but_push_rig)
        layout_pushBut.addWidget(self.but_push_fbx)

        layout_push = QtWidgets.QVBoxLayout()
        layout_push.addLayout(layout_search)
        layout_push.addWidget(self.lst_asset)
        layout_push.addLayout(layout_pushBut)

        wdt_left = QtWidgets.QWidget()
        wdt_left.setLayout(layout_clear)
        wdt_reght = QtWidgets.QWidget()
        wdt_reght.setLayout(layout_push)

        spt_layout = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        spt_layout.addWidget(wdt_left)
        spt_layout.addWidget(wdt_reght)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(spt_layout)

    def create_connections(self):
        self.but_clearScence.clicked.connect(self.autoClearScence)
        self.but_clearScence.clickedRightSig.connect(self.restoreItemCheckBox)
        self.but_clearName.clicked.connect(self.lin_searchName.clear)
        self.lst_asset.itemDoubleClicked.connect(partial(self.menu_function, 'openRigFile'))
        self.lst_asset.customContextMenuRequested.connect(self.create_contextMenu)
        self.lin_searchName.textChanged.connect(self.refresh_Item)
        self.but_push_rig.clicked.connect(self.push_asset)
        self.but_push_fbx.clicked.connect(self.push_select_to_fbx)

    def autoClearScence(self):
        """
        自动清理所有清理项
        :return:
        """
        for wdg in self.clearWgt_lis:
            wdg.run_function()

    def restoreItemCheckBox(self):
        """
        将清理项的图标返回空白状态
        :return:
        """
        for wdg in self.clearWgt_lis:
            wdg.on_toggled(None)

    def refresh_Item(self):
        """
        为列表视图生成项
        :return:
        """

        def add_item():
            item = QtWidgets.QListWidgetItem(nam)
            item.setData(QtCore.Qt.UserRole, os.path.join(self.project_path, typ, nam, 'Rig', 'Final'))  #资产所在文件夹
            item.setData(QtCore.Qt.UserRole + 1, typ)  #资产类型
            item.setData(QtCore.Qt.UserRole + 2, nam)  #资产名
            item.setData(QtCore.Qt.UserRole + 3, os.path.join(self.project_path, typ, nam, 'Rig', 'Unreal'))  #fbx文件路径
            self.lst_asset.addItem(item)

        self.lst_asset.clear()
        searchInfo = self.lin_searchName.text()
        for typ, nam_lis in self.asset_dir.items():
            for nam in nam_lis:
                if searchInfo:
                    if searchInfo.lower() in nam.lower():
                        add_item()
                else:
                    add_item()

    def create_contextMenu(self, pos):
        """
        在资产项上添加右键生成上下文菜单
        :param pos: 鼠标右键点击时的位置
        :return:
        """
        menu = QtWidgets.QMenu()
        #menu.setTearOffEnabled(True)#使菜单可以被撕下，当前位置不可用
        if self.lst_asset.itemAt(pos):
            action_openRigFile = menu.addAction(u'打开该资产rig文件')
            action_openModFile = menu.addAction(u'打开该资产mod文件')

            menu.addAction(menl(p=menu))
            action_copyRigFile = menu.addAction(u'复制该资产的rig文件')
            action_copyModFile = menu.addAction(u'复制该资产的mod文件')
            action_dupRigPath = menu.addAction(u'复制该资产的rig路径')
            action_dupModPath = menu.addAction(u'复制该资产的mod路径')
            menu.addAction(menl(p=menu))
            action_openRIgPath = menu.addAction(u'用资产管理器打开该资产的rig文件夹')
            action_openModPath = menu.addAction(u'用资产管理器打开该资产的mod文件夹')
            #------------------------------------------------------------------------------
            action_openRigFile.triggered.connect(partial(self.menu_function, 'openRigFile'))
            action_openModFile.triggered.connect(partial(self.menu_function, 'openModFile'))

            action_copyRigFile.triggered.connect(partial(self.menu_function, 'copyRigFile'))
            action_copyModFile.triggered.connect(partial(self.menu_function, 'copyModFile'))

            action_dupRigPath.triggered.connect(partial(self.menu_function, 'copyRigPath'))
            action_dupModPath.triggered.connect(partial(self.menu_function, 'copyModPath'))

            action_openRIgPath.triggered.connect(partial(self.menu_function, 'openRigPath'))
            action_openModPath.triggered.connect(partial(self.menu_function, 'openModPath'))

        menu.exec_(self.lst_asset.mapToGlobal(pos))  #菜单生成的位置

    def menu_function(self, inf, *args):
        """
        菜单项的槽函数，用来执行各个命令
        :param inf: 用于分辨是哪个信号的信息
        :return:
        """
        sel_item = self.lst_asset.selectedItems()[0]
        path = sel_item.data(QtCore.Qt.UserRole)  #rig文件所在路径
        if not os.path.exists(sel_item.data(QtCore.Qt.UserRole)):
            oma.MGlobal.displayError('资产{}没有rig文件夹'.format(sel_item.data(QtCore.Qt.UserRole + 2)))
            return None
        file_path = glob.glob(os.path.join(path, '*.ma'))  #path路径下所有ma文件的绝对路径列表

        if inf == 'openRigFile':
            if file_path and os.path.exists(file_path[0]):
                if mc.file(mf=True, q=True):
                    rest = mc.confirmDialog(title='警告', message='当前场景已被更改，是否保存后打开？',
                                            button=['保存', '不保存', '取消'])
                    if rest == u'保存':
                        mc.file(s=True)
                    elif rest == u'不保存':
                        mc.file(file_path[0], f=True, o=True, iv=True, typ='mayaAscii', op='v=0')
                    elif rest == u'取消':
                        pass
                else:
                    mc.file(file_path[0], o=True, iv=True, typ='mayaAscii', op='v=0')
            else:
                oma.MGlobal.displayError('资产{}没有rig文件'.format(sel_item.data(QtCore.Qt.UserRole + 2)))
        elif inf == 'openModFile':
            path = path.replace('Rig', 'Mod')
            mod_path = glob.glob(os.path.join(path, '*.ma'))
            if mod_path and os.path.exists(mod_path[0]):
                if mc.file(mf=True, q=True):
                    rest = mc.confirmDialog(title='警告', message='当前场景已被更改，是否保存后打开？',
                                            button=['保存', '不保存', '取消'])
                    if rest == u'保存':
                        mc.file(s=True)
                    elif rest == u'不保存':
                        mc.file(mod_path[0], f=True, o=True, iv=True, typ='mayaAscii', op='v=0')
                    elif rest == u'取消':
                        pass
                else:
                    mc.file(mod_path[0], o=True, iv=True, typ='mayaAscii', op='v=0')
            else:
                oma.MGlobal.displayError('资产{}没有mod文件'.format(sel_item.data(QtCore.Qt.UserRole + 2)))
        #----------------------------------------------------
        elif inf == 'copyRigFile':
            if file_path and os.path.exists(file_path[0]):
                cb = QtWidgets.QApplication.clipboard()
                md = QtCore.QMimeData()
                md.setUrls([PurePath(file_path[0]).as_uri()])
                cb.setMimeData(md)
            else:
                oma.MGlobal.displayError('资产{}没有rig文件'.format(sel_item.data(QtCore.Qt.UserRole + 2)))
        elif inf == 'copyModFile':
            path = path.replace('Rig', 'Mod')
            mod_path = glob.glob(os.path.join(path, '*.ma'))
            if mod_path and os.path.exists(mod_path[0]):
                cb = QtWidgets.QApplication.clipboard()
                md = QtCore.QMimeData()
                md.setUrls([PurePath(mod_path[0]).as_uri()])
                cb.setMimeData(md)
            else:
                oma.MGlobal.displayError('资产{}没有mod文件'.format(sel_item.data(QtCore.Qt.UserRole + 2)))
        #----------------------------------------------------
        elif inf == 'copyRigPath':
            cb = QtWidgets.QApplication.clipboard()
            md = QtCore.QMimeData()
            md.setText(path)
            cb.setMimeData(md)
        elif inf == 'copyModPath':
            path = path.replace('Rig', 'Mod')
            cb = QtWidgets.QApplication.clipboard()
            md = QtCore.QMimeData()
            md.setText(path)
            cb.setMimeData(md)
        #----------------------------------------------------
        elif inf == 'openRigPath':
            os.startfile(path)
        elif inf == 'openModPath':
            modPath = path.replace('Rig', 'Mod')
            if os.path.exists(modPath):
                os.startfile(modPath)
            else:
                fp('资产{}没有模型文件夹'.format(sel_item.data(QtCore.Qt.UserRole + 2)), warning=True)

    def push_asset(self):
        """
        上传文件
        :return:
        """
        sel_items = self.lst_asset.selectedItems()
        if sel_items:
            file_path = sel_items[0].data(QtCore.Qt.UserRole)
            scenceFile_path = mc.file(exn=True, q=True)  #当前文件所在完整路径
            scence_path = os.path.dirname(os.path.abspath(scenceFile_path))  #当前文件所在路径
            asset_path = sel_items[0].data(QtCore.Qt.UserRole)  #选择的资产所在路径

            if not os.path.exists(file_path):  #当该资产的rig文件夹还没创建时
                fp('正在创建{}的rig文件夹······'.format(sel_items[0].data(QtCore.Qt.UserRole + 2)), info=True)
                rig_path = os.path.dirname(os.path.abspath(file_path))
                os.mkdir(rig_path)
                os.mkdir(file_path)
                os.mkdir(file_path.replace('Final', 'Unreal'))

            self.iterate_file(sel_items[0])  #向历史文件夹中迭代文件
            if os.path.normcase(os.path.abspath(asset_path)) == os.path.normcase(os.path.abspath(scence_path)):
                # 当打开的文件就在服务器路径里时
                self.but_push_rig.setText(u'正在保存场景······')
                fp('正在保存场景······', info=True, viewMes=True)
                mc.file(s=True, f=True, op='v=0')
                self.but_push_rig.setText(u'场景上传成功！！')
                fp('场景上传成功', info=True, viewMes=True)
            else:
                self.push_file(sel_items[0])  #上传文件
        else:
            fp('没有选择需要提交的资产名', error=True, viewMes=True)

    def iterate_file(self, item):
        """
        迭代保存
        :param item:被选中的项
        :return:
        """
        file_path = item.data(QtCore.Qt.UserRole)  #服务器文件所在路径
        file_nam = '_'.join(
            [self.project_name, item.data(QtCore.Qt.UserRole + 1), item.data(QtCore.Qt.UserRole + 2), 'Rig.ma'])  #文件名
        fileNam_path = '/'.join([file_path, file_nam])  #服务器文件完整路径
        fileHistory_path = '/'.join([file_path, 'history'])  #服务器历史文件夹路径
        if os.path.exists(fileNam_path):
            if not os.path.exists(fileHistory_path):
                self.but_push_rig.setText(u'正在创建历史文件夹······')
                fp('正在创建历史文件夹······', info=True)
                os.mkdir(fileHistory_path)

            newHty_nam = self.get_history_id(fileHistory_path, file_nam)
            if not fileHistory_path:
                newHty_nam = file_nam.split('.')[0] + '_v01.ma'

            try:
                self.but_push_rig.setText(u'正在向历史文件夹内复制文件······')
                fp('正在向历史文件夹内复制文件······', info=True)
                shutil.copy(fileNam_path, '/'.join([fileHistory_path, newHty_nam]))

            except Exception as e:
                fp(
                    '{}复制到{}历史文件夹出错:{}'.format(fileNam_path, '/'.join([fileHistory_path, newHty_nam]), e),
                    error=True, viewMes=True)
        else:
            fp('文件还未上传第一版', info=True)

    def push_file(self, item):
        """
        将当前文件上传到服务器文件路径下
        :param item:
        :return:
        """
        file_nam = '_'.join(
            [self.project_name, item.data(QtCore.Qt.UserRole + 1), item.data(QtCore.Qt.UserRole + 2), 'Rig.ma'])  #文件名
        file_path = item.data(QtCore.Qt.UserRole)  #服务器文件所在路径

        self.but_push_rig.setText(u'正在保存场景······')
        fp('正在保存场景······', info=True, viewMes=True)
        mc.file(s=True, f=True, op='v=0')
        self.but_push_rig.setText(u'正在上传场景······')
        fp('正在上传场景······', info=True, viewMes=True)
        shutil.copy(mc.file(exn=True, q=True), '/'.join([file_path, file_nam]))
        self.but_push_rig.setText(u'场景上传成功！！')
        fp('场景上传成功', info=True, viewMes=True)

    @staticmethod
    def get_history_id(path, nam):
        """
        通过给定的历史文件夹路径获取该资产应该产生的下一个迭代文件名
        :param nam: 该资产的rig完整名
        :param path:历史文件夹
        :return:
        """
        file_names = os.listdir(path)
        file_names = [f for f in file_names if os.path.splitext(f)[1] == '.ma']

        prefix = nam.split('.')[0]
        if file_names:
            f_lis = []
            for f in file_names:
                if prefix in f and nam != f:
                    f_prefix = f.split('.')[0]
                    if prefix + '_v' in f_prefix:
                        i = int(f_prefix.replace(prefix + '_v', ''))
                    else:
                        continue
                    f_lis.append(i)

            f_lis.sort()
            return '{}_v{}.ma'.format(prefix, str(f_lis[-1] + 1).zfill(2))

        else:
            return '{}_v01.ma'.format(prefix)

    def push_select_to_fbx(self):
        """
        将当前选中对象导出为fbx并上传到指定资产sk文件夹内
        :return:
        """
        sel_items = self.lst_asset.selectedItems()
        if not sel_items:
            fp('没有选中有效项。', error=True, viewMes=True)

        folder_path = sel_items[0].data(QtCore.Qt.UserRole + 3)  #fbx文件夹服务器路径
        file_absPath = exportSelectToFbx()  #fbx保存的文件路径
        file_name = 'SK_{}.fbx'.format(sel_items[0].data(QtCore.Qt.UserRole + 2))  #fbx文件名
        file_path = os.sep.join([folder_path, file_name])  #fbx服务器文件路径
        if os.path.normcase(os.path.abspath(file_absPath)) == os.path.normcase(os.path.abspath(file_path)):
            fp('保存文件就是服务器fbx文件路径地址。', info=True)
        else:  #当保存位置与服务器fbx文件位置不相等时
            if not os.path.exists(folder_path):  #服务器fbx文件夹路径不存在时
                os.mkdir(folder_path)
            if os.path.exists(file_path):  #服务器fbx文件存在时
                fp('正在向历史文件夹内保存文件。', info=True)
                fileUtils.version_up(folder_path, file_name)  #保存历史文件
                fp('历史文件保存成功。', info=True)
            try:
                fp('正在向服务器中提交fbx文件。', info=True)
                shutil.copyfile(file_absPath, file_path)
                fp('fbx文件提交成功。', info=True)
                self.but_push_fbx.setText(u'fbx文件提交成功')
            except Exception as e:
                self.but_push_fbx.setText(u'fbx文件提交失败')
                fp('fbx文件提交失败。{}'.format(e), error=True, viewMes=True)


def push_rig():
    try:
        pushScence_window.close()
        pushScence_window.deleteLater()
    except:
        pass
    finally:
        pushScence_window = pushWindow()
        pushScence_window.show()
