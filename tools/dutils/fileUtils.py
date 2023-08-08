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
    通过路径与文件名生成文件夹
    :param path: 文件所在路径
    :param folder_name: 文件的名字，必须加上后缀名
    :return: 文件路径
    """
    folder = "{}/{}".format(path, folder_name)
    if not os.path.exists(folder):
        try:
            os.mkdir(folder)
            fb_print("已创建文件夹{}".format(folder), info=True)
        except OSError:
            fb_print("创建文件夹{}失败".format(folder), error=True)

    return folder


def get_all_files(path, suffix='', bringSuffix=True):
    """
    返回文件夹下指定后缀的所有文件的绝对路径
    :param path: 文件夹路径
    :param suffix: 文件后缀，为空时返回所有后缀文件
    :param bringSuffix: 返回的文件路径是否带文件后缀名
    :return: 符合条件的文件路径名列表
    """
    if not os.path.exists(path):  #文件夹是否存在
        return []

    all_files = [user_file for user_file in os.listdir(path) if os.path.isfile("{}/{}".format(path, user_file))]
    if suffix:
        return_files = []
        for user_file in all_files:
            if os.path.splitext(user_file)[1] == suffix:
                if bringSuffix:  #返回不带后缀名的文件绝对路径
                    return_files.append(user_file)
                else:  #返回带后缀名的文件绝对路径
                    return_files.append(str(user_file).rpartition(suffix)[0])
        return return_files
    else:
        if bringSuffix:
            return all_files
        else:
            return [os.path.splitext(user_file)[0] for user_file in all_files]


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


def version_up(path, user_file):
    """
    文件版本控制
    :param path:文件所在路径
    :param user_file: 文件的名字（包含后缀名）
    :return:
    """
    if os.path.exists("{}/{}".format(path, user_file)):  #场景文件所在路径，json文件名.json
        hiy_folder = create_folder(path=path, folder_name="history")  #创建历史文件夹

        file_extension = os.path.splitext(user_file)[1]  #获取文件的后缀（包含.）
        file_base_name = "{}_v".format(str(user_file).rpartition(file_extension)[0])

        files_in_old_folder = get_all_files(hiy_folder, file_extension, False)  #文件夹路径，后缀
        if files_in_old_folder:  #获取的历史文件列表
            latest_file_num = findHighestEndNum(files_in_old_folder, file_base_name)
        else:
            latest_file_num = 0

        current_file_name = "{}/{}".format(path, user_file)  #文件完整路径
        versioned_file_name = "{}/{}{:02d}{}".format(hiy_folder, file_base_name, latest_file_num + 1, file_extension)
        shutil.copyfile(current_file_name, versioned_file_name)


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
        fb_print('文件{}/{}不存在'.format(path, user_file), warning=True)
        return None


def writeInfoAsFile(path, user_file, data):
    """
    将信息写入指定文件
    :param path:要写入的文件所在路径
    :param user_file:要写入的文件名,包括后缀名
    :param data:要写入文件的信息
    :return:none
    """
    with open("{}/{}".format(path, user_file), "w") as f:
        if os.path.splitext(user_file)[1] == '.json':
            json.dump(data, f, indent=2)
        else:
            f.write(data)


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
        fb_print('没有选择有效路径', error=True)


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
        fb_print('没有选择有效文件', error=True)
