# -*- coding:GBK -*-
import maya.OpenMaya as om
import maya.cmds as mc

import traceback


class Feedback_info(object):
    def __init__(self, tex, path=None, line=None, info=False, warning=False, error=False, viewMes=False):
        if path:
            self.line = line
            self.path = path
            self.vieMes = viewMes
        else:
            self.line = None
            self.path = None
            self.vieMes = None

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
            mc.inViewMessage(amg='<font color="lightcyan">{}</font>'.format(txt), pos='midCenterBot', f=True, fst=10000)

        if self.path:
            om.MGlobal.displayInfo('文件{}:{}。'.format('{}第{}行'.format(
                self.path, self.line) if self.line else self.path, txt))
        else:
            om.MGlobal.displayInfo('{}。'.format(txt))

    def print_warning(self, txt):
        if self.vieMes:
            mc.inViewMessage(amg='<font color="yellow">{}</font>'.format(txt), pos='midCenterBot', f=True, fst=10000)

        if self.path:
            om.MGlobal.displayWarning('文件{}:{}。'.format('{}第{}行'.format(
                self.path, self.line) if self.line else self.path, txt))
        else:
            om.MGlobal.displayWarning('{}。'.format(txt))

    def print_error(self, txt):
        if self.vieMes:
            mc.inViewMessage(amg='<font color="red">{}</font>'.format(txt), pos='midCenterBot', f=True, fst=20000)

        if self.path:
            raise RuntimeError('文件{}:{}。'.format('{}第{}行'.format(
                self.path, self.line) if self.line else self.path, txt))
        else:
            raise RuntimeError(txt)


def LIN():
    line_number = traceback.extract_stack()[-2][1]
    return line_number
