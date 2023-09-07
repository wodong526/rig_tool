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
        self.tooBut_switch.setToolTip(u'����������������󣬸ø�ѡ�򽫱����')
        self.on_toggled()

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
        """
        �����item��Ӧ������
        :return:
        """
        from dutils import clearUtils
        reload(clearUtils)
        fun = getattr(clearUtils, self.fun)  #��ģ���뺯����װ�����γ�һ���µĺ������ú���������ֱ��ִ��
        if not fun():  #�������ڴ˴�
            self.on_toggled(True)
        else:
            self.on_toggled(False)

    def on_toggled(self, checked=None):
        """
        �л���ѡ���ͼ��
        :param checked:
        :return:
        """
        if checked:
            self.tooBut_switch.setIcon(QtGui.QIcon(ic['checkBox_yes']))
        elif checked == False:  #������not checked ��ΪnoneҲ����not False
            self.tooBut_switch.setIcon(QtGui.QIcon(ic['checkBox_error']))
        else:
            self.tooBut_switch.setIcon(QtGui.QIcon(ic['checkBox_blank']))


class pushWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(pushWindow, self).__init__(parent)

        self.setWindowTitle(u'�ϴ�rig��CGT')

        if mc.about(ntOS=True):  #�ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.clearWgt_lis = []
        if os.path.exists(projectPath_xxtt):
            self.project_path = projectPath_xxtt
            self.project_name = self.project_path.split('/')[2]
        else:
            fp('���������·���������������ӳ���Ƿ�ɹ�.��')

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
        for fun in zip(['clear_name', 'clear_nameSpace', 'clear_key', 'clear_hik', 'clear_animLayer', 'inspect_weight'],
                       [u'��ѯ��������', u'����ռ�����', u'����ؼ�֡', u'����humanIK', u'��������',
                        u'���Ȩ������']):
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
        self.but_push_rig = QtWidgets.QPushButton(u'�ϴ�rig�ļ�')
        self.but_push_rig.setEnabled(True)
        self.but_push_fbx = QtWidgets.QPushButton(u'�ϴ�fbx�ļ�')

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
            item.setData(QtCore.Qt.UserRole + 3, os.path.join(self.project_path, typ, nam, 'Rig', 'Unreal'))  #fbx�ļ�·��
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
        ���ʲ���������Ҽ����������Ĳ˵�
        :param pos: ����Ҽ����ʱ��λ��
        :return:
        """
        menu = QtWidgets.QMenu()
        #menu.setTearOffEnabled(True)#ʹ�˵����Ա�˺�£���ǰλ�ò�����
        if self.lst_asset.itemAt(pos):
            action_openRigFile = menu.addAction(u'�򿪸��ʲ�rig�ļ�')
            action_openModFile = menu.addAction(u'�򿪸��ʲ�mod�ļ�')

            menu.addAction(menl(p=menu))
            action_copyRigFile = menu.addAction(u'���Ƹ��ʲ���rig�ļ�')
            action_copyModFile = menu.addAction(u'���Ƹ��ʲ���mod�ļ�')
            action_dupRigPath = menu.addAction(u'���Ƹ��ʲ���rig·��')
            action_dupModPath = menu.addAction(u'���Ƹ��ʲ���mod·��')
            menu.addAction(menl(p=menu))
            action_openRIgPath = menu.addAction(u'���ʲ��������򿪸��ʲ���rig�ļ���')
            action_openModPath = menu.addAction(u'���ʲ��������򿪸��ʲ���mod�ļ���')
            #------------------------------------------------------------------------------
            action_openRigFile.triggered.connect(partial(self.menu_function, 'openRigFile'))
            action_openModFile.triggered.connect(partial(self.menu_function, 'openModFile'))

            action_copyRigFile.triggered.connect(partial(self.menu_function, 'copyRigFile'))
            action_copyModFile.triggered.connect(partial(self.menu_function, 'copyModFile'))

            action_dupRigPath.triggered.connect(partial(self.menu_function, 'copyRigPath'))
            action_dupModPath.triggered.connect(partial(self.menu_function, 'copyModPath'))

            action_openRIgPath.triggered.connect(partial(self.menu_function, 'openRigPath'))
            action_openModPath.triggered.connect(partial(self.menu_function, 'openModPath'))

        menu.exec_(self.lst_asset.mapToGlobal(pos))  #�˵����ɵ�λ��

    def menu_function(self, inf, *args):
        """
        �˵���Ĳۺ���������ִ�и�������
        :param inf: ���ڷֱ����ĸ��źŵ���Ϣ
        :return:
        """
        sel_item = self.lst_asset.selectedItems()[0]
        path = sel_item.data(QtCore.Qt.UserRole)  #rig�ļ�����·��
        if not os.path.exists(sel_item.data(QtCore.Qt.UserRole)):
            oma.MGlobal.displayError('�ʲ�{}û��rig�ļ���'.format(sel_item.data(QtCore.Qt.UserRole + 2)))
            return None
        file_path = glob.glob(os.path.join(path, '*.ma'))  #path·��������ma�ļ��ľ���·���б�

        if inf == 'openRigFile':
            if file_path and os.path.exists(file_path[0]):
                if mc.file(mf=True, q=True):
                    rest = mc.confirmDialog(title='����', message='��ǰ�����ѱ����ģ��Ƿ񱣴��򿪣�',
                                            button=['����', '������', 'ȡ��'])
                    if rest == u'����':
                        mc.file(s=True)
                    elif rest == u'������':
                        mc.file(file_path[0], f=True, o=True, iv=True, typ='mayaAscii', op='v=0')
                    elif rest == u'ȡ��':
                        pass
                else:
                    mc.file(file_path[0], o=True, iv=True, typ='mayaAscii', op='v=0')
            else:
                oma.MGlobal.displayError('�ʲ�{}û��rig�ļ�'.format(sel_item.data(QtCore.Qt.UserRole + 2)))
        elif inf == 'openModFile':
            path = path.replace('Rig', 'Mod')
            mod_path = glob.glob(os.path.join(path, '*.ma'))
            if mod_path and os.path.exists(mod_path[0]):
                if mc.file(mf=True, q=True):
                    rest = mc.confirmDialog(title='����', message='��ǰ�����ѱ����ģ��Ƿ񱣴��򿪣�',
                                            button=['����', '������', 'ȡ��'])
                    if rest == u'����':
                        mc.file(s=True)
                    elif rest == u'������':
                        mc.file(mod_path[0], f=True, o=True, iv=True, typ='mayaAscii', op='v=0')
                    elif rest == u'ȡ��':
                        pass
                else:
                    mc.file(mod_path[0], o=True, iv=True, typ='mayaAscii', op='v=0')
            else:
                oma.MGlobal.displayError('�ʲ�{}û��mod�ļ�'.format(sel_item.data(QtCore.Qt.UserRole + 2)))
        #----------------------------------------------------
        elif inf == 'copyRigFile':
            if file_path and os.path.exists(file_path[0]):
                cb = QtWidgets.QApplication.clipboard()
                md = QtCore.QMimeData()
                md.setUrls([PurePath(file_path[0]).as_uri()])
                cb.setMimeData(md)
            else:
                oma.MGlobal.displayError('�ʲ�{}û��rig�ļ�'.format(sel_item.data(QtCore.Qt.UserRole + 2)))
        elif inf == 'copyModFile':
            path = path.replace('Rig', 'Mod')
            mod_path = glob.glob(os.path.join(path, '*.ma'))
            if mod_path and os.path.exists(mod_path[0]):
                cb = QtWidgets.QApplication.clipboard()
                md = QtCore.QMimeData()
                md.setUrls([PurePath(mod_path[0]).as_uri()])
                cb.setMimeData(md)
            else:
                oma.MGlobal.displayError('�ʲ�{}û��mod�ļ�'.format(sel_item.data(QtCore.Qt.UserRole + 2)))
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
                fp('�ʲ�{}û��ģ���ļ���'.format(sel_item.data(QtCore.Qt.UserRole + 2)), warning=True)

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
            asset_path = sel_items[0].data(QtCore.Qt.UserRole)  #ѡ����ʲ�����·��

            if not os.path.exists(file_path):  #�����ʲ���rig�ļ��л�û����ʱ
                fp('���ڴ���{}��rig�ļ��С�����������'.format(sel_items[0].data(QtCore.Qt.UserRole + 2)), info=True)
                rig_path = os.path.dirname(os.path.abspath(file_path))
                os.mkdir(rig_path)
                os.mkdir(file_path)
                os.mkdir(file_path.replace('Final', 'Unreal'))

            self.iterate_file(sel_items[0])  #����ʷ�ļ����е����ļ�
            if os.path.normcase(os.path.abspath(asset_path)) == os.path.normcase(os.path.abspath(scence_path)):
                # ���򿪵��ļ����ڷ�����·����ʱ
                self.but_push_rig.setText(u'���ڱ��泡��������������')
                fp('���ڱ��泡��������������', info=True, viewMes=True)
                mc.file(s=True, f=True, op='v=0')
                self.but_push_rig.setText(u'�����ϴ��ɹ�����')
                fp('�����ϴ��ɹ�', info=True, viewMes=True)
            else:
                self.push_file(sel_items[0])  #�ϴ��ļ�
        else:
            fp('û��ѡ����Ҫ�ύ���ʲ���', error=True, viewMes=True)

    def iterate_file(self, item):
        """
        ��������
        :param item:��ѡ�е���
        :return:
        """
        file_path = item.data(QtCore.Qt.UserRole)  #�������ļ�����·��
        file_nam = '_'.join(
            [self.project_name, item.data(QtCore.Qt.UserRole + 1), item.data(QtCore.Qt.UserRole + 2), 'Rig.ma'])  #�ļ���
        fileNam_path = '/'.join([file_path, file_nam])  #�������ļ�����·��
        fileHistory_path = '/'.join([file_path, 'history'])  #��������ʷ�ļ���·��
        if os.path.exists(fileNam_path):
            if not os.path.exists(fileHistory_path):
                self.but_push_rig.setText(u'���ڴ�����ʷ�ļ��С�����������')
                fp('���ڴ�����ʷ�ļ��С�����������', info=True)
                os.mkdir(fileHistory_path)

            newHty_nam = self.get_history_id(fileHistory_path, file_nam)
            if not fileHistory_path:
                newHty_nam = file_nam.split('.')[0] + '_v01.ma'

            try:
                self.but_push_rig.setText(u'��������ʷ�ļ����ڸ����ļ�������������')
                fp('��������ʷ�ļ����ڸ����ļ�������������', info=True)
                shutil.copy(fileNam_path, '/'.join([fileHistory_path, newHty_nam]))

            except Exception as e:
                fp(
                    '{}���Ƶ�{}��ʷ�ļ��г���:{}'.format(fileNam_path, '/'.join([fileHistory_path, newHty_nam]), e),
                    error=True, viewMes=True)
        else:
            fp('�ļ���δ�ϴ���һ��', info=True)

    def push_file(self, item):
        """
        ����ǰ�ļ��ϴ����������ļ�·����
        :param item:
        :return:
        """
        file_nam = '_'.join(
            [self.project_name, item.data(QtCore.Qt.UserRole + 1), item.data(QtCore.Qt.UserRole + 2), 'Rig.ma'])  #�ļ���
        file_path = item.data(QtCore.Qt.UserRole)  #�������ļ�����·��

        self.but_push_rig.setText(u'���ڱ��泡��������������')
        fp('���ڱ��泡��������������', info=True, viewMes=True)
        mc.file(s=True, f=True, op='v=0')
        self.but_push_rig.setText(u'�����ϴ�����������������')
        fp('�����ϴ�����������������', info=True, viewMes=True)
        shutil.copy(mc.file(exn=True, q=True), '/'.join([file_path, file_nam]))
        self.but_push_rig.setText(u'�����ϴ��ɹ�����')
        fp('�����ϴ��ɹ�', info=True, viewMes=True)

    @staticmethod
    def get_history_id(path, nam):
        """
        ͨ����������ʷ�ļ���·����ȡ���ʲ�Ӧ�ò�������һ�������ļ���
        :param nam: ���ʲ���rig������
        :param path:��ʷ�ļ���
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
        ����ǰѡ�ж��󵼳�Ϊfbx���ϴ���ָ���ʲ�sk�ļ�����
        :return:
        """
        sel_items = self.lst_asset.selectedItems()
        if not sel_items:
            fp('û��ѡ����Ч�', error=True, viewMes=True)

        folder_path = sel_items[0].data(QtCore.Qt.UserRole + 3)  #fbx�ļ��з�����·��
        file_absPath = exportSelectToFbx()  #fbx������ļ�·��
        file_name = 'SK_{}.fbx'.format(sel_items[0].data(QtCore.Qt.UserRole + 2))  #fbx�ļ���
        file_path = os.sep.join([folder_path, file_name])  #fbx�������ļ�·��
        if os.path.normcase(os.path.abspath(file_absPath)) == os.path.normcase(os.path.abspath(file_path)):
            fp('�����ļ����Ƿ�����fbx�ļ�·����ַ��', info=True)
        else:  #������λ���������fbx�ļ�λ�ò����ʱ
            if not os.path.exists(folder_path):  #������fbx�ļ���·��������ʱ
                os.mkdir(folder_path)
            if os.path.exists(file_path):  #������fbx�ļ�����ʱ
                fp('��������ʷ�ļ����ڱ����ļ���', info=True)
                fileUtils.version_up(folder_path, file_name)  #������ʷ�ļ�
                fp('��ʷ�ļ�����ɹ���', info=True)
            try:
                fp('��������������ύfbx�ļ���', info=True)
                shutil.copyfile(file_absPath, file_path)
                fp('fbx�ļ��ύ�ɹ���', info=True)
                self.but_push_fbx.setText(u'fbx�ļ��ύ�ɹ�')
            except Exception as e:
                self.but_push_fbx.setText(u'fbx�ļ��ύʧ��')
                fp('fbx�ļ��ύʧ�ܡ�{}'.format(e), error=True, viewMes=True)


def push_rig():
    try:
        pushScence_window.close()
        pushScence_window.deleteLater()
    except:
        pass
    finally:
        pushScence_window = pushWindow()
        pushScence_window.show()
