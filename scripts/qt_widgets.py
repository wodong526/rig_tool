# -*- coding:GBK -*-
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from feedback_tool import Feedback_info as fp

class SeparatorAction(QWidgetAction):
    """
    为menu复写一个带字符的分隔符
    """

    def __init__(self, txt="      ", p=None):
        QWidgetAction.__init__(self, p)

        self._label = QLabel(txt)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        self._label.setSizePolicy(sizePolicy)

        self._line = QFrame()
        lineSizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._line.setSizePolicy(lineSizePolicy)
        self._line.setFrameShape(QFrame.HLine)
        self._line.setFrameShadow(QFrame.Raised)

        self.createLayout()

    def createLayout(self):
        wid = QWidget()

        actionLayout = QHBoxLayout(wid)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.setSpacing(0)
        actionLayout.addWidget(self._label)
        actionLayout.addWidget(self._line, 1)
        self.setDefaultWidget(wid)

class TableListWidget(QWidget):
    addClicked = Signal()

    def __init__(self,lab_name=None, parent=None):
        super(TableListWidget, self).__init__(parent)
        self._lab_nam = lab_name

        self.create_widget()
        self.create_layout()
        self.create_connect()

    def create_widget(self):
        self.lab = QLabel(self._lab_nam)
        self.lis = QListWidget()
        self.but_add_itm = QPushButton(u'添加')
        self.but_del_itm = QPushButton(u'删除')
        self.but_ren_itm = QPushButton(u'重命名')

    def create_layout(self):
        layout_but = QHBoxLayout()
        layout_but.addWidget(self.but_add_itm)
        layout_but.addWidget(self.but_del_itm)
        layout_but.addWidget(self.but_ren_itm)

        layout_main = QVBoxLayout()
        layout_main.setSpacing(3)
        layout_main.addWidget(self.lab)
        layout_main.addWidget(self.lis)
        layout_main.addLayout(layout_but)

        self.setLayout(layout_main)

    def create_connect(self):
        self.but_del_itm.clicked.connect(self.remove_item)
        self.but_ren_itm.clicked.connect(self.rename_item)
        self.but_add_itm.clicked.connect(self.addClicked.emit)

    def add_item(self, txt, icon_path=None):
        itm = QListWidgetItem(txt)
        itm.setIcon(QIcon(icon_path))
        self.lis.addItem(itm)

    def remove_item(self, index=None):
        if not index:
            index = self.lis.currentRow()

        if not index:
            fp(u'请选择要删除的项', error=True)
        self.lis.takeItem(index)

    def rename_item(self):
        itm = self.lis.currentItem()
        if not itm:
            fp(u'请选择要重命名的项', error=True)
        out, ok = QInputDialog.getText(self, u'重命名材质类型', u'请输入材质类型', QLineEdit.Normal, itm.text())
        if ok:
            itm.setText(out)

    def count(self):
        return self.lis.count()

    def item(self, index):
        return self.lis.item(index)

    def items(self):
        return [self.lis.item(i) for i in range(self.lis.count())]

def set_font(num):
    """
    将字符设置为输入的大小
    :param num: 要设置的字符大小
    :return: QtGui.QFont
    """
    font = QFont()
    font.setPointSize(num)
    return font
