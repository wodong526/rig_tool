# -*- coding:GBK -*- 
import maya.cmds as mc
import pymel.core as pm
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def clear_orig():
    sel_lis = mc.ls(sl = 1)
    for obj in sel_lis:
        for sub_node in mc.listRelatives(obj, ad = True):
            if 'Orig' in sub_node:
                mc.delete(sub_node)
                log.info('ģ��{}��orig�ڵ�{}��ɾ����'.format(obj, sub_node))
                continue
    


def freeze_rotation():
    objs = pm.selected()
    for obj in objs:
        if isinstance(obj, pm.nt.Joint):
            rot = obj.rotate.get()
            ra = obj.rotateAxis.get()
            jo = obj.jointOrient.get()
            rotMatrix = pm.dt.EulerRotation(rot, unit = 'degrees').asMatrix()
            raMatrix = pm.dt.EulerRotation(ra, unit = 'degrees').asMatrix()
            joMatrix = pm.dt.EulerRotation(jo, unit = 'degrees').asMatrix()
            rotationMatrix = rotMatrix * raMatrix * joMatrix
            tmat = pm.dt.TransformationMatrix(rotationMatrix)
            newRotation = tmat.eulerRotation()
            newRotation = [ pm.dt.degrees(x) for x in newRotation.asVector() ]
            obj.rotate.set(0, 0, 0)
            obj.rotateAxis.set(0, 0, 0)
            obj.jointOrient.set(newRotation)
            log.info('{}����ת�Ѷ��ᡣ'.format(obj))
            continue

def select_skinJoint():
    sel_lis = mc.ls(sl = 1)
    jnt_lis = []
    for mod in sel_lis:
        for obj in mc.listHistory(mod, af=True):
            if mc.nodeType(obj) == 'skinCluster':
                for jnt in mc.skinCluster(obj, inf=1, q=1):
                    if jnt not in jnt_lis:
                        jnt_lis.append(jnt)
    if jnt_lis:
        mc.select(jnt_lis)
        log.info('��ѡ����Ƥ�ؽڡ�')
    else:
        log.error('ѡ�ж���û����Ƥ�ؽڡ�')
        
def get_length():
    obj = mc.ls(sl=True, fl=True)
    n = len(obj)
    log.info('ѡ�ж����У�{}��������Ϊ��{}��'.format(n, obj))
        
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class SameName(QtWidgets.QDialog):
    def __init__(self, parent = maya_main_window()):
        super(SameName, self).__init__(parent)

        self.setWindowTitle(u'ѡ��ͬ���ڵ�')
        if mc.about(ntOS = True):#�ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#ɾ�������ϵİ�����ť
        elif mc.about(macOS = True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()
    
    def create_widgets(self):
        self.lin_name = QtWidgets.QLineEdit()
        self.lin_name.setAttribute(QtCore.Qt.WA_AcceptDrops)
        self.lin_name.setAlignment(QtCore.Qt.AlignCenter)
        self.lin_name.setPlaceholderText(u'������Ҫѡ��Ķ�����')
        
        validator = QtGui.QRegExpValidator(self)
        validator.setRegExp(QtCore.QRegExp('[a-zA-Z|][a-zA-Z0-9_:|]+'))
        self.lin_name.setValidator(validator)
    
    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.lin_name)
    
    def create_connections(self):
        self.lin_name.returnPressed.connect(self.select_same)
    
    def select_same(self):
        sel_lis = mc.ls(l=True)
        same_lis = []
        for obj in sel_lis:
            obj_lis = obj.split('|')
            if obj_lis[-1] == self.lin_name.text():
                same_lis.append(obj)
        mc.select(same_lis)
        log.info('��ѡ��ͬ���ڵ�{}��'.format(same_lis))
        self.close()
    
    def closeEvent(self, event):
        self.close()
        self.deleteLater()

def showSameNameWindow():
    try:
        sameNamewindow.close()
        sameNamewindow.deleteLater()
    except:
        pass
    finally:
        sameNamewindow = SameName()
        sameNamewindow.show()

def exportSelectToFbx():
    '''
    ��ѡ�еĶ��󵼳�Ϊfbx���жϿ��ؽ�������������ӡ�
    '''
    sel_lis = mc.ls(sl=1)
    if sel_lis:
        for inf in sel_lis:
            try:
                mc.parent(inf, w=True)
            except:
                log.warning('{}�Ѿ�������㼶�¡�'.format(inf))
            finally:
                if mc.listConnections(inf, d=False):
                    node_lis = mc.listConnections(inf, d=False, c=1, p=1)
                    for n in range(len(node_lis) / 2):
                        mc.disconnectAttr(node_lis[n*2+1], node_lis[n*2])
                        log.info('�ѶϿ�{}��'.format(node_lis[n*2+1]))

        mc.select(sel_lis)
        file_path = QtWidgets.QFileDialog.getSaveFileName(maya_main_window(), u'ѡ��fbx�ļ�', mc.file(exn=True, q=True), '(*.fbx)')
        if file_path[0]:
            mc.file(file_path[0], f=True, typ='FBX export', pr=True, es=True)
            log.info('�ѵ���{}��'.format(sel_lis))
        else:
            log.error('û��ѡ����Ч·����')
    else:
        log.error('û��ѡ����Ч����')


