# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import json

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui

from feedback_tool import Feedback_info as fp
from dutils import advUtils
import data_path

reload(advUtils)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class ADVTools(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(ADVTools, self).__init__(parent)

        self.setWindowTitle(u'adv辅助工具')
        if mc.about(ntOS=True):  #判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.but_importBiped = QtWidgets.QPushButton(u'导入biped关节链')
        self.but_setMetaAttr = QtWidgets.QPushButton(u'设置meta绑定相关属性')
        self.but_createDrvJnt = QtWidgets.QPushButton(u'添加双手修型关节')
        self.but_selectDrvJnt = QtWidgets.QPushButton(u'选择修型关节')

    def create_layout(self):
        addBiped_layout = QtWidgets.QHBoxLayout()
        addBiped_layout.addWidget(self.but_importBiped)
        addBiped_layout.addWidget(self.but_setMetaAttr)
        drvenJoint_layout = QtWidgets.QHBoxLayout()
        drvenJoint_layout.addWidget(self.but_createDrvJnt)
        drvenJoint_layout.addWidget(self.but_selectDrvJnt)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(addBiped_layout)
        main_layout.addLayout(drvenJoint_layout)

    def create_connections(self):
        self.but_importBiped.clicked.connect(self.import_adv_bipedMa)
        self.but_setMetaAttr.clicked.connect(self.set_meta_BipAttr)
        self.but_createDrvJnt.clicked.connect(self.createHandDrivenJoint)
        self.but_selectDrvJnt.clicked.connect(self.selectCorrectJoint)

    def import_adv_bipedMa(self):
        """
        导入基础骨架
        :return:
        """
        if (not mc.dockControl('AdvancedSkeletonDockControl', q=1, ex=1) or
                not mc.window('AdvancedSkeletonDockControl', p=1, ex=1)):
            mm.eval('source \"C:/Rig_Tools/scripts/ADV/AdvancedSkeleton5.mel\";AdvancedSkeleton5;')
        mm.eval('asFitSkeletonImport;')
        # mm.eval('''if (`exists dockControl`)if (`exists dockControl`)
        #            if (`dockControl -q -ex AdvancedSkeletonDockControl`)
        #            deleteUI -control AdvancedSkeletonDockControl;
        #            if (`window -q -ex AdvancedSkeletonWindow`)
        #            deleteUI AdvancedSkeletonWindow;''')

    def set_meta_BipAttr(self):
        """
        如果是用于meta接头的骨架则用此设置关节链函数，并且重建
        :return:
        """
        mc.setAttr('Root.inbetweenJoints', 0)
        mc.setAttr('Spine1.inbetweenJoints', 1)
        mc.setAttr('Neck.inbetweenJoints', 1)

    def createHandDrivenJoint(self):
        """
        对adv双手增加修型关节
        :return:
        """
        with open('{}repairShape_jnt_dir.json'.format(data_path.advRepairShapeJointPath), 'r') as f:
            rs_jnts_dir = json.load(f)
        if rs_jnts_dir:
            for r in ['R', 'L']:
                for jnt, data in rs_jnts_dir.items():
                    advUtils.createUiaxialDrive('{}_{}'.format(jnt, r), data[0], data[1], data[2], data[3])
            fp('adv双手修型关节已添加。', info=True)
        else:
            pass

    def selectCorrectJoint(self):
        """
        选中双手的修型关节的旋转关节
        :return:
        """
        with open('{}repairShape_jnt_dir.json'.format(data_path.advRepairShapeJointPath), 'r') as f:
            rs_jnts_dir = json.load(f)

        if rs_jnts_dir:
            sel_lis = []
            for r in ['_R', '_L']:
                for jnt, aix in rs_jnts_dir.items():
                    jnt_nam = 'jnt_{}{}_{}_skin*001'.format(jnt, r, aix[0])
                    if mc.objExists(jnt_nam):
                        sel_lis.append(jnt_nam)
                    else:
                        fp('关节{}不存在。'.format(jnt_nam), warning=True)
            if sel_lis:
                mc.select(sel_lis)
                fp('已选中修型关节。', info=True)
            else:
                fp('场景中没有添加的双手修型关节。', error=True)


def openAdvTool():
    try:
        ADVToolswindow.close()
        ADVToolswindow.deleteLater()
    except:
        pass
    finally:
        ADVToolswindow = ADVTools()
        ADVToolswindow.show()
