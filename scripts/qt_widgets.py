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
        self._widget = QtWidgets.QFrame(p)

        self._label = QtWidgets.QLabel(self._widget)
        self._label.setText(txt)
        fontMetrics = QtGui.QFontMetrics(QtGui.QFont(u'微软雅黑', 7, QtGui.QFont.Bold))
        textWidth = fontMetrics.width(txt)
        textHeigth = fontMetrics.height()
        self._label.setFixedSize(textWidth, textHeigth)

        self._line = QtWidgets.QFrame(self._widget)
        self._line.setFrameShape(QtWidgets.QFrame.HLine)
        self._line.setFrameShadow(QtWidgets.QFrame.Raised)

    def createWidget(self, menu):
        actionLayout = QtWidgets.QHBoxLayout(self._widget)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.setSpacing(0)
        actionLayout.addWidget(self._label)
        actionLayout.addWidget(self._line)
        self._widget.setLayout(actionLayout)

        return self._widget


def set_font(num):
    """
    将字符设置为输入的大小
    :param num: 要设置的字符大小
    :return: QtGui.QFont
    """
    font = QtGui.QFont()
    font.setPointSize(num)
    return font
