# coding=gbk
import re

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
from userConfig import Conf

import os

class CGTLoginWindow(QtWidgets.QDialog):
    @staticmethod
    def set_validator(val):
        reg = QtCore.QRegExp(val)
        validator = QtGui.QRegExpValidator()
        validator.setRegExp(reg)
        return validator

    def __init__(self, parent=wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)):
        super(CGTLoginWindow, self).__init__(parent)

        self.setWindowTitle(u'登录窗口')
        self.setWindowIcon(icon_dir['cgt_log'])
        if mc.about(ntOS=True):  #判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  #删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)
        self.tw = None

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.lin_account.setFocus()

    def create_widgets(self):
        self.lab_info = QtWidgets.QLabel(u'你的CgTeamWork似乎还没有登录\n请登录后使用或直接指定您的登录信息')
        self.lab_info.setAlignment(QtCore.Qt.AlignCenter)
        self.lin_ip = QtWidgets.QLineEdit('192.168.0.233')
        self.lin_ip.setValidator(self.set_validator('[0-9.]{3}[0-9]'))
        self.lin_ip.setInputMask('000.000.000.000;*')
        self.lin_ip.setToolTip(u'是cgt的ip地址，不是本机的ip地址。当前地址为：192.168.0.233')
        self.lin_account = QtWidgets.QLineEdit()
        self.lin_account.setValidator(self.set_validator('[a-zA-Z]+'))
        self.lin_password = QtWidgets.QLineEdit()
        self.lin_password.setValidator(self.set_validator('[a-zA-Z0-9_.]+'))
        self.but_login = QtWidgets.QPushButton(u'登录')

    def create_layout(self):
        layout_info = QtWidgets.QFormLayout()
        layout_info.addRow(u'ip地址：', self.lin_ip)
        layout_info.addRow(u'  账号：', self.lin_account)
        layout_info.addRow(u'  密码：', self.lin_password)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.lab_info)
        main_layout.addLayout(layout_info)
        main_layout.addWidget(self.but_login)

    def create_connections(self):
        self.but_login.clicked.connect(self.login)

    def login(self):
        """
        登录窗口
        :return:None
        """
        ip = '{}:8383'.format(self.lin_ip.text())
        account = self.lin_account.text()
        password = self.lin_password.text()

        try:
            global tw, cfg, ini_path
            tw = cgt.tw(ip, account, password)

            cfg.set_value('personal_CgtInfo', 'ip', ip)
            cfg.set_value('personal_CgtInfo', 'account', account)
            cfg.set_value('personal_CgtInfo', 'password', password)
            with open(ini_path, 'w') as f:
                cfg.write(f)

            self.close()
            self.deleteLater()
        except Exception as e:
            self.lab_info.setText(u'登录失败\n{}'.format(e))


ini_path = '{}/data/user_data.ini'.format(os.path.dirname(os.path.dirname(__file__)))
cfg = Conf(ini_path)
tw = None

try:
    tw = cgt.tw()
    cfg.set_value('personal_CgtInfo', 'ip', tw.login.http_server_ip())
    cfg.set_value('personal_CgtInfo', 'account', tw.login.account())
    cfg.set_value('personal_CgtInfo', 'account_id', tw.login.account_id())
except:
    ini_ip = cfg.get_value('personal_CgtInfo', 'ip')
    ini_account = cfg.get_value('personal_CgtInfo', 'account')
    ini_password = cfg.get_value('personal_CgtInfo', 'password')
    if ini_ip and ini_account and ini_password:
        tw = cgt.tw(ini_ip, ini_account, ini_password)
    else:
        try:
            loginWin.close()
            loginWin.deleteLater()
        except:
            pass
        finally:
            fp('请登录您的CgTeamWork账号', warning=True, viewMes=True)
            loginWin = CGTLoginWindow()
            loginWin.exec_()#使用exec_启动窗口，可以使后续代码在窗口运行结束后才运行



def get_id_lis(proj, model='asset', cla='task', stage='Mod'):
    """
    根据项目与模块和阶段获取所有id列表
    :param stage: 获取任务id时，通过过滤器获取不同阶段的id
    :param cla: 使用info类获取id还是task类获取id
    :param proj: 项目名 (str)
    :param model: 模块名 (str)
    :return: id列表 (list)
    """
    if cla == 'info':
        return tw.info.get_id(proj, model, [])
    elif cla == 'task':
        if proj == 'proj_xxtt':
            return tw.task.get_id(proj, model, [['pipeline.entity', '=', stage], 'and', ['asset.epshowup', '=', 'EP003']])
        return tw.task.get_id(proj, model, [['pipeline.entity', '=', stage]])

def get_all_project():
    """
    获取所有项目的数据库名，该名可用于cgt的api的db参数指定项目
    :return:项目数据库名列表
    """
    project_lis = []
    for inf in tw.task.get('public', 'project', get_id_lis('public', 'project'), ['project.database']):
        project_lis.append(inf['project.database'])
    return project_lis


def get_asset_dir(project, ids=[], field=['asset.cn_name', 'asset.entity'], model='asset'):
    """
    获取指定项目的所有资产的信息字典。
    :param model: 模块
    :param ids: 要查询的id列表
    :param field: 过滤器
    :param project: 要查询的项目
    :return: 资产信息字典。资产id：[资产中文名， 资产英文名]
    """
    asset_dir = {}
    for ass in tw.task.get(project, model, ids if ids else get_id_lis(project, model), field):
        asset_dir[ass['id']] = [ass[inf] for inf in field]

    return asset_dir


def get_asset_folder(project, uid, typ='all', model='asset'):
    """
    根据输入参数返回对应id的文件夹路径
    :param project: 项目名
    :param model: 模块名
    :param uid: 资产id名
    :param typ: 资产目录标识名
    :return: 资产目录路径名,只传入一个id时返回str，传入id列表时返回字典
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
    根据输入参数返回对应id资产的类型，即载具，道具，人物等
    :param project: 项目名
    :param uid: 资产id名
    :param model: 模块名
    :return: 资产类型名,只传入一个id时返回str，传入id列表时返回list
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


def push_file_to_teamWork(project, uid, filebox_info, local_path, model='asset', version=False):
    """
    将本地文件提交到cgt，官方提交方法。无论本地文件名是多少，都会以正确的文件名提交上去
    :param version: 是否迭代保存
    :param project: 数据库名
    :param uid: 提交资产阶段名（注意mod，rig这些不同的阶段为不同的id）
    :param filebox_info: 要提交的文件框标识名
    :param local_path: 文件所在的本地文件路径名
    :param model: 模块名
    :return: 提交是否成功（bool）
    """
    file_box_sign = tw.task.get_sign_filebox(project, model, uid, filebox_info)
    des_path = os.path.join(file_box_sign['path'], file_box_sign['rule'][0])#服务器文件路径

    if os.path.normcase(os.path.abspath(des_path)) == os.path.normcase(os.path.abspath(local_path)):#当前文件就是服务器文件时
        if version:
            fileUtils.version_up(local_path, True)

        mc.file(s=True, f=True, op='v=0')
        return True, file_box_sign['rule'][0]
    else:
        if version:
            path, file = os.path.split(re.sub(r'_v\d{2}', '', local_path))
            base_name, suffix = os.path.splitext(file)
            index = fileUtils.get_latest_version_number(path, base_name, suffix)#获取最新版本号

            local_path = os.path.join(path, '{}_v{:02d}{}'.format(base_name, index + 1, suffix))
            mc.file(rn=local_path)

        mc.file(s=True, f=True, op='v=0')

        info_dir = {'db': project, 'module': model, 'module_type': 'task', 'task_id': uid, 'version': '',
                    'filebox_data': file_box_sign, 'file_path_list': [local_path], 'des_file_path_list': [des_path]}

        res = tw.send_local_http(model, project, 'filebox_bulk_upload_to_filebox', info_dir, 'get')
        return res, file_box_sign['rule'][0]

def set_status(project, uid, model='asset', state='Check'):
    """
    修改资产的状态
    :param project: 数据库名
    :param uid: 资产对应阶段的id
    :param model: 模块名
    :param state: 状态名
    :return: 成功则返回true
    """
    return tw.task.update_task_status(project, model, id_list=[uid], status=state)

def get_filebox_info(project, uid, sign, field, model='asset'):
    """
    通过文件框标识和字段名获取文件框信息。
    :param project: 数据库名称。
    :param uid: 资产id
    :param model: 模块名称.
    :param sign: 文件箱标识.
    :param field: 要从文件框信息中检索的特定字段。

    :return: 包含所请求文件箱信息的字典。
    """
    rtn_dir = {}
    for key, val in tw.task.get_sign_filebox(project, model, uid, sign).items():
        if key in field:
            rtn_dir[key] = val
    return rtn_dir

def from_id_get_stage_id(project, source_id, tag_stage, model='asset', cla='task'):
    """
    根据根据资产id和tag阶段获取对应的阶段id
    :param project: 数据库名称。
    :param source_id: 已有的任意阶段的ID.
    :param tag_stage: 要查询的阶段.
    :param model: 模块类型（默认为“asset”）.
    :param cla: 任务类型（默认为“task”）.

    :return: 指定ID的资产对应的指定阶段的ID。
    """
    source_name = get_asset_dir(project, [source_id], model=model)[source_id][1]
    tag_ids = get_id_lis(project, model, cla, stage=tag_stage)

    for tag_id, tag_name in get_asset_dir(project, ids=tag_ids).items():
        if tag_name[1] == source_name:
            return tag_id

