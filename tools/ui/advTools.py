# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui

from feedback_tool import Feedback_info as fp
from dutils import advUtils

reload(advUtils)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class ADVTools(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(ADVTools, self).__init__(parent)

        self.setWindowTitle(u'adv��������')
        if mc.about(ntOS=True):  #�ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.jnt_hand_lis = ['PinkyFinger1', 'PinkyFinger2', 'PinkyFinger3', 'RingFinger1', 'RingFinger2',
                             'RingFinger3', 'MiddleFinger1', 'MiddleFinger2', 'MiddleFinger3', 'IndexFinger1',
                             'IndexFinger2', 'IndexFinger3', 'ThumbFinger2', 'ThumbFinger3']


        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.but_createDrvJnt = QtWidgets.QPushButton(u'���˫�����͹ؽ�')
        self.but_selectDrvJnt = QtWidgets.QPushButton(u'ѡ�����͹ؽ�')

    def create_layout(self):
        drvenJoint_layout = QtWidgets.QHBoxLayout()
        drvenJoint_layout.addWidget(self.but_createDrvJnt)
        drvenJoint_layout.addWidget(self.but_selectDrvJnt)

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.addLayout(drvenJoint_layout)

    def create_connections(self):
        self.but_createDrvJnt.clicked.connect(self.createHandDrivenJoint)
        self.but_selectDrvJnt.clicked.connect(self.selectCorrectJoint)

    def createHandDrivenJoint(self):
        """
        ��adv˫���������͹ؽ�
        :return:
        """
        for r in ['_R', '_L']:
            for jnt in self.jnt_hand_lis:
                advUtils.createUiaxialDrive('{}{}'.format(jnt, r), 'ry', 90)
        fp('adv˫�����͹ؽ�����ӡ�', info=True)

    def selectCorrectJoint(self):
        """
        ѡ��˫�ֵ����͹ؽڵ���ת�ؽ�
        :return:
        """
        sel_lis = []
        for r in ['_R', '_L']:
            for jnt in self.jnt_hand_lis:
                jnt_nam = 'jnt_{}{}_ry_base_001'.format(jnt, r)
                if mc.objExists(jnt_nam):
                    sel_lis.append(jnt_nam)
                else:
                    fp('�ؽ�{}�����ڡ�'.format(jnt_nam), warning=True)
        if sel_lis:
            mc.select(sel_lis)
            fp('��ѡ�����͹ؽڡ�', info=True)
        else:
            fp('������û����ӵ�˫�����͹ؽڡ�', error=True)

def openAdvTool():
    try:
        ADVToolswindow.close()
        ADVToolswindow.deleteLater()
    except:
        pass
    finally:
        ADVToolswindow = ADVTools()
        ADVToolswindow.show()
