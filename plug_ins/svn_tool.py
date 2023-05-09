# -*- coding:GBK -*-
from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance

import os
import subprocess

import maya.cmds as mc
import maya.OpenMayaUI as omui

from feedback_tool import Feedback_info as fb_print, LIN as lin
import data_path

tool_nam = __file__.split('\\')[1]


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class SvnInfo(QtWidgets.QDialog):
    def __init__(self, txt, parent=maya_main_window()):
        super(SvnInfo, self).__init__(parent)
        self.setMinimumSize(400, 500)

        self.setWindowTitle(u'服务器端svn日志')
        if mc.about(ntOS=True):  #判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.texEdit = QtWidgets.QTextEdit()
        self.texEdit.setReadOnly(True)
        self.setText(txt)
        # self.texEdit.setText(txt.decode('gbk'))
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.texEdit)

    def setText(self, logs):
        strr = ''
        for inf in logs:
            #strr += '版本号:    ' + inf['提交记录版本号'] + '\n'
            #strr += '时间:        ' + inf['提交时间'] + '\n'
            self.set_text_color('版本号:    ' + inf['提交记录版本号'] + '\n', 0, 255, 0)
            self.set_text_color('时间:        ' + inf['提交时间'] + '\n', 255, 134, 0)
            if inf['提交内容']:
                res = '提交内容:'
                for s in inf['提交内容']:
                    res += s + '\n                '
                #strr += res + '\n'
                self.set_text_color(res + '\n', 255, 0, 255)
            else:
                #strr += '提交内容: 无' + '\n\n'
                self.set_text_color('提交内容: 无' + '\n\n', 255, 0, 255)

    def set_text_color(self, text, *args):
        cursor = self.texEdit.textCursor()
        char_format = QtGui.QTextCharFormat()
        char_format.setForeground(QtGui.QColor(args[0], args[1], args[2]))
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text.decode('gbk'), char_format)
        cursor.setPosition(0)
        self.texEdit.setTextCursor(cursor)

def svn_chectOut():
    '''
    签出svn库到指定位置
    :return:
    '''
    resout = os.system('svn checkout {} {}'.format(data_path.serverSubmitsTheLogs, data_path.localPath))
    if resout == 0:
        fb_print('工具架签出成功。', info=True, viewMes=True, path=__file__, line=lin())
    else:
        fb_print('工具架签出失败。', error=True, viewMes=True, path=__file__, line=lin())


def svn_info():
    '''
    打印当前本地库的svn信息
    :return:
    '''

    def output_info(info):
        revisionNum = re.search("Revision:\s\d+", info)
        return revisionNum.group().split(":")[1]

    import re, subprocess
    server_info = subprocess.check_output("svn info {}".format(data_path.serverSubmitsTheLogs))
    loca_info = subprocess.check_output("svn info {}".format(data_path.localPath))
    server_edition = output_info(server_info)
    loca_edition = output_info(loca_info)
    if server_edition != loca_edition:
        fb_print('你的版本是{}，当前版本是{}。点击同步工具架更新到最新版本。'.format(loca_edition, server_edition),
                 warning=True,
                 viewMes=True, path=__file__, line=lin())
    else:
        fb_print('你的版本是{}，当前版本是{}。你已经是最新版本。'.format(loca_edition, server_edition), info=True,
                 viewMes=True,
                 path=__file__, line=lin())


def svn_upData():
    '''
    更新本地库为最新版本
    :return:
    '''
    resout = os.system('pushd "{}" && svn update'.format(data_path.localPath))
    if resout == 0:
        fb_print('工具架同步成功', info=True, viewMes=True, path=__file__, line=lin())
    else:
        fb_print('工具架同步失败', error=True, viewMes=True, path=__file__, line=lin())


def svn_logs():
    """
    展示服务器端svn的提交日志
    :return:
    """
    svn_repo_path = data_path.serverSubmitsTheLogs
    p = subprocess.Popen(['svn', 'log', svn_repo_path], stdout=subprocess.PIPE)
    output, err = p.communicate()
    log_lines = output.splitlines()
    log_lines = [line.strip() for line in log_lines if line.strip()]

    logs = []
    lin_dir = {}
    for lin in log_lines:
        if '-------' in lin:
            if lin_dir:
                logs.append(lin_dir)
            lin_dir = {'提交内容': []}
            continue
        out_inf = lin.split(' | ')
        if len(out_inf) > 1:
            lin_dir['提交记录版本号'] = out_inf[0].replace('r', '')
            lin_dir['提交时间'] = out_inf[2][0:19]
        else:
            lin_dir['提交内容'].append(lin)



    try:
        svn_window.close()
        svn_window.deleteLater()
    except:
        pass
    finally:
        svn_window = SvnInfo(logs)
        svn_window.show()
