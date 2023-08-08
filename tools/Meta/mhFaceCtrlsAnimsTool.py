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
        将ue导出的动画信息赋予到当前场景中指定mh的控制器上
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
        获取动画信息文件，并检查文件是否为ue导出face控制器信息的文件
        :return: json文件内的字典
        """
        file_path = QtWidgets.QFileDialog.getOpenFileName(maya_main_window(), u'选择材质文件', '', '(*.json)')
        if file_path[0]:
            with open(file_path[0], 'r') as f:
                result = json.load(f)
        else:
            fb_print('没有选择有效文件。', error=True)

        if 'dictType' not in result.keys() or result['dictType'] != 'metaHuman_FaceCtrlsAnim':
            fb_print('导入的文件不是metaHuman脸部控制器动画。', error=True)
        else:
            del result['dictType']
            return result

    def get_ctrls(self, ctrl_dir):
        """
        获取控制器信息，并将控制器名称改为Maya对应的控制器名称，并k帧
        :param ctrl_dir: 控制器信息字典
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

            if ctl.split('_')[-1].isdigit():  #最后一项是否只为数字，是则去掉尾项
                ctl = ctl.replace('_{}'.format(ctl.rsplit('.', 1)[-1], ''))

            self.set_keys(ctl, attr, inf)
        fb_print('metaHumanFace控制器导入帧完成', info=True)

    def set_keys(self, ctl, attr, inf):
        """
        为控制器进行k帧，并跳过由于UE与Maya不对应的控制器
        :param ctl: 控制器名
        :param attr: 控制器的属性名
        :param inf: 被k帧的时间与值
        :return:
        """
        replace_dic = {'CTRL_C_tongue_move': 'CTRL_C_tongue', 'CTRL_C_tongue_bendTwist': 'CTRL_C_tongue_roll',
                       'CTRL_C_tongue_tipMove': 'CTRL_C_tongue_tip', 'CTRL_C_tongue_thickThin': '',
                       'CTRL_C_tongue_wideNarrow': 'CTRL_C_tongue_narrowWide', 'CTRL_C_tongue_roll': '',
                       'CTRL_L_mouth_thicknessInwardU': '', 'CTRL_R_mouth_thicknessInwardU': '',
                       'CTRL_R_mouth_thicknessInwardD': '', 'CTRL_L_mouth_thicknessInwardD': ''}
        if ctl in replace_dic:
            if not replace_dic[ctl]:
                fb_print('控制器{}被跳过，但这是允许的，因为UE与Maya中的metaHuman控制器有少部分不对应'.format(ctl),
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
                    mc.error('控制器{}设置关键帧错误，错误信息：{}'.format(ctrl, e))
        else:
            fb_print('控制器{}不存在'.format(ctrl), warning=True)


def readCtrlsFile():
    """
    获取metaHuman控制器名称列表
    :return:
    """
    with open(metaFaceCtrlsPath + 'metaFaceCtrls.json', 'r') as f:
        result = json.load(f)

    return result['metaFaceCtrls']


class TransformFaceCtrlsKeys(object):
    """
    批量移动控制器帧
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
        批量移动face控制器的关键帧
        :param ctrls:要移动的控制器
        :param ns:被移动的控制器资产空间名称
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
                            #由于移动的时候当前帧无法移动到相邻帧的对面，且获取的控制器帧列表为从小到大，所以在正向移动时需要从末尾帧开始移动
                            ctrlKeys.reverse()

                        for key in ctrlKeys:
                            newKey = key + self.val
                            mc.keyframe(ctrlAttr, e=True, t=(key, key), tc=newKey)
                    else:
                        fb_print('控制器{}没有帧'.format(ctrlAttr), warning=True)
            else:
                fb_print('控制器{}不存在'.format(ctrl), warning=True)
        fb_print('metaHuman控制器动画移动{}帧已完成'.format(self.val), info=True)


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
            fb_print('控制器{}不存在。'.format(ctrl), warning=True)
