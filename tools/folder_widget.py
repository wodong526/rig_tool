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
        列出给定路径下所有非隐藏的文件夹。
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
        在指定路径处获取文件的修改日期。
        Args:
        file_path：将检索其修改日期的文件的路径。
        Returns:文件的修改日期。
        """
        modified_time = os.path.getmtime(path)
        modified_datetime = datetime.fromtimestamp(modified_time)
        return modified_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def __init__(self, parent=maya_main_window()):
        super(FolderWidget, self).__init__(parent)
        self.setWindowTitle(u'这是窗口')
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
        self.tree.setHeaderLabels([u'文件', u'修改日期'])
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
        刷新目录列表，并根据所选驱动器号更新文件列表。
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
        遍历树中的所有项，找到满足条件的第一个项，并滚动到该项。
        :param itm_parent:
        :param itm_body:
        :param tree: QTreeWidget实例。
        :param condition_func: 一个函数，接受一个QTreeWidgetItem作为参数，返回一个布尔值。
        """
        def traverse(item, tag):
            # 检查当前项是否满足条件
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
        清除树并为给定路径创建子项。
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
        在指定路径上为给定项创建子项。
        Args:
        item: 子项将添加到的父项。
        path: 将为其创建子项的路径。

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
        创建菜单
        """
        menu = QtWidgets.QMenu()
        itm = self.tree.currentItem()
        if itm:
            path = itm.data(0, QtCore.Qt.UserRole)
            men_paste_file = menu.addAction(u'粘贴文件')
            men_dup_file = menu.addAction(u'复制文件夹' if os.path.isdir(path) else u'复制文件')
            men_dup_file_name = menu.addAction(u'复制文件夹名称' if os.path.isdir(path) else u'复制文件名称')
            men_dup_path = menu.addAction(u'复制路径')
            menu.addAction(menl(p=menu))
            men_openexplorer = menu.addAction(u'打开文件夹' if os.path.isdir(path) else u'打开文件所在的文件夹')
            men_newfolder = menu.addAction(u'新建文件夹')
            menu.addAction(menl(p=menu))
            men_rename = menu.addAction(u'重命名')
            menu.addAction(menl(p=menu))
            men_del = menu.addAction(u'删除')

            men_openexplorer.triggered.connect(self.open_folder)
            men_dup_path.triggered.connect(self.duplicate_path)
            men_dup_file_name.triggered.connect(self.duplicate_file_name)
            men_dup_file.triggered.connect(self.duplicate_file)
            men_rename.triggered.connect(self.rename_item)
            men_del.triggered.connect(self.delete_file)
        else:
            men_paste_file = menu.addAction(u'粘贴文件')
            men_newfolder = menu.addAction(u'新建文件夹')

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
        删除当前项
        """
        bol = QtWidgets.QMessageBox.warning(self, u'警告', u'是否删除\n{}'.format('\n'.join(itms)),
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
        复制路径
        """
        QtWidgets.QApplication.clipboard().setText(itms[-1])

    @obj_existence
    def duplicate_file_name(self, itms):
        """
        复制文件名
        """
        QtWidgets.QApplication.clipboard().setText(os.path.basename(itms[-1]))

    @obj_existence
    def duplicate_file(self, itms):
        """
        复制文件
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
        粘贴文件
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
        重命名当前项
        """
        path = itms[-1]
        base_name = os.path.basename(path)
        new_name = QtWidgets.QInputDialog.getText(self, u'重命名窗口', u'将{}\n重命名为:'.format(base_name),
                                                  text=os.path.splitext(base_name)[0])
        if new_name[1]:
            new_path = os.path.join(os.path.dirname(path), new_name[0])
            os.rename(path, new_path)
            self.refresh_item()
        else:
            print('取消重命名')

    def new_folder(self):
        """
        新建文件夹
        """
        itms = self.tree.selectedItems()
        path = os.path.dirname(itms[-1].data(0, QtCore.Qt.UserRole)) if itms else os.path.join(self.lin_dir.text(),
                                                                              self.cob_file.currentText())
        new_name = QtWidgets.QInputDialog.getText(self, u'新建文件夹窗口', u'在{}\n下新建文件夹:'.format(path), text=u'新建文件夹')
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
        在树视图中打开当前项的路径
        """
        path = itms[-1]
        if os.path.isfile(path) and os.path.splitext(path)[-1] in ['.ma', '.mb']:
            if mc.file(mf=True, q=True):
                rest = mc.confirmDialog(title='警告', message='当前场景已被更改，是否保存后打开？',
                                        button=['保存', '不保存', '另存为', '取消'])
                if rest == u'保存':
                    mc.file(s=True)
                elif rest == u'取消':
                    mm.eval('SaveSceneAs;')
                elif rest == u'取消':
                    return None
                mc.file(itms[-1], o=True, f=True)

    @obj_existence
    def open_folder(self, itms):
        """
       打开包含指定项的文件夹。

       Args:
           itms(list)：项目列表，最后一项是要打开文件夹的项目。
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

