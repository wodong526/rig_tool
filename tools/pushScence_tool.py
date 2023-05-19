# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance
from functools import partial

import maya.cmds as mc
import maya.api.OpenMaya as oma
import maya.OpenMayaUI as omui

import os
import re
import shutil
import glob
from plugs.pathlib import PurePath

from feedback_tool import Feedback_info as fb_print, LIN as lin
import data_path


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
            self.setStyleSheet(
                'QPushButton:pressed {background-color: #7f7f7f; border: 1px solid #616161; padding-left: 5px; padding-top: 5px;}')
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
        self.tooBut_switch.setToolTip(u'����������������󣬸ø�ѡ�򽫱����')
        self.on_toggled(None)

        self.lab_txt = QtWidgets.QLabel(self.interpretation)
        self.but_artificial = QtWidgets.QPushButton(u'��������')

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(self.tooBut_switch)
        main_layout.addWidget(self.lab_txt)
        main_layout.addWidget(self.but_artificial)

    def create_connections(self):
        self.but_artificial.clicked.connect(self.run_function)

    def run_function(self):
        from dutils import clearUtils
        fun = getattr(clearUtils, self.fun)
        try:
            fun()
            self.on_toggled(True)
        except Exception as e:
            self.on_toggled(False)
            oma.MGlobal.displayError(e)

    def on_toggled(self, checked):
        if checked:
            self.tooBut_switch.setIcon(QtGui.QIcon('{}checkBox_yes.png'.format(data_path.iconPath)))
        elif checked == False:
            self.tooBut_switch.setIcon(QtGui.QIcon('{}checkBox_error.png'.format(data_path.iconPath)))
        else:
            self.tooBut_switch.setIcon(QtGui.QIcon('{}checkBox_blank.png'.format(data_path.iconPath)))


class pushWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(pushWindow, self).__init__(parent)

        self.setWindowTitle(u'�ϴ�rig��CGT')

        if mc.about(ntOS=True):  #�ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.clearWgt_lis = []
        self.project_path = data_path.projectPath
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
        self.but_clearScence = MyButton(u'����ǰ����')
        self.but_clearScence.setMinimumWidth(250)

        self.wdg_clear_lis = QtWidgets.QWidget()
        self.area_clear_lis = QtWidgets.QScrollArea()  # ����һ���л����Ŀؼ�
        self.area_clear_lis.setMinimumHeight(300)
        self.area_clear_lis.setWidgetResizable(True)
        self.area_clear_lis.setWidget(self.wdg_clear_lis)
        clear_layout = QtWidgets.QVBoxLayout(self.wdg_clear_lis)
        clear_layout.setContentsMargins(2, 2, 2, 2)
        for fun in zip(['clear_nameSpace', 'clear_key', 'clear_hik', 'clear_animLayer'],
                       [u'����ռ�����', u'����ؼ�֡', u'����humanIK', u'��������']):
            wdg = ClearItem(fun[0], fun[1], parent=self.area_clear_lis)
            self.clearWgt_lis.append(wdg)
            clear_layout.addWidget(wdg)
        self.area_clear_lis.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.area_clear_lis.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.lin_searchName = QtWidgets.QLineEdit()
        self.lin_searchName.setMinimumHeight(35)
        self.but_clearName = QtWidgets.QPushButton()
        self.but_clearName.setFixedSize(35, 35)
        self.but_clearName.setIcon(QtGui.QIcon('{}delete.png'.format(data_path.iconPath)))
        self.but_clearName.setIconSize(QtCore.QSize(35, 35))

        self.lst_asset = QtWidgets.QListWidget()
        self.lst_asset.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.but_push = QtWidgets.QPushButton(u'�ϴ���������ָ���ʲ���rig�ļ���')
        self.but_push.setEnabled(True)

    def create_layout(self):
        layout_clear = QtWidgets.QVBoxLayout()
        layout_clear.addWidget(self.but_clearScence)
        layout_clear.addWidget(self.area_clear_lis)

        layout_search = QtWidgets.QHBoxLayout()
        layout_search.addWidget(self.lin_searchName)
        layout_search.addWidget(self.but_clearName)

        layout_push = QtWidgets.QVBoxLayout()
        layout_push.addLayout(layout_search)
        layout_push.addWidget(self.lst_asset)
        layout_push.addWidget(self.but_push)

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
        self.lst_asset.customContextMenuRequested.connect(self.create_contextMenu)
        self.lin_searchName.textChanged.connect(self.refresh_Item)
        self.but_push.clicked.connect(self.push_asset)

    def autoClearScence(self):
        """
        �Զ���������������
        :return:
        """
        for wdg in self.clearWgt_lis:
            wdg.run_function()

    def restoreItemCheckBox(self):
        """
        ���������ͼ�귵�ؿհ�״̬
        :return:
        """
        for wdg in self.clearWgt_lis:
            wdg.on_toggled(None)

    def refresh_Item(self):
        """
        Ϊ�б���ͼ������
        :return:
        """

        def add_item():
            item = QtWidgets.QListWidgetItem(nam)
            item.setData(QtCore.Qt.UserRole, os.path.join(self.project_path, typ, nam, 'Rig', 'Final'))  #�ʲ������ļ���
            item.setData(QtCore.Qt.UserRole + 1, typ)  #�ʲ�����
            item.setData(QtCore.Qt.UserRole + 2, nam)  #�ʲ���
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
        menu = QtWidgets.QMenu()
        if self.lst_asset.itemAt(pos):
            action_openFile = menu.addAction(u'�򿪸�rig�ļ�')
            action_copyFile = menu.addAction(u'���Ƹ��ʲ���rig�ļ�')
            action_dupPath = menu.addAction(u'���Ƹ��ʲ���rig·��')
            action_openPath = menu.addAction(u'���ʲ��������򿪸��ʲ���rig�ļ���')
            action_openFile.triggered.connect(partial(self.menu_function, 'openFile'))
            action_copyFile.triggered.connect(partial(self.menu_function, 'copyFile'))
            action_dupPath.triggered.connect(partial(self.menu_function, 'copyPath'))
            action_openPath.triggered.connect(partial(self.menu_function, 'openPath'))

        menu.exec_(self.lst_asset.mapToGlobal(pos))  #�˵����ɵ�λ��

    def menu_function(self, inf):
        sel_item = self.lst_asset.selectedItems()[0]
        path = sel_item.data(QtCore.Qt.UserRole)
        if not os.path.exists(sel_item.data(QtCore.Qt.UserRole)):
            oma.MGlobal.displayError('�ʲ�{}û��rig�ļ���'.format(sel_item.data(QtCore.Qt.UserRole + 2)))
            return None
        file_path = glob.glob(os.path.join(path, '*.ma'))

        if inf == 'openFile':
            if file_path and os.path.exists(file_path[0]):
                if mc.file(mf=True, q=True):
                    rest = mc.confirmDialog(title='����', message='��ǰ�����ѱ����ģ��Ƿ񱣴��򿪣�',
                                            button=['����', '������', 'ȡ��'])
                    if rest == u'����':
                        mc.file(s=True)
                    elif rest == u'������':
                        mc.file(file_path, f=True, o=True, iv=True, typ='mayaAscii', op='v=0')
                    elif rest == u'ȡ��':
                        pass
                else:
                    mc.file(file_path, o=True, iv=True, typ='mayaAscii', op='v=0')
            else:
                oma.MGlobal.displayError('�ʲ�{}û��rig�ļ�'.format(sel_item.data(QtCore.Qt.UserRole + 2)))
        elif inf == 'copyFile':
            if file_path and os.path.exists(file_path[0]):
                cb = QtWidgets.QApplication.clipboard()
                md = QtCore.QMimeData()
                md.setUrls([PurePath(file_path[0]).as_uri()])
                cb.setMimeData(md)
            else:
                oma.MGlobal.displayError('�ʲ�{}û��rig�ļ�'.format(sel_item.data(QtCore.Qt.UserRole + 2)))
        elif inf == 'copyPath':
            com = 'echo | set /p unl = ' + path.strip() + '| clip'
            os.system(com)
        elif inf == 'openPath':
            os.startfile(path)

    def push_asset(self):
        """
        �ϴ��ļ�
        :return:
        """
        sel_items = self.lst_asset.selectedItems()
        if sel_items:
            file_path = sel_items[0].data(QtCore.Qt.UserRole)
            scenceFile_path = mc.file(exn=True, q=True)  #��ǰ�ļ���������·��
            scence_path = os.path.dirname(os.path.abspath(scenceFile_path))  #��ǰ�ļ�����·��

            if not os.path.exists(file_path):  #�����ʲ���rig�ļ��л�û����ʱ
                fb_print('���ڴ���{}��rig�ļ��С�����������'.format(sel_items[0].data(QtCore.Qt.UserRole + 2)), info=True)
                rig_path = os.path.dirname(os.path.abspath(file_path))
                os.mkdir(rig_path)
                os.mkdir(file_path)
                os.mkdir(file_path.replace('Final', 'Unreal'))

            self.iterate_file(sel_items[0])  #����ʷ�ļ����е����ļ�
            if sel_items[0].data(QtCore.Qt.UserRole) == scence_path:  #���򿪵��ļ����ڷ�����·����ʱ
                mc.file(s=True, f=True, op='v=0')
            else:
                self.push_file(sel_items[0])  #�ϴ��ļ�
        else:
            fb_print('û��ѡ����Ҫ�ύ���ʲ���', error=True, viewMes=True)

    def iterate_file(self, item):
        """
        ��������
        :param item:��ѡ�е���
        :return:
        """
        file_path = item.data(QtCore.Qt.UserRole)  #�������ļ�����·��
        file_nam = '_'.join(
            ['FHZJ', item.data(QtCore.Qt.UserRole + 1), item.data(QtCore.Qt.UserRole + 2), 'Rig.ma'])  #�ļ���
        fileNam_path = '/'.join([file_path, file_nam])  #�������ļ�����·��
        fileHistory_path = '/'.join([file_path, 'history'])  #��������ʷ�ļ���·��
        if os.path.exists(fileNam_path):
            if not os.path.exists(fileHistory_path):
                self.but_push.setText(u'���ڴ�����ʷ�ļ��С�����������')
                fb_print('���ڴ�����ʷ�ļ��С�����������', info=True)
                os.mkdir(fileHistory_path)

            newHty_nam = self.get_history_id(fileHistory_path)
            if not newHty_nam:
                newHty_nam = file_nam.split('.')[0] + '_v01.ma'

            try:
                self.but_push.setText(u'��������ʷ�ļ����ڸ����ļ�������������')
                fb_print('��������ʷ�ļ����ڸ����ļ�������������', info=True)
                shutil.copy(fileNam_path, '/'.join([fileHistory_path, newHty_nam]))

            except Exception as e:
                fb_print('�ļ����Ƶ���ʷ�ļ��г���:{}'.format(e), error=True, viewMes=True)
        else:
            fb_print('�ļ���δ�ϴ���һ��', info=True)

    def push_file(self, item):
        """
        ����ǰ�ļ��ϴ����������ļ�·����
        :param item:
        :return:
        """
        file_nam = '_'.join(
            ['FHZJ', item.data(QtCore.Qt.UserRole + 1), item.data(QtCore.Qt.UserRole + 2), 'Rig.ma'])  #�ļ���
        file_path = item.data(QtCore.Qt.UserRole)  #�������ļ�����·��

        self.but_push.setText(u'���ڱ��泡��������������')
        fb_print('���ڱ��泡��������������', info=True, viewMes=True)
        mc.file(s=True, f=True, op='v=0')
        self.but_push.setText(u'�����ϴ�����������������')
        fb_print('�����ϴ�����������������', info=True, viewMes=True)
        shutil.copy(mc.file(exn=True, q=True), '/'.join([file_path, file_nam]))
        self.but_push.setText(u'�����ϴ��ɹ�����')
        fb_print('�����ϴ��ɹ�', info=True, viewMes=True)

    def get_history_id(self, path):
        """
        ͨ����������ʷ�ļ���·����ȡ���ʲ�Ӧ�ò�������һ�������ļ���
        :param path:��ʷ�ļ���
        :return:
        """
        file_names = os.listdir(path)
        file_names = [f for f in file_names if os.path.splitext(f)[1] == '.ma']
        if file_names:
            try:
                file_names.sort(key=lambda x: int(re.findall(r'_v(\d+)', x)[-1]))
            except:
                pass
            else:
                latest_file_name = file_names[-1]
                latest_suffix = latest_file_name.split('_')[-1][1:3]
                next_suffix = int(latest_suffix) + 1
                next_file_name = latest_file_name.replace(latest_suffix, str(next_suffix).rjust(2, '0'))
                return next_file_name
        else:
            return None


def push_rig():
    try:
        pushScence_window.close()
        pushScence_window.deleteLater()
    except:
        pass
    finally:
        pushScence_window = pushWindow()
        pushScence_window.show()
