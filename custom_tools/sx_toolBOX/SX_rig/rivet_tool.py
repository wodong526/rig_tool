# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui

import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class RivetWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(RivetWindow, self).__init__(parent)

        self.setWindowTitle(u'��í������')
        if mc.about(ntOS=True):  #�ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.but_rivet_point = QtWidgets.QPushButton(u'��ѡ����ϴ�í��')
        self.but_rivet_edge = QtWidgets.QPushButton(u'��ѡ����������м����ɶ�λ��')

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.but_rivet_point)
        main_layout.addWidget(self.but_rivet_edge)

    def create_connections(self):
        self.but_rivet_point.clicked.connect(self.rivet_point)
        self.but_rivet_edge.clicked.connect(self.rivet_edge)

    def rivet_point(self):
        '''
        ��ȡ����ѡ���б��еĵ㣬������ë�ҵ��飬ѭ�����ô���ë�Һ���
        '''
        point_lis = mc.filterExpand(sm=31)#����ѡ���б�Ķ���ε�
        if point_lis:
            if not mc.objExists('grp_rivet_AA'):#�ж����Ƿ���ڣ������ھʹ���
                mc.group(n='grp_rivet_AA', em=True, w=True)

            for pot in point_lis:#��ÿ��ѡ�еĵ㶼��í��
                shape = pot.split('.')[0]#��ѡ���ģ�͵�shape��
                self.create_rivet(pot, shape)
        else:
            log.warning('û��ѡ����Ч����ε㡣')

    def create_rivet(self, pot, shp):
        '''
        ͨ������ε���Ϣ��ģ��shape������ë��
        '''
        map = mc.polyListComponentConversion(pot, tuv=True)[0]#��ȡģ�͵�map��
        uv_pos = mc.polyEditUV(map, q=True)#��ȡѡ�еĵ���uv���λ��

        folcShape_node = mc.createNode('follicle', n='folc_rivet_00#')#����ë���ڵ㣬���ص���shape�ڵ���
        folc_node = mc.listRelatives(folcShape_node, p=True)
        folc_node = mc.rename(folc_node, 'folc_rivet_T_00#')

        mc.connectAttr('{}.worldMatrix[0]'.format(shp), '{}.inputWorldMatrix'.format(folcShape_node))
        mc.connectAttr('{}.outMesh'.format(shp), '{}.inputMesh'.format(folcShape_node))
        mc.connectAttr('{}.outTranslate'.format(folcShape_node), '{}.translate'.format(folc_node))
        mc.connectAttr('{}.outRotate'.format(folcShape_node), '{}.rotate'.format(folc_node))
        mc.setAttr('{}.parameterU'.format(folcShape_node), uv_pos[0])
        mc.setAttr('{}.parameterV'.format(folcShape_node), uv_pos[1])

        mc.parent(folc_node, 'grp_rivet_AA')

    def rivet_edge(self):
        edge_lis = mc.filterExpand(sm=32)#���ص��Ƕ���α�
        if len(edge_lis) == 2:
            shp = edge_lis[0].split('.')[0]#�����ڵ�ģ�͵�shape�ڵ���
            ege_a = edge_lis[0].split('[')[1].replace(']', '')#�ߵ�id
            ege_b = edge_lis[1].split('[')[1].replace(']', '')

            crvFME_node_A = mc.createNode('curveFromMeshEdge', n='crvFME_rivet_A_00#')
            mc.setAttr('{}.ei[0]'.format(crvFME_node_A), int(ege_a))#���ñߵ�id��Ϣ
            crvFME_node_B = mc.createNode('curveFromMeshEdge', n='crvFME_rivet_B_00#')
            mc.setAttr('{}.ei[0]'.format(crvFME_node_B), int(ege_b))
            loft_node = mc.createNode('loft', n='loft_rivet_00#')
            mc.setAttr('{}.u'.format(loft_node), True)#�������Ϊ true�����ɵ����潫�ڷ��������Ͼ���ͳһ�Ĳ��������������Ϊ false����������Ϊ�ҳ���
            pntOFI_node = mc.createNode('pointOnSurfaceInfo', n='pntOSI_rivet_00#')
            mc.setAttr('{}.turnOnPercentage'.format(pntOFI_node), True)#������ã������ֵӦָ���� 0,1 ��Χ��
            mc.setAttr('{}.parameterU'.format(pntOFI_node), 0.5)#��������ϵ� U ����ֵ
            mc.setAttr('{}.parameterV'.format(pntOFI_node), 0.5)#��������ϵ� V ����ֵ

            trs = mc.createNode('transform', n='rivet_00#')
            mc.createNode('locator', n='{}Shape'.format(trs), p=trs)

            aim_node = mc.createNode('aimConstraint', p=trs)

            mc.connectAttr('{}.w'.format(shp), '{}.im'.format(crvFME_node_A))
            mc.connectAttr('{}.w'.format(shp), '{}.im'.format(crvFME_node_B))
            mc.connectAttr('{}.oc'.format(crvFME_node_A), '{}.ic[0]'.format(loft_node))
            mc.connectAttr('{}.oc'.format(crvFME_node_B), '{}.ic[1]'.format(loft_node))
            mc.connectAttr('{}.os'.format(loft_node), '{}.is'.format(pntOFI_node))

            mc.connectAttr('{}.position'.format(pntOFI_node), '{}.translate'.format(trs))
            mc.connectAttr('{}.n'.format(pntOFI_node), '{}.tg[0].tt'.format(aim_node))
            mc.connectAttr('{}.tv'.format(pntOFI_node), '{}.wu'.format(aim_node))
            mc.connectAttr('{}.crx'.format(aim_node), '{}.rx'.format(trs))
            mc.connectAttr('{}.cry'.format(aim_node), '{}.ry'.format(trs))
            mc.connectAttr('{}.crz'.format(aim_node), '{}.rz'.format(trs))
        else:
            log.warning('Ӧ��ѡ����������αߡ�')





try:
    my_rivet_window.close()
    my_rivet_window.deleteLater()
except:
    pass
finally:
    my_rivet_window = RivetWindow()
    my_rivet_window.show()