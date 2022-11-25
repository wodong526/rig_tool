# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

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
        self.lab_extract = QtWidgets.QLabel(u'��һ�¾�����')
        self.lab_extract.setAlignment(QtCore.Qt.AlignCenter)
        self.but_extract_head = QtWidgets.QPushButton(u'һ����ͷ')
        self.but_extract_body = QtWidgets.QPushButton(u'һ����ȫ��')

        self.but_createBied = QtWidgets.QPushButton(u'׼������adv�Ǽ�')
        self.but_matchJoint = QtWidgets.QPushButton(u'ƥ��Ǽ�')
        self.lin_assetsName = QtWidgets.QLineEdit()
        self.lin_assetsName.setPlaceholderText(u'���ʲ�����')
        self.lin_assetsName.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[a-zA-Z0-9_]{16}')))
        self.but_createLink = QtWidgets.QPushButton(u'��������')

        self.but_hand_transform = QtWidgets.QPushButton(u'ͷ���任')

        self.line_h_a = QtWidgets.QFrame()
        self.line_h_a.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_h_b = QtWidgets.QFrame()
        self.line_h_b.setFrameShape(QtWidgets.QFrame.HLine)

    def create_layout(self):
        extract_layout = QtWidgets.QHBoxLayout()
        extract_layout.addWidget(self.but_extract_head)
        extract_layout.addWidget(self.but_extract_body)

        link_layout = QtWidgets.QHBoxLayout()
        link_layout.addWidget(self.but_createBied)
        link_layout.addWidget(self.but_matchJoint)
        link_layout.addWidget(self.lin_assetsName)
        link_layout.addWidget(self.but_createLink)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.lab_extract)
        main_layout.addLayout(extract_layout)
        main_layout.addWidget(self.line_h_a)
        main_layout.addLayout(link_layout)
        main_layout.addWidget(self.line_h_b)
        main_layout.addWidget(self.but_hand_transform)

    def create_connections(self):
        self.but_extract_head.clicked.connect(self.extract_head)
        self.but_extract_body.clicked.connect(self.extract_body)
        self.but_createBied.clicked.connect(self.set_bied)
        self.but_matchJoint.clicked.connect(self.match_joint)
        self.but_createLink.clicked.connect(self.set_link)
        self.but_hand_transform.clicked.connect(self.set_hand)

    def extract_head(self):
        from sx_toolBOX.SX_rig.Meta import extract_meta_head
        reload(extract_meta_head)
        extract_meta_head.EXTRACT_META()

    def extract_body(self):
        from sx_toolBOX.SX_rig.Meta import extract_meta_body
        reload(extract_meta_body)
        extract_meta_body.Extract_Body()

    def set_bied(self):
        from sx_toolBOX.SX_rig import adv_to_meta
        reload(adv_to_meta)
        adv_to_meta.CreatBied()

    def match_joint(self):
        from sx_toolBOX.SX_rig.Meta import adv_to_meta
        reload(adv_to_meta)
        adv_to_meta.MatchJoint()

    def set_link(self):
        assert_name = self.lin_assetsName.text()
        print assert_name
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
        from sx_toolBOX.SX_rig.Meta import metaHuman_transformation_head
        reload(metaHuman_transformation_head)



try:
    my_window.close()
    my_window.deleteLater()
except:
    pass
finally:
    my_window = TrainingApparatus()
    my_window.show()