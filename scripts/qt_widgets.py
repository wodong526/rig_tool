# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui


class SeparatorAction(QtWidgets.QWidgetAction):
    """
    为menu复写一个带字符的分隔符
    """

    def __init__(self, txt="      ", p=None):
        QtWidgets.QWidgetAction.__init__(self, p)

        self._label = QtWidgets.QLabel(txt)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        self._label.setSizePolicy(sizePolicy)

        self._line = QtWidgets.QFrame()
        lineSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self._line.setSizePolicy(lineSizePolicy)
        self._line.setFrameShape(QtWidgets.QFrame.HLine)
        self._line.setFrameShadow(QtWidgets.QFrame.Raised)

        self.createLayout()

    def createLayout(self):
        wid = QtWidgets.QWidget()

        actionLayout = QtWidgets.QHBoxLayout(wid)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.setSpacing(0)
        actionLayout.addWidget(self._label)
        actionLayout.addWidget(self._line, 1)
        self.setDefaultWidget(wid)



def set_font(num):
    """
    将字符设置为输入的大小
    :param num: 要设置的字符大小
    :return: QtGui.QFont
    """
    font = QtGui.QFont()
    font.setPointSize(num)
    return font
