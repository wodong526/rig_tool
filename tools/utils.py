# -*- coding:GBK -*-

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui

import sys
from feedback_tool import Feedback_info as fb_print
LINE = sys._getframe()
FILE_PATH = __file__


def goToADV_pose():
    '''
    ʹ�����ڵ�adv��buildPose�ڵ㴢��Ķ��󶼻ع�ԭλ
    :return:
    '''
    if mc.objExists('buildPose'):
        mel_str = mc.getAttr('buildPose.udAttr')
        for order in mel_str.split(';'):
            if order:
                if order.split(' ')[-1][0].isalpha() and mc.objExists(order.split(' ')[-1]):
                    mm.eval(order)
        fb_print('adv�������ѻع�ԭλ��', info=True, viewMes=True)
    else:
        fb_print('������û��adv��buildPose�ڵ�', error=True)


