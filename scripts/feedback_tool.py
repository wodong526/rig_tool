# -*- coding:GBK -*-
import traceback

import maya.OpenMaya as om
import maya.cmds as mc

import sys
import os

def caller_info():
    """
    ��ȡ�йص�ǰ�������÷�����Ϣ��

    Returns:
        tuple���������÷��ļ�·�����кŵ�Ԫ�顣
    """
    back_frame = sys._getframe().f_back.f_back
    back_path = back_frame.f_code.co_filename
    back_file = os.path.basename(back_path)
    back_lin = back_frame.f_lineno

    return back_path, back_lin

class Feedback_info(object):
    def __init__(self, tex, path=False, info=False, warning=False, error=False, viewMes=False, block=True, time=3):
        """
        ʹ���ṩ�Ĳ�����ʼ���ࡣ

        Args:
        tex (str): Ҫ��ӡ���ı���
        path (bool): �Ƿ�������÷����ļ�·�����кš�
        info (bool): �Ƿ��ı���ӡΪ��Ϣ��Ϣ��
        warning (bool): �Ƿ��ı���ӡΪ������Ϣ��
        error (bool): �Ƿ��ı���ӡΪ������Ϣ��
        viewMes (bool): �Ƿ���Maya�Ӵ�����ʾ��Ϣ��
        block (bool): �Ƿ�����ʾ��Ϣʱ��ֹ����ִ�С�
        time (int): ��ʾ��Ϣ��ʱ�䣨����Ϊ��λ����
        """
        if path:
            self.path, self.line = caller_info()
        else:
            self.line = None
            self.path = False
            self.vieMes = False
        self.time = time*1000
        self.vieMes = viewMes
        self.block = block

        if info:
            self.print_info(tex)
        elif warning:
            self.print_warning(tex)
        elif error:
            self.print_error(tex)
        else:
            self.print_info(tex)

    def print_info(self, txt):
        if self.vieMes:
            mc.inViewMessage(amg='<font color="lightcyan">{}</font>'.format(txt), pos='midCenterBot', f=True, fst=self.time)

        if self.path:
            print(caller_info())
            om.MGlobal.displayInfo('�ļ�{}:{}'.format('{}��{}��'.format(
                self.path, self.line) if self.line else self.path, txt))
        else:
            om.MGlobal.displayInfo('{}'.format(txt))

    def print_warning(self, txt):
        if self.vieMes:
            mc.inViewMessage(amg='<font color="yellow">{}</font>'.format(txt), pos='midCenterBot', f=True, fst=self.time)

        if self.path:
            om.MGlobal.displayWarning('�ļ�{}:{}'.format('{}��{}��'.format(
                self.path, self.line) if self.line else self.path, txt))
        else:
            om.MGlobal.displayWarning('{}'.format(txt))

    def print_error(self, txt):
        if self.vieMes:
            mc.inViewMessage(amg='<font color="red">{}</font>'.format(txt), pos='midCenterBot', f=True, fst=self.time)

        if self.path:
            if self.block:
                raise RuntimeError('�ļ�{}:{}'.format('{}��{}��'.format(
                    self.path, self.line) if self.line else self.path, txt))
            else:
                om.MGlobal.displayError('�ļ�{}:{}'.format('{}��{}��'.format(
                    self.path, self.line) if self.line else self.path, txt))
        else:
            if self.block:
                raise RuntimeError(txt)
            else:
                om.MGlobal.displayError(txt)
