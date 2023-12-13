# coding=gbk
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui

import cgtw2 as cgt
from data_path import icon_dir
from feedback_tool import Feedback_info as fp
from dutils import fileUtils

import os
import ConfigParser


class CGTLoginWindow(QtWidgets.QDialog):
    @staticmethod
    def set_validator(val):
        reg = QtCore.QRegExp(val)
        validator = QtGui.QRegExpValidator()
        validator.setRegExp(reg)
        return validator

    def __init__(self, parent=wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)):
        super(CGTLoginWindow, self).__init__(parent)

        self.setWindowTitle(u'��¼����')
        self.setWindowIcon(icon_dir['cgt_log'])
        if mc.about(ntOS=True):  #�ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)
        self.tw = None

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.lin_account.setFocus()

    def create_widgets(self):
        self.lab_info = QtWidgets.QLabel(u'���CgTeamWork�ƺ���û�е�¼\n���¼��ʹ�û�ֱ��ָ�����ĵ�¼��Ϣ')
        self.lab_info.setAlignment(QtCore.Qt.AlignCenter)
        self.lin_ip = QtWidgets.QLineEdit('192.168.0.233')
        self.lin_ip.setValidator(self.set_validator('[0-9.]{3}[0-9]'))
        self.lin_ip.setInputMask('000.000.000.000;*')
        self.lin_ip.setToolTip(u'��cgt��ip��ַ�����Ǳ�����ip��ַ����ǰ��ַΪ��192.168.0.233')
        self.lin_account = QtWidgets.QLineEdit()
        self.lin_account.setValidator(self.set_validator('[a-zA-Z]+'))
        self.lin_password = QtWidgets.QLineEdit()
        self.lin_password.setValidator(self.set_validator('[a-zA-Z0-9_.]+'))
        self.but_login = QtWidgets.QPushButton(u'��¼')

    def create_layout(self):
        layout_info = QtWidgets.QFormLayout()
        layout_info.addRow(u'ip��ַ��', self.lin_ip)
        layout_info.addRow(u'  �˺ţ�', self.lin_account)
        layout_info.addRow(u'  ���룺', self.lin_password)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.lab_info)
        main_layout.addLayout(layout_info)
        main_layout.addWidget(self.but_login)

    def create_connections(self):
        self.but_login.clicked.connect(self.login)

    def login(self):
        """
        ��¼����
        :return:None
        """
        ip = '{}:8383'.format(self.lin_ip.text())
        account = self.lin_account.text()
        password = self.lin_password.text()

        try:
            global tw, cfg, ini_path
            tw = cgt.tw(ip, account, password)

            cfg.set('personal_CgtInfo', 'ip', ip)
            cfg.set('personal_CgtInfo', 'account', account)
            cfg.set('personal_CgtInfo', 'password', password)
            with open(ini_path, 'w') as f:
                cfg.write(f)

            self.close()
            self.deleteLater()
        except Exception as e:
            self.lab_info.setText(u'��¼ʧ��\n{}'.format(e))


ini_path = '{}/data/user_data.ini'.format(os.path.dirname(os.path.dirname(__file__)))
cfg = ConfigParser.RawConfigParser()
cfg.read(ini_path)
tw = None

try:
    tw = cgt.tw()
    cfg.set('personal_CgtInfo', 'ip', tw.login.http_server_ip())
    cfg.set('personal_CgtInfo', 'account', tw.login.account())
    cfg.set('personal_CgtInfo', 'account_id', tw.login.account_id())
except:
    ini_ip = cfg.get('personal_CgtInfo', 'ip')
    ini_account = cfg.get('personal_CgtInfo', 'account')
    ini_password = cfg.get('personal_CgtInfo', 'password')
    if ini_ip and ini_account and ini_password:
        tw = cgt.tw(ini_ip, ini_account, ini_password)
    else:
        try:
            loginWin.close()
            loginWin.deleteLater()
        except:
            pass
        finally:
            fp('���¼����CgTeamWork�˺�', warning=True, viewMes=True)
            loginWin = CGTLoginWindow()
            loginWin.exec_()#ʹ��exec_�������ڣ�����ʹ���������ڴ������н����������



def get_id_lis(proj, model='asset', cla='task', stage='Mod'):
    """
    ������Ŀ��ģ��ͽ׶λ�ȡ����id�б�
    :param stage: ��ȡ����idʱ��ͨ����������ȡ��ͬ�׶ε�id
    :param cla: ʹ��info���ȡid����task���ȡid
    :param proj: ��Ŀ�� (str)
    :param model: ģ���� (str)
    :return: id�б� (list)
    """
    if cla == 'info':
        return tw.info.get_id(proj, model, [])
    elif cla == 'task':
        return tw.task.get_id(proj, model, [['pipeline.entity', '=', stage], 'and', ['asset.epshowup', '=', 'EP003']])


def get_all_project():
    """
    ��ȡ������Ŀ�����ݿ���������������cgt��api��db����ָ����Ŀ
    :return:��Ŀ���ݿ����б�
    """
    project_lis = []
    for inf in tw.task.get('public', 'project', get_id_lis('public', 'project'), ['project.database']):
        project_lis.append(inf['project.database'])
    return project_lis


def get_asset_dir(project, ids=[], field=['asset.cn_name', 'asset.entity']):
    """
    ��ȡָ����Ŀ�������ʲ�����Ϣ�ֵ䡣
    :param ids: Ҫ��ѯ��id�б�
    :param field: ������
    :param project: Ҫ��ѯ����Ŀ
    :return: �ʲ���Ϣ�ֵ䡣�ʲ�id��[�ʲ��������� �ʲ�Ӣ����]
    """
    asset_dir = {}
    for ass in tw.task.get(project, 'asset', ids if ids else get_id_lis(project, 'asset'), field):
        asset_dir[ass['id']] = [ass[inf] for inf in field]

    return asset_dir


def get_asset_folder(project, uid, typ='all', model='asset'):
    """
    ��������������ض�Ӧid���ļ���·��
    :param project: ��Ŀ��
    :param model: ģ����
    :param uid: �ʲ�id��
    :param typ: �ʲ�Ŀ¼��ʶ��
    :return: �ʲ�Ŀ¼·����,ֻ����һ��idʱ����str������id�б�ʱ�����ֵ�
    """
    if type(uid) == str:
        uid = [uid]

    if typ == 'all':
        folder_lis = {}
        for d in tw.task.get_dir(project, model, uid, ['mod_final', 'rig_final', 'rig_unreal', 'dyn_final']):
            folder_lis[d['id']] = (d['mod_final'], d['rig_final'], d['rig_unreal'], d['dyn_final'])
        return folder_lis
    return tw.task.get_dir(project, model, uid, [typ])[0][typ]


def get_asset_type(project, uid, model='asset'):
    """
    ��������������ض�Ӧid�ʲ������ͣ����ؾߣ����ߣ������
    :param project: ��Ŀ��
    :param uid: �ʲ�id��
    :param model: ģ����
    :return: �ʲ�������,ֻ����һ��idʱ����str������id�б�ʱ����list
    """
    if type(uid) == str:
        uid = [uid]

    if uid.__len__() > 1:
        typ_lis = {}
        for d in tw.task.get_field_and_dir(project, model, uid, ['asset_type.entity'], ['asset_type']):
            typ_lis[d['id']] = d['asset_type.entity']
        return typ_lis
    else:
        return tw.task.get_field_and_dir(project, model, uid, ['asset_type.entity'], ['asset_type'])[0][
            'asset_type.entity']


def push_file_to_teamWork(project, uid, filebox_info, local_path, model='asset', save=True):
    """
    �������ļ��ύ��cgt���ٷ��ύ���������۱����ļ����Ƕ��٣���������ȷ���ļ����ύ��ȥ
    :param save:�Ƿ񱣴浱ǰ���������ϴ�
    :param project: ���ݿ���
    :param uid: �ύ�ʲ��׶�����ע��mod��rig��Щ��ͬ�Ľ׶�Ϊ��ͬ��id��
    :param filebox_info: Ҫ�ύ���ļ����ʶ��
    :param local_path: �ļ����ڵı����ļ�·����
    :param model: ģ����
    :return: �ύ�Ƿ�ɹ���bool��
    """
    file_box_sign = tw.task.get_sign_filebox(project, model, uid, filebox_info)
    des_path = os.path.join(file_box_sign['path'], file_box_sign['rule'][0])

    if os.path.normcase(os.path.abspath(des_path)) == os.path.normcase(os.path.abspath(local_path)):
        fileUtils.version_up(*os.path.split(des_path))
        if save:
            mc.file(s=True, f=True, op='v=0')
        return True, file_box_sign['rule'][0]
    else:
        info_dir = {'db': project, 'module': model, 'module_type': 'task', 'task_id': uid, 'version': '',
                    'filebox_data': file_box_sign, 'file_path_list': [local_path], 'des_file_path_list': [des_path]}
        if save:
            mc.file(s=True, f=True, op='v=0')
        res = tw.send_local_http(model, project, 'filebox_bulk_upload_to_filebox', info_dir, 'get')
        return res, file_box_sign['rule'][0]

def set_status(project, uid, model='asset', state='Check'):
    """
    �޸��ʲ���״̬
    :param project: ���ݿ���
    :param uid: �ʲ���Ӧ�׶ε�id
    :param model: ģ����
    :param state: ״̬��
    :return: �ɹ��򷵻�true
    """
    return tw.task.update_task_status(project, model, id_list=[uid], status=state)
