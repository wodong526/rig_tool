# coding=gbk
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui

import shutil
import os
import re
import json

from feedback_tool import Feedback_info as fb_print, LIN as lin


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def create_folder(path, folder_name):
    """
    ͨ��·�����ļ��������ļ���
    :param path: �ļ�����·��
    :param folder_name: �ļ������֣�������Ϻ�׺��
    :return: �ļ�·��
    """
    folder = "{}/{}".format(path, folder_name)
    if not os.path.exists(folder):
        try:
            os.mkdir(folder)
            fb_print("�Ѵ����ļ���{}".format(folder), info=True)
        except OSError:
            fb_print("�����ļ���{}ʧ��".format(folder), error=True)

    return folder


def get_all_files(path, suffix='', bringSuffix=True):
    """
    �����ļ�����ָ����׺�������ļ��ľ���·��
    :param path: �ļ���·��
    :param suffix: �ļ���׺��Ϊ��ʱ�������к�׺�ļ�
    :param bringSuffix: ���ص��ļ�·���Ƿ���ļ���׺��
    :return: �����������ļ�·�����б�
    """
    if not os.path.exists(path):  #�ļ����Ƿ����
        return []

    all_files = [user_file for user_file in os.listdir(path) if os.path.isfile("{}/{}".format(path, user_file))]
    if suffix:
        return_files = []
        for user_file in all_files:
            if os.path.splitext(user_file)[1] == suffix:
                if bringSuffix:  #���ز�����׺�����ļ�����·��
                    return_files.append(user_file)
                else:  #���ش���׺�����ļ�����·��
                    return_files.append(str(user_file).rpartition(suffix)[0])
        return return_files
    else:
        if bringSuffix:
            return all_files
        else:
            return [os.path.splitext(user_file)[0] for user_file in all_files]


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


def version_up(path, user_file):
    """
    �ļ��汾����
    :param path:�ļ�����·��
    :param user_file: �ļ������֣�������׺����
    :return:
    """
    if os.path.exists("{}/{}".format(path, user_file)):  #�����ļ�����·����json�ļ���.json
        hiy_folder = create_folder(path=path, folder_name="history")  #������ʷ�ļ���

        file_extension = os.path.splitext(user_file)[1]  #��ȡ�ļ��ĺ�׺������.��
        file_base_name = "{}_v".format(str(user_file).rpartition(file_extension)[0])

        files_in_old_folder = get_all_files(hiy_folder, file_extension, False)  #�ļ���·������׺
        if files_in_old_folder:  #��ȡ����ʷ�ļ��б�
            latest_file_num = findHighestEndNum(files_in_old_folder, file_base_name)
        else:
            latest_file_num = 0

        current_file_name = "{}/{}".format(path, user_file)  #�ļ�����·��
        versioned_file_name = "{}/{}{:02d}{}".format(hiy_folder, file_base_name, latest_file_num + 1, file_extension)
        shutil.copyfile(current_file_name, versioned_file_name)


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
        fb_print('�ļ�{}/{}������'.format(path, user_file), warning=True)
        return None


def writeInfoAsFile(path, user_file, data):
    """
    ����Ϣд��ָ���ļ�
    :param path:Ҫд����ļ�����·��
    :param user_file:Ҫд����ļ���,������׺��
    :param data:Ҫд���ļ�����Ϣ
    :return:none
    """
    with open("{}/{}".format(path, user_file), "w") as f:
        if os.path.splitext(user_file)[1] == '.json':
            json.dump(data, f, indent=2)
        else:
            f.write(data)


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
        fb_print('û��ѡ����Ч·��', error=True)


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
        fb_print('û��ѡ����Ч�ļ�', error=True)
