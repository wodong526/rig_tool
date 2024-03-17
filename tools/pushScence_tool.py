# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.api.OpenMaya as oma
import maya.OpenMayaUI as omui

import os
import glob
from pathlib import PurePath
from functools import partial

from feedback_tool import Feedback_info as fp
import data_path
reload(data_path)
from data_path import icon_dir as ic, projectPath_xxtt as pojpt_xt
from dutils import cgtUtils as cgt
from qt_widgets import SeparatorAction as menl, set_font
from rig_tool import exportSelectToFbx
import folder_widget
reload(folder_widget)
import folder_widget as flw


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


class AssetTtem(QtWidgets.QWidget):
    def __init__(self, l_tex, r_tex, parent=None):
        super(AssetTtem, self).__init__(parent)
        __lab_Ltex = QtWidgets.QLabel(l_tex)
        __lab_Rtex = QtWidgets.QLabel(r_tex)
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(__lab_Ltex)
        main_layout.addStretch()
        main_layout.addWidget(__lab_Rtex)


class ClearItem(QtWidgets.QWidget):
    def __init__(self, fun, interpretation, parent=None):
        super(ClearItem, self).__init__(parent)
        self.setMaximumHeight(40)

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
        fun = getattr(clearUtils, self.fun)  #将模块与函数组装起来形成一个新的函数，该函数可用于直接执行
        if not fun():  #清理发生在此处
            self.on_toggled(True)
            return True#清理成功
        else:
            self.on_toggled(False)
            return False#清理失败

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


class PushWindow(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(PushWindow, self).__init__(parent)

        self.setWindowTitle(u'上传rig到CGT')
        self.setWindowIcon(QtGui.QIcon(ic['cgt_logo']))

        if mc.about(ntOS=True):  #判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.clearWgt_lis = []
        if os.path.exists(pojpt_xt[0]):
            self.project_name = pojpt_xt[0].split('/')[2]
        else:
            fp('导入服务器路径出错，请检查服务器映射是否成功.。', error=True, block=True)

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
        for fun in zip(['clear_name', 'clear_nameSpace', 'clear_key', 'clear_hik', 'clear_animLayer', 'inspect_weight',
                        'clear_unknown_node', 'clear_unknown_plug'],
                       [u'查询场景重名', u'清理空间名称', u'清理关键帧', u'清理humanIK', u'清理动画层', u'检查权重总量',
                        u'清理未知节点', u'清理未知插件']):
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
        self.but_localAsset = QtWidgets.QPushButton(u'->')
        self.but_localAsset.setFixedSize(35, 35)

        self.lst_asset = QtWidgets.QListWidget()
        self.lst_asset.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.comb_typ = QtWidgets.QComboBox()
        self.comb_typ.setMaximumSize(65, 25)
        self.comb_typ.setFont(set_font(10))
        self.comb_typ.addItems([u'模型', u'绑定', u'ueFBX'])
        self.but_push = QtWidgets.QPushButton(u'上传')

        self.wid_folder = flw.FolderWidget()
        self.wid_folder.setVisible(False)

    def create_layout(self):
        layout_clear = QtWidgets.QVBoxLayout()
        layout_clear.addWidget(self.but_clearScence)
        layout_clear.addWidget(self.area_clear_lis)

        layout_search = QtWidgets.QHBoxLayout()
        layout_search.setSpacing(3)
        layout_search.addWidget(self.lin_searchName)
        layout_search.addWidget(self.but_clearName)
        layout_search.addWidget(self.but_localAsset)

        layout_pushBut = QtWidgets.QHBoxLayout()
        layout_pushBut.addWidget(self.comb_typ)
        layout_pushBut.addWidget(self.but_push)

        layout_push = QtWidgets.QVBoxLayout()
        layout_push.addLayout(layout_search)
        layout_push.addWidget(self.lst_asset)
        layout_push.addLayout(layout_pushBut)

        wdt_left = QtWidgets.QWidget()
        wdt_left.setLayout(layout_clear)
        wdt_left.setMaximumWidth(300)
        wdt_reght = QtWidgets.QWidget()
        wdt_reght.setMinimumWidth(270)
        wdt_reght.setLayout(layout_push)

        spt_layout = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        spt_layout.addWidget(wdt_left)
        spt_layout.addWidget(wdt_reght)
        spt_layout.addWidget(self.wid_folder)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(spt_layout)

    def create_connections(self):
        self.but_clearScence.clicked.connect(self.autoClearScence)
        self.but_clearScence.clickedRightSig.connect(self.restoreItemCheckBox)
        self.but_clearName.clicked.connect(self.lin_searchName.clear)
        self.but_localAsset.clicked.connect(self.local_asset_widget_vis)
        self.lst_asset.itemDoubleClicked.connect(partial(self.menu_function, 'openRigFile'))
        self.lst_asset.customContextMenuRequested.connect(self.create_contextMenu)
        self.lin_searchName.returnPressed.connect(self.refresh_Item)
        self.but_push.clicked.connect(self.push_file)

    def autoClearScence(self):
        """
        自动清理所有清理项
        :return:
        """
        self.but_clearScence.setStyleSheet("background-color: green")
        for wdg in self.clearWgt_lis:
            if not wdg.run_function():
                self.but_clearScence.setStyleSheet("background-color: red")

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

        def add_item(ass_nam, ch_nam, ass_typ, uid, mod_final, rig_final, rig_unreal, dyn_final):
            """
            向列表编辑器中添加项，并附上每项的相关信息
            :param ass_nam: 资产的英文名
            :param ch_nam: 资产的中文名
            :param ass_typ: 资产的类型名
            :param uid: 资产的mod阶段id
            :param mod_final: 模型文件夹路径
            :param rig_final: 绑定文件夹路径
            :param rig_unreal: uefbx文件夹路径
            :param dyn_final: 特效dyn文件夹路径
            :return: None
            """
            item = QtWidgets.QListWidgetItem(self.lst_asset)
            self.lst_asset.setItemWidget(item, AssetTtem(ass_nam, ch_nam))
            item.setData(QtCore.Qt.UserRole, uid)  #资产的task.mod.id
            item.setData(QtCore.Qt.UserRole + 1, mod_final)  #mod文件夹
            item.setData(QtCore.Qt.UserRole + 2, rig_final)  #rig文件夹
            item.setData(QtCore.Qt.UserRole + 3, rig_unreal)  #ueFBX文件夹
            item.setData(QtCore.Qt.UserRole + 4, dyn_final)  #dyn文件夹
            item.setData(QtCore.Qt.UserRole + 5, ass_typ)  #资产类型名
            item.setData(QtCore.Qt.UserRole + 6, ass_nam)  #资产名(英文)

        self.lst_asset.clear()
        searchInfo = self.lin_searchName.text()
        mod_dir = cgt.get_asset_dir(pojpt_xt[1])
        mod_id_lis = cgt.get_id_lis(pojpt_xt[1], 'asset')
        folder_dir = cgt.get_asset_folder(pojpt_xt[1], mod_id_lis)
        typ_dir = cgt.get_asset_type(pojpt_xt[1], mod_id_lis)
        for i in mod_id_lis:  #返回的是所有id的文件夹列表
            if searchInfo:
                if searchInfo.lower() in mod_dir[i][1].lower() or searchInfo in mod_dir[i][0]:
                    add_item(mod_dir[i][1], mod_dir[i][0], typ_dir[i], i, *folder_dir[i])
            else:
                add_item(mod_dir[i][1], mod_dir[i][0], typ_dir[i], i, *folder_dir[i])

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
            action_openUePath = menu.addAction(u'用资产管理器打开该资产的UeFbx文件夹')
            #------------------------------------------------------------------------------
            action_openRigFile.triggered.connect(partial(self.menu_function, 'openRigFile'))
            action_openModFile.triggered.connect(partial(self.menu_function, 'openModFile'))

            action_copyRigFile.triggered.connect(partial(self.menu_function, 'copyRigFile'))
            action_copyModFile.triggered.connect(partial(self.menu_function, 'copyModFile'))

            action_dupRigPath.triggered.connect(partial(self.menu_function, 'copyRigPath'))
            action_dupModPath.triggered.connect(partial(self.menu_function, 'copyModPath'))

            action_openRIgPath.triggered.connect(partial(self.menu_function, 'openRigPath'))
            action_openModPath.triggered.connect(partial(self.menu_function, 'openModPath'))
            action_openUePath.triggered.connect(partial(self.menu_function, 'openUefbxPath'))

        menu.exec_(self.lst_asset.mapToGlobal(pos))  #菜单生成的位置

    def menu_function(self, inf, *args):
        """
        菜单项的槽函数，用来执行各个命令
        :param inf: 用于分辨是哪个信号的信息
        :return:
        """
        sel_item = self.lst_asset.selectedItems()[0]
        path = sel_item.data(QtCore.Qt.UserRole + 2)  #rig文件所在路径
        # if not os.path.exists(sel_item.data(QtCore.Qt.UserRole + 2)):
        #     oma.MGlobal.displayError('资产{}没有rig文件夹'.format(sel_item.data(QtCore.Qt.UserRole + 6)))
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
                oma.MGlobal.displayError('资产{}没有rig文件'.format(sel_item.data(QtCore.Qt.UserRole + 6)))
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
                oma.MGlobal.displayError('资产{}没有mod文件'.format(sel_item.data(QtCore.Qt.UserRole + 6)))
        #----------------------------------------------------
        elif inf == 'copyRigFile':
            if file_path and os.path.exists(file_path[0]):
                cb = QtWidgets.QApplication.clipboard()
                md = QtCore.QMimeData()
                md.setUrls([PurePath(file_path[0]).as_uri()])
                cb.setMimeData(md)
            else:
                oma.MGlobal.displayError('资产{}没有rig文件'.format(sel_item.data(QtCore.Qt.UserRole + 6)))
        elif inf == 'copyModFile':
            path = path.replace('Rig', 'Mod')
            mod_path = glob.glob(os.path.join(path, '*.ma'))
            if mod_path and os.path.exists(mod_path[0]):
                cb = QtWidgets.QApplication.clipboard()
                md = QtCore.QMimeData()
                md.setUrls([PurePath(mod_path[0]).as_uri()])
                cb.setMimeData(md)
            else:
                oma.MGlobal.displayError('资产{}没有mod文件'.format(sel_item.data(QtCore.Qt.UserRole + 6)))
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
            if os.path.exists(path):
                os.startfile(path)
            else:
                fp('资产{}没有rig文件夹'.format(sel_item.data(QtCore.Qt.UserRole + 6)), warning=True)
        elif inf == 'openModPath':
            modPath = path.replace('Rig', 'Mod')
            if os.path.exists(modPath):
                os.startfile(modPath)
            else:
                fp('资产{}没有模型文件夹'.format(sel_item.data(QtCore.Qt.UserRole + 6)), warning=True)
        elif inf == 'openUefbxPath':
            fbxPath = sel_item.data(QtCore.Qt.UserRole + 3)
            if os.path.exists(fbxPath):
                os.startfile(fbxPath)
            else:
                fp('资产{}没有UeFbx文件夹'.format(sel_item.data(QtCore.Qt.UserRole + 6)), warning=True)
        else:
            fp('好像参数不对啊！淦！！', warning=True, viewMes=True)

    def push_file(self):
        sel_item = None
        if self.lst_asset.selectedItems():
            sel_item = self.lst_asset.selectedItems()[0]
        else:
            fp('没有选择有效项', error=True, viewMes=True)

        push_typ = {0: 'mod_body', 1: 'rig_body', 2: 'rig_fbx'}[self.comb_typ.currentIndex()]
        if push_typ in ['rig_body', 'rig_fbx']:#当为rig模块时
            ids = cgt.get_id_lis(pojpt_xt[1], stage='Rig')
            for uid, val in cgt.get_asset_dir(pojpt_xt[1], ids, ['asset.entity']).items():#通过资产名匹配获得rig阶段的id
                if val[0] == sel_item.data(QtCore.Qt.UserRole+6):
                    res = None#提交结果。true:提交成功/false:提交失败
                    path = None#提交到的目录文件路径，包含文件本身
                    if push_typ == 'rig_body':
                        res, path = cgt.push_file_to_teamWork(pojpt_xt[1], uid, push_typ, mc.file(exn=True, q=True))
                    elif push_typ == 'rig_fbx':
                        fbx_path = exportSelectToFbx() if sel_item.data(
                            QtCore.Qt.UserRole + 5) == 'CHR' else exportSelectToFbx(totpose=False)  #fbx保存的文件路径
                        res, path = cgt.push_file_to_teamWork(pojpt_xt[1], uid, push_typ, fbx_path, save=False)
                    if res:
                        fp('文件{}上传成功！！'.format(path), info=True, viewMes=True) if cgt.set_status(pojpt_xt[1], uid) \
                            else fp('文件{}上传成功但状态未修改成功'.format(path), warning=True, viewMes=True)
                    elif not res:
                        fp('文件{}上传失败！！'.format(path), error=True, viewMes=True)
                    else:
                        fp('未知的结果。', warning=True, viewMes=True)
                    break
        elif push_typ in ['mod_body']:#当为mod模块时，因为当前项储存的id就是mod.id，所以不需要检测rig的id
            res, path = cgt.push_file_to_teamWork(pojpt_xt[1], sel_item.data(QtCore.Qt.UserRole), push_typ,
                                                  mc.file(exn=True, q=True))
            if res:
                fp('文件{}上传成功！！'.format(path), info=True, viewMes=True) \
                    if cgt.set_status(pojpt_xt[1], sel_item.data(QtCore.Qt.UserRole)) \
                    else fp('文件{}上传成功但状态未修改成功'.format(path), warning=True, viewMes=True)
                self.but_push.setText(u'{}上传成功'.format(sel_item.data(QtCore.Qt.UserRole+6)))
            elif not res:
                fp('文件{}上传失败！！'.format(path), error=True, viewMes=True)
            else:
                fp('未知的结果。', warning=True, viewMes=True)

    def local_asset_widget_vis(self):
        if self.wid_folder.isVisible():
            self.wid_folder.setVisible(False)
            self.but_localAsset.setText(u'->')
        else:
            self.wid_folder.setVisible(True)
            self.but_localAsset.setText(u'<-')


def push_rig():
    try:
        pushScence_window.close()
        pushScence_window.deleteLater()
    except:
        pass
    finally:
        pushScence_window = PushWindow()
        pushScence_window.show()
