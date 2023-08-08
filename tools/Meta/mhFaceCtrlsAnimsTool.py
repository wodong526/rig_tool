# -*- coding:GBK -*-
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui

import json

from feedback_tool import Feedback_info as fb_print
from data_path import metaFaceCtrlsPath


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class ExportMetaHumanFaceCtrlAnimToMaya(object):
    """
        ��ue�����Ķ�����Ϣ���赽��ǰ������ָ��mh�Ŀ�������
    """

    def __init__(self, combo_box):
        namSpace = combo_box.currentText()
        if namSpace:
            self.ns = namSpace
        else:
            self.ns = ''

        self.get_ctrls(self.getFaceCtrlFile())

    def getFaceCtrlFile(self):
        """
        ��ȡ������Ϣ�ļ���������ļ��Ƿ�Ϊue����face��������Ϣ���ļ�
        :return: json�ļ��ڵ��ֵ�
        """
        file_path = QtWidgets.QFileDialog.getOpenFileName(maya_main_window(), u'ѡ������ļ�', '', '(*.json)')
        if file_path[0]:
            with open(file_path[0], 'r') as f:
                result = json.load(f)
        else:
            fb_print('û��ѡ����Ч�ļ���', error=True)

        if 'dictType' not in result.keys() or result['dictType'] != 'metaHuman_FaceCtrlsAnim':
            fb_print('������ļ�����metaHuman����������������', error=True)
        else:
            del result['dictType']
            return result

    def get_ctrls(self, ctrl_dir):
        """
        ��ȡ��������Ϣ���������������Ƹ�ΪMaya��Ӧ�Ŀ��������ƣ���k֡
        :param ctrl_dir: ��������Ϣ�ֵ�
        :return:
        """
        for ctl, inf in ctrl_dir.items():
            attr = 'ty'

            if '.' in ctl:
                ctl_str_lis = ctl.split('.')

                ctl = ctl_str_lis[0]
                if len(ctl_str_lis) > 2:
                    attr = ctl_str_lis[1]. \
                               replace('Location', 'translate'). \
                               replace('Rotation', 'rotate'). \
                               replace('Scale', 'scale') + ctl_str_lis[-1].upper()
                else:
                    attr = 'translate' + ctl_str_lis[-1].upper()

            if ctl.split('_')[-1].isdigit():  #���һ���Ƿ�ֻΪ���֣�����ȥ��β��
                ctl = ctl.replace('_{}'.format(ctl.rsplit('.', 1)[-1], ''))

            self.set_keys(ctl, attr, inf)
        fb_print('metaHumanFace����������֡���', info=True)

    def set_keys(self, ctl, attr, inf):
        """
        Ϊ����������k֡������������UE��Maya����Ӧ�Ŀ�����
        :param ctl: ��������
        :param attr: ��������������
        :param inf: ��k֡��ʱ����ֵ
        :return:
        """
        replace_dic = {'CTRL_C_tongue_move': 'CTRL_C_tongue', 'CTRL_C_tongue_bendTwist': 'CTRL_C_tongue_roll',
                       'CTRL_C_tongue_tipMove': 'CTRL_C_tongue_tip', 'CTRL_C_tongue_thickThin': '',
                       'CTRL_C_tongue_wideNarrow': 'CTRL_C_tongue_narrowWide', 'CTRL_C_tongue_roll': '',
                       'CTRL_L_mouth_thicknessInwardU': '', 'CTRL_R_mouth_thicknessInwardU': '',
                       'CTRL_R_mouth_thicknessInwardD': '', 'CTRL_L_mouth_thicknessInwardD': ''}
        if ctl in replace_dic:
            if not replace_dic[ctl]:
                fb_print('������{}������������������ģ���ΪUE��Maya�е�metaHuman���������ٲ��ֲ���Ӧ'.format(ctl),
                         info=True)
                return None
            else:
                ctl = replace_dic[ctl]

        ctrl = self.ns + ctl
        if mc.objExists(ctrl):
            for tim, val in inf:
                try:
                    mc.setKeyframe(ctrl, at=attr, v=val, t=tim)
                except Exception as e:
                    mc.error('������{}���ùؼ�֡���󣬴�����Ϣ��{}'.format(ctrl, e))
        else:
            fb_print('������{}������'.format(ctrl), warning=True)


def readCtrlsFile():
    """
    ��ȡmetaHuman�����������б�
    :return:
    """
    with open(metaFaceCtrlsPath + 'metaFaceCtrls.json', 'r') as f:
        result = json.load(f)

    return result['metaFaceCtrls']


class TransformFaceCtrlsKeys(object):
    """
    �����ƶ�������֡
    """

    def __init__(self, spn_box, combo_box):
        self.val = spn_box.value()
        namSpace = combo_box.currentText()
        if namSpace:
            ns = namSpace
        else:
            ns = ''

        ctrl_lis = readCtrlsFile()
        self.transformKeys(ctrl_lis, ns)

    def transformKeys(self, ctrls, ns):
        """
        �����ƶ�face�������Ĺؼ�֡
        :param ctrls:Ҫ�ƶ��Ŀ�����
        :param ns:���ƶ��Ŀ������ʲ��ռ�����
        :return:
        """
        for ctl in ctrls:
            ctrl = ns + ctl
            if mc.objExists(ctrl):
                for attr in mc.listAttr(ctrl, k=True):
                    ctrlAttr = '{}.{}'.format(ctrl, attr)
                    ctrlKeys = mc.keyframe(ctrlAttr, q=True)
                    if ctrlKeys:
                        if self.val >= 0:
                            #�����ƶ���ʱ��ǰ֡�޷��ƶ�������֡�Ķ��棬�һ�ȡ�Ŀ�����֡�б�Ϊ��С���������������ƶ�ʱ��Ҫ��ĩβ֡��ʼ�ƶ�
                            ctrlKeys.reverse()

                        for key in ctrlKeys:
                            newKey = key + self.val
                            mc.keyframe(ctrlAttr, e=True, t=(key, key), tc=newKey)
                    else:
                        fb_print('������{}û��֡'.format(ctrlAttr), warning=True)
            else:
                fb_print('������{}������'.format(ctrl), warning=True)
        fb_print('metaHuman�����������ƶ�{}֡�����'.format(self.val), info=True)


def elect_metaFaceCtrl(combo_box):
    namSpace = combo_box.currentText()
    ctrl_lis = readCtrlsFile()
    mc.select(cl=True)
    no_lis = ['CTRL_lookAtSwitch', 'CTRL_faceGUIfollowHead', 'CTRL_eyesAimFollowHead', 'CTRL_rigLogicSwitch']
    for ctl in ctrl_lis:
        if ctl in no_lis:
            continue

        ctrl = namSpace + ctl
        if mc.objExists(ctrl):
            mc.select(ctrl, add=True)
        else:
            fb_print('������{}�����ڡ�'.format(ctrl), warning=True)
