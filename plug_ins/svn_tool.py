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

        self.setWindowTitle(u'��������svn��־')
        if mc.about(ntOS=True):  #�ж�ϵͳ����
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
            #strr += '�汾��:    ' + inf['�ύ��¼�汾��'] + '\n'
            #strr += 'ʱ��:        ' + inf['�ύʱ��'] + '\n'
            self.set_text_color('�汾��:    ' + inf['�ύ��¼�汾��'] + '\n', 0, 255, 0)
            self.set_text_color('ʱ��:        ' + inf['�ύʱ��'] + '\n', 255, 134, 0)
            if inf['�ύ����']:
                res = '�ύ����:'
                for s in inf['�ύ����']:
                    res += s + '\n                '
                #strr += res + '\n'
                self.set_text_color(res + '\n', 255, 0, 255)
            else:
                #strr += '�ύ����: ��' + '\n\n'
                self.set_text_color('�ύ����: ��' + '\n\n', 255, 0, 255)

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
    ǩ��svn�⵽ָ��λ��
    :return:
    '''
    resout = os.system('svn checkout {} {}'.format(data_path.serverSubmitsTheLogs, data_path.localPath))
    if resout == 0:
        fb_print('���߼�ǩ���ɹ���', info=True, viewMes=True, path=__file__, line=lin())
    else:
        fb_print('���߼�ǩ��ʧ�ܡ�', error=True, viewMes=True, path=__file__, line=lin())


def svn_info():
    '''
    ��ӡ��ǰ���ؿ��svn��Ϣ
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
        fb_print('��İ汾��{}����ǰ�汾��{}�����ͬ�����߼ܸ��µ����°汾��'.format(loca_edition, server_edition),
                 warning=True,
                 viewMes=True, path=__file__, line=lin())
    else:
        fb_print('��İ汾��{}����ǰ�汾��{}�����Ѿ������°汾��'.format(loca_edition, server_edition), info=True,
                 viewMes=True,
                 path=__file__, line=lin())


def svn_upData():
    '''
    ���±��ؿ�Ϊ���°汾
    :return:
    '''
    resout = os.system('pushd "{}" && svn update'.format(data_path.localPath))
    if resout == 0:
        fb_print('���߼�ͬ���ɹ�', info=True, viewMes=True, path=__file__, line=lin())
    else:
        fb_print('���߼�ͬ��ʧ��', error=True, viewMes=True, path=__file__, line=lin())


def svn_logs():
    """
    չʾ��������svn���ύ��־
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
            lin_dir = {'�ύ����': []}
            continue
        out_inf = lin.split(' | ')
        if len(out_inf) > 1:
            lin_dir['�ύ��¼�汾��'] = out_inf[0].replace('r', '')
            lin_dir['�ύʱ��'] = out_inf[2][0:19]
        else:
            lin_dir['�ύ����'].append(lin)



    try:
        svn_window.close()
        svn_window.deleteLater()
    except:
        pass
    finally:
        svn_window = SvnInfo(logs)
        svn_window.show()
