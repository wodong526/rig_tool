# coding=gbk
import shutil
import os
import subprocess
from datetime import datetime
from PySide2 import QtWidgets, QtGui, QtCore
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui

from data_path import icon_dir as ic
from qt_widgets import SeparatorAction as menl
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class FolderWidget(QtWidgets.QWidget):
    default_path = 'E:/'

    @classmethod
    def is_hidden(cls, filepath):
        if isinstance(filepath, unicode):
            filepath = filepath.encode('mbcs')
        try:
            output = subprocess.check_output(['attrib', filepath], shell=True)
            return ' SH ' in output
        except subprocess.CalledProcessError:
            return False
    @classmethod
    def list_folder(cls, path, no_hidden=False):
        """
        �г�����·�������з����ص��ļ��С�
        """
        lis_file = []
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if no_hidden:
                lis_file.append(entry) if not cls.is_hidden(full_path) else None
            else:
                lis_file.append(entry)

        return lis_file

    @classmethod
    def get_file_modification_date(self, path):
        """
        ��ָ��·������ȡ�ļ����޸����ڡ�
        Args:
        file_path�����������޸����ڵ��ļ���·����
        Returns:�ļ����޸����ڡ�
        """
        modified_time = os.path.getmtime(path)
        modified_datetime = datetime.fromtimestamp(modified_time)
        return modified_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def __init__(self, parent=maya_main_window()):
        super(FolderWidget, self).__init__(parent)
        self.setWindowTitle(u'���Ǵ���')
        self.setMinimumWidth(450)
        self.iconProvider = QtWidgets.QFileIconProvider()

        self.create_widget()
        self.create_layout()
        self.create_connect()

    def create_widget(self):
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setColumnWidth(0, 300)
        self.tree.setColumnWidth(1, 100)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tree.setHeaderLabels([u'�ļ�', u'�޸�����'])
        self.tree.header().setStyleSheet('QHeaderView::section{background:skyblue;border: 1px solid #d8d8d8;'
                                         'text-align: center;}')

        self.lin_dir = QtWidgets.QLineEdit(self.default_path)
        self.lin_dir.setMinimumHeight(26)
        self.cob_file = QtWidgets.QComboBox()
        self.cob_file.setMinimumHeight(26)
        self.but_refresh = QtWidgets.QPushButton()
        self.but_refresh.setIcon(QtGui.QIcon(ic['refresh']))
        self.refresh_dir()

    def create_layout(self):
        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(self.lin_dir)
        path_layout.addWidget(self.cob_file)
        path_layout.addWidget(self.but_refresh)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(path_layout)
        main_layout.addWidget(self.tree)

    def create_connect(self):
        self.lin_dir.returnPressed.connect(self.refresh_dir)
        self.cob_file.currentIndexChanged.connect(self.refresh_item)
        self.but_refresh.clicked.connect(self.refresh_item)
        self.tree.itemDoubleClicked.connect(self.open_file)
        self.tree.customContextMenuRequested.connect(self.create_menu)

    def refresh_dir(self):
        """
        ˢ��Ŀ¼�б���������ѡ�������Ÿ����ļ��б�
        """
        drive_ltter = self.lin_dir.text()
        if not os.path.exists(drive_ltter):
            return None
        self.cob_file.clear()
        for obj in self.list_folder(drive_ltter, no_hidden=True):
            if os.path.isdir(os.path.join(drive_ltter, obj)):
                self.cob_file.addItem(obj)
        self.cob_file.setCurrentIndex(self.cob_file.count() - 1)
        self.refresh_item()

    def find_and_scroll_to_item(self, tree, itm_body, itm_parent):
        """
        �������е�������ҵ����������ĵ�һ��������������
        :param itm_parent:
        :param itm_body:
        :param tree: QTreeWidgetʵ����
        :param condition_func: һ������������һ��QTreeWidgetItem��Ϊ����������һ������ֵ��
        """
        def traverse(item, tag):
            # ��鵱ǰ���Ƿ���������
            if item.data(0, QtCore.Qt.UserRole) == tag:
                return item

            for i in range(item.childCount()):
                result = traverse(item.child(i), tag)
                if result:
                    return result
            return None
        #print(itm_body, itm_parent)
        for i in range(tree.topLevelItemCount()):

            for itm in [itm_parent, itm_body]:
                if not itm:
                    continue
                new_itm = traverse(tree.topLevelItem(i), itm)
                if new_itm:
                    tree.setCurrentItem(new_itm)
                    if os.path.isdir(new_itm.data(0, QtCore.Qt.UserRole)):
                        tree.expandItem(new_itm)
                    tree.scrollToItem(new_itm, QtWidgets.QTreeWidget.PositionAtCenter)
        return None

    def refresh_item(self):
        """
        �������Ϊ����·���������
        Args:
        Returns:None
        """
        itm_body = None
        itm_parent = None
        if self.tree.currentItem():
            try:
                itm_body = self.tree.currentItem().data(0, QtCore.Qt.UserRole)
                itm_parent = self.tree.currentItem().parent().data(0, QtCore.Qt.UserRole)
            except:
                pass
        self.tree.clear()
        drive_ltter = self.lin_dir.text()
        path = os.path.join(drive_ltter, self.cob_file.currentText())
        if not os.path.exists(path):
            return None

        for sub_path in self.list_folder(path):
            self.create_sub_item(self.tree.invisibleRootItem(), os.path.join(path, sub_path))

        if itm_body or itm_parent:
            self.find_and_scroll_to_item(self.tree, itm_body, itm_parent)

    def create_sub_item(self, item, path):
        """
        ��ָ��·����Ϊ����������
        Args:
        item: �����ӵ��ĸ��
        path: ��Ϊ�䴴�������·����

        Returns:None
        """
        title = os.path.basename(path)
        if title == '.mayaSwatches': return None
        root = QtWidgets.QTreeWidgetItem(item)

        root.setData(0, QtCore.Qt.UserRole, path)
        root.setText(0, title)
        icon = self.iconProvider.icon(QtCore.QFileInfo(path))
        root.setIcon(0, icon)

        tim = self.get_file_modification_date(path)
        root.setText(1, str(tim))

        if not os.path.isdir(path): return None
        for obj in os.listdir(path):
            sub_path = os.path.join(path, obj)
            self.create_sub_item(root, sub_path)

    def create_menu(self, pos):
        """
        �����˵�
        """
        menu = QtWidgets.QMenu()
        itm = self.tree.currentItem()
        if itm:
            path = itm.data(0, QtCore.Qt.UserRole)
            men_paste_file = menu.addAction(u'ճ���ļ�')
            men_dup_file = menu.addAction(u'�����ļ���' if os.path.isdir(path) else u'�����ļ�')
            men_dup_file_name = menu.addAction(u'�����ļ�������' if os.path.isdir(path) else u'�����ļ�����')
            men_dup_path = menu.addAction(u'����·��')
            menu.addAction(menl(p=menu))
            men_openexplorer = menu.addAction(u'���ļ���' if os.path.isdir(path) else u'���ļ����ڵ��ļ���')
            men_newfolder = menu.addAction(u'�½��ļ���')
            menu.addAction(menl(p=menu))
            men_rename = menu.addAction(u'������')
            menu.addAction(menl(p=menu))
            men_del = menu.addAction(u'ɾ��')

            men_openexplorer.triggered.connect(self.open_folder)
            men_dup_path.triggered.connect(self.duplicate_path)
            men_dup_file_name.triggered.connect(self.duplicate_file_name)
            men_dup_file.triggered.connect(self.duplicate_file)
            men_rename.triggered.connect(self.rename_item)
            men_del.triggered.connect(self.delete_file)
        else:
            men_paste_file = menu.addAction(u'ճ���ļ�')
            men_newfolder = menu.addAction(u'�½��ļ���')

        men_paste_file.triggered.connect(self.paste_file)
        men_newfolder.triggered.connect(self.new_folder)

        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def obj_existence(func):
        def wrapper(self, *args, **kwargs):
            itm_lis = [itm.data(0, QtCore.Qt.UserRole) for itm in self.tree.selectedItems() if
                       os.path.exists(itm.data(0, QtCore.Qt.UserRole))]
            if itm_lis:
                return func(self, itm_lis)
            else:
                return None

        return wrapper

    @obj_existence
    def delete_file(self, itms):
        """
        ɾ����ǰ��
        """
        bol = QtWidgets.QMessageBox.warning(self, u'����', u'�Ƿ�ɾ��\n{}'.format('\n'.join(itms)),
                                            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if bol == QtWidgets.QMessageBox.No:
            return None
        for path in itms:
            if not os.path.exists(path):
                continue
            if os.path.isdir(path):
                os.rmdir(path)
            elif os.path.isfile(path):
                os.remove(path)
        self.refresh_item()

    @obj_existence
    def duplicate_path(self, itms):
        """
        ����·��
        """
        QtWidgets.QApplication.clipboard().setText(itms[-1])

    @obj_existence
    def duplicate_file_name(self, itms):
        """
        �����ļ���
        """
        QtWidgets.QApplication.clipboard().setText(os.path.basename(itms[-1]))

    @obj_existence
    def duplicate_file(self, itms):
        """
        �����ļ�
        """
        path = itms[-1]
        md = QtCore.QMimeData()
        if os.path.isfile(path):
            md.setUrls([QtCore.QUrl.fromLocalFile(path)])
        elif os.path.isdir(path):
            md.setUrls([QtCore.QUrl.fromLocalFile(path)])
        QtWidgets.QApplication.clipboard().setMimeData(md)

    def paste_file(self):
        """
        ճ���ļ�
        """
        itms = self.tree.selectedItems()
        path = itms[-1].data(0, QtCore.Qt.UserRole) if itms else os.path.join(self.lin_dir.text(),
                                                                              self.cob_file.currentText())
        md = QtWidgets.QApplication.clipboard().mimeData()
        if md.hasUrls():
            for url in md.urls():
                if os.path.isfile(path):
                    path = os.path.dirname(path)
                if os.path.isdir(url.toLocalFile()) or os.path.isfile(url.toLocalFile()):
                    shutil.copy(url.toLocalFile(), path)

            self.refresh_item()

    @obj_existence
    def rename_item(self, itms):
        """
        ��������ǰ��
        """
        path = itms[-1]
        base_name = os.path.basename(path)
        new_name = QtWidgets.QInputDialog.getText(self, u'����������', u'��{}\n������Ϊ:'.format(base_name),
                                                  text=os.path.splitext(base_name)[0])
        if new_name[1]:
            new_path = os.path.join(os.path.dirname(path), new_name[0])
            os.rename(path, new_path)
            self.refresh_item()
        else:
            print('ȡ��������')

    def new_folder(self):
        """
        �½��ļ���
        """
        itms = self.tree.selectedItems()
        path = os.path.dirname(itms[-1].data(0, QtCore.Qt.UserRole)) if itms else os.path.join(self.lin_dir.text(),
                                                                              self.cob_file.currentText())
        new_name = QtWidgets.QInputDialog.getText(self, u'�½��ļ��д���', u'��{}\n���½��ļ���:'.format(path), text=u'�½��ļ���')
        if new_name[1]:
            new_path = os.path.join(path, new_name[0])
            i = 1
            suffix = ''
            while os.path.exists(new_path + suffix):
                i += 1
                suffix = '({})'.format(i)
            os.mkdir(new_path + suffix)
            self.refresh_item()

    @obj_existence
    def open_file(self, itms):
        """
        ������ͼ�д򿪵�ǰ���·��
        """
        path = itms[-1]
        if os.path.isfile(path) and os.path.splitext(path)[-1] in ['.ma', '.mb']:
            if mc.file(mf=True, q=True):
                rest = mc.confirmDialog(title='����', message='��ǰ�����ѱ����ģ��Ƿ񱣴��򿪣�',
                                        button=['����', '������', '���Ϊ', 'ȡ��'])
                if rest == u'����':
                    mc.file(s=True)
                elif rest == u'ȡ��':
                    mm.eval('SaveSceneAs;')
                elif rest == u'ȡ��':
                    return None
                mc.file(itms[-1], o=True, f=True)

    @obj_existence
    def open_folder(self, itms):
        """
       �򿪰���ָ������ļ��С�

       Args:
           itms(list)����Ŀ�б����һ����Ҫ���ļ��е���Ŀ��
       """
        os.system('explorer /select, {}'.format(itms[-1].replace('/', '\\')))

def show_window():
    try:
        my_folder_window.close()
        my_folder_window.deleteLater()
    except:
        pass
    finally:
        my_folder_window = FolderWidget()
        my_folder_window.show()

