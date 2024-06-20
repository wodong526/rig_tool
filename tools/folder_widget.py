# coding=gbk
import stat
import shutil
import os
import sys
import subprocess
from datetime import datetime
from PySide2 import QtWidgets, QtGui, QtCore
from shiboken2 import wrapInstance
if sys.version_info.major == 3:
    from importlib import reload

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui

from feedback_tool import Feedback_info as fp
from data_path import icon_dir as ic
from qt_widgets import SeparatorAction as menl
from dutils import fileUtils as fu
from userConfig import Conf
reload(fu)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

cf = Conf()
class FolderWidget(QtWidgets.QWidget):
    default_path = cf.get_value('folder_widget_data', 'default_path', 'str')#默认上层路径
    sub_index = cf.get_value('folder_widget_data', 'sub_index', 'int')#默认上层路径下要显示的子文件夹下标

    @classmethod
    def is_hidden(cls, filepath):
        if isinstance(filepath, str):
            filepath = filepath.encode('utf-8')
        try:
            output = subprocess.check_output(['attrib', filepath.decode('utf-8')], shell=True)
            return b' SH ' in output
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
        self.create_shortcut()

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
        path_layout.setSpacing(5)
        path_layout.addWidget(self.lin_dir)
        path_layout.addWidget(self.cob_file)
        path_layout.addWidget(self.but_refresh)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addLayout(path_layout)
        main_layout.addWidget(self.tree)

    def create_connect(self):
        self.lin_dir.returnPressed.connect(self.refresh_dir)
        self.cob_file.currentIndexChanged.connect(self.refresh_item)
        self.but_refresh.clicked.connect(self.refresh_item)
        self.tree.itemDoubleClicked.connect(self.open_file)
        self.tree.customContextMenuRequested.connect(self.create_menu)

    def create_shortcut(self):
        """
            创建快捷键快捷方式。
        """
        QtWidgets.QShortcut(QtGui.QKeySequence("F2"), self, self.rename_item)
        QtWidgets.QShortcut(QtGui.QKeySequence("delete"), self, self.delete_file)

    def refresh_dir(self):
        """
        刷新目录列表，并根据所选驱动器号更新文件列表。
        """
        drive_ltter = self.lin_dir.text()
        if not os.path.exists(drive_ltter) or not os.path.isdir(drive_ltter):
            fp(u'路径{}不存在！'.format(drive_ltter), warning=True)
            return None
        self.cob_file.clear()
        for obj in self.list_folder(drive_ltter, no_hidden=True):
            if os.path.isdir(os.path.join(drive_ltter, obj)):
                self.cob_file.addItem(obj)
        try:
            self.cob_file.setCurrentIndex(FolderWidget.sub_index)
        except:
            self.cob_file.setCurrentIndex(self.cob_file.count() - 1)
        self.refresh_item()

        cf.set_value('folder_widget_data', 'default_path', str(drive_ltter))

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
        cf.set_value('folder_widget_data', 'sub_index', str(self.cob_file.currentIndex()))

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
            if os.path.isfile(path) and os.path.splitext(path)[-1] in ['.ma', '.mb', '.fbx', '.obj']:
                men_import_file = menu.addAction(u'导入文件')
                men_import_file.triggered.connect(self.import_file)
                menu.addAction(menl(p=menu))
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
            itm_dir = {itm: itm.data(0, QtCore.Qt.UserRole) for itm in self.tree.selectedItems() if
                       os.path.exists(itm.data(0, QtCore.Qt.UserRole))}#返回item本身
            if itm_dir:
                return func(self, itm_dir)
            else:
                return None

        return wrapper

    def delete_item(self, item):
        """
        从树结构中删除给定项。
        Args:
            item: 要删除的项。
        """
        if item.parent():
            parent_item = item.parent()
            parent_item.removeChild(item)
        else:
            index = self.tree.indexOfTopLevelItem(item)
            self.tree.takeTopLevelItem(index)

    def query_item(self, target_data):
        for i in range(self.tree.topLevelItemCount()):
            top_level_item = self.tree.topLevelItem(i)
            if top_level_item is not None:
                ret = self.check_item(top_level_item, target_data)
                if ret is not None:
                    return ret

    def check_item(self, item, target_data):
        if item.data(0, QtCore.Qt.UserRole) == target_data:
            return item

        for j in range(item.childCount()):
            child_item = item.child(j)
            ret = self.check_item(child_item, target_data)
            if ret is not None:
                return ret

    @obj_existence
    def delete_file(self, itm_dir):
        """
        删除当前项
        """
        bol = QtWidgets.QMessageBox.warning(self, u'警告', u'是否删除\n{}'.format('\n'.join(itm_dir.values())),
                                            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if bol == QtWidgets.QMessageBox.No:
            return None
        list(map(fu.delete_files, list(itm_dir.values())))
        list(map(self.delete_item, list(itm_dir.keys())))

    @obj_existence
    def duplicate_path(self, itm_dir):
        """
        复制路径
        """
        path = [p for p in itm_dir.values()][0]
        QtWidgets.QApplication.clipboard().setText(path)
        fp('已复制路径：{}'.format(path), info=True)

    @obj_existence
    def duplicate_file_name(self, itm_dir):
        """
        复制文件名
        """
        path = [p for p in itm_dir.values()][0]
        QtWidgets.QApplication.clipboard().setText(os.path.basename(path))
        fp('已复制文件名：{}'.format(os.path.basename(path).encode('gbk')), info=True)

    @obj_existence
    def duplicate_file(self, itm_dir):
        """
        复制文件
        """
        path = [p for p in itm_dir.values()][0]
        md = QtCore.QMimeData()
        md.setUrls([QtCore.QUrl.fromLocalFile(path)])
        QtWidgets.QApplication.clipboard().setMimeData(md)
        fp('已复制文件：{}'.format(path.encode('gbk')), info=True)

    def paste_file(self):
        """
        粘贴文件
        """
        itms = self.tree.selectedItems()
        path = itms[-1].data(0, QtCore.Qt.UserRole) if itms else os.path.join(self.lin_dir.text(),
                                                                              self.cob_file.currentText())#被复制到的文件夹
        md = QtWidgets.QApplication.clipboard().mimeData()
        if itms:#获取要创建新项的父级项
            if os.path.isdir(path):
                p_itm = itms[-1]
            elif itms[-1].parent():
                p_itm = itms[-1].parent()
            else:
                p_itm = self.tree.invisibleRootItem()
        else:
            p_itm = self.tree.invisibleRootItem()

        if md.hasUrls():
            for url in md.urls():
                if os.path.isfile(path):
                    path = os.path.dirname(path)

                tag_path = os.path.join(path, os.path.basename(url.toLocalFile()))#被复制成的文件路径
                if os.path.normcase(os.path.abspath(url.toLocalFile())) == os.path.normcase(os.path.abspath(tag_path)):
                    fp('复制的文件与目标文件在同一目录：{}'.format(url.toLocalFile().encode('gbk')), warning=True)
                    continue

                if os.path.exists(tag_path):
                    rest = mc.confirmDialog(title=u'警告', message=u'{}下已有文件\n{}\n是否替换?'.format(
                        path, os.path.basename(url.toLocalFile())), button=[u'替换', u'另存为', u'取消'])
                    if rest == u'替换':
                        list(map(fu.delete_files, [tag_path]))
                        itm = self.query_item(tag_path)
                        self.delete_item(itm)
                    elif rest == u'另存为':
                        i = 1
                        suffix = ''
                        p, typ = os.path.splitext(tag_path)
                        while os.path.exists(p+suffix+typ):
                            i += 1
                            suffix = '({})'.format(i)
                        tag_path = p+suffix+typ
                    elif rest == u'取消':
                        continue

                shutil.copy(url.toLocalFile(), tag_path)
                fp('已粘贴文件{}到{}'.format(os.path.basename(url.toLocalFile()).encode('gbk'), tag_path.encode('gbk')), info=True)
                self.create_sub_item(p_itm, tag_path)

    @obj_existence
    def rename_item(self, itm_dir):
        """
        重命名当前项
        """
        itm = [p for p in itm_dir.keys()][0]
        path = itm_dir[itm]
        base_name = os.path.basename(path)
        name, suffix = os.path.splitext(base_name)
        new_name = QtWidgets.QInputDialog.getText(self, u'重命名窗口', u'将{}\n重命名为:'.format(base_name),
                                                  text=name)
        if new_name[1]:
            new_path = os.path.join(os.path.dirname(path), '{}{}'.format(new_name[0], suffix))
            os.rename(path, new_path)
            itm.setText(0, new_name[0]+suffix)
            itm.setData(0, QtCore.Qt.UserRole, new_path)
            fp('已重命名为：{}'.format(new_path.encode('gbk')), info=True)
        else:
            fp('已取消重命名', info=True)

    def new_folder(self):
        """
        新建文件夹
        """
        itms = self.tree.selectedItems()

        path = itms[-1].data(0, QtCore.Qt.UserRole) if itms else os.path.join(self.lin_dir.text(),
                                                                              self.cob_file.currentText())
        if itms:#获取要创建新项的父级项
            if os.path.isfile(path):
                p = itms[-1].parent()
                path = os.path.dirname(path)
            elif itms[-1].parent():
                p = itms[-1]
            else:
                path = os.path.dirname(path)
                p = self.tree.invisibleRootItem()
        elif not itms:
            p = self.tree.invisibleRootItem()

        new_name = QtWidgets.QInputDialog.getText(self, u'新建文件夹窗口', u'在{}\n下新建文件夹:'.format(path), text=u'新建文件夹')
        if new_name[1]:
            new_path = os.path.join(path, new_name[0])
            i = 1
            suffix = ''
            while os.path.exists(new_path + suffix):
                suffix = '({})'.format(i)
                i += 1
            os.mkdir(new_path + suffix)
            os.chmod(new_path + suffix, stat.S_IWRITE)
            self.create_sub_item(p, new_path + suffix)
            fp('已新建文件夹：{}{}'.format(new_path.encode('gbk'), suffix), info=True)

    @obj_existence
    def open_file(self, itm_dir):
        """
        在树视图中打开当前项的路径
        """
        path = ''
        for itm in itm_dir.values():
            path = itm
        if os.path.isfile(path) and os.path.splitext(path)[-1] in ['.ma', '.mb']:
            if mc.file(mf=True, q=True):
                rest = mc.confirmDialog(title='警告', message='当前场景已被更改，是否保存后打开？',
                                        button=['保存', '不保存', '另存为', '取消'])
                if rest == u'保存':
                    mc.file(s=True)
                elif rest == u'另存为':
                    mm.eval('SaveSceneAs;')
                elif rest == u'取消':
                    return None
            mc.file(path, o=True, f=True)

    @obj_existence
    def open_folder(self, itm_dir):
        """
       打开包含指定项的文件夹。

       Args:
           itm_dir(dir)：项目列表，最后一项是要打开文件夹的项目。
       """
        os.system('explorer /select, {}'.format([p for p in itm_dir.values()][0].replace('/', '\\')))

    @obj_existence
    def import_file(self, itm_dir):
        """
        导入选中的文件。
        Args:
            itm_dir(dir)：项目列表，最后一项是要打开文件夹的项目。
        """
        path = [p for p in itm_dir.values()][0]
        if os.path.isfile(path) and os.path.splitext(path)[-1] in ['.ma', '.mb', '.fbx', '.obj']:
            mc.file(path, i=True, f=True)
        else:
            fp('选中对象不是文件或后缀不是ma，mb，fbx，obj', error=True)


if __name__ == '__main__':
    try:
        my_folder_window.close()
        my_folder_window.deleteLater()
    except:
        pass
    finally:
        my_folder_window = FolderWidget()
        my_folder_window.show()

