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
    通过路径与文件名生成文件夹
    :param path: 文件所在路径
    :param folder_name: 文件的名字，不加后缀名
    :return: 文件路径
    """
    folder = "{}/{}".format(path, folder_name)
    if not os.path.exists(folder):
        try:
            os.mkdir(folder)
            fp("已创建文件夹{}".format(folder), info=True)
        except OSError:
            fp("创建文件夹{}失败".format(folder), error=True)

    return folder

def findHighestEndNum(names, base_name):
    """
    返回提供的文件路径列表里版本最高的文件路径
    :param names: 文件路径列表
    :param base_name: 文件的基础名+"_v"
    :return:历史版本里最新的版本号
    """
    highest_value = 0
    base_name_suffix_m = re.search(r'\d+$', base_name)
    if base_name_suffix_m:
        base_name_suffix = base_name_suffix_m.group()
        base_name = base_name.rpartition(base_name_suffix)[0]

    for name in names:
        if base_name in name:
            suffix = name.partition(base_name)[2]  #返回base_name的前面，自身，后面三个元素组成的列表
            if suffix and re.match("^[0-9]*$", suffix):
                num = int(suffix)
                if num > highest_value:
                    highest_value = num

    return highest_value


def get_all_files(path, suffix=''):
    """
    返回文件夹下指定后缀的所有文件的绝对路径
    :param path: 文件夹路径
    :param suffix: 文件后缀，为空时返回所有后缀文件
    :return: 符合条件的文件路径名列表
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
    从历史记录文件中获取给定基本名称和后缀的最新版本号。

    Args:
    history (list): 表示版本历史记录的文件路径列表。
    base_name (str): 文件的基本名称。
    suffix (str): 文件的后缀。

    Returns:
    int: 最新版本号。
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
    文件版本控制
    :param to_history: 是否保存到history文件夹
    :param file_path:文件所在路径
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
    从给定路径与文件名读取指定文件的内容
    :param path: 文件所在的路径
    :param user_file: 文件名（需要包含后缀名）
    :return: 当文件存在时返回文件内容，不存在时返回None
    """
    if os.path.exists("{}/{}".format(path, user_file)):
        with open("{}/{}".format(path, user_file), "r") as f:
            if os.path.splitext(user_file)[1] == '.json':
                data = json.load(f)
            else:
                data = f.read()
        return data
    else:
        fp('文件{}/{}不存在'.format(path, user_file), warning=True)
        return None


def writeInfoAsFile(path, user_file, data):
    """
    将信息写入指定文件
    :param path:要写入的文件所在路径
    :param user_file:要写入的文件名,包括后缀名
    :param data:要写入文件的信息
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
    生成保存文件窗口
    :param title:窗口名
    :param path: 窗口刚打开的路径
    :param file_typ: 窗口中显示的文件类型
    :return: 返回的保存文件的绝对路径
    """
    if not file_typ:
        file_type = '(*.all)'
    else:
        file_type = '(*.{})'.format(file_typ)

    file_path = QtWidgets.QFileDialog.getSaveFileName(maya_main_window(), title, path, file_type)
    if file_path[0]:
        return file_path[0]
    else:
        fp('没有选择有效路径', error=True)


def getFilePath(title='', path='', file_typ=''):
    """
    生成选择文件窗口
    :param title: 窗口名
    :param path: 窗口刚打开的路径
    :param file_typ: 窗口中显示的文件类型
    :return: 返回选择的文件的绝对路径
    """
    if not file_typ:
        file_type = '(*.all)'
    else:
        file_type = '(*.{})'.format(file_typ)

    file_path = QtWidgets.QFileDialog.getOpenFileName(maya_main_window(), title, path, file_type)
    if file_path[0]:
        return file_path[0]
    else:
        fp('没有选择有效文件', error=True)

def remove_readonly(func, path, _):
    """
    错误处理函数，尝试移除文件的只读属性然后重新调用删除函数。
    """
    os.chmod(path, stat.S_IWRITE)  # 移除只读属性
    func(path)

def delete_files(path, force=True):
    """
    删除文件或文件夹
    """
    if not os.path.exists(path):
        return
    if not os.access(path, os.W_OK):#当文件为只读时
        if force:
            os.chmod(path, stat.S_IWRITE)
        else:
            fp('文件{}属性为只读，取消删除'.format(path.encode('gbk')), warning=True)
            return
    if os.path.isdir(path):
        shutil.rmtree(path, onerror=remove_readonly)
    elif os.path.isfile(path):
        os.remove(path)
    fp('已删除文件：{}'.format(path.encode('gbk')), info=True)

def run_file(path):
    os.startfile(path)
    