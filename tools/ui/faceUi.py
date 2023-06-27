# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui

from feedback_tool import Feedback_info as fb_print
from dutils import ctrlUtils, blendShapeUtils
import rig_tool

reload(rig_tool)
reload(blendShapeUtils)

from ast import literal_eval
from functools import partial


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class FaceWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(FaceWindow, self).__init__(parent)

        self.setWindowTitle(u'绑脸窗口')
        if mc.about(ntOS=True):  #判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.lin_nam = QtWidgets.QLineEdit()
        self.lin_nam.setPlaceholderText(u'对象名')
        self.lin_typ = QtWidgets.QLineEdit()
        self.lin_typ.setPlaceholderText(u'控制器类型名')
        self.spn_num = QtWidgets.QSpinBox()
        self.spn_num.setMinimum(1)
        self.but_createCtl = QtWidgets.QPushButton(u'创建控制器')

        self.lin_modNam = QtWidgets.QLineEdit()
        self.lin_modNam.setPlaceholderText(u'被打毛囊的模型名')
        self.but_foll = QtWidgets.QPushButton(u'根据选择对象创建毛囊')

        self.lin_rbf = QtWidgets.QLineEdit()
        self.lin_rbf.setPlaceholderText(u'rbf名字')
        self.but_rbf = QtWidgets.QPushButton(u'创建八方向小球')

        self.lin_BSgeo_nam = QtWidgets.QLineEdit()
        self.lin_BSgeo_nam.setPlaceholderText(u'要生成bs的模型名')
        self.lin_BS_nam = QtWidgets.QLineEdit()
        self.lin_BS_nam.setPlaceholderText(u'要生成bs的名字')
        self.but_createBS = QtWidgets.QPushButton(u'创建bs')

        self.lin_bsWeight = QtWidgets.QLineEdit()
        self.lin_bsWeight.setPlaceholderText(u'bs名称')
        self.lin_ctlAttr = QtWidgets.QLineEdit()
        self.lin_ctlAttr.setPlaceholderText(u'控制器及属性名称')
        self.lin_val = QtWidgets.QLineEdit()
        self.lin_val.setPlaceholderText(u'(驱动的值, )')
        self.but_create = QtWidgets.QPushButton(u'创建对应')

        self.but_disCont = QtWidgets.QPushButton(u'断开控制器与bsHandl链接')
        self.but_reCont = QtWidgets.QPushButton(u'刷新控制器与bsHandl链接')
        self.but_impCont = QtWidgets.QPushButton(u'导入控制器与bsHandl信息')
        self.but_expCont = QtWidgets.QPushButton(u'导出控制器与bsHandl信息')

    def create_layout(self):
        layout_ctl = QtWidgets.QHBoxLayout()
        layout_ctl.addWidget(self.lin_nam)
        layout_ctl.addWidget(self.lin_typ)
        layout_ctl.addWidget(self.spn_num)
        layout_ctl.addWidget(self.but_createCtl)

        layout_foll = QtWidgets.QHBoxLayout()
        layout_foll.addWidget(self.lin_modNam)
        layout_foll.addWidget(self.but_foll)

        layout_rbf = QtWidgets.QHBoxLayout()
        layout_rbf.addWidget(self.lin_rbf)
        layout_rbf.addWidget(self.but_rbf)

        layout_create_bs = QtWidgets.QHBoxLayout()
        layout_create_bs.addWidget(self.lin_BSgeo_nam)
        layout_create_bs.addWidget(self.lin_BS_nam)
        layout_create_bs.addWidget(self.but_createBS)

        layout_bsLink = QtWidgets.QHBoxLayout()
        layout_bsLink.addWidget(self.lin_bsWeight)
        layout_bsLink.addWidget(self.lin_ctlAttr)
        layout_bsLink.addWidget(self.lin_val)
        layout_bsLink.addWidget(self.but_create)

        layout_bsInfo = QtWidgets.QHBoxLayout()
        layout_bsInfo.addWidget(self.but_disCont)
        layout_bsInfo.addWidget(self.but_reCont)
        layout_bsInfo.addWidget(self.but_expCont)
        layout_bsInfo.addWidget(self.but_impCont)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(layout_ctl)
        main_layout.addLayout(layout_foll)
        main_layout.addLayout(layout_rbf)
        main_layout.addLayout(layout_create_bs)
        main_layout.addLayout(layout_bsLink)
        main_layout.addLayout(layout_bsInfo)

    def create_connections(self):
        self.but_createCtl.clicked.connect(self.createCtl)
        self.but_foll.clicked.connect(self.createFoll)
        self.but_rbf.clicked.connect(self.createRBF)
        self.but_createBS.clicked.connect(self.createBS)
        self.but_create.clicked.connect(self.createCtrlBs)
        self.but_disCont.clicked.connect(partial(self.bsHandl_control, 'disCont'))
        self.but_reCont.clicked.connect(partial(self.bsHandl_control, 'reCont'))
        self.but_impCont.clicked.connect(partial(self.bsHandl_control, 'impCont'))
        self.but_expCont.clicked.connect(partial(self.bsHandl_control, 'expCont'))

    def createCtl(self):
        nam = self.lin_nam.text()
        side = int(self.spn_num.text())
        typ = self.lin_typ.text()

        ctl_lis = []
        if side == 1:
            ctl_lis.append(ctrlUtils.create_ctl(nam + '_m', cid=typ, color=22))
        elif side == 2:
            ctl_lis.append(ctrlUtils.create_ctl(nam + '_l', cid=typ, color=6))
            ctl_lis.append(ctrlUtils.create_ctl(nam + '_r', cid=typ, color=13))

        for ctl in ctl_lis:
            zero = ctrlUtils.fromObjCreateGroup(ctl[5:-4], 'ctrl', ctl)[0][0]

            if '_r_' in ctl:
                mc.setAttr(zero + '.ry', 180)
                mc.setAttr(zero + '.sz', -1)

            off = mc.listRelatives(zero)[0]
            grp = mc.group(p=zero, n='con_{}'.format(ctl[5:]), em=1)
            mc.matchTransform(grp, zero)
            mc.parent(off, grp)

    def createFoll(self):
        sel_lis = mc.ls(sl=1)

        for grp in sel_lis:
            nam = grp[5:-4]

            foll = rig_tool.createFollicle(self.lin_modNam.text(), grp, nam)
            mc.pointConstraint(foll, 'zero_{}_001'.format(nam), mo=True)

    def createRBF(self):
        nam = self.lin_rbf.text()
        rig_tool.create_shape_helper(nam)

    def createBS(self):
        geo = self.lin_BSgeo_nam.text()
        bsNam = self.lin_BS_nam.text()
        bs = blendShapeUtils.create_blendshape(geo, bsNam)

        blendShapeUtils.BSWeights(bs, 'trs_{}_whMaster'.format(bs))

    def createCtrlBs(self):
        bs_weight_nam = self.lin_bsWeight.text()
        ctrl_attr = self.lin_ctlAttr.text()
        val = self.lin_val.text()
        bs = self.lin_BS_nam.text()
        if not bs:
            fb_print('没有输入BS名称', error=True)
        weights_handle = mc.listConnections('{}.weightsHandle'.format(bs), s=False)[0]
        self.wh = blendShapeUtils.BSWeights(bs, weights_handle)
        self.wh.set_bs_weight_attr(bs_weight_nam, ctrl_attr, literal_eval(val))

    def bsHandl_control(self, typ):
        bs = self.lin_BS_nam.text()
        try:
            weights_handle = mc.listConnections('{}.weightsHandle'.format(bs), s=False)[0]
            self.wh = blendShapeUtils.BSWeights(bs, weights_handle)
        except:
            self.wh = blendShapeUtils.BSWeights(bs, None)

        if typ == 'disCont':
            self.wh.disconnect_ctrls_to_bsHandl()
        elif typ == 'reCont':
            self.wh.reconnect_ctrls_to_bsHandl()
        elif typ == 'impCont':
            self.wh.import_connections()
        elif typ == 'expCont':
            self.wh.export_connections()


try:
    my_window.close()
    my_window.deleteLater()
except:
    pass
finally:
    my_window = FaceWindow()
    my_window.show()
