# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import maya.OpenMayaAnim as omain

import cPickle as pickle
import os

from dutils import apiUtils, fileUtils
reload(apiUtils)
from feedback_tool import Feedback_info as fp


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def gatWeightsToData(fn_skin, data, dag_path, components):
    """
    获取蒙皮节点的权重列表
    :param fn_skin:MFnSkinCluster类型对象
    :param data:承载蒙皮权重信息的字典
    :param dag_path:蒙皮节点的dagPath对象
    :param components:蒙皮节点的组件节点
    :return:转载好权重值的字典
    """
    weights = apiUtils.getCurrentWeights(fn_skin, dag_path, components)
    influencePaths = om.MDagPathArray()
    numInfluences = fn_skin.influenceObjects(influencePaths)  #影响数
    numComponentsPerInfluence = weights.length() / numInfluences  #点数
    for ii in range(influencePaths.length()):  #第几个影响
        influenceName = influencePaths[ii].partialPathName()
        data['weights'][influenceName] = [weights[jj * numInfluences + ii] for jj in
                                          range(numComponentsPerInfluence)]

    return data


def blendWeights(fn_skin, data, dag_path, components, get=False):
    """
    获取或设置混合权重方式
    :param data: 承载混合权重方式的字典
    :param fn_skin: MFnSkinCluster类型对象
    :param dag_path: 蒙皮节点的dagPath对象
    :param get: 是获取还是设置
    :param components: 蒙皮节点的组件节点
    :return:
    """
    if get:
        weights = om.MDoubleArray()
        fn_skin.getBlendWeights(dag_path, components, weights)
        data['blendWeights'] = [weights[i] for i in range(weights.length())]
        return data
    elif not get:
        blendWeights = om.MDoubleArray(len(data['blendWeights']))
        for i, w in enumerate(data['blendWeights']):
            blendWeights.set(w, i)
        fn_skin.setBlendWeights(dag_path, components, blendWeights)


class TransforSkinWeightWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(TransforSkinWeightWindow, self).__init__(parent)

        self.scene_path = os.path.dirname(mc.file(exn=1, q=1))

        self.setWindowTitle(u'权重传递工具')
        if mc.about(ntOS=True):  #判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.but_outSkin = QtWidgets.QPushButton(u'导出权重')
        self.but_imptSkin = QtWidgets.QPushButton(u'导入权重')

        self.lin_prefix = QtWidgets.QLineEdit()
        self.lin_prefix.setPlaceholderText(u'前缀')
        self.lin_repIn = QtWidgets.QLineEdit()
        self.lin_repIn.setPlaceholderText(u'替')
        self.lin_repOut = QtWidgets.QLineEdit()
        self.lin_repOut.setPlaceholderText(u'换')
        self.lin_suffix = QtWidgets.QLineEdit()
        self.lin_suffix.setPlaceholderText(u'后缀')

        self.line_h_a = QtWidgets.QFrame()
        self.line_h_a.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_h_a.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_h_b = QtWidgets.QFrame()
        self.line_h_b.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_h_b.setFrameShadow(QtWidgets.QFrame.Raised)

        self.but_getPoint = QtWidgets.QPushButton(u'获取一个点的权重')
        self.but_setPoint = QtWidgets.QPushButton(u'设置点权重')

    def create_layout(self):
        layout_jntNam = QtWidgets.QHBoxLayout()
        layout_jntNam.addWidget(self.lin_prefix)
        layout_jntNam.addWidget(self.line_h_a)
        layout_jntNam.addWidget(self.lin_repIn)
        layout_jntNam.addWidget(self.lin_repOut)
        layout_jntNam.addWidget(self.line_h_b)
        layout_jntNam.addWidget(self.lin_suffix)

        layout_transPointWeight = QtWidgets.QHBoxLayout()
        layout_transPointWeight.addWidget(self.but_getPoint)
        layout_transPointWeight.addWidget(self.but_setPoint)

        layout_main = QtWidgets.QVBoxLayout(self)
        layout_main.setSpacing(3)
        layout_main.setContentsMargins(3, 3, 3, 3)
        layout_main.addWidget(self.but_outSkin)
        layout_main.addLayout(layout_jntNam)
        layout_main.addWidget(self.but_imptSkin)
        layout_main.addLayout(layout_transPointWeight)

    def create_connections(self):
        self.but_outSkin.clicked.connect(self.exportSkin)
        self.but_imptSkin.clicked.connect(self.importSkin)
        self.but_getPoint.clicked.connect(self.get_select_point_weight)
        self.but_setPoint.clicked.connect(self.set_select_point_weight)

    def exportSkin(self, file_path=''):
        nod = mc.ls(sl=True, fl=True)
        if nod and mc.nodeType(mc.listRelatives(nod[0], s=True)[0]) == 'mesh':
            fn_skin = apiUtils.fromObjGetRigNode(nod[0], path_name=False)[0]
            data = {'weights': {},
                    'blendWeights': [],
                    'name': nod[0]}
            dagPath, components = apiUtils.getGeometryComponents(fn_skin)
            data = gatWeightsToData(fn_skin, data, dagPath, components)
            data = blendWeights(fn_skin, data, dagPath, components, True)

            if not file_path:
                file_path = fileUtils.saveFilePath(u'选择要导出权重的文件路径', self.scene_path, 'dong')
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            fp('蒙皮{}的权重数据已导出到{}'.format(fn_skin.name(), file_path))
        else:
            fp('选择对象{}不是蒙皮节点'.format(nod[0]), error=True)

    def importSkin(self):
        nod = mc.ls(sl=True, fl=True)
        if nod and mc.nodeType(mc.listRelatives(nod[0], s=True)[0]) == 'mesh':
            fn_skin = apiUtils.fromObjGetRigNode(nod[0], path_name=False)[0]
            dagPath, components = apiUtils.getGeometryComponents(fn_skin)

            file_path = fileUtils.getFilePath(u'选择要导入权重的文件路径', self.scene_path, 'dong')
            with open(file_path, 'rb') as f:
                data = pickle.load(f)

            self.setInfluenceWeights(fn_skin, data, dagPath, components)
            blendWeights(fn_skin, data, dagPath, components)
            fp('已将{}的蒙皮信息导入到{}中'.format(file_path, fn_skin.name()))
        else:
            fp('选择对象{}不是蒙皮节点'.format(nod[0]), error=True)

    def setInfluenceWeights(self, fn_skin, data, dag_path, components):
        """
        根据字典将权重赋予MFnSkinCluster对象
        :param fn_skin: MFnSkinCluster类型对象
        :param data: 承载蒙皮权重信息的字典
        :param dag_path: 蒙皮节点的dagPath对象
        :param components: 蒙皮节点的组件节点
        :return:
        """
        weights = apiUtils.getCurrentWeights(fn_skin, dag_path, components)
        influencePaths = om.MDagPathArray()
        fn_skin.influenceObjects(influencePaths)  #当前影响关节对象的容器，已包含关节对象可迭代
        numComponentsPerInfluence = weights.length() / influencePaths.length()  #当前影响对象的点数

        if len(data['weights'].keys()) != influencePaths.length():
            fp('导入的蒙皮关节数量与选中的关节数量不对应', error=True, viewMes=True)
        if numComponentsPerInfluence != len(data['weights'].values()[0]):
            fp('导入的模型点数与选中模型中的点数不对应', error=True, viewMes=True)
        for data_jnt, dataWeights in data['weights'].items():  #关节名，权重列表
            jnt = self.reJointName(data_jnt)
            for ii in range(influencePaths.length()):  #当前影响关节列表
                influenceName = influencePaths[ii].partialPathName()  #当前关节名
                if influenceName == jnt:
                    for jj in range(numComponentsPerInfluence):  #每个点
                        weights.set(dataWeights[jj], jj * influencePaths.length() + ii)
                    break
            else:
                fp('字典中的关节{}对应的场景关节{}在蒙皮节点{}中找不到对应项,这可能导致一些点的权重总量不为1'.format(
                    data_jnt, jnt, fn_skin.name()), warning=True)

        apiUtils.setCurrentWeights(fn_skin, weights, influencePaths.length(), dag_path, components)


    def reJointName(self, jnt):
        """
        将导入的关节与场景中的关节名做匹配
        :param jnt: 导入的关节
        :return: 修改后的关节名
        """
        prefix = self.lin_prefix.text()
        repIn = self.lin_repIn.text()
        repOut = self.lin_repOut.text()
        suffix = self.lin_suffix.text()

        if prefix:
            jnt = prefix + jnt
        if repIn:
            jnt = jnt.replace(repIn, repOut)
        if suffix:
            jnt = jnt + suffix

        return jnt

    def get_select_point_weight(self):
        """
        获取选中的一个点的权重
        :return: None
        """
        dag, com = apiUtils.getApiNode(com=True)
        skin = apiUtils.fromObjGetRigNode(dag, path_name=False)[0]
        skin_lis = apiUtils.getCurrentWeights(skin, *apiUtils.getGeometryComponents(skin))#权重列表
        influencePaths = om.MDagPathArray()#影响关节列表
        skin.influenceObjects(influencePaths)

        it_vtx = om.MItMeshVertex(dag, com)#选中的点id迭代器
        if it_vtx.count() == 1:
            vtx_id = it_vtx.count()
        else:
            fp('选中的点数量应为1，实际为{}'.format(it_vtx.count()), error=True, viewMes=True)
        self.skin_dir = {}
        for i in range(influencePaths.length()):
            self.skin_dir[influencePaths[i].partialPathName()] = skin_lis[vtx_id * influencePaths.length() + i]
        fp('获取点权重完成', info=True, viewMes=True)

    def set_select_point_weight(self):
        """
        将获取的点权重设置给选中的点或选中的模型
        :return:None
        """
        dag, com = apiUtils.getApiNode(com=True)
        skin = apiUtils.fromObjGetRigNode(dag, path_name=False)[0]
        weight_lis = apiUtils.getCurrentWeights(skin, *apiUtils.getGeometryComponents(skin))  #权重列表

        influencePaths = om.MDagPathArray()  #影响关节列表
        skin.influenceObjects(influencePaths)

        it_vtx = om.MItMeshVertex(dag, com)  #选中的点id迭代器
        if it_vtx.count() == 0:
            fp('选中的点数量应大于等于1，实际为{}'.format(it_vtx.count()), error=True, viewMes=True)
        vtx_lis = []
        while not it_vtx.isDone():
            vtx_lis.append(it_vtx.index())
            it_vtx.next()
        for i in range(len(weight_lis)/influencePaths.length()):
            if i in vtx_lis:
                for n in range(influencePaths.length()):
                    if influencePaths[n].partialPathName() in self.skin_dir.keys():
                        weight_lis[i*influencePaths.length()+n] = self.skin_dir[influencePaths[n].partialPathName()]
                    else:
                        fp('关节{}不在选中对象{}的蒙皮中'.format(influencePaths[n].partialPathName(), dag.partialPathName()), error=True)

        apiUtils.setCurrentWeights(skin, weight_lis, influencePaths.length(), *apiUtils.getGeometryComponents(skin))
        fp('设置点权重完成', info=True, viewMes=True)


try:
    transSkinwindow.close()
    transSkinwindow.deleteLater()
except:
    pass
finally:
    transSkinwindow = TransforSkinWeightWindow()
    transSkinwindow.show()
