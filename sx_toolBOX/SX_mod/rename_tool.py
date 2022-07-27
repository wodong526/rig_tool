# -*- coding:GBK -*- 
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui

import string
import copy
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class RenameWindow(QtWidgets.QDialog):
    def __init__(self, parent = maya_main_window()):
        super(RenameWindow, self).__init__(parent)

        self.setWindowTitle(u'重命名工具')
        if mc.about(ntOS = True):#判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#删除窗口上的帮助按钮
        elif mc.about(macOS = True):
            self.setWindowFlags(QtCore.Qt.Tool)
        self.setContentsMargins(2, 2, 2, 2)

        self.create_widgets()
        self.create_layout()
        self.create_connections()
    
    def create_widgets(self):
        self.sel_mod = QtWidgets.QPushButton(u'选择子级所有模型')
        
        self.front_line = QtWidgets.QLineEdit()
        self.behind_line = QtWidgets.QLineEdit()
        self.whole_line = QtWidgets.QLineEdit()
        
        self.frame_A = QtWidgets.QFrame()
        self.frame_A.setFrameShape(QtWidgets.QFrame.HLine)
        self.frame_B = QtWidgets.QFrame()
        self.frame_B.setFrameShape(QtWidgets.QFrame.HLine)
        
        self.replace_lable = QtWidgets.QLabel(u'替换')
        self.replace_noumenon_line = QtWidgets.QLineEdit()
        self.replace_noumenon_line.setPlaceholderText(u'将')
        self.replace_target_line = QtWidgets.QLineEdit()
        self.replace_target_line.setPlaceholderText(u'替换成')
        
        self.num_label = QtWidgets.QLabel(u'类型')
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(['1,2,3~', 'A,B,C~', 'a,b,c~'])
        self.start_line = QtWidgets.QLineEdit()
        self.start_line.setValidator(QtGui.QIntValidator(0, 9999))
        self.step_line = QtWidgets.QLineEdit()
        self.step_line.setValidator(QtGui.QIntValidator(0, 9999))
        self.run_but = QtWidgets.QPushButton(u'R U N')
    
    def create_layout(self):
        increase_layout = QtWidgets.QFormLayout()
        increase_layout.addRow(u'前缀', self.front_line)
        increase_layout.addRow(u'后缀', self.behind_line)
        increase_layout.addRow(u'全部', self.whole_line)
        
        replace_layout = QtWidgets.QHBoxLayout()
        replace_layout.addWidget(self.replace_lable)
        replace_layout.addWidget(self.replace_noumenon_line)
        replace_layout.addWidget(self.replace_target_line)
        
        num_layout = QtWidgets.QFormLayout()
        num_layout.addRow(self.num_label, self.type_combo)
        num_layout.addRow(u'初始', self.start_line)
        num_layout.addRow(u'步长', self.step_line)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.sel_mod)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addLayout(increase_layout)
        main_layout.addWidget(self.frame_A)
        main_layout.addLayout(replace_layout)
        main_layout.addWidget(self.frame_B)
        main_layout.addLayout(num_layout)
        main_layout.addWidget(self.run_but)
    
    def create_connections(self):
        self.sel_mod.clicked.connect(self.select_mod)
        self.type_combo.activated.connect(self.num_change)
        self.run_but.clicked.connect(self.rename_obj)
    
    def select_mod(self):
        '''
        判断选择对象
        '''
        sel = mc.ls(sl = 1)
        mod_lis = []
        if len(sel) > 1:
            for single in sel:
                for trs in mc.listRelatives(single, ad = True):
                    if mc.nodeType(trs) == 'mesh':
                        mod_lis.append(mc.listRelatives(trs, p = True)[0])
            log.warning('虽然非常不建议选择多个层级下的物体改名，但我还是帮你选中他们了。')
        elif len(sel) == 1:
            for trs in mc.listRelatives(sel, ad = True):
                if mc.nodeType(trs) == 'mesh':
                    mod_lis.append(mc.listRelatives(trs, p = True)[0])
            log.info('已选中{}下所有模型对象。'.format(sel[0]))
        else:
            log.error('选择对象为空。')
        mc.select(mod_lis)
    
    def num_change(self, *arg):
        '''
        使用不同编号类型时，在起始和步长栏里编写初始内容
        '''
        if arg[0] == 1:
            self.start_line.setText('A')
            self.start_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[A-Z]')))
            self.step_line.setReadOnly(True)
        elif arg[0] == 2:
            self.start_line.setText('a')
            self.start_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[a-z]')))
            self.step_line.setReadOnly(True)
        else:
            self.start_line.setText('1')
            self.step_line.setText('1')
            self.step_line.setReadOnly(False)
    
    def rename_obj(self):
        '''
        按从上到下的顺序累加命名
        '''
        sel_lis = mc.ls(sl = True)
        ren_lis = copy.copy(sel_lis)
        
        dup_lis = copy.copy(sel_lis)
        for i in range(len(sel_lis)):
            dup_lis.remove(dup_lis[0])
            if sel_lis[i] in dup_lis:
                log.warning('选择对象中的{}重复，请先清理选中对象中的重命名。'.format(sel_lis[i]))
        
        if self.front_line.text():
            ren_lis = self.front_ren(ren_lis)
        if self.behind_line.text():
            ren_lis = self.behind_ren(ren_lis)
        if self.whole_line.text():
            ren_lis = self.whole_ren(ren_lis)
        if self.replace_noumenon_line.text():
            ren_lis = self.replace_ren(ren_lis)
        if self.start_line.text():
            ren_lis = self.number_ren(ren_lis)
        
        for n in range(len(sel_lis)):
            mc.rename(sel_lis[n], ren_lis[n])
    
    def front_ren(self, sel):
        front = self.front_line.text()
        ret_lis = []
        for obj in sel:
            ret_lis.append(front + obj)
        
        return ret_lis
    
    def behind_ren(self, sel):
        behind = self.behind_line.text()
        ret_lis = []
        for obj in sel:
            ret_lis.append(obj + behind)
        
        return ret_lis
    
    def whole_ren(self, sel):
        whole = self.whole_line.text()
        ret_lis = []
        for obj in sel:
            ret_lis.append(whole)
        
        return ret_lis
    
    def replace_ren(self, sel):
        noumenon = self.replace_noumenon_line.text()
        target = self.replace_target_line.text()
        ret_lis = []
        for obj in sel:
            if noumenon in obj:
                ret_lis.append(obj.replace(noumenon, target))
            else:
                log.info('{}对象没有{}，已跳过。'.format(obj, noumenon))
                ret_lis.append(obj)
        return ret_lis
    
    def number_ren(self, sel):
        type_com = self.type_combo.currentIndex()
        ret_lis = []
        if type_com == 0:
            start = int(self.start_line.text())
            step_t = self.step_line.text()
            if step_t:
                step = int(step_t)
            else:
                step = 1
            for obj in sel:
                ret_lis.append('{}{}'.format(obj, start))
                start += step
        elif type_com == 1:
            start = self.start_line.text()
            letter_lis = list(string.ascii_uppercase)
            letter_ind = letter_lis.index(start)
            for obj in sel:
                ret_lis.append(obj + letter_lis[letter_ind])
                letter_ind += 1
                if letter_ind == 26:
                    letter_ind = 0
        elif type_com == 2:
            start = self.start_line.text()
            letter_lis = list(string.ascii_lowercase)
            letter_ind = letter_lis.index(start)
            for obj in sel:
                ret_lis.append(obj + letter_lis[letter_ind])
                letter_ind += 1
                if letter_ind == 26:
                    letter_ind = 0
        return ret_lis
    

try:
    my_window.close()
    my_window.deleteLater()
except:
    pass
finally:
    my_window = RenameWindow()
    my_window.show()