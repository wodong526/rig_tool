# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui

import copy
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class CREATE_TRACK(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(CREATE_TRACK, self).__init__(parent)

        self.setWindowTitle(u'�Զ������Ĵ�')
        if mc.about(ntOS=True):  # �ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setMinimumWidth(250)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.if_mod = False

    def create_widgets(self):
        self.name_lab = QtWidgets.QLabel(u'����')

        self.get_curve_but = QtWidgets.QPushButton(u'��ȡ����')
        self.get_mod_but = QtWidgets.QPushButton(u'��ȡģ��')
        self.ctl_but = QtWidgets.QPushButton(u'������')

        self.name_lin = QtWidgets.QLineEdit()
        self.name_lin.setToolTip(u'�������ƹؼ���')
        validator = QtGui.QRegExpValidator(self)
        validator.setRegExp(QtCore.QRegExp('[a-zA-Z][a-zA-Z0-9_]+'))
        self.name_lin.setValidator(validator)
        self.curve_lin = QtWidgets.QLineEdit()
        self.curve_lin.setEnabled(False)
        self.curve_lin.setToolTip(u'�����ť����ѡ�еıպ�����')
        self.curve_lin.setFocusPolicy(QtCore.Qt.NoFocus)
        self.mod_lin = QtWidgets.QLineEdit()
        self.mod_lin.setEnabled(False)
        self.mod_lin.setToolTip(u'�����ť�����Ĵ����')
        self.mod_lin.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ctl_lin = QtWidgets.QLineEdit()
        self.ctl_lin.setEnabled(False)
        self.ctl_lin.setToolTip(u'�����ť�����Ĵ�������')

        self.create_track_but = QtWidgets.QPushButton(u'�����Ĵ�')
        self.trackQuantity_sp = QtWidgets.QSpinBox()
        self.trackQuantity_sp.setValue(30)
        self.trackQuantity_sp.setMinimum(1)

        self.undoTrack_but = QtWidgets.QPushButton(u'�����Ĵ�')
        self.undoTrack_but.setEnabled(False)
        self.conn_but = QtWidgets.QPushButton(u'��������')
        self.conn_but.setEnabled(False)

        self.transverse_rvs_but = QtWidgets.QPushButton(u'�Ĵ�����ת')
        self.transverse_rvs_but.setEnabled(False)
        self.vertical_rvs_but = QtWidgets.QPushButton(u'�Ĵ�����ת')
        self.vertical_rvs_but.setEnabled(False)
        self.portrait_rvs_but = QtWidgets.QPushButton(u'�Ĵ�����ת')
        self.portrait_rvs_but.setEnabled(False)
        self.create_ctl_but = QtWidgets.QPushButton(u'���ɿ�����')
        self.create_ctl_but.setEnabled(False)

    def create_layout(self):
        main_layout = QtWidgets.QFormLayout(self)
        main_layout.addRow(self.name_lab, self.name_lin)
        main_layout.addRow(self.get_curve_but, self.curve_lin)
        main_layout.addRow(self.get_mod_but, self.mod_lin)
        main_layout.addRow(self.ctl_but, self.ctl_lin)
        main_layout.addRow(self.create_track_but, self.trackQuantity_sp)
        main_layout.addRow(self.undoTrack_but, self.conn_but)
        main_layout.addRow(self.transverse_rvs_but, self.vertical_rvs_but)
        main_layout.addRow(self.portrait_rvs_but, self.create_ctl_but)
        main_layout.setContentsMargins(0, 0, 0, 0)

    def create_connections(self):
        self.get_curve_but.clicked.connect(self.get_curve)
        self.get_mod_but.clicked.connect(self.get_mode)
        self.ctl_but.clicked.connect(self.get_ctl)
        self.create_track_but.clicked.connect(self.set_track)
        self.undoTrack_but.clicked.connect(self.undo_mod)
        self.conn_but.clicked.connect(self.create_link)
        self.transverse_rvs_but.clicked.connect(self.transverse_rvs)
        self.vertical_rvs_but.clicked.connect(self.vertical_rvs)
        self.portrait_rvs_but.clicked.connect(self.portrait_rvs)
        self.create_ctl_but.clicked.connect(self.create_controller)

    def get_curve(self):
        '''
        ѡ������ȷ���Ĵ�λ�÷�Χ���������ߣ�ͨ��ѡ������ɸѡΪֻ��Ϊ������������߶���
        ���������self.curveAll�������������ߵ�trs��
        :return:
        '''
        sel_lis = mc.ls(sl = True)

        crv_lis = ''
        if len(sel_lis) == 2:
            for crv in sel_lis:
                shp = mc.listRelatives(crv, s = True)
                if shp:
                    if mc.nodeType(shp) == 'nurbsCurve':
                        crv_lis = crv_lis + crv + ','
                    else:
                        log.error('����{}��������'.format(crv))
                        return False
                else:
                    log.error('����{}�������ߡ�'.format(crv))
        else:
            log.error('Ӧѡ��2������ʵ��ѡ��{}����'.format(len(sel_lis)))
            return False
        self.curve_lin.setText(crv_lis)
        self.curveAll = copy.copy(sel_lis)#����

    def get_mode(self):
        '''
        ѡ�񵥸��Ĵ����õ���ģ�ͣ�ͨ��ѡ������ɸѡΪֻ��Ϊһ������Ķ���ζ���
        ���������self.modAll���ո�ģ�͵�trs��
        :return:
        '''
        sel_lis = mc.ls(sl=True)

        mod_lis = ''
        if len(sel_lis) == 1:
            for obj in sel_lis:
                shp = mc.listRelatives(obj, s=True)
                if shp:
                    if mc.nodeType(shp) == 'mesh':
                        mod_lis = mod_lis + obj + ','
                    else:
                        log.error('����{}����ģ��'.format(obj))
                        return False
                else:
                    log.error('����{}����ģ�͡�'.format(obj))
        else:
            log.error('Ӧѡ��1������ʵ��ѡ��{}����'.format(len(sel_lis)))
            return False
        self.mod_lin.setText(mod_lis)
        self.modAll = copy.copy(sel_lis)[0]#ģ��

    def get_ctl(self):
        '''
        ѡ�����ڿ����Ĵ��˶��Ŀ������ƣ��ÿ�����������������������õ��Ĵ��˶���Ч��
        ���������self.ctl���ոÿ�������trs��
        :return:
        '''
        sel = mc.ls(sl=True)
        if len(sel) == 1:
            shp = mc.listRelatives(sel[0], s=True)
            if shp:
                if mc.nodeType(shp) == 'nurbsCurve':
                    self.ctl_lin.setText(sel[0])
                    self.ctl = sel[0]
                else:
                    log.error('ѡ����������ߡ�')
                    return False
            else:
                log.error('ѡ����������ߡ�')
                return False
        else:
            log.error('Ӧѡ��1������ʵ��ѡ��{}����'.format(len(sel)))
            return False

    def set_track(self):
        '''
        �����жϸ��б༭�����������룬�в��ܼ���ִ�У�����������ִ��
        ������Ҫ�����Ĵ�ģ�͡���Ƥ�ؽڡ��������ӡ��������桢xform���飬���������������ڵ���ŵ�xform��
        ��__init__�����ｨ���������self.if_mod�����жϵ�ǰ�����Ƿ�Ϊ�����Ĵ������
        ��Ϊ��ʱ����������߻�δ���ɣ���������ɺ��ٽ�������ģ�͵ĺ������ں������к�if_mod��Ϊ�棬�ٴ����иú���������������������
        ���ߵ�����λ�û����õ��������������λ�ã��Դ����ﵽ�ں������ɵĹؽ�ʱ�Ը�����������λ�ý��м������λ��
        :return:
        '''
        if not self.name_lin.text():
            log.error('û���������ơ�')
            return False
        else:
            self.nam = self.name_lin.text()
        if not self.curve_lin.text():
            log.error('û��ѡ�����ߡ�')
            return False
        if not self.mod_lin.text():
            log.error('û��ѡ���Ĵ������')
            return False
        if not self.ctl_lin.text():
            log.error('û��ѡ���������')
            return False

        if not mc.objExists('grp_xform_D'):
            self.xform_grp = mc.group(n = 'grp_xform_D', em = True, w = True)
        else:
            self.xform_grp = 'grp_xform_D'

        if not mc.objExists('grp_surface_{}'.format(self.nam)):
            self.surface_grp = mc.group(n = 'grp_surface_{}'.format(self.nam), em = True)
        else:
            self.surface_grp = 'grp_surface_{}'.format(self.nam)

        if not mc.objExists('grp_mod_{}'.format(self.nam)):
            self.mode_grp = mc.group(n = 'grp_mod_{}'.format(self.nam), em = True)
        else:
            self.mode_grp = 'grp_mod_{}'.format(self.nam)

        if not mc.objExists('grp_jnt_{}'.format(self.nam)):
            self.jnt_grp = mc.group(n = 'grp_jnt_{}'.format(self.nam), em = True)
        else:
            self.jnt_grp = 'grp_jnt_{}'.format(self.nam)

        if not mc.objExists('grp_loc_{}'.format(self.nam)):
            self.loc_grp = mc.group(n = 'grp_loc_{}'.format(self.nam), em = True)
        else:
            self.loc_grp = 'grp_loc_{}'.format(self.nam)

        if not mc.objExists('grp_link_{}'.format(self.nam)):
            self.link_grp = mc.group(n = 'grp_link_{}'.format(self.nam), em = True, p = self.xform_grp)
        else:
            self.link_grp = 'grp_link_{}'.format(self.nam)

        if self.if_mod:
            self.for_create_ref()
        else:
            self.loft_suf = mc.loft(self.curveAll[0], self.curveAll[1], ch = False, rn = False, rsn = True, u = True)[0]
            self.loft_suf = mc.rename(self.loft_suf, 'loft_{}_tag_001'.format(self.nam))
            mc.setAttr('{}.visibility'.format(self.loft_suf), False)
            mc.parent(self.loft_suf, self.surface_grp)
            self.loft_suf_shp = mc.listRelatives(self.loft_suf, s = True)[0]

            crvInfo_node = mc.createNode('curveFromSurfaceIso', n = 'crvIso_{}_pathInfo_001'.format(self.nam))
            mc.setAttr('{}.isoparmValue'.format(crvInfo_node), 0.5)#�����ɵ�����·���ŵ�����������м�
            mc.connectAttr('{}.worldSpace[0]'.format(self.loft_suf_shp), '{}.inputSurface'.format(crvInfo_node))

            self.crv_path_shp = mc.createNode('nurbsCurve', n = 'crv_{}_path_001Shape'.format(self.nam))

            crv_path = mc.listRelatives(self.crv_path_shp, p = True)[0]
            mc.parent(crv_path, self.surface_grp)
            nam = mc.rename(crv_path, 'crv_{}_path_001'.format(self.nam))
            mc.setAttr('{}.inheritsTransform'.format(nam), 0)
            mc.setAttr('{}.visibility'.format(nam), 0)

            mc.connectAttr('{}.outputCurve'.format(crvInfo_node), '{}.create'.format(self.crv_path_shp))
            self.if_mod = True
            self.for_create_ref()

    def for_create_ref(self):
        '''
        �������ģ������������motionPath�������ӣ����Բ鿴λ���Ƿ����
        �ڸú������к��������ӵ���椰�ť������ʹ��
        :return:
        '''
        self.motPath_lis = []
        for i in range(self.trackQuantity_sp.value()):
            i_str = str(i)
            val = (1.0 / self.trackQuantity_sp.value()) * i
            ref_mod = mc.duplicate(self.modAll, n = 'mod_{}_{}'.format(self.modAll, i_str.rjust(3, '0')))[0]
            mc.parent(ref_mod, self.mode_grp)
            motPath_node = mc.createNode('motionPath', n='reference_motPath_{}'.format(i_str.rjust(3, '0')))
            self.motPath_lis.append(motPath_node)
            mc.setAttr('{}.fractionMode'.format(motPath_node), 1)
            mc.connectAttr('{}.worldSpace[0]'.format(self.crv_path_shp), '{}.geometryPath'.format(motPath_node))
            mc.connectAttr('{}.allCoordinates'.format(motPath_node), '{}.translate'.format(ref_mod))
            mc.setAttr('{}.uValue'.format(motPath_node), val)
        self.undoTrack_but.setEnabled(True)
        self.conn_but.setEnabled(True)

    def undo_mod(self):
        '''
        ��ģ�����µ�����ģ�Ͷ�ɾ��������motionPath�ڵ���ģ��ֱ������������ɾ��ģ��ʱmotionPath�ڵ���Զ���ɾ��������ɾ�����б�ʱ�ᱨ��
        :return:
        '''
        del_lis = mc.listRelatives(self.mode_grp)
        try:
            mc.delete(del_lis)
            mc.delete(self.motPath_lis)
        except:
            pass
        self.conn_but.setEnabled(False)
        self.undoTrack_but.setEnabled(False)

    def create_link(self):
        '''
        ���ɺ��ļ���ڵ�
        �����йؽڶ�������ɺ���ܻ��ÿ���ؽڵ���һ���ؽڣ�������Ҫ������һ��forѭ����������һ���ڵ��λ��
        :return:
        '''
        mc.delete(mc.listRelatives(self.mode_grp))
        mc.addAttr(self.ctl, ln='run', dv=0, k=True, at='float')
        self.aim_lis = []
        self.loc_lis = []
        mod_lis = []
        for i in range(self.trackQuantity_sp.value()):
            val = (1.0 / self.trackQuantity_sp.value()) * i
            i_str = str(i + 1).rjust(3, '0')
            loc = mc.spaceLocator(n='loc_{}_{}'.format(self.nam, i_str), a=True)[0]
            mc.setAttr('{}.visibility'.format(loc), 0)
            self.loc_lis.append(loc)
            mc.parent(loc, self.loc_grp)

            mod_lvDai = mc.duplicate(self.modAll, n='mod_{}_{}'.format(self.nam, i_str))
            mod_lis.append(mod_lvDai)
            mc.parent(mod_lvDai, self.mode_grp)

            mc.addAttr(loc, ln='defualtVale', dv=val, k=True, at='float')
            mc.addAttr(loc, ln='int_run', at='long', k=True)

            add_def_node = mc.createNode('addDoubleLinear', n='mlt_{}_{}'.format(self.nam, i_str))
            mc.connectAttr('{}.defualtVale'.format(loc), '{}.input1'.format(add_def_node))

            mult_node = mc.createNode('multDoubleLinear', n='mult_{}_{}'.format(self.nam, i_str))
            mc.setAttr('{}.input2'.format(mult_node), 0.01)
            mc.connectAttr('{}.output'.format(mult_node), '{}.input2'.format(add_def_node))
            mc.connectAttr('{}.run'.format(self.ctl), '{}.input1'.format(mult_node))

            posi_node = mc.createNode('pointOnSurfaceInfo', n='posi_{}_{}'.format(self.nam, i_str))
            mc.setAttr('{}.parameterV'.format(posi_node), 0.5)
            mc.connectAttr('{}.worldSpace[0]'.format(self.loft_suf_shp), '{}.inputSurface'.format(posi_node))

            mc.connectAttr('{}.output'.format(add_def_node), '{}.int_run'.format(loc))

            cond_node = mc.createNode('condition', n = 'cond_{}_{}'.format(self.nam, i_str))
            mc.setAttr('{}.operation'.format(cond_node), 2)
            mc.connectAttr('{}.output'.format(add_def_node), '{}.firstTerm'.format(cond_node))
            mc.connectAttr('{}.int_run'.format(loc), '{}.secondTerm'.format(cond_node))
            mc.connectAttr('{}.int_run'.format(loc), '{}.colorIfTrueR'.format(cond_node))

            add_if_node = mc.createNode('addDoubleLinear', n='add_{}_{}'.format(self.nam, i_str))
            mc.setAttr('{}.input2'.format(add_if_node), -1)
            mc.connectAttr('{}.int_run'.format(loc), '{}.input1'.format(add_if_node))
            mc.connectAttr('{}.output'.format(add_if_node), '{}.colorIfFalseR'.format(cond_node))

            #��������ӽڵ㣬�����2ѡ�������
            plu_lvDai_node = mc.createNode('plusMinusAverage', n='plu_{}_{}'.format(self.nam, i_str))
            mc.setAttr('{}.operation'.format(plu_lvDai_node), 2)
            mc.connectAttr('{}.output'.format(add_def_node), '{}.input1D[0]'.format(plu_lvDai_node))
            mc.connectAttr('{}.outColorR'.format(cond_node), '{}.input1D[1]'.format(plu_lvDai_node))

            motPath = mc.createNode('motionPath', n='motPath_{}_{}'.format(self.nam, i_str))
            mc.setAttr('{}.fractionMode'.format(motPath), 1)#�������߱����ƶ����ر���ʵ��λ���ƶ�
            mc.connectAttr('{}.worldSpace[0]'.format(self.crv_path_shp), '{}.geometryPath'.format(motPath))
            mc.connectAttr('{}.allCoordinates'.format(motPath), '{}.translate'.format(loc))
            mc.connectAttr('{}.output1D'.format(plu_lvDai_node), '{}.uValue'.format(motPath))

            clo_nod = mc.createNode('closestPointOnSurface', n='los_{}_{}'.format(self.nam, i_str))
            mc.connectAttr('{}.worldSpace[0]'.format(self.loft_suf_shp), '{}.inputSurface'.format(clo_nod))
            mc.connectAttr('{}.translate'.format(loc), '{}.inPosition'.format(clo_nod))

            sufInfo_node = mc.createNode('pointOnSurfaceInfo', n = 'pointInfo_{}_{}'.format(self.nam, i_str))
            mc.connectAttr('{}.parameterU'.format(clo_nod), '{}.parameterU'.format(sufInfo_node))
            mc.connectAttr('{}.parameterV'.format(clo_nod), '{}.parameterV'.format(sufInfo_node))
            mc.connectAttr('{}.worldSpace[0]'.format(self.loft_suf_shp), '{}.inputSurface'.format(sufInfo_node))

            aim_nod = mc.createNode('aimConstraint', n='aim_{}_{}'.format(self.nam, i_str))
            mc.parent(aim_nod, self.link_grp)
            self.aim_lis.append(aim_nod)
            mc.connectAttr('{}.normal'.format(sufInfo_node), '{}.worldUpVector'.format(aim_nod))
            for aix in ['X', 'Y', 'Z']:
                mc.connectAttr('{}.constraintRotate{}'.format(aim_nod, aix), '{}.rotate{}'.format(loc, aix))
            log.info('{}���������ɡ�'.format(loc))

        for inf in range(self.trackQuantity_sp.value()):
            inf_str = str(inf + 1).rjust(3, '0')
            if inf == self.trackQuantity_sp.value() - 1:
                aim_jnt = self.loc_lis[0]
            else:
                aim_jnt = self.loc_lis[inf + 1]

            plus_aix_nod = mc.createNode('plusMinusAverage', n='plus_aix_{}_{}'.format(self.nam, inf_str))
            mc.setAttr('{}.operation'.format(plus_aix_nod), 2)
            mc.connectAttr('{}.translate'.format(aim_jnt), '{}.input3D[0]'.format(plus_aix_nod))
            mc.connectAttr('{}.translate'.format(self.loc_lis[inf]), '{}.input3D[1]'.format(plus_aix_nod))

            mc.connectAttr('{}.output3D'.format(plus_aix_nod), '{}.target[0].targetTranslate'.format(self.aim_lis[inf]))
            log.info('{}����Լ�������ɡ�'.format(self.loc_lis[inf]))

        self.create_lvDai(mod_lis)

    def create_lvDai(self, mod_lis):
        '''
        �����Ƶ��Ĵ�ģ�ͷŵ���Ӧλ�ã�����ؽڽ�����Ƥ
        :param mod_lis:
        :return:
        '''
        for i in range(len(mod_lis)):
            loc = self.loc_lis[i]
            pos = mc.xform(loc, ws=True, q=True, t=True)
            rot = mc.xform(loc, ws=True, q=True, ro=True)

            mod = mod_lis[i]
            mc.select(cl=True)
            jnt = mc.joint(n='jnt_{}_{}'.format(self.nam, str(i + 1).rjust(3, '0')))
            mc.parent(jnt, self.jnt_grp)

            mc.xform(jnt, t=pos, ro=rot)
            mc.xform(mod, t=pos, ro=rot)
            mc.makeIdentity(jnt, a=True, t=True, r=True, n=False, pn=True)
            mc.makeIdentity(mod, a=True, t=True, r=True, n=False, pn=True)
            mc.skinCluster(mod, jnt)
            link = mc.parentConstraint(loc, jnt, mo=True, n='parConn_{}_{}'.format(self.nam, str(i + 1).rjust(3, '0')))
            mc.parent(link, self.link_grp)
        log.info('�ѽ����ؽ����Ĵ���Ƭ���ӡ�')
        self.transverse_rvs_but.setEnabled(True)
        self.vertical_rvs_but.setEnabled(True)
        self.portrait_rvs_but.setEnabled(True)
        self.create_ctl_but.setEnabled(True)

    def transverse_rvs(self):
        '''
        ��ģ�������ε�Ŀ��Լ���ڵ�֮����ӼӼ��ڵ㣬���Խ������180�ȣ��ڵ�һ��ʹ��ʱ����Ϊ��Ҫ���ɽڵ���������ʱ��
        :return:
        '''
        if hasattr(self, 'transvs'):
            for node in self.transvs:
                if mc.getAttr('{}.input2'.format(node)) == 180:
                    mc.setAttr('{}.input2'.format(node), 0)
                elif mc.getAttr('{}.input2'.format(node)) == 0:
                    mc.setAttr('{}.input2'.format(node), 180)
                else:
                    log.warning('�ڵ�{}�����޸Ĵ���'.format(node))
            log.info('�Ĵ�x�᷽������ת180�ȡ�')

        else:
            self.transvs = []
            i = 0
            for aim, jnt in zip(self.aim_lis, self.loc_lis):
                i = i+1
                i_str = str(i).rjust(3, '0')
                add_node = mc.createNode('addDoubleLinear', n='add_rotX_{}_{}'.format(self.nam, i_str))
                self.transvs.append(add_node)

                mc.setAttr('{}.input2'.format(add_node), 180)
                mc.connectAttr('{}.constraintRotateX'.format(aim), '{}.input1'.format(add_node))
                mc.connectAttr('{}.output'.format(add_node), '{}.rotateX'.format(jnt), f=True)
            log.info('�Ĵ�x�᷽������ת180�ȡ�')

    def vertical_rvs(self):
        if hasattr(self, 'vertical'):
            for node in self.vertical:
                if mc.getAttr('{}.input2'.format(node)) == 180:
                    mc.setAttr('{}.input2'.format(node), 0)
                elif mc.getAttr('{}.input2'.format(node)) == 0:
                    mc.setAttr('{}.input2'.format(node), 180)
                else:
                    log.warning('�ڵ�{}�����޸Ĵ���'.format(node))
            log.info('�Ĵ�z�᷽������ת180�ȡ�')

        else:
            self.vertical = []
            i = 0
            for aim, jnt in zip(self.aim_lis, self.loc_lis):
                i = i + 1
                i_str = str(i).rjust(3, '0')
                add_node = mc.createNode('addDoubleLinear', n='add_rotY_{}_{}'.format(self.nam, i_str))
                self.vertical.append(add_node)

                mc.setAttr('{}.input2'.format(add_node), 180)
                mc.connectAttr('{}.constraintRotateY'.format(aim), '{}.input1'.format(add_node))
                mc.connectAttr('{}.output'.format(add_node), '{}.rotateY'.format(jnt), f=True)
            log.info('�Ĵ�y�᷽������ת180�ȡ�')

    def portrait_rvs(self):
        '''
        �����淴��Ϳ���ֱ��������·����ת��Ч�������ᵼ��ģ�͵�λ��Ҳ���ŷ�ת
        :return:
        '''
        mc.reverseSurface(self.loft_suf, ch=False, d=0, rpo=True)
        log.info('�Ĵ�z�᷽������ת180�ȡ�')

    def create_controller(self):
        '''
        �������ÿһ���м����ɹؽڲ���������Ƥ�������ɿ�����
        ����Ƥ�ؽ�ֱ�ӷŵ����������£���Ϊ����ģ�͵Ĺؽڲ���Ӱ��������Ƥ�ؽڣ����Բ���Ӱ��Ч��
        :return:
        '''
        ctl_grp = mc.group(n='grp_clt_{}'.format(self.nam), em=True, w=True)
        jnt_lis = []
        for column in range(mc.getAttr('{}.spansU'.format(self.loft_suf))):
            i = str(column+1)
            i = i.rjust(3, '0')

            row = mc.getAttr('{}.spansV'.format(self.loft_suf)) + 3
            pos_lis = [0, 0, 0]
            for pnt in range(row):
                pos = mc.xform('{}.cv[{}][{}]'.format(self.loft_suf, column, pnt), ws=True, q=True, t=True)
                pos_lis[0] = pos[0] + pos_lis[0]
                pos_lis[1] = pos[1] + pos_lis[1]
                pos_lis[2] = pos[2] + pos_lis[2]

            ctl_pos = [pos_lis[0]/row, pos_lis[1]/row, pos_lis[2]/row]
            mc.select(cl=True)
            jnt = mc.joint(n='jnt_ctl_{}_{}'.format(self.nam, i))
            jnt_lis.append(jnt)
            mc.setAttr('{}.visibility'.format(jnt), 0)
            mc.xform(jnt, ws=True, t=ctl_pos)

            ctl = mc.createNode('transform', n='ctl_{}_{}'.format(self.nam, i))
            shp = mc.createNode('nurbsCurve', p=ctl)
            mm.eval(self.ctl_point())
            mc.setAttr('{}.overrideEnabled'.format(shp), 1)
            mc.setAttr('{}.overrideRGBColors'.format(shp), 1)
            mc.setAttr('{}.overrideColorRGB'.format(shp), 1, 1, 0)

            grp = mc.group(n='grp_{}_{}'.format(self.nam, i), em=True, w=True)
            grp_offset = mc.group(n='grp_{}_offset_{}'.format(self.nam, i), p=grp, em=True)
            mc.parent(ctl, grp_offset)
            mc.xform(grp, ws=True, t=ctl_pos)
            mc.parent(jnt, ctl)
            mc.parent(grp, ctl_grp)

            for aix in ['X', 'Y', 'Z']:
                mc.setAttr('{}.rotate{}'.format(ctl, aix), k=False, l=False, cb=False)
            log.info('������{}������ɡ�'.format(ctl))
        sclt = mc.skinCluster(jnt_lis, self.loft_suf)[0]
        for i in range(mc.getAttr('{}.spansU'.format(self.loft_suf))):
            mc.skinPercent(sclt, '{}.cv[{}][:]'.format(self.loft_suf, i), tv=[('{}'.format(jnt_lis[i]), 1)])
        log.info('������Ч������ɡ�')

    def ctl_point(self):
        '''
        ��������״�ĵ���Ϣ
        :return:
        '''
        pos = '''setAttr ".cc" -type "nurbsCurve"
                 1 15 0 no 3
                 16 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
                 16
                 0.5 0.5 0.5
                 0.5 0.5 -0.5
                 -0.5 0.5 -0.5
                 -0.5 -0.5 -0.5
                 0.5 -0.5 -0.5
                 0.5 0.5 -0.5
                 -0.5 0.5 -0.5
                 -0.5 0.5 0.5
                 0.5 0.5 0.5
                 0.5 -0.5 0.5
                 0.5 -0.5 -0.5
                 -0.5 -0.5 -0.5
                 -0.5 -0.5 0.5
                 0.5 -0.5 0.5
                 -0.5 -0.5 0.5
                 -0.5 0.5 0.5;'''
        return pos


try:
    my_window.close()
    my_window.deleteLater()
except:
    pass
finally:
    my_window = CREATE_TRACK()
    my_window.show()