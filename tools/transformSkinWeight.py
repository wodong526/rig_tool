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
    ��ȡ��Ƥ�ڵ��Ȩ���б�
    :param fn_skin:MFnSkinCluster���Ͷ���
    :param data:������ƤȨ����Ϣ���ֵ�
    :param dag_path:��Ƥ�ڵ��dagPath����
    :param components:��Ƥ�ڵ������ڵ�
    :return:ת�غ�Ȩ��ֵ���ֵ�
    """
    weights = apiUtils.getCurrentWeights(fn_skin, dag_path, components)
    influencePaths = om.MDagPathArray()
    numInfluences = fn_skin.influenceObjects(influencePaths)  #Ӱ����
    numComponentsPerInfluence = weights.length() / numInfluences  #����
    for ii in range(influencePaths.length()):  #�ڼ���Ӱ��
        influenceName = influencePaths[ii].partialPathName()
        data['weights'][influenceName] = [weights[jj * numInfluences + ii] for jj in
                                          range(numComponentsPerInfluence)]

    return data


def blendWeights(fn_skin, data, dag_path, components, get=False):
    """
    ��ȡ�����û��Ȩ�ط�ʽ
    :param data: ���ػ��Ȩ�ط�ʽ���ֵ�
    :param fn_skin: MFnSkinCluster���Ͷ���
    :param dag_path: ��Ƥ�ڵ��dagPath����
    :param get: �ǻ�ȡ��������
    :param components: ��Ƥ�ڵ������ڵ�
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

        self.setWindowTitle(u'Ȩ�ش��ݹ���')
        if mc.about(ntOS=True):  #�ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.but_outSkin = QtWidgets.QPushButton(u'����Ȩ��')
        self.but_imptSkin = QtWidgets.QPushButton(u'����Ȩ��')

        self.lin_prefix = QtWidgets.QLineEdit()
        self.lin_prefix.setPlaceholderText(u'ǰ׺')
        self.lin_repIn = QtWidgets.QLineEdit()
        self.lin_repIn.setPlaceholderText(u'��')
        self.lin_repOut = QtWidgets.QLineEdit()
        self.lin_repOut.setPlaceholderText(u'��')
        self.lin_suffix = QtWidgets.QLineEdit()
        self.lin_suffix.setPlaceholderText(u'��׺')

        self.line_h_a = QtWidgets.QFrame()
        self.line_h_a.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_h_a.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_h_b = QtWidgets.QFrame()
        self.line_h_b.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_h_b.setFrameShadow(QtWidgets.QFrame.Raised)

        self.but_getPoint = QtWidgets.QPushButton(u'��ȡһ�����Ȩ��')
        self.but_setPoint = QtWidgets.QPushButton(u'���õ�Ȩ��')

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
                file_path = fileUtils.saveFilePath(u'ѡ��Ҫ����Ȩ�ص��ļ�·��', self.scene_path, 'dong')
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            fp('��Ƥ{}��Ȩ�������ѵ�����{}'.format(fn_skin.name(), file_path))
        else:
            fp('ѡ�����{}������Ƥ�ڵ�'.format(nod[0]), error=True)

    def importSkin(self):
        nod = mc.ls(sl=True, fl=True)
        if nod and mc.nodeType(mc.listRelatives(nod[0], s=True)[0]) == 'mesh':
            fn_skin = apiUtils.fromObjGetRigNode(nod[0], path_name=False)[0]
            dagPath, components = apiUtils.getGeometryComponents(fn_skin)

            file_path = fileUtils.getFilePath(u'ѡ��Ҫ����Ȩ�ص��ļ�·��', self.scene_path, 'dong')
            with open(file_path, 'rb') as f:
                data = pickle.load(f)

            self.setInfluenceWeights(fn_skin, data, dagPath, components)
            blendWeights(fn_skin, data, dagPath, components)
            fp('�ѽ�{}����Ƥ��Ϣ���뵽{}��'.format(file_path, fn_skin.name()))
        else:
            fp('ѡ�����{}������Ƥ�ڵ�'.format(nod[0]), error=True)

    def setInfluenceWeights(self, fn_skin, data, dag_path, components):
        """
        �����ֵ佫Ȩ�ظ���MFnSkinCluster����
        :param fn_skin: MFnSkinCluster���Ͷ���
        :param data: ������ƤȨ����Ϣ���ֵ�
        :param dag_path: ��Ƥ�ڵ��dagPath����
        :param components: ��Ƥ�ڵ������ڵ�
        :return:
        """
        weights = apiUtils.getCurrentWeights(fn_skin, dag_path, components)
        influencePaths = om.MDagPathArray()
        fn_skin.influenceObjects(influencePaths)  #��ǰӰ��ؽڶ�����������Ѱ����ؽڶ���ɵ���
        numComponentsPerInfluence = weights.length() / influencePaths.length()  #��ǰӰ�����ĵ���

        if len(data['weights'].keys()) != influencePaths.length():
            fp('�������Ƥ�ؽ�������ѡ�еĹؽ���������Ӧ', error=True, viewMes=True)
        if numComponentsPerInfluence != len(data['weights'].values()[0]):
            fp('�����ģ�͵�����ѡ��ģ���еĵ�������Ӧ', error=True, viewMes=True)
        for data_jnt, dataWeights in data['weights'].items():  #�ؽ�����Ȩ���б�
            jnt = self.reJointName(data_jnt)
            for ii in range(influencePaths.length()):  #��ǰӰ��ؽ��б�
                influenceName = influencePaths[ii].partialPathName()  #��ǰ�ؽ���
                if influenceName == jnt:
                    for jj in range(numComponentsPerInfluence):  #ÿ����
                        weights.set(dataWeights[jj], jj * influencePaths.length() + ii)
                    break
            else:
                fp('�ֵ��еĹؽ�{}��Ӧ�ĳ����ؽ�{}����Ƥ�ڵ�{}���Ҳ�����Ӧ��,����ܵ���һЩ���Ȩ��������Ϊ1'.format(
                    data_jnt, jnt, fn_skin.name()), warning=True)

        apiUtils.setCurrentWeights(fn_skin, weights, influencePaths.length(), dag_path, components)


    def reJointName(self, jnt):
        """
        ������Ĺؽ��볡���еĹؽ�����ƥ��
        :param jnt: ����Ĺؽ�
        :return: �޸ĺ�Ĺؽ���
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
        ��ȡѡ�е�һ�����Ȩ��
        :return: None
        """
        dag, com = apiUtils.getApiNode(com=True)
        skin = apiUtils.fromObjGetRigNode(dag, path_name=False)[0]
        skin_lis = apiUtils.getCurrentWeights(skin, *apiUtils.getGeometryComponents(skin))#Ȩ���б�
        influencePaths = om.MDagPathArray()#Ӱ��ؽ��б�
        skin.influenceObjects(influencePaths)

        it_vtx = om.MItMeshVertex(dag, com)#ѡ�еĵ�id������
        if it_vtx.count() == 1:
            vtx_id = it_vtx.count()
        else:
            fp('ѡ�еĵ�����ӦΪ1��ʵ��Ϊ{}'.format(it_vtx.count()), error=True, viewMes=True)
        self.skin_dir = {}
        for i in range(influencePaths.length()):
            self.skin_dir[influencePaths[i].partialPathName()] = skin_lis[vtx_id * influencePaths.length() + i]
        fp('��ȡ��Ȩ�����', info=True, viewMes=True)

    def set_select_point_weight(self):
        """
        ����ȡ�ĵ�Ȩ�����ø�ѡ�еĵ��ѡ�е�ģ��
        :return:None
        """
        dag, com = apiUtils.getApiNode(com=True)
        skin = apiUtils.fromObjGetRigNode(dag, path_name=False)[0]
        weight_lis = apiUtils.getCurrentWeights(skin, *apiUtils.getGeometryComponents(skin))  #Ȩ���б�

        influencePaths = om.MDagPathArray()  #Ӱ��ؽ��б�
        skin.influenceObjects(influencePaths)

        it_vtx = om.MItMeshVertex(dag, com)  #ѡ�еĵ�id������
        if it_vtx.count() == 0:
            fp('ѡ�еĵ�����Ӧ���ڵ���1��ʵ��Ϊ{}'.format(it_vtx.count()), error=True, viewMes=True)
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
                        fp('�ؽ�{}����ѡ�ж���{}����Ƥ��'.format(influencePaths[n].partialPathName(), dag.partialPathName()), error=True)

        apiUtils.setCurrentWeights(skin, weight_lis, influencePaths.length(), *apiUtils.getGeometryComponents(skin))
        fp('���õ�Ȩ�����', info=True, viewMes=True)


try:
    transSkinwindow.close()
    transSkinwindow.deleteLater()
except:
    pass
finally:
    transSkinwindow = TransforSkinWeightWindow()
    transSkinwindow.show()
