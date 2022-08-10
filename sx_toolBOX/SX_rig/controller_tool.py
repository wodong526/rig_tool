# -*- coding:GBK -*- 
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.mel as mel
import maya.OpenMayaUI as omui

import os
import math
import functools
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
class myLabel(QtWidgets.QLabel):
    
    doubleClickSig = QtCore.Signal(int)
    
    def __init__(self, name):
        super(myLabel, self).__init__()
        self.name = name
    
    def mouseDoubleClickEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            self.doubleClickSig.emit(self.name)


class create_ctl(QtWidgets.QDialog):#使该窗口为控件
    def __init__(self, parent = maya_main_window()):
        super(create_ctl, self).__init__(parent)

        self.setWindowTitle(u'控制器生成器_V1.1')
        if mc.about(ntOS = True):#判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#删除窗口上的帮助按钮
        elif mc.about(macOS = True):
            self.setWindowFlags(QtCore.Qt.Tool)
        
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        self.setMaximumSize(800, 610)
        self.setMinimumHeight(600)
        
        self.create_widgets()
        self.create_layout()
        self.create_connections()
    
    def create_widgets(self):
        self.copy_but = QtWidgets.QPushButton(u'复制控制器形态')
        self.paste_but = QtWidgets.QPushButton(u'粘贴控制器形态')
        self.ctl_lin = QtWidgets.QLineEdit()
        self.ctl_lin.setEnabled(False)
        
        self.mir_but = QtWidgets.QPushButton(u'镜像控制器')
        self.spa_comb = QtWidgets.QComboBox()
        self.spa_comb.addItems([u'对象', u'世界'])
        self.aix_comb = QtWidgets.QComboBox()
        self.aix_comb.addItems(['X', 'Y', 'Z'])
        
        self.grp_but = QtWidgets.QPushButton(u'生成父级组')
        self.grp_lin = QtWidgets.QLineEdit()
        reg = QtCore.QRegExp('[a-zA-Z0-9_]+')
        validator = QtGui.QRegExpValidator(self)
        validator.setRegExp(reg)
        self.grp_lin.setValidator(validator)
        
        self.all_color_but = QtWidgets.QPushButton(u'更多颜色')
        self.all_color_but.setMaximumSize(62, 30)
        
        ctl_lis = self.get_ctl_bmp()
        self.button_lis = []
        for i in range(len(ctl_lis)):
            button = QtWidgets.QPushButton(ctl_lis[i].split('.')[0])
            button.setMaximumSize(55, 55)
            button.setIcon(QtGui.QIcon('{}{}'.format(self.ctl_path, ctl_lis[i])))
            button.setIconSize(QtCore.QSize(25, 25))
            button.clicked.connect(functools.partial(self.reade_ctl, ctl_lis[i].split('.')[0]))
            self.button_lis.append(button)
        
        self.color_lab = {}
        for i in range(1, 32):
            color = mc.colorIndex(i, q = True)
            label = myLabel(i)
            pix = QtGui.QPixmap(30, 30)
            pix.fill(QtGui.QColor.fromRgbF(color[0], color[1], color[2]))
            label.setPixmap(pix)
            label.doubleClickSig.connect(self.get_color)
            self.color_lab['label_{}'.format(i)] = label
    
    def create_layout(self):
        copyCtl_layout = QtWidgets.QHBoxLayout()
        copyCtl_layout.addWidget(self.copy_but)
        copyCtl_layout.addWidget(self.ctl_lin)
        copyCtl_layout.addWidget(self.paste_but)
        
        mirror_layout = QtWidgets.QHBoxLayout()
        mirror_layout.addWidget(self.mir_but)
        mirror_layout.addWidget(self.spa_comb)
        mirror_layout.addWidget(self.aix_comb)
        
        grp_layout = QtWidgets.QHBoxLayout()
        grp_layout.addWidget(self.grp_but)
        grp_layout.addWidget(self.grp_lin)
        
        lable_layout = QtWidgets.QVBoxLayout()
        ind = 1
        for i in range(3):
            h_lab_layout = QtWidgets.QHBoxLayout()
            for n in range(11):
                if ind == 32:
                    h_lab_layout.addWidget(self.all_color_but)
                    break
                h_lab_layout.addWidget(self.color_lab['label_{}'.format(ind)])
                ind += 1
            h_lab_layout.addStretch()
            lable_layout.addLayout(h_lab_layout)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setObjectName('master')
        main_layout.addStretch()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.addLayout(copyCtl_layout)
        main_layout.addLayout(mirror_layout)
        main_layout.addLayout(grp_layout)
        main_layout.addLayout(lable_layout)
        main_layout.addWidget(self.add_maya_widget(main_layout.objectName()))
        for h in range(int(math.ceil(len(self.button_lis) / 6.0))):
            h_layout = QtWidgets.QHBoxLayout()
            for v in range(6):
                h_layout.addWidget(self.button_lis[h * 6 + v])
                h_layout.addStretch()
            main_layout.addLayout(h_layout)   
    
    def create_connections(self):
        self.copy_but.clicked.connect(self.copy_shape)
        self.paste_but.clicked.connect(self.past_shape)
        self.mir_but.clicked.connect(self.mirror_ctl)
        self.grp_but.clicked.connect(self.create_grp)
        self.all_color_but.clicked.connect(self.get_all_color)
    
    def add_maya_widget(self, name):
        mc.setParent(name)
        self.sliderGrp = mc.colorSliderGrp(rgb = [1, 1, 0.122], cc = self.set_ctl_color)
        ptr = omui.MQtUtil.findControl(self.sliderGrp)
        colLayout = wrapInstance(int(ptr), QtWidgets.QWidget)
        return colLayout
    
    def get_color(self, *args):
        color = mc.colorIndex(args[0], q = True)
        self.set_ctl_color(color)
    
    def set_ctl_color(self, color):
        sel_cv = self.if_cv()
        if type(sel_cv) == unicode:
            cv_shape = mc.listRelatives(sel_cv, s = True)[0]
            if type(color) == list:
                mc.setAttr('{}.overrideEnabled'.format(cv_shape), 1)
                mc.setAttr('{}.overrideRGBColors'.format(cv_shape), 1)
                mc.setAttr('{}.overrideColorRGB'.format(cv_shape), color[0], color[1], color[2])
                mc.colorSliderGrp(self.sliderGrp, rgb = color, e = True)
            elif type(color) == unicode:
                ctl_rgb = mc.colorSliderGrp(self.sliderGrp, q = True, rgb = True)
                mc.setAttr('{}.overrideEnabled'.format(cv_shape), 1)
                mc.setAttr('{}.overrideRGBColors'.format(cv_shape), 1)
                mc.setAttr('{}.overrideColorRGB'.format(cv_shape), ctl_rgb[0], ctl_rgb[1], ctl_rgb[2])
            else:
                pass
        else:
            pass
    
    def get_ctl_bmp(self):
        self.ctl_path = mc.internalVar(uad = True) + mc.about(v = True) + "/scripts/sx_toolBOX/SX_rig/data/ControllerFiles/"
        bmp_lis = []
        for f in os.listdir(self.ctl_path):
            if os.path.splitext(f)[-1] == '.bmp':
                bmp_lis.append(f)
        return bmp_lis
    
    def reade_ctl(self, n):
        with open('{}{}.cs'.format(self.ctl_path, str(n)), 'r') as f:
            con = f.read()
        trs = mc.createNode('transform', n = 'nurbsCurve')
        mc.createNode('nurbsCurve', p = trs)
        mel.eval(con)
        mc.select(mc.listRelatives(mc.ls(sl = True), p = True))
        self.set_ctl_color('dong')
    
    def create_grp(self):
        sel_cv = self.if_cv()
        if type(sel_cv) == unicode:
            pos = mc.xform(sel_cv, t = True, q = True, ws = True)
            rot = mc.xform(sel_cv, ro = True, q = True, ws = True)
            scl = mc.xform(sel_cv, s = True, q = True, ws = True)
            name = self.grp_lin.text()
            ctl_name = mc.rename(sel_cv, 'ctl_{}_001'.format(name))
            grp = mc.group(em = True, n = 'zero_{}_001'.format(name))
            grpOffset = mc.group(em = True, p = grp, n = 'Offset_{}_001'.format(name))
            mc.xform(grp, t = pos, ro = rot, s = scl, ws = True)
            mc.parent(ctl_name, grpOffset)
            mc.select(grp)
    
    def get_all_color(self):
        mc.colorEditor()
        if mc.colorEditor(q = 1, r = 1):
            color = mc.colorEditor(q = 1, rgb = 1)
            if color:
                self.set_ctl_color(color)
    def if_cv(self):
        sel_cv = mc.ls(sl = True)
        if len(sel_cv) == 1:
            cv_shape = mc.listRelatives(sel_cv[0], s = True)
            if cv_shape == None:
                log.error('选择对象没有shape节点。')
                return False
            elif mc.nodeType(cv_shape[0]) == 'nurbsCurve':
                return sel_cv[0]
            else:
                log.error('选择对象应为曲线。')
                return False
        else:
            log.error('应选择1个对象，实际选择{}。'.format(len(sel_cv)))
            return False
    
    def mirror_ctl(self):
        spa = self.spa_comb.currentIndex()
        aix = self.aix_comb.currentIndex()
        if spa == 0:
            if aix == 0:
                self.for_mir(0, 0)
            elif aix == 1:
                self.for_mir(0, 1)
            elif aix == 2:
                self.for_mir(0, 2)
        elif spa == 1:
            if aix == 0:
                self.for_mir(1, 0)
            elif aix == 1:
                self.for_mir(1, 1)
            elif aix == 2:
                self.for_mir(1, 2)
    
    def for_mir(self, t, i):
        ctl_cv = self.if_cv()
        if type(ctl_cv) == unicode:
            spa_n = mc.getAttr('{}.spans'.format(ctl_cv)) 
            deg_n = mc.getAttr('{}.degree'.format(ctl_cv))
            cv_n = spa_n + deg_n
            
            if t == 0:
                for n in range(cv_n):
                    old_pos = mc.xform('{}.cv[{}]'.format(ctl_cv, n), os = True, q = True, t = True)
                    old_pos[i] = old_pos[i] * -1
                    mc.xform('{}.cv[{}]'.format(ctl_cv, n), os = True, t = old_pos)
            elif t == 1:
                for n in range(cv_n):
                    old_pos = mc.xform('{}.cv[{}]'.format(ctl_cv, n), ws = True, q = True, t = True)
                    old_pos[i] = old_pos[i] * -1
                    mc.xform('{}.cv[{}]'.format(ctl_cv, n), ws = True, t = old_pos)
    
    def copy_shape(self):
        ctl_cv = self.if_cv()
        if type(ctl_cv) == unicode:
            self.ctl_lin.setText(ctl_cv)
    
    def past_shape(self):
        ctl_cv = self.if_cv()
        if type(ctl_cv) == unicode:
            if self.ctl_lin.text():
                ctl = self.ctl_lin.text()
                dup_cv = mc.duplicateCurve(ctl, ch = False, n = 'dup_cv')[0]
                old_name = mc.listRelatives(ctl_cv, s = True)
                mc.delete(old_name)
                new_name = mc.rename(mc.listRelatives(dup_cv, s = True), old_name)
                mc.parent(new_name, ctl_cv, s = True, r = True)
                mc.delete(dup_cv)
                log.info('已copy控制器形态到{}。'.format(ctl_cv))
            else:
                log.error('未复制任何控制形态。')
                return False



try:
    my_window.close()
    my_window.deleteLater()
except:
    pass
finally:
    my_window = create_ctl()
    my_window.show()