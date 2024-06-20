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
    default_path = cf.get_value('folder_widget_data', 'default_path', 'str')#Ĭ���ϲ�·��
    sub_index = cf.get_value('folder_widget_data', 'sub_index', 'int')#Ĭ���ϲ�·����Ҫ��ʾ�����ļ����±�

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
        self.create_shortcut()

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
            ������ݼ���ݷ�ʽ��
        """
        QtWidgets.QShortcut(QtGui.QKeySequence("F2"), self, self.rename_item)
        QtWidgets.QShortcut(QtGui.QKeySequence("delete"), self, self.delete_file)

    def refresh_dir(self):
        """
        ˢ��Ŀ¼�б���������ѡ�������Ÿ����ļ��б�
        """
        drive_ltter = self.lin_dir.text()
        if not os.path.exists(drive_ltter) or not os.path.isdir(drive_ltter):
            fp(u'·��{}�����ڣ�'.format(drive_ltter), warning=True)
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
        cf.set_value('folder_widget_data', 'sub_index', str(self.cob_file.currentIndex()))

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
            if os.path.isfile(path) and os.path.splitext(path)[-1] in ['.ma', '.mb', '.fbx', '.obj']:
                men_import_file = menu.addAction(u'�����ļ�')
                men_import_file.triggered.connect(self.import_file)
                menu.addAction(menl(p=menu))
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
            itm_dir = {itm: itm.data(0, QtCore.Qt.UserRole) for itm in self.tree.selectedItems() if
                       os.path.exists(itm.data(0, QtCore.Qt.UserRole))}#����item����
            if itm_dir:
                return func(self, itm_dir)
            else:
                return None

        return wrapper

    def delete_item(self, item):
        """
        �����ṹ��ɾ�������
        Args:
            item: Ҫɾ�����
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
        ɾ����ǰ��
        """
        bol = QtWidgets.QMessageBox.warning(self, u'����', u'�Ƿ�ɾ��\n{}'.format('\n'.join(itm_dir.values())),
                                            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if bol == QtWidgets.QMessageBox.No:
            return None
        list(map(fu.delete_files, list(itm_dir.values())))
        list(map(self.delete_item, list(itm_dir.keys())))

    @obj_existence
    def duplicate_path(self, itm_dir):
        """
        ����·��
        """
        path = [p for p in itm_dir.values()][0]
        QtWidgets.QApplication.clipboard().setText(path)
        fp('�Ѹ���·����{}'.format(path), info=True)

    @obj_existence
    def duplicate_file_name(self, itm_dir):
        """
        �����ļ���
        """
        path = [p for p in itm_dir.values()][0]
        QtWidgets.QApplication.clipboard().setText(os.path.basename(path))
        fp('�Ѹ����ļ�����{}'.format(os.path.basename(path).encode('gbk')), info=True)

    @obj_existence
    def duplicate_file(self, itm_dir):
        """
        �����ļ�
        """
        path = [p for p in itm_dir.values()][0]
        md = QtCore.QMimeData()
        md.setUrls([QtCore.QUrl.fromLocalFile(path)])
        QtWidgets.QApplication.clipboard().setMimeData(md)
        fp('�Ѹ����ļ���{}'.format(path.encode('gbk')), info=True)

    def paste_file(self):
        """
        ճ���ļ�
        """
        itms = self.tree.selectedItems()
        path = itms[-1].data(0, QtCore.Qt.UserRole) if itms else os.path.join(self.lin_dir.text(),
                                                                              self.cob_file.currentText())#�����Ƶ����ļ���
        md = QtWidgets.QApplication.clipboard().mimeData()
        if itms:#��ȡҪ��������ĸ�����
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

                tag_path = os.path.join(path, os.path.basename(url.toLocalFile()))#�����Ƴɵ��ļ�·��
                if os.path.normcase(os.path.abspath(url.toLocalFile())) == os.path.normcase(os.path.abspath(tag_path)):
                    fp('���Ƶ��ļ���Ŀ���ļ���ͬһĿ¼��{}'.format(url.toLocalFile().encode('gbk')), warning=True)
                    continue

                if os.path.exists(tag_path):
                    rest = mc.confirmDialog(title=u'����', message=u'{}�������ļ�\n{}\n�Ƿ��滻?'.format(
                        path, os.path.basename(url.toLocalFile())), button=[u'�滻', u'���Ϊ', u'ȡ��'])
                    if rest == u'�滻':
                        list(map(fu.delete_files, [tag_path]))
                        itm = self.query_item(tag_path)
                        self.delete_item(itm)
                    elif rest == u'���Ϊ':
                        i = 1
                        suffix = ''
                        p, typ = os.path.splitext(tag_path)
                        while os.path.exists(p+suffix+typ):
                            i += 1
                            suffix = '({})'.format(i)
                        tag_path = p+suffix+typ
                    elif rest == u'ȡ��':
                        continue

                shutil.copy(url.toLocalFile(), tag_path)
                fp('��ճ���ļ�{}��{}'.format(os.path.basename(url.toLocalFile()).encode('gbk'), tag_path.encode('gbk')), info=True)
                self.create_sub_item(p_itm, tag_path)

    @obj_existence
    def rename_item(self, itm_dir):
        """
        ��������ǰ��
        """
        itm = [p for p in itm_dir.keys()][0]
        path = itm_dir[itm]
        base_name = os.path.basename(path)
        name, suffix = os.path.splitext(base_name)
        new_name = QtWidgets.QInputDialog.getText(self, u'����������', u'��{}\n������Ϊ:'.format(base_name),
                                                  text=name)
        if new_name[1]:
            new_path = os.path.join(os.path.dirname(path), '{}{}'.format(new_name[0], suffix))
            os.rename(path, new_path)
            itm.setText(0, new_name[0]+suffix)
            itm.setData(0, QtCore.Qt.UserRole, new_path)
            fp('��������Ϊ��{}'.format(new_path.encode('gbk')), info=True)
        else:
            fp('��ȡ��������', info=True)

    def new_folder(self):
        """
        �½��ļ���
        """
        itms = self.tree.selectedItems()

        path = itms[-1].data(0, QtCore.Qt.UserRole) if itms else os.path.join(self.lin_dir.text(),
                                                                              self.cob_file.currentText())
        if itms:#��ȡҪ��������ĸ�����
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

        new_name = QtWidgets.QInputDialog.getText(self, u'�½��ļ��д���', u'��{}\n���½��ļ���:'.format(path), text=u'�½��ļ���')
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
            fp('���½��ļ��У�{}{}'.format(new_path.encode('gbk'), suffix), info=True)

    @obj_existence
    def open_file(self, itm_dir):
        """
        ������ͼ�д򿪵�ǰ���·��
        """
        path = ''
        for itm in itm_dir.values():
            path = itm
        if os.path.isfile(path) and os.path.splitext(path)[-1] in ['.ma', '.mb']:
            if mc.file(mf=True, q=True):
                rest = mc.confirmDialog(title='����', message='��ǰ�����ѱ����ģ��Ƿ񱣴��򿪣�',
                                        button=['����', '������', '���Ϊ', 'ȡ��'])
                if rest == u'����':
                    mc.file(s=True)
                elif rest == u'���Ϊ':
                    mm.eval('SaveSceneAs;')
                elif rest == u'ȡ��':
                    return None
            mc.file(path, o=True, f=True)

    @obj_existence
    def open_folder(self, itm_dir):
        """
       �򿪰���ָ������ļ��С�

       Args:
           itm_dir(dir)����Ŀ�б����һ����Ҫ���ļ��е���Ŀ��
       """
        os.system('explorer /select, {}'.format([p for p in itm_dir.values()][0].replace('/', '\\')))

    @obj_existence
    def import_file(self, itm_dir):
        """
        ����ѡ�е��ļ���
        Args:
            itm_dir(dir)����Ŀ�б����һ����Ҫ���ļ��е���Ŀ��
        """
        path = [p for p in itm_dir.values()][0]
        if os.path.isfile(path) and os.path.splitext(path)[-1] in ['.ma', '.mb', '.fbx', '.obj']:
            mc.file(path, i=True, f=True)
        else:
            fp('ѡ�ж������ļ����׺����ma��mb��fbx��obj', error=True)


if __name__ == '__main__':
    try:
        my_folder_window.close()
        my_folder_window.deleteLater()
    except:
        pass
    finally:
        my_folder_window = FolderWidget()
        my_folder_window.show()

