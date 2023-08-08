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
from feedback_tool import Feedback_info as fp


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


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

    def create_layout(self):
        layout_jntNam = QtWidgets.QHBoxLayout()
        layout_jntNam.addWidget(self.lin_prefix)
        layout_jntNam.addWidget(self.line_h_a)
        layout_jntNam.addWidget(self.lin_repIn)
        layout_jntNam.addWidget(self.lin_repOut)
        layout_jntNam.addWidget(self.line_h_b)
        layout_jntNam.addWidget(self.lin_suffix)

        layout_main = QtWidgets.QVBoxLayout(self)
        layout_main.setSpacing(3)
        layout_main.setContentsMargins(3, 3, 3, 3)
        layout_main.addWidget(self.but_outSkin)
        layout_main.addLayout(layout_jntNam)
        layout_main.addWidget(self.but_imptSkin)

    def create_connections(self):
        self.but_outSkin.clicked.connect(self.exportSkin)
        self.but_imptSkin.clicked.connect(self.importSkin)

    def exportSkin(self):
        nod = mc.ls(sl=True, fl=True)
        if nod and mc.nodeType(mc.listRelatives(nod[0], s=True)[0]) == 'mesh':
            fn_skin = apiUtils.fromObjGetRigNode(nod[0], path_name=False)[0]
            data = {'weights': {},
                    'blendWeights': [],
                    'name': nod[0]}
            dagPath, components = apiUtils.getGeometryComponents(fn_skin)
            data = self.gatWeightsToData(fn_skin, data, dagPath, components)
            data = self.blendWeights(fn_skin, data, dagPath, components, True)

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
            self.blendWeights(fn_skin, data, dagPath, components)
            fp('�ѽ�{}����Ƥ��Ϣ���뵽{}��'.format(file_path, fn_skin.name()))
        else:
            fp('ѡ�����{}������Ƥ�ڵ�'.format(nod[0]), error=True)

    def gatWeightsToData(self, fn_skin, data, dag_path, components):
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
        numInfluences = fn_skin.influenceObjects(influencePaths)  #��ǰӰ��ؽڶ�����������Ѱ����ؽڶ���ɵ���
        numComponentsPerInfluence = weights.length() / numInfluences  #����
        if len(data['weights'].keys()) == influencePaths.length():
            for data_jnt, dataWeights in data['weights'].items():  #�ؽ�����Ȩ���б�
                jnt = self.reJointName(data_jnt)
                for ii in range(influencePaths.length()):  #��ǰӰ��ؽ��б�
                    influenceName = influencePaths[ii].partialPathName()  #��ǰ�ؽ���
                    if influenceName == jnt:
                        for jj in range(numComponentsPerInfluence):  #ÿ����
                            weights.set(dataWeights[jj], jj * numInfluences + ii)
                        break
                else:
                    fp('�ֵ��еĹؽ�{}��Ӧ�ĳ����ؽ�{}����Ƥ�ڵ�{}���Ҳ�����Ӧ��,����ܵ���һЩ���Ȩ��������Ϊ1'.format(
                        data_jnt, jnt, fn_skin.name()), warning=True)
            apiUtils.setCurrentWeights(fn_skin, weights, numInfluences, dag_path, components)
        else:
            fp('�������Ƥ�ؽ������볡���еĹؽ���������Ӧ', error=True)

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
            jnt = prefix + prefix
        if repIn:
            jnt = jnt.replace(repIn, repOut)
        if suffix:
            jnt = jnt + suffix

        return jnt

    def blendWeights(self, fn_skin, data, dag_path, components, get=False):
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


try:
    transSkinwindow.close()
    transSkinwindow.deleteLater()
except:
    pass
finally:
    transSkinwindow = TransforSkinWeightWindow()
    transSkinwindow.show()
