# coding=gbk
import stat
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui

import shutil
import os
import re
import json

from feedback_tool import Feedback_info as fp


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def create_folder(path, folder_name=''):
    """
    ͨ��·�����ļ��������ļ���
    :param path: �ļ�����·��
    :param folder_name: �ļ������֣����Ӻ�׺��
    :return: �ļ�·��
    """
    folder = "{}/{}".format(path, folder_name)
    if not os.path.exists(folder):
        try:
            os.mkdir(folder)
            fp("�Ѵ����ļ���{}".format(folder), info=True)
        except OSError:
            fp("�����ļ���{}ʧ��".format(folder), error=True)

    return folder

def findHighestEndNum(names, base_name):
    """
    �����ṩ���ļ�·���б���汾��ߵ��ļ�·��
    :param names: �ļ�·���б�
    :param base_name: �ļ��Ļ�����+"_v"
    :return:��ʷ�汾�����µİ汾��
    """
    highest_value = 0
    base_name_suffix_m = re.search(r'\d+$', base_name)
    if base_name_suffix_m:
        base_name_suffix = base_name_suffix_m.group()
        base_name = base_name.rpartition(base_name_suffix)[0]

    for name in names:
        if base_name in name:
            suffix = name.partition(base_name)[2]  #����base_name��ǰ�棬������������Ԫ����ɵ��б�
            if suffix and re.match("^[0-9]*$", suffix):
                num = int(suffix)
                if num > highest_value:
                    highest_value = num

    return highest_value


def get_all_files(path, suffix=''):
    """
    �����ļ�����ָ����׺�������ļ��ľ���·��
    :param path: �ļ���·��
    :param suffix: �ļ���׺��Ϊ��ʱ�������к�׺�ļ�
    :return: �����������ļ�·�����б�
    """
    all_files = [user_file for user_file in os.listdir(path) if os.path.isfile("{}/{}".format(path, user_file))]
    if suffix:
        return_files = []
        for user_file in all_files:
            if os.path.splitext(user_file)[1] == suffix:
                return_files.append(user_file)
        return return_files
    else:
        return all_files


def get_latest_version_number(history, base_name, suffix):
    """
    ����ʷ��¼�ļ��л�ȡ�����������ƺͺ�׺�����°汾�š�

    Args:
    history (list): ��ʾ�汾��ʷ��¼���ļ�·���б�
    base_name (str): �ļ��Ļ������ơ�
    suffix (str): �ļ��ĺ�׺��

    Returns:
    int: ���°汾�š�
    """
    index = 0
    for num in [os.path.split(h_path)[1].split('{}_v'.format(base_name))[-1] for h_path in
                get_all_files(history, suffix) if
                re.search(r'{}_v\d+{}'.format(base_name, suffix), os.path.split(h_path)[1])]:
        if int(os.path.splitext(num)[0]) > index:
            index = int(os.path.splitext(num)[0])

    return index

def version_up(file_path, to_history):
    """
    �ļ��汾����
    :param to_history: �Ƿ񱣴浽history�ļ���
    :param file_path:�ļ�����·��
    :return:
    """
    if not os.path.exists(file_path):
        return False

    path, file = os.path.split(file_path)
    base_name, suffix = os.path.splitext(file)
    history = os.path.join(path, 'history')
    if to_history:
        ver = get_latest_version_number(history, base_name, suffix)
        versioned_file_name = os.path.join(history, '{}_v{:02d}{}'.format(base_name, ver + 1, suffix))
    else:
        ver = get_latest_version_number(path, base_name, suffix)
        versioned_file_name = os.path.join(path, '{}_v{:02d}{}'.format(base_name, ver + 1, suffix))

    shutil.copyfile(file_path, versioned_file_name)
    return True


def fromFileReadInfo(path, user_file):
    """
    �Ӹ���·�����ļ�����ȡָ���ļ�������
    :param path: �ļ����ڵ�·��
    :param user_file: �ļ�������Ҫ������׺����
    :return: ���ļ�����ʱ�����ļ����ݣ�������ʱ����None
    """
    if os.path.exists("{}/{}".format(path, user_file)):
        with open("{}/{}".format(path, user_file), "r") as f:
            if os.path.splitext(user_file)[1] == '.json':
                data = json.load(f)
            else:
                data = f.read()
        return data
    else:
        fp('�ļ�{}/{}������'.format(path, user_file), warning=True)
        return None


def writeInfoAsFile(path, user_file, data):
    """
    ����Ϣд��ָ���ļ�
    :param path:Ҫд����ļ�����·��
    :param user_file:Ҫд����ļ���,������׺��
    :param data:Ҫд���ļ�����Ϣ
    :return:none
    """
    file_path = os.path.join(path, user_file)
    with open(file_path, "w") as f:
        if os.path.splitext(user_file)[1] == '.json':
            json.dump(data, f, indent=2)
        else:
            f.write(data)
    return file_path


def saveFilePath(title='', path='', file_typ=''):
    """
    ���ɱ����ļ�����
    :param title:������
    :param path: ���ڸմ򿪵�·��
    :param file_typ: ��������ʾ���ļ�����
    :return: ���صı����ļ��ľ���·��
    """
    if not file_typ:
        file_type = '(*.all)'
    else:
        file_type = '(*.{})'.format(file_typ)

    file_path = QtWidgets.QFileDialog.getSaveFileName(maya_main_window(), title, path, file_type)
    if file_path[0]:
        return file_path[0]
    else:
        fp('û��ѡ����Ч·��', error=True)


def getFilePath(title='', path='', file_typ=''):
    """
    ����ѡ���ļ�����
    :param title: ������
    :param path: ���ڸմ򿪵�·��
    :param file_typ: ��������ʾ���ļ�����
    :return: ����ѡ����ļ��ľ���·��
    """
    if not file_typ:
        file_type = '(*.all)'
    else:
        file_type = '(*.{})'.format(file_typ)

    file_path = QtWidgets.QFileDialog.getOpenFileName(maya_main_window(), title, path, file_type)
    if file_path[0]:
        return file_path[0]
    else:
        fp('û��ѡ����Ч�ļ�', error=True)

def remove_readonly(func, path, _):
    """
    ���������������Ƴ��ļ���ֻ������Ȼ�����µ���ɾ��������
    """
    os.chmod(path, stat.S_IWRITE)  # �Ƴ�ֻ������
    func(path)

def delete_files(path, force=True):
    """
    ɾ���ļ����ļ���
    """
    if not os.path.exists(path):
        return
    if not os.access(path, os.W_OK):#���ļ�Ϊֻ��ʱ
        if force:
            os.chmod(path, stat.S_IWRITE)
        else:
            fp('�ļ�{}����Ϊֻ����ȡ��ɾ��'.format(path.encode('gbk')), warning=True)
            return
    if os.path.isdir(path):
        shutil.rmtree(path, onerror=remove_readonly)
    elif os.path.isfile(path):
        os.remove(path)
    fp('��ɾ���ļ���{}'.format(path.encode('gbk')), info=True)

def run_file(path):
    os.startfile(path)
    