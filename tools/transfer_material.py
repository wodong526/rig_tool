# coding=gbk
#作者：woDong
#QQ: 1915367400
#Github: https://github.com/wodong526
#Bilibili: https://space.bilibili.com/381417672
#时间：2024/7/19, 上午10:38
#文件：replace_matrary

import os

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui

import qt_widgets as qw
from data_path import icon_dir as ic
from dutils import fileUtils as fu
from userConfig import Conf
from feedback_tool import Feedback_info as fp

cf = Conf()
_material_main_window = None

class Material:
    def __init__(self, mat_name, typ=None, color=None, trans=None, sg=None, objs=None, edit=True):
        # type: (str, str|None, list[float, float, float]|None, list[str]|None, str|None, list[str]|None, bool) -> None
        self._mat_name = mat_name
        if edit:
            self._mat_type = str()          # type: str
            self._mat_attr_color = []       # type: list[float, float, float]|{str: str}
            self._mat_attr_trans = []       # type: list
            self._mat_sg = str()            # type: str
            self._mat_objs = []             # type: list[str]

            self._get_mat_type()
            self._get_color()
            self._get_trans()
            self._get_sg()
            self._get_objs()
        else:
            self._mat_type = typ
            self._mat_attr_color = color
            self._mat_attr_trans = trans
            self._mat_sg = sg
            self._mat_objs = objs



    def _get_mat_type(self):
        self._mat_type = mc.nodeType(self._mat_name)

    def _get_color(self):
        # type: () -> None
        up_attr = mc.connectionInfo(self._mat_name + '.color', sfd=True)
        if up_attr and mc.nodeType(up_attr.split('.')[0]) == 'file':
            node = up_attr.split('.')[0]
            path = mc.getAttr('{}.fileTextureName'.format(node))
            self._mat_attr_color = {node: path}
        else:
            self._mat_attr_color = mc.getAttr('{}.color'.format(self._mat_name))[0]

    def _get_trans(self):
        # type: () -> None
        self._mat_attr_trans = mc.getAttr('{}.transparency'.format(self._mat_name))[0]

    def _get_sg(self):
        # type: () -> None
        for attr in mc.connectionInfo('{}.outColor'.format(self._mat_name), dfs=True):
            node = attr.split('.')[0]
            if mc.nodeType(node) == 'shadingEngine':
                self._mat_sg = node
                break
        else:
            fp('传递材质工具：找不到材质球{}的SG节点'.format(self._mat_name), error=True, viewMes=True)

    def _get_objs(self):
        mc.select(cl=True)
        mc.hyperShade(o=self._mat_name)
        self._mat_objs = mc.ls(sl=True)
        if not self._mat_objs:
            fp('传递材质工具：材质球{}中没有赋予任何模型'.format(self._mat_name), warning=True)

    @property
    def mat_name(self):
        # type: () -> str
        return self._mat_name

    @property
    def mat_type(self):
        # type: () -> str
        return self._mat_type

    @property
    def mat_attr_color(self):
        # type: () -> list[float, float, float]|{str: str}
        return self._mat_attr_color

    @property
    def mat_attr_trans(self):
        # type: () -> list
        return self._mat_attr_trans

    @property
    def mat_sg(self):
        # type: () -> str
        return self._mat_sg

    @property
    def mat_objs(self):
        # type: () -> list[str]
        return self._mat_objs

class PreferencesDialog(QDialog):
    def __init__(self, parent=wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget)):
        super(PreferencesDialog, self).__init__(parent)
        self.setWindowTitle(u'传递材质工具首选项')

        self._itm_lis = []

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self._create_exclude_list()
        self._create_right_list()

    def create_widgets(self):
        self.wgt_exclude = qw.TableListWidget(u'排除材质名称:', self)
        self.wgt_right = qw.TableListWidget(u'支持的材质球类型:', self)

        self.but_save = QPushButton(u'保存')
        self.but_cancel = QPushButton(u'取消')

    def create_layout(self):
        tab_exclude = QTabWidget()
        tab_exclude.addTab(self.wgt_exclude, u'排除材质')
        tab_exclude.addTab(self.wgt_right, u'支持材质球类型')

        layout_tool = QHBoxLayout()
        layout_tool.addWidget(self.but_save)
        layout_tool.addWidget(self.but_cancel)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(tab_exclude)
        main_layout.addSpacing(0)
        main_layout.addLayout(layout_tool)

    def create_connections(self):
        self.wgt_exclude.addClicked.connect(self._add_exclude_item)
        self.wgt_right.addClicked.connect(self._add_right_item)
        self.but_save.clicked.connect(self._save_preferences)
        self.but_cancel.clicked.connect(self._cancel_preferences)

    def _create_exclude_list(self):
        exclude_lis = cf.get_value('transfer_material', 'exclude_mat', 'str').split(',')
        for nam in exclude_lis:
            self.wgt_exclude.add_item(nam, ic['hypershadeIcon'])

    def _create_right_list(self):
        right_lis = cf.get_value('transfer_material', 'right_type', 'str').split(',')
        for typ_nam in right_lis:
            self.wgt_right.add_item(typ_nam, ic['hypershade'])

    def _add_exclude_item(self):
        out, ok = QInputDialog.getText(self, u'添加材质球名', u'请输入材质球名', QLineEdit.Normal, '')
        if ok:
            self.wgt_exclude.add_item(out, ic['hypershadeIcon'])

    def _add_right_item(self):
        out, ok = QInputDialog.getText(self, u'添加材质球类型', u'请输入材质球类型', QLineEdit.Normal, '')
        if ok:
            self.wgt_right.add_item(out, ic['hypershade'])

    def _save_preferences(self):
        self._save_exclude_list()
        self._save_right_list()
        self.close()

    def _save_exclude_list(self):
        cf.set_value('transfer_material', 'exclude_mat',
                     ','.join(map(lambda i: self.wgt_exclude.item(i).text(), range(self.wgt_exclude.count()))))

    def _save_right_list(self):
        cf.set_value('transfer_material', 'right_type',
                     ','.join(map(lambda i: self.wgt_right.item(i).text(), range(self.wgt_right.count()))))

    def _cancel_preferences(self):
        self.close()

class ReplaceMaterialTool(QMainWindow):
    def __init__(self, parent=wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget)):
        super(ReplaceMaterialTool, self).__init__(parent)

        self.setWindowTitle(u'传递材质工具')
        self.setMinimumWidth(300)

        self._mat_lis = []

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.wgt_main = QWidget()

        self.menu_edit = QMenu('编辑')
        self.action_pref = QAction('首选项')
        self.action_pref.setIcon(QIcon(ic['home']))
        self.menu_edit.addAction(self.action_pref)

        self.but_scence_path = QPushButton(u'场景路径')
        self.set_scene_path()
        self.but_export_sel_mat = QPushButton(u'导出选中材质')
        self.but_export_all_mat = QPushButton(u'导出所有材质')

        self.line_h_1 = QFrame()
        self.line_h_1.setFrameShape(QFrame.HLine)

        self.but_import_sel_mat = QPushButton(u'导入材质')

        self.line_h_2 = QFrame()
        self.line_h_2.setFrameShape(QFrame.HLine)

        self.but_del_unseless = QPushButton(u'删除无用材质')

    def create_layout(self):
        menu_bar = self.menuBar()
        menu_bar.addMenu(self.menu_edit)

        layout_export = QHBoxLayout()
        layout_export.addWidget(self.but_export_sel_mat)
        layout_export.addWidget(self.but_export_all_mat)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(3)
        main_layout.addWidget(self.but_scence_path)
        main_layout.addLayout(layout_export)
        main_layout.addWidget(self.line_h_1)
        main_layout.addWidget(self.but_import_sel_mat)
        main_layout.addWidget(self.line_h_2)
        main_layout.addWidget(self.but_del_unseless)

        self.wgt_main.setLayout(main_layout)
        self.setCentralWidget(self.wgt_main)

    def create_connections(self):
        self.action_pref.triggered.connect(self.show_preferences)

        self.but_scence_path.clicked.connect(self.open_file_path)

        self.but_export_sel_mat.clicked.connect(self.export_select_materials)
        self.but_export_all_mat.clicked.connect(self.export_all_materials)
        self.but_import_sel_mat.clicked.connect(self.import_materials)
        self.but_del_unseless.clicked.connect(self.delete_useless_materials)

    def set_scene_path(self):
        # type: () -> str
        scene_path = mc.file(q=True, exn=True)
        self.but_scence_path.setText(os.path.dirname(scene_path))
        return scene_path

    def open_file_path(self):
        json_name = os.path.splitext(self.set_scene_path())[0] + '.json'
        if os.path.exists(json_name):
            os.system('explorer /select, {}'.format(json_name.replace('/', '\\')))
        else:
            os.startfile(self.set_scene_path())

    def export_mat_fun(self, sel=False, all=False):
        # type: (bool, bool) -> None
        """
        决定导出选择列表中的材质还是场景中所有材质
        :param sel:只导出选中材质
        :param all:导出所有材质
        :return:
        """
        mat_lis = []
        mat_typ_lis = mc.listNodeTypes('shader')
        if sel:
            mat_lis = filter(lambda obj: mc.nodeType(obj) in mat_typ_lis, mc.ls(sl=True))
        elif all:
            mat_lis = mc.ls(mat=True)
        list(map(lambda mat: mat_lis.remove(mat), cf.get_value('transfer_material', 'exclude_mat').split(',')))
        for mat in mat_lis:
            if mc.nodeType(mat) not in cf.get_value('transfer_material', 'right_type').split(','):
                mat_lis.remove(mat)
                fp('传递材质工具：材质球{}的类型不被允许'.format(mat), warning=True)

        self._mat_lis = list(map(lambda mat: Material(mat), mat_lis))

    def export_select_materials(self):
        self.export_mat_fun(sel=True)
        self._export_matreials()

    def export_all_materials(self):
        self.export_mat_fun(all=True)
        self._export_matreials()

    def _export_matreials(self):
        export_dir = {mat.mat_name:
            {
            'type': mat.mat_type,
            'color': mat.mat_attr_color,
            'transparency': mat.mat_attr_trans,
            'shadingEngine': mat.mat_sg,
            'objs': mat.mat_objs
            }
            for mat in self._mat_lis}
        json_name = os.path.split(self.set_scene_path())[-1].split('.')[0]+'.json'
        out_path = fu.writeInfoAsFile(self.but_scence_path.text(), json_name, export_dir)
        fp('传递材质工具：已导出{}个材质球信息到{}'.format(self._mat_lis.__len__(), out_path), info=True, viewMes=True)

    def import_materials(self):
        file_path, ok = QFileDialog.getOpenFileName(self, u'选择材质文件', os.path.split(self.set_scene_path())[0], '(*.json)')
        if not ok:
            fp('传递材质工具：没有选择文件。', warning=True)
            return

        mat_dir = fu.fromFileReadInfo(*os.path.split(file_path))
        self._set_materials(mat_dir)

    def _set_materials(self, mat_dir):
        # type: (dict) -> None
        """
        创建与设置材质球
        :param mat_dir:读取的材质球信息
        :return:
        """
        for mat in [Material(nam, mat['type'], mat['color'], mat['transparency'], mat['shadingEngine'], mat['objs'], False)
                    for nam, mat in mat_dir.items()]:

            #材质球
            if mc.objExists(mat.mat_name):
                if mc.objectType(mat.mat_name) != mat.mat_type:
                    mc.delete(mat.mat_name)
            else:
                mc.shadingNode(mat.mat_type, asShader=True, name=mat.mat_name)
            mc.setAttr('{}.transparency'.format(mat.mat_name), *mat.mat_attr_trans, typ='double3')

            #材质球颜色或者贴图节点
            if isinstance(mat.mat_attr_color, list):
                mc.setAttr('{}.color'.format(mat.mat_name), *mat.mat_attr_color, typ='double3')
            elif isinstance(mat.mat_attr_color, dict):
                file_nam, pix_path = list(mat.mat_attr_color.items())[0]
                if not mc.objExists(file_nam):
                    mc.shadingNode('file', at=True, icm=True, n=file_nam)
                    plac_tex = mc.shadingNode('place2dTexture', au=True)

                    fil_lis = ['coverage', 'translateFrame', 'rotateFrame', 'mirrorU', 'mirrorV', 'stagger', 'wrapU',
                               'wrapV', 'repeatUV', 'offset', 'rotateUV', 'noiseUV', 'vertexUvOne', 'vertexUvTwo',
                               'vertexUvThree', 'vertexCameraOne', 'uv', 'uvFilterSize']
                    plac_lis = ['coverage', 'translateFrame', 'rotateFrame', 'mirrorU', 'mirrorV', 'stagger', 'wrapU',
                                'wrapV', 'repeatUV', 'offset', 'rotateUV', 'noiseUV', 'vertexUvOne', 'vertexUvTwo',
                                'vertexUvThree', 'vertexCameraOne', 'outUV', 'outUvFilterSize']
                    for up, douwn in zip(plac_lis, fil_lis):
                        mc.connectAttr('{}.{}'.format(plac_tex, up), '{}.{}'.format(file_nam, douwn))

                mc.setAttr('{}.fileTextureName'.format(file_nam), pix_path, typ='string')
                mc.connectAttr('{}.outColor'.format(file_nam), '{}.color'.format(mat.mat_name), f=True)

            #着色器节点
            if not mc.objExists(mat.mat_sg):
                mc.sets(r=True, no=True, em=True, n=mat.mat_sg)
            mc.connectAttr('{}.outColor'.format(mat.mat_name), '{}.surfaceShader'.format(mat.mat_sg), f=True)

            #向模型赋予材质球
            for obj in mat.mat_objs:
                if not mc.objExists(obj):
                    fp('传递材质工具：材质球{}对应的模型{} 不存在。'.format(mat.mat_name, obj),
                       error=True, viewMes=True, block=False)
                else:
                    mc.sets(obj, e=True, fe=mat.mat_sg)

            fp('传递材质工具：已导入材质球：{}'.format(mat.mat_name), info=True)
        else:
            fp('传递材质工具：导入材质已完成。', warning=True)

    def delete_useless_materials(self):
        mm.eval('MLdeleteUnused;')
        fp('传递材质工具：已删除无用材质。', info=True)

    def show_preferences(self):
        preferences = PreferencesDialog(self)
        preferences.exec_()


try:
    _material_main_window.close()
    _material_main_window.deleteLater()
except:
    pass
finally:
    _material_main_window = ReplaceMaterialTool()
    _material_main_window.show()
