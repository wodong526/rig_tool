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
from functools import partial

from feedback_tool import Feedback_info as fb_print
import data_path
from Meta import mhFaceCtrlsAnimsTool, extract_meta_head, extract_meta_body, adv_to_meta, \
                 metaHuman_transformation_head, metaHand_to_adv
reload(mhFaceCtrlsAnimsTool)

if sys.version_info.major == 3:
    #当环境为py3时
    from importlib import reload


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class TrainingApparatus(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(TrainingApparatus, self).__init__(parent)

        self.setWindowTitle(u'Meta调教器')
        if mc.about(ntOS=True):  # 判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # 删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.but_extract_head = QtWidgets.QPushButton(u'一键扣头')
        self.but_extract_body = QtWidgets.QPushButton(u'一键扣全身')

        self.but_createBied = QtWidgets.QPushButton(u'准备生成adv骨架')
        self.but_matchJoint = QtWidgets.QPushButton(u'匹配骨架')
        self.lin_assetsName = QtWidgets.QLineEdit()
        self.lin_assetsName.setPlaceholderText(u'填资产名。')
        self.lin_assetsName.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[a-zA-Z0-9_]{16}')))
        self.but_createLink = QtWidgets.QPushButton(u'创建链接')

        self.but_hand_transform = QtWidgets.QPushButton(u'头部变换')
        self.but_hand_to_adv = QtWidgets.QPushButton(u'meta头接adv骨架')

        self.but_getDnaPath = QtWidgets.QPushButton(u'获取dna文件路径')
        self.but_getRL4_value = QtWidgets.QPushButton(u'获取RL4文件信息')
        self.but_createRL4 = QtWidgets.QPushButton(u'生成embeddedNodeRL4节点')

        self.but_refNamSpace = QtWidgets.QPushButton()
        self.but_refNamSpace.setMaximumWidth(30)
        self.but_refNamSpace.setIcon(QtGui.QIcon('{}{}'.format(data_path.iconPath, 'refresh.png')))
        self.cob_namSpace = QtWidgets.QComboBox()
        self.but_get_faceCtrl_anim = QtWidgets.QPushButton(u'获取控制器动画信息文件')
        self.but_get_faceCtrl_anim.setMaximumWidth(130)

        self.lab_trsCtlKey = QtWidgets.QLabel(u'移动metaFace控制器帧')
        self.spinBox_trsVal = QtWidgets.QSpinBox()
        self.spinBox_trsVal.setMinimum(-9999999)
        self.spinBox_trsVal.setMaximum(9999999)
        self.but_transformKeys = QtWidgets.QPushButton(u'移动控制器帧')

        self.line_h_a = QtWidgets.QFrame()
        self.line_h_a.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_h_b = QtWidgets.QFrame()
        self.line_h_b.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_h_c = QtWidgets.QFrame()
        self.line_h_c.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_h_d = QtWidgets.QFrame()
        self.line_h_d.setFrameShape(QtWidgets.QFrame.HLine)

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

        trsfFaceAnim_layout = QtWidgets.QHBoxLayout()
        trsfFaceAnim_layout.addWidget(self.but_refNamSpace)
        trsfFaceAnim_layout.addWidget(self.cob_namSpace)
        trsfFaceAnim_layout.addWidget(self.but_get_faceCtrl_anim)

        trsfFaceAnimKeys_layout = QtWidgets.QHBoxLayout()
        trsfFaceAnimKeys_layout.addWidget(self.lab_trsCtlKey)
        trsfFaceAnimKeys_layout.addWidget(self.spinBox_trsVal)
        trsfFaceAnimKeys_layout.addWidget(self.but_transformKeys)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(3, 3, 3, 3)
        main_layout.setSpacing(3)
        main_layout.addLayout(extract_layout)
        main_layout.addWidget(self.line_h_a)
        main_layout.addLayout(link_layout)
        main_layout.addWidget(self.line_h_b)
        main_layout.addWidget(self.but_hand_transform)
        main_layout.addWidget(self.but_hand_to_adv)
        main_layout.addWidget(self.line_h_c)
        main_layout.addLayout(createRL4_layout)
        main_layout.addWidget(self.line_h_d)
        main_layout.addLayout(trsfFaceAnim_layout)
        main_layout.addLayout(trsfFaceAnimKeys_layout)

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
        self.but_refNamSpace.clicked.connect(self.refresh_nameSpace)
        self.but_get_faceCtrl_anim.clicked.connect(partial(mhFaceCtrlsAnimsTool.ExportMetaHumanFaceCtrlAnimToMaya,
                                                           self.cob_namSpace))
        self.but_transformKeys.clicked.connect(partial(mhFaceCtrlsAnimsTool.TransformFaceCtrlsKeys,
                                                       self.spinBox_trsVal, self.cob_namSpace))


    def extract_head(self):
        '''
        将头的绑定从文件中剥离出来
        :return:
        '''
        reload(extract_meta_head)
        extract_meta_head.EXTRACT_META()

    def extract_body(self):
        '''
        将头和身体的绑定从文件中剥离出来
        :return:
        '''
        reload(extract_meta_body)
        extract_meta_body.Extract_Body()

    def set_bied(self):
        '''
        导入adv的骨架，将meta头的关节链和身体的关节链合并起来
        :return:
        '''
        reload(adv_to_meta)
        adv_to_meta.CreatBied()

    def match_joint(self):
        '''
        将adv的定位骨架骨点放到meta的骨架对应位置上
        :return:
        '''
        reload(adv_to_meta)
        adv_to_meta.MatchJoint()

    def set_link(self):
        '''
        设置链接
        :return:
        '''
        assert_name = self.lin_assetsName.text()
        if assert_name:
            if mc.ls('Main'):
                reload(adv_to_meta)
                adv_to_meta.createLink(assert_name)
            else:
                fb_print('未bulid场景。', error=True)
                return False
        else:
            fb_print('未输入资产名。', error=True)
            return False

    def set_hand(self):
        '''
        导入变换meta的头的py文件，作为一个单独的工具使用
        :return:
        '''
        reload(metaHuman_transformation_head)
        metaHuman_transformation_head.transform_head()

    def set_hand_to_adv(self):
        '''
        将meta的头接到adv的骨架上
        :return:
        '''
        reload(metaHand_to_adv)
        metaHand_to_adv.metaHead_to_adv()

    def get_RL4_path(self):
        '''
        获取dna文件所在路径
        :return:
        '''
        self.RL4_path = None
        scence_path = mc.file(exn=True, q=True)
        os.path.dirname(scence_path)
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, u'选择dna文件', scence_path, '(*.dna)')
        if file_path[0]:
            self.RL4_path = file_path[0]
            self.but_getDnaPath.setStyleSheet("background-color: green")
        else:
            fb_print('没有选择有效文件。', error=True)

    def get_RL4_value(self):
        '''
        获取正确RL4节点的名字和属性信息
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
            fb_print('无效的选择对象。', error=True)

    def create_RL4(self):
        '''
        生成embeddedNodeRL4节点并设置好属性
        :return: 
        '''
        if self.RL4_path and self.RL4_nam and self.RL4_val_dir:
            mm.eval('source "Z:/Library/rig_plug_in/maya_plug/custom_tools/sx_toolBOX/SX_rig/Meta/create_RL4node.mel"')
            mm.eval('MHCreateRL4node "{}" {};'.format(self.RL4_path, self.RL4_nam))
            for attr, val in self.RL4_val_dir.items():
                mc.setAttr('{}.{}'.format(self.RL4_nam, attr), val)
            fb_print('生成embeddedNodeRL4节点完成。', info=True)
        else:
            fb_print('条件不满足。', error=True)

    def refresh_nameSpace(self):
        ref_lis = mc.file(q=True, r=True)
        self.cob_namSpace.clear()
        for ref in ref_lis:
            nam = mc.referenceQuery(ref, ns=True)
            self.cob_namSpace.addItem(nam[1:]+':')



try:
    my_window.close()
    my_window.deleteLater()
except:
    pass
finally:
    my_window = TrainingApparatus()
    my_window.show()