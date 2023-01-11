# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui

import os
import sys
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

if sys.version_info.major == 3:
    #������Ϊpy3ʱ
    from importlib import reload


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class TrainingApparatus(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(TrainingApparatus, self).__init__(parent)

        self.setWindowTitle(u'Meta������')
        if mc.about(ntOS=True):  # �ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.but_extract_head = QtWidgets.QPushButton(u'һ����ͷ')
        self.but_extract_body = QtWidgets.QPushButton(u'һ����ȫ��')

        self.but_createBied = QtWidgets.QPushButton(u'׼������adv�Ǽ�')
        self.but_matchJoint = QtWidgets.QPushButton(u'ƥ��Ǽ�')
        self.lin_assetsName = QtWidgets.QLineEdit()
        self.lin_assetsName.setPlaceholderText(u'���ʲ�����')
        self.lin_assetsName.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[a-zA-Z0-9_]{16}')))
        self.but_createLink = QtWidgets.QPushButton(u'��������')

        self.but_hand_transform = QtWidgets.QPushButton(u'ͷ���任')
        self.but_hand_to_adv = QtWidgets.QPushButton(u'metaͷ��adv�Ǽ�')

        self.but_getDnaPath = QtWidgets.QPushButton(u'��ȡdna�ļ�·��')
        self.but_getRL4_value = QtWidgets.QPushButton(u'��ȡRL4�ļ���Ϣ')
        self.but_createRL4 = QtWidgets.QPushButton(u'����embeddedNodeRL4�ڵ�')

        self.line_h_a = QtWidgets.QFrame()
        self.line_h_a.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_h_b = QtWidgets.QFrame()
        self.line_h_b.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_h_c = QtWidgets.QFrame()
        self.line_h_c.setFrameShape(QtWidgets.QFrame.HLine)

    def create_layout(self):
        extract_layout = QtWidgets.QHBoxLayout()
        extract_layout.addWidget(self.but_extract_head)
        extract_layout.addWidget(self.but_extract_body)

        link_layout = QtWidgets.QHBoxLayout()
        link_layout.addWidget(self.but_createBied)
        link_layout.addWidget(self.but_matchJoint)
        link_layout.addWidget(self.lin_assetsName)
        link_layout.addWidget(self.but_createLink)

        createRL4_layout = QtWidgets.QHBoxLayout()
        createRL4_layout.addWidget(self.but_getDnaPath)
        createRL4_layout.addWidget(self.but_getRL4_value)
        createRL4_layout.addWidget(self.but_createRL4)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(extract_layout)
        main_layout.addWidget(self.line_h_a)
        main_layout.addLayout(link_layout)
        main_layout.addWidget(self.line_h_b)
        main_layout.addWidget(self.but_hand_transform)
        main_layout.addWidget(self.but_hand_to_adv)
        main_layout.addWidget(self.line_h_c)
        main_layout.addLayout(createRL4_layout)

    def create_connections(self):
        self.but_extract_head.clicked.connect(self.extract_head)
        self.but_extract_body.clicked.connect(self.extract_body)
        self.but_createBied.clicked.connect(self.set_bied)
        self.but_matchJoint.clicked.connect(self.match_joint)
        self.but_createLink.clicked.connect(self.set_link)
        self.but_hand_transform.clicked.connect(self.set_hand)
        self.but_hand_to_adv.clicked.connect(self.set_hand_to_adv)
        self.but_getDnaPath.clicked.connect(self.get_RL4_path)
        self.but_getRL4_value.clicked.connect(self.get_RL4_value)
        self.but_createRL4.clicked.connect(self.create_RL4)

    def extract_head(self):
        '''
        ��ͷ�İ󶨴��ļ��а������
        :return:
        '''
        from sx_toolBOX.SX_rig.Meta import extract_meta_head
        reload(extract_meta_head)
        extract_meta_head.EXTRACT_META()

    def extract_body(self):
        '''
        ��ͷ������İ󶨴��ļ��а������
        :return:
        '''
        from sx_toolBOX.SX_rig.Meta import extract_meta_body
        reload(extract_meta_body)
        extract_meta_body.Extract_Body()

    def set_bied(self):
        '''
        ����adv�ĹǼܣ���metaͷ�Ĺؽ���������Ĺؽ����ϲ�����
        :return:
        '''
        from sx_toolBOX.SX_rig.Meta import adv_to_meta
        reload(adv_to_meta)
        adv_to_meta.CreatBied()

    def match_joint(self):
        '''
        ��adv�Ķ�λ�Ǽܹǵ�ŵ�meta�ĹǼܶ�Ӧλ����
        :return:
        '''
        from sx_toolBOX.SX_rig.Meta import adv_to_meta
        reload(adv_to_meta)
        adv_to_meta.MatchJoint()

    def set_link(self):
        '''
        ��������
        :return:
        '''
        assert_name = self.lin_assetsName.text()
        if assert_name:
            if mc.ls('Main'):
                from sx_toolBOX.SX_rig import adv_to_meta
                reload(adv_to_meta)
                adv_to_meta.createLink(assert_name)
            else:
                log.error('δbulid������')
                return False
        else:
            log.error('δ�����ʲ�����')
            return False

    def set_hand(self):
        '''
        ����任meta��ͷ��py�ļ�����Ϊһ�������Ĺ���ʹ��
        :return:
        '''
        from sx_toolBOX.SX_rig.Meta import metaHuman_transformation_head
        reload(metaHuman_transformation_head)

    def set_hand_to_adv(self):
        '''
        ��meta��ͷ�ӵ�adv�ĹǼ���
        :return:
        '''
        from sx_toolBOX.SX_rig.Meta import metaHand_to_adv
        reload(metaHand_to_adv)
        metaHand_to_adv.metaHead_to_adv()

    def get_RL4_path(self):
        '''
        ��ȡdna�ļ�����·��
        :return:
        '''
        self.RL4_path = None
        scence_path = mc.file(exn=True, q=True)
        os.path.dirname(scence_path)
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, u'ѡ��dna�ļ�', scence_path, '(*.dna)')
        if file_path[0]:
            self.RL4_path = file_path[0]
            self.but_getDnaPath.setStyleSheet("background-color: green")
        else:
            log.warning('û��ѡ����Ч�ļ���')

    def get_RL4_value(self):
        '''
        ��ȡ��ȷRL4�ڵ�����ֺ�������Ϣ
        :return:
        '''
        self.RL4_nam = None
        self.RL4_val_dir = {}
        if mc.ls(sl=True) and mc.nodeType(mc.ls(sl=True)[0]) == 'embeddedNodeRL4':
            self.RL4_nam = mc.ls(sl=True)[0]
            for inf in mc.listAttr('{}.jntTranslationOutputs'.format(self.RL4_nam), m=True):
                self.RL4_val_dir[inf] = mc.getAttr('{}.{}'.format(self.RL4_nam, inf))
            for inf in mc.listAttr('{}.jntScaleOutputs'.format(self.RL4_nam), m=True):
                self.RL4_val_dir[inf] = mc.getAttr('{}.{}'.format(self.RL4_nam, inf))
            self.but_getRL4_value.setStyleSheet("background-color: green")
        else:
            log.error('��Ч��ѡ�����')

    def create_RL4(self):
        '''
        ����embeddedNodeRL4�ڵ㲢���ú�����
        :return: 
        '''
        if self.RL4_path and self.RL4_nam and self.RL4_val_dir:
            mm.eval('source "Z:/Library/rig_plug_in/maya_plug/custom_tools/sx_toolBOX/SX_rig/Meta/create_RL4node.mel"')
            mm.eval('MHCreateRL4node "{}" {};'.format(self.RL4_path, self.RL4_nam))
            for attr, val in self.RL4_val_dir.items():
                mc.setAttr('{}.{}'.format(self.RL4_nam, attr), val)
            log.info('����embeddedNodeRL4�ڵ���ɡ�')
        else:
            log.error('���������㡣')


try:
    my_window.close()
    my_window.deleteLater()
except:
    pass
finally:
    my_window = TrainingApparatus()
    my_window.show()