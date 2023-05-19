# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm
import pymel.core as pm
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import traceback

from feedback_tool import Feedback_info as fb_print
from dutils import clearUtils, ctrlutils, skinUtils

FILE_PATH = __file__


def LIN():
    line_number = traceback.extract_stack()[-2][1]
    return line_number


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def freeze_rotation():
    objs = pm.selected()
    for obj in objs:
        if isinstance(obj, pm.nt.Joint):
            rot = obj.rotate.get()
            ra = obj.rotateAxis.get()
            jo = obj.jointOrient.get()
            rotMatrix = pm.dt.EulerRotation(rot, unit='degrees').asMatrix()
            raMatrix = pm.dt.EulerRotation(ra, unit='degrees').asMatrix()
            joMatrix = pm.dt.EulerRotation(jo, unit='degrees').asMatrix()
            rotationMatrix = rotMatrix * raMatrix * joMatrix
            tmat = pm.dt.TransformationMatrix(rotationMatrix)
            newRotation = tmat.eulerRotation()
            newRotation = [pm.dt.degrees(x) for x in newRotation.asVector()]
            obj.rotate.set(0, 0, 0)
            obj.rotateAxis.set(0, 0, 0)
            obj.jointOrient.set(newRotation)
            fb_print('{}����ת�Ѷ��ᡣ'.format(obj), info=True)
            continue


def select_skinJoint():
    """
    ͨ��ѡ�е�ģ�ͻ�ȡ��ģ�͵���Ƥ�ؽ�
    :return:
    """
    sel_lis = mc.ls(sl=1)
    jnt_lis = []
    for mod in sel_lis:
        skin = mm.eval('findRelatedSkinCluster("{}")'.format(mod))
        for jnt in mc.skinCluster(skin, inf=1, q=1):
            if jnt not in jnt_lis:
                jnt_lis.append(jnt)
    if jnt_lis:
        mc.select(jnt_lis)
        fb_print('��ѡ����Ƥ�ؽڡ�', info=True)
    else:
        fb_print('ѡ�ж���û����Ƥ�ؽڡ�', error=True)


def get_length():
    obj = mc.ls(sl=True, fl=True)
    n = len(obj)
    fb_print('ѡ�ж����У�{}��������Ϊ��{}��'.format(n, obj), info=True)


class SameName(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(SameName, self).__init__(parent)

        self.setWindowTitle(u'ѡ��ͬ���ڵ�')
        if mc.about(ntOS=True):  # �ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.lin_name = QtWidgets.QLineEdit()
        self.lin_name.setAttribute(QtCore.Qt.WA_AcceptDrops)
        self.lin_name.setAlignment(QtCore.Qt.AlignCenter)
        self.lin_name.setPlaceholderText(u'������Ҫѡ��Ķ�����')

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
        fb_print('��ѡ��ͬ���ڵ�{}��'.format(same_lis), info=True)
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
    """
    ��ѡ�еĶ��󵼳�Ϊfbx���жϿ��ؽ�������������ӡ�
    """
    sel_lis = mc.ls(sl=1)
    if sel_lis:

        #�ȼ��ģ������û��ë��ģ��
        obj_lis = []
        hair_lis = []
        for obj in sel_lis:
            for inf in mc.listRelatives(obj, ad=True):
                obj_lis.append(inf)
        if obj_lis:
            for obj in obj_lis:
                if 'Hair' in obj or 'hair' in obj:
                    if not mc.nodeType(obj) == 'joint':
                        hair_lis.append(obj)
        if hair_lis:
            resout = mc.confirmDialog(title='���棺', message='{}\n������ë��ģ�ͣ�Ӧ��ɾ����'.format(hair_lis),
                                      button=['ȡ������', '��������'])
            if resout == u'ȡ������':
                return None
            elif resout == u'��������':
                pass

        namSpas, namSpas_lis = clearUtils.clear_nameSpace(q=True)  #���������пռ���ʱ��ʾ
        if namSpas:
            resout = mc.confirmDialog(title='���棺', button=['����ռ������ٵ���', '������ֱ�ӵ���', 'ȡ��'],
                                      message='�������пռ����ƣ�\n{}\n�Ƿ�������ٵ�����ֱ�ӵ�����'.format(
                                          '\n'.join(namSpas_lis)))
            if resout == u'����ռ������ٵ���':
                clearUtils.clear_nameSpace()
            elif resout == u'������ֱ�ӵ���':
                pass
            else:
                return None

        file_path = mc.file(exn=True, q=True)
        file_nam = file_path.split('/')[-1].split('.')[0]
        fbx_nam = 'SK'
        for nam in file_nam.split('_')[2:-1]:
            fbx_nam = fbx_nam + '_' + nam
        file_path = QtWidgets.QFileDialog.getSaveFileName(maya_main_window(), u'ѡ��fbx�ļ�',
                                                          file_path.replace(file_path.split('/')[-1], fbx_nam),
                                                          '(*.fbx)')  #��ȡ����fbx·��

        if file_path[0]:
            node_lis = []
            pert_dir = {}
            for inf in sel_lis:  #�Ͽ�ѡ�����ĸ����Ա��⵼�����ڶ���
                if mc.listRelatives(inf, p=True):
                    pert_dir[inf] = mc.listRelatives(inf, p=True)[0]
                    mc.parent(inf, w=True)
                else:
                    fb_print('{}��������㼶�¡�'.format(inf), info=True)

                if mc.listConnections(inf, d=False):
                    node_lis = mc.listConnections(inf, d=False, c=1, p=1)
                    for n in range(len(node_lis) / 2):
                        mc.disconnectAttr(node_lis[n * 2 + 1], node_lis[n * 2])
                        fb_print('�ѶϿ�{}��'.format(node_lis[n * 2 + 1]), info=True)

            mc.select(sel_lis)
            mc.FBXProperty('Export|IncludeGrp|Animation', '-v', '0')
            mc.file(file_path[0], f=True, typ='FBX export', pr=True, es=True)
            fb_print('�ѵ���{}��'.format(sel_lis), info=True)

            for n in range(len(node_lis) / 2):  #�����������νڵ�
                mc.connectAttr(node_lis[n * 2 + 1], node_lis[n * 2])
                fb_print('������{}��'.format(node_lis[n * 2 + 1]), info=True)
            for inf in pert_dir:  # ����p�ظ���
                mc.parent(inf, pert_dir[inf])

        else:
            fb_print('û��ѡ����Ч·����', error=True)

    else:
        fb_print('û��ѡ����Ч����', error=True)


def createRibbon(nam, ctl_n, jnt_n, foll_ctl=False):
    """
    ����������֮������ik�ؽ����Ϳ�������ʹ����������ʱ����ik
    :param foll_ctl: ���ɵ���������Ƿ�����������������������������߶���
    :param nam: ��rig������
    :param ctl_n: ����������
    :param jnt_n: ik�ؽ�����
    :return: None
    """
    sel_lis = mc.ls(sl=True)
    for cvr in sel_lis:
        if foll_ctl:
            mc.rebuildCurve(cvr, rpo=True, end=1, kr=0, kt=False, s=ctl_n - 1)
        else:
            mc.rebuildCurve(cvr, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kt=0, s=1, d=3, tol=0.01)
    surf = mc.loft(sel_lis[0], sel_lis[1], ch=False, u=True, rn=False, po=0, n='surf_{}_{:03d}'.format(nam, 1))[0]
    mc.setAttr('{}.inheritsTransform'.format(surf), False)

    crvFromSur = mc.createNode('curveFromSurfaceIso', n='crvFromSur_{}_{:03d}'.format(nam, 1))
    mc.setAttr('{}.isoparmValue'.format(crvFromSur), 0.5)
    mc.setAttr('{}.isoparmDirection'.format(crvFromSur), 1)
    lsoShape = mc.createNode('nurbsCurve', n='crv_{}_{:03d}Shape'.format(nam, 1))
    lso = mc.rename(mc.listRelatives(lsoShape, p=True), 'crv_{}_{:03d}'.format(nam, 1))
    mc.setAttr('{}.v'.format(lso), False)
    mc.connectAttr('{}.worldSpace[0]'.format(surf), '{}.inputSurface'.format(crvFromSur))
    mc.connectAttr('{}.outputCurve'.format(crvFromSur), '{}.create'.format(lsoShape))

    motPath_node = mc.createNode('motionPath', n='motPath_{}_{:03d}'.format(nam, 1))
    mc.setAttr('{}.fractionMode'.format(motPath_node), 1)
    mc.connectAttr('{}.worldSpace[0]'.format(lsoShape), '{}.geometryPath'.format(motPath_node))
    jnt_lis = []
    for i in range(1, jnt_n + 1):
        mc.select(cl=True)
        jnt = mc.joint(n='jnt_{}_{:03d}'.format(nam, i))
        mc.connectAttr('{}.allCoordinates'.format(motPath_node), '{}.translate'.format(jnt))
        mc.setAttr('{}.uValue'.format(motPath_node), (i - 1) / (jnt_n - 1.0))
        mc.disconnectAttr('{}.allCoordinates'.format(motPath_node), '{}.translate'.format(jnt))
        mc.makeIdentity(jnt, a=True, r=True)
        if jnt_lis:
            mc.parent(jnt, jnt_lis[-1])
        jnt_lis.append(jnt)

    grp_lis = []
    ctl_lis = []
    ctlJnt_lis = []
    for i in range(1, ctl_n + 1):
        ctl = ctrlutils.create_ctl('ctl_{}_{:03d}'.format(nam, i), id='C01')
        grp, ctl = ctrlutils.fromObjCreateGroup(nam, ctl)

        mc.select(cl=True)
        ctlJnt = mc.joint(n='jnt_ctl_{}_{:03d}'.format(nam, i))
        mc.setAttr('{}.v'.format(ctlJnt), False)
        mc.parent(ctlJnt, ctl[0])
        grp_lis.append(grp[0])
        ctl_lis.append(ctl[0])
        ctlJnt_lis.append(ctlJnt)

        mc.connectAttr('{}.allCoordinates'.format(motPath_node), '{}.translate'.format(grp[0]))
        mc.setAttr('{}.uValue'.format(motPath_node), (i - 1) / (ctl_n - 1.0))
        mc.disconnectAttr('{}.allCoordinates'.format(motPath_node), '{}.translate'.format(grp[0]))

    mc.joint(jnt_lis[0], e=True, oj='xyz', sao='yup', zso=True, ch=True)
    ikHad = mc.ikHandle(sj=jnt_lis[0], ee=jnt_lis[-1], c=lso, sol='ikSplineSolver', ccv=False,
                        n='ikHad_{}_{:03d}'.format(nam, 1))[0]
    surSkin = mc.skinCluster(ctlJnt_lis, surf, n='skin_{}_{:03d}'.format(nam, 1))[0]

    grp_main = mc.group(n='grp_{}_001'.format(nam), w=True, em=True)
    mc.parent(ikHad, jnt_lis[0], grp_lis, surf, lso, grp_main)

    cvr_info = mc.createNode('curveInfo', n='cvrInfo_{}_{:03d}'.format(nam, 1))
    mc.connectAttr('{}.worldSpace[0]'.format(lsoShape), '{}.inputCurve'.format(cvr_info))
    cvr_length = mc.getAttr('{}.arcLength'.format(cvr_info))

    mult_node = mc.createNode('multiplyDivide', n='mult_{}_cvrLength_{:03d}'.format(nam, 1))
    mc.setAttr('{}.operation'.format(mult_node), 2)
    mc.setAttr('{}.input2X'.format(mult_node), cvr_length)
    mc.connectAttr('{}.arcLength'.format(cvr_info), '{}.input1X'.format(mult_node))

    for i in range(len(jnt_lis) - 1):
        mc.connectAttr('{}.outputX'.format(mult_node), '{}.scaleX'.format(jnt_lis[i]))


def cleanBindingDistortion():
    topLevel = mc.ls(sl=True)[0]
    if mc.listConnections(topLevel, d=False):
        mods = mc.listRelatives(topLevel, ad=True)
        skinUtils.processingSkinPrecision(mods)

    else:
        fb_print('ѡ�����û�б�root����Լ��', error=True, viewMes=True)





