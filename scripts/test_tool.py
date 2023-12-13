#coding:utf-8
from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui
import maya.OpenMaya as om

import os
import json
from functools import partial

VIS_TIME = 1000


def maya_main_window():
    return wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)


def print_info(txt, typ=None):
    if typ == 'warning':
        mc.inViewMessage(amg='<font color="yellow">{}</font>'.format(txt), pos='midCenterBot', f=True, fst=VIS_TIME)
        om.MGlobal.displayWarning('{}'.format(txt))

    elif typ == 'error':
        mc.inViewMessage(amg='<font color="red">{}</font>'.format(txt), pos='midCenterBot', f=True, fst=VIS_TIME)
        om.MGlobal.displayError(txt)
        raise RuntimeError(txt)
    else:
        mc.inViewMessage(amg='<font color="lightcyan">{}</font>'.format(txt), pos='midCenterBot', f=True, fst=VIS_TIME)
        om.MGlobal.displayInfo('{}'.format(txt))


def readCtrlsFile():
    """
    获取metaHuman控制器名称列表
    :return:
    """
    meta_info_path = 'X:/Project/Library/metahumanFace_script/metaFaceCtrls.json'
    if os.path.exists(meta_info_path):
        with open(meta_info_path, 'r') as f:
            result = json.load(f)
        return result['FacialControls']
    else:
        print_info('x盘路径不存在，无法使用该功能', typ='error')


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
            print_info('没有选择有效文件。', typ='error')

        if 'dictType' not in result.keys() or result['dictType'] != 'metaHuman_FaceCtrlsAnim':
            print_info('导入的文件不是metaHuman脸部控制器动画。', typ='error')
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
        print_info('metaHumanFace控制器导入帧完成')

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
                print_info('控制器{}被跳过，但这是允许的，因为UE与Maya中的metaHuman控制器有少部分不对应'.format(ctl),
                           typ='warning')
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
            print_info('控制器{}不存在'.format(ctrl), typ='warning')


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
                        print_info('控制器{}没有帧'.format(ctrlAttr), typ='warning')
            else:
                print_info('控制器{}不存在'.format(ctrl), typ='warning')
        print_info('metaHuman控制器动画移动{}帧已完成'.format(self.val))


class MetaFaceWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(MetaFaceWindow, self).__init__(parent)

        self.setWindowTitle(u'面捕数据接入工具')
        if mc.about(ntOS=True):  #判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.but_refNamSpace = QtWidgets.QPushButton()
        self.but_refNamSpace.setMaximumWidth(30)
        ic = QtGui.QIcon(QtCore.QResource('refresh.png').absoluteFilePath())
        self.but_refNamSpace.setIcon(ic)
        self.cob_namSpace = QtWidgets.QComboBox()
        self.but_get_faceCtrl_anim = QtWidgets.QPushButton(u'获取控制器动画信息文件')
        self.but_get_faceCtrl_anim.setMaximumWidth(130)

        self.but_selAll_faceCtrl = QtWidgets.QPushButton(u'选择所有face控制器')

        self.lab_trsCtlKey = QtWidgets.QLabel(u'移动metaFace控制器帧')
        self.spinBox_trsVal = QtWidgets.QSpinBox()
        self.spinBox_trsVal.setMinimum(-9999999)
        self.spinBox_trsVal.setMaximum(9999999)
        self.but_transformKeys = QtWidgets.QPushButton(u'移动控制器帧')

    def create_layout(self):
        trsfFaceAnim_layout = QtWidgets.QHBoxLayout()
        trsfFaceAnim_layout.addWidget(self.but_refNamSpace)
        trsfFaceAnim_layout.addWidget(self.cob_namSpace)
        trsfFaceAnim_layout.addWidget(self.but_get_faceCtrl_anim)

        trsfFaceAnimKeys_layout = QtWidgets.QHBoxLayout()
        trsfFaceAnimKeys_layout.addWidget(self.lab_trsCtlKey)
        trsfFaceAnimKeys_layout.addWidget(self.spinBox_trsVal)
        trsfFaceAnimKeys_layout.addWidget(self.but_transformKeys)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(trsfFaceAnim_layout)
        main_layout.addWidget(self.but_selAll_faceCtrl)
        main_layout.addLayout(trsfFaceAnimKeys_layout)

    def create_connections(self):
        self.but_refNamSpace.clicked.connect(self.refresh_nameSpace)
        self.but_get_faceCtrl_anim.clicked.connect(partial(ExportMetaHumanFaceCtrlAnimToMaya, self.cob_namSpace))
        self.but_selAll_faceCtrl.clicked.connect(partial(self.elect_metaFaceCtrl, self.cob_namSpace))
        self.but_transformKeys.clicked.connect(partial(TransformFaceCtrlsKeys, self.spinBox_trsVal, self.cob_namSpace))

    def refresh_nameSpace(self):
        ref_lis = mc.file(q=True, r=True)
        self.cob_namSpace.clear()
        for ref in ref_lis:
            nam = os.path.splitext(os.path.basename(ref))[0]
            self.cob_namSpace.addItem(nam + ':')

    def elect_metaFaceCtrl(self, combo_box):
        namSpace = combo_box.currentText()
        ctrl_lis = readCtrlsFile()
        mc.select(cl=True)
        no_lis = ['CTRL_lookAtSwitch', 'CTRL_faceGUIfollowHead', 'CTRL_eyesAimFollowHead', 'CTRL_rigLogicSwitch',
                  'CTRL_C_tongue', 'CTRL_C_tongue_narrowWide']
        for ctl in ctrl_lis:
            if ctl in no_lis:
                continue

            ctrl = namSpace + ctl
            if mc.objExists(ctrl):
                mc.select(ctrl, add=True)
            else:
                print_info('控制器{}不存在。'.format(ctrl), typ='warning')


if __name__ == '__main__':
    try:
        meta_win.close()
        meta_win.deleteLater()
    except:
        pass
    finally:
        meta_win = MetaFaceWindow()
        meta_win.show()
