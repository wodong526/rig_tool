# -*- coding:GBK -*-
import traceback

import maya.OpenMaya as om
import maya.cmds as mc

import sys
import os

def caller_info():
    """
    获取有关当前函数调用方的信息。

    Returns:
        tuple：包含调用方文件路径和行号的元组。
    """
    back_frame = sys._getframe().f_back.f_back
    back_path = back_frame.f_code.co_filename
    back_file = os.path.basename(back_path)
    back_lin = back_frame.f_lineno

    return back_path, back_lin

class Feedback_info(object):
    def __init__(self, tex, path=False, info=False, warning=False, error=False, viewMes=False, block=True, time=3):
        """
        使用提供的参数初始化类。

        Args:
        tex (str): 要打印的文本。
        path (bool): 是否包含调用方的文件路径和行号。
        info (bool): 是否将文本打印为信息消息。
        warning (bool): 是否将文本打印为警告消息。
        error (bool): 是否将文本打印为错误消息。
        viewMes (bool): 是否在Maya视窗内显示消息。
        block (bool): 是否在显示消息时阻止程序执行。
        time (int): 显示消息的时间（以秒为单位）。
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
            om.MGlobal.displayInfo('文件{}:{}'.format('{}第{}行'.format(
                self.path, self.line) if self.line else self.path, txt))
        else:
            om.MGlobal.displayInfo('{}'.format(txt))

    def print_warning(self, txt):
        if self.vieMes:
            mc.inViewMessage(amg='<font color="yellow">{}</font>'.format(txt), pos='midCenterBot', f=True, fst=self.time)

        if self.path:
            om.MGlobal.displayWarning('文件{}:{}'.format('{}第{}行'.format(
                self.path, self.line) if self.line else self.path, txt))
        else:
            om.MGlobal.displayWarning('{}'.format(txt))

    def print_error(self, txt):
        if self.vieMes:
            mc.inViewMessage(amg='<font color="red">{}</font>'.format(txt), pos='midCenterBot', f=True, fst=self.time)

        if self.path:
            if self.block:
                raise RuntimeError('文件{}:{}'.format('{}第{}行'.format(
                    self.path, self.line) if self.line else self.path, txt))
            else:
                om.MGlobal.displayError('文件{}:{}'.format('{}第{}行'.format(
                    self.path, self.line) if self.line else self.path, txt))
        else:
            if self.block:
                raise RuntimeError(txt)
            else:
                om.MGlobal.displayError(txt)
