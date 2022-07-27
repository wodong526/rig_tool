# -*- coding:GBK -*- 
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui

import os
import functools

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class create_ctl(QtWidgets.QDialog):#使该窗口为控件
    def __init__(self, parent = maya_main_window()):
        super(create_ctl, self).__init__(parent)

        self.setWindowTitle(u'控制器生成器')
        if mc.about(ntOS = True):#判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#删除窗口上的帮助按钮
        elif mc.about(macOS = True):
            self.setWindowFlags(QtCore.Qt.Tool)
        
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        self.setMaximumSize(430, 450)
        self.setMinimumSize(430, 450)

        self.create_widgets()
        self.create_layout()
        self.create_connections()
    
    def create_widgets(self):
        ctl_lis = self.get_ctl_bmp()
        self.button_lis = []
        for i in range(len(ctl_lis)):
            button = QtWidgets.QPushButton(ctl_lis[i].split('.')[0])
            button.setIcon(QtGui.QIcon('{}{}'.format(self.ctl_path, ctl_lis[i])))
            button.setIconSize(QtCore.QSize(32, 32))
            button.clicked.connect(functools.partial(self.reade_ctl, ctl_lis[i].split('.')[0]))
            self.button_lis.append(button)
    
    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addStretch()
        for h in range(len(self.button_lis) / 6 + 1):
            h_layout = QtWidgets.QHBoxLayout()
            for v in range(6):
                if h * 6 + v > 64:
                    break
                h_layout.addWidget(self.button_lis[h * 6 + v])
                h_layout.addStretch()
            main_layout.addLayout(h_layout)
            main_layout.setContentsMargins(2, 2, 2, 2)
            
    
    def create_connections(self):
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
        point = self.replace_str(con)

        mc.curve(d = 1, p = point)
    
    def replace_str(self, s):
        pos = []
        for h in s.split('\n'):
            pot_lis = h.split(' ')
            a = []
            for i in pot_lis:
                a.append(float(i))
            pos.append(a)

        return pos


try:
    my_window.close()
    my_window.deleteLater()
except:
    pass
finally:
    my_window = create_ctl()
    my_window.show()